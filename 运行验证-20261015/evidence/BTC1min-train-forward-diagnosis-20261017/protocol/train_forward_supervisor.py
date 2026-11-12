"""New-scope synchronous supervisor:600s aggregate,60min work,8GiB RSS,100MiB disk."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

PHASE = Path(__file__).resolve().parents[1]
BASE = PHASE.parents[1]
ART = PHASE / "artifacts"
AUTH = PHASE / "root/train-forward-authorization-and-fixed-scope.json"
ENV = {"OMP_NUM_THREADS": "6", "OMP_THREAD_LIMIT": "6", "OPENBLAS_NUM_THREADS": "6",
       "MKL_NUM_THREADS": "6", "VECLIB_MAXIMUM_THREADS": "6", "NUMEXPR_NUM_THREADS": "6",
       "BLIS_NUM_THREADS": "6", "PYTHONDONTWRITEBYTECODE": "1"}


def save(path, data):
    with path.open("x") as handle:
        json.dump(data, handle, indent=2, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


def disk():
    return sum(q.stat().st_size for q in PHASE.rglob("*") if q.is_file() and not q.is_symlink())


def own_rss(pid):
    pending, seen, total = [pid], set(), 0
    while pending:
        current = pending.pop()
        if current in seen:
            continue
        seen.add(current)
        answer = subprocess.run(["/bin/ps", "-o", "rss=", "-p", str(current)], capture_output=True, text=True)
        if answer.returncode == 0 and answer.stdout.strip():
            total += int(answer.stdout.strip()) * 1024
        answer = subprocess.run(["/usr/bin/pgrep", "-P", str(current)], capture_output=True, text=True)
        if answer.returncode not in (0, 1):
            raise RuntimeError("Owned process monitor failed")
        pending.extend(int(x) for x in answer.stdout.split())
    return total, sorted(seen)


def rss_highwater(who):
    number = resource.getrusage(who).ru_maxrss
    return number if sys.platform == "darwin" else number * 1024


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["preflight", "forward", "summary"])
    parser.add_argument("--approval", default=None)
    args = parser.parse_args()
    ART.mkdir(exist_ok=True)
    auth = json.loads(AUTH.read_text())
    previous = [json.loads(q.read_text()) for q in sorted(ART.glob("resource-*.json"))
                if not q.name.endswith(".started.json")]
    spent = sum(q["elapsed_seconds_charged"] for q in previous)
    remaining = min(600 - spent, (datetime.fromisoformat(auth["work_deadline_utc"]) -
                                  datetime.now(timezone.utc)).total_seconds())
    if remaining <= 0 or disk() >= 104857600:
        raise RuntimeError("New-scope budget/deadline exhausted")
    prerequisite = {"forward": "preflight", "summary": "forward"}.get(args.stage)
    if prerequisite and not any(q["stage"] == prerequisite and q["status"] == "PASS" for q in previous):
        raise RuntimeError("Missing successful supervised prerequisite")
    if args.stage != "preflight" and any(q["stage"] == args.stage for q in previous):
        raise RuntimeError("Single-use stage already attempted; no retry")
    prefix = ART / ("resource-%04d-%s" % (len(previous) + 1, args.stage))
    save(prefix.with_suffix(".started.json"), {"stage": args.stage,
         "at_utc": datetime.now(timezone.utc).isoformat(), "prior_seconds": spent,
         "remaining_seconds": remaining})
    env = os.environ.copy()
    env.update(ENV)
    env["TRAIN_FORWARD_SUPERVISED_PHASE"] = str(PHASE)
    for name in ["TMPDIR", "XDG_CACHE_HOME", "TORCH_HOME", "MPLCONFIGDIR"]:
        path = ART / "local-cache" / name.lower()
        path.mkdir(parents=True, exist_ok=True)
        env[name] = str(path)
    command = [str(BASE / ".venv/bin/python"), "-I", "-B",
               str(PHASE / "protocol/train_only_forward.py"), args.stage]
    if args.approval:
        command += ["--approval", args.approval]
    start = time.monotonic()
    peak, reason, child, pids = 0, None, None, set()
    try:
        with prefix.with_suffix(".stdout.txt").open("x") as out, prefix.with_suffix(".stderr.txt").open("x") as err:
            child = subprocess.Popen(command, env=env, stdout=out, stderr=err, start_new_session=True)
            while child.poll() is None:
                rss, owned = own_rss(child.pid)
                pids.update(owned)
                rss += rss_highwater(resource.RUSAGE_SELF)
                peak = max(peak, rss)
                if rss > 8589934592:
                    reason = "RSS_CAP"
                elif time.monotonic() - start >= remaining:
                    reason = "COMPUTE_OR_TOTAL_WORK_CAP"
                elif disk() >= 104857600:
                    reason = "PHASE_DISK_CAP"
                if reason:
                    os.killpg(child.pid, signal.SIGTERM)
                    try:
                        child.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        os.killpg(child.pid, signal.SIGKILL)
                    break
                time.sleep(0.2)
            child.wait()
    except BaseException:
        reason = reason or "SUPERVISOR_EXCEPTION"
        if child is not None and child.poll() is None:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait()
        raise
    finally:
        elapsed = time.monotonic() - start
        peak = max(peak, rss_highwater(resource.RUSAGE_CHILDREN) + rss_highwater(resource.RUSAGE_SELF))
        if peak > 8589934592:
            reason = reason or "COMPLETED_RSS_HWM_CAP"
        if disk() >= 104857600:
            reason = reason or "PHASE_DISK_CAP"
        receipt = {"stage": args.stage, "at_utc": datetime.now(timezone.utc).isoformat(),
                   "status": "PASS" if child is not None and child.returncode == 0 and reason is None else "STOP",
                   "exit_code": None if child is None else child.returncode, "stop_reason": reason,
                   "elapsed_seconds_charged": elapsed, "cumulative_seconds": spent + elapsed,
                   "compute_cap_seconds": 600, "work_deadline_utc": auth["work_deadline_utc"],
                   "peak_RSS_bytes": peak, "whole_new_phase_disk_bytes": disk(),
                   "known_worker_and_descendant_pids": sorted(pids), "command": command,
                   "thread_environment": ENV, "sample_interval_seconds": 0.2,
                   "RSS_not_virtual_memory_cap": True, "new_scope_not_old_budget": True}
        save(prefix.with_suffix(".json"), receipt)
        print(json.dumps(receipt))
    if receipt["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()

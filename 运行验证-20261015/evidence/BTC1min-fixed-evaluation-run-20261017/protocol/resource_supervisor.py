"""Stdlib-only synchronous resource supervisor; only inspects owned child PIDs."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

PHASE = Path(__file__).resolve().parents[1]
ART = PHASE / "artifacts"
BASE = PHASE.parents[1]
VENV = BASE / ".venv/bin/python"
THREAD_ENV = {
    "OMP_NUM_THREADS": "6", "OMP_THREAD_LIMIT": "6", "OPENBLAS_NUM_THREADS": "6",
    "MKL_NUM_THREADS": "6", "VECLIB_MAXIMUM_THREADS": "6",
    "NUMEXPR_NUM_THREADS": "6", "BLIS_NUM_THREADS": "6", "PYTHONDONTWRITEBYTECODE": "1",
}


def now():
    return datetime.now(timezone.utc).isoformat()


def write_new(path, value):
    with path.open("x") as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


def owned_disk_bytes():
    # Both owned output trees count; root/governance outputs are outside our ownership.
    return sum(x.stat().st_size for tree in [PHASE / "protocol", ART]
               for x in tree.rglob("*") if x.is_file() and not x.is_symlink())


def rss_of_owned_tree(pid):
    pending, seen, total = [pid], set(), 0
    while pending:
        current = pending.pop()
        if current in seen:
            continue
        seen.add(current)
        # Targeted owned process only: never enumerate other users' processes.
        result = subprocess.run(["/bin/ps", "-o", "rss=", "-p", str(current)],
                                capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            total += int(result.stdout.strip()) * 1024
        children = subprocess.run(["/usr/bin/pgrep", "-P", str(current)],
                                  capture_output=True, text=True)
        if children.returncode not in (0, 1):
            raise RuntimeError("Owned descendant monitoring failed")
        pending.extend(int(x) for x in children.stdout.split())
    return total, sorted(seen)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["health", "preflight", "fit_predict", "score"])
    parser.add_argument("--approval", default=None)
    args = parser.parse_args()
    ART.mkdir(exist_ok=True)
    authpath = PHASE / "root/execution-authorization.json"
    auth = json.loads(authpath.read_text())
    previous = [json.loads(x.read_text()) for x in sorted(ART.glob("resource-session-*.json"))
                if not x.name.endswith(".started.json")]
    spent = sum(x["elapsed_seconds_counted_toward_compute_cap"] for x in previous)
    if args.stage != "health" and not any(x["stage"] == "health" and x["status"] == "PASS_STAGE"
                                         for x in previous):
        raise RuntimeError("A successful health receipt is required; no fallback environment")
    prerequisite = {"fit_predict": "preflight", "score": "fit_predict"}.get(args.stage)
    if prerequisite and not any(x["stage"] == prerequisite and x["status"] == "PASS_STAGE"
                                for x in previous):
        raise RuntimeError("Successful supervised prerequisite missing: " + prerequisite)
    remaining = min(3600 - spent, (datetime.fromisoformat(auth["work_deadline_utc"]) -
                                  datetime.now(timezone.utc)).total_seconds())
    if remaining <= 0 or owned_disk_bytes() >= 1073741824:
        raise RuntimeError("No remaining authorized budget")
    number = len(previous) + 1
    prefix = ART / ("resource-session-%04d-%s" % (number, args.stage))
    marker = prefix.with_suffix(".started.json")
    write_new(marker, {"at_utc": now(), "stage": args.stage, "prior_compute_seconds": spent,
                       "remaining_seconds": remaining, "parent_pid": os.getpid()})
    env = os.environ.copy()
    env.update(THREAD_ENV)
    env["BTC_FIXED_SUPERVISED_PHASE"] = str(PHASE)
    # Redirect framework/temp cache writes into this phase instead of the old environment.
    for name in ["TMPDIR", "XDG_CACHE_HOME", "TORCH_HOME", "MPLCONFIGDIR"]:
        target = ART / "local-runtime" / name.lower()
        target.mkdir(parents=True, exist_ok=True)
        env[name] = str(target)
    worker = PHASE / "protocol" / ("runtime_health.py" if args.stage == "health" else "fixed_evaluation.py")
    command = [str(VENV), "-I", "-B", str(worker)]
    if args.stage != "health":
        command += [args.stage]
    if args.approval:
        command += ["--approval", args.approval]
    start = time.monotonic()
    peak = 0
    reason = None
    owned_pids = set()
    stdout = prefix.with_suffix(".stdout.txt")
    stderr = prefix.with_suffix(".stderr.txt")
    child = None
    try:
        with stdout.open("x") as out, stderr.open("x") as err:
            child = subprocess.Popen(command, env=env, stdout=out, stderr=err,
                                     start_new_session=True)
            while child.poll() is None:
                rss, pids = rss_of_owned_tree(child.pid)
                own_hwm = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                rss += own_hwm if sys.platform == "darwin" else own_hwm * 1024
                owned_pids.update(pids)
                peak = max(peak, rss)
                elapsed = time.monotonic() - start
                if rss > 8589934592:
                    reason = "RSS_LIMIT"
                elif elapsed >= remaining:
                    reason = "COMPUTE_OR_WORK_DEADLINE"
                elif owned_disk_bytes() >= 1073741824:
                    reason = "OWNED_DISK_LIMIT"
                if reason:
                    os.killpg(child.pid, signal.SIGTERM)
                    try:
                        child.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        os.killpg(child.pid, signal.SIGKILL)
                        child.wait()
                    break
                time.sleep(0.25)
            returncode = child.wait()
    except BaseException:
        reason = reason or "SUPERVISOR_EXCEPTION"
        if child is not None and child.poll() is None:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait()
        raise
    finally:
        elapsed = time.monotonic() - start
        # macOS ru_maxrss is actual high-water resident memory in bytes, not RLIMIT_AS.
        child_hwm = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        if sys.platform != "darwin":
            child_hwm *= 1024
        own_hwm = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if sys.platform != "darwin":
            own_hwm *= 1024
        peak = max(peak, child_hwm + own_hwm)
        disk = owned_disk_bytes()
        if peak > 8589934592:
            reason = reason or "OBSERVED_RSS_HIGH_WATER_LIMIT"
        if disk >= 1073741824:
            reason = reason or "OWNED_DISK_LIMIT"
        receipt = {"stage": args.stage, "at_utc": now(), "command": command,
                   "status": "PASS_STAGE" if child is not None and child.returncode == 0 and reason is None else "STOP_STAGE",
                   "exit_code": None if child is None else child.returncode,
                   "stop_reason": reason, "worker_pid": None if child is None else child.pid,
                   "observed_owned_pids": sorted(owned_pids),
                   "peak_actual_RSS_bytes": peak, "owned_disk_bytes_at_end": disk,
                   "elapsed_seconds_counted_toward_compute_cap": elapsed,
                   "cumulative_seconds_including_health_preflight": spent + elapsed,
                   "hard_compute_seconds_cap": 3600, "work_deadline_utc": auth["work_deadline_utc"],
                   "monitor_interval_seconds": 0.25,
                   "monitor_scope": "owned worker/descendants sampled RSS plus supervisor HWM; completed child RSS HWM also checked; not virtual address space",
                   "environment_caps": THREAD_ENV,
                   "stdout_path": str(stdout), "stderr_path": str(stderr)}
        write_new(prefix.with_suffix(".json"), receipt)
        print(json.dumps(receipt))
    if receipt["status"] != "PASS_STAGE":
        raise SystemExit(2)


if __name__ == "__main__":
    main()

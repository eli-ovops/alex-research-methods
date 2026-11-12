"""Single-child resource supervisor. Does not import scientific/model libraries."""
import os, sys, json, time, subprocess, argparse, signal
from pathlib import Path
from datetime import datetime, timezone
P=Path(__file__).resolve().parent
A=P/"artifacts";A.mkdir(exist_ok=True)
def utc():return datetime.now(timezone.utc).isoformat()
def save(f,v):f.write_text(json.dumps(v,indent=2)+"\n")
def disk():return sum(f.stat().st_size for f in P.rglob("*") if f.is_file())
def main():
    ap=argparse.ArgumentParser();ap.add_argument("stage",choices=["prepare","run"]);ap.add_argument("--approval");args=ap.parse_args()
    auth=json.loads((P/"authorization-and-budget.json").read_text())
    deadline=datetime.fromisoformat(auth["total_unit_deadline_UTC"])
    prior=list(A.glob("session-*.receipt.json"))
    used=sum(json.loads(f.read_text())["elapsed_monotonic_seconds"] for f in prior)
    assert used<7200 and datetime.now(timezone.utc)<deadline
    seq=len(prior)+1
    stem="session-"+str(seq).zfill(3)+"-"+args.stage
    # Exclusive per-stage supervisor start marker prevents accidental duplicate launches.
    marker=P/("supervisor-"+args.stage+"-started.json")
    with marker.open("x") as f:json.dump({"UTC":utc(),"pid":os.getpid(),"stage":args.stage},f)
    env=os.environ.copy()
    # No environment values are logged except explicit safe thread/offline settings.
    settings={k:"6" for k in ["OMP_NUM_THREADS","MKL_NUM_THREADS","OPENBLAS_NUM_THREADS","VECLIB_MAXIMUM_THREADS","NUMEXPR_NUM_THREADS"]}
    settings.update({"PYTHONDONTWRITEBYTECODE":"1","PYTHONHASHSEED":"20261017",
       "MPLCONFIGDIR":str(A/"cache"),"XDG_CACHE_HOME":str(A/"cache"),
       "TORCH_HOME":str(A/"cache/torch"),"HF_HUB_OFFLINE":"1","TRANSFORMERS_OFFLINE":"1"})
    env.update(settings)
    cmd=[str(P.parents[1]/".venv/bin/python"),"-I","-B",str(P/"daily_adapter.py"),args.stage]
    # P=base/evidence/phase so parents[1] is base.
    if args.approval:cmd+=["--approval",str(Path(args.approval).resolve())]
    out=(A/(stem+".stdout.txt")).open("xb");err=(A/(stem+".stderr.txt")).open("xb")
    t0=time.monotonic();started=utc();child=None;peak=0;peak_combined=0;stop=None
    try:
        child=subprocess.Popen(cmd,stdout=out,stderr=err,env=env,start_new_session=True)
        save(A/(stem+".live.json"),{"start_UTC":started,"pid":child.pid,"supervisor_pid":os.getpid(),
              "stage":args.stage,"prior_used_seconds":used,"command":cmd,"safe_env_settings":settings})
        while child.poll() is None:
            elapsed=time.monotonic()-t0
            if elapsed+used>=7200:stop="CUMULATIVE_COMPUTE_EVALUATION_BUDGET"
            if datetime.now(timezone.utc)>=deadline:stop="TOTAL_UTC_DEADLINE"
            if disk()>auth["new_disk_bytes_max"]:stop="NEW_DISK_LIMIT"
            # Only the known child PID, never a scan of other users' processes.
            rr=subprocess.run(["/bin/ps","-o","pid=,rss=","-p",str(child.pid)+","+str(os.getpid())],capture_output=True,text=True)
            if rr.returncode==0 and rr.stdout.strip():
                known={int(line.split()[0]):int(line.split()[1])*1024 for line in rr.stdout.splitlines()}
                peak=max(peak,known.get(child.pid,0))
                peak_combined=max(peak_combined,sum(known.values()))
                if peak_combined>auth["RSS_bytes_max"]:stop="KNOWN_WORKER_PLUS_SUPERVISOR_RSS_LIMIT"
            if stop:
                os.killpg(child.pid,signal.SIGTERM)
                try:child.wait(timeout=5)
                except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
                break
            time.sleep(.25)
        rc=child.wait()
    finally:
        out.close();err.close()
        receipt={"start_UTC":started,"end_UTC":utc(),"stage":args.stage,"known_child_pid":None if child is None else child.pid,
          "exit_code":None if child is None else child.returncode,"stop_reason":stop,
          "elapsed_monotonic_seconds":time.monotonic()-t0,"prior_used_seconds":used,
          "cumulative_seconds_including_this":used+time.monotonic()-t0,
          "peak_known_child_RSS_bytes_sampled":peak,"peak_worker_plus_supervisor_RSS_bytes_sampled":peak_combined,"new_disk_bytes":disk(),
          "child_terminated_no_live_process":child is None or child.poll() is not None,
          "no_automatic_retry":True,"sample_interval_seconds":.25}
        save(A/(stem+".receipt.json"),receipt)
    print(json.dumps(receipt),flush=True)
    if stop or rc!=0:sys.exit(1)
if __name__=="__main__":main()


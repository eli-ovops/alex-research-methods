"""Known-worker-only RSS/disk/deadline supervision; no market computations."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,signal,subprocess,sys,time

E=Path(__file__).resolve().parent
A=E/'artifacts';A.mkdir(exist_ok=True)
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,x):
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def rss(pid):
    r=subprocess.run(['/bin/ps','-o','rss=','-p',str(pid)],capture_output=True,text=True)
    return int(r.stdout.strip())*1024 if r.stdout.strip() else 0
def disk():return sum(p.stat().st_size for p in E.rglob('*') if p.is_file())

def main():
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['prepare','run']);ap.add_argument('--approval');args=ap.parse_args()
    auth=json.loads((E/'authorization-and-budget.json').read_text())
    deadline=datetime.datetime.fromisoformat(auth['total_unit_deadline_UTC'])
    prior=sum(json.loads(p.read_text())['elapsed_seconds'] for p in A.glob('session-*.receipt.json'))
    assert prior<1800 and datetime.datetime.now(datetime.timezone.utc)<deadline
    if args.stage=='run':assert not (E/'market-run-started.lock').exists(),'MARKET_ALREADY_STARTED'
    i=1
    while (A/f'session-{i:03d}.started.json').exists():i+=1
    prefix=A/f'session-{i:03d}'
    with Path(str(prefix)+'.started.json').open('x') as f:json.dump({'UTC':utc(),'supervisor_PID':os.getpid(),'stage':args.stage,'prior_seconds':prior},f)
    env=dict(os.environ)
    for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):env[k]='2'
    env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',TMPDIR=str(A),XDG_CACHE_HOME=str(A/'cache'))
    cmd=[sys.executable,'-I','-B',str(E/'adapter.py'),args.stage]
    if args.approval:cmd+=['--approval',args.approval]
    start=time.monotonic();began=utc();peak=0;cause=None
    with Path(str(prefix)+'.stdout.txt').open('x') as out,Path(str(prefix)+'.stderr.txt').open('x') as err:
        p=subprocess.Popen(cmd,stdout=out,stderr=err,env=env,start_new_session=True)
        save(Path(str(prefix)+'.live.json'),{'start_UTC':began,'worker_PID':p.pid,'supervisor_PID':os.getpid(),'stage':args.stage,'known_only':True})
        print(json.dumps({'start_UTC':began,'worker_PID':p.pid,'supervisor_PID':os.getpid(),'stage':args.stage}),flush=True)
        while p.poll() is None:
            peak=max(peak,rss(os.getpid())+rss(p.pid))
            elapsed=time.monotonic()-start
            cause=('COMPUTE_BUDGET' if prior+elapsed>=1800 else 'RSS_LIMIT' if peak>536870912 else
                   'DISK_LIMIT' if disk()>33554432 else 'UTC_DEADLINE' if datetime.datetime.now(datetime.timezone.utc)>=deadline else None)
            if cause:
                os.killpg(p.pid,signal.SIGTERM)
                try:p.wait(timeout=5)
                except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
                break
            time.sleep(.1)
        code=p.wait()
    elapsed=time.monotonic()-start
    rec={'stage':args.stage,'start_UTC':began,'end_UTC':utc(),'worker_PID':p.pid,
         'supervisor_PID':os.getpid(),'elapsed_seconds':elapsed,'cumulative_seconds':prior+elapsed,
         'peak_known_process_RSS_bytes_sampled':peak,'new_directory_bytes':disk(),
         'exit_code':code,'stop_reason':cause,'thread_limit':2,'worker_alive':False,
         'market_run_claim_exists':(E/'market-run-started.lock').exists(),
         'no_models_network_install_accounts_trades':True}
    save(Path(str(prefix)+'.receipt.json'),rec);print(json.dumps(rec),flush=True)
    sys.exit(code if code else (1 if cause else 0))
if __name__=='__main__':main()

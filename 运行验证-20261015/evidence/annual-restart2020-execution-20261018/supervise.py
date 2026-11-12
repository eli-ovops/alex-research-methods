"""Known-worker-only stdlib budget monitor for one fresh-capital diagnostic."""
from pathlib import Path
import argparse,datetime,json,os,signal,subprocess,sys,time
D=Path(__file__).resolve().parent;A=D/'artifacts';A.mkdir(exist_ok=True)
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def rss(pid):
    x=subprocess.run(['/bin/ps','-o','rss=','-p',str(pid)],capture_output=True,text=True)
    return int(x.stdout.strip())*1024 if x.stdout.strip() else 0
def disk():return sum(p.stat().st_size for p in D.rglob('*') if p.is_file())
def main():
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=('prepare','run'));ap.add_argument('--approval');args=ap.parse_args()
    au=json.loads((D/'root-admission.json').read_text());deadline=datetime.datetime.fromisoformat(au['work_deadline_UTC'])
    prior=sum(json.loads(p.read_text())['elapsed_seconds'] for p in A.glob('session-*.receipt.json'))
    assert prior<600 and datetime.datetime.now(datetime.timezone.utc)<deadline
    if args.stage=='run':assert not (D/'formal-restart2020-started.lock').exists(),'FORMAL_ALREADY_STARTED'
    i=1
    while (A/f'session-{i:03d}.started.json').exists():i+=1
    stem=A/f'session-{i:03d}'
    with Path(str(stem)+'.started.json').open('x') as f:json.dump({'UTC':utc(),'stage':args.stage,'supervisor_PID':os.getpid(),'prior_seconds':prior},f)
    env=dict(os.environ)
    for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):env[k]='2'
    env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',TMPDIR=str(A),XDG_CACHE_HOME=str(A/'cache'))
    cmd=[sys.executable,'-I','-B',str(D/'restart_adapter.py'),args.stage]
    if args.approval:cmd+=['--approval',args.approval]
    begin=utc();start=time.monotonic();peak=0;reason=None
    with Path(str(stem)+'.stdout.txt').open('x') as out,Path(str(stem)+'.stderr.txt').open('x') as err:
        p=subprocess.Popen(cmd,stdout=out,stderr=err,env=env,start_new_session=True)
        save(Path(str(stem)+'.live.json'),{'start_UTC':begin,'stage':args.stage,'worker_PID':p.pid,'supervisor_PID':os.getpid()})
        print(json.dumps({'start_UTC':begin,'worker_PID':p.pid,'supervisor_PID':os.getpid(),'stage':args.stage}),flush=True)
        while p.poll() is None:
            peak=max(peak,rss(os.getpid())+rss(p.pid));elapsed=time.monotonic()-start
            reason=('COMPUTE_BUDGET' if prior+elapsed>=600 else 'RSS_LIMIT' if peak>536870912 else
                    'DISK_LIMIT' if disk()>33554432 else 'UTC_DEADLINE' if datetime.datetime.now(datetime.timezone.utc)>=deadline else None)
            if reason:
                os.killpg(p.pid,signal.SIGTERM)
                try:p.wait(timeout=5)
                except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
                break
            time.sleep(.05)
        code=p.wait()
    elapsed=time.monotonic()-start
    rec={'stage':args.stage,'start_UTC':begin,'end_UTC':utc(),'worker_PID':p.pid,'supervisor_PID':os.getpid(),
      'exit_code':code,'stop_reason':reason,'elapsed_seconds':elapsed,'cumulative_seconds':prior+elapsed,
      'peak_worker_plus_supervisor_RSS_bytes_sampled':peak,'new_directory_bytes':disk(),'thread_limit':2,
      'no_live_worker':True,'formal_claim_exists':(D/'formal-restart2020-started.lock').exists(),
      'models_network_install_accounts_or_trades':False}
    save(Path(str(stem)+'.receipt.json'),rec);print(json.dumps(rec),flush=True)
    sys.exit(code if code else (1 if reason else 0))
if __name__=='__main__':main()

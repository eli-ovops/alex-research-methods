"""One supported formal invocation, bounded resources, no retries."""
from pathlib import Path
from datetime import datetime,timezone
import subprocess,sys,os,time,json,resource
D=Path(__file__).resolve().parent.parent;A=D/'artifacts'
def utc():return datetime.now(timezone.utc).isoformat()
def save(p,v):
    with p.open('x') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
assert len(sys.argv)==2
assert not (D/'execution/formal-C-started.lock').exists(),'ALREADY_FORMAL_CLAIMED'
env=dict(os.environ)
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):env[k]='2'
env['PYTHONDONTWRITEBYTECODE']='1'
cmd=[sys.executable,'-I','-B',str(D/'execution/adapter.py'),'run','--gate',sys.argv[1]]
start=time.monotonic();started=utc();before=resource.getrusage(resource.RUSAGE_CHILDREN)
save(A/'formal-command-started.json',dict(UTC=started,command=cmd,env_thread_limits={k:env[k] for k in env if k.endswith('NUM_THREADS') or k=='VECLIB_MAXIMUM_THREADS'},supervisor_PID=os.getpid()))
peak=0;reason=None;code=None
with (A/'formal.stdout.txt').open('x') as out,(A/'formal.stderr.txt').open('x') as err:
    p=subprocess.Popen(cmd,stdout=out,stderr=err,env=env)
    while p.poll() is None:
        elapsed=time.monotonic()-start
        snapshot=subprocess.run(['/bin/ps','-o','rss=','-p',str(p.pid)+','+str(os.getpid())],capture_output=True,text=True)
        rss=sum(int(n) for n in snapshot.stdout.split())*1024;peak=max(peak,rss)
        disk=sum(q.stat().st_size for q in D.rglob('*') if q.is_file())
        if elapsed>600:reason='COMPUTE_TIME_LIMIT'
        elif peak>536870912:reason='RSS_LIMIT'
        elif disk>33554432:reason='DISK_LIMIT'
        if reason:p.terminate();break
        time.sleep(.02)
    try:code=p.wait(timeout=5)
    except subprocess.TimeoutExpired:p.kill();code=p.wait();reason=reason or 'TERMINATION_TIMEOUT'
after=resource.getrusage(resource.RUSAGE_CHILDREN)
# ru_maxrss on macOS is bytes; on Linux it is KiB.
exact_child_max=after.ru_maxrss*(1024 if sys.platform.startswith('linux') else 1)
receipt=dict(start_UTC=started,end_UTC=utc(),command=cmd,worker_PID=p.pid,supervisor_PID=os.getpid(),exit_code=code,stop_reason=reason,wall_seconds=time.monotonic()-start,children_user_seconds=after.ru_utime-before.ru_utime,children_system_seconds=after.ru_stime-before.ru_stime,peak_worker_plus_supervisor_RSS_bytes_sampled=peak,child_max_RSS_bytes=exact_child_max,new_directory_bytes=sum(q.stat().st_size for q in D.rglob('*') if q.is_file()),thread_limit=2,stdlib_worker_single_thread=True,formal_claim_exists=(D/'execution/formal-C-started.lock').exists(),no_live_worker=p.poll() is not None)
save(A/'formal-command-receipt.json',receipt)
print(json.dumps(receipt,ensure_ascii=False))
sys.exit(code or (1 if reason else 0))

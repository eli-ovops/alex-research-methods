"""Resource wrapper; one invocation per mode; stdout/stderr retained, no old adapters."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,resource,subprocess,sys,time
D=Path(__file__).resolve().parent
mode=sys.argv[1];assert mode in ('prepare','formal')
args=[sys.executable,'-B','-E','-S',str(D/'accounting.py'),'--'+mode]+sys.argv[2:]
# Exclusive wrapper admission preserves failures, never overwrite/retry formal.
with (D/(mode+'-command-started.json')).open('x') as f:json.dump({'UTC':datetime.now(timezone.utc).isoformat(),'command':args},f)
env={'PATH':'/usr/bin:/bin:/usr/sbin:/sbin','LANG':'en_US.UTF-8','OMP_NUM_THREADS':'2','MKL_NUM_THREADS':'2','OPENBLAS_NUM_THREADS':'2','VECLIB_MAXIMUM_THREADS':'2','NUMEXPR_NUM_THREADS':'2','PYTHONDONTWRITEBYTECODE':'1'}
def limits():
    resource.setrlimit(resource.RLIMIT_CPU,(590,590))
started=datetime.now(timezone.utc).isoformat();t=time.monotonic();ru0=resource.getrusage(resource.RUSAGE_CHILDREN);peak=0;stopped=None
with (D/(mode+'-stdout.txt')).open('xb') as out,(D/(mode+'-stderr.txt')).open('xb') as err:
    p=subprocess.Popen(args,stdin=subprocess.DEVNULL,stdout=out,stderr=err,env=env,preexec_fn=limits)
    while p.poll() is None:
        try:
            ps=subprocess.run(['/bin/ps','-o','rss=','-p',str(p.pid)],capture_output=True,timeout=1)
            if ps.stdout.strip():peak=max(peak,int(ps.stdout.strip())*1024)
        except (ValueError,subprocess.TimeoutExpired):pass
        disk=sum(x.stat().st_size for x in D.rglob('*') if x.is_file())
        if peak>512*1024**2:stopped='RSS_LIMIT'
        if disk>16*1024**2:stopped='DISK_LIMIT'
        if time.monotonic()-t>590:stopped='WALL_LIMIT'
        if datetime.now(timezone.utc)>=datetime(2026,10,21,4,45,tzinfo=timezone.utc):stopped='WORK_DEADLINE'
        if stopped:p.kill();break
        time.sleep(.02)
    code=p.wait()
wall=time.monotonic()-t;ru1=resource.getrusage(resource.RUSAGE_CHILDREN)
def fp(p):b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
r={'mode':mode,'command':args,'UTC_start':started,'UTC_end':datetime.now(timezone.utc).isoformat(),'exit_code':code,'resource_stop':stopped,
 'whole_command_monotonic_wall_seconds':wall,'child_CPU_user_system_seconds':ru1.ru_utime+ru1.ru_stime-ru0.ru_utime-ru0.ru_stime,
 'child_CPU_scope':'includes child and ps sampler descendants; excludes prior commands and independent review',
 'rusage_children_peak_RSS_bytes_macOS':ru1.ru_maxrss,'sampled_child_peak_RSS_bytes':peak,'RSS_guard':'20ms sampled; RLIMIT_CPU hard; stdlib-only process, thread env2',
 'stdout':fp(D/(mode+'-stdout.txt')),'stderr':fp(D/(mode+'-stderr.txt')),'formal_attempts':1 if mode=='formal' else 0}
with (D/(mode+'-command-receipt.json')).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
print(json.dumps(r,indent=2));raise SystemExit(code if not stopped else 99)

"""Known-PID resource supervisor; no dependency/model imports."""
import sys,os,json,time,datetime,hashlib,subprocess,re
from pathlib import Path
D=Path(__file__).absolute().parent;UTC=datetime.timezone.utc;DISK=1073741824

def now():return datetime.datetime.now(UTC).isoformat()
def ident(p):b=Path(p).read_bytes();return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def used():return sum(p.stat().st_size for p in D.rglob('*') if p.is_file())
def save(n,x):
 b=(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
 if used()+len(b)>DISK:raise RuntimeError('DISK_CAP')
 with (D/n).open('xb') as f:f.write(b)
def sealcheck():
 s=json.loads((D/'source-seal.json').read_text())
 for p,v in s['inputs'].items():
  if ident(p)!=v:raise RuntimeError('SOURCE_MISMATCH')
 return s

def main():
 stage=sys.argv[1];s=sealcheck();c=json.loads((D/'config.json').read_text());deadline=datetime.datetime.fromisoformat(c['deadline_utc'])
 if stage not in ['health','run']:raise RuntimeError('STAGE')
 if datetime.datetime.now(UTC)>=deadline:raise RuntimeError('DEADLINE')
 prior=0
 if stage=='run':
  if len(sys.argv)!=4 or sys.argv[2]!='--approval':raise RuntimeError('GATE_REQUIRED')
  gp=Path(sys.argv[3]);g=json.loads(gp.read_text())
  if g.get('allow_five_date_unit') is not True or g.get('source_inputs')!=s['inputs']:raise RuntimeError('GATE_MISMATCH')
  h=json.loads((D/'session-health.json').read_text())
  if h['status']!='PASS':raise RuntimeError('HEALTH_FAILED')
  prior=h['elapsed_seconds']
  if prior>=1680:raise RuntimeError('BUDGET')
  save('formal-started.lock',{'UTC':now(),'pid':os.getpid(),'gate':str(gp),'identity':ident(gp),'single_invocation':True})
 else:save('health-started.lock',{'UTC':now(),'pid':os.getpid()})
 start=time.monotonic();started=now();peak=0;stop=None;child=None;code=None
 env={k:'1' for k in c['thread_env_names']};env.update(PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(D),HOME=str(D),XDG_CACHE_HOME=str(D/'cache'))
 with (D/('run-'+stage+'.stdout.txt')).open('x') as out,(D/('run-'+stage+'.stderr.txt')).open('x') as err:
  try:
   child=subprocess.Popen([sys.executable,'-I','-B',str(D/'adapter.py'),'formal' if stage=='run' else 'health'],stdout=out,stderr=err,env=env)
   save('live-'+stage+'.json',{'UTC':started,'supervisor_pid':os.getpid(),'worker_pid':child.pid,'stage':stage})
   while child.poll() is None:
    q=subprocess.run(['/bin/ps','-o','rss=','-p',str(os.getpid())+','+str(child.pid)],capture_output=True,text=True,check=True)
    peak=max(peak,sum(int(v) for v in q.stdout.split())*1024)
    if peak>536870912:stop='RSS_LIMIT'
    elif prior+time.monotonic()-start>1680:stop='COMPUTE_LIMIT_RESERVE120S'
    elif datetime.datetime.now(UTC)>=deadline:stop='DEADLINE'
    elif used()>DISK:stop='DISK_LIMIT'
    if stop:break
    time.sleep(.1)
  except Exception as e:stop='SUPERVISOR_'+type(e).__name__
  finally:
   if child is not None:
    if child.poll() is None:
     try:child.terminate()
     except ProcessLookupError:pass
     try:child.wait(timeout=3)
     except subprocess.TimeoutExpired:
      try:child.kill()
      except ProcessLookupError:pass
      child.wait()
    else:child.wait()
    code=child.returncode
 elapsed=time.monotonic()-start
 rec={'status':'PASS' if code==0 and stop is None else 'STOP','stage':stage,'started_UTC':started,'ended_UTC':now(),'elapsed_seconds':elapsed,'prior_seconds':prior,'cumulative_seconds':prior+elapsed,'total_cap_seconds':1800,'worker_limit_including_prior_seconds':1680,'reserved_for_acceptance_seconds':120,'exit_code':code,'stop':stop,'sampled_combined_peak_RSS_bytes':peak,'sampling_seconds':.1,'disk_bytes':used(),'supervisor_pid':os.getpid(),'worker_pid':None if child is None else child.pid,'no_active_worker':True,'source_seal':ident(D/'source-seal.json')}
 save('session-'+stage+'.json',rec);print(json.dumps(rec));return 0 if rec['status']=='PASS' else 1
if __name__=='__main__':sys.exit(main())

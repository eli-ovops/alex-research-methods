"""Separate once-only local metadata-key inspection; no network or data pages."""
from pathlib import Path
import sys,json,hashlib,datetime,time,subprocess,io
D=Path(__file__).absolute().parent
APP=D.parent/'root/gap-declaration-readonly-addendum.json'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def h(p):
 b=p.read_bytes();return {'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def save(n,x):
 b=(json.dumps(x,indent=2,ensure_ascii=False)+'\n').encode();used=sum(p.stat().st_size for p in D.rglob('*') if p.is_file())
 if used+len(b)>33554432:raise RuntimeError('DISK_LIMIT')
 with (D/n).open('xb') as f:f.write(b)
def worker():
 import pyarrow as pa
 import pyarrow.parquet as pq
 if pa.__version__!='26.0.0':raise RuntimeError('DEPENDENCY_VERSION_MISMATCH')
 pa.set_cpu_count(2);pa.set_io_thread_count(2)
 original=json.loads((D/'output-seal.json').read_text())['inputs']
 for n in ['footer.original.bin','first4.original.bin']:
  if h(D/n)!=original[str(D/n)]:raise RuntimeError('INPUT_CHANGED')
 cfg=json.loads((D/'config.json').read_text());tailp=Path(cfg['prior_tail']['path'])
 if h(tailp)!={'sha256':cfg['prior_tail']['sha256'],'bytes':8}:raise RuntimeError('TAIL_CHANGED')
 source=io.BytesIO((D/'first4.original.bin').read_bytes()+(D/'footer.original.bin').read_bytes()+tailp.read_bytes())
 meta=pq.read_metadata(source)
 keys=meta.metadata or {};val=keys.get(b'contains_gaps')
 if val is not None and len(val)>4096:raise RuntimeError('DECLARATION_VALUE_OVERSIZE')
 declaration=None if val is None else val.decode('utf8','strict')
 paths=[D/'gap_inspection.py',D/'gap-inspection-source-seal.json',APP,D/'output-seal.json',D/'config.json',D/'footer.original.bin',D/'first4.original.bin',tailp,D/'session-run.json']
 save('metadata-gap-declaration.json',{'status':'COMPLETE_LOCAL_DECLARATION_ONLY','UTC':now(),'exact_key':'contains_gaps','present':val is not None,'value_UTF8_exact':declaration,'gap_related_keynames_only':[k.decode('utf8','replace') for k in keys if b'gap' in k.lower()],'interpretation':'File self-description only, not independently verified gap-free continuity or complete history. No data pages/column statistics/other metadata values accessed.','network_requests':0,'rawfooter_printed':False,'prior_formal_unchanged':True,'inputs':{str(p):h(p) for p in paths}})
def main():
 if len(sys.argv)>1 and sys.argv[1]=='_worker':worker();return
 app=json.loads(APP.read_text());deadline=datetime.datetime.fromisoformat(app['deadline_utc'])
 if datetime.datetime.now(datetime.timezone.utc)>=deadline:raise RuntimeError('DEADLINE')
 seal=json.loads((D/'gap-inspection-source-seal.json').read_text())
 for p,v in seal['inputs'].items():
  if h(Path(p))!=v:raise RuntimeError('SOURCE_IDENTITY')
 prior=json.loads((D/'session-run.json').read_text())['cumulative_seconds']+10
 env={'PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'2','OPENBLAS_NUM_THREADS':'2','MKL_NUM_THREADS':'2','VECLIB_MAXIMUM_THREADS':'2','ARROW_NUM_THREADS':'2','TMPDIR':str(D)}
 started=now();t=time.monotonic();peak=0;stop=None
 with (D/'gap-inspection.stdout.txt').open('x') as o,(D/'gap-inspection.stderr.txt').open('x') as e:
  child=subprocess.Popen([sys.executable,'-I','-B',str(D/'gap_inspection.py'),'_worker'],stdout=o,stderr=e,env=env)
  while child.poll() is None:
   rss=subprocess.run(['/bin/ps','-o','rss=','-p',str(__import__('os').getpid())+','+str(child.pid)],capture_output=True,text=True,check=True)
   peak=max(peak,sum(int(v) for v in rss.stdout.split())*1024)
   if peak>512*1048576:stop='RSS_LIMIT'
   elif time.monotonic()-t+prior>300:stop='COMPUTE_LIMIT'
   elif datetime.datetime.now(datetime.timezone.utc)>=deadline:stop='DEADLINE'
   elif sum(p.stat().st_size for p in D.rglob('*') if p.is_file())>33554432:stop='DISK_LIMIT'
   if stop:child.terminate();break
   time.sleep(.1)
  try:code=child.wait(timeout=3)
  except subprocess.TimeoutExpired:child.kill();code=child.wait()
 elapsed=time.monotonic()-t
 rec={'stage':'gap-inspection','status':'PASS' if code==0 and stop is None else 'STOP','started_UTC':started,'ended_UTC':now(),'exit_code':code,'stop':stop,'worker_pid':child.pid,'elapsed_seconds':elapsed,'prior_formal_seconds':prior-10,'conservative_other_local_checks_charge_seconds':10,'cumulative_charged_seconds':prior+elapsed,'sampled_combined_peak_RSS_bytes':peak,'sampling_interval_seconds':.1,'disk_bytes':sum(p.stat().st_size for p in D.rglob('*') if p.is_file()),'network_requests':0,'new_formal_lock':False,'no_active_worker':True}
 save('gap-inspection-resource.json',rec);print(json.dumps(rec));sys.exit(0 if rec['status']=='PASS' else 1)
if __name__=='__main__':main()

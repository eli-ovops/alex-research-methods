"""Owned once-only cost-space diagnostic. No forecast, account, portfolio or network."""
from pathlib import Path
from fractions import Fraction
from array import array
import sys,os,json,time,datetime,hashlib,math,subprocess
D=Path(__file__).absolute().parent;UTC=datetime.timezone.utc;DISK=16777216

def now():return datetime.datetime.now(UTC).isoformat()
def identity(p):
 b=p.read_bytes();return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def used():return sum(p.stat().st_size for p in D.rglob('*') if p.is_file())
def save(n,x):
 b=(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
 if used()+len(b)>DISK:raise RuntimeError('RESOURCE_STOP_DISK')
 with (D/n).open('xb') as f:f.write(b)
def sealcheck():
 s=json.loads((D/'source-seal.json').read_text())
 for p,v in s['inputs'].items():
  if identity(Path(p))!=v:raise RuntimeError('DATA_INVALID_SEALED_INPUT')
 return s

def valid_quote(q):return all(v is not None and math.isfinite(v) and v>0 for v in q) and q[2]>q[0]
class Selector:
 def __init__(self,grid,gap):self.grid=grid;self.gap=gap;self.k=0;self.previous=None;self.points=[];self.bad=0;self.gaps=0;self.rows=0
 def feed(self,r,q):
  if r is None or not isinstance(r,int) or r<=0 or (self.previous is not None and r<self.previous['r']):raise RuntimeError('DATA_INVALID_RECEIPT_CLOCK')
  while self.k<len(self.grid) and self.grid[self.k]<r:
   self.points.append(self.previous);self.k+=1
  ok=valid_quote(q);before=self.bad;self.bad+=int(not ok)
  if self.previous is not None and r-self.previous['r']>self.gap:self.gaps+=1
  self.previous={'r':r,'q':tuple(q),'valid':ok,'bad_before':before,'bad_after':self.bad,'gaps':self.gaps,'row':self.rows};self.rows+=1
 def finish(self):
  while self.k<len(self.grid):self.points.append(self.previous);self.k+=1
  return self.points
REASONS=['missing_endpoint','invalid_endpoint_BBO','endpoint_too_old','invalid_interior_BBO','observed_interval_gap']
def qualify(a,b,t,u,age):
 if a is None or b is None:return ['missing_endpoint']
 if a['r']>t or b['r']>u or b['row']<a['row']:raise RuntimeError('DATA_INVALID_ASOF_INVARIANT')
 causes=[]
 if not a['valid'] or not b['valid']:causes.append('invalid_endpoint_BBO')
 if t-a['r']>age or u-b['r']>age:causes.append('endpoint_too_old')
 # Inclusive endpoint-to-endpoint original rows, as frozen in proposal.
 if b['bad_after']-a['bad_before']>0:causes.append('invalid_interior_BBO')
 if b['gaps']-a['gaps']>0:causes.append('observed_interval_gap')
 return causes

def cash_space(ask_entry,bid_exit,bps):
 ask=Fraction.from_float(ask_entry);bid=Fraction.from_float(bid_exit);f=Fraction(bps,10000)
 C=bid*(1-f)-ask*(1+f);S=10000*C/ask
 return C,S

def type7(values,p):
 if not values:return None
 v=sorted(values);z=(len(v)-1)*p;i=z.numerator//z.denominator;frac=z-i
 if not frac:return v[i]
 ans=v[i]+(v[i+1]-v[i])*float(frac)
 if not math.isfinite(ans):raise RuntimeError('NUMERICAL_INVALID_QUANTILE')
 return ans

def distribution(v):
 if not v:return {'min':None,'p50':None,'p95':None,'p99':None,'max':None}
 return {'min':min(v),'p50':type7(v,Fraction(1,2)),'p95':type7(v,Fraction(95,100)),'p99':type7(v,Fraction(99,100)),'max':max(v)}

def preflight():
 checks={}
 C,S=cash_space(100.0,110.0,25);assert C==Fraction(379,40) and S==Fraction(1895,2);checks['two_sided_fee_fraction_and_bp']=True
 assert cash_space(100.0,100.0,0)[0]==0 and cash_space(100.0,90.0,0)[0]<0;checks['signed_zero_negative_preserved']=True
 v=array('d',[0,10,20,30]);assert type7(v,Fraction(1,2))==15 and type7(v,Fraction(95,100))==28.5;checks['type7_interpolation']=True
 q=(99.0,2.0,100.0,3.0);bad=(99.0,0.0,100.0,3.0)
 s=Selector([3,5,8],5);s.feed(1,q);s.feed(5,q);s.feed(5,bad);s.feed(9,q);p=s.finish();assert p[0]['r']==1 and p[1]['row']==2 and not p[1]['valid'];assert 'invalid_endpoint_BBO' in qualify(p[0],p[1],3,5,5);checks['asof_last_tie_and_no_goodrow_fallback']=True
 s=Selector([1,11],5);s.feed(1,q);s.feed(7,bad);s.feed(11,q);a,b=s.finish();assert qualify(a,b,1,11,5)==['invalid_interior_BBO','observed_interval_gap'];checks['inclusive_interior_bad_and_gap']=True
 assert qualify(None,None,1,2,5)==['missing_endpoint'];assert 'endpoint_too_old' in qualify(p[0],p[0],10,11,5);checks['missing_age_fixed']=True
 try:s.feed(10,q)
 except RuntimeError:checks['backward_clock_rejected']=True
 else:raise AssertionError('backward not rejected')
 fees=[0,1,5,10,25];cs=[cash_space(100.0,101.0,f)[0] for f in fees];assert all(a>=b for a,b in zip(cs,cs[1:]));checks['fee_monotonicity']=True
 save('synthetic-preflight.json',{'status':'PASS_SYNTHETIC_ONLY_NO_MARKET_READ','UTC':now(),'checks':checks,'source':identity(D/'once_cost.py'),'config':identity(D/'config.json'),'network':0,'market_source_reads':0,'quotes':'All fixtures invented; no financial evidence.'})

def formal():
 c=json.loads((D/'config.json').read_text());src=Path(c['source']['path']);st=src.stat();h=hashlib.sha256();read=0
 if st.st_size!=c['source']['bytes']:raise RuntimeError('DATA_INVALID_SOURCE_SIZE')
 with src.open('rb') as f:
  while True:
   block=f.read(1048576)
   if not block:break
   h.update(block);read+=len(block)
 if h.hexdigest()!=c['source']['sha256'] or read!=c['source']['bytes']:raise RuntimeError('DATA_INVALID_SOURCE_HASH')
 save('actual-source-identity.json',{'UTC':now(),'path':str(src),'sha256':h.hexdigest(),'bytes':read,'hash_passes':1,'source_not_copied':True})
 import pyarrow as pa
 import pyarrow.parquet as pq
 if pa.__version__!='26.0.0':raise RuntimeError('DATA_INVALID_DEPENDENCY')
 pa.set_cpu_count(2);pa.set_io_thread_count(2)
 f=pq.ParquetFile(src);cols=c['projection'];grid=[c['grid_start_ns']+j*c['step_ns'] for j in range(c['planned_entries']+1)];selector=Selector(grid,c['gap_ns']);batches=0
 for n in cols:
  if n not in f.schema.names:raise RuntimeError('DATA_INVALID_MISSING_FIELD')
  if f.schema.column(f.schema.names.index(n)).physical_type!=('INT64' if n=='receipt_timestamp' else 'DOUBLE'):raise RuntimeError('DATA_INVALID_TYPE')
 for batch in f.iter_batches(batch_size=50000,columns=cols,use_threads=False):
  if batch.schema.names!=cols:raise RuntimeError('DATA_INVALID_PROJECTION')
  a=[batch.column(j).to_pylist() for j in range(5)];batches+=1
  for k in range(batch.num_rows):selector.feed(a[0][k],[a[j][k] for j in range(1,5)])
 if selector.rows!=f.metadata.num_rows:raise RuntimeError('DATA_INVALID_ROW_COUNT')
 points=selector.finish();post=src.stat()
 if (st.st_size,st.st_mtime_ns,st.st_ino)!=(post.st_size,post.st_mtime_ns,post.st_ino):raise RuntimeError('DATA_INVALID_SOURCE_CHANGED')
 allreason={r:0 for r in REASONS};firstreason={r:0 for r in REASONS};hours={str(i):{'planned':0,'eligible':0,'excluded':0} for i in range(24)};eligible=[]
 for i in range(c['planned_entries']):
  t,u=grid[i:i+2];a,b=points[i:i+2];hr=str((t//3600000000000)%24);hours[hr]['planned']+=1;causes=qualify(a,b,t,u,c['age_ns'])
  if causes:
   hours[hr]['excluded']+=1;firstreason[causes[0]]+=1
   for r in causes:allreason[r]+=1
  else:hours[hr]['eligible']+=1;eligible.append(i)
 n=len(eligible)
 if n+sum(firstreason.values())!=c['planned_entries']:raise RuntimeError('DATA_INVALID_ELIGIBILITY_CONSERVATION')
 # No endpoint/individual-window object is persisted. Only a local ephemeral cache.
 save('eligibility-seal.json',{'UTC':now(),'source_identity':c['source'],'planned':c['planned_entries'],'eligible':n,'excluded':c['planned_entries']-n,'all_applicable_reasons':allreason,'exclusive_first_reasons':firstreason,'hourly_coverage_only':hours,'source_rows':selector.rows,'batches':batches,'policy':'Frozen asof/age/gap/inclusive valid rows, no outcome filter; no prices/times/window labels retained.'})
 results=[]
 for bps in c['fees_bps']:
  counts={'negative':0,'zero':0,'positive':0};Cvalues=array('d');Svalues=array('d')
  for i in eligible:
   a,b=points[i:i+2];C,S=cash_space(a['q'][2],b['q'][0],bps)
   counts['negative' if C<0 else 'positive' if C>0 else 'zero']+=1
   try:cv,sv=float(C),float(S)
   except (OverflowError,ValueError):raise RuntimeError('NUMERICAL_INVALID_DISPLAY')
   if not math.isfinite(cv) or not math.isfinite(sv):raise RuntimeError('NUMERICAL_INVALID_DISPLAY')
   Cvalues.append(cv);Svalues.append(sv)
  if sum(counts.values())!=n:raise RuntimeError('DATA_INVALID_SIGN_COUNTS')
  if n==0:classification='DATA_INSUFFICIENT'
  elif counts['positive']==0:classification='NO_POSITIVE_SPACE_OBSERVED_THIS_DAY_POLICY_FEE'
  else:classification='NOT_EXCLUDED_CONDITIONAL_SPACE_EXISTS_THIS_DAY_POLICY_FEE'
  results.append({'one_way_fee_bps':bps,'eligible_count':n,'exact_sign_counts':counts,'fractions':{k:v/n if n else None for k,v in counts.items()},'signed_unit_quote_cash_difference':distribution(Cvalues),'signed_scale_invariant_bp':distribution(Svalues),'classification':classification})
 if any(a['exact_sign_counts']['positive']<b['exact_sign_counts']['positive'] for a,b in zip(results,results[1:])):raise RuntimeError('DATA_INVALID_FEE_MONOTONICITY')
 out={'status':'COMPLETE_FIXED_DAY_POLICY_DIAGNOSTIC' if n else 'DATA_INSUFFICIENT','UTC':now(),'source_identity':c['source'],'grid_policy':{'planned':c['planned_entries'],'t_first_UTC':'2022-10-01T00:01:00Z','t_last_UTC':'2022-10-01T23:58:00Z','step_seconds':60,'horizon_seconds':60,'age_max_seconds':5,'interior_gap_max_seconds':5,'asof':'last physical receipt<=endpoint, ties last physical; latest invalid no fallback'},'eligibility':{'planned':c['planned_entries'],'eligible':n,'excluded':c['planned_entries']-n,'exclusive_first_reasons':firstreason,'all_applicable_reasons':allreason,'hourly_coverage_only':hours},'whole_day_all_fees':results,'invariants_passed':True,'arithmetic':'Fraction.from_float of storedfloat64; fees exactbps/10000; exactsign; array(d) Type7 signeddisplay min/p50/p95/p99/max. No positive truncation/sum/reinvestment/mean portfolio return.','no_hourly_cost_results':True,'limits':['Hindsight/oracle future quote-space only; not an actionable signal or investor/account PnL.','Single examined day and60s long-only ask-in/bid-out policy; no universal upper bound, significance, freshOOS, current profitability or capacity.','contains_gapsYes preserved, unit/collectorclock/PIT and source completeness not independently certified.','No actual fees/fills/depth capacity; unit cash algebra does not claim1BTC fills orUSDT=USD.','No model, labels export, network, source copy or trades.']}
 save('diagnostic-summary.json',out);save('result-seal.json',{'UTC':now(),'summary':identity(D/'diagnostic-summary.json'),'eligibility_seal':identity(D/'eligibility-seal.json'),'source_identity_receipt':identity(D/'actual-source-identity.json'),'source_stat_after_unchanged':True,'source_config_seal':identity(D/'source-seal.json')})

def main():
 if len(sys.argv)>1 and sys.argv[1]=='_worker':
  sealcheck()
  if sys.argv[2]=='preflight':preflight()
  elif sys.argv[2]=='run':formal()
  else:raise RuntimeError('BAD_WORKER_STAGE')
  return
 if len(sys.argv)<2 or sys.argv[1] not in ['preflight','run']:raise RuntimeError('BAD_STAGE')
 stage=sys.argv[1];s=sealcheck();c=json.loads((D/'config.json').read_text());deadline=datetime.datetime.fromisoformat(c['deadline_utc'])
 if datetime.datetime.now(UTC)>=deadline:raise RuntimeError('RESOURCE_STOP_DEADLINE')
 if stage=='run':
  if len(sys.argv)!=4 or sys.argv[2]!='--approval':raise RuntimeError('GATE_REQUIRED')
  gp=Path(sys.argv[3]);g=json.loads(gp.read_text())
  if g.get('allow_once_cost_diagnostic') is not True or g.get('source_inputs')!=s['inputs']:raise RuntimeError('GATE_MISMATCH')
  if g.get('preflight_input')!=identity(D/'synthetic-preflight.json'):raise RuntimeError('PREFLIGHT_GATE_MISMATCH')
  with (D/'formal-started.lock').open('x') as f:json.dump({'UTC':now(),'pid':os.getpid(),'gate':str(gp),'gate_identity':identity(gp)},f)
 previous=sum(json.loads(p.read_text())['elapsed_seconds'] for p in D.glob('session-*.json'));start=time.monotonic();started=now();peak=0;stop=None
 env={'PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'2','OPENBLAS_NUM_THREADS':'2','MKL_NUM_THREADS':'2','VECLIB_MAXIMUM_THREADS':'2','ARROW_NUM_THREADS':'2','TMPDIR':str(D)}
 with (D/(stage+'.stdout.txt')).open('x') as o,(D/(stage+'.stderr.txt')).open('x') as e:
  child=subprocess.Popen([sys.executable,'-I','-B',str(D/'once_cost.py'),'_worker',stage],stdout=o,stderr=e,env=env);save(stage+'.live.json',{'UTC':started,'supervisor_pid':os.getpid(),'worker_pid':child.pid})
  while child.poll() is None:
   r=subprocess.run(['/bin/ps','-o','rss=','-p',str(os.getpid())+','+str(child.pid)],capture_output=True,text=True,check=True);peak=max(peak,sum(int(v) for v in r.stdout.split())*1024)
   if peak>536870912:stop='RSS_LIMIT'
   elif time.monotonic()-start+previous>1800:stop='COMPUTE_LIMIT'
   elif datetime.datetime.now(UTC)>=deadline:stop='DEADLINE'
   elif used()>DISK:stop='DISK_LIMIT'
   if stop:child.terminate();break
   time.sleep(.1)
  try:code=child.wait(timeout=3)
  except subprocess.TimeoutExpired:child.kill();code=child.wait()
 elapsed=time.monotonic()-start;rec={'stage':stage,'status':'PASS' if code==0 and stop is None else 'STOP','started_UTC':started,'ended_UTC':now(),'exit_code':code,'stop':stop,'elapsed_seconds':elapsed,'previous_stage_seconds':previous,'cumulative_seconds':previous+elapsed,'sampled_combined_peak_RSS_bytes':peak,'sampling_interval_seconds':.1,'supervisor_pid':os.getpid(),'worker_pid':child.pid,'new_disk_bytes':used(),'source_seal':identity(D/'source-seal.json'),'no_active_worker':True,'network_requests':0};save('session-'+stage+'.json',rec);print(json.dumps(rec));sys.exit(0 if rec['status']=='PASS' else 1)
if __name__=='__main__':main()

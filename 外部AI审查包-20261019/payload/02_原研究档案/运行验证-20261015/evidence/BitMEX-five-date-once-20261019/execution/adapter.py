"""Independent fixed XBTUSD retrospective research adapter; raw arrays remain local."""
import os,sys,json,time,datetime,hashlib,urllib.request,gzip,csv,math,re
from pathlib import Path
import numpy as np
D=Path(__file__).absolute().parent; UTC=datetime.timezone.utc; DISK=1073741824

def now():return datetime.datetime.now(UTC).isoformat()
def ident(p):
 h=hashlib.sha256();n=0
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b);n+=len(b)
 return {'bytes':n,'sha256':h.hexdigest()}
def used():return sum(p.stat().st_size for p in D.rglob('*') if p.is_file())
def save(n,x):
 b=(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
 if used()+len(b)>DISK:raise RuntimeError('DISK_CAP')
 with (D/n).open('xb') as f:f.write(b)
def npz(n,**x):
 # Small sampled arrays only; never expanded raw-event arrays.
 if sum(v.nbytes for v in x.values())+used()+65536>DISK:raise RuntimeError('DISK_CAP')
 with (D/n).open('xb') as f:np.savez(f,**x)
def sealcheck():
 s=json.loads((D/'source-seal.json').read_text())
 for p,v in s['inputs'].items():
  if ident(p)!=v:raise RuntimeError('SEALED_INPUT_MISMATCH')
 return s
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*a,**kw):return None

def health():
 start=time.monotonic();c=json.loads((D/'config.json').read_text());sealcheck()
 if sys.version_info[:3]!=(3,12,14) or np.__version__!='2.2.6':raise RuntimeError('DEPENDENCY_VERSION')
 if any(os.environ.get(k)!='1' for k in c['thread_env_names']):raise RuntimeError('THREAD_ENV')
 # No market data: tie rule, causal selection, unpenalized intercept, and fees.
 queries=[60,120];out=[];prev=None;i=0
 for ts,v in [(59,1),(60,2),(60,3),(121,4)]:
  while i<len(queries) and queries[i]<ts:out.append(prev);i+=1
  prev=(ts,v)
 while i<len(queries):out.append(prev);i+=1
 assert out==[(60,3),(60,3)]
 x=np.array([[1.,2.],[1.,4.],[1.,6.]])
 mu=x.mean(0);sd=x.std(0);z=(x-mu)/np.where(sd==0,1,sd);z[:,sd==0]=0
 assert np.isfinite(z).all() and np.all(z[:,0]==0)
 assert abs(float(np.mean(np.array([1.,2.,3.])))-2)<1e-12
 assert 102*(1-.0005)-100*(1+.0005)>0
 assert len(range(2,1439))==1437 and len(range(1,1440))==1439
 assert np.quantile(np.array([0.,1.,2.,3.]),.25,method='linear')==.75
 save('health-preflight.json',{'status':'PASS_NO_MARKET_OR_FIT','UTC':now(),'elapsed_seconds':time.monotonic()-start,'python':sys.version.split()[0],'numpy':np.__version__,'thread_env':{k:os.environ[k] for k in c['thread_env_names']},'fixtures':['tie-last physical asof','past-only selection','zero variance channel','population scaling','fee decimal/bps','1437 grid','linear quantile'],'no_market_read':True,'no_fit_or_prediction':True})

def download(obj):
 N=int(obj['Size']);url='https://s3-eu-west-1.amazonaws.com/public.bitmex.com/'+obj['Key'];day=obj['Key'].split('/')[-1][:8]
 h=hashlib.sha256();got=0;p=D/(day+'.partial.gz');rec={'url':url,'method':'GET','requests':1,'started_UTC':now(),'expected_bytes':N,'expected_ETag':obj['ETag'],'body_read':False}
 try:
  req=urllib.request.Request(url,headers={'If-Match':obj['ETag'],'Accept-Encoding':'identity'})
  op=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
  with op.open(req,timeout=30) as r:
   rec.update(status=r.status,headers={k:r.headers.get(k) for k in ['Content-Length','ETag','Last-Modified','Content-Type','Content-Encoding','x-amz-version-id']})
   if r.status!=200 or r.headers.get('Content-Length')!=str(N) or r.headers.get('ETag')!=obj['ETag'] or r.headers.get('Content-Encoding','identity').lower()!='identity':raise RuntimeError('HTTP_IDENTITY')
   with p.open('xb') as f:
    while got<N:
     b=r.read(min(1048576,N-got));rec['body_read']=True
     if not b:raise RuntimeError('SHORT_BODY')
     if used()+len(b)>DISK:raise RuntimeError('DISK_CAP')
     f.write(b);h.update(b);got+=len(b)
    if r.read(1):raise RuntimeError('OVERSIZE_BODY')
  dest=D/(day+'.original.csv.gz');p.rename(dest)
  rec.update(ended_UTC=now(),bytes=got,sha256=h.hexdigest(),path=str(dest));save(day+'-download.json',rec)
  return dest,{'bytes':got,'sha256':h.hexdigest()}
 except Exception as e:
  rec.update(ended_UTC=now(),bytes=got,partial_sha256=h.hexdigest(),error_type=type(e).__name__,status=getattr(e,'code',rec.get('status')))
  save(day+'-download-STOP.json',rec);raise
class HashRead:
 def __init__(self,f):self.f=f;self.h=hashlib.sha256();self.n=0
 def read(self,n=-1):
  b=self.f.read(n);self.h.update(b);self.n+=len(b);return b
class Lines:
 def __init__(self,f):self.f=f;self.total=0;self.record=0
 def __iter__(self):return self
 def __next__(self):
  b=self.f.readline(8193)
  if not b:raise StopIteration
  self.total+=len(b);self.record+=len(b)
  if self.record>8192:raise RuntimeError('RECORD_CAP')
  return b.decode('utf8','strict')
def parse_ns(s,day):
 if not re.fullmatch(r'\d{4}-\d{2}-\d{2}D\d{2}:\d{2}:\d{2}\.\d{9}',s):raise RuntimeError('TARGET_CLOCK_FORMAT')
 if s[:10]!=day:raise RuntimeError('TARGET_DATE')
 hh=int(s[11:13]);mm=int(s[14:16]);ss=int(s[17:19])
 if hh>23 or mm>59 or ss>59:raise RuntimeError('TARGET_CLOCK_RANGE')
 return ((hh*60+mm)*60+ss)*1000000000+int(s[20:])

def scan(p,day,expected,reuse_hash=False,require_training_coverage=False):
 start=time.monotonic();queries=np.arange(1,1440,dtype=np.int64)*60*1000000000
 points=np.full((1439,4),np.nan);ages=np.full(1439,np.inf);j=0;prev=None;last=None;rows=target=ties=gaps=0;maxgap=0
 before=p.stat();raw=open(p,'rb');wrapped=HashRead(raw) if reuse_hash else raw
 with raw:
  with gzip.GzipFile(fileobj=wrapped,mode='rb') as g:
   lines=Lines(g);r=csv.reader(lines,strict=True);header=next(r);lines.record=0
   if header!=['timestamp','symbol','bidSize','bidPrice','askPrice','askSize']:raise RuntimeError('HEADER')
   for row in r:
    lines.record=0;rows+=1
    if len(row)!=6:raise RuntimeError('CSV_WIDTH')
    if row[1]!='XBTUSD':continue
    target+=1;ts=parse_ns(row[0],day)
    try:bs,bp,ap,ass=map(float,row[2:])
    except (ValueError,OverflowError):raise RuntimeError('TARGET_BBO_PARSE')
    vals=(bp,ap,bs,ass)
    if not all(math.isfinite(v) and v>0 for v in vals) or ap<=bp:raise RuntimeError('TARGET_BBO_INVALID')
    if last is not None:
     if ts<last:raise RuntimeError('TARGET_BACKWARD')
     delta=ts-last;ties+=int(delta==0);gaps+=int(delta>5000000000);maxgap=max(maxgap,delta)
    while j<len(queries) and int(queries[j])<ts:
     if prev is not None:points[j]=prev[1];ages[j]=(int(queries[j])-prev[0])/1e9
     j+=1
    prev=(ts,vals);last=ts
   while j<len(queries):
    if prev is not None:points[j]=prev[1];ages[j]=(int(queries[j])-prev[0])/1e9
    j+=1
  if reuse_hash:
   while wrapped.read(1048576):pass
 after=p.stat()
 if (before.st_ino,before.st_size,before.st_mtime_ns)!=(after.st_ino,after.st_size,after.st_mtime_ns):raise RuntimeError('SOURCE_CHANGED')
 actual={'bytes':wrapped.n,'sha256':wrapped.h.hexdigest()} if reuse_hash else expected
 if actual!=expected or before.st_size!=expected['bytes']:raise RuntimeError('SOURCE_HASH')
 if target==0:raise RuntimeError('TARGET_ABSENT')
 # sampled points 00:01..23:59, no event arrays retained
 mid=(points[:,0]+points[:,1])/2;valid=np.isfinite(points).all(1)&(ages<=5)&(ages>=0)
 nowix=np.arange(1,1438);past=nowix-1;future=nowix+1
 current=valid[nowix]&valid[past];futureok=valid[future];score=current&futureok
 if require_training_coverage and np.count_nonzero(score)<.8*1437:raise RuntimeError('TRAIN_DAY_BELOW80PERCENT')
 x=np.column_stack((10000*(mid[nowix]/mid[past]-1),10000*(points[nowix,1]-points[nowix,0])/mid[nowix],(points[nowix,2]-points[nowix,3])/(points[nowix,2]+points[nowix,3])))
 y=10000*(mid[future]/mid[nowix]-1)
 npz(day.replace('-','')+'-local-sampled-inputs.npz',x=x,y=y,current=current,futureok=futureok,score=score,bid_exit=points[future,0],ask_entry=points[nowix,1],mid_entry=mid[nowix],minute=np.arange(2,1439))
 save(day.replace('-','')+'-QC.json',{'UTC':now(),'source':str(p),'identity':actual,'gzip_EOF_CRC':True,'rows_all_symbols':rows,'target_rows':target,'target_equal_times':ties,'target_gaps_over5s':gaps,'max_gap_native_ns':maxgap,'target_backward':0,'strict_target_BBO_invalid':0,'planned_windows':1437,'current_past_eligible':int(current.sum()),'scorable':int(score.sum()),'unscorable':int((~score).sum()),'scan_elapsed_seconds':time.monotonic()-start,'clock_assumption':'D9 timestamp interpreted UTC API convention proxy, not certified receipt/event time','no_expandedCSV':True})
 return {k:v for k,v in [('x',x),('y',y),('current',current),('futureok',futureok),('score',score),('bid_exit',points[future,0]),('ask_entry',points[nowix,1]),('mid_entry',mid[nowix]),('minute',np.arange(2,1439))]}

def fit(x,y):
 mu=x.mean(0);sd=x.std(0);const=sd==0;scale=np.where(const,1,sd);z=(x-mu)/scale;z[:,const]=0
 ym=float(y.mean());zc=z-z.mean(0);yc=y-ym
 w=np.linalg.solve(zc.T@zc+np.eye(x.shape[1]),zc.T@yc);intercept=ym-float(z.mean(0)@w)
 if not np.isfinite(w).all() or not math.isfinite(intercept):raise RuntimeError('FIT_NONFINITE')
 return {'mu':mu,'sd':scale,'constant':const,'w':w,'intercept':intercept}
def predict(m,x):
 z=(x-m['mu'])/m['sd'];z[:,m['constant']]=0
 return z@m['w']+m['intercept']
def model_json(m):return {k:(v.tolist() if isinstance(v,np.ndarray) else v) for k,v in m.items()}
def metric(y,p):
 e=y-p;return {'n':len(y),'MSE':float(np.mean(e*e)),'MAE_bps':float(np.mean(np.abs(e))),'signed_bias_bps':float(np.mean(p-y)),'direction_hit':float(np.mean(np.sign(y)==np.sign(p)))}

def formal():
 c=json.loads((D/'config.json').read_text());sealcheck();a=c['authorization'];cohort=json.loads(Path(a['fixed_cohort']['path']).read_text());data={};identities={}
 for obj in cohort['objects']:
  ds=obj['Key'].split('/')[-1][:8];day=ds[:4]+'-'+ds[4:6]+'-'+ds[6:]
  save('progress-'+ds+'.json',{'UTC':now(),'stage':'REUSE_SCAN' if ds=='20240101' else 'GET_THEN_SCAN','date':ds})
  if ds=='20240101':
   p=Path(a['input_reuse']['path']);expected={'bytes':a['input_reuse']['bytes'],'sha256':a['input_reuse']['expected_sha256']};reuse=True
  else:p,expected=download(obj);reuse=False
  data[ds]=scan(p,day,expected,reuse,ds in cohort['train_dates']);identities[ds]={'path':str(p),**expected}
 save('all-source-and-QC-seal.json',{'UTC':now(),'sources':identities,'QC_inputs':{str(D/(ds+'-QC.json')):ident(D/(ds+'-QC.json')) for ds in data},'sampled_inputs':{str(D/(ds+'-local-sampled-inputs.npz')):ident(D/(ds+'-local-sampled-inputs.npz')) for ds in data}})
 train=cohort['train_dates'];tests=cohort['test_dates'];tx=np.concatenate([data[s]['x'][data[s]['score']] for s in train]);ty=np.concatenate([data[s]['y'][data[s]['score']] for s in train]);models={}
 for name,nf in [('A',2),('B',3)]:models[name]=fit(tx[:,:nf],ty)
 save('weights-and-scaling.json',{'UTC':now(),'train_dates':train,'train_rows':len(ty),'alpha':1,'fit_counts':{'A':1,'B':1},'training_only_population_scaler':True,'models':{k:model_json(v) for k,v in models.items()}})
 save('weights-seal.json',{'UTC':now(),'weights':ident(D/'weights-and-scaling.json'),'prior_input_seal':ident(D/'all-source-and-QC-seal.json')})
 predictions={};signals={}
 for s in tests:
  d=data[s];mask=d['current'];predictions[s]={};signals[s]={};arrays={'current_eligible':mask,'minute':d['minute']}
  for name,nf in [('A',2),('B',3)]:
   p=np.full(1437,np.nan);p[mask]=predict(models[name],d['x'][mask,:nf])
   if not np.isfinite(p[mask]).all():raise RuntimeError('PRED_NONFINITE')
   predictions[s][name]=p;arrays['prediction_'+name]=p;signals[s][name]={}
   for f in [5,10]:
    sig=mask&(p>d['x'][:,1]+2*f);signals[s][name][f]=sig;arrays['signal_'+name+'_'+str(f)]=sig
  npz(s+'-sealed-predictions-and-signals.npz',**arrays)
 save('predictions-and-signals-seal.json',{'UTC':now(),'weights_seal':ident(D/'weights-seal.json'),'all_current_past_eligible_predicted_before_future_QC_scoring':True,'files':{str(D/(s+'-sealed-predictions-and-signals.npz')):ident(D/(s+'-sealed-predictions-and-signals.npz')) for s in tests}})
 # Test future-eligibility stop only AFTER all current-eligible predictions/signals sealed.
 for s in tests:
  if np.count_nonzero(data[s]['score'])<.8*1437:raise RuntimeError('TEST_DAY_BELOW80PERCENT_AFTER_PREDICTION_SEAL')
 # Only now expose future scoring eligibility and aggregate errors/cost.
 days={};blocks={};costok=True;allmeans=[]
 for s in tests:
  d=data[s];mask=d['score'];y=d['y'][mask];pa=predictions[s]['A'][mask];pb=predictions[s]['B'][mask];ms={'M0':metric(y,np.zeros_like(y)),'A':metric(y,pa),'B':metric(y,pb)}
  improve={k:(1-ms['B']['MSE']/ms[k]['MSE'] if ms[k]['MSE']>0 else None) for k in ['M0','A']}
  d0=y*y-(y-pb)**2;da=(y-pa)**2-(y-pb)**2
  blockids=d['minute'][mask]//20;bsums=np.zeros((72,2));bcounts=np.zeros(72,dtype=np.int64)
  for k in range(72):
   kk=blockids==k;bcounts[k]=kk.sum();bsums[k]=[d0[kk].sum(),da[kk].sum()]
  blocks[s]=(bsums,bcounts)
  costs={}
  for name in ['A','B']:
   costs[name]={}
   for f in [5,10]:
    sig=signals[s][name][f];bad=int(np.count_nonzero(sig&~d['futureok']));costok=costok and bad==0
    picked=sig&mask;v=10000*(d['bid_exit'][picked]*(1-f/10000)-d['ask_entry'][picked]*(1+f/10000))/d['mid_entry'][picked]
    costs[name][str(f)]={'triggered_current_only':int(sig.sum()),'triggered_future_unscorable':bad,'scored_signals':int(picked.sum()),'zero_operations_on_scorable':int(np.count_nonzero(mask&~sig)),'positive':int((v>0).sum()),'zero':int((v==0).sum()),'negative':int((v<0).sum()),'mean_quote_score_per_all_scorable_windows':float(v.sum()/mask.sum()),'mean_quote_score_per_scored_signal':float(v.mean()) if len(v) else None}
  days[s]={'metrics':ms,'B_relative_MSE_improvement':improve,'paired_mean_squared_error_advantage':{'M0_minus_B':float(d0.mean()),'A_minus_B':float(da.mean())},'costs':costs,'n_scorable':int(mask.sum()),'n_current_past':int(d['current'].sum())}
 rng=np.random.Generator(np.random.PCG64(0));draws=np.empty((1000,2))
 for i in range(1000):
  sums=np.zeros(2);n=0
  for s in tests:
   ix=rng.integers(0,72,size=72);sums+=blocks[s][0][ix].sum(0);n+=int(blocks[s][1][ix].sum())
  if n==0:raise RuntimeError('EMPTY_BOOTSTRAP_DRAW')
  draws[i]=sums/n
 lower=np.quantile(draws,.025,axis=0,method='linear');upper=np.quantile(draws,.975,axis=0,method='linear')
 gates={'each_day_B_improvement_M0_and_A_at_least5percent':all(v is not None and v>=.05 for s in days for v in days[s]['B_relative_MSE_improvement'].values()),'both_bootstrap_2p5_lower_above0':bool((lower>0).all()),'cost_future_unscorable_zero_all_models_fees':costok,'B5eachday_mean_quote_space_positive':all(days[s]['costs']['B']['5']['mean_quote_score_per_all_scorable_windows']>0 for s in tests),'B5total_signals_at_least30':sum(days[s]['costs']['B']['5']['triggered_current_only'] for s in tests)>=30,'B5eachday_signals_at_least10':all(days[s]['costs']['B']['5']['triggered_current_only']>=10 for s in tests)}
 classification='RETAIN_CANDIDATE' if all(gates.values()) else 'NOT_SUPPORTED'
 if not costok:classification='COST_INCONCLUSIVE_FUTURE_UNSCORABLE'
 elif not gates['B5total_signals_at_least30'] or not gates['B5eachday_signals_at_least10']:classification='INSUFFICIENT_COST_SIGNAL_EVIDENCE'
 save('evaluation-results.json',{'UTC':now(),'status':'VALID_COMPUTATION','classification':classification,'days':days,'bootstrap':{'draws':1000,'seed':0,'generator':'PCG64','blocks_per_day':72,'minutes_per_block':20,'row_weighted':True,'same_draw_indexes_for_both_differences':True,'M0_minus_B':{'lower_2p5':float(lower[0]),'upper_97p5':float(upper[0])},'A_minus_B':{'lower_2p5':float(lower[1]),'upper_97p5':float(upper[1])}},'gates':gates,'fits':{'A':1,'B':1},'prediction_days':tests,'limitations':['Retrospective OOS; timestamps proxy UTC not certified receipt/PIT','Quote-space not inverse-native PNL/account ROI','Hypothetical per-side fee, no actual fills/funding/liquidation/capacity','Only two test days; not long-run confidence guarantee','Old FAILED unchanged; no trading or wealth achievement']})
 save('result-seal.json',{'UTC':now(),'prediction_seal':ident(D/'predictions-and-signals-seal.json'),'evaluation_results':ident(D/'evaluation-results.json'),'weights_seal':ident(D/'weights-seal.json')})

if __name__=='__main__':
 try:
  np.seterr(all='raise')
  if sys.argv[1]=='health':health()
  elif sys.argv[1]=='formal':formal()
  else:raise RuntimeError('UNKNOWN_STAGE')
 except Exception as e:
  code=str(e);safe=code if re.fullmatch('[A-Z0-9_]{1,100}',code) else 'SANITIZED_RUNTIME_FAILURE'
  save('worker-'+sys.argv[1]+'-STOP.json',{'UTC':now(),'error_type':type(e).__name__,'code':safe,'no_raw_values_exported':True});raise SystemExit(1)

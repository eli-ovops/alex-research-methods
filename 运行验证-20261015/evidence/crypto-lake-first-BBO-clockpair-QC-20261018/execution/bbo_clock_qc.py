"""Local-only, one six-column passive BBO/clock-pair QC; never emits quotes."""
from pathlib import Path
import sys,os,json,time,datetime,hashlib,subprocess,math
D=Path(__file__).absolute().parent;CAP=8388608;UTC=datetime.timezone.utc

def now():return datetime.datetime.now(UTC).isoformat()
def identity(p):
 b=p.read_bytes();return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def used():return sum(p.stat().st_size for p in D.rglob('*') if p.is_file())
def save(n,x):
 b=(json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode()
 if used()+len(b)>CAP:raise RuntimeError('DISK_BEFORE_WRITE')
 with (D/n).open('xb') as f:f.write(b)
def sealcheck():
 x=json.loads((D/'source-seal.json').read_text())
 for p,v in x['inputs'].items():
  if identity(Path(p))!=v:raise RuntimeError('SEALED_INPUT_MISMATCH')
 return x

def worker():
 c=json.loads((D/'config.json').read_text());sealcheck();source=Path(c['source']['path']);before=source.stat()
 if before.st_size!=c['source']['bytes']:raise RuntimeError('SOURCE_SIZE_MISMATCH')
 h=hashlib.sha256();read=0
 with source.open('rb') as f:
  while True:
   b=f.read(1048576)
   if not b:break
   h.update(b);read+=len(b)
 if read!=c['source']['bytes'] or h.hexdigest()!=c['source']['sha256']:raise RuntimeError('SOURCE_SHA_MISMATCH')
 save('source-identity-before-decode.json',{'UTC':now(),'path':str(source),'bytes':read,'sha256':h.hexdigest(),'full_hash_passes':1,'original_not_copied':True})
 import pyarrow as pa
 import pyarrow.parquet as pq
 if pa.__version__!='26.0.0':raise RuntimeError('DEPENDENCY_MISMATCH')
 pa.set_cpu_count(2);pa.set_io_thread_count(2)
 f=pq.ParquetFile(source);cols=c['columns_exact']
 if any(n not in f.schema.names for n in cols):raise RuntimeError('MISSING_COLUMN')
 for n in cols:
  expected='INT64' if n in cols[:2] else 'DOUBLE'
  if f.schema.column(f.schema.names.index(n)).physical_type!=expected:raise RuntimeError('TYPE_MISMATCH')
 quotes=cols[2:];stats={n:{'null':0,'nonfinite':0,'negative':0,'zero':0,'finite_positive':0} for n in quotes};issues={};rows=0;batches=0;valid=0;locked=0;crossed=0;positiveprices=0
 bounds=[1000000,10000000,100000000,250000000,1000000000]
 labels=['(0,1000000]','(1000000,10000000]','(10000000,100000000]','(100000000,250000000]','(250000000,1000000000]','>1000000000']
 pair={'invalid':0,'valid':0,'negative':0,'zero':0,'positive':0,'min_delta_native':None,'max_delta_native':None,'positive_delta_buckets_native':{n:0 for n in labels},'negative_magnitude_buckets_native':{n:0 for n in labels}}
 dayhour=int(datetime.datetime(2022,10,1,tzinfo=UTC).timestamp())//3600
 hourly={str(dayhour+i):{'rows':0,'strict_valid_BBO':0,'negative_clock':0,'zero_clock':0,'positive_clock':0,'invalid_clock':0} for i in range(24)}
 outside={'nonpositive_or_null_timestamp':0,'outside_source_day_conditional_ns':0}
 def pointer(reason):
  v=issues.setdefault(reason,[])
  if len(v)<5:v.append(rows)
 def bucket(v):
  for j,b in enumerate(bounds):
   if v<=b:return labels[j]
  return labels[-1]
 for batch in f.iter_batches(batch_size=50000,columns=cols,use_threads=False):
  if batch.schema.names!=cols:raise RuntimeError('UNEXPECTED_PROJECTION')
  values=[batch.column(j).to_pylist() for j in range(6)];batches+=1
  for k in range(batch.num_rows):
   vals=[values[j][k] for j in range(6)];t,r=vals[:2];qs=vals[2:];good=[]
   for j,n in enumerate(quotes):
    v=qs[j];s=stats[n]
    if v is None:s['null']+=1;good.append(False);pointer(n+'.null')
    elif not math.isfinite(v):s['nonfinite']+=1;good.append(False);pointer(n+'.nonfinite')
    elif v<0:s['negative']+=1;good.append(False);pointer(n+'.negative')
    elif v==0:s['zero']+=1;good.append(False);pointer(n+'.zero')
    else:s['finite_positive']+=1;good.append(True)
   pricegood=good[0] and good[2];islocked=False;iscrossed=False
   if pricegood:
    positiveprices+=1;islocked=qs[2]==qs[0];iscrossed=qs[2]<qs[0]
    if islocked:locked+=1;pointer('locked_positive_prices')
    if iscrossed:crossed+=1;pointer('crossed_positive_prices')
   state=all(good) and pricegood and qs[2]>qs[0]
   if state:valid+=1
   else:pointer('strict_invalid_state')
   hr=None
   if t is None or t<=0:outside['nonpositive_or_null_timestamp']+=1
   else:
    hr=str(t//3600000000000)
    if hr not in hourly:outside['outside_source_day_conditional_ns']+=1;hr=None
    else:hourly[hr]['rows']+=1;hourly[hr]['strict_valid_BBO']+=int(state)
   if t is None or r is None or t<=0 or r<=0:
    pair['invalid']+=1;pointer('invalid_positive_clock_pair')
    if hr is not None:hourly[hr]['invalid_clock']+=1
   else:
    if not isinstance(t,int) or not isinstance(r,int):raise RuntimeError('CLOCK_NONINTEGER')
    delta=r-t;pair['valid']+=1
    pair['min_delta_native']=delta if pair['min_delta_native'] is None else min(delta,pair['min_delta_native']);pair['max_delta_native']=delta if pair['max_delta_native'] is None else max(delta,pair['max_delta_native'])
    if delta<0:
     pair['negative']+=1;pair['negative_magnitude_buckets_native'][bucket(-delta)]+=1;pointer('negative_clock_reading_difference')
     if hr is not None:hourly[hr]['negative_clock']+=1
    elif delta==0:
     pair['zero']+=1
     if hr is not None:hourly[hr]['zero_clock']+=1
    else:
     pair['positive']+=1;pair['positive_delta_buckets_native'][bucket(delta)]+=1
     if hr is not None:hourly[hr]['positive_clock']+=1
   rows+=1
 after=source.stat()
 if (before.st_size,before.st_mtime_ns,before.st_ino)!=(after.st_size,after.st_mtime_ns,after.st_ino):raise RuntimeError('SOURCE_STAT_CHANGED')
 if rows!=f.metadata.num_rows:raise RuntimeError('ROW_COUNT_MISMATCH')
 for n,s in stats.items():
  if sum(s.values())!=rows:raise RuntimeError('FIELD_COUNT_INVARIANT')
 if pair['negative']+pair['zero']+pair['positive']!=pair['valid'] or pair['valid']+pair['invalid']!=rows:raise RuntimeError('PAIR_INVARIANT')
 if sum(pair['positive_delta_buckets_native'].values())!=pair['positive'] or sum(pair['negative_magnitude_buckets_native'].values())!=pair['negative']:raise RuntimeError('BUCKET_INVARIANT')
 if sum(v['rows'] for v in hourly.values())+sum(outside.values())!=rows:raise RuntimeError('HOUR_INVARIANT')
 result={'status':'COMPLETE_LOCAL_BBO_AND_SAME_ROW_CLOCK_QC','UTC':now(),'rows_scanned':rows,'batches':batches,'columns_decoded_exact':cols,'source_identity':c['source'],'full_source_hash_before_decode_once':True,'source_stat_after_unchanged':True,'field_quality_counts':stats,'positive_price_pair_count':positiveprices,'locked_count_positive_prices':locked,'crossed_count_positive_prices':crossed,'strict_valid_state_count':valid,'strict_invalid_state_count':rows-valid,'paired_clock':pair,'hourly_counts_conditional_ns':{datetime.datetime.fromtimestamp(int(k)*3600,UTC).isoformat():v for k,v in hourly.items()},'timestamp_hour_outside_counts':outside,'first5_issue_rowindices_per_reason':issues,'count_invariants_passed':True,'definitions':{'valid_state':'All four quote values finite positive and ask_price>bid_price; descriptive only, no row deletion.','clock_delta':'Exact same-row receipt_timestamp-timestamp; native int64 difference. ns bucket/UTC reading conditional on source ns declaration. Not measured network latency, clock sync or PIT certification.','buckets':'Positive magnitude exclusive intervals, zero separately. Same fixed bounds for positive difference and magnitude of negative difference.','issues':'Zero-based original physical row index only; first5 each reason, no raw values.','no_change':'No spread/imbalance series, future shift, offset correction, sorting/fill/drop, signals/returns/models or trades.'}}
 save('BBO-clockpair-summary.json',result);save('output-seal.json',{'UTC':now(),'summary':identity(D/'BBO-clockpair-summary.json'),'source_hash_receipt':identity(D/'source-identity-before-decode.json'),'source_stat_after_unchanged':True})

def main():
 if len(sys.argv)>1 and sys.argv[1]=='_worker':worker();return
 if len(sys.argv)!=3 or sys.argv[1]!='--approval':raise RuntimeError('GATE_REQUIRED')
 seal=sealcheck();c=json.loads((D/'config.json').read_text());gatep=Path(sys.argv[2]);g=json.loads(gatep.read_text())
 if g.get('allow_BBO_clockpair_qc') is not True or g.get('source_inputs')!=seal['inputs']:raise RuntimeError('GATE_MISMATCH')
 deadline=datetime.datetime.fromisoformat(c['deadline_utc'])
 if datetime.datetime.now(UTC)>=deadline:raise RuntimeError('DEADLINE')
 with (D/'formal-started.lock').open('x') as f:json.dump({'UTC':now(),'gate':str(gatep),'identity':identity(gatep),'pid':os.getpid()},f)
 start=time.monotonic();started=now();peak=0;stop=None;env={'PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'2','OPENBLAS_NUM_THREADS':'2','MKL_NUM_THREADS':'2','VECLIB_MAXIMUM_THREADS':'2','ARROW_NUM_THREADS':'2','TMPDIR':str(D)}
 with (D/'run.stdout.txt').open('x') as o,(D/'run.stderr.txt').open('x') as e:
  child=subprocess.Popen([sys.executable,'-I','-B',str(D/'bbo_clock_qc.py'),'_worker'],stdout=o,stderr=e,env=env);save('run.live.json',{'UTC':started,'supervisor_pid':os.getpid(),'worker_pid':child.pid})
  while child.poll() is None:
   r=subprocess.run(['/bin/ps','-o','rss=','-p',str(os.getpid())+','+str(child.pid)],capture_output=True,text=True,check=True);peak=max(peak,sum(int(v) for v in r.stdout.split())*1024)
   if peak>512*1048576:stop='RSS_LIMIT'
   elif time.monotonic()-start>300:stop='COMPUTE_WALL_LIMIT'
   elif datetime.datetime.now(UTC)>=deadline:stop='UTC_DEADLINE'
   elif used()>CAP:stop='DISK_LIMIT'
   if stop:child.terminate();break
   time.sleep(.1)
  try:code=child.wait(timeout=3)
  except subprocess.TimeoutExpired:child.kill();code=child.wait()
 elapsed=time.monotonic()-start;rec={'status':'PASS' if code==0 and stop is None else 'STOP','started_UTC':started,'ended_UTC':now(),'exit_code':code,'stop':stop,'elapsed_seconds':elapsed,'supervisor_pid':os.getpid(),'worker_pid':child.pid,'sampled_combined_peak_RSS_bytes':peak,'sampling_interval_seconds':.1,'new_disk_bytes':used(),'source_seal':identity(D/'source-seal.json'),'network_requests':0,'no_active_worker':True};save('session-run.json',rec);print(json.dumps(rec));sys.exit(0 if rec['status']=='PASS' else 1)
if __name__=='__main__':main()

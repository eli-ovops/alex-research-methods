"""Single exact object acquisition and physical-order three-column QC, no quotes."""
from pathlib import Path
import sys,os,json,time,datetime,hashlib,subprocess,urllib.request,heapq,shutil
D=Path(__file__).absolute().parent
CAP=335544320
UTC=datetime.timezone.utc
def now():return datetime.datetime.now(UTC).isoformat()
def identity(p):
 b=p.read_bytes();return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def used():return sum(p.stat().st_size for p in D.rglob('*') if p.is_file())
def save(n,x):
 b=(json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode()
 if used()+len(b)>CAP:raise RuntimeError('DISK_BEFORE_JSON_WRITE')
 with (D/n).open('xb') as f:f.write(b)
def nsutc(v):
 s,n=divmod(v,1000000000)
 try:return datetime.datetime.fromtimestamp(s,UTC).strftime('%Y-%m-%dT%H:%M:%S')+f'.{n:09d}Z'
 except (OverflowError,ValueError,OSError):return 'OUT_OF_DATETIME_RANGE'
def checkseal():
 x=json.loads((D/'source-seal.json').read_text())
 for p,v in x['inputs'].items():
  if identity(Path(p))!=v:raise RuntimeError('SEALED_IDENTITY_MISMATCH')
 return x
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*a,**kw):return None

def worker():
 c=json.loads((D/'config.json').read_text());checkseal();t=c['target'];N=t['expected_total_bytes']
 import pyarrow as pa
 import pyarrow.parquet as pq
 if pa.__version__!='26.0.0':raise RuntimeError('DEPENDENCY_MISMATCH')
 pa.set_cpu_count(2);pa.set_io_thread_count(2)
 if shutil.disk_usage(D).free<CAP:raise RuntimeError('FREE_DISK_INSUFFICIENT')
 rec={'url':t['url'],'method':'GET','If-Match':t['expected_etag'],'started_UTC':now(),'body_read':False,'requests':1}
 partial=D/'source.parquet.partial';whole=hashlib.sha256();foot=hashlib.sha256();got=0;chunkcap=1048576;fs=c['acquisition']['check_prior_footer_hash'];lo=fs['offset'];hi=lo+fs['bytes']
 try:
  opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
  req=urllib.request.Request(t['url'],headers={'If-Match':t['expected_etag']})
  with opener.open(req,timeout=30) as r:
   rec.update(status=r.status,headers=dict(r.headers))
   if r.status!=200:raise RuntimeError('STATUS_NOT200')
   if r.headers.get('Content-Length')!=str(N):raise RuntimeError('LENGTH_HEADER_MISMATCH')
   if r.headers.get('ETag')!=t['expected_etag']:raise RuntimeError('ETAG_MISMATCH')
   if r.headers.get('x-amz-version-id')!=t['expected_version_id']:raise RuntimeError('VERSION_MISMATCH')
   with partial.open('xb') as f:
    while got<N:
     block=r.read(min(chunkcap,N-got));rec['body_read']=True
     if not block:raise RuntimeError('SHORT_BODY')
     if used()+len(block)>CAP:raise RuntimeError('DISK_BEFORE_STREAM_WRITE')
     a=max(got,lo);b=min(got+len(block),hi)
     if b>a:foot.update(block[a-got:b-got])
     whole.update(block);f.write(block);got+=len(block)
    if r.read(1):raise RuntimeError('OVERSIZE_BODY')
  if got!=N or foot.hexdigest()!=fs['SHA256']:raise RuntimeError('BODY_OR_FOOTER_IDENTITY')
  final=D/'source.original.parquet'
  if final.exists():raise RuntimeError('DESTINATION_EXISTS')
  partial.rename(final)
  rec.update(ended_UTC=now(),body_bytes=got,full_sha256=whole.hexdigest(),footer_stream_sha256=foot.hexdigest(),prior_footer_matched=True,path=str(final))
  save('download-receipt.json',rec)
 except Exception as e:
  rec.update(ended_UTC=now(),body_bytes=got,partial_sha256=whole.hexdigest(),error=repr(e))
  if hasattr(e,'code'):rec['status']=e.code
  save('download-error.json',rec);raise
 # Only this exact projection is decoded. No pandas/to_table/price columns.
 cols=['timestamp','receipt_timestamp','sequence_number'];f=pq.ParquetFile(final)
 if any(n not in f.schema.names for n in cols):raise RuntimeError('REQUIRED_COLUMNS_ABSENT')
 if any(f.schema.column(f.schema.names.index(n)).physical_type!='INT64' for n in cols):raise RuntimeError('CLOCK_TYPE_NOT_INT64')
 thresholds=[100000000,250000000,500000000,1000000000,5000000000,60000000000]
 gt=[250000000,1000000000,5000000000,60000000000];daystart=int(datetime.datetime(2022,10,1,tzinfo=UTC).timestamp());stats={};prev={n:None for n in cols};prevpos={n:None for n in cols};top=[]
 for n in cols:
  stats[n]={'null':0,'zero':0,'negative':0,'positive':0,'adjacent_nonnull':0,'equal':0,'backward':0,'forward':0,'min_positive_increment':None,'max_positive_increment':None,'max_negative_jump_magnitude':0,'jumps_gt1':0}
  if n!='sequence_number':stats[n].update(first_positive_UTC_ns=None,last_positive_UTC_ns=None,positive_adjacent_pairs=0,equal_positive_pairs=0,backward_positive_pairs=0,positive_delta_bucket_counts={str(t):0 for t in thresholds},positive_delta_gt60s=0,over_threshold_counts={str(t):0 for t in gt},hourly_counts_conditional_ns={},date_compatible_counts_by_unit={u:0 for u in ['s','ms','us','ns']})
 rows=0;batches=0
 for batch in f.iter_batches(batch_size=50000,columns=cols,use_threads=False):
  if batch.schema.names!=cols:raise RuntimeError('UNEXPECTED_BATCH_COLUMNS')
  values=[batch.column(j).to_pylist() for j in range(3)];batches+=1
  for k in range(batch.num_rows):
   for j,n in enumerate(cols):
    v=values[j][k];s=stats[n];p=prev[n]
    if v is None:s['null']+=1;prev[n]=None;prevpos[n]=None;continue
    if not isinstance(v,int):raise RuntimeError('NONINTEGER_DECODED')
    if v==0:s['zero']+=1
    elif v<0:s['negative']+=1
    else:s['positive']+=1
    if p is not None:
     q=v-p;s['adjacent_nonnull']+=1
     if q==0:s['equal']+=1
     elif q<0:s['backward']+=1;s['max_negative_jump_magnitude']=max(s['max_negative_jump_magnitude'],-q)
     else:
      s['forward']+=1;s['jumps_gt1']+=int(q>1)
      s['min_positive_increment']=q if s['min_positive_increment'] is None else min(q,s['min_positive_increment']);s['max_positive_increment']=q if s['max_positive_increment'] is None else max(q,s['max_positive_increment'])
    prev[n]=v
    if n=='sequence_number':continue
    if v<=0:prevpos[n]=None;continue
    if s['first_positive_UTC_ns'] is None:s['first_positive_UTC_ns']=nsutc(v)
    s['last_positive_UTC_ns']=nsutc(v)
    hour=v//3600000000000;s['hourly_counts_conditional_ns'][str(hour)]=s['hourly_counts_conditional_ns'].get(str(hour),0)+1
    for u,scale in [('s',1),('ms',1000),('us',1000000),('ns',1000000000)]:
     s['date_compatible_counts_by_unit'][u]+=int(daystart*scale<=v<(daystart+86400)*scale)
    pp=prevpos[n]
    if pp is not None:
     delta=v-pp;s['positive_adjacent_pairs']+=1
     if delta==0:s['equal_positive_pairs']+=1
     elif delta<0:s['backward_positive_pairs']+=1
     else:
      for bound in thresholds:
       if delta<=bound:s['positive_delta_bucket_counts'][str(bound)]+=1;break
      else:s['positive_delta_gt60s']+=1
      for bound in gt:s['over_threshold_counts'][str(bound)]+=int(delta>bound)
      if n=='receipt_timestamp':
       item=(delta,rows,pp,v)
       if len(top)<5:heapq.heappush(top,item)
       elif item>top[0]:heapq.heapreplace(top,item)
    prevpos[n]=v
   rows+=1
 if rows!=f.metadata.num_rows:raise RuntimeError('ROW_DECLARATION_MISMATCH')
 for n in cols:
  s=stats[n]
  if n!='sequence_number':s['hourly_counts_conditional_ns']={datetime.datetime.fromtimestamp(int(k)*3600,UTC).isoformat():v for k,v in sorted(s['hourly_counts_conditional_ns'].items(),key=lambda z:int(z[0]))}
 result={'status':'COMPLETE_THREE_COLUMN_PHYSICAL_ORDER_QC','UTC':now(),'full_source_identity':{'path':str(final),'sha256':whole.hexdigest(),'bytes':got},'rows_scanned':rows,'batches':batches,'columns_decoded_exact':cols,'batch_rows_cap':50000,'use_threads':False,'stats':stats,'top5_receipt_positive_gaps_conditional_ns':[{'row_index_right':i,'delta_ns':v,'left_UTC_conditional_ns':nsutc(a),'right_UTC_conditional_ns':nsutc(b)} for v,i,a,b in sorted(top,reverse=True)],'definitions':{'adjacent_nonnull':'Immediate physical neighbors, including zero/negative. Null resets previous; no bridge.','positive_clock_intervals':'Immediate positive clock neighbors only; zero/negative/null reset. Zero exchange time unavailable, never treated as real epoch.','buckets':'Exclusive positive-delta buckets <=100ms, (100,250]ms, (250,500]ms, (500ms,1s], (1,5]s, (5,60]s, >60s; equal/negative separately.','raw_increment_units':'Native int64 units; ns-derived fields conditional on publisher source declaration, not certified from type.','sequence_jumps':'Native number gaps are descriptive; sampled snapshots need not have consecutive exchange IDs.','contains_gaps':'Prior separate footer declaration Yes; not re-read here.'},'limits':'No price/size/other data column decoded. No actual feeddisconnect certification, clock synchronization or contemporaneous serveravailability proof. No labels/returns/model/backtest/trade.'}
 save('clock-sequence-summary.json',result)
 save('output-seal.json',{'UTC':now(),'source_identity':result['full_source_identity'],'metadata_inputs_match':True,'summary':identity(D/'clock-sequence-summary.json'),'download_receipt':identity(D/'download-receipt.json')})

def main():
 if len(sys.argv)>1 and sys.argv[1]=='_worker':worker();return
 if len(sys.argv)!=3 or sys.argv[1]!='--approval':raise RuntimeError('GATE_REQUIRED')
 cfg=json.loads((D/'config.json').read_text());seal=checkseal();gatep=Path(sys.argv[2]);gate=json.loads(gatep.read_text())
 if gate.get('allow_clock_sequence_qc') is not True or gate.get('source_inputs')!=seal['inputs']:raise RuntimeError('GATE_MISMATCH')
 deadline=datetime.datetime.fromisoformat(cfg['deadline_utc'])
 if datetime.datetime.now(UTC)>=deadline:raise RuntimeError('DEADLINE')
 with (D/'formal-started.lock').open('x') as f:json.dump({'UTC':now(),'pid':os.getpid(),'gate':str(gatep),'gate_identity':identity(gatep)},f)
 started=now();t=time.monotonic();peak=0;stop=None
 env={'PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'2','OPENBLAS_NUM_THREADS':'2','MKL_NUM_THREADS':'2','VECLIB_MAXIMUM_THREADS':'2','ARROW_NUM_THREADS':'2','TMPDIR':str(D)}
 with (D/'run.stdout.txt').open('x') as o,(D/'run.stderr.txt').open('x') as e:
  child=subprocess.Popen([sys.executable,'-I','-B',str(D/'clock_qc.py'),'_worker'],stdout=o,stderr=e,env=env)
  save('run.live.json',{'UTC':started,'supervisor_pid':os.getpid(),'worker_pid':child.pid})
  while child.poll() is None:
   r=subprocess.run(['/bin/ps','-o','rss=','-p',str(os.getpid())+','+str(child.pid)],capture_output=True,text=True,check=True);peak=max(peak,sum(int(v) for v in r.stdout.split())*1024)
   if peak>512*1048576:stop='RSS_LIMIT'
   elif time.monotonic()-t>600:stop='COMPUTE_WALL_LIMIT'
   elif datetime.datetime.now(UTC)>=deadline:stop='UTC_DEADLINE'
   elif used()>CAP:stop='DISK_LIMIT'
   if stop:child.terminate();break
   time.sleep(.1)
  try:code=child.wait(timeout=3)
  except subprocess.TimeoutExpired:child.kill();code=child.wait()
 elapsed=time.monotonic()-t
 rec={'status':'PASS' if code==0 and stop is None else 'STOP','started_UTC':started,'ended_UTC':now(),'exit_code':code,'stop':stop,'elapsed_seconds':elapsed,'supervisor_pid':os.getpid(),'worker_pid':child.pid,'sampled_combined_peak_RSS_bytes':peak,'sampling_interval_seconds':.1,'new_disk_bytes':used(),'source_seal':identity(D/'source-seal.json'),'no_active_worker':True}
 save('session-run.json',rec);print(json.dumps(rec));sys.exit(0 if rec['status']=='PASS' else 1)
if __name__=='__main__':main()

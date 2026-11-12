"""Known-footer passive QC: new scope, reused accepted tail; no data pages."""
import sys, os, json, hashlib, datetime, time, struct, subprocess, urllib.request, io
from pathlib import Path
D=Path(__file__).absolute().parent
S=D.parent/'root/scope.json'
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest(p):
 b=p.read_bytes();return {'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def save(n,x):
 raw=(json.dumps(x,indent=2,ensure_ascii=False)+'\n').encode('utf8')
 used=sum(p.stat().st_size for p in D.rglob('*') if p.is_file())
 if used+len(raw)>33554432:raise RuntimeError('DISK_LIMIT_BEFORE_JSON_WRITE')
 with (D/n).open('xb') as f:f.write(raw)
def limits(c):
 if datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(c['deadline_utc']):raise RuntimeError('UTC_DEADLINE')
 if sum(p.stat().st_size for p in D.rglob('*') if p.is_file())>33554432:raise RuntimeError('DISK_LIMIT')
def sealcheck():
 seal=json.loads((D/'source-seal.json').read_text())
 for p,v in seal['inputs'].items():
  if digest(Path(p))!=v:raise RuntimeError('SEALED_IDENTITY_MISMATCH')
 return seal
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*a,**kw):return None

def worker(mode):
 c=json.loads((D/'config.json').read_text());sealcheck();limits(c)
 import pyarrow as pa
 import pyarrow.parquet as pq
 if pa.__version__!='26.0.0':raise RuntimeError('DEPENDENCY_VERSION_MISMATCH')
 pa.set_cpu_count(2);pa.set_io_thread_count(2)
 t=c['target'];total=t['expected_total_bytes'];received=0;requests=0
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
 def get(a,b,name):
  nonlocal received,requests
  limits(c);requests+=1
  if requests>2:raise RuntimeError('REQUEST_LIMIT')
  rec={'url':t['url'],'method':'GET','Range':f'bytes={a}-{b}','If-Match':t['expected_etag'],'started_UTC':now(),'body_read':False}
  try:
   req=urllib.request.Request(t['url'],headers={'Range':rec['Range'],'If-Match':t['expected_etag']})
   with opener.open(req,timeout=25) as r:
    rec.update(status=r.status,headers=dict(r.headers))
    if r.status!=206:raise RuntimeError('STATUS_NOT206')
    expected=f'bytes {a}-{b}/{total}'
    if r.headers.get('Content-Range')!=expected:raise RuntimeError('CONTENT_RANGE_MISMATCH')
    if r.headers.get('ETag')!=t['expected_etag']:raise RuntimeError('ETAG_MISMATCH')
    if r.headers.get('x-amz-version-id')!=t['expected_version_id']:raise RuntimeError('VERSION_MISMATCH')
    if r.headers.get('Content-Length')!=str(b-a+1):raise RuntimeError('CONTENT_LENGTH_MISMATCH')
    body=r.read(b-a+1);rec['body_read']=True;received+=len(body)
    if len(body)!=b-a+1 or received>16043448:raise RuntimeError('BODY_LENGTH_OR_CAP')
   f=D/name
   used=sum(p.stat().st_size for p in D.rglob('*') if p.is_file())
   if used+len(body)>33554432:raise RuntimeError('DISK_LIMIT_BEFORE_BINARY_WRITE')
   with f.open('xb') as out:out.write(body)
   rec.update(body_path=str(f),body_bytes=len(body),body_sha256=hashlib.sha256(body).hexdigest(),ended_UTC=now())
   save(name+'.receipt.json',rec);return body
  except Exception as e:
   rec.update(error=repr(e),ended_UTC=now())
   if hasattr(e,'code'):rec['status']=e.code
   save(name+'.error.json',rec);raise
 tail=Path(c['prior_tail']['path']).read_bytes()
 if len(tail)!=8 or hashlib.sha256(tail).hexdigest()!=c['prior_tail']['sha256']:raise RuntimeError('PRIOR_TAIL_IDENTITY')
 size=struct.unpack('<I',tail[:4])[0]
 if tail[4:]!=b'PAR1' or size!=16043444:raise RuntimeError('PRIOR_FOOTER_DECLARATION_MISMATCH')
 footer=get(total-8-size,total-9,'footer.original.bin')
 header=get(0,3,'first4.original.bin')
 if header!=b'PAR1':raise RuntimeError('INVALID_HEADER_MAGIC')
 # Artificial metadata-only in-memory container; no duplicate footer on disk.
 # Original chunk offsets refer to the remote full file; data pages absent.
 wrapper=io.BytesIO(header+footer+tail)
 meta=pq.read_metadata(wrapper)
 columns=[{'name':meta.schema.column(i).name,'path':meta.schema.column(i).path,'physical_type':meta.schema.column(i).physical_type,'logical_type':str(meta.schema.column(i).logical_type),'max_definition_level':meta.schema.column(i).max_definition_level,'max_repetition_level':meta.schema.column(i).max_repetition_level} for i in range(meta.num_columns)]
 groups=[]
 for i in sorted(set(list(range(min(2,meta.num_row_groups)))+list(range(max(0,meta.num_row_groups-2),meta.num_row_groups)))):
  g=meta.row_group(i);cs=[]
  for j in range(g.num_columns):
   x=g.column(j)
   cs.append({'path':x.path_in_schema,'compression':x.compression,'encodings':list(x.encodings),'num_values':x.num_values,'data_page_offset':x.data_page_offset,'dictionary_page_offset':x.dictionary_page_offset,'total_compressed_size':x.total_compressed_size,'total_uncompressed_size':x.total_uncompressed_size})
  groups.append({'index':i,'num_rows':g.num_rows,'total_byte_size':g.total_byte_size,'columns':cs})
 result={'status':'PASS_METADATA_ONLY','UTC':now(),'target':t,'requests':requests,'application_body_bytes':received,'footer_bytes':size,'footer_start_offset':total-8-size,'num_rows_declared':meta.num_rows,'num_columns':meta.num_columns,'num_row_groups':meta.num_row_groups,'created_by':meta.created_by,'format_version':meta.format_version,'columns':columns,'row_groups':groups,'metadata_wrapper_artificial':True,'metadata_key_names_only':[k.decode('utf8','replace') for k in (meta.metadata or {})],'limits':'No row/data-page/statistics minmax decoded or disclosed; declarations not data quality, actual clock span, checksum, profit or capacity.'}
 save('metadata-summary.json',result);limits(c)
 save('output-seal.json',{'UTC':now(),'inputs':{str(D/n):digest(D/n) for n in ['footer.original.bin','first4.original.bin','metadata-summary.json']}})

def main():
 mode=sys.argv[1]
 if mode=='_worker':worker(sys.argv[2]);return
 if mode!='run':raise RuntimeError('BAD_MODE')
 seal=sealcheck();c=json.loads((D/'config.json').read_text());limits(c)
 if mode=='run':
  if len(sys.argv)!=4 or sys.argv[2]!='--approval':raise RuntimeError('GATE_REQUIRED')
  gp=Path(sys.argv[3]);gate=json.loads(gp.read_text())
  if gate.get('allow_known_footer_qc') is not True:raise RuntimeError('GATE_DENIED')
  for p,v in seal['inputs'].items():
   if gate.get('source_inputs',{}).get(p)!=v:raise RuntimeError('GATE_SOURCE_MISMATCH')
  with (D/'formal-started.lock').open('x') as f:json.dump({'UTC':now(),'pid':os.getpid(),'gate':str(gp),'gate_identity':digest(gp)},f)
 previous=0.0
 for p in D.glob('session-*.json'):
  previous+=json.loads(p.read_text()).get('elapsed_seconds',0)
 start=time.monotonic();started=now();env={'PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'2','OPENBLAS_NUM_THREADS':'2','MKL_NUM_THREADS':'2','VECLIB_MAXIMUM_THREADS':'2','NUMEXPR_NUM_THREADS':'2','ARROW_NUM_THREADS':'2','TMPDIR':str(D)}
 out=D/(mode+'.stdout.txt');err=D/(mode+'.stderr.txt');peak=0;stop=None
 with out.open('x') as o,err.open('x') as e:
  child=subprocess.Popen([sys.executable,'-I','-B',str(D/'footer_qc.py'),'_worker',mode],stdout=o,stderr=e,env=env)
  save(mode+'.live.json',{'UTC':started,'supervisor_pid':os.getpid(),'worker_pid':child.pid,'stage':mode})
  while child.poll() is None:
   elapsed=time.monotonic()-start
   rssout=subprocess.run(['/bin/ps','-o','rss=','-p',str(os.getpid())+','+str(child.pid)],capture_output=True,text=True,check=True)
   rss=sum(int(v) for v in rssout.stdout.split())*1024;peak=max(peak,rss)
   if rss>512*1048576:stop='RSS_LIMIT'
   elif elapsed+previous>300:stop='COMPUTE_LIMIT'
   elif datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(c['deadline_utc']):stop='DEADLINE'
   elif sum(p.stat().st_size for p in D.rglob('*') if p.is_file())>33554432:stop='DISK_LIMIT'
   if stop:child.terminate();break
   time.sleep(.1)
  try:code=child.wait(timeout=3)
  except subprocess.TimeoutExpired:child.kill();code=child.wait()
 elapsed=time.monotonic()-start
 rec={'status':'PASS' if code==0 and not stop else 'STOP','stage':mode,'started_UTC':started,'ended_UTC':now(),'exit_code':code,'stop':stop,'supervisor_pid':os.getpid(),'worker_pid':child.pid,'elapsed_seconds':elapsed,'previous_seconds':previous,'cumulative_seconds':previous+elapsed,'sampled_peak_combined_RSS_bytes':peak,'rss_sampling_seconds':.1,'new_disk_bytes':sum(p.stat().st_size for p in D.rglob('*') if p.is_file()),'source_seal':digest(D/'source-seal.json'),'no_active_worker':True,'scope':'Passive metadata only. No vendor SDK/model/data-page decode.'}
 save('session-'+mode+'.json',rec);print(json.dumps(rec));sys.exit(0 if rec['status']=='PASS' else 1)
if __name__=='__main__':main()

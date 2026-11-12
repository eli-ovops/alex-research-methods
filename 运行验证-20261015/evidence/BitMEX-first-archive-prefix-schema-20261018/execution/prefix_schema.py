"""One bounded anonymous prefix GET; passive CSV structure/identifiers only."""
from pathlib import Path
from collections import Counter
import sys,os,json,time,datetime,hashlib,subprocess,urllib.request,zlib,csv,re
D=Path(__file__).absolute().parent;UTC=datetime.timezone.utc;DISK=2097152

def now():return datetime.datetime.now(UTC).isoformat()
def identity(p):b=p.read_bytes();return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def used():return sum(p.stat().st_size for p in D.rglob('*') if p.is_file())
def save(n,x):
 b=(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
 if used()+len(b)>DISK:raise RuntimeError('DISK_LIMIT_BEFORE_WRITE')
 with (D/n).open('xb') as f:f.write(b)
def sealcheck():
 x=json.loads((D/'source-seal.json').read_text())
 for p,v in x['inputs'].items():
  if identity(Path(p))!=v:raise RuntimeError('SEALED_IDENTITY_MISMATCH')
 return x
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*a,**kw):return None

class PrefixLines:
 """One-byte expanded output: no decoded rows beyond requested CSV records."""
 def __init__(self,data):
  self.data=data;self.pos=0;self.pending=b'';self.dec=zlib.decompressobj(16+zlib.MAX_WBITS);self.expanded=0;self.record_bytes=0;self.reason=None;self.incomplete_line_bytes=0;self.members_ended=0
 def byte(self):
  if self.expanded>=4194304:self.reason='EXPANDED_CAP';return None
  while True:
   if not self.pending:
    if self.pos>=len(self.data):self.reason='AVAILABLE_PREFIX_EXHAUSTED';return None
    self.pending=self.data[self.pos:self.pos+4096];self.pos+=len(self.pending)
   out=self.dec.decompress(self.pending,1);self.pending=self.dec.unconsumed_tail
   if self.dec.eof:
    # A member EOF does not certify the whole99MB archive or its CRC.
    self.members_ended+=1;self.pending=self.dec.unused_data;self.dec=zlib.decompressobj(16+zlib.MAX_WBITS)
   if out:self.expanded+=1;return out
 def __iter__(self):return self
 def __next__(self):
  line=bytearray()
  while True:
   b=self.byte()
   if b is None:
    self.incomplete_line_bytes=len(line)
    raise StopIteration
   self.record_bytes+=1
   if self.record_bytes>8192:raise RuntimeError('CSV_RECORD_BYTES_LIMIT')
   line.extend(b)
   if b==b'\n':return line.decode('utf8','strict')

def worker():
 c=json.loads((D/'config.json').read_text());sealcheck();src=c['source'];rec={'url':src['url'],'method':'GET','request_range':'bytes=0-1048575','If-Match':src['ETag_expected'],'Accept-Encoding':'identity','started_UTC':now(),'body_read':False,'public_requests':1}
 try:
  op=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
  req=urllib.request.Request(src['url'],headers={'Range':'bytes=0-1048575','If-Match':src['ETag_expected'],'Accept-Encoding':'identity'})
  with op.open(req,timeout=30) as r:
   rec.update(status=r.status,headers=dict(r.headers))
   if r.status!=206:raise RuntimeError('STATUS_NOT206')
   if r.headers.get('Content-Range')!='bytes 0-1048575/99509710':raise RuntimeError('CONTENT_RANGE_MISMATCH')
   if r.headers.get('ETag')!=src['ETag_expected']:raise RuntimeError('ETAG_MISMATCH')
   if r.headers.get('Content-Length')!='1048576':raise RuntimeError('CONTENT_LENGTH_MISMATCH')
   if r.headers.get('Content-Encoding','identity').lower()!='identity':raise RuntimeError('UNEXPECTED_CONTENT_ENCODING')
   body=r.read(1048576);rec['body_read']=True
   if len(body)!=1048576:raise RuntimeError('SHORT_PREFIX_BODY')
  p=D/'localprefix.partial.gz'
  if used()+len(body)>DISK:raise RuntimeError('DISK_BEFORE_PREFIX_WRITE')
  with p.open('xb') as f:f.write(body)
  rec.update(ended_UTC=now(),body_bytes=len(body),prefix_sha256=hashlib.sha256(body).hexdigest(),prefix_path=str(p),full_gzip_SHA_CRC_verified=False)
  save('GET-receipt.json',rec)
 except Exception as e:
  rec.update(ended_UTC=now(),error=repr(e))
  if hasattr(e,'code'):rec['status']=e.code
  save('GET-error.json',rec);raise
 lines=PrefixLines(body);csv.field_size_limit(8192);reader=csv.reader(lines,strict=True)
 def record():
  lines.record_bytes=0
  return next(reader)
 try:header=record()
 except StopIteration:raise RuntimeError('NO_COMPLETE_HEADER')
 if len(header)>64:raise RuntimeError('HEADER_COLUMNS_LIMIT')
 required=['timestamp','symbol','bidSize','bidPrice','askPrice','askSize'];hc=Counter(header);missing=[x for x in required if hc[x]!=1];extras=[x for x in header if x not in required]
 ti=header.index('timestamp') if hc['timestamp']==1 else None;si=header.index('symbol') if hc['symbol']==1 else None
 widths=Counter();symbols=Counter();formats=Counter();fractions=Counter();dates={'matches_2024_01_01':0,'does_not_match':0,'not_inspected_due_width_or_header':0};rows=0;badwidth=0;stop=None;incomplete_csv=False
 def fmt(s):
  if re.fullmatch(r'\d{4}-\d{2}-\d{2}D\d{2}:\d{2}:\d{2}(?:\.\d+)?',s):return 'YYYY-MM-DDDhh:mm:ss[.fraction]_nozone'
  if re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z',s):return 'ISO_T_Z'
  if re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?[+-]\d{2}:?\d{2}',s):return 'ISO_T_numericzone'
  if re.fullmatch(r'\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?',s):return 'date_time_nozone'
  return 'OTHER_OR_EMPTY'
 while rows<1000:
  try:r=record()
  except StopIteration:stop=lines.reason or 'AVAILABLE_PREFIX_EXHAUSTED';break
  except csv.Error:
   if lines.reason in ['AVAILABLE_PREFIX_EXHAUSTED','EXPANDED_CAP']:stop=lines.reason;incomplete_csv=True;break
   raise
  if len(r)>64:raise RuntimeError('DATA_COLUMNS_LIMIT')
  rows+=1;widths[str(len(r))]+=1
  if len(r)!=len(header):badwidth+=1;dates['not_inspected_due_width_or_header']+=1;continue
  if si is not None:symbols[r[si]]+=1
  if ti is not None:
   s=r[ti];formats[fmt(s)]+=1;dates['matches_2024_01_01' if s.startswith('2024-01-01') else 'does_not_match']+=1
   m=re.search(r'\.(\d+)',s)
   fractions[str(len(m.group(1))) if m else 'none']+=1
  else:dates['not_inspected_due_width_or_header']+=1
 if rows==1000:stop='1000_COMPLETE_RECORD_CAP'
 if sum(widths.values())!=rows:raise RuntimeError('COUNT_INVARIANT')
 out={'status':'COMPLETE_BOUNDED_PREFIX_STRUCTURE_ONLY','UTC':now(),'header_exact':header,'header_column_count':len(header),'required_unique_ok':not missing,'missing_or_nonunique_required':missing,'extra_columns':extras,'complete_records_after_header':rows,'field_width_counts':dict(widths),'width_mismatch_records':badwidth,'symbols':{'exact_XBTUSD_count':symbols['XBTUSD'],'exact_XBT_USDT_count':symbols['XBT_USDT'],'unique_count':len(symbols),'sorted_unique_identifiers_first20':sorted(symbols)[:20],'identifier_list_truncated':len(symbols)>20,'presence_scope':'Only inspectedprefixrecords, not entirefile/day orproductmapping'},'timestamp_string_format_counts':dict(formats),'fractional_digit_count_histogram':dict(fractions),'date_prefix_counts':dates,'decode':{'expanded_bytes_exact':lines.expanded,'stop_reason':stop,'incomplete_trailing_line_bytes_if_encountered':lines.incomplete_line_bytes,'incomplete_CSV_record_if_encountered':incomplete_csv,'gzip_members_ended_if_encountered':lines.members_ended,'flush_called':False,'whole_gzip_EOF_CRC_verified':False,'price_size_numeric_parse':False,'raw_decoded_records_saved':False},'prefix_identity':{'bytes':len(body),'sha256':rec['prefix_sha256'],'source_total_bytes_declared':99509710},'limits':['Only prefix structure/identifier/stringformat; no fullfilequality/datecoverage/symbolabsence conclusion.','Timestampformat/dateprefix do not prove UTC, exchangeevent vsreceiverclock or liveavailability.','No price/size numeric parsing/output, rawrecords/time arrays, features/futurelabels/financialcalculation/model/trades.','Officialmonitoring/research publication basis supports limited local sourceinspection, not blanketML/externalAI/commercialrights.']}
 save('schema-summary.json',out);save('output-seal.json',{'UTC':now(),'prefix':identity(p),'receipt':identity(D/'GET-receipt.json'),'summary':identity(D/'schema-summary.json'),'source_seal':identity(D/'source-seal.json')})

def main():
 if len(sys.argv)>1 and sys.argv[1]=='_worker':worker();return
 if len(sys.argv)!=3 or sys.argv[1]!='--approval':raise RuntimeError('GATE_REQUIRED')
 s=sealcheck();c=json.loads((D/'config.json').read_text());gp=Path(sys.argv[2]);g=json.loads(gp.read_text());deadline=datetime.datetime.fromisoformat(c['deadline_utc'])
 if g.get('allow_prefix_schema_qc') is not True or g.get('source_inputs')!=s['inputs']:raise RuntimeError('GATE_MISMATCH')
 if datetime.datetime.now(UTC)>=deadline:raise RuntimeError('DEADLINE')
 with (D/'formal-started.lock').open('x') as f:json.dump({'UTC':now(),'gate':str(gp),'identity':identity(gp),'pid':os.getpid()},f)
 start=time.monotonic();started=now();peak=0;stop=None;env={'PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'2','OPENBLAS_NUM_THREADS':'2','MKL_NUM_THREADS':'2','VECLIB_MAXIMUM_THREADS':'2','TMPDIR':str(D)}
 with (D/'run.stdout.txt').open('x') as o,(D/'run.stderr.txt').open('x') as e:
  child=subprocess.Popen([sys.executable,'-I','-B','-S',str(D/'prefix_schema.py'),'_worker'],stdout=o,stderr=e,env=env);save('run.live.json',{'UTC':started,'supervisor_pid':os.getpid(),'worker_pid':child.pid})
  while child.poll() is None:
   q=subprocess.run(['/bin/ps','-o','rss=','-p',str(os.getpid())+','+str(child.pid)],capture_output=True,text=True,check=True);peak=max(peak,sum(int(v) for v in q.stdout.split())*1024)
   if peak>268435456:stop='RSS_LIMIT'
   elif time.monotonic()-start>300:stop='COMPUTE_LIMIT'
   elif datetime.datetime.now(UTC)>=deadline:stop='DEADLINE'
   elif used()>DISK:stop='DISK_LIMIT'
   if stop:child.terminate();break
   time.sleep(.1)
  try:code=child.wait(timeout=3)
  except subprocess.TimeoutExpired:child.kill();code=child.wait()
 elapsed=time.monotonic()-start;out={'status':'PASS' if code==0 and stop is None else 'STOP','started_UTC':started,'ended_UTC':now(),'exit_code':code,'stop':stop,'elapsed_seconds':elapsed,'sampled_combined_peak_RSS_bytes':peak,'sampling_interval_seconds':.1,'supervisor_pid':os.getpid(),'worker_pid':child.pid,'disk_bytes':used(),'source_seal':identity(D/'source-seal.json'),'no_active_worker':True};save('session-run.json',out);print(json.dumps(out));sys.exit(0 if out['status']=='PASS' else 1)
if __name__=='__main__':main()

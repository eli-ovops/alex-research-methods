"""Fixed complete archive inventory and exactXBTUSD quality counts, no quotes export."""
from pathlib import Path
from collections import Counter
import sys,os,json,time,datetime,hashlib,subprocess,urllib.request,gzip,csv,re,math
D=Path(__file__).absolute().parent;UTC=datetime.timezone.utc;DISK=134217728

def now():return datetime.datetime.now(UTC).isoformat()
def identity(p):b=p.read_bytes();return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def used():return sum(p.stat().st_size for p in D.rglob('*') if p.is_file())
def save(n,x):
 b=(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
 if used()+len(b)>DISK:raise RuntimeError('DISK_BEFORE_WRITE')
 with (D/n).open('xb') as f:f.write(b)
def sealcheck():
 x=json.loads((D/'source-seal.json').read_text())
 for p,v in x['inputs'].items():
  if identity(Path(p))!=v:raise RuntimeError('SEALED_INPUT_MISMATCH')
 return x
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*a,**kw):return None
class BoundedLines:
 def __init__(self,g):self.g=g;self.expanded=0;self.record_bytes=0;self.eof=False;self.last_line_newline=None
 def __iter__(self):return self
 def __next__(self):
  remaining=4294967296-self.expanded
  if remaining<=0:raise RuntimeError('EXPANDED_CAP')
  b=self.g.readline(min(8193,remaining))
  if not b:self.eof=True;raise StopIteration
  self.expanded+=len(b);self.record_bytes+=len(b)
  if self.record_bytes>8192:raise RuntimeError('RECORD_BYTES_CAP')
  self.last_line_newline=b.endswith(b'\n')
  return b.decode('utf8','strict')

def clock_class(s):
 if re.fullmatch(r'\d{4}-\d{2}-\d{2}D\d{2}:\d{2}:\d{2}\.\d{9}',s):
  try:datetime.datetime(int(s[:4]),int(s[5:7]),int(s[8:10]),int(s[11:13]),int(s[14:16]),int(s[17:19]))
  except ValueError:return 'D9_INVALID_CALENDAR_OR_TIME',False
  return 'CANONICAL_FIXEDWIDTH_D9_NOZONE',True
 if re.fullmatch(r'\d{4}-\d{2}-\d{2}D\d{2}:\d{2}:\d{2}(?:\.\d+)?',s):return 'D_OTHER_FRACTION_OR_NONE_NOZONE',False
 return 'OTHER_OR_EMPTY',False

def worker():
 c=json.loads((D/'config.json').read_text());sealcheck();src=c['source'];N=src['expected_bytes'];got=0;whole=hashlib.sha256();prefix=hashlib.sha256();partial=D/'source.partial.gz'
 rec={'url':src['url'],'method':'GET','If-Match':src['expected_ETag'],'Accept-Encoding':'identity','started_UTC':now(),'body_read':False,'requests':1}
 try:
  op=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect());req=urllib.request.Request(src['url'],headers={'If-Match':src['expected_ETag'],'Accept-Encoding':'identity'})
  with op.open(req,timeout=30) as r:
   rec.update(status=r.status,headers=dict(r.headers))
   if r.status!=200:raise RuntimeError('STATUS_NOT200')
   if r.headers.get('Content-Length')!=str(N):raise RuntimeError('CONTENT_LENGTH_MISMATCH')
   if r.headers.get('ETag')!=src['expected_ETag']:raise RuntimeError('ETAG_MISMATCH')
   if r.headers.get('Content-Encoding','identity').lower()!='identity':raise RuntimeError('CONTENT_ENCODING_MISMATCH')
   with partial.open('xb') as f:
    while got<N:
     b=r.read(min(1048576,N-got));rec['body_read']=True
     if not b:raise RuntimeError('SHORT_BODY')
     if used()+len(b)>DISK:raise RuntimeError('DISK_BEFORE_STREAM_WRITE')
     if got<1048576:prefix.update(b[:min(len(b),1048576-got)])
     whole.update(b);f.write(b);got+=len(b)
    if r.read(1):raise RuntimeError('OVERSIZE_BODY')
  if got!=N or prefix.hexdigest()!=src['expected_first1048576_SHA256']:raise RuntimeError('BODY_OR_PREFIX_IDENTITY_MISMATCH')
  p=D/'source.original.csv.gz'
  if p.exists():raise RuntimeError('DESTINATION_EXISTS')
  partial.rename(p);rec.update(ended_UTC=now(),bytes=got,full_SHA256=whole.hexdigest(),first1048576_SHA256=prefix.hexdigest(),prior_prefix_matched_before_decode=True,path=str(p));save('download-receipt.json',rec)
 except Exception as e:
  rec.update(ended_UTC=now(),bytes=got,partial_SHA256=whole.hexdigest(),error_type=type(e).__name__)
  if hasattr(e,'code'):rec['status']=e.code
  code=str(e);rec['code']=code if re.fullmatch('[A-Z0-9_]{1,96}',code) else 'IO_OR_RESPONSE_ERROR'
  save('download-error.json',rec);raise
 counts=Counter();widths=Counter();total=0;repeat=0;badwidth=0;empty=0;normal=0;target=0;linezero=0;clockprev=None
 fields=['bidSize','bidPrice','askPrice','askSize'];stats={k:{'empty':0,'parseerror':0,'nonfinite':0,'negative':0,'zero':0,'finitepositive':0} for k in fields};positiveprices=0;locked=0;crossed=0;strictvalid=0;formats=Counter();dates={'matches_2024_01_01':0,'does_not_match':0};clock={'canonical_D9':0,'other_or_bad':0,'adjacent_canonical_target_pairs':0,'equal':0,'backwards':0,'forwards':0,'policy':'Adjacent physical target observations; bad targetclock/unknown-width/emptyidentifier/repeatedheader resets previous. Other valid symbols do not reset target adjacency.'}
 before=p.stat();csv.field_size_limit(8192)
 with gzip.open(p,'rb') as gz:
  lines=BoundedLines(gz);reader=csv.reader(lines,strict=True)
  def record():lines.record_bytes=0;return next(reader)
  header=record()
  if header!=src['exact_header'] or len(header)>64 or any(header.count(k)!=1 for k in src['exact_header']):raise RuntimeError('HEADER_NOT_EXACT_UNIQUE')
  ix={k:header.index(k) for k in header}
  while True:
   try:r=record()
   except StopIteration:break
   total+=1;widths[str(len(r))]+=1
   if len(r)>64:raise RuntimeError('COLUMNS_CAP')
   if r==header:repeat+=1;clockprev=None;continue
   if len(r)!=len(header):badwidth+=1;linezero+=int(len(r)==0);clockprev=None;continue
   normal+=1;sym=r[ix['symbol']]
   if len(sym)>128:raise RuntimeError('SYMBOL_LENGTH_CAP')
   if sym=='':empty+=1;clockprev=None;continue
   counts[sym]+=1
   if len(counts)>4096:raise RuntimeError('UNIQUE_SYMBOL_CAP')
   if sym!='XBTUSD':continue
   target+=1;vals={};positive={}
   for k in fields:
    token=r[ix[k]];s=stats[k]
    if token.strip()=='':s['empty']+=1;positive[k]=False;continue
    try:v=float(token)
    except (ValueError,OverflowError):s['parseerror']+=1;positive[k]=False;continue
    vals[k]=v
    if not math.isfinite(v):s['nonfinite']+=1;positive[k]=False
    elif v<0:s['negative']+=1;positive[k]=False
    elif v==0:s['zero']+=1;positive[k]=False
    else:s['finitepositive']+=1;positive[k]=True
   prices=positive['bidPrice'] and positive['askPrice']
   if prices:
    positiveprices+=1;locked+=int(vals['askPrice']==vals['bidPrice']);crossed+=int(vals['askPrice']<vals['bidPrice'])
   if all(positive.values()) and vals['askPrice']>vals['bidPrice']:strictvalid+=1
   stamp=r[ix['timestamp']];fc,ok=clock_class(stamp);formats[fc]+=1;dates['matches_2024_01_01' if stamp.startswith('2024-01-01') else 'does_not_match']+=1
   if ok:
    clock['canonical_D9']+=1
    if clockprev is not None:
     clock['adjacent_canonical_target_pairs']+=1;clock['equal' if stamp==clockprev else 'backwards' if stamp<clockprev else 'forwards']+=1
    clockprev=stamp
   else:clock['other_or_bad']+=1;clockprev=None
  if not lines.eof:raise RuntimeError('NO_DECODED_EOF')
  expanded=lines.expanded;lastnewline=lines.last_line_newline
 after=p.stat()
 if (before.st_size,before.st_mtime_ns,before.st_ino)!=(after.st_size,after.st_mtime_ns,after.st_ino):raise RuntimeError('SOURCE_CHANGED')
 if total!=repeat+badwidth+normal or normal!=empty+sum(counts.values()) or sum(widths.values())!=total:raise RuntimeError('INVENTORY_INVARIANT')
 if target!=counts['XBTUSD'] or any(sum(v.values())!=target for v in stats.values()) or sum(formats.values())!=target or sum(dates.values())!=target:raise RuntimeError('TARGET_COUNT_INVARIANT')
 if clock['equal']+clock['backwards']+clock['forwards']!=clock['adjacent_canonical_target_pairs']:raise RuntimeError('CLOCK_COUNT_INVARIANT')
 result={'status':'COMPLETE_FULL_FIXED_FILE_SYMBOL_INVENTORY_AND_TARGET_QC','UTC':now(),'source_identity':{'path':str(p),'bytes':N,'sha256':whole.hexdigest(),'first1048576_sha256':prefix.hexdigest()},'gzip_EOF_trailer_CRC_verified':True,'decodedstream_EOF':True,'expanded_bytes':expanded,'last_physical_line_newline':lastnewline,'expanded_CSV_persisted':False,'header_exact':header,'CSV_records_after_initial_header':total,'field_width_counts':dict(widths),'malformed_width_records':badwidth,'empty_physical_CSV_records_subset':linezero,'repeated_header_records':repeat,'normal_width_nonrepeat_records':normal,'empty_identifier_records':empty,'unique_nonempty_symbols':len(counts),'symbol_counts_exact':dict(sorted(counts.items())),'target_exact_XBTUSD':{'rows':target,'present_complete_file':target>0,'numeric_field_counts':stats,'positive_price_pair_count':positiveprices,'locked_count_positive_prices':locked,'crossed_count_positive_prices':crossed,'strict_valid_state_count':strictvalid,'strict_invalid_state_count':target-strictvalid,'timestamp_format_counts':dict(formats),'date_prefix_counts':dates,'lexical_clock_QC':clock},'count_invariants_passed':True,'limits':['Fixedcomplete2024-01-01file only; not otherfiles/currentmarket or stablequality.','No rawprice/qty/timearrays/statistics or decodedrecords exported; numericalcategories only.','D9stringshape/lexicalorder/dateprefix do not certifyUTC,event-vs-receiveclock,realprecision,PIT or feedcontinuity.','XBTUSDpresence here not fullhistoricalspec/units or spot; no fallbackasset used.','Researchpublication scope limited; fullML/commercial/externalAIrightsPARTIAL.','No feature/label/cost/return/model/account/backtest/trade/payment.']}
 save('inventory-summary.json',result);save('output-seal.json',{'UTC':now(),'source_stream_identity':result['source_identity'],'download_receipt':identity(D/'download-receipt.json'),'summary':identity(D/'inventory-summary.json'),'source_seal':identity(D/'source-seal.json')})

def main():
 if len(sys.argv)>1 and sys.argv[1]=='_worker':
  try:worker()
  except Exception as e:
   msg=str(e);code=msg if re.fullmatch('[A-Z0-9_]{1,96}',msg) else 'SANITIZED_PARSE_OR_IO_FAILURE'
   save('worker-error.json',{'UTC':now(),'error_type':type(e).__name__,'code':code,'raw_cells_or_error_message_not_exported':True});sys.exit(1)
  return
 if len(sys.argv)!=3 or sys.argv[1]!='--approval':raise RuntimeError('GATE_REQUIRED')
 s=sealcheck();c=json.loads((D/'config.json').read_text());gp=Path(sys.argv[2]);g=json.loads(gp.read_text());deadline=datetime.datetime.fromisoformat(c['deadline_utc'])
 if g.get('allow_fullquote_symbol_qc') is not True or g.get('source_inputs')!=s['inputs']:raise RuntimeError('GATE_MISMATCH')
 if datetime.datetime.now(UTC)>=deadline:raise RuntimeError('DEADLINE')
 with (D/'formal-started.lock').open('x') as f:json.dump({'UTC':now(),'pid':os.getpid(),'gate':str(gp),'gate_identity':identity(gp)},f)
 start=time.monotonic();started=now();peak=0;stop=None;env={'PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'2','OPENBLAS_NUM_THREADS':'2','MKL_NUM_THREADS':'2','VECLIB_MAXIMUM_THREADS':'2','TMPDIR':str(D)}
 with (D/'run.stdout.txt').open('x') as o,(D/'run.stderr.txt').open('x') as e:
  child=subprocess.Popen([sys.executable,'-I','-B','-S',str(D/'fullquote_qc.py'),'_worker'],stdout=o,stderr=e,env=env)
  try:
   save('run.live.json',{'UTC':started,'supervisor_pid':os.getpid(),'worker_pid':child.pid})
   while child.poll() is None:
    q=subprocess.run(['/bin/ps','-o','rss=','-p',str(os.getpid())+','+str(child.pid)],capture_output=True,text=True,check=True);peak=max(peak,sum(int(v) for v in q.stdout.split())*1024)
    if peak>268435456:stop='RSS_LIMIT'
    elif time.monotonic()-start>300:stop='COMPUTE_LIMIT'
    elif datetime.datetime.now(UTC)>=deadline:stop='DEADLINE'
    elif used()>DISK:stop='DISK_LIMIT'
    if stop:break
    time.sleep(.1)
  except Exception as e:
   stop='SUPERVISOR_EXCEPTION_'+type(e).__name__
  finally:
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

 elapsed=time.monotonic()-start;rec={'status':'PASS' if code==0 and stop is None else 'STOP','started_UTC':started,'ended_UTC':now(),'exit_code':code,'stop':stop,'elapsed_seconds':elapsed,'sampled_combined_peak_RSS_bytes':peak,'sampling_interval_seconds':.1,'supervisor_pid':os.getpid(),'worker_pid':child.pid,'disk_bytes':used(),'source_seal':identity(D/'source-seal.json'),'no_active_worker':True};save('session-run.json',rec);print(json.dumps(rec));sys.exit(0 if rec['status']=='PASS' else 1)
if __name__=='__main__':main()

import urllib.request, urllib.error, ssl, json, hashlib, re, time, datetime, pathlib, decimal
D=pathlib.Path('/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/liquity-oct-completed-task-demand-20261020'); O=D/'source-owner'
p=json.loads((D/'root/protocol.json').read_text()); deadline=1792448700
# Fixed UTC deadline from sealed protocol; calendar conversion only.
deadline=datetime.datetime.strptime(p['pagination']['deadline_utc'],'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc).timestamp()
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*a,**k): return None
op=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()),NoRedirect()); op.addheaders=[]
R=[]; rawtotal=0; last_end=None; boundaries={}; results=[]; stop=None
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
sha=lambda b:hashlib.sha256(b).hexdigest()
def write(name,obj):
 with (O/name).open('x') as f: json.dump(obj,f,ensure_ascii=False,indent=2)
def get(url,label):
 global rawtotal,last_end
 if len(R)>=24: raise RuntimeError('NETWORK_ACTION_CAP')
 if time.time()>=deadline: raise RuntimeError('DEADLINE')
 if last_end is not None: time.sleep(max(0,1-(time.monotonic()-last_end)))
 if time.time()+15>deadline: raise RuntimeError('DEADLINE_BEFORE_REQUEST')
 rec={'slot':len(R)+1,'URL':url,'UTC_start':now(),'file':label+'.body.bin'}; R.append(rec)
 body=b''; err=None; begin=time.monotonic()
 with (O/rec['file']).open('xb') as f:
  try:
   try: resp=op.open(urllib.request.Request(url,method='GET'),timeout=15)
   except urllib.error.HTTPError as e: resp=e
   with resp:
    rec['HTTP_status']=resp.code; rec['safe_headers']={k:resp.headers.get(k) for k in ['Date','Content-Type']}
    chunks=[]; size=0
    while True:
     remain=15-(time.monotonic()-begin)
     if remain<=0: raise TimeoutError('TOTAL_REQUEST_15S')
     try: resp.fp.raw._sock.settimeout(remain)
     except AttributeError: pass
     chunk=resp.read(min(65536,1048577-size))
     if not chunk: break
     chunks.append(chunk);f.write(chunk);size+=len(chunk)
     if size>1048576: raise RuntimeError('BODY_CAP')
    body=b''.join(chunks)
  except Exception as e: err=type(e).__name__+': '+str(e)
 rec['UTC_end']=now();last_end=time.monotonic(); data=(O/rec['file']).read_bytes(); rec['bytes']=len(data);rec['sha256']=sha(data);rawtotal+=len(data);rec['transport_error']=err
 if err: raise RuntimeError(err)
 if rawtotal>16777216: raise RuntimeError('TOTAL_RAW_CAP')
 if rec.get('HTTP_status')!=200: raise RuntimeError('HTTP_NON200_STOP_ALL_NETWORK_'+str(rec.get('HTTP_status')))
 try: j=json.loads(data)
 except Exception as e: raise RuntimeError('JSON_PARSE:'+str(e))
 if not isinstance(j,dict): raise RuntimeError('JSON_NOT_OBJECT')
 return j

def iso(s):
 if not isinstance(s,str): raise ValueError('Block.time missing')
 m=re.fullmatch(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{1,9}))?(Z|[+-]\d{2}:\d{2})',s)
 if not m: raise ValueError('ISO invalid')
 dt=datetime.datetime.strptime(m[1]+ ('+0000' if m[3]=='Z' else m[3].replace(':','')),'%Y-%m-%dT%H:%M:%S%z')
 return decimal.Decimal(int(dt.timestamp()))+decimal.Decimal('0.'+(m[2] or '0'))

def block(n,label):
 j=get('https://api.blockcypher.com/v1/eth/main/blocks/'+str(n),label)
 if j.get('error') or j.get('errors') or j.get('chain')!='ETH.main' or type(j.get('height'))!=int or j['height']!=n or not re.fullmatch('[0-9a-fA-F]{64}',str(j.get('hash',''))): raise RuntimeError('BLOCK_IDENTITY')
 t=iso(j.get('time'));return {'height':n,'hash':j['hash'],'time_raw':j['time'],'timestamp_metadata':str(t)}
def num(x):
 if isinstance(x,int) and not isinstance(x,bool): return x
 if not isinstance(x,str) or not re.fullmatch(r'(?:0x[0-9a-fA-F]+|[0-9]+)',x):raise ValueError('numeric identity missing/invalid')
 return int(x,16 if x.startswith('0x') else 10)
def hash32(x):return isinstance(x,str) and re.fullmatch(r'0x[0-9a-fA-F]{64}',x)
with (O/'started.lock').open('x') as f:f.write(now())
try:
 bpath=pathlib.Path(p['reused_start_boundary']['path']);b=bpath.read_bytes()
 if sha(b)!=p['reused_start_boundary']['sha256'] or json.loads(b).get('result')!='26093738':raise RuntimeError('REUSED_BOUNDARY_IDENTITY')
 base='https://api.routescan.io/v2/network/mainnet/evm/1/etherscan/api?'
 j=get(base+'module=block&action=getblocknobytime&timestamp=1792368000&closest=after','01-end-boundary')
 if j.get('status')!='1' or j.get('message')!='OK' or not re.fullmatch('[0-9]+',str(j.get('result',''))):raise RuntimeError('END_BOUNDARY_SCHEMA')
 E=int(j['result']);boundaries['E']=E
 for n,label in [(26093737,'02-start-before'),(26093738,'03-start-after'),(E-1,'04-end-before'),(E,'05-end-after')]:boundaries[label]=block(n,label)
 for a,b,t in [('02-start-before','03-start-after',1790812800),('04-end-before','05-end-after',1792368000)]:
  ta=decimal.Decimal(boundaries[a]['timestamp_metadata']);tb=decimal.Decimal(boundaries[b]['timestamp_metadata'])
  if not ta<decimal.Decimal(t)<=tb:raise RuntimeError('BOUNDARY_NOT_BRACKETED')
 boundaries['status']='PASS_STRICT_PAIRS_AND_BRACKETS'
 for index,ad in enumerate(p['fixed_addresses']):
  ar=dict(ad,status='INCOMPLETE_UNKNOWN',pages=[],unique_events_in_interval=None,unique_transactions_in_interval=None);results.append(ar);keys=set();txs=set();seen=set();allkeys=set(); page=1
  try:
   while True:
    j=get(base+'module=logs&action=getLogs&fromBlock=26093737&toBlock='+str(E)+'&address='+ad['address']+'&topic0='+p['topic0']+'&page='+str(page)+'&offset=200','%02d-logs-%d-page%d'%(len(R)+1,index+1,page))
    if j.get('status')!='1' or j.get('message')!='OK' or not isinstance(j.get('result'),list):raise ValueError('PROVIDER_NOT_SUCCESS_LIST')
    rows=j['result'];pr={'page':page,'rows':len(rows),'request_slot':len(R)};ar['pages'].append(pr)
    if not rows:
     ar.update(status='COMPLETE_PROVIDER_SCOPE',unique_events_in_interval=len(keys),unique_transactions_in_interval=len(txs),validated_outer_unique_events=len(allkeys));break
    ph=sha(json.dumps(rows,sort_keys=True,separators=(',',':')).encode())
    if ph in seen:raise ValueError('DUPLICATE_PAGE')
    seen.add(ph)
    for row in rows:
     if not isinstance(row,dict) or row.get('address','').lower()!=ad['address'] or not isinstance(row.get('topics'),list) or not row['topics'] or row['topics'][0].lower()!=p['topic0']:raise ValueError('LOG_ADDRESS_TOPIC_IDENTITY')
     if not hash32(row.get('blockHash')) or not hash32(row.get('transactionHash')):raise ValueError('LOG_BLOCK_OR_TX_HASH_MISSING_INVALID')
     if not isinstance(row.get('data'),str) or not re.fullmatch('0x(?:[0-9a-fA-F]{2})*',row['data']):raise ValueError('LOG_DATA_MISSING_INVALID')
     bn=num(row.get('blockNumber'));li=num(row.get('logIndex'));ts=num(row.get('timeStamp'))
     if not 26093737<=bn<=E or li<0:raise ValueError('LOG_BLOCK_INDEX_RANGE')
     key=(row['blockHash'].lower(),row['transactionHash'].lower(),li)
     if key in allkeys:raise ValueError('DUPLICATE_EVENT_PAGING')
     allkeys.add(key)
     if 1790812800<=ts<1792368000:keys.add(key);txs.add(row['transactionHash'].lower())
    page+=1
  except ValueError as e:ar.update(reason=str(e),validated_partial_unique_events_in_interval=len(keys),validated_partial_unique_transactions_in_interval=len(txs))
except Exception as e:stop=type(e).__name__+': '+str(e)
# Any source refusal/global budget/transport/boundary failure stops network. No retries.
for ad in p['fixed_addresses'][len(results):]:results.append(dict(ad,status='NOT_EXECUTED_UNKNOWN',reason=stop or 'NOT_REACHED'))
status='COMPLETE_FIXED_SIX_PROVIDER_SCOPE' if not stop and all(a['status']=='COMPLETE_PROVIDER_SCOPE' for a in results) else 'PARTIAL_OR_STOPPED_UNKNOWN'
res={'status':status,'stop_reason':stop,'fixed_interval_UTC':[p['start_inclusive_utc'],p['end_exclusive_utc']],'boundaries':boundaries,'per_address':results,'counts_are_events_not_troves_or_profit':True,'gross_cash':'NOT_VERIFIED','money_fields_decoded_or_summed':False,'requests':len(R),'UTC_finished':now()}
write('result.json',res)
receipt={'status':status,'requests':R,'request_count':len(R),'raw_body_total_bytes':rawtotal,'result_sha256':sha((O/'result.json').read_bytes()),'protocol_sha256':sha((D/'root/protocol.json').read_bytes()),'no_retry_redirect_credentials_custom_headers':True,'actual_model_effort_CPU_RSS':'UNKNOWN','UTC_finished':now()}
write('receipt.json',receipt)
print(json.dumps({'status':status,'stop':stop,'requests':len(R),'per_address':results,'result_sha256':sha((O/'result.json').read_bytes()),'receipt_sha256':sha((O/'receipt.json').read_bytes())},ensure_ascii=False))

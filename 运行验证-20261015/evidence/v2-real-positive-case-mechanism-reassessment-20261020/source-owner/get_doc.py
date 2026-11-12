"""Own bounded official-document downloader, no source/JS execution."""
from pathlib import Path
from urllib.parse import urlparse
import json,sys,subprocess,hashlib,datetime
P=Path(__file__).resolve().parent;P.mkdir(parents=True,exist_ok=True)
n,url=sys.argv[1:];assert urlparse(url).hostname in ['docs.uniswap.org','developers.uniswap.org','uniswap.org','www.uniswap.org']
assert len(list(P.glob('*.request.json')))<3
used=sum(f.stat().st_size for f in P.glob('*.source'));cap=min(524288,1048576-used);assert cap>0
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,10,19,20,14,11,tzinfo=datetime.timezone.utc)
f=P/(n+'.source');assert not f.exists();U=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();H=lambda b:hashlib.sha256(b).hexdigest()
(P/(n+'.request.json')).write_text(json.dumps({'fixed_utc':U(),'url':url,'method':'GET','body_cap':cap,'whole_raw_cap':1048576,'timeout_seconds':25,'strict_default_TLS':True,'anonymous_no_identity_auth_proxy_change':True,'no_source_JS_or_financial_execution':True},indent=2)+'\n')
start=U();r=subprocess.run(['/usr/bin/curl','-q','--silent','--show-error','--max-time','25','--connect-timeout','10','--max-filesize',str(cap),'--dump-header','-','--output',str(f),'--write-out','\nOWN_META:%{json}',url],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30);end=U();head,sep,meta=r.stdout.partition(b'\nOWN_META:');m=json.loads(meta)if sep else {};safe={}
for line in head.decode('iso-8859-1').splitlines():
 if ':'in line:
  k,v=line.split(':',1)
  if k.lower()in ['date','content-type','content-length','content-encoding','etag','last-modified','cache-control','server','retry-after','location']:safe[k.lower()]=v.strip()
b=f.read_bytes()if f.exists()else b''
if not f.exists():f.write_bytes(b'')
a={'URL':url,'started_utc':start,'finished_utc':end,'HTTP':m.get('http_code'),'curl_exit':r.returncode,'TLS_verify_result':m.get('ssl_verify_result'),'redirects_followed':m.get('num_redirects'),'body_bytes':len(b),'sha256':H(b),'safe_headers':safe,'stderr':r.stderr.decode(errors='replace'),'complete_HTTP200':r.returncode==0 and m.get('http_code')==200,'refusal_or_auth_rate_limit':m.get('http_code')in[401,402,403,407,429]}
(P/(n+'.acquisition.json')).write_text(json.dumps(a,indent=2)+'\n');print(json.dumps(a))

"""Own bounded passive getter. No source code or script execution."""
from pathlib import Path
import sys,json,subprocess,datetime,hashlib
from urllib.parse import urlparse
P=Path(__file__).resolve().parent
n,url=sys.argv[1:]
assert urlparse(url).scheme=='https'
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,10,19,20,23,tzinfo=datetime.timezone.utc)
assert not (P/(n+'.request.json')).exists()
used=sum(f.stat().st_size for f in P.glob('*.source'))+sum(f.stat().st_size for f in P.glob('*search.source.json'))
cap=min(5242880,12582912-used);assert cap>0
U=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
request={'UTC':U(),'method':'GET','url':url,'timeout_seconds':25,'body_cap':cap,'no_redirect_follow':True,'default_strict_TLS':True,'no_identity_auth_proxy_change':True}
(P/(n+'.request.json')).write_text(json.dumps(request,indent=2)+'\n')
f=P/(n+'.source');start=U()
r=subprocess.run(['/usr/bin/curl','-q','--silent','--show-error','--max-time','25','--connect-timeout','10','--max-filesize',str(cap),'--dump-header','-','--output',str(f),'--write-out','\nOWN_META:%{json}',url],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
end=U();head,sep,meta=r.stdout.partition(b'\nOWN_META:');m=json.loads(meta)if sep else {};safe={}
for line in head.decode('iso-8859-1').splitlines():
 if ':'in line:
  k,v=line.split(':',1)
  if k.lower()in ['date','content-type','content-length','content-encoding','etag','last-modified','cache-control','server','retry-after','location']:safe[k.lower()]=v.strip()
b=f.read_bytes()if f.exists()else b''
if not f.exists():f.write_bytes(b'')
a={'url':url,'started_utc':start,'finished_utc':end,'HTTP':m.get('http_code'),'curl_exit':r.returncode,'TLS_verify_result':m.get('ssl_verify_result'),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'safe_headers':safe,'stderr':r.stderr.decode(errors='replace'),'complete_HTTP200':r.returncode==0 and m.get('http_code')==200,'refusal_auth_rate_limit':m.get('http_code')in [401,402,403,407,429]}
(P/(n+'.acquisition.json')).write_text(json.dumps(a,indent=2)+'\n');print(json.dumps(a))

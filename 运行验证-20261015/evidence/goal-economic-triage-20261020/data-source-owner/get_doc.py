"""Own bounded passive document getter, disallow RPC hosts and API requests."""
from pathlib import Path
from urllib.parse import urlparse
import json,sys,datetime,subprocess,hashlib
P=Path(__file__).resolve().parent;n,url=sys.argv[1:];u=urlparse(url)
assert u.scheme=='https'and u.hostname in ['ethereum.publicnode.com','www.publicnode.com','publicnode.com','geth.ethereum.org','eips.ethereum.org']
assert '-rpc.'not in u.hostname and not u.query
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,10,19,20,35,30,tzinfo=datetime.timezone.utc)
assert not (P/(n+'.request.json')).exists()
used=sum(f.stat().st_size for f in P.glob('*.source'));cap=min(1048576,3145728-used);assert cap>0
U=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();f=P/(n+'.source')
(P/(n+'.request.json')).write_text(json.dumps({'UTC':U(),'method':'GET','url':url,'document_only':True,'no_rpc_API_or_subscription':True,'max_body_bytes':cap,'timeout_seconds':25,'strict_default_TLS':True,'redirects_not_followed':True,'no_identity_auth_proxy_change':True},indent=2)+'\n')
start=U();r=subprocess.run(['/usr/bin/curl','-q','--silent','--show-error','--max-time','25','--connect-timeout','10','--max-filesize',str(cap),'--dump-header','-','--output',str(f),'--write-out','\nOWN_META:%{json}',url],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30);end=U();head,sep,meta=r.stdout.partition(b'\nOWN_META:');m=json.loads(meta)if sep else {};safe={}
for line in head.decode('iso-8859-1').splitlines():
 if ':'in line:
  k,v=line.split(':',1)
  if k.lower()in ['date','content-type','content-length','content-encoding','etag','last-modified','cache-control','server','retry-after','location']:safe[k.lower()]=v.strip()
b=f.read_bytes()if f.exists()else b''
if not f.exists():f.write_bytes(b'')
a={'URL':url,'started_UTC':start,'finished_UTC':end,'HTTP':m.get('http_code'),'curl_exit':r.returncode,'TLS_verify_result':m.get('ssl_verify_result'),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'safe_headers':safe,'stderr':r.stderr.decode(errors='replace'),'complete_HTTP200':r.returncode==0 and m.get('http_code')==200,'refusal_auth_ratelimit':m.get('http_code')in [401,402,403,407,429]}
(P/(n+'.acquisition.json')).write_text(json.dumps(a,indent=2)+'\n');print(json.dumps(a))

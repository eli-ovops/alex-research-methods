"""Own bounded primary SEC public text getter. No source execution or accounting."""
from pathlib import Path
import json,datetime,hashlib,subprocess,sys
from urllib.parse import urlparse
P=Path(__file__).resolve().parent;P.mkdir(parents=True,exist_ok=True)
n,url=sys.argv[1:];target=P/(n+'.source');assert not target.exists()
assert urlparse(url).hostname in ['www.sec.gov','data.sec.gov']
assert len(list(P.glob('*.request.json')))<8
assert sum(f.stat().st_size for f in P.glob('*.source'))+1048576<=8388608
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,10,19,20,8,21,tzinfo=datetime.timezone.utc)
U=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();H=lambda b:hashlib.sha256(b).hexdigest()
(P/(n+'.request.json')).write_text(json.dumps({'fixed_utc':U(),'method':'GET','url':url,'single_cap':1048576,'timeout_seconds':25,'strict_default_TLS':True,'anonymous_default_identity_no_key_or_credentials_or_proxy_changes':True,'no_source_execution_or_arithmetic':True},indent=2)+'\n')
start=U();r=subprocess.run(['/usr/bin/curl','-q','--silent','--show-error','--max-time','25','--connect-timeout','10','--max-filesize','1048576','--dump-header','-','--output',str(target),'--write-out','\nOWN_META:%{json}',url],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30);end=U();head,sep,meta=r.stdout.partition(b'\nOWN_META:');m=json.loads(meta)if sep else {};safe={}
for line in head.decode('iso-8859-1').splitlines():
 if ':'in line:
  k,v=line.split(':',1)
  if k.lower()in ['date','content-type','content-length','content-encoding','etag','last-modified','cache-control','server','retry-after']:safe[k.lower()]=v.strip()
b=target.read_bytes()if target.exists()else b''
if not target.exists():target.write_bytes(b'')
a={'url':url,'started_utc':start,'finished_utc':end,'HTTP':m.get('http_code'),'curl_exit':r.returncode,'TLS_verify_result':m.get('ssl_verify_result'),'redirects':m.get('num_redirects'),'body_bytes':len(b),'sha256':H(b),'safe_headers':safe,'stderr':r.stderr.decode(errors='replace'),'complete_HTTP200':r.returncode==0 and m.get('http_code')==200,'refusal_or_auth_rate_limit':m.get('http_code')in[401,402,403,407,429]}
(P/(n+'.acquisition.json')).write_text(json.dumps(a,indent=2)+'\n');print(json.dumps(a))

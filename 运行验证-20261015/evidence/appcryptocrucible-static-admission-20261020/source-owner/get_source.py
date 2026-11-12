"""Own bounded anonymous GitHub REST getter; never executes downloaded text."""
from pathlib import Path
import subprocess,json,sys,hashlib,datetime
P=Path(__file__).resolve().parent;P.mkdir(parents=True,exist_ok=True)
n,url=sys.argv[1:];f=P/(n+'.response.json');assert not f.exists(),'No duplicate GET or overwrite'
assert url.startswith('https://api.github.com/repos/appCryptoCrucible/liquidation')
assert len(list(P.glob('*.request.json')))<10
assert sum(x.stat().st_size for x in P.glob('*.response.json'))<6291456
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,10,19,19,30,15,tzinfo=datetime.timezone.utc)
U=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();H=lambda b:hashlib.sha256(b).hexdigest()
(P/(n+'.request.json')).write_text(json.dumps({'method':'GET','URL':url,'fixed_utc':U(),'anonymous':True,'strict_default_TLS':True,'body_cap':2097152,'timeout_seconds':25,'no_source_execution':True},indent=2)+'\n')
start=U();r=subprocess.run(['/usr/bin/curl','-q','--silent','--show-error','--max-time','25','--connect-timeout','10','--max-filesize','2097152','--dump-header','-','--output',str(f),'--write-out','\nOWN_META:%{json}',url],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30);end=U()
headers,sep,m=r.stdout.partition(b'\nOWN_META:');j=json.loads(m)if sep else {};safe={}
for line in headers.decode('iso-8859-1').splitlines():
 if ':'in line:
  k,v=line.split(':',1)
  if k.lower()in {'date','content-type','content-length','etag','last-modified','x-ratelimit-limit','x-ratelimit-remaining','x-ratelimit-reset','retry-after'}:safe[k.lower()]=v.strip()
b=f.read_bytes()if f.exists()else b''
if not f.exists():f.write_bytes(b'')
rec={'URL':url,'started_utc':start,'finished_utc':end,'http_status':j.get('http_code'),'curl_exit':r.returncode,'SSL_verify_result':j.get('ssl_verify_result'),'redirects':j.get('num_redirects'),'bytes':len(b),'sha256':H(b),'safe_headers':safe,'stderr':r.stderr.decode(errors='replace'),'complete':r.returncode==0 and j.get('http_code')==200,'refusal_or_auth_or_limit':j.get('http_code')in [401,402,403,407,429]}
(P/(n+'.receipt.json')).write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec))

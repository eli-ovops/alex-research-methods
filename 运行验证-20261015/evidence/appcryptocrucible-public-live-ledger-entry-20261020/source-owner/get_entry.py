"""Own public source/entry getter. No chain or financial queries, no source execution."""
from pathlib import Path
import json,sys,hashlib,datetime,subprocess
P=Path(__file__).resolve().parent;P.mkdir(parents=True,exist_ok=True)
n,url=sys.argv[1:];f=P/(n+'.response.json');assert not f.exists()
assert url.startswith('https://api.github.com/repos/appCryptoCrucible/liquidation/')
assert len(list(P.glob('*.request.json')))<5
assert sum(q.stat().st_size for q in P.glob('*.response.json'))+524288<=2097152
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,10,19,19,50,18,tzinfo=datetime.timezone.utc)
U=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();H=lambda b:hashlib.sha256(b).hexdigest()
(P/(n+'.request.json')).write_text(json.dumps({'fixed_utc':U(),'URL':url,'method':'GET','single_body_cap':524288,'whole_body_cap':2097152,'timeout_seconds':25,'strict_default_TLS':True,'anonymous_no_credentials_or_identity_proxy_change':True,'purpose':'Find already published real execution address/complete period ledger entry only; no chain lookup or arithmetic'},indent=2)+'\n')
start=U();r=subprocess.run(['/usr/bin/curl','-q','--silent','--show-error','--max-time','25','--connect-timeout','10','--max-filesize','524288','--dump-header','-','--output',str(f),'--write-out','\nOWN_META:%{json}',url],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30);end=U();head,sep,meta=r.stdout.partition(b'\nOWN_META:');info=json.loads(meta)if sep else {};safe={}
for line in head.decode('iso-8859-1').splitlines():
 if ':'in line:
  k,v=line.split(':',1)
  if k.lower()in {'date','content-type','content-length','etag','last-modified','link','x-ratelimit-limit','x-ratelimit-remaining','x-ratelimit-reset','retry-after'}:safe[k.lower()]=v.strip()
b=f.read_bytes()if f.exists()else b''
if not f.exists():f.write_bytes(b'')
j={'URL':url,'started_utc':start,'finished_utc':end,'HTTP':info.get('http_code'),'curl_exit':r.returncode,'TLS_verify_result':info.get('ssl_verify_result'),'bytes':len(b),'sha256':H(b),'safe_headers':safe,'stderr':r.stderr.decode(errors='replace'),'complete_HTTP200':r.returncode==0 and info.get('http_code')==200,'refusal_or_auth_or_rate_limit':info.get('http_code')in[401,402,403,407,429]}
(P/(n+'.acquisition.json')).write_text(json.dumps(j,indent=2)+'\n');print(json.dumps(j))

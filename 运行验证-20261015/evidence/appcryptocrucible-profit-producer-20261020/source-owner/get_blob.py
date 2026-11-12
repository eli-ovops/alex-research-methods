"""Own bounded GitHub REST blob reader; fetched bytes are never executed."""
from pathlib import Path
import sys,json,hashlib,datetime,subprocess,base64
P=Path(__file__).resolve().parent;P.mkdir(parents=True,exist_ok=True)
OLD=P.parent.parent/'appcryptocrucible-static-admission-20261020/source-owner'
n,repo_path=sys.argv[1:]
t=json.loads((OLD/'03-tree.response.json').read_bytes());assert t['sha']=='0958f715725a563f8ebcbf44c81cc133a2e59f22'and not t['truncated']
matches=[x for x in t['tree']if x['path']==repo_path and x['type']=='blob'];assert len(matches)==1
item=matches[0];assert item['size']<190000
assert len(list(P.glob('*.request.json')))<4
assert sum(f.stat().st_size for f in P.glob('*.response.json'))+262144<=1048576
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,10,19,19,43,12,tzinfo=datetime.timezone.utc)
U=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();H=lambda b:hashlib.sha256(b).hexdigest()
url='https://api.github.com/repos/appCryptoCrucible/liquidation/git/blobs/'+item['sha'];target=P/(n+'.response.json');assert not target.exists()
request={'fixed_utc':U(),'url':url,'method':'GET','repo_path':repo_path,'fixed_commit':'364059aba56e773da01f6507224cf530bbbb1b09','fixed_tree':t['sha'],'expected_blob':item['sha'],'expected_decoded_bytes':item['size'],'single_response_cap':262144,'all_response_cap':1048576,'anonymous_default_TLS_no_source_execution':True}
(P/(n+'.request.json')).write_text(json.dumps(request,indent=2)+'\n')
start=U();r=subprocess.run(['/usr/bin/curl','-q','--silent','--show-error','--max-time','25','--connect-timeout','10','--max-filesize','262144','--dump-header','-','--output',str(target),'--write-out','\nOWN_META:%{json}',url],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30);end=U();headers,sep,meta=r.stdout.partition(b'\nOWN_META:');m=json.loads(meta)if sep else {};safe={}
for line in headers.decode('iso-8859-1').splitlines():
 if ':'in line:
  k,v=line.split(':',1)
  if k.lower()in {'date','content-type','content-length','etag','last-modified','x-ratelimit-limit','x-ratelimit-remaining','x-ratelimit-reset','retry-after'}:safe[k.lower()]=v.strip()
b=target.read_bytes()if target.exists()else b''
if not target.exists():target.write_bytes(b'')
rec={'url':url,'repo_path':repo_path,'started_utc':start,'finished_utc':end,'http_status':m.get('http_code'),'curl_exit':r.returncode,'SSL_verify_result':m.get('ssl_verify_result'),'bytes':len(b),'response_sha256':H(b),'safe_headers':safe,'stderr':r.stderr.decode(errors='replace'),'complete_HTTP200':r.returncode==0 and m.get('http_code')==200,'refusal_or_auth_or_limit':m.get('http_code')in[401,402,403,407,429]}
if rec['complete_HTTP200']:
 j=json.loads(b);assert j['encoding']=='base64';text=base64.b64decode(j['content']);blob=hashlib.sha1(b'blob '+str(len(text)).encode()+b'\0'+text).hexdigest();assert blob==j['sha']==item['sha']and len(text)==item['size'];out=P/(n+'.source'+Path(repo_path).suffix);out.write_bytes(text);rec.update(blob_sha=blob,decoded_bytes=len(text),decoded_SHA256=H(text),tree_bound=True,local_Git_blob_SHA1_match=True,decoded_path=str(out.resolve()))
(P/(n+'.acquisition.json')).write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec))

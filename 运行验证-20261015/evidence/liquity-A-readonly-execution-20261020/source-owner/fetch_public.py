#!/usr/bin/env python3
"""Finite public-document GET only; never calls chain endpoints."""
import argparse, datetime, hashlib, json, pathlib, subprocess, sys
p=argparse.ArgumentParser()
p.add_argument('name'); p.add_argument('url'); p.add_argument('out')
a=p.parse_args(); out=pathlib.Path(a.out); out.mkdir(parents=True,exist_ok=True)
body=out/(a.name+'.body'); receipt=out/(a.name+'.receipt.json')
if body.exists() or receipt.exists(): raise SystemExit('STOP existing output')
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
request={'url':a.url,'method':'GET','started_at_utc':start,'max_bytes':2097152,'timeout_seconds':25,'redirects_allowed':False,'auth':False,'retries':0}
(out/(a.name+'.request.json')).write_text(json.dumps(request,indent=2)+'\n')
r=subprocess.run(['curl','-q','-sS','--max-time','25','--max-filesize','2097152','--dump-header','-','--output',str(body),'--write-out','\nREAD_META %{http_code} %{url_effective} %{size_download}\n',a.url],capture_output=True)
headers=r.stdout.decode('iso-8859-1','replace').splitlines(); safe={}; code=None; effective=None
for line in headers:
    if line.startswith('READ_META '):
        parts=line.split(); code=int(parts[1]); effective=parts[2]
    elif ':' in line:
        k,v=line.split(':',1)
        if k.lower() in {'content-type','content-length','content-encoding','date','etag','last-modified','cache-control','retry-after','location'}: safe[k]=v.strip()
data=body.read_bytes() if body.exists() else b''
rec={**request,'finished_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'HTTP':code,'effective_url':effective,'safe_headers':safe,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'curl_exit':r.returncode,'error':r.stderr.decode('utf-8','replace') or None,'complete':r.returncode==0 and len(data)<=2097152,'RPC_or_EVM':False}
receipt.write_text(json.dumps(rec,indent=2)+'\n')
print(json.dumps({k:rec[k] for k in ['HTTP','bytes','sha256','curl_exit','complete']}))
if r.returncode or code!=200 or len(data)>2097152: sys.exit(2)

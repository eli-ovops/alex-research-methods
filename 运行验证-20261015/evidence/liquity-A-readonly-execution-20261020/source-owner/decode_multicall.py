import base64,hashlib,json,pathlib,sys
p=pathlib.Path(sys.argv[1]); items=[]
for source,dest in [('06-multicall-deployment-list','multicall-deployments.json'),('07-multicall-source','Multicall3.official.sol')]:
 d=json.loads((p/(source+'.body')).read_text()); raw=base64.b64decode(d['content'])
 blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+bytes([0])+raw).hexdigest()
 assert blob==d['sha'],(blob,d['sha'])
 (p/dest).write_bytes(raw)
 items.append({'path':dest,'source_path':d['path'],'git_blob':blob,'download_url':d['download_url'],'sha256':hashlib.sha256(raw).hexdigest()})
(p/'multicall-official-source-identity.json').write_text(json.dumps(items,indent=2)+'\n')
print(json.dumps(items))

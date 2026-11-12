import base64, hashlib, json, pathlib, sys
p=pathlib.Path(sys.argv[1])
selection={
'01-registry':{'AddressesRegistry.sol':'registry.verified.sol'},
'02-stability-pool':{'src/StabilityPool.sol':'stability-pool.verified.sol'},
'03-weth-price-feed':{
 'src/PriceFeeds/WETHPriceFeed.sol':'weth-price-feed.verified.sol',
 'src/PriceFeeds/MainnetPriceFeedBase.sol':'mainnet-price-feed-base.verified.sol',
 'src/Interfaces/IMainnetPriceFeed.sol':'mainnet-price-feed.interface.sol',
 'src/Dependencies/AggregatorV3Interface.sol':'aggregator-v3.interface.sol'}
}
summaries=[]
for name, files in selection.items():
 d=json.loads((p/(name+'.body')).read_text())
 rec={k:d.get(k) for k in ['chainId','address','match','creationMatch','runtimeMatch','verifiedAt','compilation','deployment','additionalInput']}
 rec['source_body_sha256']=hashlib.sha256((p/(name+'.body')).read_bytes()).hexdigest()
 rec['extracted']=[]
 for key, dest in files.items():
  raw=d['sources'][key]['content'].encode('utf-8')
  (p/dest).write_bytes(raw)
  rec['extracted'].append({'source_key':key,'path':dest,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
 summaries.append(rec)
(p/'dependencies.identity.json').write_text(json.dumps(summaries,indent=2)+'\n')
d=json.loads((p/'05-multicall-readme.body').read_text())
raw=base64.b64decode(d['content']); blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
assert blob==d['sha']
(p/'multicall-readme.md').write_bytes(raw)
(p/'multicall-readme.identity.json').write_text(json.dumps({'path':d['path'],'git_blob':d['sha'],'git_blob_calculated':blob,'download_url':d['download_url'],'html_url':d['html_url'],'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()},indent=2)+'\n')
print(json.dumps({'dependencies':len(summaries),'multicall_readme_blob':blob}))

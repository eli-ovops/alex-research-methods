import datetime,hashlib,json,pathlib,sys
p=pathlib.Path(sys.argv[1]); receipts=[]
for f in sorted(p.glob('[0-9][0-9]-*.receipt.json')):
 d=json.loads(f.read_text()); receipts.append({'path':f.name,**d})
assert len(receipts)==11
assert all(r['HTTP']==200 and r['complete'] for r in receipts)
rec={'finalized_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'COMPLETE_PUBLIC_SOURCE_BINDING_ONLY','public_GETs':len(receipts),'initial_cap':8,'revised_cap':12,'cap_amendment':'Root explicit in-turn instruction after necessary runtime fields were found absent; three additional exact dependency runtimeBytecode-only requests. Multicall already obtained, no twelfth request.','raw_body_bytes':sum(r['bytes'] for r in receipts),'per_body_cap':2097152,'all_complete':True,'network_stopped':True,'requests':receipts,'proxyResolution_requested_or_used':False,'live_chain_requests':0,'third_party_source_or_ABI_or_EVM_execution':0,'own_public_fetch_and_static_parsers_executed':True,'model_or_backtest_or_trade':0,'accounts_credentials_payments_installs':0,'actual_model_effort_CPU_RSS':'UNKNOWN','local_recovery':'One Git blob assertion stopped because own inline parser used literal backslash-zero, corrected using bytes([0]); reparsed saved raw sources without network retry.','report_sha256':hashlib.sha256((p/'report.md').read_bytes()).hexdigest()}
(p/'receipt.json').write_text(json.dumps(rec,indent=2)+'\n')
coverage={'semantic_reads':{'registry.verified.sol':'relevant declarations/constructor/setAddresses approximately4303-4432','stability-pool.verified.sol':'188-211','weth-price-feed.verified.sol':'full46lines','mainnet-price-feed-base.verified.sol':'full125lines','mainnet-price-feed.interface.sol':'full16lines','aggregator-v3.interface.sol':'full12lines','Multicall3.official.sol':'1-40,90-123','multicall-readme.md':'deployment/ABI/aggregate3 relevant excerpts'},'json_scope':'identity/selected ABI/source content extraction/runtime onchainBytecode and keys; not full compilation/metadata semantic audit','current_state_verified':False,'three_dependency_actual_constructor_arguments_obtained':False,'TM_prior_record_constructor_registry_binding':'explicit constructorArguments word matches registry20f7','aggregator_specific_deployment_identity':'UNKNOWN until sameB oracle getter supplies exact address; included source is interface only','licensing':'file-level SPDX only; no broad production/data-service authorization conclusion'}
(p/'coverage.json').write_text(json.dumps(coverage,indent=2)+'\n')
manifest=[]
for f in sorted(p.iterdir()):
 if f.is_file() and f.name!='manifest.json':
  data=f.read_bytes();manifest.append({'path':f.name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
(p/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'GETs':len(receipts),'raw_body_bytes':rec['raw_body_bytes'],'files':len(manifest),'report_sha256':rec['report_sha256']}))

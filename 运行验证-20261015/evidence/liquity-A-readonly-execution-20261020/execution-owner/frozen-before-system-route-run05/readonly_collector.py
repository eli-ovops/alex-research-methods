#!/usr/bin/env python3
"""Prospective A only. Fixed-block observations; no signing, estimates, or sending."""
import argparse, datetime as dt, json, pathlib, sys, time, os, resource, signal, math
from readonly_core import *
HERE=pathlib.Path(__file__).resolve().parent
UNIT=HERE.parent
RUN_ID="remaining-preflight-20261020-04"
RUN_DIR=HERE/"runs"/RUN_ID
LATEST_FIELDS=['entireDebt','entireColl','redistBoldDebtGain','redistCollGain','accruedInterest','recordedDebt','annualInterestRate','weightedRecordedDebt','accruedBatchManagementFee','lastInterestRateAdjTime']
FIXED={'tm':'0x7bcb64b2c9206a5b699ed43363f6f98d4776cf5a','registry':'0x20f7c9ad66983f6523a0881d0f82406541417526','sp':'0x5721cbbd64fc7ae3ef44a0a3f9a790a9264cf9bf','feed':'0xcc5f8102eb670c89a4a3c567c[REDACTED_PHONE]c24f','multicall':'0xca11bde05977b3631167028862be2a173976ca11'}

class Bindings:
    def __init__(self,path):
        self.path=pathlib.Path(path);self.raw=self.path.read_bytes();self.config=json.loads(self.raw);self.records={};self.selectors={};self.addresses={};self.runtime={}
        for role,x in self.config['contracts'].items():
            p=pathlib.Path(x['record_path']);b=p.read_bytes()
            if digest(b)!=x['record_sha256']:raise Stop('BINDING_FILE_HASH')
            r=json.loads(b)
            if str(r.get('chainId'))!='1':raise Stop('BINDING_CHAIN')
            target=r['address'].lower()
            if role in FIXED and target!=FIXED[role]:raise Stop('BINDING_FIXED_ADDRESS')
            if not re.fullmatch('0x[0-9a-f]{40}',target):raise Stop('BINDING_ADDRESS')
            self.addresses[role]=target;self.records[role]=r
            runtime=r.get('runtimeBytecode',{}).get('onchainBytecode')
            if not runtime and x.get('runtime_record_path'):
                rb=pathlib.Path(x['runtime_record_path']).read_bytes()
                if digest(rb)!=x['runtime_record_sha256']:raise Stop('RUNTIME_RECORD_HASH')
                rr=json.loads(rb)
                if rr['address'].lower()!=target or str(rr['chainId'])!='1':raise Stop('RUNTIME_RECORD_IDENTITY')
                runtime=rr['runtimeBytecode']['onchainBytecode']
            if not runtime:raise Stop('RUNTIME_BYTES_NOT_BOUND_'+role.upper())
            if not rawhex(runtime):raise Stop('RUNTIME_EMPTY')
            self.runtime[role]=runtime.lower()
        if set(self.records)!=set(FIXED):raise Stop('BINDING_ROLE_SET')
        needed={'tm':['getTroveIdsCount','getTroveFromTroveIdsArray','getTroveStatus','getLatestTroveData','shutdownTime','stabilityPool'], 'registry':['MCR','priceFeed','stabilityPool'], 'sp':['getTotalBoldDeposits'], 'feed':['priceSource','lastGoodPrice','ethUsdOracle','fetchPrice'], 'multicall':['aggregate3']}
        for role,names in needed.items():
            for name in names:self.selectors[(role,name)]=abi_method(self.records[role],name,allow_nonview=(role=='multicall' or (role=='feed' and name=='fetchPrice')))[0]
        latest=abi_method(self.records['tm'],'getLatestTroveData')[1]['outputs']
        if len(latest)!=1 or [x['name'] for x in latest[0].get('components',[])]!=LATEST_FIELDS or any(x['type']!='uint256' for x in latest[0]['components']):raise Stop('LATEST_TUPLE_VERSION')
        if self.selectors[('multicall','aggregate3')]!='0x82ad56cb':raise Stop('AGGREGATOR_SELECTOR')
        # Engineering encoding is derived only from hash-bound ABI, never a guessed TM getter.
    def method(self,role,name,*args):return (self.addresses[role],call_data(self.selectors[(role,name)],*args))


def oracle_price(mode,last_good,oracle,round_result,decimals,block_time):
    aggregator_int,threshold,feed_decimals=oracle
    if feed_decimals!=8 or decimals!=feed_decimals:raise Stop('ORACLE_DECIMALS_VERSION')
    if mode==2:
        if last_good<=0:raise Stop('LAST_GOOD_PRICE_INVALID')
        return last_good,'LAST_GOOD_PROTOCOL_MODE'
    if mode!=0:raise Stop('WETH_PRICE_MODE_UNSUPPORTED')
    if not round_result[0]:raise Stop('ORACLE_RESPONSE_FAILED_EXECUTION_FALLBACK_UNKNOWN')
    round_id,answer,started,updated,answered=uints(round_result[1],5)
    if round_id>=2**80 or answered>=2**80:raise Stop('ORACLE_UINT80')
    if answer>=2**255:answer-=2**256
    if updated>block_time:raise Stop('ORACLE_FUTURE_TIMESTAMP_UNDERFLOW')
    if answer<=0 or block_time-updated>=threshold:raise Stop('ORACLE_PRIMARY_INVALID_NEW_SHUTDOWN_NOT_SIMULATED')
    return answer*10**(18-feed_decimals),'PRIMARY_FRESH_CHAINLINK'


def qualify(rows,count,mcr,sp_total,price,basefee,fee_policy,usd_anchor=None):
    available=sp_total-min(10**18,sp_total)
    for r in rows:
        debt=r['latest']['entireDebt'];coll=r['latest']['entireColl'];icr=(coll*price)//debt if debt else 2**256-1
        r['ICR']=str(icr);r['eligible']=count>1 and r['status'] in (1,4) and icr<mcr and debt>0 and available>=debt
        r['fee_qualified']=None;r['exclusion']=None if r['eligible'] else 'STATUS_ICR_LAST_TROVE_OR_FULL_SP_CONDITION'
        if not r['eligible']:continue
        # Full-SP-only route; constants are source-bound in the admission manifest.
        reward=37500000000000000+min(coll//200,2*10**18)
        r['minimum_reward_wei']=str(reward)
        if not fee_policy.get('method_review_accepted') or usd_anchor is None:continue
        gas=fee_policy['gas_limit'];tip=fee_policy['priority_fee_wei']
        if gas!=1000000 or tip!=100000000:raise Stop('FROZEN_FEE_POLICY_MISMATCH')
        maxfee=2*basefee+tip;ceiling=gas*maxfee
        cap=min(10**15,(5*10**36)//usd_anchor,reward//4)
        r.update(fee_qualified=ceiling<=cap,minimum_reward_minus_ceiling=reward-ceiling,assumed_gas_limit=gas,assumed_max_fee_per_gas_wei=str(maxfee),assumed_worst_cost_wei=str(ceiling),attempt_cap_wei=str(cap),scenario_only_not_actual_fee_or_fill=True)
    return rows

class Scanner:
    def __init__(self,binding,rpc,padding=32):self.b=binding;self.rpc=rpc;self.padding=padding;self.high_water=0;self.usd_anchor=None;self.artifacts=[]
    def aggregate(self,calls,tag):
        hash32(tag)  # Provider-documented bare block hash, not EIP1898 requireCanonical.
        data=aggregate3(self.b.selectors[('multicall','aggregate3')],calls)
        result=self.rpc.call('eth_call',[{'to':self.b.addresses['multicall'],'from':'0x'+'0'*40,'gas':hex(30000000),'input':data},tag])
        self.artifacts.append(self.rpc.last_artifact)
        return decode_aggregate3(result,len(calls))
    def snapshot(self,h,initial=False):
        self.artifacts=[];number=h['number'];quantity(number);tag=h['hash'];hash32(tag);ts=quantity(h['timestamp']);bh=tag;started={'UTC':utc(),'monotonic_ns':time.monotonic_ns()}
        if initial:
            ok,v=self.aggregate([self.b.method('tm','getTroveIdsCount')],tag)[0]
            if not ok:raise Stop('COUNT_CALL_FAILED')
            n=uints(v,1)[0]
            if n*1216+8192>self.rpc.max_body:raise Stop('N_CANNOT_FIT_FULL_RESPONSE_CAP')
            self.padding=((n+31)//32)*32+32
        base=[('tm','getTroveIdsCount'),('tm','shutdownTime'),('registry','MCR'),('registry','priceFeed'),('registry','stabilityPool'),('tm','stabilityPool'),('feed','priceSource'),('feed','lastGoodPrice'),('feed','ethUsdOracle')]
        calls=[self.b.method(*x) for x in base]+[self.b.method('tm','getTroveFromTroveIdsArray',i) for i in range(self.padding)]
        res=self.aggregate(calls,tag)
        if any(not z[0] for z in res[:len(base)]):raise Stop('BASE_GETTER_FAILED')
        n=uints(res[0][1],1)[0]
        if n>self.padding:
            raise Stop('N_EXCEEDS_ADMITTED_PADDING_REPREFLIGHT_REQUIRED')
        ids=[]
        for i,z in enumerate(res[len(base):]):
            if i<n:
                if not z[0]:raise Stop('ID_PAGE_INCOMPLETE')
                ids.append(uints(z[1],1)[0])
            elif z[0]:raise Stop('INDEX_PAST_COUNT_SUCCEEDED')
        if len(set(ids))!=n:raise Stop('DUPLICATE_OR_MISSING_IDS')
        if address(res[3][1])!=self.b.addresses['feed'] or address(res[4][1])!=self.b.addresses['sp'] or address(res[5][1])!=self.b.addresses['sp']:raise Stop('DEPENDENCY_ADDRESS_CHANGED')
        mcr=uints(res[2][1],1)[0];mode=uints(res[6][1],1)[0];lastgood=uints(res[7][1],1)[0];oracle=uints(res[8][1],3)
        if oracle[0]>=2**160 or oracle[0]==0 or oracle[2]!=8:raise Stop('ORACLE_ADDRESS_OR_PRECISION')
        second=[]
        for i in ids:second += [self.b.method('tm','getTroveStatus',i),self.b.method('tm','getLatestTroveData',i)]
        # fetchPrice is intentionally LAST: its nonpersistent EVM writes must not affect B-state getters.
        second += [self.b.method('sp','getTotalBoldDeposits'),self.b.method('feed','fetchPrice')]
        results=self.aggregate(second,tag)
        if any(not z[0] for z in results[:-1]):raise Stop('LATEST_STATUS_OR_SP_FAILED')
        if not results[-1][0]:raise Stop('FETCH_PRICE_REVERT_UNKNOWN_NO_CACHED_SUBSTITUTE')
        price,failure=uints(results[-1][1],2)
        if failure not in (0,1) or price<=0 or mode not in (0,2):raise Stop('FETCH_PRICE_RETURN_SCHEMA_OR_MODE')
        if mode==2 and (failure or price!=lastgood):raise Stop('FETCH_LASTGOOD_VERSION')
        sp=uints(results[-2][1],1)[0]
        path='PRIMARY_FEED_CALL' if mode==0 else 'LAST_GOOD_PROTOCOL_MODE'
        if failure:path='SIMULATED_NEW_ORACLE_FAILURE_POLICY_SKIP_NOT_PROTOCOL_INELIGIBLE'
        rows=[]
        for k,i in enumerate(ids):
            st=uints(results[2*k][1],1)[0]
            if st>4:raise Stop('STATUS_ENUM_VERSION')
            rows.append({'id':i,'status':st,'latest':dict(zip(LATEST_FIELDS,uints(results[2*k+1][1],10)))})
        # Every state read pins bare H; number fence checks B->H at completion, not finality.
        fence=self.rpc.call('eth_getBlockByNumber',[number,False])
        if fence.get('hash')!=bh or fence.get('number')!=number:raise Stop('MIXED_BLOCK_OR_REORG_DURING_SCAN')
        self.rpc.close()  # Successful snapshot ends its connection group before waiting for a NEW head.
        if not failure:rows=qualify(rows,n,mcr,sp,price,quantity(h['baseFeePerGas']),self.b.config['fee_policy'],self.usd_anchor)
        else:
            for r in rows:r.update(eligible=None,fee_qualified=None,policy_skip='SIMULATED_NEW_FAILURE_NOT_PROTOCOL_INELIGIBLE')
        return {'block':h,'blockHash':bh,'started':started,'formed':{'UTC':utc(),'monotonic_ns':time.monotonic_ns()},'count':n,'padding':self.padding,'ids_complete':True,'rows':rows,'MCR':str(mcr),'SP_total':str(sp),'protocol_price_18':str(price),'oracle_path':path,'oracle_raw':{'priceSource':mode,'lastGoodPrice':str(lastgood),'ethUsdOracle':list(map(str,oracle)),'fetchPrice_last_simulated_subcall':results[-1],'simulated_newOracleFailureDetected':bool(failure),'B_state_values_not_overwritten_by_simulation':True,'eth_call_context':{'from':'0x'+'0'*40,'gas':hex(30000000),'outer_target':self.b.addresses['multicall']}},'shutdownTime':str(uints(res[1][1],1)[0]),'state_read_block_hash':tag,'state_identifier_semantics':'Provider-documented bare hash string; requireCanonical NOT requested or claimed','same_block_fence_passed':True,'raw_response_artifacts':list(self.artifacts),'historical_own_fill_or_profit':False}


def forecast(c,budget,snapshot_bytes,scan_seconds,cpu_seconds=0,notification_bytes=None,wait_seconds=0,measured=None,already_disk=0,wait_disk=0,wait_cpu=0):
    # Early CU-only lower bound; final admission MUST supply complete measured head cycles.
    if not notification_bytes or any(type(n)!=int or n<=0 for n in notification_bytes):raise Stop('ACTUAL_NOTIFICATION_BYTES_REQUIRED')
    stream_cu=(max(notification_bytes)+24)//25;blocks=14*86400//12;wait_heads=math.ceil(wait_seconds/12);logs=(blocks+99)//100
    rpc_min=2*c['rpc_CU']['eth_call']+c['rpc_CU']['eth_getBlockByNumber']
    if measured is None:
        per_cu=rpc_min+stream_cu;per_methods=3;reserve_cu=logs*c['rpc_CU']['eth_getLogs'];reserve_methods=logs+2;reserve_disk=reserve_cpu=0
    else:
        if len(measured)<3 or any(m['methods']<3 or m['CU']<rpc_min for m in measured):raise Stop('FULL_MEASUREMENTS_REQUIRED')
        per_cu=max(m['CU'] for m in measured);per_methods=max(m['methods'] for m in measured)
        snapshot_bytes=max(m['disk'] for m in measured);cpu_seconds=max(m['cpu'] for m in measured);scan_seconds=max(m['processing_seconds'] for m in measured)
        r=c['audit_reserve'];reserve_cu=logs*c['rpc_CU']['eth_getLogs']+r['max_detail_transactions']*(c['rpc_CU']['eth_getTransactionByHash']+c['rpc_CU']['eth_getTransactionReceipt'])
        reserve_methods=logs+2*r['max_detail_transactions'];reserve_disk=r['disk_bytes'];reserve_cpu=r['cpu_seconds']
    total_cu=blocks*per_cu+wait_heads*stream_cu+reserve_cu;total_methods=blocks*per_methods+reserve_methods
    disk=already_disk+blocks*snapshot_bytes+wait_heads*wait_disk+reserve_disk;cpu=budget.state()['cpu']+blocks*cpu_seconds+wait_heads*wait_cpu+reserve_cpu
    details={'forecast_kind':'FULL_MEASURED_WITH_BOUNDED_AUDIT_ALLOWANCE' if measured is not None else 'CU_ONLY_LOWER_BOUND_NOT_ADMISSION','CU_forecast':total_cu,'methods_forecast':total_methods,'already_CU':budget.cu,'already_methods':budget.methods,'CU_cap':budget.cu_limit,'method_cap':budget.method_limit,'actual_notification_sample_bytes':notification_bytes,'stream_conservative_CU_per_head':stream_cu,'perblock_minimum_RPC_CU':rpc_min,'blocks':blocks,'wait_heads':wait_heads,'disk_including_already_and_wait_and_audit':disk,'CPU_including_prior_and_wait_and_audit':cpu,'full_measured_cycles':measured,'already_disk':already_disk}
    if total_cu+budget.cu>budget.cu_limit or total_methods+budget.methods>budget.method_limit:raise Stop('FORECAST_QUOTA_INSUFFICIENT',details)
    if disk>2*1024**3-1048576:raise Stop('FORECAST_DISK_INSUFFICIENT',details)
    if cpu>budget.cpu_limit:raise Stop('FORECAST_CPU_INSUFFICIENT',details)
    if scan_seconds>=c.get('timeliness',{}).get('max_processing_seconds',12):raise Stop('PREFLIGHT_SCAN_CANNOT_KEEP_UP',details)
    return dict(details,conservative_stream_CU_per_head=stream_cu,not_a_guarantee='Measured projection with explicit bounded audit allowance. Growth/faster heads/audit allowance exhaustion stops UNKNOWN; no downsampling.')


def timely(head,policy,processing_seconds=None,backlog=False,now=None):
    validate_header(head);now=time.time() if now is None else now;age=now-quantity(head['timestamp'])
    if age>policy['max_header_age_seconds'] or age < -policy['max_future_seconds']:raise Stop('STALE_OR_FUTURE_HEAD_UNKNOWN')
    if processing_seconds is not None and processing_seconds>=policy['max_processing_seconds']:raise Stop('PROCESSING_OVERRUN_UNKNOWN')
    if backlog:raise Stop('SOCKET_BACKLOG_UNKNOWN')
    return {'header_age_at_application_check_seconds':age,'application_read_not_wire_arrival':True}


def forward_head(stream,track,policy,evidence):
    started=time.monotonic()
    for attempt in range(policy['max_sample_attempts']):
        if time.monotonic()-started>policy['max_sample_wait_seconds']:raise Stop('PREFLIGHT_SAMPLE_TIME_CAP')
        head=stream.head();timely(head,policy);event=track.accept(head)
        if event in {'FIRST','EXTENDS'}:return head
        evidence.save('preflight-nonforward-head',{'header':head,'event':event,'counts_as_sample':False})
        if event=='REORG':raise Stop('PREFLIGHT_REORG_NOT_FORWARD_SAMPLE')
    raise Stop('PREFLIGHT_DISTINCT_HEAD_SAMPLE_INCOMPLETE')


def stage(status):
    # Nonsecret process proof; configuration is never labeled an active observer.
    row={'status':status,'PID':os.getpid(),'UTC':utc(),'monotonic_ns':time.monotonic_ns(),'credential_saved':False}
    row['process_CPU_seconds']=time.process_time()
    RUN_DIR.mkdir(parents=True,exist_ok=True)
    with (RUN_DIR/'runtime-stage.jsonl').open('a') as out:out.write(json.dumps(row)+'\n')


def compact_snapshot(snapshot):
    out=dict(snapshot);out['rows']=[{k:v for k,v in r.items() if k!='latest' and (k!='ICR' or r.get('eligible'))} for r in snapshot['rows']]
    out['latest_values_location']='Lossless full RPC response artifacts (fixed64-byte-delta-v1 when used), ABI-decoded in memory; no fields discarded from source archive.'
    return out


def audited_logs(rpc,b,lo,hi,known_headers):
    logs=rpc.call('eth_getLogs',[{'address':b.addresses['tm'],'fromBlock':hex(lo),'toBlock':hex(hi)}])
    if not isinstance(logs,list):raise Stop('LOGS_NOT_LIST')
    seen=set();resolved=[]
    for l in logs:
        n=quantity(l.get('blockNumber'));idx=quantity(l.get('logIndex'));tx=l.get('transactionHash')
        if not lo<=n<=hi or l.get('address','').lower()!=b.addresses['tm'] or l.get('removed') is True:raise Stop('LOGS_SCOPE_OR_REMOVED')
        if n not in known_headers or known_headers[n]['hash']!=l.get('blockHash'):raise Stop('AUDIT_LOG_HASH_NOT_CANONICAL_TRACK')
        key=(l.get('blockHash'),tx,idx)
        if key in seen:raise Stop('DUPLICATE_EVENT')
        seen.add(key)
        if not re.fullmatch('0x[0-9a-fA-F]{64}',str(tx)):raise Stop('LOG_TX_HASH')
        topics=l.get('topics')
        if not isinstance(topics,list) or not topics:raise Stop('LOG_TOPIC_SCHEMA')
        resolved.append(l)
    return resolved


def completed_event_audit(rpc,b,lo,hi,headers,max_transactions=1000):
    logs=audited_logs(rpc,b,lo,hi,headers);txs={}
    events=[e for e in b.records['tm']['abi'] if e.get('type')=='event' and e.get('name')=='Liquidation']
    if len(events)!=1:raise Stop('LIQUIDATION_EVENT_ABI')
    sig='Liquidation('+','.join(abi_type(x) for x in events[0]['inputs'])+')'
    topic='0x'+keccak256(sig.encode()).hex()
    for log in logs:
        if log['topics'][0].lower()!=topic:continue
        txhash=log['transactionHash']
        if txhash in txs:continue
        if len(txs)>=max_transactions:raise Stop('AUDIT_TRANSACTION_ALLOWANCE_EXHAUSTED_UNKNOWN')
        tx=rpc.call('eth_getTransactionByHash',[txhash]);receipt=rpc.call('eth_getTransactionReceipt',[txhash])
        n=quantity(log['blockNumber'])
        if tx.get('hash')!=txhash or receipt.get('transactionHash')!=txhash or tx.get('blockHash')!=log['blockHash'] or receipt.get('blockHash')!=log['blockHash'] or receipt.get('status')!='0x1':raise Stop('COMPLETION_TX_RECEIPT_IDENTITY')
        if tx.get('blockNumber')!=log['blockNumber'] or receipt.get('blockNumber')!=log['blockNumber']:raise Stop('COMPLETION_BLOCK_NUMBER')
        if not re.fullmatch('0x[0-9a-fA-F]{40}',str(tx.get('from',''))) or not re.fullmatch('0x[0-9a-fA-F]{40}',str(tx.get('to',''))):raise Stop('COMPLETION_PARTY_ADDRESS')
        txs[txhash]={'transaction':tx,'receipt':receipt,'completed_block_received_UTC':headers[n].get('_received_UTC'),'completion_known_only_after_B':'Already missed if no earlier causal candidate; rawepisode/snapshot timestamps retained for independent classification'}
    rpc.close()  # Successful audit group complete; no request replay.
    return {'from':lo,'to':hi,'logs':logs,'completed_transactions':txs,'not_signal':'Posthoc audit; not available to earlier candidate decisions','no_actual_own_capture_or_profit':True}


def independent_preflight_reference(evidence,header):
    # Two bounded anonymous public metadata GETs, once only; never a source/refusal fallback.
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()),NoRedirect());opener.addheaders=[]
    records=[];responses=[]
    for url in ['https://api.blockcypher.com/v1/eth/main','https://api.blockcypher.com/v1/eth/main/blocks/'+str(quantity(header['number']))]:
        if responses:time.sleep(1)
        start={'UTC':utc(),'monotonic_ns':time.monotonic_ns()};raw=b'';status=None;err=None;headers={}
        try:
            try:r=opener.open(urllib.request.Request(url,method='GET'),timeout=15)
            except urllib.error.HTTPError as e:r=e
            with r:
                status=r.code;headers={k:r.headers.get(k) for k in ['Date','Content-Type']};raw=r.read(262145)
        except Exception as ex:err='PUBLIC_TRANSPORT_'+type(ex).__name__
        record=evidence.save('independent-reference',{'URL':url,'start':start,'end':{'UTC':utc(),'monotonic_ns':time.monotonic_ns()},'HTTP':status,'headers':headers,'body_utf8':raw.decode('utf8','replace'),'safe_error':err})
        records.append(record)
        if err or status!=200 or len(raw)>262144:raise Stop('INDEPENDENT_REFERENCE_ACCESS_OR_SIZE')
        try:j=json.loads(raw)
        except Exception:raise Stop('INDEPENDENT_REFERENCE_JSON') from None
        if not isinstance(j,dict) or j.get('error') or j.get('errors'):raise Stop('INDEPENDENT_REFERENCE_SCHEMA')
        responses.append(j)
    root,block=responses
    if root.get('name')!='ETH.main' or type(root.get('height'))!=int or not re.fullmatch('[0-9a-fA-F]{64}',str(root.get('hash',''))):raise Stop('INDEPENDENT_ROOT_IDENTITY')
    if block.get('chain')!='ETH.main' or block.get('height')!=quantity(header['number']) or '0x'+str(block.get('hash','')).lower()!=header['hash'].lower():raise Stop('INDEPENDENT_SAME_B_IDENTITY')
    m=re.fullmatch(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{1,9}))?(Z|[+-]\d{2}:\d{2})',str(block.get('time','')))
    if not m:raise Stop('INDEPENDENT_BLOCK_TIME_SCHEMA')
    calendar=dt.datetime.strptime(m[1]+('+0000' if m[3]=='Z' else m[3].replace(':','')),'%Y-%m-%dT%H:%M:%S%z')
    if int(calendar.timestamp())!=quantity(header['timestamp']) or (m[2] and int(m[2])!=0):raise Stop('INDEPENDENT_BLOCK_TIME_MISMATCH')
    return {'status':'BOUNDED_INDEPENDENT_HEAD_AND_FIXED_B_CHECK','head_public':{k:root.get(k) for k in ['name','height','hash','time']},'fixed_B':block['height'],'fixed_hash':block['hash'],'fixed_time_raw':block['time'],'raw_artifacts':records,'limit':'Two bounded preflight observations only, not continuous14day independenttimeliness/globalfastest/independentbackends proof. No automaticpolling.'}


def verify_release(binding):
    path=UNIT/'root/remaining-preflight-run04-release.json'
    if not path.is_file():raise Stop('STATIC_RELEASE_MISSING')
    r=json.loads(path.read_bytes())
    if r.get('status')!='RELEASED_READONLY_A_PREFLIGHT' or r.get('bindings_sha256')!=digest(binding.raw) or r.get('run_id')!=RUN_ID:raise Stop('STATIC_RELEASE_BINDING')
    for p in [HERE/'readonly_core.py',HERE/'readonly_collector.py',HERE/'start-A-remaining-preflight-run04.command']:
        if r.get('reviewed_code_sha256',{}).get(p.name)!=digest(p.read_bytes()):raise Stop('STATIC_RELEASE_CODE_HASH')
    return r


def load_resource_amendment(c):
    source=c['resource_authorization'];raw=pathlib.Path(source['path']).read_bytes()
    if digest(raw)!=source['sha256']:raise Stop('RESOURCE_AUTHORIZATION_HASH')
    r=json.loads(raw)
    if r.get('status')!='APPROVED_REMAINING_A_UNIT_ADAPTATION_NOT_YET_LIVE' or r.get('prior_usage_reset') is not False:raise Stop('RESOURCE_AUTHORIZATION_STATUS')
    caps=r['caps_changed'];unchanged=r['caps_unchanged']
    if caps.get('absolute_adaptation_preflight_stop_UTC')!='2026-10-20T08:10:50Z' or caps.get('adaptation_preflight_cumulative_hours')!=5.5 or caps.get('additional_single_window_hours')!=2 or caps.get('window_start_UTC')!='2026-10-20T06:10:50Z':raise Stop('RESOURCE_AUTHORIZATION_CAPS')
    required={'CPU_total_seconds':7200,'threads':2,'RAM_GiB':1,'new_disk_GiB_cumulative':2,'shared_methods':400000,'peak_CU_per_second':100,'new_platform_payments':0,'human_total_hours':8,'shared_A_B_CU':25000000,'actual_remaining_free_balance_stricter':True}
    if any(unchanged.get(k)!=v for k,v in required.items()):raise Stop('RESOURCE_UNCHANGED_CAPS_MISMATCH')
    if r.get('B_models_training_return_backtests_wallets_signatures_transactions_authorized') is not False:raise Stop('RESOURCE_SCOPE_MISMATCH')
    for key in ['proposal','accepted_proposal_review']:
        x=r[key]
        if digest(pathlib.Path(x['path']).read_bytes())!=x['sha256']:raise Stop('RESOURCE_APPROVAL_SOURCE_HASH')
    source=c['state_hash_identifier_source']
    if digest(pathlib.Path(source['path']).read_bytes())!=source['sha256']:raise Stop('HASH_IDENTIFIER_SOURCE_HASH')
    return r


def authorized_peak(c,release):
    source=c.get('supplemental_peak_authorization',{})
    if source.get('path')!=str(UNIT/'root/peak300-supplemental-authorization.json'):raise Stop('PEAK_AUTHORIZATION_PATH')
    path=pathlib.Path(source['path'])
    if not path.is_file():raise Stop('PEAK_AUTHORIZATION_MISSING')
    raw=path.read_bytes()
    if source.get('sha256')!=digest(raw):raise Stop('PEAK_AUTHORIZATION_HASH')
    a=json.loads(raw)
    original=c['resource_authorization']
    if original.get('sha256')!='9db20a81259f7574dac7755cfff92515008787317b7b71831181c9c5737600dd' or a.get('original_resource_authorization')!=original:raise Stop('PEAK_PARENT_AUTHORIZATION_BINDING')
    if a.get('status')!='APPROVED_PEAK300_ONLY' or a.get('human_approved') is not True or type(a.get('approved_peak_CU_per_second')) is not int or a['approved_peak_CU_per_second']!=300:raise Stop('PEAK_HUMAN_AUTHORIZATION_REQUIRED')
    if a.get('prior_usage_reset') is not False or a.get('other_caps_unchanged') is not True or a.get('deadline_UTC')!='2026-10-20T08:10:50Z':raise Stop('PEAK_AUTHORIZATION_SCOPE')
    if release.get('supplemental_peak_authorization_sha256')!=digest(raw) or release.get('authorized_peak_CU_per_second')!=300:raise Stop('PEAK_RELEASE_BINDING')
    return 300


def load_admission(path):
    b=Bindings(path);c=b.config
    b.release=verify_release(b);load_resource_amendment(c);b.authorized_peak=authorized_peak(c,b.release)
    prior_cpu=b.release.get('prior_CPU_upper_bound_seconds')
    if type(prior_cpu) not in (int,float) or not 6319<=prior_cpu<7200:raise Stop('PRIOR_CPU_UPPER_BOUND_UNBOUND')
    if c.get('stream_billing_source_bound') is not True or c.get('stream_CU_per_byte')!='0.04':raise Stop('STREAM_BILLING_UNBOUND')
    billing=c['billing_source'];bb=pathlib.Path(billing['path']).read_bytes()
    if digest(bb)!=billing['sha256']:raise Stop('BILLING_SOURCE_HASH')
    source=json.loads(bb)
    if c['rpc_CU']!=source['method_CU']:raise Stop('METHOD_BILLING_VALUES_MISMATCH')
    if source.get('bandwidth_CU_numerator')!=4 or source.get('bandwidth_CU_denominator')!=100:raise Stop('STREAM_BILLING_SOURCE_MISMATCH')
    for name in ['eth_chainId','eth_getBlockByNumber','eth_getCode','eth_call','eth_getLogs','eth_getTransactionByHash','eth_getTransactionReceipt']:
        if type(c['rpc_CU'].get(name))!=int or c['rpc_CU'][name]<0:raise Stop('RPC_BILLING_UNBOUND')
    if c.get('constants_source_bound') is not True:raise Stop('COMPENSATION_CONSTANTS_NOT_BOUND')
    for src in c['constants_sources']+[c['fee_policy']['engineering_defaults']]:
        if digest(pathlib.Path(src['path']).read_bytes())!=src['sha256']:raise Stop('CONSTANTS_OR_FEE_SOURCE_HASH')
    quota=c['quota_source'];qb=pathlib.Path(quota['path']).read_bytes()
    if digest(qb)!=quota['sha256']:raise Stop('QUOTA_RECEIPT_INVALID')
    usage=json.loads(qb)
    if usage.get('project_working_free_balance_ceiling_CU')!=25000000 or usage.get('retained_local_CU_reserved')!=447 or usage.get('retained_local_method_attempts')!=19 or usage.get('no_payment_or_settings_change') is not True or usage.get('credential_access') is not False:raise Stop('RECOVERY_QUOTA_SCOPE')
    state=c.get('shared_prior_usage',{})
    if state.get('cu')!=447 or state.get('methods')!=19:raise Stop('RECOVERY_PRIOR_USAGE_UNBOUND')
    src=c['prior_CPU_source'];raw=pathlib.Path(src['path']).read_bytes()
    if digest(raw)!=src['sha256']:raise Stop('RECOVERY_PRIOR_CPU_SOURCE_HASH')
    return b


def run_live(binding_path):
    deadline=dt.datetime(2026,10,20,8,10,50,tzinfo=dt.timezone.utc).timestamp()
    seconds=math.floor(deadline-time.time())
    if seconds<=0:raise Stop('PREFLIGHT_ADAPTATION_DEADLINE')
    def timeout_handler(signum,frame):raise Stop('PREFLIGHT_ADAPTATION_DEADLINE')
    signal.signal(signal.SIGALRM,timeout_handler);signal.alarm(seconds)
    b=load_admission(binding_path);c=b.config;stage('STATIC_CHECKS_PASSED')
    # No credential prompt until nonsecret prerequisites validate. All inputs come from local TTY.
    # Nonsecret quota already documented by Root; no second user questionnaire.
    quota=c['quota_source'];qb=pathlib.Path(quota['path']).read_bytes()
    if digest(qb)!=quota['sha256']:raise Stop('QUOTA_RECEIPT_HASH')
    usage=json.loads(qb);remaining=c['verified_free_working_ceiling_CU'];methods=400000
    if remaining!=25000000:raise Stop('RECOVERY_FREE_WORKING_CAP')
    if type(remaining)!=int or remaining<=0:raise Stop('NO_VERIFIED_FREE_QUOTA')
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    stage('WAITING_LOCAL_INPUT');endpoint=prompt_endpoint()
    resource.setrlimit(resource.RLIMIT_CPU,(7200,7200))
    for role in b.records:
        if not b.runtime[role]:raise Stop('RUNTIME_NOT_BOUND')
    # Shared prior expenditures must be fixed by Root, not silently reset to zero.
    if 'shared_prior_usage' not in c:raise Stop('SHARED_BUDGET_UNBOUND')
    prior=dict(c['shared_prior_usage']);prior['cpu']=b.release['prior_CPU_upper_bound_seconds']+time.process_time()  # Include startup/input CPU, not waitingwall.
    budget=Budget(min(remaining,25_000_000),min(methods,400_000),peak=b.authorized_peak,state=prior);evidence=Evidence(RUN_DIR/'evidence',UNIT);rpc=RPC(endpoint,budget,evidence,c['rpc_CU'])
    stream=None;state={'status':'LIVE_PREFLIGHT_IN_PROGRESS','started':utc(),'A_observation_started':False}
    with (RUN_DIR/'live-once.lock').open('x') as f:f.write(json.dumps({'UTC':utc(),'PID':os.getpid(),'run_id':RUN_ID}))
    stage('LIVE_PREFLIGHT_IN_PROGRESS')
    try:
        if rpc.call('eth_chainId',[])!='0x1':raise Stop('CHAIN_ID')
        h=rpc.call('eth_getBlockByNumber',['latest',False])
        for role,target in b.addresses.items():
            live=rpc.call('eth_getCode',[target,h['number']])
            if live.lower()!=b.runtime[role]:raise Stop('RUNTIME_MISMATCH_'+role.upper())
        rpc.close()  # Successful identity group complete before public/WS waits.
        reference=independent_preflight_reference(evidence,h);evidence.save('independent-reference-check',reference)
        stream=HeadStream(endpoint,budget,evidence,c['stream_subscribe_CU'],c['stream_CU_per_byte'])
        probe_track=ChainTrack();wait_samples=[]
        for _ in range(3):
            bs=evidence.used();cs=time.process_time();probe=forward_head(stream,probe_track,c['timeliness'],evidence)
            wait_samples.append({'disk':evidence.used()-bs,'cpu':time.process_time()-cs})
        lower_now=dt.datetime.now(dt.timezone.utc);lower_t0=(lower_now+dt.timedelta(days=1)).replace(hour=0,minute=0,second=0,microsecond=0)
        lower=forecast(c,budget,0,0,0,stream.notification_wire_bytes,(lower_t0-lower_now).total_seconds())
        evidence.save('preflight-minimum-quota-bound',{'bound':lower,'actual_N_read':False,'not_scan_CPU_or_disk_validation':True})
        scanner=Scanner(b,rpc);timely(probe,c['timeliness']);initial_start=time.monotonic();snap=scanner.snapshot(probe,initial=True);evidence.save('preflight-snapshot',compact_snapshot(snap));timely(probe,c['timeliness'],time.monotonic()-initial_start,stream.backlog())
        measured=[]
        for _ in range(c.get('preflight_heads',3)):
            bs=evidence.used();cs=time.process_time();old=budget.state();head=forward_head(stream,probe_track,c['timeliness'],evidence);processing=time.monotonic()
            ss=scanner.snapshot(head);evidence.save('preflight-head',compact_snapshot(ss));elapsed=time.monotonic()-processing
            timely(head,c['timeliness'],elapsed,stream.backlog())
            measured.append({'disk':evidence.used()-bs,'cpu':time.process_time()-cs,'processing_seconds':elapsed,'CU':budget.cu-old['cu'],'methods':budget.methods-old['methods'],'B':head['number'],'hash':head['hash']})
        now=dt.datetime.now(dt.timezone.utc);t0=(now+dt.timedelta(days=1)).replace(hour=0,minute=0,second=0,microsecond=0);t1=t0+dt.timedelta(days=14)
        estimate=forecast(c,budget,0,0,notification_bytes=stream.notification_wire_bytes,wait_seconds=(t0-now).total_seconds(),measured=measured,already_disk=evidence.used(),wait_disk=max(x['disk'] for x in wait_samples),wait_cpu=max(x['cpu'] for x in wait_samples))
        signal.alarm(0)
        state.update(status='ARMED_ACTIVE_PROCESS',T0=t0.isoformat(),T1=t1.isoformat(),preflight=estimate,pid=os.getpid(),binding_sha256=digest(b.raw),code_sha256={p.name:digest(p.read_bytes()) for p in [HERE/'readonly_core.py',HERE/'readonly_collector.py']})
        evidence.save('admission',state);stage('ARMED_ACTIVE_PROCESS');print('ARMED_ACTIVE_PROCESS; T0='+t0.isoformat()+'; key not saved.',flush=True)
        tracker=ChainTrack();episodes=Episodes();last_audit=None;covered=0;unknown=0;scenario_wei=0;completed_count=0;clock_wall=time.time();clock_mono=time.monotonic();anchor_B=None;audit_usage={'transactions':0,'disk':0,'cpu':0}
        def audit_window(lo,hi,headers):
            old_disk=evidence.used();old_cpu=time.process_time();remaining=c['audit_reserve']['max_detail_transactions']-audit_usage['transactions']
            result=completed_event_audit(rpc,b,lo,hi,headers,max_transactions=remaining);evidence.save('result-audit',result)
            audit_usage['transactions']+=len(result['completed_transactions']);audit_usage['disk']+=evidence.used()-old_disk;audit_usage['cpu']+=time.process_time()-old_cpu
            if audit_usage['disk']>c['audit_reserve']['disk_bytes'] or audit_usage['cpu']>c['audit_reserve']['cpu_seconds']:raise Stop('AUDIT_ALLOWANCE_EXHAUSTED_UNKNOWN')
            return result
        while dt.datetime.now(dt.timezone.utc)<t1:
            budget.resource_check()
            if abs((time.time()-clock_wall)-(time.monotonic()-clock_mono))>1:raise Stop('UTC_MONOTONIC_CLOCK_DISCONTINUITY')
            head=stream.head();received=dt.datetime.now(dt.timezone.utc);timely(head,c['timeliness'])
            if received<t0:continue
            if received>=t1:break
            n=quantity(head['number']);event=tracker.accept(head)
            if event=='DUPLICATE':continue
            if event=='REORG':
                episodes.unknown()
                if anchor_B is not None and n<=anchor_B:raise Stop('REORG_INVALIDATES_FIXED_USD_ANCHOR')
                last_audit=min(last_audit,n-1) if last_audit is not None else None;evidence.save('reorg',{'UTC':utc(),'header':head,'action':'Priorbranch snapshots/virtualdecisions invalidated; no reranking to claim freshopportunity','coverage_complete':False});unknown+=1
            processing=time.monotonic();snapshot=scanner.snapshot(head);timely(head,c['timeliness'],time.monotonic()-processing,stream.backlog())
            if dt.datetime.fromisoformat(snapshot['formed']['UTC'])>=t1:
                evidence.save('late-final-snapshot',compact_snapshot(snapshot));unknown+=1;break
            if snapshot['oracle_raw']['simulated_newOracleFailureDetected']:
                episodes.unknown();evidence.save('oracle-policy-skip',snapshot);continue
            if scanner.usd_anchor is None:
                scanner.usd_anchor=int(snapshot['protocol_price_18']);anchor_B=n
                evidence.save('A-USD-anchor',{'B':head['number'],'hash':head['hash'],'protocol_ETH_USD_18':str(scanner.usd_anchor),'arrival':head['_received_UTC'],'formed':snapshot['formed'],'fixed_before_candidate_fee_evaluation':True})
                snapshot['rows']=qualify(snapshot['rows'],snapshot['count'],int(snapshot['MCR']),int(snapshot['SP_total']),int(snapshot['protocol_price_18']),quantity(head['baseFeePerGas']),c['fee_policy'],scanner.usd_anchor)
            day=snapshot['formed']['UTC'][:10];selected=episodes.update(snapshot['rows'],day,head['hash'])
            if selected:scenario_wei+=selected['minimum_reward_minus_ceiling']
            snapshot['virtual_selected']=selected;snapshot['not_fill']=True;evidence.save('snapshot',compact_snapshot(snapshot));covered+=1
            n=quantity(head['number'])
            if last_audit is None:last_audit=n-1
            if n-last_audit>=100:
                audit=audit_window(last_audit+1,n,tracker.headers);completed_count+=len(audit['completed_transactions']);last_audit=n
            timely(head,c['timeliness'],time.monotonic()-processing,stream.backlog())
            if covered%20==0:evidence.save('heartbeat',{'status':'OBSERVING','covered_blocks':covered,'unknown':unknown,'UTC':utc(),'budget':budget.state()})
        if last_audit is not None and tracker.tip>last_audit:audit_window(last_audit+1,tracker.tip,tracker.headers)
        state.update(status='WINDOW_ENDED_PENDING_INDEPENDENT_REVIEW',covered_blocks=covered,unknown_reorgs=unknown,episode_participations=episodes.participations,UTC_day_clusters=episodes.daily,scenario_reward_less_assumed_gas_wei=str(scenario_wei),scenario_after_actual_necessary_costs='UNKNOWN_PENDING_ACTUAL_LABOR_INFRASTRUCTURE_LEDGER_AND_INDEPENDENT_REVIEW',completed_tx_audits=completed_count,coverage_ratio_and_missed_unknown='Independent canonical/timing audit required; never fill gaps0',complete_A_pass_not_automatically_declared=True)
    except Stop as ex:state.update(status='STOPPED_INCONCLUSIVE',safe_reason=str(ex),safe_details=getattr(ex,'details',None),coverage_unknown=True)
    except BaseException as ex:state.update(status='STOPPED_INCONCLUSIVE',safe_reason='LOCAL_'+type(ex).__name__,coverage_unknown=True)
    finally:
        if stream:stream.close()
        rpc.close()
        state['ended']=utc();state['budget']=budget.state()
        # No credential/provider error repr or traceback is serialized.
        evidence.save('terminal',state,endpoint);stage(state['status']);print(state['status']+'; '+state.get('safe_reason','end'),flush=True)


def main():
    ap=argparse.ArgumentParser(description='A-only collector; endpoint is never an argument.')
    ap.add_argument('--check-bindings',type=pathlib.Path);ap.add_argument('--live',type=pathlib.Path)
    args=ap.parse_args()
    try:
        if args.check_bindings:
            b=load_admission(args.check_bindings);print(json.dumps({'status':'STATIC_INPUTS_VALID_NOT_LIVE','binding_sha256':digest(b.raw)}));return
        if args.live:run_live(args.live);return
        ap.print_help()
    except Stop as ex:
        if args.live:stage('STOPPED_'+str(ex))
        print('STOP: '+str(ex));sys.exit(2)
    except BaseException as ex:
        if args.live:stage('STOPPED_LOCAL_'+type(ex).__name__)
        print('STOP: LOCAL_'+type(ex).__name__);sys.exit(2)
if __name__=='__main__':main()

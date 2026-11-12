"""Formal A entry candidate. No key, no automatic Root release or implicit startup."""
from adapters import *
from stream import FormalStream,finalize_terminal
from observer_loop import observe_window

CODE_FILES=['adapters.py','stream.py','observer_loop.py','observer.py']
CAPS={'total_CPU_seconds':18000,'project_shadow_CU':25000000,'project_total_methods':400000,'project_disk_bytes':8589934592,'disk_reserve_bytes':1048576,'threads':2,'RAM_project_bytes':1073741824,'RPC_body_bytes':8388608,'WS_message_bytes':1048576,'peak_engineering_CU_per_10seconds':3000,'per_message_frame_cap':16,'per_message_control_cap':8,'new_payments':0}

def stage(status,state):
    row={'status':status,'PID':os.getpid(),'UTC':utc(),'monotonic_ns':time.monotonic_ns(),'no_key_or_user_input':True,'process_CPU_seconds':time.process_time(),'budget':state.get('budget')}
    with (HERE/'runtime-stage.jsonl').open('a') as f:f.write(json.dumps(row,separators=(',',':'))+'\n')

def verify_release():
    raw=(HERE/'binding.json').read_bytes();cfg=json.loads(raw)
    if cfg.get('publication_status')!='BOUND_FORMAL_A_WAIT_ROOT_RELEASE':raise Stop('FORMAL_BINDING_NOT_PUBLISHED')
    if cfg.get('limits')!=CAPS or cfg.get('T0')!='2026-10-21T00:00:00Z' or cfg.get('T1')!='2026-11-04T00:00:00Z':raise Stop('FORMAL_CAPS_OR_WINDOW_CHANGED')
    expected_path=BASE/'root/dRPC-formal-A-Root-release-20261020.json'
    if pathlib.Path(cfg.get('root_release_path',''))!=expected_path:raise Stop('ROOT_RELEASE_LOCATION')
    rr=expected_path.read_bytes();release=json.loads(rr)
    if release.get('status')!='RELEASED_FORMAL_A_ANONYMOUS_READONLY' or release.get('binding_sha256')!=digest(raw):raise Stop('ROOT_FORMAL_RELEASE_NOT_EXACT')
    if release.get('limits')!=CAPS or release.get('T0')!=cfg['T0'] or release.get('T1')!=cfg['T1']:raise Stop('ROOT_RELEASE_CAPS_WINDOW')
    if set(release.get('code_sha256',{}))!=set(CODE_FILES):raise Stop('ROOT_SOURCE_SET')
    for name in CODE_FILES:
        if digest((HERE/name).read_bytes())!=release['code_sha256'][name]:raise Stop('ROOT_SOURCE_HASH')
    prior=release.get('prior_usage',{})
    for name,floor,cap in [('shadow_CU',33850,25000000),('methods',93,400000),('CPU_guard',7440,18000)]:
        if type(prior.get(name)) is not int or not floor<=prior[name]<cap:raise Stop('RELEASE_PRIOR_USAGE_NOT_RETAINED')
    if prior.get('Alchemy_CU')!=32734:raise Stop('OLD_ALCHEMY_USAGE_CHANGED')
    now=dt.datetime.now(dt.timezone.utc);t0=dt.datetime.fromisoformat(cfg['T0'].replace('Z','+00:00'))
    deadline=dt.datetime.fromisoformat(release['startup_deadline_UTC'].replace('Z','+00:00'))
    if not now<deadline<=t0:raise Stop('ROOT_STARTUP_RELEASE_EXPIRED_OR_AFTER_T0')
    return cfg,release,{'binding_sha256':digest(raw),'Root_release_sha256':digest(rr)},deadline

def verified_json(source):
    data=pathlib.Path(source['path']).read_bytes()
    if digest(data)!=source['sha256']:raise Stop('ACCEPTED_SOURCE_HASH_CHANGED')
    return json.loads(data)

class FormalScanner(HashScanner):
    def aggregate(self,calls,tag):
        result=super().aggregate(calls,tag)
        if len(calls)==1 and calls[0]==self.b.method('tm','getTroveIdsCount') and result[0][0]:
            n=uints(result[0][1],1)[0]
            if ((n+31)//32)*32+32>160:raise Stop('ADMITTED_PADDING_GROWTH_REQUIRES_NEW_PREFLIGHT')
        return result

def audit_method_compatibility(rpc,b,h,evidence):
    B,H=h['number'],h['hash']
    logs=rpc.call('eth_getLogs',[{'address':b.addresses['tm'],'fromBlock':B,'toBlock':B}])
    for log in logs:
        if log['blockNumber']!=B or log['blockHash']!=H or log['address'].lower()!=b.addresses['tm'] or log.get('removed') is True:raise Stop('STARTUP_LOG_BLOCK_IDENTITY')
    txs=h.get('transactions')
    if not isinstance(txs,list) or not txs:raise Stop('STARTUP_EMPTY_BLOCK_TRANSACTION_METHOD_UNKNOWN')
    txhash=txs[0];hash32(txhash)
    tx=rpc.call('eth_getTransactionByHash',[txhash]);receipt=rpc.call('eth_getTransactionReceipt',[txhash])
    if tx.get('hash')!=txhash or receipt.get('transactionHash')!=txhash or tx.get('blockHash')!=H or receipt.get('blockHash')!=H or tx.get('blockNumber')!=B or receipt.get('blockNumber')!=B:raise Stop('STARTUP_TX_RECEIPT_IDENTITY')
    fence=rpc.call('eth_getBlockByNumber',[B,False])
    if fence.get('hash')!=H or fence.get('number')!=B:raise Stop('STARTUP_COMPATIBILITY_FENCE')
    evidence.save('startup-audit-method-compatibility',{'B':B,'hash':H,'fixed_first_tx':txhash,'log_count':len(logs),'success':True,'not_profit_case_selection':True})

def forecast_from_samples(cfg,c,budget,evidence,prior_result,stream,fresh_cycle,fresh_wait):
    now=dt.datetime.now(dt.timezone.utc);t0=dt.datetime.fromisoformat(cfg['T0'].replace('Z','+00:00'))
    if now>=t0:raise Stop('ORIGINAL_T0_NO_LONGER_FULLY_AVAILABLE')
    measured=list(prior_result['measured_cycles'])+[fresh_cycle]
    wait=list(prior_result['wait_samples'])+fresh_wait
    notifications=list(prior_result['notification_wire_bytes'])+stream.notification_wire_bytes
    return original.forecast(c,budget,0,0,notification_bytes=notifications,wait_seconds=(t0-now).total_seconds(),measured=measured,already_disk=evidence.used(),wait_disk=max(x['disk'] for x in wait),wait_cpu=max(x['cpu'] for x in wait))

def main():
    state={'status':'FORMAL_ENTRY_PENDING_VALIDATION','started':utc(),'A_observation_started':False,'no_key_or_user_input':True,'ARMED':False,'dRPC_actual_CU':'UNKNOWN','dRPC_anonymous_remaining_CU':'UNKNOWN'}
    rpc=stream=evidence=budget=None
    try:
        cfg,release,identity,deadline=verify_release();state.update(identity)
        def startup_alarm(signum,frame):raise Stop('FORMAL_STARTUP_DEADLINE')
        signal.signal(signal.SIGALRM,startup_alarm);signal.alarm(max(1,math.ceil(deadline.timestamp()-time.time())))
        with (HERE/'formal-start.once').open('x') as f:f.write(json.dumps({'UTC':utc(),'PID':os.getpid(),'Root_release_sha256':identity['Root_release_sha256']}))
        acceptance=verified_json(cfg['accepted_preflight']['Root_acceptance'])
        if acceptance.get('status')!='ROOT_ACCEPTED_CURRENT_BOUNDED_FULL_CENSUS_TECHNICAL_PREFLIGHT_ONLY':raise Stop('ROOT_PREFLIGHT_NOT_ACCEPTED')
        old=verified_json(cfg['accepted_preflight']['result'])
        if old.get('status')!='PASS_BOUNDED_FULL_CENSUS_PREFLIGHT_ONLY_NOT_ARMED' or len(old.get('measured_cycles',[]))!=3:raise Stop('ACCEPTED_PREFLIGHT_SAMPLE_IDENTITY')
        p=pathlib.Path(cfg['original_binding']['path'])
        if digest(p.read_bytes())!=cfg['original_binding']['sha256']:raise Stop('ORIGINAL_BINDING_CHANGED')
        b=original.Bindings(p);c=b.config
        for source in cfg['policy_sources']+c['constants_sources']+[c['fee_policy']['engineering_defaults']]:
            if digest(pathlib.Path(source['path']).read_bytes())!=source['sha256']:raise Stop('FROZEN_POLICY_OR_ECONOMIC_SOURCE_CHANGED')
        c['effective_limits']={'new_disk_bytes_cumulative':8589934592,'disk_admission_reserve_bytes':1048576}
        t0,t1=original.fixed_observation_window(c)
        evidence=DataEvidence(HERE/'evidence',BASE,cap=8589934592)
        route=DRPCRoute.from_system();prior=release['prior_usage']
        original.set_process_CPU_limit({'CPU_total_seconds_cumulative':18000},prior['CPU_guard'],route.config_child_CPU_seconds)
        budget=FormalBudget(25000000,400000,peak=300,cpu=18000,ram=1073741824,state={'cu':prior['shadow_CU'],'methods':prior['methods'],'cpu':prior['CPU_guard']+time.process_time()+route.config_child_CPU_seconds})
        state['prior_usage']=prior;state['status']='FORMAL_STARTUP_CHECKING';stage(state['status'],state)
        rpc=FormalRPC(AnonymousEndpoint(),budget,evidence,c['rpc_CU'],max_body=8388608,route=route)
        if rpc.call('eth_chainId',[])!='0x1':raise Stop('CHAIN_ID')
        h=rpc.call('eth_getBlockByNumber',['latest',False]);original.timely(h,c['timeliness'])
        for role,target in b.addresses.items():
            live=rpc.call('eth_getCode',[target,{'blockHash':h['hash'],'requireCanonical':True}])
            if rawhex(live)!=rawhex(b.runtime[role]):raise Stop('RUNTIME_MISMATCH_'+role.upper())
        audit_method_compatibility(rpc,b,h,evidence);rpc.close()
        # Exact accepted independent metadata identity/time validator, with error raw suppressed.
        raw_save=evidence.save
        def safe_save(kind,obj,endpoint=None):
            if kind=='independent-reference' and (obj.get('safe_error') or obj.get('HTTP')!=200):
                obj=dict(obj);data=obj.pop('body_utf8','').encode();obj['body_bytes']=len(data);obj['body_sha256']=digest(data);obj['safe_error']='PUBLIC_REFERENCE_FAILED';obj['raw_error_body_saved']=False
            return raw_save(kind,obj,endpoint)
        evidence.save=safe_save
        reference=original.independent_preflight_reference(evidence,h);evidence.save('independent-reference-check',reference)
        stream=FormalStream(route,budget,evidence,state,time.monotonic());continuity=ChainTrack();fresh_wait=[]
        bs=evidence.used();cs=time.process_time();head=original.forward_head(stream,continuity,c['timeliness'],evidence)
        fresh_wait.append({'disk':evidence.used()-bs,'cpu':time.process_time()-cs})
        scanner=FormalScanner(b,rpc);processing=time.monotonic();initial=scanner.snapshot(head,initial=True)
        evidence.save('startup-current-initial-snapshot',original.compact_snapshot(initial));original.timely(head,c['timeliness'],time.monotonic()-processing,stream.backlog())
        bs=evidence.used();cs=time.process_time();old_budget=budget.state();wait_disk=evidence.used();wait_cpu=time.process_time()
        head=original.forward_head(stream,continuity,c['timeliness'],evidence)
        fresh_wait.append({'disk':evidence.used()-wait_disk,'cpu':time.process_time()-wait_cpu})
        processing=time.monotonic();snapshot=scanner.snapshot(head);evidence.save('startup-current-steady-snapshot',original.compact_snapshot(snapshot));elapsed=time.monotonic()-processing
        original.timely(head,c['timeliness'],elapsed,stream.backlog())
        cycle={'disk':evidence.used()-bs,'cpu':time.process_time()-cs,'processing_seconds':elapsed,'CU':budget.cu-old_budget['cu'],'methods':budget.methods-old_budget['methods'],'B':head['number'],'hash':head['hash'],'scope':'notification+complete same-H scan+save; original3 cycles retained without replacement'}
        estimate=forecast_from_samples(cfg,c,budget,evidence,old,stream,cycle,fresh_wait)
        # Actual filesystem headroom is separate from cumulative project disk allowance.
        fs=os.statvfs(HERE);available=fs.f_bavail*fs.f_frsize
        needed=estimate['disk_including_already_and_wait_and_audit']-evidence.used()+1048576
        if available<needed:raise Stop('ACTUAL_FILESYSTEM_HEADROOM_INSUFFICIENT')
        evidence.save('formal-startup-admission',{'UTC':utc(),'estimate':estimate,'fresh_cycle':cycle,'fresh_wait':fresh_wait,'physical_free_bytes':available,'needed_additional_bytes_with_reserve':needed,'provider_actual_balance':'UNKNOWN','Root_release':identity})
        signal.alarm(0)
        state.update(status='ARMED_ACTIVE_PROCESS',ARMED=True,T0=t0.isoformat(),T1=t1.isoformat(),preflight=estimate,PID=os.getpid())
        state['budget']=budget.state();stage(state['status'],state)
        # First T0 snapshot freezes its own protocol USD anchor before fee evaluation.
        observe_window(b,c,budget,evidence,rpc,stream,scanner,t0,t1,state,continuity,lambda:stage('OBSERVING',state))
    except Stop as ex:
        state.update(status='STOPPED_INCONCLUSIVE',safe_reason=str(ex),safe_details=ex.details,coverage_unknown=True)
    except BaseException as ex:
        state.update(status='STOPPED_INCONCLUSIVE',safe_reason=core._DIAGNOSTIC_TYPES.get(type(ex),'OTHER'),coverage_unknown=True)
    finally:
        signal.alarm(0)
        if stream is not None:stream.close()
        if rpc is not None:rpc.close()
        state['ended']=utc();state['active_process']=False
        state['ever_ARMED']=state.get('ARMED',False);state['ARMED']=False
        if budget is not None:state['budget']=budget.state()
        if evidence is not None:finalize_terminal(evidence,state)
        state['process_CPU_seconds']=time.process_time();child=resource.getrusage(resource.RUSAGE_CHILDREN);state['children_CPU_seconds']=child.ru_utime+child.ru_stime
        with (HERE/'terminal.json').open('x') as f:f.write(json.dumps(state,indent=2)+'\n')
        stage(state['status'],state)
    return 0 if state['status']=='WINDOW_ENDED_PENDING_INDEPENDENT_REVIEW' else 1

if __name__=='__main__':raise SystemExit(main())

#!/usr/bin/env python3
"""One explicitly authorized fixed historical getCode; no full A collector import."""
from readonly_core import *
import signal
HERE=pathlib.Path(__file__).resolve().parent
UNIT=HERE.parent
ADDRESS='0xca11bde05977b3631167028862be2a173976ca11'
BLOCK='0x19043c9'
DEADLINE='2026-10-20T06:04:55Z'
INITIAL_CPU=time.process_time()

def phase(status):
    row={'status':status,'PID':os.getpid(),'UTC':utc(),'monotonic_ns':time.monotonic_ns(),'credential_saved':False}
    with (HERE/'one-read-diagnostic-stage.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')

def arm_deadline():
    end=dt.datetime(2026,10,20,6,4,55,tzinfo=dt.timezone.utc).timestamp()
    seconds=int(end-time.time())
    if seconds<=0:raise Stop('DIAGNOSTIC_DEADLINE')
    def stop_signal(signum,frame):raise Stop('DIAGNOSTIC_DEADLINE')
    signal.signal(signal.SIGALRM,stop_signal);signal.alarm(seconds)

def load_inputs():
    auth_path=UNIT/'root/one-read-diagnostic-auth.json';ab=auth_path.read_bytes();a=json.loads(ab)
    release=json.loads((UNIT/'root/one-read-diagnostic-release.json').read_bytes())
    if a.get('status')!='AUTHORIZED_SINGLE_FIXED_GETCODE_DIAGNOSTIC' or release.get('status')!='RELEASED_SINGLE_FIXED_GETCODE_DIAGNOSTIC' or release.get('auth_sha256')!=digest(ab):raise Stop('DIAGNOSTIC_AUTH_RELEASE')
    if a.get('deadline_UTC')!=DEADLINE or a.get('method')!='eth_getCode' or a.get('address')!=ADDRESS or a.get('block')!=BLOCK or a.get('max_RPC_methods')!=1 or a.get('no_retry') is not True or a.get('no_payment') is not True:raise Stop('DIAGNOSTIC_SCOPE')
    for name in ['readonly_core.py','one_read_diagnostic.py','start-one-read-diagnostic.command']:
        if release.get('reviewed_code_sha256',{}).get(name)!=digest((HERE/name).read_bytes()):raise Stop('DIAGNOSTIC_REVIEW_HASH')
    bb=(HERE/'bindings.json').read_bytes()
    if release.get('binding_sha256')!=digest(bb):raise Stop('DIAGNOSTIC_BINDING_HASH')
    binding=json.loads(bb);source=binding['contracts']['multicall'];raw=pathlib.Path(source['record_path']).read_bytes()
    if digest(raw)!=source['record_sha256'] or release.get('runtime_source_sha256')!=digest(raw):raise Stop('DIAGNOSTIC_RUNTIME_SOURCE_HASH')
    obj=json.loads(raw)
    if str(obj.get('chainId'))!='1' or obj.get('address','').lower()!=ADDRESS:raise Stop('DIAGNOSTIC_RUNTIME_IDENTITY')
    expected=obj['runtimeBytecode']['onchainBytecode'].lower()
    if not rawhex(expected):raise Stop('DIAGNOSTIC_RUNTIME_EMPTY')
    prior=a['prior_usage'];cpu=release.get('prior_CPU_upper_bound_seconds',prior.get('cpu'))
    if type(prior.get('cu'))is not int or prior['cu']!=120 or type(prior.get('methods'))is not int or prior['methods']!=7:raise Stop('DIAGNOSTIC_PRIOR_USAGE')
    if type(prior.get('cpu'))not in (int,float) or type(cpu)not in (int,float) or not 5836<=prior['cpu']<=cpu<7200:raise Stop('DIAGNOSTIC_PRIOR_CPU')
    remaining=a.get('verified_remaining_CU')
    if type(remaining)is not int or remaining<=140:raise Stop('DIAGNOSTIC_FREE_QUOTA')
    prior=dict(prior);prior['cpu']=cpu
    return a,prior,min(remaining,25000000),expected

def execute_once(endpoint,budget,evidence,expected):
    # The sole network method exists only here; RPC itself fails closed without retries.
    with (HERE/'one-read-diagnostic.once.lock').open('x') as lock:lock.write(json.dumps({'PID':os.getpid(),'UTC':utc(),'fixed_method':'eth_getCode','fixed_block':BLOCK}))
    phase('DIAGNOSTIC_ONE_REQUEST')
    rpc=RPC(endpoint,budget,evidence,{'eth_getCode':20});rpc.seq=6
    code=rpc.call('eth_getCode',[ADDRESS,BLOCK])
    same=code.lower()==expected
    return {'status':'SUCCESS_NOT_REPRODUCED_RUNTIME_MATCH' if same else 'STOPPED_RUNTIME_MISMATCH','runtime_exact_bytes_match':same,'observed_code_sha256_bytes':digest(rawhex(code)),'expected_code_sha256_bytes':digest(rawhex(expected)),'request_artifact':rpc.last_artifact,'meaning':'Success only means old transport error not reproduced on this read; no old-root-cause/fix/complete-A/profit conclusion.'}

def main():
    budget=None;evidence=None;result={'status':'STOPPED_BEFORE_REQUEST'}
    try:
        arm_deadline();a,prior,limit,expected=load_inputs();phase('STATIC_DIAGNOSTIC_CHECKS_PASSED')
        resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_CPU,(7200,7200))
        phase('WAITING_LOCAL_INPUT');endpoint=prompt_endpoint()
        prior['cpu']+=time.process_time()-INITIAL_CPU
        budget=Budget(cu_limit=limit,state=prior);budget.resource_check();evidence=Evidence(HERE/'one-read-diagnostic-evidence',UNIT)
        result=execute_once(endpoint,budget,evidence,expected)
    except Stop as ex:result={'status':'STOPPED_DIAGNOSTIC','safe_reason':str(ex)}
    except FileExistsError:result={'status':'STOPPED_DIAGNOSTIC','safe_reason':'DIAGNOSTIC_ONCE_LOCK_EXISTS'}
    except BaseException:result={'status':'STOPPED_DIAGNOSTIC','safe_reason':'LOCAL_OTHER'}
    finally:
        result.update(ended_UTC=utc(),old_A_not_restarted=True,diagnostic_max_requests=1)
        if budget:result['budget']=budget.state()
        try:
            if evidence:evidence.save('diagnostic-terminal',result)
            phase(result['status'])
        except BaseException:
            result={'status':'STOPPED_DIAGNOSTIC','safe_reason':'LOCAL_FINALIZATION_OTHER'}
        # Safe constants only; no endpoint or exception text.
        print(result['status']+'; '+result.get('safe_reason','END'),flush=True)
if __name__=='__main__':main()

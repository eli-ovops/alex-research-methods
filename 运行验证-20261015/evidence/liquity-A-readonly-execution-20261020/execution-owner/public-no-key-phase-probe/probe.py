#!/usr/bin/env python3
"""Unexecuted until exact Root release: one public HEAD /, no API/account/input."""
import datetime as dt, hashlib, importlib.util, json, pathlib, resource, signal, ssl, time
HERE=pathlib.Path(__file__).resolve().parent
UNIT=HERE.parents[1]
CORE=HERE.parent/'safe-open-phase-candidate/readonly_core.py'
CORE_SHA='96f67fec33e5d23edc3e67b029ccd695e23fa747176315a784ad62bde92eb82f'
HOST='eth-mainnet.g.alchemy.com'
PHASES={'SOCKET_CONNECT','PROXY_CONNECT_SEND','PROXY_CONNECT_HEADER','TLS_HANDSHAKE','HTTP_REQUEST_SEND','HTTP_RESPONSE_HEADER'}
STOP_CODES={'SYSTEM_ROUTE_IP_LITERAL_REQUIRED','SYSTEM_ROUTE_LOOPBACK_PORT_REQUIRED','SYSTEM_ROUTE_CONFIG_READ_FAILED','SYSTEM_ROUTE_DISABLED_OR_PAC','SYSTEM_ROUTE_PORT_REQUIRED','SYSTEM_ROUTE_STRICT_TLS_REQUIRED','SYSTEM_ROUTE_TIMEOUT','SYSTEM_ROUTE_CONNECT_HEADER_CAP','SYSTEM_ROUTE_CONNECT_EOF','SYSTEM_ROUTE_CONNECT_STATUS_INVALID','SYSTEM_ROUTE_CONNECT_NON200_NO_AUTH','PUBLIC_REQUEST_DEADLINE','PUBLIC_PROCESS_DEADLINE'}
class GuardStop(Exception):pass

def validate_release():
    p=UNIT/'root/public-no-key-phase-probe-release.json'
    if not p.is_file():raise GuardStop('RELEASE_MISSING')
    r=json.loads(p.read_bytes())
    if r.get('status')!='RELEASED_PUBLIC_HEAD_PHASE_ONCE' or r.get('probe_sha256')!=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest() or r.get('core_sha256')!=CORE_SHA:raise GuardStop('RELEASE_IDENTITY')
    if r.get('target')!={'host':HOST,'method':'HEAD','path':'/','attempts':1,'query':False,'authentication':False,'RPC':False}:raise GuardStop('RELEASE_SCOPE')
    if r.get('whole_process_wall_limit_seconds')!=20 or r.get('request_limit_seconds')!=15 or r.get('socket_limit_seconds')!=5:raise GuardStop('RELEASE_LIMITS')
    end=dt.datetime.fromisoformat(r['valid_until_UTC'].replace('Z','+00:00'))
    if dt.datetime.now(dt.timezone.utc)>=end:raise GuardStop('RELEASE_EXPIRED')
    if hashlib.sha256(CORE.read_bytes()).hexdigest()!=CORE_SHA:raise GuardStop('CORE_IDENTITY')


def main():
    # No route/TLS/module load or lock is performed before exact Root release and source identity.
    validate_release()
    lock=HERE/'public-head.once.lock'
    with lock.open('x') as f:f.write(json.dumps({'scope':'ONE_PUBLIC_HEAD_NOT_RPC_OR_OBSERVATION','UTC':dt.datetime.now(dt.timezone.utc).isoformat()}))
    start=time.monotonic();start_ns=time.monotonic_ns();phase='OPEN';connection=None;core=None
    child_before=resource.getrusage(resource.RUSAGE_CHILDREN)
    result={'status':'STOPPED_PUBLIC_HEAD','UTC_start':dt.datetime.now(dt.timezone.utc).isoformat(),'attempts':1,'public_transport_HEAD_attempts':1,'RPC_method_attempts':0,'prior_RPC_methods_retained':63,'prior_CU_retained':32734,'HTTP_status':None,'explicit_body_bytes_read':0,'raw_headers_or_body_saved':False,'strict_verify':True,'TLS_completed':False,'phases':[],'no_key_or_account_or_input':True}
    def mark(value):
        nonlocal phase
        phase=value if value in PHASES else 'OTHER'
        result['phases'].append({'phase':phase,'UTC':dt.datetime.now(dt.timezone.utc).isoformat(),'elapsed_monotonic_ns':time.monotonic_ns()-start_ns})
    def expired(signum,frame):raise GuardStop('PUBLIC_PROCESS_DEADLINE')
    signal.signal(signal.SIGALRM,expired);signal.alarm(20)
    try:
        spec=importlib.util.spec_from_file_location('isolated_safe_phase_definitions',CORE)
        core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
        # Only the previously reviewed definitions are imported. No RPC/HeadStream/prompt objects.
        route=core.SystemHTTPSRoute.from_system()
        context=ssl.create_default_context()
        if not context.check_hostname or context.verify_mode!=ssl.CERT_REQUIRED:raise GuardStop('STRICT_VERIFY_GUARD')
        request_start=time.monotonic()
        def remaining():
            n=15-(time.monotonic()-request_start)
            if n<=0:raise GuardStop('PUBLIC_REQUEST_DEADLINE')
            return n
        connection=core.RouteHTTPSConnection(route,timeout=remaining(),context=context,phase_callback=mark)
        connection.set_debuglevel(0);connection.connect();result['TLS_completed']=True
        connection.sock.settimeout(min(5,remaining()));mark('HTTP_REQUEST_SEND')
        connection.request('HEAD','/',body=None,headers={})
        connection.sock.settimeout(min(5,remaining()));mark('HTTP_RESPONSE_HEADER')
        response=connection.getresponse();remaining()
        if type(response.status)is not int or not 100<=response.status<=599:raise GuardStop('HTTP_STATUS_SCHEMA')
        result.update(status='ONE_PUBLIC_HTTP_RESPONSE_RECEIVED_NOT_RPC_PROOF',HTTP_status=response.status)
        # Never follow redirects, authenticate, retry, or read response body/header values.
        response.close()
    except BaseException as ex:
        allowed=STOP_CODES|{'STRICT_VERIFY_GUARD','HTTP_STATUS_SCHEMA'}
        code=ex.args[0] if type(ex)is GuardStop and len(ex.args)==1 and ex.args[0] in allowed else None
        if core is not None:
            result['safe_diagnostic']=core.safe_transport_diagnostic(ex,phase,start_ns,0)
            if type(ex)is core.Stop and len(ex.args)==1 and type(ex.args[0])is str and ex.args[0] in STOP_CODES:code=ex.args[0]
        else:result['safe_diagnostic']={'phase':'OTHER','exception_type':'OTHER'}
        result['safe_Stop_code']=code
    finally:
        signal.alarm(0)
        if connection is not None:
            try:connection.close()
            except Exception:pass
        child_after=resource.getrusage(resource.RUSAGE_CHILDREN)
        result.update(UTC_end=dt.datetime.now(dt.timezone.utc).isoformat(),whole_active_wall_seconds=time.monotonic()-start,process_CPU_seconds=time.process_time(),children_CPU_delta_seconds=child_after.ru_utime+child_after.ru_stime-child_before.ru_utime-child_before.ru_stime)
        with (HERE/'result.json').open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
        print(result['status'])
    return 0 if result['status']=='ONE_PUBLIC_HTTP_RESPONSE_RECEIVED_NOT_RPC_PROOF' else 2

if __name__=='__main__':
    try:exit_code=main()
    except GuardStop:print('STOPPED_LOCAL_RELEASE_GUARD');exit_code=2
    except BaseException:print('STOPPED_LOCAL_SAFE_GUARD');exit_code=2
    raise SystemExit(exit_code)

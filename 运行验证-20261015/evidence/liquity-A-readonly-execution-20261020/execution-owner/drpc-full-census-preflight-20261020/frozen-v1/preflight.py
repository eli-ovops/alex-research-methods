"""Bounded dRPC preflight only; never calls original run_live or arms observation."""
from adapters import *

WIRE_PATH=OWNER/'drpc-one-public-newheads-20261020/probe.py'
if digest(WIRE_PATH.read_bytes())!='51a6f18a9808fd1f6bc4f2b52c6dac7b53f6b14437dd4e0f165e0d7f238714b9':
    raise Stop('FROZEN_WS_CODEC_CHANGED')
spec=importlib.util.spec_from_file_location('frozen_public_ws_codec',WIRE_PATH)
codec=importlib.util.module_from_spec(spec);spec.loader.exec_module(codec)

class TimedWire(codec.Wire):
    def timeout(self):
        left=min(self.start+180,self.deadline)-time.monotonic()
        if left<=0:raise Stop('THIS_UNIT_WALL_OR_WS_PHASE_DEADLINE')
        return min(self.read_timeout_cap,left)

class PublicStream:
    def __init__(self,route,budget,evidence,state,start):
        self.route=route;self.budget=budget;self.evidence=evidence;self.state=state
        self.wire=TimedWire({},start);self.wire.deadline=min(start+180,time.monotonic()+15)
        self.notification_payload_bytes=[];self.notification_wire_bytes=[];self.subscription=None
        self.wire.sock=route.open_tls(ssl.create_default_context(),15)
        self.state['WS_connections']=1
        key=base64.b64encode(os.urandom(16)).decode('ascii')
        request=('GET / HTTP/1.1\r\nHost: eth.drpc.org\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: '+key+'\r\nSec-WebSocket-Version: 13\r\n\r\n').encode('ascii')
        self.wire.sock.settimeout(self.wire.timeout());self.wire.sock.sendall(request);header=b''
        while not header.endswith(b'\r\n\r\n'):
            if len(header)>=8192:raise Stop('WS_HANDSHAKE_CAP')
            header+=self.wire.read(1)
        try:lines=header.decode('ascii').split('\r\n')
        except UnicodeError:raise Stop('WS_HANDSHAKE_SCHEMA') from None
        m=re.fullmatch(r'HTTP/1\.1 ([0-9]{3})(?: [^\r\n]*)?',lines[0])
        if not m:raise Stop('WS_HANDSHAKE_STATUS')
        status=int(m[1]);headers={}
        self.evidence.save('ws-upgrade',{'UTC':utc(),'HTTP':status,'header_bytes':len(header),'header_sha256':digest(header),'raw_header_saved':False})
        if status!=101:raise Stop('WS_HANDSHAKE_NON101_NO_REDIRECT')
        for line in lines[1:-2]:
            if ':' not in line:raise Stop('WS_HANDSHAKE_SCHEMA')
            name,value=line.split(':',1);name=name.lower()
            if name in headers or not re.fullmatch(r'[a-z0-9!#$%&\x27*+.^_`|~-]+',name):raise Stop('WS_HANDSHAKE_DUPLICATE_OR_INVALID_HEADER')
            headers[name]=value.strip()
        accept=base64.b64encode(hashlib.sha1((key+codec.GUID).encode('ascii')).digest()).decode('ascii')
        if headers.get('upgrade','').lower()!='websocket' or 'upgrade' not in [x.strip().lower() for x in headers.get('connection','').split(',')] or headers.get('sec-websocket-accept')!=accept:raise Stop('WS_HANDSHAKE_ACCEPT')
        if 'sec-websocket-extensions' in headers or 'sec-websocket-protocol' in headers:raise Stop('WS_UNREQUESTED_NEGOTIATION')
        self.send_rpc('eth_subscribe',1,['newHeads'])
        self.wire.deadline=min(start+180,time.monotonic()+15)
        obj=self.receive('ack')
        if set(obj)!={'jsonrpc','id','result'} or obj.get('jsonrpc')!='2.0' or type(obj.get('id')) is not int or obj['id']!=1 or not isinstance(obj.get('result'),str) or not re.fullmatch(r'0x[0-9a-fA-F]{1,128}',obj['result']):raise Stop('WS_SUBSCRIBE_ACK_SCHEMA')
        self.subscription=obj['result'];self.state['WS_subscription_ack']=True
    def send_rpc(self,method,seq,params):
        if (method,seq) not in [('eth_subscribe',1),('eth_unsubscribe',2)]:raise Stop('WS_METHOD_ALLOWLIST')
        self.budget.charge(10)
        body={'jsonrpc':'2.0','id':seq,'method':method,'params':params}
        record={'UTC':utc(),'monotonic_ns':time.monotonic_ns(),'request':body,'send_started':True,'send_completed':False,'engineering_equivalent_CU':10,'dRPC_actual_CU':'UNKNOWN'}
        try:self.wire.send_frame(1,json.dumps(body,separators=(',',':')).encode('ascii'));record['send_completed']=True
        finally:self.evidence.save('ws-outbound',record)
    def receive(self,kind):
        before=self.wire.bytes
        try:data,arrived,mono=self.wire.receive_message()
        except codec.Stop as ex:raise Stop(ex.args[0]) from None
        wire_bytes=self.wire.bytes-before;cost=(wire_bytes+24)//25
        try:
            obj=codec.decode_json(data)
            if not isinstance(obj,dict) or 'error' in obj:raise Stop('WS_ERROR_OR_SCHEMA')
            if kind=='head':
                params=obj.get('params')
                if set(obj)!={'jsonrpc','method','params'} or obj.get('jsonrpc')!='2.0' or obj.get('method')!='eth_subscription' or not isinstance(params,dict) or set(params)!={'subscription','result'} or params.get('subscription')!=self.subscription:raise Stop('WS_NOTIFICATION_BINDING')
                codec.validate_head(params['result'])
            elif kind=='ack':
                if set(obj)!={'jsonrpc','id','result'} or obj.get('jsonrpc')!='2.0' or type(obj.get('id')) is not int or obj['id']!=1 or not isinstance(obj['result'],str) or not re.fullmatch(r'0x[0-9a-fA-F]{1,128}',obj['result']):raise Stop('WS_SUBSCRIBE_ACK_SCHEMA')
            elif kind=='unsubscribe':
                if set(obj)!={'jsonrpc','id','result'} or obj.get('jsonrpc')!='2.0' or type(obj.get('id')) is not int or obj['id']!=2 or obj['result'] is not True:raise Stop('WS_UNSUBSCRIBE_ACK_SCHEMA')
        except (Stop,codec.Stop):
            self.evidence.save('stream-error',{'UTC':arrived,'safe_category':'WS_ERROR_OR_SCHEMA','payload_bytes':len(data),'body_sha256':digest(data),'raw_body_saved':False})
            self.budget.delivered(cost,mono);raise Stop('WS_ERROR_OR_SCHEMA') from None
        record={'UTC':arrived,'monotonic_ns':int(mono*10**9),'body_utf8':data.decode('utf8'),'payload_bytes':len(data),'wire_bytes_including_interleaved_control':wire_bytes,'engineering_conservative_CU':cost,'dRPC_actual_CU':'UNKNOWN','application_read_not_wire_arrival':True,'kind':kind}
        self.evidence.save('stream-validated-before-accounting',record)
        self.budget.delivered(cost,mono)
        self.evidence.save('stream',dict(record,budget=self.budget.state()))
        if kind=='head':
            self.notification_payload_bytes.append(len(data));self.notification_wire_bytes.append(wire_bytes)
            self.state['dRPC_documented_notification_count']=len(self.notification_payload_bytes)
        self.state['WS_received_frames']=self.wire.frames;self.state['WS_received_bytes']=self.wire.bytes
        return obj
    def head(self):
        self.wire.deadline=min(self.wire.start+180,time.monotonic()+60);self.wire.read_timeout_cap=60
        obj=self.receive('head');h=obj['params']['result']
        h['_received_UTC']=utc();h['_received_monotonic_ns']=time.monotonic_ns()
        return h
    def backlog(self):return bool(self.wire.sock.pending() or select.select([self.wire.sock],[],[],0)[0])
    def unsubscribe(self):
        self.wire.deadline=min(self.wire.start+180,time.monotonic()+5);self.wire.read_timeout_cap=5
        self.send_rpc('eth_unsubscribe',2,[self.subscription]);self.receive('unsubscribe');self.state['WS_unsubscribe_ack']=True
    def close(self):
        if self.wire.sock:
            try:self.wire.sock.close()
            except Exception:pass

def main():
    start=time.monotonic();initial_CPU=time.process_time()
    cfg=json.loads((HERE/'config.json').read_text());limits=cfg['limits']
    state={'status':'PREFLIGHT_IN_PROGRESS','phase':'SOURCE_PREFLIGHT','PID':os.getpid(),'started':utc(),'A_observation_started':False,'ARMED':False,'requests_unit_cap':30,'provider':'dRPC anonymous public Ethereum','dRPC_actual_CU':'UNKNOWN','dRPC_anonymous_remaining_CU':'UNKNOWN','dRPC_documented_subscribe_CU':20,'dRPC_documented_notification_CU_each':20,'dRPC_unsubscribe_CU':'UNKNOWN','Alchemy_CU_retained':32734,'engineering_shadow_prior':32945,'project_methods_prior':71,'CPU_guard_prior':7365,'WS_connections':0,'completed_snapshots':[],'measurement_kind':'bounded transport and engineering preflight, not performance or profit'}
    evidence=rpc=stream=budget=None
    def alarm_handler(signum,frame):raise Stop('THIS_UNIT_WALL_180_STOP')
    signal.signal(signal.SIGALRM,alarm_handler);signal.alarm(180)
    resource.setrlimit(resource.RLIMIT_CPU,(15,15));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    try:
        with (HERE/'preflight.once').open('x') as f:f.write(json.dumps({'UTC':utc(),'PID':os.getpid(),'scope':'PRECHECK_ONLY_NO_ARM'}))
        for source in cfg['policy_sources']:
            if digest(pathlib.Path(source['path']).read_bytes())!=source['sha256']:raise Stop('FROZEN_POLICY_SOURCE_CHANGED')
        p=pathlib.Path(cfg['original_binding']['path']);raw=p.read_bytes()
        if digest(raw)!=cfg['original_binding']['sha256']:raise Stop('ORIGINAL_BINDING_CHANGED')
        binding=original.Bindings(p);c=binding.config
        for source in c['constants_sources']+[c['fee_policy']['engineering_defaults']]:
            if digest(pathlib.Path(source['path']).read_bytes())!=source['sha256']:raise Stop('ECONOMIC_SOURCE_CHANGED')
        c['effective_limits']={'new_disk_bytes_cumulative':8589934592,'disk_admission_reserve_bytes':1048576}
        state['frozen_source_identity_pass']=True
        state['anonymous_policy_admission']={'public_free_documented':True,'actual_balance':'UNKNOWN','not_numeric_quota_substitution':True,'real_service_refusal_stops':True,'free_backend_timeout_seconds':2,'rate_limit_normal_CU_per_min_per_IP':120000,'rate_limit_high_demand_floor_CU_per_min_per_IP':50400,'IP_shared_other_usage':'UNKNOWN','batch_limit':3,'logs_limit':10000}
        evidence=DataEvidence(HERE/'evidence',BASE,cap=8589934592)
        # Sanitize only independent metadata errors; original function and validation remain unchanged.
        raw_save=evidence.save
        def safe_save(kind,obj,endpoint=None):
            if kind=='independent-reference':state['independent_metadata_GET_attempts']=state.get('independent_metadata_GET_attempts',0)+1
            if kind=='independent-reference' and (obj.get('safe_error') or obj.get('HTTP')!=200):
                obj=dict(obj);body=obj.pop('body_utf8','').encode();obj['body_bytes']=len(body);obj['body_sha256']=digest(body);obj['raw_error_body_saved']=False;obj['safe_error']='PUBLIC_REFERENCE_FAILED'
            return raw_save(kind,obj,endpoint)
        evidence.save=safe_save
        budget=PreflightBudget(25000000,400000,peak=300,cpu=18000,ram=134217728,state={'cu':32945,'methods':71,'cpu':7365})
        endpoint=AnonymousEndpoint();route=DRPCRoute.from_system()
        state['route_config_child_CPU_seconds']=route.config_child_CPU_seconds
        rpc=DRPCRPC(endpoint,budget,evidence,c['rpc_CU'],max_body=1048576,route=route)
        state['phase']='CHAIN_AND_RUNTIME_IDENTITY'
        if rpc.call('eth_chainId',[])!='0x1':raise Stop('CHAIN_ID')
        h=rpc.call('eth_getBlockByNumber',['latest',False]);timeliness=original.timely(h,c['timeliness'])
        state['initial_B']=h['number'];state['initial_H']=h['hash'];state['runtime_checks']={}
        for role,target in binding.addresses.items():
            live=rpc.call('eth_getCode',[target,{'blockHash':h['hash'],'requireCanonical':True}])
            if rawhex(live)!=rawhex(binding.runtime[role]):raise Stop('RUNTIME_MISMATCH_'+role.upper())
            state['runtime_checks'][role]={'same_hash':h['hash'],'address':target,'runtime_bytes':len(rawhex(live)),'sha256':digest(rawhex(live)),'exact_bytes':True}
        rpc.close()
        state['phase']='INDEPENDENT_REFERENCE'
        reference=original.independent_preflight_reference(evidence,h)
        evidence.save('independent-reference-check',reference);state['independent_reference']=reference
        state['phase']='WS_AND_WAIT_SAMPLES'
        stream=PublicStream(route,budget,evidence,state,start)
        track=ChainTrack();wait_samples=[];state['wait_samples']=wait_samples
        # Unchanged original flow: three notification wait samples, third is initial scan head.
        for _ in range(3):
            bs=evidence.used();cs=time.process_time();probe=original.forward_head(stream,track,c['timeliness'],evidence)
            wait_samples.append({'disk':evidence.used()-bs,'cpu':time.process_time()-cs,'B':probe['number'],'hash':probe['hash']})
        now=dt.datetime.now(dt.timezone.utc);t0=dt.datetime.fromisoformat(cfg['T0'].replace('Z','+00:00'));t1=dt.datetime.fromisoformat(cfg['T1'].replace('Z','+00:00'))
        if now>=t0 or t1-t0!=dt.timedelta(days=14):raise Stop('ORIGINAL_OBSERVATION_WINDOW_UNAVAILABLE')
        lower=original.forecast(c,budget,0,0,0,stream.notification_wire_bytes,(t0-now).total_seconds())
        evidence.save('preflight-minimum-quota-bound',{'bound':lower,'actual_N_read':False,'not_scan_CPU_or_disk_validation':True,'engineering_equivalent_not_provider_balance':True})
        state['phase']='INITIAL_FULL_CENSUS'
        scanner=HashScanner(binding,rpc);original.timely(probe,c['timeliness']);processing=time.monotonic()
        snap=scanner.snapshot(probe,initial=True);evidence.save('preflight-snapshot',original.compact_snapshot(snap))
        original.timely(probe,c['timeliness'],time.monotonic()-processing,stream.backlog())
        state['completed_snapshots'].append({'kind':'initial','B':probe['number'],'hash':probe['hash'],'N':snap['count'],'P':snap['padding'],'ids_complete':True})
        measured=[];state['measured_cycles']=measured;state['phase']='THREE_MEASURED_FULL_CYCLES'
        for _ in range(3):
            bs=evidence.used();cs=time.process_time();old=budget.state();head=original.forward_head(stream,track,c['timeliness'],evidence);processing=time.monotonic()
            ss=scanner.snapshot(head);evidence.save('preflight-head',original.compact_snapshot(ss));elapsed=time.monotonic()-processing
            original.timely(head,c['timeliness'],elapsed,stream.backlog())
            item={'disk':evidence.used()-bs,'cpu':time.process_time()-cs,'processing_seconds':elapsed,'CU':budget.cu-old['cu'],'methods':budget.methods-old['methods'],'B':head['number'],'hash':head['hash']}
            measured.append(item);state['completed_snapshots'].append({'kind':'measured','B':head['number'],'hash':head['hash'],'N':ss['count'],'P':ss['padding'],'ids_complete':True})
        state['notification_wire_bytes']=list(stream.notification_wire_bytes)
        state['phase']='UNSUBSCRIBE'
        stream.unsubscribe();stream.close();stream=None
        now=dt.datetime.now(dt.timezone.utc)
        if now>=t0:raise Stop('ORIGINAL_T0_REACHED_DURING_PREFLIGHT')
        state['measured_cycles']=measured;state['wait_samples']=wait_samples
        state['phase']='RESOURCE_PROJECTION'
        try:
            estimate=original.forecast(c,budget,0,0,notification_bytes=[int(x) for x in state.get('notification_wire_bytes',[])],wait_seconds=(t0-now).total_seconds(),measured=measured,already_disk=evidence.used(),wait_disk=max(x['disk'] for x in wait_samples),wait_cpu=max(x['cpu'] for x in wait_samples))
        except Stop as ex:
            if ex.details is not None:state['resource_forecast']=ex.details
            raise
        state['resource_forecast']=estimate
        state['status']='PASS_BOUNDED_FULL_CENSUS_PREFLIGHT_ONLY_NOT_ARMED'
        state['phase']='DONE'
    except Stop as ex:
        state['status']='STOPPED_INCONCLUSIVE'
        state['safe_reason']=str(ex)
        if ex.details is not None:state['failure_details']=ex.details
    except codec.Stop as ex:state['status']='STOPPED_INCONCLUSIVE';state['safe_reason']=ex.args[0]
    except BaseException as ex:
        state['status']='STOPPED_INCONCLUSIVE';state['safe_reason']=core._DIAGNOSTIC_TYPES.get(type(ex),'OTHER')
    finally:
        if stream is not None:
            state['notification_wire_bytes']=list(stream.notification_wire_bytes)
            stream.close()
        if rpc is not None:rpc.close()
        signal.alarm(0)
        state['ended']=utc();state['whole_run_monotonic_seconds']=time.monotonic()-start
        state['process_CPU_seconds']=time.process_time();child=resource.getrusage(resource.RUSAGE_CHILDREN)
        state['children_CPU_seconds']=child.ru_utime+child.ru_stime
        state['self_peak_RSS_bytes_macos']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if budget is not None:state['engineering_budget']=budget.state()
        if 'resource_forecast' in state:
            f=state['resource_forecast']
            state['forecast_gate_flags']={'engineering_CU':f['CU_forecast']+f['already_CU']<=25000000,'methods':f['methods_forecast']+f['already_methods']<=400000,'disk_with_reserve':f['disk_including_already_and_wait_and_audit']<=8589934592-1048576,'CPU':f['CPU_including_prior_and_wait_and_audit']<=18000,'processing':max(x['processing_seconds'] for x in f['full_measured_cycles'])<12}
        if evidence is not None:
            state['physical_project_bytes']=evidence.used()
            try:evidence.save('terminal',state)
            except Stop:state['terminal_archive_save_failed']=True
        with (HERE/'result.json').open('x') as f:f.write(json.dumps(state,indent=2)+'\n')
    return 0 if state['status']=='PASS_BOUNDED_FULL_CENSUS_PREFLIGHT_ONLY_NOT_ARMED' else 1

if __name__=='__main__':raise SystemExit(main())

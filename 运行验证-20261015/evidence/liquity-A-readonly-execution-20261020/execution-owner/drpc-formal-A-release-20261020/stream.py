"""Frozen, accepted WS implementation plus explicit formal lifetime limits."""
from adapters import *
WIRE_PATH=OWNER/'drpc-one-public-newheads-20261020/probe.py'
if digest(WIRE_PATH.read_bytes())!='51a6f18a9808fd1f6bc4f2b52c6dac7b53f6b14437dd4e0f165e0d7f238714b9':raise Stop('FROZEN_WS_CODEC_CHANGED')
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
    def settle_received(self,before,kind,arrival):
        wire_bytes=self.wire.bytes-before;cost=(wire_bytes+24)//25
        self.state['WS_received_frames']=self.wire.frames;self.state['WS_received_bytes']=self.wire.bytes
        self.state['WS_frame_counter_scope']='Parser frame attempts; final partial frame may be incomplete. Byte counter includes known returned bytes and upgrade.'
        debit={'kind':kind,'known_received_wire_bytes':wire_bytes,'engineering_equivalent_CU':cost,'dRPC_actual_CU':'UNKNOWN','shadow_CU_before':self.budget.cu,'guard_predebit_fallback':False}
        self.state.setdefault('WS_receive_settlements',[]).append(debit)
        if not cost:
            debit['shadow_CU_after']=self.budget.cu
            return
        try:
            self.budget.delivered(cost,arrival)
        finally:
            # Fixed Budget checks resources before cu+=cost. Already-received bytes
            # remain owed even when that guard stops before the normal debit.
            if self.budget.cu==debit['shadow_CU_before']:
                self.budget.cu+=cost
                while self.budget.window and arrival-self.budget.window[0][0]>=10.0:self.budget.window.popleft()
                self.budget.window.append((arrival,cost));debit['guard_predebit_fallback']=True
            debit['shadow_CU_after']=self.budget.cu
    def receive(self,kind):
        before=self.wire.bytes;settlement_started=False;arrival=time.monotonic()
        try:
            try:data,arrived,arrival=self.wire.receive_message()
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
                raise Stop('WS_ERROR_OR_SCHEMA') from None
            record={'UTC':arrived,'monotonic_ns':int(arrival*10**9),'body_utf8':data.decode('utf8'),'payload_bytes':len(data),'wire_bytes_including_interleaved_control':wire_bytes,'engineering_conservative_CU':cost,'dRPC_actual_CU':'UNKNOWN','application_read_not_wire_arrival':True,'kind':kind}
            self.evidence.save('stream-validated-before-accounting',record)
            settlement_started=True
            self.settle_received(before,kind,arrival)
            self.evidence.save('stream',dict(record,budget=self.budget.state()))
            if kind=='head':
                self.notification_payload_bytes.append(len(data));self.notification_wire_bytes.append(wire_bytes)
                self.state['dRPC_documented_notification_count']=len(self.notification_payload_bytes)
            return obj
        finally:
            if not settlement_started:
                settlement_started=True
                self.settle_received(before,kind,time.monotonic())
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

def finalize_terminal(evidence,state):
    try:evidence.save('terminal',state)
    except Exception:
        state['terminal_archive_save_failed']=True
        if 'safe_reason' in state:state['failure_before_terminal_archive']=state['safe_reason']
        state['status']='STOPPED_INCONCLUSIVE';state['safe_reason']='TERMINAL_ARCHIVE_SAVE_FAILED'

class FormalWire(codec.Wire):
    """No preflight lifetime byte/frame/wall caps; bounded individual messages."""
    def __init__(self,state,start,budget):
        super().__init__(state,start);self.budget=budget
    def timeout(self):
        left=self.deadline-time.monotonic()
        if left<=0:raise Stop('WS_PHASE_DEADLINE_NO_RECONNECT')
        return min(self.read_timeout_cap,left)
    def read(self,n):
        if n>1048576:raise Stop('WS_SINGLE_READ_CAP')
        data=bytearray()
        while len(data)<n:
            self.budget.resource_check();self.sock.settimeout(self.timeout())
            part=self.sock.recv(min(65536,n-len(data)))
            if not part:raise Stop('WS_EOF_NO_RECONNECT')
            self.bytes+=len(part);data.extend(part)
        return bytes(data)
    def receive_message(self):
        message=bytearray();fragmented=False;message_frames=0;message_controls=0
        while True:
            self.frames+=1;message_frames+=1
            if message_frames>16:raise Stop('WS_PER_MESSAGE_FRAME_CAP')
            first,second=self.read(2);fin=bool(first&0x80);opcode=first&15
            if first&0x70 or second&0x80:raise Stop('WS_RSV_OR_SERVER_MASK_INVALID')
            n=second&127
            if n==126:
                n=struct.unpack('!H',self.read(2))[0]
                if n<126:raise Stop('WS_LENGTH_NONCANONICAL')
            elif n==127:
                n=struct.unpack('!Q',self.read(8))[0]
                if n<65536 or n>=2**63:raise Stop('WS_LENGTH_NONCANONICAL')
            if opcode in (8,9,10):
                self.controls+=1;message_controls+=1
                if message_controls>8 or not fin or n>125:raise Stop('WS_CONTROL_INVALID_OR_PER_MESSAGE_CAP')
                data=self.read(n)
                if opcode==8:raise Stop('WS_SERVER_CLOSE_NO_RECONNECT')
                if opcode==9:self.send_frame(10,data)
                continue
            if opcode==1:
                if fragmented:raise Stop('WS_FRAGMENT_SEQUENCE_INVALID')
            elif opcode==0:
                if not fragmented:raise Stop('WS_FRAGMENT_SEQUENCE_INVALID')
            else:raise Stop('WS_OPCODE_UNSUPPORTED')
            if len(message)+n>1048576:raise Stop('WS_MESSAGE_1MiB_CAP')
            message.extend(self.read(n))
            if fin:return bytes(message),utc(),time.monotonic()
            fragmented=True

class FormalStream(PublicStream):
    def __init__(self,route,budget,evidence,state,start):
        # Accepted handshake+ack uses its bounded 15s setup, not a 180s observer cap.
        super().__init__(route,budget,evidence,state,start)
        old=self.wire;wire=FormalWire({},old.start,budget)
        wire.sock=old.sock;wire.bytes=old.bytes;wire.frames=old.frames;wire.controls=old.controls
        self.wire=wire;self.total_notifications=0
    def head(self):
        self.wire.deadline=time.monotonic()+60;self.wire.read_timeout_cap=60
        obj=self.receive('head');head=obj['params']['result']
        head['_received_UTC']=utc();head['_received_monotonic_ns']=time.monotonic_ns()
        self.total_notifications+=1
        self.state['dRPC_documented_notification_count']=self.total_notifications
        self.notification_payload_bytes=self.notification_payload_bytes[-128:]
        self.notification_wire_bytes=self.notification_wire_bytes[-128:]
        return head
    def settle_received(self,before,kind,arrival):
        try:return super().settle_received(before,kind,arrival)
        finally:
            # Full message bodies/budget records remain archived; in-memory tail bounded.
            if 'WS_receive_settlements' in self.state:
                self.state['WS_receive_settlements']=self.state['WS_receive_settlements'][-16:]
    def unsubscribe(self):
        self.wire.deadline=time.monotonic()+5;self.wire.read_timeout_cap=5
        self.send_rpc('eth_unsubscribe',2,[self.subscription]);self.receive('unsubscribe')
        self.state['WS_unsubscribe_ack']=True

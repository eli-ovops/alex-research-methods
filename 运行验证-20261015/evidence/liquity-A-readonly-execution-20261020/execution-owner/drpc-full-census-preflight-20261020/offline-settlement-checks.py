"""Only MF1/MF2 fake-wire checks; no old suite, scutil, sockets or preflight main."""
import socket
def denied(*args,**kwargs):raise AssertionError('NETWORK_FORBIDDEN')
socket.create_connection=denied
import preflight as p

class FakeWire:
    def __init__(self,mode='success'):
        self.bytes=336;self.frames=1;self.mode=mode
    def receive_message(self):
        self.frames+=1
        if self.mode=='partial':
            self.bytes+=26
            raise p.codec.Stop('WS_EOF_NO_RECONNECT')
        if self.mode=='timeout':
            self.bytes+=26
            raise TimeoutError('SYNTHETIC_SECRET_NOT_OUTPUT')
        data=b'{"jsonrpc":"2.0","id":1,"result":"0x1234"}'
        self.bytes+=len(data)+2
        return data,p.utc(),p.time.monotonic()

class FakeEvidence:
    def __init__(self,fail=None):self.fail=fail;self.records=[]
    def save(self,kind,record):
        if kind==self.fail:raise p.Stop('SYNTHETIC_SAVE_FAILED')
        self.records.append(kind)

def make(mode='success',fail=None,budget=None):
    s=object.__new__(p.PublicStream)
    s.wire=FakeWire(mode);s.state={};s.evidence=FakeEvidence(fail)
    s.budget=budget or p.Budget(25000000,400000,peak=300,cpu=18000,state={'cu':0,'methods':0,'cpu':0})
    s.notification_payload_bytes=[];s.notification_wire_bytes=[]
    return s

def execute(s,expected_exception=None):
    try:s.receive('ack')
    except BaseException as e:
        assert expected_exception is not None and isinstance(e,expected_exception)
    else:assert expected_exception is None
    records=s.state['WS_receive_settlements']
    assert len(records)==1 and records[0]['shadow_CU_after']==s.budget.cu
    assert s.state['WS_received_bytes']==s.wire.bytes and s.state['WS_received_frames']==s.wire.frames
    expected=(s.wire.bytes-336+24)//25
    assert s.budget.cu==expected
    return records[0]

execute(make());print('PASS successful receive settles exactly once')
execute(make('partial'),p.Stop);print('PASS partial EOF settles received bytes')
execute(make('timeout'),TimeoutError);print('PASS partial timeout settles received bytes without exception text')
execute(make(fail='stream-validated-before-accounting'),p.Stop);print('PASS save-before-delivery failure settles once')
execute(make(fail='stream'),p.Stop);print('PASS save-after-delivery failure does not double debit')
b=p.Budget(25000000,400000,peak=300,cpu=18000,state={'cu':0,'methods':0,'cpu':0})
def early_guard():raise p.Stop('SYNTHETIC_RESOURCE_GUARD')
b.resource_check=early_guard
r=execute(make(budget=b),p.Stop);assert r['guard_predebit_fallback'] is True
print('PASS resource guard before debit records owed shadow and window')
b=p.Budget(1,400000,peak=300,cpu=18000,state={'cu':0,'methods':0,'cpu':0})
r=execute(make(budget=b),p.Stop);assert r['guard_predebit_fallback'] is False
print('PASS delivered post-debit cap exception does not debit twice')
state={'status':'PASS_BOUNDED_FULL_CENSUS_PREFLIGHT_ONLY_NOT_ARMED'}
p.finalize_terminal(FakeEvidence('terminal'),state)
assert state['status']=='STOPPED_INCONCLUSIVE' and state['safe_reason']=='TERMINAL_ARCHIVE_SAVE_FAILED'
state={'status':'STOPPED_INCONCLUSIVE','safe_reason':'ORIGINAL_FIXED_FAILURE'}
p.finalize_terminal(FakeEvidence('terminal'),state)
assert state['failure_before_terminal_archive']=='ORIGINAL_FIXED_FAILURE'
print('PASS terminal archive failure forbids PASS and preserves earlier fixed failure')
print('SYNTHETIC_ONLY 8 PASS; no network, system route, old suite or preflight entry')

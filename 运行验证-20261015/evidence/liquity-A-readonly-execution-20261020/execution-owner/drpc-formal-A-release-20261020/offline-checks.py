"""Formal wiring guards only; no client entry, route read, TLS/API or strategy run."""
import ast
import socket
import textwrap
from pathlib import Path
def denied(*args,**kwargs):raise AssertionError('NETWORK_FORBIDDEN')
socket.create_connection=denied
import adapters as a
import stream as s
import observer as o

class Fake:
    def __init__(self,data):self.data=data;self.sent=[]
    def recv(self,n):out,self.data=self.data[:n],self.data[n:];return out
    def settimeout(self,n):assert 0<n<=60
    def sendall(self,data):self.sent.append(data)
class Budget:
    def resource_check(self):pass

payload=(a.OWNER/'drpc-one-public-newheads-20261020/head-notification.body.bin').read_bytes()
frame=b'\x81\x7e'+len(payload).to_bytes(2,'big')+payload
w=s.FormalWire({},a.time.monotonic()-1000,Budget());w.deadline=a.time.monotonic()+60;w.read_timeout_cap=60;w.sock=Fake(frame*80)
assert w.timeout()>0
for _ in range(80):assert w.receive_message()[0]==payload
assert w.frames==80 and w.bytes>131072
print('PASS no global180s/16frame/128KiB preflight lifetime caps')

w=s.FormalWire({},a.time.monotonic(),Budget());w.deadline=a.time.monotonic()+60;w.sock=Fake(b'\x89\x00'*9)
try:w.receive_message()
except a.Stop as e:assert str(e)=='WS_CONTROL_INVALID_OR_PER_MESSAGE_CAP'
else:raise AssertionError('CONTROL_CAP_EXPECTED')
print('PASS per-message control cap remains fail-closed')

allowed={'eth_chainId','eth_getBlockByNumber','eth_call','eth_getCode','eth_getLogs','eth_getTransactionByHash','eth_getTransactionReceipt'}
constants=[x for x in a.DRPCRPC.call.__code__.co_consts if isinstance(x,frozenset)]
assert frozenset(allowed) in constants
assert not any(name.startswith(('eth_send','wallet','sign')) for name in allowed)
print('PASS seven read-only methods include logs transaction receipt')

saved=a.DRPCRPC.call
try:
    a.DRPCRPC.call=lambda self,method,params:[None]*10000
    rpc=object.__new__(a.FormalRPC);rpc._failed=False;rpc.close=lambda:None
    try:rpc.call('eth_getLogs',[])
    except a.Stop as e:assert str(e)=='PUBLIC_LOG_CAP_COMPLETENESS_UNKNOWN' and rpc._failed
    else:raise AssertionError('LOG_CAP_EXPECTED')
finally:a.DRPCRPC.call=saved
print('PASS public log cap stops with incomplete-coverage reason')

here=o.HERE;fixture=here/'offline-fixtures';fixture.mkdir(exist_ok=False)
(fixture/'binding.json').write_bytes((here/'binding.template.json').read_bytes())
o.HERE=fixture
try:
    try:o.verify_release()
    except a.Stop as e:assert str(e)=='FORMAL_BINDING_NOT_PUBLISHED'
    else:raise AssertionError('DRAFT_MUST_NOT_ACTIVATE')
finally:o.HERE=here
assert not (here/'binding.json').exists() and not (here/'formal-start.once').exists()
print('PASS pending template cannot publish or start')

class FailedEvidence:
    def save(self,*args,**kwargs):raise a.Stop('SYNTHETIC_SAVE_FAILURE')
state={'status':'WINDOW_ENDED_PENDING_INDEPENDENT_REVIEW'}
s.finalize_terminal(FailedEvidence(),state)
assert state['status']=='STOPPED_INCONCLUSIVE' and state['safe_reason']=='TERMINAL_ARCHIVE_SAVE_FAILED'
print('PASS formal terminal save failure cannot remain successful')

col=(a.OWNER/'readonly_collector.py').read_text();start=col.index('        tracker=ChainTrack();episodes=Episodes();');end=col.index('\n    except Stop as ex:state.update',start)
old=textwrap.dedent(col[start:end]).strip()
current=(here/'observer_loop.py').read_text();current=textwrap.dedent(current[current.index('    tracker='):]).strip()
current=current.replace("\n    continuity_event=continuity.accept(head)\n    if received<t0 and continuity_event=='REORG':evidence.save('warmup-reorg',{'UTC':utc(),'header':head,'not_formal_A_sample':True})",'')
current=current.replace("\n    if covered==1:\n        state['A_observation_started']=True;state['budget']=budget.state()\n        if on_first_complete is not None:on_first_complete()",'')
assert current==old
assert o.original.qualify is a.original.qualify and a.Episodes is a.core.Episodes
print('PASS original economics Episodes and audit loop preserved except explicit metadata/continuity')

budget=a.FormalBudget(25000000,400000,peak=300,cpu=18000,state={'cu':33850,'methods':100,'cpu':7440})
budget.charge(0);assert budget.methods==101
assert budget.cu==33850 and budget.cpu_prior==7440
print('PASS formal cumulative methods are not preflight30-capped or reset')
print('SYNTHETIC_ONLY 8 PASS; no route/network/main/economic execution')

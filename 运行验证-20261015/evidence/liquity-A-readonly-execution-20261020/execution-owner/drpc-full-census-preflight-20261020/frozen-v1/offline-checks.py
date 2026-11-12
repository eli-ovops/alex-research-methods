"""Affected wiring only; no preflight/main(), network or system config calls."""
import ast
import socket
from pathlib import Path
def denied(*args,**kwargs):raise AssertionError('NETWORK_FORBIDDEN')
socket.create_connection=denied
import adapters as a
import preflight as p

root=Path(__file__).resolve().parent
cfg=a.json.loads((root/'config.json').read_text())
binding=a.original.Bindings(cfg['original_binding']['path'])
assert set(binding.records)==set(a.original.FIXED)
print('PASS five ABI/runtime frozen bindings and selectors')

original_snapshot=a.original.Scanner.snapshot
assert a.HashScanner.snapshot.__code__.co_names.count('super')==1
assert a.original.Scanner.snapshot is original_snapshot
tree=ast.parse((root/'preflight.py').read_text())
assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='run_live' for n in ast.walk(tree))
assert cfg['T0']=='2026-10-21T00:00:00Z' and cfg['T1']=='2026-11-04T00:00:00Z'
print('PASS original snapshot/qualify/forecast retained and no live entry')

class FakeRPC:
 last_artifact={'synthetic':True}
 def call(self,method,params):
  self.method,self.params=method,params
  # ABI encoding (bool,bytes)[] containing one success with one uint256 word.
  return '0x'+(a.word(32)+a.word(1)+a.word(32)+a.word(1)+a.word(64)+a.word(32)+a.word(105)).hex()
rpc=FakeRPC();scanner=a.HashScanner(binding,rpc);h='0x'+'12'*32
assert scanner.aggregate([binding.method('tm','getTroveIdsCount')],h)==[(True,'0x'+a.word(105).hex())]
assert rpc.method=='eth_call' and rpc.params[1]=={'blockHash':h,'requireCanonical':True}
assert 'data' in rpc.params[0] and 'input' not in rpc.params[0]
assert rpc.params[0]['gas']==hex(30000000)
print('PASS hash object/data/from/gas aggregate wiring')

fixture=root/'offline-fixtures';fixture.mkdir(exist_ok=False)
ev=a.DataEvidence(fixture,fixture,cap=8589934592)
public=(a.OWNER/'drpc-one-public-newheads-20261020/head-notification.body.bin').read_bytes()
changed=public.replace(b'"jsonrpc":"2.0"',b'"jsonrpc":"2.1"')
assert changed!=public
req={'method':'eth_call','params':[{'data':'0x1234'}]}
one=ev.save('rpc',{'request':req,'body_utf8':public.decode()})
two=ev.save('rpc',{'request':req,'body_utf8':changed.decode()})
obj=a.json.loads(a.gzip.decompress(a.read_artifact_range(two)))
assert 'body_delta' in obj and obj['body_delta']['encoding']=='fixed64-byte-delta-v1'
assert a.reconstruct_rpc_body(two,fixture)==changed
ev.save('rpc',{'request':{'method':'eth_call','params':[{'data':'0x123456'}]},'body_utf8':public.decode()})
assert len(ev.delta_cache)==2
print('PASS data-key lossless delta roundtrip using synthetic variation of prior public bytes')

budget=a.PreflightBudget(25000000,400000,peak=300,cpu=18000,state={'cu':32945,'methods':101,'cpu':7365})
try:budget.charge(26)
except a.Stop as e:assert str(e)=='THIS_UNIT_30_METHOD_CAP'
else:raise AssertionError('EXPECTED_METHOD_STOP')
print('PASS diagnostic method cap keeps cumulative baseline')

assert p.original.qualify is a.original.qualify and p.original.forecast is a.original.forecast
print('PASS unchanged economic and resource function identity')
print('SYNTHETIC_ONLY 6 PASS; no route/TLS/API/WS or strategy execution')

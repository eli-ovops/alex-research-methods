"""Synthetic codec checks only; never run probe.run or system configuration."""
import importlib.util
from pathlib import Path
import socket
import time

def deny(*args, **kwargs):
    raise AssertionError('NETWORK_FORBIDDEN')
socket.create_connection = deny
spec = importlib.util.spec_from_file_location('isolated_probe', Path(__file__).with_name('probe.py'))
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)

class Fake:
    def __init__(self, data):
        self.data = data
        self.sent = []
    def settimeout(self, timeout):
        assert 0 < timeout <= 30
    def recv(self, n):
        out, self.data = self.data[:n], self.data[n:]
        return out
    def sendall(self, data):
        self.sent.append(data)

def wire(data):
    w = p.Wire({}, time.monotonic())
    w.sock = Fake(data)
    return w

def stopped(w, label):
    try:
        w.receive_message()
    except p.Stop as e:
        assert e.args == (label,)
    else:
        raise AssertionError('EXPECTED_STOP')

checks = []
w = wire(b'\x81\x02{}')
assert w.receive_message()[0] == b'{}'
checks.append('complete_text')
w = wire(b'\x01\x01{\x80\x01}')
assert w.receive_message()[0] == b'{}'
checks.append('bounded_fragment_reassembly')
w = wire(b'\x89\x01x\x81\x02{}')
assert w.receive_message()[0] == b'{}'
assert w.controls == 1 and w.sock.sent[0][0] == 0x8a and w.sock.sent[0][1] & 0x80
mask, payload = w.sock.sent[0][2:6], w.sock.sent[0][6:]
assert bytes(v ^ mask[i % 4] for i, v in enumerate(payload)) == b'x'
checks.append('ping_masked_pong')
stopped(wire(b'\x81\x82'), 'WS_RSV_OR_SERVER_MASK_INVALID')
checks.append('server_mask_rejected')
stopped(wire(b'\x81\x7e\x00\x02'), 'WS_LENGTH_NONCANONICAL')
checks.append('nonminimal_length_rejected')
stopped(wire(b'\x00\x00'), 'WS_FRAGMENT_SEQUENCE_INVALID')
checks.append('orphan_continuation_rejected')
stopped(wire(b'\x09\x00'), 'WS_CONTROL_INVALID_OR_CAP')
checks.append('fragmented_ping_rejected')
w = wire(b'\x8a\x00' * 9)
stopped(w, 'WS_CONTROL_INVALID_OR_CAP')
checks.append('control_count_cap')
w = wire(b'\x81\x00')
w.bytes = p.RECEIVE_CAP
stopped(w, 'RECEIVE_TOTAL_CAP')
checks.append('cumulative_receive_cap')
try:
    p.decode_json(b'{"error":"SYNTHETIC_NOT_A_SECRET","error":1}')
except p.Stop as e:
    assert e.args == ('JSON_DUPLICATE_KEY',)
else:
    raise AssertionError('EXPECTED_STOP')
checks.append('duplicate_json_key_rejected')
for label in checks:
    print('PASS ' + label)
print('SYNTHETIC_ONLY 10 PASS; no system route read or network')

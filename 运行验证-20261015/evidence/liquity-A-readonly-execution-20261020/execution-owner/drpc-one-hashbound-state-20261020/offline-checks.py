import importlib.util
from pathlib import Path
import socket

def deny(*args, **kwargs):
    raise AssertionError('NETWORK_FORBIDDEN')
socket.create_connection = deny
spec = importlib.util.spec_from_file_location('isolated_probe', Path(__file__).with_name('probe.py'))
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
assert p.notfound({'code': -32001, 'message': 'SYNTHETIC_ANY_TEXT'}) == 'RESOURCE_NOT_FOUND'
for value in ['header not found', 'header for hash not found', 'block not found', 'unknown block']:
    assert p.notfound({'code': -32000, 'message': value}) == 'EXPLICIT_NOT_FOUND_NONPREFERRED_CODE'
for code, value in [(-32602, 'header not found'), (-32000, 'Header not found'), (-32000, 'header not found '), (-32000, 'invalid argument'), (-32000, 'not found')]:
    assert p.notfound({'code': code, 'message': value}) is None
assert p.SOURCE.is_file()
assert p.hexbytes('0x' + '00' * 32, 32) == bytes(32)
print('PASS exact predeclared negative-control classification and source path; synthetic only; no network/system-route read')

"""One five-step anonymous hash-bound state diagnostic; no import-time I/O."""
import datetime
import hashlib
import http.client
import ipaddress
import json
from pathlib import Path
import re
import resource
import signal
import socket
import ssl
import subprocess
import time

BASE = Path(__file__).resolve().parent
SOURCE = BASE.parents[2] / 'liquity-official-deployment-binding-20261020/root/sourcify-record.body'
SOURCE_SHA = '002c37f8674d4fef6fb721a70d1ad26af02ee4a678aba0ae4bdd27222265f202'
TM = '0x7bcb64B2c9206a5B699eD43363f6F98D4776Cf5A'
SELECTOR = '0x4aff96e1'
RUNTIME_SHA = 'c46a82f256fb8daa445eeaad42bb0a27e498297b17c5da0d1f7eaaa328dcd371'
HOST = 'eth.drpc.org'
ZERO_HASH = '0x' + '00' * 32
TX = {'to': TM, 'from': '0x' + '00' * 20, 'gas': '0x186a0', 'data': SELECTOR}
CAP = 65536

class Stop(Exception):
    pass

def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def parse_json(raw):
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise Stop('JSON_DUPLICATE_KEY')
            out[key] = value
        return out
    try:
        return json.loads(raw.decode('utf8'), object_pairs_hook=pairs)
    except (ValueError, UnicodeError):
        raise Stop('JSON_INVALID') from None

def quantity(value):
    if not isinstance(value, str) or not re.fullmatch(r'0x(?:0|[1-9a-f][0-9a-f]*)', value):
        raise Stop('QUANTITY_INVALID')
    return int(value, 16)

def hexbytes(value, size=None):
    if not isinstance(value, str) or not re.fullmatch(r'0x(?:[0-9a-fA-F]{2})*', value):
        raise Stop('HEX_BYTES_INVALID')
    raw = bytes.fromhex(value[2:])
    if size is not None and len(raw) != size:
        raise Stop('HEX_BYTE_LENGTH_INVALID')
    return raw

def header(value):
    if not isinstance(value, dict):
        raise Stop('BLOCK_NULL_OR_SCHEMA')
    for key in ('number', 'timestamp', 'baseFeePerGas', 'gasLimit', 'gasUsed'):
        quantity(value.get(key))
    for key in ('hash', 'parentHash', 'stateRoot', 'transactionsRoot', 'receiptsRoot'):
        hexbytes(value.get(key), 32)
    hexbytes(value.get('logsBloom'), 256)
    if not isinstance(value.get('transactions'), list):
        raise Stop('BLOCK_TRANSACTIONS_SCHEMA')
    for txhash in value['transactions']:
        hexbytes(txhash, 32)
    if quantity(value['gasUsed']) > quantity(value['gasLimit']):
        raise Stop('BLOCK_GAS_INCONSISTENT')

def notfound(error):
    if not isinstance(error, dict) or type(error.get('code')) is not int:
        return None
    code = error['code']
    if code == -32001:
        return 'RESOURCE_NOT_FOUND'
    # Exact pre-run whitelist only; no normalization, wildcard or error-text output.
    if code == -32000 and error.get('message') in (
            'header not found', 'header for hash not found', 'block not found', 'unknown block'):
        return 'EXPLICIT_NOT_FOUND_NONPREFERRED_CODE'
    return None

class Transport:
    def __init__(self, state, started):
        self.state = state
        self.started = started
        self.sock = None
        self.response = None
    def timeout(self):
        left = 45 - (time.monotonic() - self.started)
        if left <= 0:
            raise Stop('WHOLE_RUN_DEADLINE')
        return min(5, left)
    def open(self):
        self.state['phase'] = 'SYSTEM_ROUTE'
        cfg = subprocess.run(['/usr/sbin/scutil', '--proxy'], stdin=subprocess.DEVNULL,
             capture_output=True, timeout=min(3, self.timeout()),
             env={'PATH': '/usr/bin:/bin:/usr/sbin:/sbin', 'LANG': 'en_US.UTF-8'})
        if cfg.returncode != 0 or len(cfg.stdout) > 65536:
            raise Stop('SYSTEM_ROUTE_READ_FAILED')
        values = {}
        for line in cfg.stdout.decode('utf8', 'replace').splitlines():
            m = re.fullmatch(r'\s*(HTTPSEnable|HTTPSProxy|HTTPSPort|ProxyAutoConfigEnable)\s*:\s*(.*?)\s*', line)
            if m:
                if m[1] in values:
                    raise Stop('SYSTEM_ROUTE_DUPLICATE_FIELD')
                values[m[1]] = m[2]
        if values.get('HTTPSEnable') != '1' or values.get('ProxyAutoConfigEnable') not in (None, '0'):
            raise Stop('SYSTEM_ROUTE_DISABLED_OR_PAC')
        try:
            ip = ipaddress.ip_address(values.get('HTTPSProxy', '').strip('[]'))
        except ValueError:
            raise Stop('SYSTEM_ROUTE_LITERAL_REQUIRED') from None
        port = values.get('HTTPSPort', '')
        if not ip.is_loopback or not re.fullmatch(r'[0-9]{1,5}', port) or not 1 <= int(port) <= 65535:
            raise Stop('SYSTEM_ROUTE_LOOPBACK_PORT_REQUIRED')
        self.state['phase'] = 'TCP'
        self.sock = socket.create_connection((str(ip), int(port)), timeout=self.timeout())
        self.state['phase'] = 'CONNECT'
        self.sock.settimeout(self.timeout())
        self.sock.sendall(b'CONNECT eth.drpc.org:443 HTTP/1.1\r\nHost: eth.drpc.org:443\r\n\r\n')
        raw = bytearray()
        while not raw.endswith(b'\r\n\r\n'):
            if len(raw) >= 8192:
                raise Stop('CONNECT_HEADER_CAP')
            self.sock.settimeout(self.timeout())
            part = self.sock.recv(1)
            if not part:
                raise Stop('CONNECT_EOF')
            raw.extend(part)
        m = re.fullmatch(rb'HTTP/1\.[01] ([0-9]{3})(?: [^\r\n]*)?', bytes(raw).split(b'\r\n', 1)[0])
        if not m:
            raise Stop('CONNECT_STATUS_INVALID')
        self.state['connect_status'] = int(m[1])
        if int(m[1]) != 200:
            raise Stop('CONNECT_NON200_NO_AUTH')
        del raw, cfg, values, ip, port
        self.state['phase'] = 'TLS_HANDSHAKE'
        context = ssl.create_default_context()
        if not context.check_hostname or context.verify_mode != ssl.CERT_REQUIRED:
            raise Stop('STRICT_TLS_REQUIRED')
        self.sock.settimeout(self.timeout())
        self.sock = context.wrap_socket(self.sock, server_hostname=HOST)
        self.state['strict_tls'] = True
        version = self.sock.version()
        self.state['tls_version'] = version if version in ('TLSv1.2', 'TLSv1.3') else 'OTHER'
    def request(self, seq, method, params, negative=False):
        if method not in ('eth_getBlockByNumber', 'eth_call', 'eth_getCode') or not 1 <= seq <= 5:
            raise Stop('METHOD_ALLOWLIST')
        rec = {'id': seq, 'method': method, 'started_utc': utc(),
               'started_elapsed_seconds': time.monotonic() - self.started,
               'send_started': False, 'send_completed': False, 'http_status': None,
               'negative_control': negative}
        rec['params'] = params
        self.state['requests'].append(rec)
        self.state['phase'] = 'RPC_SEND'
        cost = {'eth_getBlockByNumber': 20, 'eth_call': 26, 'eth_getCode': 20}[method]
        if self.state['engineering_equivalent_shadow_CU'] + cost > 25000000:
            raise Stop('ENGINEERING_SHADOW_CU_CAP')
        self.state['engineering_equivalent_shadow_CU'] += cost
        rec['engineering_equivalent_CU_debit'] = cost
        self.state['method_attempts'] += 1
        self.state['shared_method_attempts_total'] = 66 + self.state['method_attempts']
        body = json.dumps({'jsonrpc': '2.0', 'id': seq, 'method': method, 'params': params}, separators=(',', ':')).encode('ascii')
        packet = (b'POST / HTTP/1.1\r\nHost: eth.drpc.org\r\nContent-Type: application/json\r\nConnection: keep-alive\r\nContent-Length: '
                  + str(len(body)).encode('ascii') + b'\r\n\r\n' + body)
        self.sock.settimeout(self.timeout())
        rec['send_started'] = True
        self.sock.sendall(packet)
        rec['send_completed'] = True
        self.state['phase'] = 'HTTP_HEADERS'
        self.sock.settimeout(self.timeout())
        self.response = http.client.HTTPResponse(self.sock)
        self.response.begin()
        rec['http_status'] = self.response.status
        self.state['phase'] = 'HTTP_BODY'
        data = bytearray()
        while True:
            timeout = self.timeout()
            if self.response.isclosed():
                break
            self.sock.settimeout(timeout)
            part = self.response.read(min(4096, CAP + 1 - len(data)))
            data.extend(part)
            if len(data) > CAP:
                raise Stop('RESPONSE_BODY_CAP')
            if not part:
                break
        rec['body_bytes'] = len(data)
        rec['body_sha256'] = hashlib.sha256(data).hexdigest()
        rec['ended_utc'] = utc()
        rec['ended_elapsed_seconds'] = time.monotonic() - self.started
        if self.response.length not in (None, 0):
            raise Stop('HTTP_BODY_TRUNCATED')
        if self.response.status != 200:
            raise Stop('HTTP_NON200_NO_REDIRECT')
        obj = parse_json(data)
        if not isinstance(obj, dict) or obj.get('jsonrpc') != '2.0' or type(obj.get('id')) is not int or obj['id'] != seq:
            raise Stop('JSONRPC_ID_OR_SCHEMA')
        if 'error' in obj:
            error = obj['error']
            if isinstance(error, dict) and type(error.get('code')) is int:
                rec['error_code'] = error['code']
            rec['body_saved'] = False
            if negative and set(obj) == {'jsonrpc', 'id', 'error'} and notfound(error):
                rec['safe_error_class'] = notfound(error)
                self.state['negative_control_pass'] = True
                return None, None
            rec['safe_error_class'] = 'UNCLASSIFIED_JSONRPC_ERROR'
            raise Stop('RPC_ERROR_NOT_EXPECTED_NOTFOUND')
        if set(obj) != {'jsonrpc', 'id', 'result'} or obj['result'] is None:
            raise Stop('RPC_NULL_OR_SCHEMA')
        if negative:
            raise Stop('NEGATIVE_CONTROL_RETURNED_RESULT')
        return obj['result'], bytes(data)
    def save(self, seq, data):
        (BASE / ('%02d-success.body.bin' % seq)).write_bytes(data)
        self.state['requests'][-1]['body_saved'] = True
    def next_step(self):
        if self.response is not None and self.response.will_close:
            raise Stop('SERVER_CONNECTION_CLOSED_NO_RECONNECT')
        if self.response is not None:
            self.response.close()
            self.response = None
    def close(self):
        for obj in (self.response, self.sock):
            if obj is not None:
                try:
                    obj.close()
                except BaseException:
                    pass

def run():
    started = time.monotonic()
    state = {'status': 'STOPPED_INCONCLUSIVE', 'started_utc': utc(), 'phase': 'ONCE',
             'requests': [], 'method_attempts': 0, 'shared_method_attempts_total': 66,
             'prior_Alchemy_CU_retained': 32734, 'dRPC_actual_CU': 'UNKNOWN',
             'engineering_equivalent_shadow_CU': 32833,
             'engineering_shadow_cap': 25000000,
             'engineering_shadow_is_provider_bill': False,
             'negative_control_pass': False, 'runtime_exact_match': False,
             'fence_same_hash': False, 'strict_tls': False, 'retry_count': 0,
             'target_TM': TM, 'selector': SELECTOR, 'gas': TX['gas'],
             'from_zero': True, 'state_override': False}
    transport = Transport(state, started)
    def alarm_handler(signum, frame):
        raise Stop('WHOLE_PROCESS_DEADLINE')
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(45)
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    try:
        with (BASE / 'probe.once').open('x') as f:
            f.write(state['started_utc'] + '\n')
        state['phase'] = 'SOURCE_PREFLIGHT'
        raw = SOURCE.read_bytes()
        if hashlib.sha256(raw).hexdigest() != SOURCE_SHA:
            raise Stop('SOURCE_IDENTITY_MISMATCH')
        source = parse_json(raw)
        if source.get('address', '').lower() != TM.lower() or str(source.get('chainId')) != '1':
            raise Stop('SOURCE_CHAIN_ADDRESS_MISMATCH')
        abi = [a for a in source['abi'] if a.get('name') == 'getTroveIdsCount']
        if len(abi) != 1 or abi[0].get('inputs') != [] or abi[0].get('stateMutability') != 'view' or [a.get('type') for a in abi[0].get('outputs', [])] != ['uint256']:
            raise Stop('SOURCE_ABI_MISMATCH')
        if not any(s.get('signature') == 'getTroveIdsCount()' and s.get('signatureHash4') == SELECTOR for s in source['signatures']['function']):
            raise Stop('SOURCE_SELECTOR_MISMATCH')
        expected = hexbytes(source['runtimeBytecode']['onchainBytecode'])
        if hashlib.sha256(expected).hexdigest() != RUNTIME_SHA:
            raise Stop('SOURCE_RUNTIME_MISMATCH')
        state['source_identity_pass'] = True
        transport.open()
        value, data = transport.request(1, 'eth_getBlockByNumber', ['latest', False])
        header(value)
        B, H = value['number'], value['hash']
        if H.lower() == ZERO_HASH:
            raise Stop('POSITIVE_HASH_ZERO')
        state['B'], state['H'], state['block_timestamp'] = B, H, value['timestamp']
        transport.save(1, data)
        transport.next_step()
        block = {'blockHash': H, 'requireCanonical': True}
        value, data = transport.request(2, 'eth_call', [TX, block])
        count = hexbytes(value, 32)
        state['count_uint256_decimal'] = str(int.from_bytes(count, 'big'))
        transport.save(2, data)
        transport.next_step()
        transport.request(3, 'eth_call', [TX, {'blockHash': ZERO_HASH, 'requireCanonical': True}], negative=True)
        transport.next_step()
        value, data = transport.request(4, 'eth_getCode', [TM, block])
        actual = hexbytes(value)
        state['runtime_actual_bytes'] = len(actual)
        state['runtime_actual_sha256'] = hashlib.sha256(actual).hexdigest()
        if actual != expected:
            raise Stop('RUNTIME_BYTE_MISMATCH')
        state['runtime_exact_match'] = True
        transport.save(4, data)
        transport.next_step()
        value, data = transport.request(5, 'eth_getBlockByNumber', [B, False])
        header(value)
        if value['number'] != B or value['hash'].lower() != H.lower():
            raise Stop('FENCE_BLOCK_IDENTITY_MISMATCH')
        state['fence_same_hash'] = True
        transport.save(5, data)
        state['phase'] = 'DONE'
        state['status'] = 'PASS_ONE_HASH_BOUND_COUNT_RUNTIME_AND_FENCE'
    except Stop as exc:
        state['safe_reason'] = exc.args[0]
    except BaseException as exc:
        types = {TimeoutError: 'TimeoutError', ssl.SSLError: 'SSLError', ssl.SSLEOFError: 'SSLEOFError',
                 ssl.SSLCertVerificationError: 'SSLCertVerificationError', OSError: 'OSError',
                 ConnectionError: 'ConnectionError', FileExistsError: 'FileExistsError',
                 http.client.HTTPException: 'HTTPException', subprocess.TimeoutExpired: 'SubprocessTimeout'}
        state['safe_reason'] = types.get(type(exc), 'OTHER')
        number = getattr(exc, 'errno', None)
        if type(number) is int:
            state['errno'] = number
    finally:
        transport.close()
        signal.alarm(0)
        own = resource.getrusage(resource.RUSAGE_SELF)
        child = resource.getrusage(resource.RUSAGE_CHILDREN)
        state['ended_utc'] = utc()
        state['whole_run_monotonic_seconds'] = time.monotonic() - started
        state['process_CPU_seconds'] = own.ru_utime + own.ru_stime
        state['children_CPU_seconds'] = child.ru_utime + child.ru_stime
        state['self_peak_RSS_bytes_macos'] = own.ru_maxrss
        state['connection_closed_locally'] = True
        with (BASE / 'result.json').open('x') as f:
            json.dump(state, f, sort_keys=True, indent=2)
            f.write('\n')
    return 0 if state['status'] == 'PASS_ONE_HASH_BOUND_COUNT_RUNTIME_AND_FENCE' else 1

if __name__ == '__main__':
    raise SystemExit(run())

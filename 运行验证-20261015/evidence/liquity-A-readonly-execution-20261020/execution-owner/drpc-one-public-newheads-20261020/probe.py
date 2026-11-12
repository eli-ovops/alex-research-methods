"""One keyless newHeads subscription; no network at import."""
import base64
import datetime
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import resource
import signal
import socket
import ssl
import struct
import subprocess
import time

BASE = Path(__file__).resolve().parent
HOST = 'eth.drpc.org'
GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
MESSAGE_CAP = 65536
RECEIVE_CAP = 131072

class Stop(Exception):
    pass

def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def decode_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise Stop('JSON_DUPLICATE_KEY')
            result[key] = value
        return result
    try:
        return json.loads(data.decode('utf8'), object_pairs_hook=pairs)
    except (ValueError, UnicodeError):
        raise Stop('JSON_INVALID') from None

def quantity(value):
    if not isinstance(value, str) or not re.fullmatch(r'0x(?:0|[1-9a-f][0-9a-f]*)', value):
        raise Stop('HEADER_QUANTITY_INVALID')
    return int(value, 16)

def fixed_hex(value, size):
    if not isinstance(value, str) or not re.fullmatch('0x[0-9a-fA-F]{' + str(size * 2) + '}', value):
        raise Stop('HEADER_FIXED_HEX_INVALID')

def validate_head(head):
    if not isinstance(head, dict):
        raise Stop('HEADER_OBJECT_REQUIRED')
    hashes = ('hash', 'parentHash', 'sha3Uncles', 'stateRoot', 'transactionsRoot', 'receiptsRoot', 'mixHash')
    nums = ('number', 'timestamp', 'difficulty', 'gasLimit', 'gasUsed', 'baseFeePerGas')
    optional_hashes = ('withdrawalsRoot', 'parentBeaconBlockRoot', 'requestsHash')
    optional_nums = ('blobGasUsed', 'excessBlobGas', 'totalDifficulty', 'size')
    allowed = set(hashes + nums + optional_hashes + optional_nums + ('nonce', 'logsBloom', 'miner', 'extraData'))
    if not set(head) <= allowed:
        raise Stop('HEADER_UNKNOWN_FIELD')
    for key in hashes:
        fixed_hex(head.get(key), 32)
    for key in nums:
        quantity(head.get(key))
    for key in optional_hashes:
        if key in head:
            fixed_hex(head[key], 32)
    for key in optional_nums:
        if key in head:
            quantity(head[key])
    fixed_hex(head.get('nonce'), 8)
    fixed_hex(head.get('logsBloom'), 256)
    fixed_hex(head.get('miner'), 20)
    extra = head.get('extraData')
    if not isinstance(extra, str) or not re.fullmatch(r'0x(?:[0-9a-fA-F]{2}){0,32}', extra):
        raise Stop('HEADER_EXTRA_DATA_INVALID')
    if quantity(head['gasUsed']) > quantity(head['gasLimit']):
        raise Stop('HEADER_GAS_INCONSISTENT')

class Wire:
    def __init__(self, state, start):
        self.state = state
        self.start = start
        self.deadline = start + 15
        self.read_timeout_cap = 5
        self.sock = None
        self.frames = 0
        self.controls = 0
        self.bytes = 0
    def timeout(self):
        left = min(self.start + 45, self.deadline) - time.monotonic()
        if left <= 0:
            raise Stop('PHASE_DEADLINE')
        return min(self.read_timeout_cap, left)
    def read(self, n):
        if self.bytes + n > RECEIVE_CAP:
            raise Stop('RECEIVE_TOTAL_CAP')
        data = bytearray()
        while len(data) < n:
            self.sock.settimeout(self.timeout())
            part = self.sock.recv(n - len(data))
            if not part:
                raise Stop('WS_EOF_NO_RECONNECT')
            self.bytes += len(part)
            data.extend(part)
        return bytes(data)
    def send_frame(self, opcode, data):
        if opcode in (8, 9, 10) and len(data) > 125:
            raise Stop('CLIENT_CONTROL_CAP')
        mask = os.urandom(4)
        n = len(data)
        if n < 126:
            header = bytes((0x80 | opcode, 0x80 | n))
        elif n <= 65535:
            header = bytes((0x80 | opcode, 0xfe)) + struct.pack('!H', n)
        else:
            raise Stop('CLIENT_MESSAGE_CAP')
        self.sock.settimeout(self.timeout())
        self.sock.sendall(header + mask + bytes(v ^ mask[i % 4] for i, v in enumerate(data)))
    def send_rpc(self, obj, method):
        self.state['rpc_method_attempts'] += 1
        self.state['shared_method_attempts_total'] = 64 + self.state['rpc_method_attempts']
        self.state[method + '_send_started'] = True
        self.send_frame(1, json.dumps(obj, separators=(',', ':')).encode('ascii'))
        self.state[method + '_send_completed'] = True
    def receive_message(self):
        message = bytearray()
        fragmented = False
        while True:
            self.frames += 1
            if self.frames > 16:
                raise Stop('WS_FRAME_COUNT_CAP')
            first, second = self.read(2)
            fin = bool(first & 0x80)
            opcode = first & 15
            if first & 0x70 or second & 0x80:
                raise Stop('WS_RSV_OR_SERVER_MASK_INVALID')
            n = second & 127
            if n == 126:
                n = struct.unpack('!H', self.read(2))[0]
                if n < 126:
                    raise Stop('WS_LENGTH_NONCANONICAL')
            elif n == 127:
                n = struct.unpack('!Q', self.read(8))[0]
                if n < 65536 or n >= 2**63:
                    raise Stop('WS_LENGTH_NONCANONICAL')
            if opcode in (8, 9, 10):
                self.controls += 1
                if self.controls > 8 or not fin or n > 125:
                    raise Stop('WS_CONTROL_INVALID_OR_CAP')
                data = self.read(n)
                if opcode == 8:
                    raise Stop('WS_SERVER_CLOSE')
                if opcode == 9:
                    self.send_frame(10, data)
                continue
            if opcode == 1:
                if fragmented:
                    raise Stop('WS_FRAGMENT_SEQUENCE_INVALID')
            elif opcode == 0:
                if not fragmented:
                    raise Stop('WS_FRAGMENT_SEQUENCE_INVALID')
            else:
                raise Stop('WS_OPCODE_UNSUPPORTED')
            if len(message) + n > MESSAGE_CAP:
                raise Stop('WS_MESSAGE_CAP')
            message.extend(self.read(n))
            if fin:
                return bytes(message), utc(), time.monotonic()
            fragmented = True

def run():
    started = time.monotonic()
    result = {'started_utc': utc(), 'status': 'STOPPED_INCONCLUSIVE', 'phase': 'ONCE',
              'rpc_method_attempts': 0, 'shared_method_attempts_total': 64,
              'prior_Alchemy_CU_retained': 32734, 'dRPC_actual_CU': 'UNKNOWN',
              'dRPC_anonymous_monthly_quota': 'UNKNOWN', 'documented_subscribe_CU': 20,
              'documented_notification_CU': 20, 'documented_unsubscribe_CU': 'UNKNOWN',
              'subscription_ack_valid': False, 'head_received_valid': False,
              'unsubscribe_ack_valid': False, 'retry_count': 0,
              'strict_tls': False, 'proxy_private_values_saved': False,
              'application_receive_time_not_wire_time': True}
    wire = Wire(result, started)
    raw = None
    def alarm_handler(signum, frame):
        raise Stop('WHOLE_PROCESS_DEADLINE')
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(45)
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    try:
        with (BASE / 'probe.once').open('x') as f:
            f.write(result['started_utc'] + '\n')
        result['phase'] = 'SYSTEM_ROUTE'
        cfg = subprocess.run(['/usr/sbin/scutil', '--proxy'], stdin=subprocess.DEVNULL,
                capture_output=True, timeout=min(3, wire.timeout()),
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
        result['phase'] = 'TCP'
        raw = socket.create_connection((str(ip), int(port)), timeout=wire.timeout())
        raw.settimeout(wire.timeout())
        result['phase'] = 'CONNECT'
        raw.sendall(b'CONNECT eth.drpc.org:443 HTTP/1.1\r\nHost: eth.drpc.org:443\r\n\r\n')
        header = bytearray()
        while not header.endswith(b'\r\n\r\n'):
            if len(header) >= 8192:
                raise Stop('CONNECT_HEADER_CAP')
            raw.settimeout(wire.timeout())
            part = raw.recv(1)
            if not part:
                raise Stop('CONNECT_EOF')
            header.extend(part)
        m = re.fullmatch(rb'HTTP/1\.[01] ([0-9]{3})(?: [^\r\n]*)?', bytes(header).split(b'\r\n', 1)[0])
        if not m:
            raise Stop('CONNECT_STATUS_INVALID')
        result['connect_status'] = int(m[1])
        if int(m[1]) != 200:
            raise Stop('CONNECT_NON200_NO_AUTH')
        del cfg, values, ip, port, header
        result['phase'] = 'TLS_HANDSHAKE'
        context = ssl.create_default_context()
        if not context.check_hostname or context.verify_mode != ssl.CERT_REQUIRED:
            raise Stop('STRICT_TLS_REQUIRED')
        raw.settimeout(wire.timeout())
        wire.sock = context.wrap_socket(raw, server_hostname=HOST)
        raw = None
        result['strict_tls'] = True
        version = wire.sock.version()
        result['tls_version'] = version if version in ('TLSv1.2', 'TLSv1.3') else 'OTHER'
        result['phase'] = 'WS_UPGRADE'
        key = base64.b64encode(os.urandom(16)).decode('ascii')
        request = ('GET / HTTP/1.1\r\nHost: eth.drpc.org\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: '
                   + key + '\r\nSec-WebSocket-Version: 13\r\n\r\n').encode('ascii')
        wire.sock.settimeout(wire.timeout())
        wire.sock.sendall(request)
        header = bytearray()
        while not header.endswith(b'\r\n\r\n'):
            if len(header) >= 8192:
                raise Stop('UPGRADE_HEADER_CAP')
            header.extend(wire.read(1))
        try:
            lines = bytes(header).decode('ascii').split('\r\n')
        except UnicodeError:
            raise Stop('UPGRADE_HEADER_INVALID') from None
        match = re.fullmatch(r'HTTP/1\.1 ([0-9]{3})(?: [^\r\n]*)?', lines[0])
        if not match:
            raise Stop('UPGRADE_STATUS_INVALID')
        result['http_upgrade_status'] = int(match[1])
        result['upgrade_header_bytes'] = len(header)
        headers = {}
        for line in lines[1:-2]:
            if ':' not in line:
                raise Stop('UPGRADE_HEADER_INVALID')
            name, value = line.split(':', 1)
            name = name.lower()
            if not re.fullmatch(r'[a-z0-9!#$%&\x27*+.^_`|~-]+', name) or name in headers:
                raise Stop('UPGRADE_DUPLICATE_OR_INVALID_HEADER')
            headers[name] = value.strip()
        if int(match[1]) != 101:
            result['refusal_header_sha256'] = hashlib.sha256(header).hexdigest()
            result['refusal_body_read'] = False
            result['refusal_body_sha256'] = 'UNKNOWN_NOT_READ'
            raise Stop('UPGRADE_NON101_NO_REDIRECT')
        accept = base64.b64encode(hashlib.sha1((key + GUID).encode('ascii')).digest()).decode('ascii')
        connection_tokens = [x.strip().lower() for x in headers.get('connection', '').split(',')]
        if headers.get('upgrade', '').lower() != 'websocket' or 'upgrade' not in connection_tokens or headers.get('sec-websocket-accept') != accept:
            raise Stop('UPGRADE_ACCEPT_INVALID')
        if 'sec-websocket-extensions' in headers or 'sec-websocket-protocol' in headers:
            raise Stop('UPGRADE_UNREQUESTED_EXTENSION_OR_PROTOCOL')
        del headers, header, lines
        result['phase'] = 'SUBSCRIBE_SEND'
        result['subscribe_send_utc'] = utc()
        wire.send_rpc({'jsonrpc': '2.0', 'id': 1, 'method': 'eth_subscribe', 'params': ['newHeads']}, 'subscribe')
        wait_start = time.monotonic()
        wire.deadline = min(started + 45, wait_start + 30)
        wire.read_timeout_cap = 30
        result['phase'] = 'SUBSCRIBE_ACK'
        data, arrived, mono = wire.receive_message()
        obj = decode_json(data)
        if not isinstance(obj, dict) or set(obj) != {'jsonrpc', 'id', 'result'} or obj.get('jsonrpc') != '2.0' or type(obj.get('id')) is not int or obj['id'] != 1:
            raise Stop('SUBSCRIBE_ERROR_OR_SCHEMA')
        sub = obj['result']
        if not isinstance(sub, str) or not re.fullmatch(r'0x[0-9a-fA-F]{1,128}', sub):
            raise Stop('SUBSCRIPTION_ID_INVALID')
        (BASE / 'subscribe-ack.body.bin').write_bytes(data)
        result['subscription_ack_valid'] = True
        result['subscription_ack_utc'] = arrived
        result['subscription_ack_elapsed_seconds'] = mono - started
        result['phase'] = 'FIRST_HEAD'
        data, arrived, mono = wire.receive_message()
        obj = decode_json(data)
        if not isinstance(obj, dict) or set(obj) != {'jsonrpc', 'method', 'params'} or obj.get('jsonrpc') != '2.0' or obj.get('method') != 'eth_subscription':
            raise Stop('NOTIFICATION_ERROR_OR_SCHEMA')
        params = obj['params']
        if not isinstance(params, dict) or set(params) != {'subscription', 'result'} or params.get('subscription') != sub:
            raise Stop('NOTIFICATION_SUBSCRIPTION_MISMATCH')
        head = params['result']
        validate_head(head)
        received_epoch = datetime.datetime.fromisoformat(arrived).timestamp()
        age = received_epoch - quantity(head['timestamp'])
        (BASE / 'head-notification.body.bin').write_bytes(data)
        result['head_received_valid'] = True
        result['head_receive_utc'] = arrived
        result['head_receive_elapsed_seconds'] = mono - started
        result['head_number'] = head['number']
        result['head_hash'] = head['hash']
        result['head_parent_hash'] = head['parentHash']
        result['head_timestamp'] = head['timestamp']
        result['local_head_age_seconds'] = age
        result['local_age_check_pass'] = -2 <= age <= 30
        result['notification_payload_bytes'] = len(data)
        result['head_wait_elapsed_seconds'] = mono - wait_start
        result['status'] = 'ONE_VALID_HEAD_RECEIVED'
        if not result['local_age_check_pass']:
            result['status'] = 'VALID_HEAD_LOCAL_FRESHNESS_FAILED'
        result['phase'] = 'UNSUBSCRIBE_OPTION'
        if started + 45 - time.monotonic() >= 2:
            wire.deadline = min(started + 45, time.monotonic() + 5)
            wire.read_timeout_cap = 5
            result['phase'] = 'UNSUBSCRIBE_SEND'
            wire.send_rpc({'jsonrpc': '2.0', 'id': 2, 'method': 'eth_unsubscribe', 'params': [sub]}, 'unsubscribe')
            result['phase'] = 'UNSUBSCRIBE_ACK'
            data, arrived, mono = wire.receive_message()
            obj = decode_json(data)
            if not isinstance(obj, dict) or set(obj) != {'jsonrpc', 'id', 'result'} or obj.get('jsonrpc') != '2.0' or type(obj.get('id')) is not int or obj['id'] != 2 or obj.get('result') is not True:
                raise Stop('UNSUBSCRIBE_ERROR_OR_SCHEMA')
            (BASE / 'unsubscribe-ack.body.bin').write_bytes(data)
            result['unsubscribe_ack_valid'] = True
            result['unsubscribe_ack_utc'] = arrived
        else:
            result['unsubscribe_skipped_insufficient_time'] = True
        result['phase'] = 'DONE'
    except Stop as exc:
        result['safe_reason'] = exc.args[0]
    except BaseException as exc:
        types = {TimeoutError: 'TimeoutError', ssl.SSLError: 'SSLError', ssl.SSLEOFError: 'SSLEOFError',
                 ssl.SSLCertVerificationError: 'SSLCertVerificationError', OSError: 'OSError',
                 ConnectionError: 'ConnectionError', subprocess.TimeoutExpired: 'SubprocessTimeout', FileExistsError: 'FileExistsError'}
        result['safe_reason'] = types.get(type(exc), 'OTHER')
        errno = getattr(exc, 'errno', None)
        if type(errno) is int:
            result['errno'] = errno
    finally:
        for sock in (wire.sock, raw):
            if sock is not None:
                try:
                    sock.close()
                except BaseException:
                    pass
        signal.alarm(0)
        own = resource.getrusage(resource.RUSAGE_SELF)
        child = resource.getrusage(resource.RUSAGE_CHILDREN)
        result['ended_utc'] = utc()
        result['whole_run_monotonic_seconds'] = time.monotonic() - started
        result['received_wire_bytes_including_upgrade'] = wire.bytes
        result['received_frames'] = wire.frames
        result['received_control_frames'] = wire.controls
        result['process_CPU_seconds'] = own.ru_utime + own.ru_stime
        result['children_CPU_seconds'] = child.ru_utime + child.ru_stime
        result['self_peak_RSS_bytes_macos'] = own.ru_maxrss
        result['memory_limit'] = '128MiB_TARGET_OUTER_SAMPLED_MONITOR_NOT_ABSOLUTE_HARD_RSS'
        result['connection_closed_locally'] = True
        with (BASE / 'result.json').open('x') as f:
            json.dump(result, f, sort_keys=True, indent=2)
            f.write('\n')
    return 0 if result['head_received_valid'] and result.get('local_age_check_pass') else 1

if __name__ == '__main__':
    raise SystemExit(run())

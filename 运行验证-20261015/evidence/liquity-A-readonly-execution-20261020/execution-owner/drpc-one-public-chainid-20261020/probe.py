"""One anonymous public chain-id POST; definitions do not initiate network."""
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
HOST = 'eth.drpc.org'
BODY = b'{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}'
CAP = 65536

class Stop(Exception):
    pass

def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def run():
    started = time.monotonic()
    result = {'started_utc': utc(), 'status': 'STOPPED', 'phase': 'ONCE',
              'rpc_attempted': False, 'send_started': False, 'send_completed': False,
              'http_status': None, 'http_response_bytes': 0,
              'proxy_connect_status': None, 'strict_tls': False,
              'prior_Alchemy_CU_retained': 32734, 'prior_rpc_methods_retained': 63,
              'dRPC_CU': 'UNKNOWN', 'new_rpc_method_attempts': 0,
              'route_private_values_saved': False, 'retry_count': 0}
    raw = tls = response = None
    def alarm_handler(signum, frame):
        raise Stop('WHOLE_PROCESS_DEADLINE')
    def remaining():
        left = 15 - (time.monotonic() - started)
        if left <= 0:
            raise Stop('REQUEST_DEADLINE')
        return min(5, left)
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(20)
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    try:
        with (BASE / 'probe.once').open('x') as f:
            f.write(result['started_utc'] + '\n')
        result['phase'] = 'SYSTEM_ROUTE'
        cfg = subprocess.run(['/usr/sbin/scutil', '--proxy'], stdin=subprocess.DEVNULL,
              capture_output=True, timeout=min(3, remaining()),
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
            raise Stop('SYSTEM_ROUTE_IP_LITERAL_REQUIRED') from None
        port_text = values.get('HTTPSPort', '')
        if not ip.is_loopback or not re.fullmatch(r'[0-9]{1,5}', port_text) or not 1 <= int(port_text) <= 65535:
            raise Stop('SYSTEM_ROUTE_LOOPBACK_PORT_REQUIRED')
        result['phase'] = 'TCP'
        raw = socket.create_connection((str(ip), int(port_text)), timeout=remaining())
        result['phase'] = 'CONNECT_SEND'
        raw.settimeout(remaining())
        raw.sendall(b'CONNECT eth.drpc.org:443 HTTP/1.1\r\nHost: eth.drpc.org:443\r\n\r\n')
        result['phase'] = 'CONNECT_RESPONSE'
        header = bytearray()
        while not header.endswith(b'\r\n\r\n'):
            if len(header) >= 8192:
                raise Stop('CONNECT_HEADER_CAP')
            raw.settimeout(remaining())
            part = raw.recv(1)
            if not part:
                raise Stop('CONNECT_EOF')
            header.extend(part)
        m = re.fullmatch(rb'HTTP/1\.[01] ([0-9]{3})(?: [^\r\n]*)?', bytes(header).split(b'\r\n', 1)[0])
        if not m:
            raise Stop('CONNECT_STATUS_INVALID')
        result['proxy_connect_status'] = int(m[1])
        if int(m[1]) != 200:
            raise Stop('CONNECT_NON200_NO_AUTH')
        del header, cfg, values, ip, port_text
        result['phase'] = 'TLS_HANDSHAKE'
        ctx = ssl.create_default_context()
        if not ctx.check_hostname or ctx.verify_mode != ssl.CERT_REQUIRED:
            raise Stop('STRICT_TLS_REQUIRED')
        raw.settimeout(remaining())
        tls = ctx.wrap_socket(raw, server_hostname=HOST)
        raw = None
        result['strict_tls'] = True
        result['tls_version'] = tls.version() if tls.version() in ('TLSv1.2', 'TLSv1.3') else 'OTHER'
        result['phase'] = 'RPC_SEND'
        result['rpc_attempted'] = True
        result['new_rpc_method_attempts'] = 1
        result['shared_rpc_method_attempts_total'] = 64
        request = (b'POST / HTTP/1.1\r\nHost: eth.drpc.org\r\nContent-Type: application/json\r\nConnection: close\r\nContent-Length: '
                   + str(len(BODY)).encode('ascii') + b'\r\n\r\n' + BODY)
        tls.settimeout(remaining())
        result['send_started'] = True
        tls.sendall(request)
        result['send_completed'] = True
        result['phase'] = 'HTTP_HEADERS'
        tls.settimeout(remaining())
        response = http.client.HTTPResponse(tls)
        response.begin()
        result['http_status'] = response.status
        result['phase'] = 'HTTP_BODY'
        data = bytearray()
        while True:
            timeout = remaining()
            if response.isclosed():
                break
            tls.settimeout(timeout)
            part = response.read(min(4096, CAP + 1 - len(data)))
            data.extend(part)
            if len(data) > CAP:
                raise Stop('RESPONSE_BODY_CAP')
            if not part:
                break
        result['http_response_bytes'] = len(data)
        result['http_body_sha256'] = hashlib.sha256(data).hexdigest()
        if response.length not in (None, 0):
            raise Stop('HTTP_BODY_TRUNCATED')
        if response.status != 200:
            raise Stop('HTTP_NON200_NO_REDIRECT')
        result['phase'] = 'JSON_VALIDATION'
        try:
            obj = json.loads(data)
        except (ValueError, UnicodeError):
            raise Stop('JSON_INVALID') from None
        if not isinstance(obj, dict) or set(obj) != {'jsonrpc', 'id', 'result'} or obj.get('jsonrpc') != '2.0' or type(obj.get('id')) is not int or obj['id'] != 1:
            raise Stop('JSONRPC_ERROR_OR_SCHEMA')
        value = obj['result']
        if not isinstance(value, str) or not re.fullmatch(r'0x(?:0|[1-9a-f][0-9a-f]*)', value) or value != '0x1':
            raise Stop('CHAIN_ID_MISMATCH_OR_NONCANONICAL')
        (BASE / 'response.body.bin').write_bytes(data)
        result['jsonrpc_response'] = obj
        result['status'] = 'SUCCESS_ETHEREUM_CHAIN_ID_ONLY'
        result['phase'] = 'DONE'
    except Stop as exc:
        result['safe_reason'] = exc.args[0]
    except BaseException as exc:
        allowed = (TimeoutError, ssl.SSLError, ConnectionError, OSError,
                   http.client.HTTPException, subprocess.TimeoutExpired, FileExistsError)
        names = {TimeoutError: 'TimeoutError', ssl.SSLError: 'SSLError',
                 ConnectionError: 'ConnectionError', OSError: 'OSError',
                 http.client.HTTPException: 'HTTPException', subprocess.TimeoutExpired: 'SubprocessTimeout',
                 FileExistsError: 'FileExistsError'}
        result['safe_reason'] = next((names[c] for c in allowed if isinstance(exc, c)), 'OTHER')
        err = getattr(exc, 'errno', None)
        if type(err) is int:
            result['errno'] = err
    finally:
        for item in (response, tls, raw):
            if item is not None:
                try:
                    item.close()
                except BaseException:
                    pass
        signal.alarm(0)
        result['ended_utc'] = utc()
        result['monotonic_wall_seconds'] = time.monotonic() - started
        own = resource.getrusage(resource.RUSAGE_SELF)
        child = resource.getrusage(resource.RUSAGE_CHILDREN)
        result['process_cpu_seconds'] = own.ru_utime + own.ru_stime
        result['children_cpu_seconds'] = child.ru_utime + child.ru_stime
        result['self_peak_rss_bytes_macos'] = own.ru_maxrss
        result['memory_limit'] = '128MiB_TARGET_OUTER_MONITOR_REQUIRED_NOT_HARD_RLIMIT_AS'
        with (BASE / 'result.json').open('x') as f:
            json.dump(result, f, sort_keys=True, indent=2)
            f.write('\n')
    return 0 if result['status'] == 'SUCCESS_ETHEREUM_CHAIN_ID_ONLY' else 1

if __name__ == '__main__':
    raise SystemExit(run())

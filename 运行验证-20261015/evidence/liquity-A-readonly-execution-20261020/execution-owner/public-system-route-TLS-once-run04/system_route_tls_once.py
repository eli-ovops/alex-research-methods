"""Unexecuted until Root releases: one existing loopback HTTP CONNECT + strict TLS only."""
import socket,ssl,signal,time,datetime,pathlib,json,os,subprocess,re,ipaddress
TARGET='eth-mainnet.g.alchemy.com'
class Deadline(Exception):pass
class SafeStop(Exception):pass
def alarm(signum,frame):raise Deadline()
labels={Deadline:'WALL_DEADLINE',socket.gaierror:'gaierror',socket.herror:'herror',TimeoutError:'TimeoutError',ConnectionRefusedError:'ConnectionRefusedError',ConnectionResetError:'ConnectionResetError',ConnectionAbortedError:'ConnectionAbortedError',BrokenPipeError:'BrokenPipeError',OSError:'OSError',ssl.SSLError:'SSLError',ssl.SSLEOFError:'SSLEOFError',ssl.SSLZeroReturnError:'SSLZeroReturnError',ssl.SSLCertVerificationError:'SSLCertVerificationError',subprocess.TimeoutExpired:'CONFIG_READ_TIMEOUT'}
started=time.monotonic();cpu=time.process_time();phase='CONFIG';raw=None;tls=None
record={'status':'STOPPED','UTC_start':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phase':phase,'CONNECT_attempts':0,'target_HTTP_API_RPC_requests':0,'HTTP_CONNECT_status':None,'safe_error':None,'errno':None,'TLSversion':None,'strict_verify':False}
try:
    guard=pathlib.Path(__file__).with_name('once-started.lock')
    fd=os.open(guard,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.write(fd,b'ONE_SYSTEM_ROUTE_PUBLIC_TLS_ATTEMPT_NO_RETRY\n');os.close(fd)
    signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,10)
    cfg=subprocess.run(['/usr/sbin/scutil','--proxy'],env={'PATH':'/usr/bin:/bin:/usr/sbin:/sbin','LANG':'en_US.UTF-8'},capture_output=True,timeout=3)
    if cfg.returncode!=0:raise SafeStop('CONFIG_READ_FAILED')
    values={}
    for line in cfg.stdout.decode('utf8','replace').splitlines():
        m=re.fullmatch(r'\s*(HTTPSEnable|HTTPSProxy|HTTPSPort|ProxyAutoConfigEnable)\s*:\s*(.*?)\s*',line)
        if m:values[m[1]]=m[2]
    if values.get('HTTPSEnable')!='1' or values.get('ProxyAutoConfigEnable') not in (None,'0'):raise SafeStop('CONFIG_NOT_ENABLED_OR_PAC')
    proxy=values.get('HTTPSProxy','');port=values.get('HTTPSPort','')
    # Strict IP literal only: names including localhost fail closed, no DNS fallback.
    try:loopback=ipaddress.ip_address(proxy.strip('[]')).is_loopback
    except ValueError:loopback=False
    if not loopback or not re.fullmatch(r'[0-9]+',port) or not 1<=int(port)<=65535:raise SafeStop('CONFIG_NOT_LOOPBACK_OR_PORT')
    context=ssl.create_default_context()
    if not context.check_hostname or context.verify_mode!=ssl.CERT_REQUIRED:raise SafeStop('STRICT_VERIFY_UNAVAILABLE')
    record['strict_verify']=True;phase='CONNECT_TCP'
    raw=socket.create_connection((proxy.strip('[]'),int(port)),timeout=5)
    phase='CONNECT_RESPONSE';record['CONNECT_attempts']=1
    raw.sendall(b'CONNECT eth-mainnet.g.alchemy.com:443 HTTP/1.1\r\nHost: eth-mainnet.g.alchemy.com:443\r\n\r\n')
    head=bytearray()
    while not head.endswith(b'\r\n\r\n'):
        if len(head)>=8192:raise SafeStop('CONNECT_HEADER_CAP')
        part=raw.recv(1)
        if not part:raise SafeStop('CONNECT_EOF')
        head.extend(part)
    first=bytes(head).split(b'\r\n',1)[0];m=re.fullmatch(rb'HTTP/1\.[01] ([0-9]{3})(?: [^\r\n]*)?',first)
    if not m:raise SafeStop('CONNECT_STATUS_INVALID')
    status=int(m[1]);record['HTTP_CONNECT_status']=status
    if status!=200:raise SafeStop('CONNECT_NON200_STOP_NO_AUTH')
    phase='TLS';tls=context.wrap_socket(raw,server_hostname=TARGET);raw=None
    version=tls.version();record['TLSversion']=version if version in {'TLSv1.2','TLSv1.3'} else 'OTHER'
    record['status']='ONE_SYSTEM_ROUTE_TLS_SUCCEEDED_NOT_A_PREFLIGHT_PASS'
except SafeStop as ex:
    # Only locally hardcoded SafeStop literals above, never provider/error text.
    record['safe_error']=ex.args[0]
except BaseException as ex:
    kind=type(ex);record['safe_error']=labels.get(kind,'OTHER')
    if kind in labels:
        n=getattr(ex,'errno',None);record['errno']=n if type(n)is int else None
finally:
    signal.setitimer(signal.ITIMER_REAL,0)
    for obj in [tls,raw]:
        if obj is not None:
            try:obj.close()
            except BaseException:pass
    record.update(phase=phase,UTC_end=datetime.datetime.now(datetime.timezone.utc).isoformat(),wall_seconds=time.monotonic()-started,process_CPU_seconds=time.process_time()-cpu)
    print(json.dumps(record,sort_keys=True))

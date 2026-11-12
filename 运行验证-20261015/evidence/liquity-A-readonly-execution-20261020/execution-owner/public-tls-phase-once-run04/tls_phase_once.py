"""One public TLS handshake only. No HTTP/API path, account, credential or retry."""
import socket,ssl,signal,time,datetime,pathlib,json,os,resource
HOST='eth-mainnet.g.alchemy.com'
class Deadline(Exception):pass
def alarm(signum,frame):raise Deadline()
labels={Deadline:'WALL_DEADLINE',socket.gaierror:'gaierror',socket.herror:'herror',TimeoutError:'TimeoutError',ConnectionRefusedError:'ConnectionRefusedError',ConnectionResetError:'ConnectionResetError',ConnectionAbortedError:'ConnectionAbortedError',BrokenPipeError:'BrokenPipeError',OSError:'OSError',ssl.SSLError:'SSLError',ssl.SSLEOFError:'SSLEOFError',ssl.SSLZeroReturnError:'SSLZeroReturnError',ssl.SSLCertVerificationError:'SSLCertVerificationError'}
started=time.monotonic();cpu=time.process_time();phase='TCP';raw=None;tls=None
record={'status':'STOPPED','UTC_start':datetime.datetime.now(datetime.timezone.utc).isoformat(),'network_attempts':0,'HTTP_or_RPC_requests':0,'phase':'TCP','exception_type':None,'errno':None,'TLSversion':None}
try:
    # Exclusive local guard prevents accidental execution twice.
    guard=pathlib.Path(__file__).with_name('once-started.lock')
    fd=os.open(guard,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.write(fd,b'ONE_PUBLIC_TLS_HANDSHAKE_STARTED_NO_RETRY\n');os.close(fd)
    signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,10)
    context=ssl.create_default_context()
    if not context.check_hostname or context.verify_mode!=ssl.CERT_REQUIRED:raise RuntimeError()
    record['network_attempts']=1
    raw=socket.create_connection((HOST,443),timeout=5)
    phase='TLS';tls=context.wrap_socket(raw,server_hostname=HOST);raw=None
    version=tls.version();record['TLSversion']=version if version in {'TLSv1.2','TLSv1.3'} else 'OTHER'
    record['status']='ONE_TLS_HANDSHAKE_SUCCEEDED_NOT_A_PREFLIGHT_PASS'
except BaseException as ex:
    kind=type(ex);record['exception_type']=labels.get(kind,'OTHER')
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

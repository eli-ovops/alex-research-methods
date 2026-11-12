"""A-only safety/ABI/evidence primitives. No wallet or transaction submission."""
import warnings, select, email.utils, http.client, subprocess, ipaddress
import base64, collections, datetime as dt, getpass, gzip, hashlib, json, os, pathlib, re, resource, socket, ssl, struct, sys, time, urllib.request, urllib.error, urllib.parse

class Stop(RuntimeError):
    """Safe, constant diagnostic only; never embed an endpoint or provider text."""
    def __init__(self,code,details=None):
        super().__init__(code);self.details=details

ALLOWED = {'eth_chainId','eth_getBlockByNumber','eth_getBlockByHash','eth_getCode','eth_call','eth_getLogs','eth_getTransactionByHash','eth_getTransactionReceipt','eth_subscribe','eth_unsubscribe'}
HOST = 'eth-mainnet.g.alchemy.com'

def utc(): return dt.datetime.now(dt.timezone.utc).isoformat()
def digest(b): return hashlib.sha256(b).hexdigest()
def quantity(x):
    if not isinstance(x,str) or not re.fullmatch(r'0x(?:0|[1-9a-fA-F][0-9a-fA-F]*)',x): raise Stop('NONCANONICAL_QUANTITY')
    return int(x,16)
def word(n):
    if type(n)!=int or not 0<=n<2**256: raise Stop('UINT256_RANGE')
    return n.to_bytes(32,'big')
def rawhex(x):
    if not isinstance(x,str) or not re.fullmatch(r'0x(?:[0-9a-fA-F]{2})*',x): raise Stop('ABI_HEX')
    return bytes.fromhex(x[2:])
def uints(x,n):
    b=rawhex(x)
    if len(b)!=32*n:raise Stop('ABI_FIXED_LENGTH')
    return tuple(int.from_bytes(b[i:i+32],'big') for i in range(0,len(b),32))
def address(x):
    n=uints(x,1)[0]
    if n>=2**160:raise Stop('ABI_ADDRESS_HIGH_BITS')
    return '0x'+n.to_bytes(20,'big').hex()
def call_data(selector,*args):
    if not re.fullmatch('0x[0-9a-fA-F]{8}',selector):raise Stop('ABI_SELECTOR')
    return selector+''.join(word(a).hex() for a in args)

def aggregate3(selector,calls):
    # ABI (address,bool,bytes)[]; offset base of dynamic elements is after length.
    parts=[]
    for target,data in calls:
        if not re.fullmatch('0x[0-9a-fA-F]{40}',target):raise Stop('ABI_TARGET')
        b=rawhex(data);parts.append(word(int(target,16))+word(1)+word(96)+word(len(b))+b+b'\0'*((-len(b))%32))
    offset=32*len(parts);heads=[]
    for part in parts:heads.append(word(offset));offset+=len(part)
    return selector+(word(32)+word(len(parts))+b''.join(heads)+b''.join(parts)).hex()

def decode_aggregate3(encoded,expected):
    b=rawhex(encoded)
    def u(i):
        if i<0 or i+32>len(b) or i%32:raise Stop('ABI_DYNAMIC_BOUNDS')
        return int.from_bytes(b[i:i+32],'big')
    if u(0)!=32 or u(32)!=expected:raise Stop('ABI_AGGREGATE_COUNT')
    base=64;out=[];ranges=[]
    for k in range(expected):
        start=base+u(base+32*k)
        if start<base+32*expected:raise Stop('ABI_DYNAMIC_OVERLAP')
        success=u(start);offs=u(start+32)
        if success not in (0,1) or offs!=64:raise Stop('ABI_AGGREGATE_SCHEMA')
        n=u(start+offs);begin=start+offs+32;end=begin+n
        if end>len(b):raise Stop('ABI_DYNAMIC_BOUNDS')
        padded=end+((-n)%32)
        if padded>len(b) or any(b[end:padded]):raise Stop('ABI_NONZERO_PADDING')
        if any(start<r[1] and padded>r[0] for r in ranges):raise Stop('ABI_DYNAMIC_OVERLAP')
        ranges.append((start,padded));out.append((bool(success),'0x'+b[begin:end].hex()))
    return out

class SecretEndpoint:
    def __init__(self,url):
        p=urllib.parse.urlsplit(url)
        if p.scheme!='https' or p.hostname!=HOST or p.netloc!=HOST or p.query or p.fragment or p.username or p.password or not re.fullmatch(r'/v2/[A-Za-z0-9_-]+',p.path):raise Stop('ENDPOINT_NOT_ALLOWED')
        self._url=url;self._path=p.path
    def __repr__(self):return '<AlchemyEndpoint REDACTED>'
    def safe(self):return 'https://'+HOST+'/v2/[REDACTED]'
    def redact(self,b):
        return b.replace(self._url.encode(),self.safe().encode()).replace(self._path.encode(),b'/v2/[REDACTED]').replace(self._path[4:].encode(),b'[REDACTED]')

def prompt_endpoint():
    if not sys.stdin.isatty():raise Stop('SECRET_REQUIRES_LOCAL_TTY')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error',getpass.GetPassWarning)
            value=getpass.getpass('Alchemy HTTPS RPC URL (hidden, memory only): ')
    except getpass.GetPassWarning:raise Stop('SECRET_NOECHO_UNAVAILABLE') from None
    return SecretEndpoint(value)

class Evidence:
    def __init__(self,path,unit_root,cap=2*1024**3):
        self.path=pathlib.Path(path);self.path.mkdir(parents=True,exist_ok=True);self.root=pathlib.Path(unit_root);self.cap=min(cap,8*1024**3);self.seq=0;self.delta_cache={};self.archive_prefix=str(time.time_ns());self.archive_index=0;self.archive=None;self.known_used=0;self.last_inventory=0
    def used(self):
        if not self.last_inventory or time.monotonic()-self.last_inventory>60:
            total=0
            for p in self.root.rglob('*'):
                if p.is_file() and not p.is_symlink():
                    st=p.stat();total+=max(st.st_size,getattr(st,'st_blocks',0)*512)
            self.known_used=total;self.last_inventory=time.monotonic()
        return self.known_used
    def save(self,kind,obj,endpoint=None):
        obj=dict(obj);cache_key=None;body=None;depth=0
        if kind=='rpc' and isinstance(obj.get('body_utf8'),str) and obj.get('request',{}).get('method')=='eth_call':
            request=obj['request'];cache_key=(request['method'],len(request.get('params',[{}])[0].get('input','')))
            body=obj['body_utf8'].encode();prior=self.delta_cache.get(cache_key)
            if prior and prior[2]<63:
                previous,artifact,old_depth=prior;depth=old_depth+1;changes=[]
                for off in range(0,len(body),64):
                    chunk=body[off:off+64]
                    if chunk!=previous[off:off+64]:changes.append([off,base64.b64encode(chunk).decode()])
                delta={'encoding':'fixed64-byte-delta-v1','base_artifact':artifact,'length_bytes':len(body),'sha256_reconstructed_body':digest(body),'changed_chunks':changes}
                if len(json.dumps(delta))<len(body):obj.pop('body_utf8');obj['body_delta']=delta
                else:depth=0
        data=json.dumps(obj,ensure_ascii=False,separators=(',',':')).encode()
        if endpoint:data=endpoint.redact(data)
        self.seq+=1;packed=gzip.compress(data,mtime=0)
        if self.used()+len(packed)+1048576>self.cap:raise Stop('DISK_BUDGET')
        if self.archive is None or self.archive.stat().st_size+len(packed)>1048576:
            self.archive_index+=1;self.archive=self.path/(self.archive_prefix+'-records-'+str(self.archive_index)+'.json.gz')
            with self.archive.open('xb'):pass
        dest=self.archive;before=dest.stat();offset=before.st_size
        with dest.open('ab') as f:f.write(packed)
        after=dest.stat();self.known_used+=max(after.st_size,getattr(after,'st_blocks',0)*512)-max(before.st_size,getattr(before,'st_blocks',0)*512)
        artifact={'path':str(dest),'offset':offset,'bytes':len(packed),'sha256':digest(packed),'encoding':'one gzip member, immutable byte range; archive appends later members'}
        if cache_key is not None:
            if len(self.delta_cache)>=8 and cache_key not in self.delta_cache:self.delta_cache.pop(next(iter(self.delta_cache)))
            self.delta_cache[cache_key]=(body,artifact,depth)
        return artifact

class Budget:
    # Local conservative 10-second rolling ledger; not provider token bucket or shared account balance.
    def __init__(self,cu_limit=25_000_000,method_limit=400_000,peak=100,cpu=7200,ram=1024**3,state=None):
        self.cu_limit=min(cu_limit,25_000_000);self.method_limit=min(method_limit,400_000);self.peak=min(peak,300);self.cpu_limit=min(cpu,18000);self.ram_limit=min(ram,1024**3)
        self.cu=(state or {}).get('cu',0);self.methods=(state or {}).get('methods',0);self.cpu_prior=(state or {}).get('cpu',0);self.started_cpu=time.process_time();self.window=collections.deque()
    def resource_check(self):
        cpu=self.cpu_prior+time.process_time()-self.started_cpu
        if cpu>=self.cpu_limit:raise Stop('CPU_BUDGET')
        rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024)
        if rss>=self.ram_limit:raise Stop('RAM_BUDGET')
    def charge(self,cost,count=1):
        if type(cost)!=int or cost<0 or type(count)!=int or count<0:raise Stop('BILLING_UNKNOWN')
        self.resource_check()
        if self.cu+cost>self.cu_limit or self.methods+count>self.method_limit:raise Stop('CU_OR_METHOD_BUDGET')
        if cost>self.peak*10:raise Stop('PEAK_SINGLE_REQUEST')
        while True:
            now=time.monotonic()
            while self.window and now-self.window[0][0]>=10.0:self.window.popleft()
            if sum(x[1] for x in self.window)+cost<=self.peak*10:break
            time.sleep(max(.01,10.0-(now-self.window[0][0])))
        self.window.append((time.monotonic(),cost));self.cu+=cost;self.methods+=count
    def delivered(self,cost,arrival):
        # Already-delivered notifications cannot be delayed retroactively to fake compliance.
        self.resource_check();self.cu+=cost
        while self.window and arrival-self.window[0][0]>=10.0:self.window.popleft()
        self.window.append((arrival,cost))
        if self.cu>self.cu_limit:raise Stop('ACTUAL_DELIVERY_CU_CAP_EXCEEDED_STOP')
        if sum(x[1] for x in self.window)>self.peak*10:raise Stop('ACTUAL_DELIVERY_PEAK_EXCEEDED_STOP')
    def state(self):return {'cu':self.cu,'methods':self.methods,'cpu':self.cpu_prior+time.process_time()-self.started_cpu}

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*a,**k):return None

def safe_headers(headers):
    # Only normalized nonreflective values, never arbitrary provider header text.
    out={}
    value=headers.get('Date')
    try:
        parsed=email.utils.parsedate_to_datetime(value)
        out['Date']=parsed.astimezone(dt.timezone.utc).isoformat()
    except (ValueError,TypeError,IndexError,AttributeError):pass
    c=headers.get('Content-Type','').split(';',1)[0].strip().lower()
    if c in {'application/json','text/plain','text/html'}:out['Content-Type']=c
    return out

def validate_rpc_result(method,value):
    # Structural metadata only; detailed ABI/identity checks remain in Scanner.
    if method in {'eth_chainId','eth_getCode','eth_call'}:
        if method=='eth_chainId':quantity(value)
        else:rawhex(value)
    elif method in {'eth_getBlockByNumber','eth_getBlockByHash'}:
        validate_header(value)
    elif method=='eth_getLogs':
        if not isinstance(value,list):raise Stop('RPC_RESULT_SCHEMA')
        for item in value:validate_log(item)
    elif method in {'eth_getTransactionByHash','eth_getTransactionReceipt'}:
        if not isinstance(value,dict):raise Stop('RPC_RESULT_SCHEMA')
        key='hash' if method=='eth_getTransactionByHash' else 'transactionHash'
        hash32(value.get(key));hash32(value.get('blockHash'));quantity(value.get('blockNumber'));quantity(value.get('transactionIndex'))
        if method=='eth_getTransactionReceipt':
            quantity(value.get('status'))
            if not isinstance(value.get('logs'),list):raise Stop('RPC_RESULT_SCHEMA')
            for item in value['logs']:validate_log(item)
    else:raise Stop('RPC_RESULT_SCHEMA')

def hash32(value):
    if not isinstance(value,str) or not re.fullmatch('0x[0-9a-fA-F]{64}',value):raise Stop('HASH_SCHEMA')

def validate_header(value):
    if not isinstance(value,dict):raise Stop('HEADER_SCHEMA')
    for key in ['number','timestamp','baseFeePerGas']:quantity(value.get(key))
    for key in ['hash','parentHash']:hash32(value.get(key))

def validate_log(value):
    if not isinstance(value,dict):raise Stop('LOG_SCHEMA')
    for key in ['blockNumber','logIndex','transactionIndex']:quantity(value.get(key))
    for key in ['blockHash','transactionHash']:hash32(value.get(key))
    if not re.fullmatch('0x[0-9a-fA-F]{40}',str(value.get('address'))):raise Stop('LOG_SCHEMA')
    if not isinstance(value.get('topics'),list):raise Stop('LOG_SCHEMA')
    for topic in value['topics']:hash32(topic)
    rawhex(value.get('data'))

# Unreleased diagnostic candidate: fixed labels only, never exception text.
_DIAGNOSTIC_TYPES={urllib.error.URLError:'URLError',urllib.error.HTTPError:'HTTPError',OSError:'OSError',ConnectionError:'ConnectionError',ConnectionAbortedError:'ConnectionAbortedError',ConnectionRefusedError:'ConnectionRefusedError',ConnectionResetError:'ConnectionResetError',BrokenPipeError:'BrokenPipeError',TimeoutError:'TimeoutError',socket.gaierror:'gaierror',socket.herror:'herror',ssl.SSLError:'SSLError',ssl.SSLCertVerificationError:'SSLCertVerificationError',ssl.SSLEOFError:'SSLEOFError',ssl.SSLZeroReturnError:'SSLZeroReturnError',EOFError:'EOFError',ValueError:'ValueError',RuntimeError:'RuntimeError'}
_DIAGNOSTIC_TYPES.update({http.client.RemoteDisconnected:'RemoteDisconnected',http.client.BadStatusLine:'BadStatusLine',http.client.IncompleteRead:'IncompleteRead',http.client.ResponseNotReady:'ResponseNotReady',http.client.CannotSendRequest:'CannotSendRequest',http.client.HTTPException:'HTTPException'})
_DIAGNOSTIC_TLS_TYPES={ssl.SSLError,ssl.SSLCertVerificationError,ssl.SSLEOFError,ssl.SSLZeroReturnError}

def safe_transport_diagnostic(ex,phase,started_ns,received):
    # Exact-type lookup prevents arbitrary dynamic exception class names reaching disk.
    outer_type=type(ex);outer=_DIAGNOSTIC_TYPES.get(outer_type,'OTHER')
    reason=ex.reason if outer_type is urllib.error.URLError else None
    inner_type=type(reason)
    inner='NONE' if reason is None else ('TEXT_NOT_SAVED' if inner_type is str else _DIAGNOSTIC_TYPES.get(inner_type,'OTHER'))
    def integer_attr(obj,key):
        # Do not inspect properties on unknown custom exception classes.
        if type(obj) not in _DIAGNOSTIC_TYPES:return None
        value=getattr(obj,key,None)
        return value if type(value) is int else None
    err=integer_attr(reason,'errno')
    if err is None:err=integer_attr(ex,'errno')
    verify=integer_attr(reason,'verify_code')
    if verify is None:verify=integer_attr(ex,'verify_code')
    return {'phase':phase if phase in {'REQUEST_BUILD','OPEN','READ','SOCKET_CONNECT','PROXY_CONNECT_SEND','PROXY_CONNECT_HEADER','TLS_HANDSHAKE','HTTP_REQUEST_SEND','HTTP_RESPONSE_HEADER'} else 'OTHER',
            'exception_type':outer,'reason_type':inner,'errno':err,'verify_code':verify,
            'timeout':outer_type is TimeoutError or inner_type is TimeoutError,
            'TLS':outer_type in _DIAGNOSTIC_TLS_TYPES or inner_type in _DIAGNOSTIC_TLS_TYPES,
            'certificate_verification':outer_type is ssl.SSLCertVerificationError or inner_type is ssl.SSLCertVerificationError,
            'elapsed_monotonic_ns':max(0,time.monotonic_ns()-started_ns),
            'bytes_received':received if type(received) is int and received>=0 else 0}

class SystemHTTPSRoute:
    """Fixed destination, one existing loopback route read once; private values never logged."""
    def __init__(self,proxy,port,config_child_CPU_seconds=0):
        try:address=ipaddress.ip_address(proxy.strip('[]'))
        except ValueError:raise Stop('SYSTEM_ROUTE_IP_LITERAL_REQUIRED') from None
        if not address.is_loopback or type(port)is not int or not 1<=port<=65535:raise Stop('SYSTEM_ROUTE_LOOPBACK_PORT_REQUIRED')
        self._proxy=str(address);self._port=port;self.config_child_CPU_seconds=config_child_CPU_seconds
    @classmethod
    def from_system(cls):
        before=resource.getrusage(resource.RUSAGE_CHILDREN)
        try:
            result=subprocess.run(['/usr/sbin/scutil','--proxy'],env={'PATH':'/usr/bin:/bin:/usr/sbin:/sbin','LANG':'en_US.UTF-8'},capture_output=True,timeout=3)
            if result.returncode!=0 or len(result.stdout)>65536:raise Stop('SYSTEM_ROUTE_CONFIG_READ_FAILED')
            values={}
            for line in result.stdout.decode('utf8','replace').splitlines():
                m=re.fullmatch(r'\s*(HTTPSEnable|HTTPSProxy|HTTPSPort|ProxyAutoConfigEnable)\s*:\s*(.*?)\s*',line)
                if m:values[m[1]]=m[2]
            if values.get('HTTPSEnable')!='1' or values.get('ProxyAutoConfigEnable') not in (None,'0'):raise Stop('SYSTEM_ROUTE_DISABLED_OR_PAC')
            port=values.get('HTTPSPort','')
            if not re.fullmatch(r'[0-9]+',port):raise Stop('SYSTEM_ROUTE_PORT_REQUIRED')
            after=resource.getrusage(resource.RUSAGE_CHILDREN)
            child=max(0,after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime)
            return cls(values.get('HTTPSProxy',''),int(port),child)
        except Stop:raise
        except Exception:raise Stop('SYSTEM_ROUTE_CONFIG_READ_FAILED') from None
    def open_tls(self,context,timeout=15,phase_callback=None):
        if not context.check_hostname or context.verify_mode!=ssl.CERT_REQUIRED:raise Stop('SYSTEM_ROUTE_STRICT_TLS_REQUIRED')
        started=time.monotonic();raw=None
        def remaining():
            value=min(15,timeout)-(time.monotonic()-started)
            if value<=0:raise Stop('SYSTEM_ROUTE_TIMEOUT')
            return min(5,value)
        try:
            if phase_callback is not None:phase_callback('SOCKET_CONNECT')
            raw=socket.create_connection((self._proxy,self._port),timeout=remaining())
            raw.settimeout(remaining())
            if phase_callback is not None:phase_callback('PROXY_CONNECT_SEND')
            raw.sendall(b'CONNECT eth-mainnet.g.alchemy.com:443 HTTP/1.1\r\nHost: eth-mainnet.g.alchemy.com:443\r\n\r\n')
            if phase_callback is not None:phase_callback('PROXY_CONNECT_HEADER')
            header=bytearray()
            while not header.endswith(b'\r\n\r\n'):
                if len(header)>=8192:raise Stop('SYSTEM_ROUTE_CONNECT_HEADER_CAP')
                raw.settimeout(remaining());part=raw.recv(1)
                if not part:raise Stop('SYSTEM_ROUTE_CONNECT_EOF')
                header.extend(part)
            m=re.fullmatch(rb'HTTP/1\.[01] ([0-9]{3})(?: [^\r\n]*)?',bytes(header).split(b'\r\n',1)[0])
            if not m:raise Stop('SYSTEM_ROUTE_CONNECT_STATUS_INVALID')
            if int(m[1])!=200:raise Stop('SYSTEM_ROUTE_CONNECT_NON200_NO_AUTH')
            if phase_callback is not None:phase_callback('TLS_HANDSHAKE')
            raw.settimeout(remaining());tls=context.wrap_socket(raw,server_hostname=HOST)
            try:remaining()
            except BaseException:
                tls.close();raise
            raw=None;return tls
        finally:
            if raw is not None:
                try:raw.close()
                except Exception:pass

class RouteHTTPSConnection(http.client.HTTPSConnection):
    def __init__(self,route,timeout,context,phase_callback=None):
        super().__init__(HOST,443,timeout=timeout,context=context);self._route=route;self._phase_callback=phase_callback
    def connect(self):
        self.sock=self._route.open_tls(self._context,self.timeout,phase_callback=self._phase_callback)


class RPC:
    def __init__(self,endpoint,budget,evidence,costs,max_body=8*1024**2,route=None):
        if route is None:raise Stop('SYSTEM_ROUTE_REQUIRED_NO_DIRECT_FALLBACK')
        self.route=route
        self.endpoint=endpoint;self.budget=budget;self.evidence=evidence;self.costs=costs;self.max_body=max_body;self.seq=0
        self._tls_context=ssl.create_default_context();self._connection=None;self._failed=False
    def close(self):
        connection=self._connection;self._connection=None
        if connection is not None:
            try:connection.close()
            except Exception:pass
    def _remaining(self,started):
        remaining=15-(time.monotonic()-started)
        if remaining<=0:raise Stop('RPC_TIMEOUT')
        return remaining
    def call(self,method,params):
        if self._failed:raise Stop('RPC_SESSION_STOPPED_NO_RETRY')
        if method not in ALLOWED or method in {'eth_subscribe','eth_unsubscribe'}:raise Stop('METHOD_NOT_ALLOWED')
        if method not in self.costs:raise Stop('METHOD_COST_UNBOUND')
        self.budget.charge(self.costs[method]);self.seq+=1
        request={'jsonrpc':'2.0','id':self.seq,'method':method,'params':params};started={'UTC':utc(),'monotonic_ns':time.monotonic_ns()};raw=b'';status=None;safe_error=None;headers={}
        request_started=time.monotonic();request_started_ns=time.monotonic_ns();phase='REQUEST_BUILD';transport_diagnostic=None
        connection_reused=False;r=None
        def set_phase(value):
            nonlocal phase
            phase=value
        try:
            payload=json.dumps(request).encode()
            phase='OPEN'
            connection_reused=self._connection is not None and self._connection.sock is not None
            if self._connection is None:
                self._connection=RouteHTTPSConnection(self.route,timeout=self._remaining(request_started),context=self._tls_context,phase_callback=set_phase)
                self._connection.set_debuglevel(0)  # Never expose URL/path/body through stdlib debug output.
            connection=self._connection
            if connection.sock is None:
                connection.timeout=self._remaining(request_started);connection.connect()
            connection.sock.settimeout(self._remaining(request_started))
            # HTTP/1.1 persistence; no proxy/tunnel, redirect handler, retry or URL argument.
            phase='HTTP_REQUEST_SEND'
            connection.request('POST',self.endpoint._path,body=payload,headers={'Content-Type':'application/json'})
            connection.sock.settimeout(self._remaining(request_started))
            phase='HTTP_RESPONSE_HEADER'
            r=connection.getresponse();phase='READ'
            status=r.status;headers=safe_headers(r.headers);pieces=[];length=0
            while True:
                remaining=self._remaining(request_started)
                # HTTPResponse may close fp after the final Content-Length/chunked byte.
                if r.isclosed():
                    if r.length not in (None,0):raise Stop('RPC_INCOMPLETE_BODY')
                    break
                if connection.sock is not None:connection.sock.settimeout(remaining)
                else:
                    # http.client detaches socket when response.will_close; retain per-read deadline.
                    try:r.fp.raw._sock.settimeout(remaining)
                    except AttributeError:raise Stop('RPC_TIMEOUT_CONTROL_UNAVAILABLE')
                chunk=r.read(min(65536,self.max_body+1-length))
                if not chunk:
                    if r.length not in (None,0):raise Stop('RPC_INCOMPLETE_BODY')
                    break
                pieces.append(chunk);length+=len(chunk);raw=b''.join(pieces)
                if length>self.max_body:raise Stop('RPC_BODY_CAP')
            server_closed=r.will_close;r.close();r=None
            if server_closed:self.close()  # A subsequent NEW method may create a new connection; never replay this method.
        except Stop as ex:safe_error=str(ex)
        except Exception as ex:
            transport_diagnostic=safe_transport_diagnostic(ex,phase,request_started_ns,len(raw))
            safe_error='TRANSPORT_'+transport_diagnostic['exception_type']
        finally:
            if r is not None:
                try:r.close()
                except Exception:pass
        ended={'UTC':utc(),'monotonic_ns':time.monotonic_ns()}
        result=None
        if not safe_error and status!=200:safe_error='HTTP_REFUSAL_OR_ERROR_'+str(status)
        if not safe_error:
            try:
                j=json.loads(raw)
                if not isinstance(j,dict) or j.get('id')!=self.seq or j.get('jsonrpc')!='2.0' or 'error'in j or j.get('result') is None:raise Stop('RPC_ERROR_NULL_OR_ID')
                result=j['result'];validate_rpc_result(method,result)
            except Stop as ex:safe_error=str(ex)
            except Exception:safe_error='RPC_JSON_SCHEMA'
        if safe_error:self._failed=True;self.close()
        record={'transport_connection_reused':connection_reused,'endpoint':self.endpoint.safe(),'request':request,'started':started,'ended':ended,'HTTP':status,'headers':headers,'error':safe_error,'budget':self.budget.state()}
        if transport_diagnostic is not None:record['transport_diagnostic']=transport_diagnostic
        if safe_error:
            # Refusal/error/null/schema bodies can reflect secrets in escaped forms: never archive them.
            record['provider_error_body_saved']=False
        else:record['body_utf8']=self.endpoint.redact(raw).decode('utf8')
        try:self.last_artifact=self.evidence.save('rpc',record,self.endpoint)
        except BaseException:
            self._failed=True;self.close();raise
        if safe_error:raise Stop(safe_error)
        return result

class HeadStream:
    """Minimal RFC6455 TLS client, single thread; no proxy/env/library telemetry."""
    def __init__(self,endpoint,budget,evidence,subscribe_cu,notification_rate,max_body=1024**2,route=None):
        if route is None:raise Stop('SYSTEM_ROUTE_REQUIRED_NO_DIRECT_FALLBACK')
        self.route=route
        if notification_rate!='0.04':raise Stop('STREAM_BILLING_UNBOUND')
        self.endpoint=endpoint;self.budget=budget;self.evidence=evidence;self.max_body=max_body;self.sock=None;self.notification_payload_bytes=[];self.notification_wire_bytes=[]
        budget.charge(subscribe_cu)
        try:
            self.sock=self.route.open_tls(ssl.create_default_context(),15)
            key=base64.b64encode(os.urandom(16)).decode()
            request=('GET '+endpoint._path+' HTTP/1.1\r\nHost: '+HOST+'\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: '+key+'\r\nSec-WebSocket-Version: 13\r\n\r\n').encode()
            self.sock.sendall(request);header=b''
            while not header.endswith(b'\r\n\r\n'):
                header+=self._read(1)
                if len(header)>16384:raise Stop('WS_HANDSHAKE_CAP')
            lines=header.decode('ascii').split('\r\n');headers={x.split(':',1)[0].lower():x.split(':',1)[1].strip() for x in lines[1:] if ':'in x}
            accept=base64.b64encode(hashlib.sha1((key+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest()).decode()
            accepted=lines[0].startswith('HTTP/1.1 101 ') and headers.get('sec-websocket-accept')==accept
            evidence.save('stream-handshake',{'UTC':utc(),'endpoint':endpoint.safe(),'accepted':accepted,'raw_headers_saved':False},endpoint)
            if not accepted:raise Stop('WS_HANDSHAKE_REFUSAL')
            self.send({'jsonrpc':'2.0','id':1,'method':'eth_subscribe','params':['newHeads']})
            j=self.receive_json(charge=False)
            if j.get('id')!=1 or 'error'in j or not re.fullmatch('0x[0-9a-fA-F]+',str(j.get('result'))):raise Stop('WS_SUBSCRIPTION_ERROR')
            self.subscription=j['result'];self.sock.settimeout(60);evidence.save('stream-subscribe',{'UTC':utc(),'endpoint':endpoint.safe(),'subscription':self.subscription,'response':j,'budget':budget.state()},endpoint)
        except Stop:raise
        except Exception:raise Stop('WS_CONNECT_OR_PROTOCOL_ERROR') from None
    def _read(self,n):
        out=b''
        while len(out)<n:
            x=self.sock.recv(n-len(out))
            if not x:raise Stop('WS_DISCONNECTED_NO_RECONNECT')
            out+=x
        return out
    def send(self,obj):
        b=json.dumps(obj,separators=(',',':')).encode();mask=os.urandom(4)
        if len(b)<126:head=bytes([0x81,0x80|len(b)])
        elif len(b)<65536:head=b'\x81\xfe'+struct.pack('!H',len(b))
        else:head=b'\x81\xff'+struct.pack('!Q',len(b))
        self.sock.sendall(head+mask+bytes(v^mask[i%4] for i,v in enumerate(b)))
    def receive_json(self,charge=True):
        while True:
            first,second=self._read(2);opcode=first&15
            if first&0x70 or second&0x80:raise Stop('WS_UNEXPECTED_EXTENSIONS_OR_MASK')
            n=second&127
            frame_header_bytes=2
            if n==126:n=struct.unpack('!H',self._read(2))[0];frame_header_bytes+=2
            elif n==127:n=struct.unpack('!Q',self._read(8))[0];frame_header_bytes+=8
            if n>self.max_body:raise Stop('WS_BODY_CAP')
            b=self._read(n)
            if opcode==8:raise Stop('WS_SERVER_CLOSED')
            if opcode==9:
                if n>125:raise Stop('WS_CONTROL_FRAME')
                mask=os.urandom(4);self.sock.sendall(bytes([0x8a,0x80|n])+mask+bytes(v^mask[i%4] for i,v in enumerate(b)));continue
            if opcode==10:continue
            if opcode!=1 or not first&0x80:raise Stop('WS_FRAGMENTED_OR_NON_TEXT_UNSUPPORTED')
            # Exact payload .04 CU/byte; reserve unencrypted WS framing too because provider overhead scope is unknown.
            billed_bound_bytes=n+frame_header_bytes;cost=(billed_bound_bytes+24)//25
            arrival=time.monotonic();arrived_utc=utc()
            # Charge actual delivered bytes even if rejected; never persist error/invalid payload.
            try:
                j=json.loads(b)
                if not isinstance(j,dict) or 'error' in j:raise Stop('WS_ERROR_OR_SCHEMA')
                if charge:
                    params=j.get('params',{})
                    if j.get('method')!='eth_subscription' or not isinstance(params,dict) or params.get('subscription')!=self.subscription:raise Stop('WS_UNEXPECTED_NOTIFICATION')
                    validate_header(params.get('result'))
                elif j.get('id')!=1 or not re.fullmatch('0x[0-9a-fA-F]+',str(j.get('result'))):raise Stop('WS_SUBSCRIPTION_ERROR')
            except Exception:
                self.evidence.save('stream-error',{'UTC':arrived_utc,'safe_category':'WS_ERROR_OR_INVALID_SCHEMA','payload_bytes':n,'raw_body_saved':False},self.endpoint)
                self.budget.delivered(cost,arrival)
                raise Stop('WS_ERROR_OR_INVALID_SCHEMA') from None
            self.evidence.save('stream-validated-before-accounting',{'UTC':arrived_utc,'monotonic_ns':time.monotonic_ns(),'body_utf8':b.decode('utf8'),'payload_bytes':n,'frame_header_bytes':frame_header_bytes,'conservative_CU':cost,'arrival_scope':'Applicationreadtime; not NIC or providerbillingtimestamp'},self.endpoint)
            self.budget.delivered(cost,arrival)
            if charge:
                self.notification_payload_bytes.append(n);self.notification_wire_bytes.append(billed_bound_bytes)
                self.notification_payload_bytes=self.notification_payload_bytes[-128:];self.notification_wire_bytes=self.notification_wire_bytes[-128:]
            self.evidence.save('stream',{'UTC':utc(),'monotonic_ns':time.monotonic_ns(),'body_utf8':b.decode('utf8','replace'),'payload_bytes':n,'frame_header_bytes':frame_header_bytes,'bandwidth_CU_exact_payload_numerator':4*n,'bandwidth_CU_denominator':100,'conservative_charged_CU':cost,'provider_frame_overhead_scope':'UNKNOWN_conservatively_included','budget':self.budget.state()},self.endpoint)
            return j
    def head(self):
        try:j=self.receive_json()
        except Stop:raise
        except Exception:raise Stop('WS_READ_ERROR') from None
        if j.get('method')!='eth_subscription' or j.get('params',{}).get('subscription')!=self.subscription or not isinstance(j.get('params',{}).get('result'),dict):raise Stop('WS_UNEXPECTED_NOTIFICATION')
        h=j['params']['result'];h['_received_UTC']=utc();h['_received_monotonic_ns']=time.monotonic_ns();return h
    def backlog(self):
        return bool(self.sock.pending() or select.select([self.sock],[],[],0)[0])
    def close(self):
        if self.sock:
            try:self.sock.close()
            except Exception:pass

class ChainTrack:
    def __init__(self):self.headers={};self.tip=None;self.gaps=[]
    def accept(self,h):
        n=quantity(h.get('number'));b=h.get('hash');parent=h.get('parentHash')
        if not re.fullmatch('0x[0-9a-fA-F]{64}',str(b)) or not re.fullmatch('0x[0-9a-fA-F]{64}',str(parent)):raise Stop('HEADER_IDENTITY')
        if self.tip is None:self.headers[n]=h;self.tip=n;return 'FIRST'
        if n==self.tip and self.headers[n]['hash']==b:return 'DUPLICATE'
        if n==self.tip+1 and parent==self.headers[self.tip]['hash']:
            self.headers[n]=h;self.tip=n
            for k in list(self.headers):
                if k<n-128:del self.headers[k]
            return 'EXTENDS'
        if n<=self.tip and n-1 in self.headers and self.headers[n-1]['hash']==parent:
            for k in list(self.headers):
                if k>=n:del self.headers[k]
            self.headers[n]=h;self.tip=n;return 'REORG'
        self.gaps.append({'previous':self.tip,'received':n});raise Stop('MISSING_HEAD_OR_UNRESOLVED_REORG')

class Episodes:
    def __init__(self):self.rows={};self.daily={};self.generation=0;self.participations=[]
    def unknown(self):
        for v in self.rows.values():v['unknown_gap']=True
    def update(self,rows,day,blockhash):
        eligible=[]
        present={str(r['id']) for r in rows}
        for key in list(self.rows):
            if key not in present:del self.rows[key]  # Full same-block universe confirms ID removal.
        for r in rows:
            key=str(r['id']);old=self.rows.get(key)
            if not r['eligible']:
                self.rows.pop(key,None);continue
            if old is None:
                self.generation+=1;old={'episode':self.generation,'unknown_gap':False,'participated':False};self.rows[key]=old
            if old['unknown_gap']:continue
            if not old['participated'] and r.get('fee_qualified') is True:
                old['participated']=True;eligible.append(r);self.participations.append({'id':r['id'],'episode':old['episode'],'day':day,'blockHash':blockhash,'selected':False})
        selected=None
        if eligible and day not in self.daily:
            selected=sorted(eligible,key=lambda r:(-r['minimum_reward_minus_ceiling'],r['id']))[0]
            self.daily[day]={'id':selected['id'],'blockHash':blockhash}
            for row in self.participations:
                if row['blockHash']==blockhash and row['id']==selected['id']:row['selected']=True
        return selected

def keccak256(data):
    """Legacy Ethereum Keccak-256, NOT hashlib.sha3_256; vector-tested locally."""
    rc=[0x0000000000000001,0x0000000000008082,0x800000000000808a,0x8000000080008000,0x000000000000808b,0x0000000080000001,0x8000000080008081,0x8000000000008009,0x000000000000008a,0x0000000000000088,0x0000000080008009,0x000000008000000a,0x000000008000808b,0x800000000000008b,0x8000000000008089,0x8000000000008003,0x8000000000008002,0x8000000000000080,0x000000000000800a,0x800000008000000a,0x8000000080008081,0x8000000000008080,0x0000000080000001,0x8000000080008008]
    rot=[[0,36,3,41,18],[1,44,10,45,2],[62,6,43,15,61],[28,55,25,21,56],[27,20,39,8,14]];mask=(1<<64)-1
    def rol(x,n):return ((x<<n)|(x>>(64-n if n else 64)))&mask
    def perm(a):
        for r in rc:
            c=[a[x]^a[x+5]^a[x+10]^a[x+15]^a[x+20] for x in range(5)];d=[c[(x-1)%5]^rol(c[(x+1)%5],1) for x in range(5)]
            for x in range(5):
                for y in range(5):a[x+5*y]^=d[x]
            b=[0]*25
            for x in range(5):
                for y in range(5):b[y+5*((2*x+3*y)%5)]=rol(a[x+5*y],rot[x][y])
            for x in range(5):
                for y in range(5):a[x+5*y]=b[x+5*y]^((~b[(x+1)%5+5*y])&b[(x+2)%5+5*y])
            a[0]^=r
    z=bytearray(data);q=136-(len(z)%136)
    z.extend(b'\x81' if q==1 else b'\x01'+b'\0'*(q-2)+b'\x80');a=[0]*25
    for off in range(0,len(z),136):
        for i in range(17):a[i]^=int.from_bytes(z[off+8*i:off+8*i+8],'little')
        perm(a)
    return b''.join(v.to_bytes(8,'little') for v in a)[:32]

def abi_type(p):
    return '('+','.join(abi_type(c) for c in p['components'])+')'+p['type'][5:] if p['type'].startswith('tuple') else p['type']

def abi_method(record,name,inputs=None,allow_nonview=False):
    rows=[x for x in record['abi'] if x.get('type')=='function' and x.get('name')==name and (inputs is None or [abi_type(a) for a in x['inputs']]==inputs)]
    if len(rows)!=1:raise Stop('ABI_METHOD_NOT_UNIQUE')
    x=rows[0]
    if x.get('stateMutability') not in ('view','pure') and not allow_nonview:raise Stop('ABI_METHOD_NOT_VIEW')
    signature=name+'('+','.join(abi_type(a) for a in x['inputs'])+')'
    return '0x'+keccak256(signature.encode()).hex()[:8],x


def reconstruct_rpc_body(path,root):
    root=pathlib.Path(root).resolve();chain=[];current=pathlib.Path(path['path'] if isinstance(path,dict) else path).resolve();artifact=path if isinstance(path,dict) else None
    for _ in range(64):
        if root not in current.parents:raise Stop('DELTA_PATH_OUTSIDE_UNIT')
        raw=current.read_bytes() if artifact is None else read_artifact_range(artifact)
        obj=json.loads(gzip.decompress(raw));chain.append(obj)
        if 'body_utf8' in obj:
            body=obj['body_utf8'].encode();break
        delta=obj.get('body_delta',{});a=delta.get('base_artifact',{});current=pathlib.Path(a['path']).resolve()
        artifact=a
        if digest(read_artifact_range(a))!=a['sha256']:raise Stop('DELTA_BASE_HASH')
    else:raise Stop('DELTA_CHAIN_TOO_LONG')
    for obj in reversed(chain[:-1]):
        d=obj['body_delta'];size=d['length_bytes'];arr=bytearray(body[:size]);arr.extend(b'\0'*max(0,size-len(arr)))
        for off,encoded in d['changed_chunks']:
            part=base64.b64decode(encoded,validate=True)
            if off%64 or off<0 or len(part)>64 or off+len(part)>size:raise Stop('DELTA_CHUNK_BOUNDS')
            arr[off:off+len(part)]=part
        body=bytes(arr)
        if digest(body)!=d['sha256_reconstructed_body']:raise Stop('DELTA_RECONSTRUCTION_HASH')
    return body


def read_artifact_range(a):
    with pathlib.Path(a['path']).open('rb') as f:
        f.seek(a.get('offset',0));raw=f.read(a['bytes'])
    if len(raw)!=a['bytes'] or digest(raw)!=a['sha256']:raise Stop('ARTIFACT_BYTE_RANGE_HASH')
    return raw

"""Isolated dRPC transport wiring; old Scanner/qualify/forecast remain unchanged."""
import importlib.util
import signal
import math
from pathlib import Path
import hashlib
import sys
OWNER=Path(__file__).resolve().parent.parent
BASE=OWNER.parent
DEPENDENCIES={
 'readonly_core.py':'54b09fc1d32186dfca56c0a8eb15b6172b335693824489676ba47c627c7af5bc',
 'readonly_collector.py':'2284076c49b25393fc057fafcbccb46a4bcf671b67303063f109c5d06077c485',
 'bindings-throughput10s-attempt-02.json':'2b4d1f6b228c63388cbcfbf9abe6d60ddf4fd803101639b5747ae9e8a9dac245'}
for name,want in DEPENDENCIES.items():
 if hashlib.sha256((OWNER/name).read_bytes()).hexdigest()!=want:raise RuntimeError('FROZEN_DEPENDENCY_CHANGED')
sys.path.insert(0,str(OWNER))
from readonly_core import *
import readonly_core as core
import readonly_collector as original
DRPC_HOST='eth.drpc.org'
HERE=Path(__file__).resolve().parent
class AnonymousEndpoint:
 _path='/'
 def safe(self):return 'DRPC_ANONYMOUS_PUBLIC_ETHEREUM'
 def redact(self,data):return data
class PreflightBudget(Budget):
 def charge(self,cost,count=1):
  if self.methods+count>101:raise Stop('THIS_UNIT_30_METHOD_CAP')
  return super().charge(cost,count)

class DataEvidence(Evidence):
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
            request=obj['request'];cache_key=(request['method'],len(request.get('params',[{}])[0].get('data','')))
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
        local=sum(max(p.stat().st_size,getattr(p.stat(),'st_blocks',0)*512) for p in HERE.rglob('*') if p.is_file() and not p.is_symlink())
        if local+len(packed)+65536>6*1024**2:raise Stop('THIS_UNIT_DISK_CAP')
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

class DRPCRoute(SystemHTTPSRoute):
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
    def open_tls(self,context,timeout=15):
        if not context.check_hostname or context.verify_mode!=ssl.CERT_REQUIRED:raise Stop('SYSTEM_ROUTE_STRICT_TLS_REQUIRED')
        started=time.monotonic();raw=None
        def remaining():
            value=min(15,timeout)-(time.monotonic()-started)
            if value<=0:raise Stop('SYSTEM_ROUTE_TIMEOUT')
            return min(5,value)
        try:
            raw=socket.create_connection((self._proxy,self._port),timeout=remaining())
            raw.settimeout(remaining())
            raw.sendall(b'CONNECT eth.drpc.org:443 HTTP/1.1\r\nHost: eth.drpc.org:443\r\n\r\n')
            header=bytearray()
            while not header.endswith(b'\r\n\r\n'):
                if len(header)>=8192:raise Stop('SYSTEM_ROUTE_CONNECT_HEADER_CAP')
                raw.settimeout(remaining());part=raw.recv(1)
                if not part:raise Stop('SYSTEM_ROUTE_CONNECT_EOF')
                header.extend(part)
            m=re.fullmatch(rb'HTTP/1\.[01] ([0-9]{3})(?: [^\r\n]*)?',bytes(header).split(b'\r\n',1)[0])
            if not m:raise Stop('SYSTEM_ROUTE_CONNECT_STATUS_INVALID')
            if int(m[1])!=200:raise Stop('SYSTEM_ROUTE_CONNECT_NON200_NO_AUTH')
            raw.settimeout(remaining());tls=context.wrap_socket(raw,server_hostname=DRPC_HOST)
            try:remaining()
            except BaseException:
                tls.close();raise
            raw=None;return tls
        finally:
            if raw is not None:
                try:raw.close()
                except Exception:pass

class DRPCConnection(http.client.HTTPSConnection):
 def __init__(self,route,timeout,context):
  super().__init__(DRPC_HOST,443,timeout=timeout,context=context);self._route=route
 def connect(self):self.sock=self._route.open_tls(self._context,self.timeout)

class DRPCRPC(RPC):
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
        if method not in {'eth_chainId','eth_getBlockByNumber','eth_call','eth_getCode'}:raise Stop('METHOD_NOT_ALLOWED')
        if method not in self.costs:raise Stop('METHOD_COST_UNBOUND')
        self.budget.charge(self.costs[method]);self.seq+=1
        request={'jsonrpc':'2.0','id':self.seq,'method':method,'params':params};started={'UTC':utc(),'monotonic_ns':time.monotonic_ns()};raw=b'';status=None;safe_error=None;headers={}
        request_started=time.monotonic();request_started_ns=time.monotonic_ns();phase='REQUEST_BUILD';transport_diagnostic=None
        connection_reused=False;r=None
        try:
            payload=json.dumps(request).encode()
            phase='OPEN'
            connection_reused=self._connection is not None and self._connection.sock is not None
            if self._connection is None:
                self._connection=DRPCConnection(self.route,timeout=self._remaining(request_started),context=self._tls_context)
                self._connection.set_debuglevel(0)  # Never expose URL/path/body through stdlib debug output.
            connection=self._connection
            if connection.sock is None:
                connection.timeout=self._remaining(request_started);connection.connect()
            connection.sock.settimeout(self._remaining(request_started))
            # HTTP/1.1 persistence; no proxy/tunnel, redirect handler, retry or URL argument.
            connection.request('POST',self.endpoint._path,body=payload,headers={'Content-Type':'application/json'})
            connection.sock.settimeout(self._remaining(request_started))
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
        record={'body_bytes':len(raw),'body_sha256':digest(raw),'engineering_equivalent_not_provider_bill':True,'transport_connection_reused':connection_reused,'endpoint':self.endpoint.safe(),'request':request,'started':started,'ended':ended,'HTTP':status,'headers':headers,'error':safe_error,'budget':self.budget.state()}
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

class HashScanner(original.Scanner):
 def aggregate(self,calls,tag):
  hash32(tag)
  data=aggregate3(self.b.selectors[('multicall','aggregate3')],calls)
  result=self.rpc.call('eth_call',[{'to':self.b.addresses['multicall'],'from':'0x'+'0'*40,'gas':hex(30000000),'data':data},{'blockHash':tag,'requireCanonical':True}])
  self.artifacts.append(self.rpc.last_artifact)
  decoded=decode_aggregate3(result,len(calls))
  if calls and calls[0]==self.b.method('tm','getTroveIdsCount') and decoded[0][0]:
   n=uints(decoded[0][1],1)[0]
   if len(calls)==1:self._initial_hash_count=(tag,n)
   elif getattr(self,'_initial_hash_count',None) is not None and self._initial_hash_count[0]==tag and self._initial_hash_count[1]!=n:raise Stop('SAME_HASH_COUNT_INCONSISTENT')
  return decoded
 def snapshot(self,h,initial=False):
  result=super().snapshot(h,initial)
  result['state_identifier_semantics']='EIP1898 object {blockHash:H,requireCanonical:true}; transaction data field; number fence retained'
  result['state_identifier_object']={'blockHash':h['hash'],'requireCanonical':True}
  return result

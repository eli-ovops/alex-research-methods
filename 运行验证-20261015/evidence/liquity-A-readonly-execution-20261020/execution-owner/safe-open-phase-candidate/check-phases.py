"""Synthetic, offline AST-extracted hooks. No complete client import or real system/socket."""
import ast,json,time,resource,pathlib,types,ssl,socket,http.client,urllib.error,hashlib,re
C=pathlib.Path(__file__).parent;O=C.parent;started=time.process_time();wall=time.monotonic();sentinel='SYNTHETIC_SECRET_DO_NOT_PERSIST_7261'
socket.create_connection=lambda *a,**k:(_ for _ in ()).throw(AssertionError('REAL_NETWORK_FORBIDDEN'))
text=(C/'readonly_core.py').read_text();tree=ast.parse(text);base=ast.parse((O/'readonly_core.py').read_text())
# Only whitelist diagnostic constants/classes/functions are executed, never imports/main/real route config.
names={'safe_transport_diagnostic','SystemHTTPSRoute','RouteHTTPSConnection','RPC'}
body=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in names or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in {'_DIAGNOSTIC_TYPES','_DIAGNOSTIC_TLS_TYPES'} for t in n.targets) or isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and isinstance(n.value.func.value,ast.Name) and n.value.func.value.id=='_DIAGNOSTIC_TYPES']
phases=['SOCKET_CONNECT','PROXY_CONNECT_SEND','PROXY_CONNECT_HEADER','TLS_HANDSHAKE','HTTP_REQUEST_SEND','HTTP_RESPONSE_HEADER'];rows=[]
class Stop(Exception):pass
for target in phases:
 state={'TLS_done':False,'calls':0,'closed':0};header=bytearray(b'HTTP/1.1 200 Connection established\r\n\r\n')
 def fail(label):
  if label==target:raise TimeoutError(sentinel)
 class FakeSocket:
  def settimeout(self,n):assert 0<n<=15
  def sendall(self,b):fail('PROXY_CONNECT_SEND');assert b.startswith(b'CONNECT ') and sentinel.encode()not in b
  def recv(self,n):fail('PROXY_CONNECT_HEADER');return bytes([header.pop(0)])
  def close(self):state['closed']+=1
 class Context:
  check_hostname=True;verify_mode=ssl.CERT_REQUIRED
  def wrap_socket(self,raw,server_hostname):fail('TLS_HANDSHAKE');state['TLS_done']=True;return raw
 def fake_connect(*a,**kw):state['calls']+=1;fail('SOCKET_CONNECT');return FakeSocket()
 class FakeHTTPSConnection:
  def __init__(self,host,port,timeout,context):self._context=context;self.timeout=timeout;self.sock=None
  def set_debuglevel(self,n):assert n==0
  def request(self,*a,**k):assert state['TLS_done'];fail('HTTP_REQUEST_SEND')
  def getresponse(self):fail('HTTP_RESPONSE_HEADER');raise AssertionError('UNEXPECTED_SUCCESS')
  def close(self):
   if self.sock:self.sock.close();self.sock=None
 fssl=types.SimpleNamespace(**{k:getattr(ssl,k) for k in dir(ssl) if not k.startswith('__')});fssl.create_default_context=lambda:Context()
 fsock=types.SimpleNamespace(create_connection=fake_connect,gaierror=socket.gaierror,herror=socket.herror)
 fc=types.SimpleNamespace(**{k:getattr(http.client,k) for k in dir(http.client) if not k.startswith('__')});fc.HTTPSConnection=FakeHTTPSConnection
 env={'Stop':Stop,'re':re,'time':time,'ssl':fssl,'socket':fsock,'http':types.SimpleNamespace(client=fc),'urllib':types.SimpleNamespace(error=urllib.error),'HOST':'FIXED_PUBLIC_TARGET_NOT_A_URL','json':json,'ALLOWED':{'eth_chainId'},'utc':lambda:'SYNTHETIC_UTC'}
 exec(compile(ast.Module(body=body,type_ignores=[]),'EXTRACTED_HOOKS_ONLY','exec'),env)
 route=object.__new__(env['SystemHTTPSRoute']);route._proxy='127.0.0.1';route._port=1
 class Budget:
  def __init__(self):self.methods=63
  def charge(self,c):assert c==0
  def state(self):return {'cu':32734,'methods':63,'cpu':6940}
 class Endpoint:
  _path='/SYNTHETIC_ONLY/'+sentinel
  def safe(self):return 'REDACTED'
 class Evidence:
  def __init__(self):self.rows=[]
  def save(self,kind,record,endpoint):self.rows.append(record);return {'synthetic':True}
 evidence=Evidence();rpc=env['RPC'](Endpoint(),Budget(),evidence,{'eth_chainId':0},route=route)
 try:rpc.call('eth_chainId',[])
 except Stop as e:assert str(e)=='TRANSPORT_TimeoutError'
 else:raise AssertionError('EXPECTED_STOP')
 record=evidence.rows[0];diag=record['transport_diagnostic'];assert diag['phase']==target and diag['exception_type']=='TimeoutError' and diag['timeout']is True
 assert record['provider_error_body_saved']is False and record['HTTP']is None
 assert sentinel not in json.dumps(record) and rpc._failed and rpc._connection is None and state['calls']==1
 try:rpc.call('eth_chainId',[])
 except Stop as e:assert str(e)=='RPC_SESSION_STOPPED_NO_RETRY'
 else:raise AssertionError('RETRY_NOT_STOPPED')
 assert state['calls']==1
 rows.append({'synthetic_injection':target,'expected_phase':target,'actual_phase':diag['phase'],'expected_stop':'TRANSPORT_TimeoutError','actual_stop':'TRANSPORT_TimeoutError','synthetic_secret_absent':True,'one_fake_connect_no_replay':True})
# Diagnostic legacy compatibility and hostile labels/classes do not expose arbitrary strings.
for label in ['REQUEST_BUILD','OPEN','READ','ARBITRARY_'+sentinel]:
 got=env['safe_transport_diagnostic'](TimeoutError(sentinel),label,time.monotonic_ns(),0)
 assert got['phase']==(label if label in {'REQUEST_BUILD','OPEN','READ'} else 'OTHER') and sentinel not in json.dumps(got)
Unknown=type('DYNAMIC_'+sentinel,(Exception,),{});d=env['safe_transport_diagnostic'](Unknown(sentinel),'OPEN',time.monotonic_ns(),0);assert d['exception_type']=='OTHER' and sentinel not in json.dumps(d)
# Untouched entire top-level AST units must match; affected hooks checked in exact complete diff.
changed={'safe_transport_diagnostic','SystemHTTPSRoute','RouteHTTPSConnection','RPC'};a=[ast.dump(n) for n in tree.body if not isinstance(n,(ast.ClassDef,ast.FunctionDef)) or n.name not in changed];b=[ast.dump(n) for n in base.body if not isinstance(n,(ast.ClassDef,ast.FunctionDef)) or n.name not in changed];assert a==b
# Within affected classes, unaffected methods also remain identical.
for cls,modified in [('SystemHTTPSRoute',{'open_tls'}),('RouteHTTPSConnection',{'__init__','connect'}),('RPC',{'call'})]:
 aa=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==cls);bb=next(n for n in base.body if isinstance(n,ast.ClassDef) and n.name==cls)
 assert [ast.dump(n) for n in aa.body if not isinstance(n,ast.FunctionDef) or n.name not in modified]==[ast.dump(n) for n in bb.body if not isinstance(n,ast.FunctionDef) or n.name not in modified]
result={'status':'PASS_SYNTHETIC_DIAGNOSTIC_WIRING_NOT_REAL_FAILURE_REPRODUCTION','six_phase_results':rows,'legacy_unknown_phase_unknown_dynamic_class_secret_checks':'PASS','unchanged_AST_budget_stream_other_functions_unaffected_methods':'PASS','real_socket_calls':0,'system_route_config_reads':0,'complete_client_import_or_entry':False,'main_core_unchanged_sha256':hashlib.sha256((O/'readonly_core.py').read_bytes()).hexdigest(),'body_CPU_seconds':time.process_time()-started,'body_wall_seconds':time.monotonic()-wall,'maxrss_platform_units':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
(C/'checks-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

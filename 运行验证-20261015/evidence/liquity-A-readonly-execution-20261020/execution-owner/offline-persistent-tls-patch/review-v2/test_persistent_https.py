"""Offline mocked transport safety; never realTLS/rootcause reproduction."""
import pathlib,tempfile,unittest,unittest.mock as mock,json,gzip,ast
import candidate_readonly_core as c

FAKE='PSEUDO_SECRET_SAFETY_FIXTURE'
class Sock:
    def __init__(self):self.timeouts=[]
    def settimeout(self,n):self.timeouts.append(n)
class Response:
    def __init__(self,obj=None,status=200,will_close=False,body=None,fail_read=None):
        self.body=json.dumps(obj).encode() if body is None else body;self.status=status;self.headers={};self.will_close=will_close;self.fail_read=fail_read;self.reads=0;self.closed=False;self.length=None
    def read(self,n):
        self.reads+=1
        if self.fail_read and self.reads==2:raise self.fail_read
        x=self.body[:n];self.body=self.body[n:];return x
    def close(self):self.closed=True
    def isclosed(self):return self.closed
class Conn:
    def __init__(self,host,port,timeout,context,responses,fail=None):
        self.host=host;self.port=port;self.timeout=timeout;self.context=context;self.responses=responses;self.fail=fail;self.sock=None;self.connections=0;self.requests=[];self.closes=0;self.debug=None
    def set_debuglevel(self,n):self.debug=n
    def connect(self):
        self.connections+=1
        if self.fail:raise self.fail
        self.sock=Sock()
    def request(self,method,path,body,headers):self.requests.append((method,path,body,headers))
    def getresponse(self):return self.responses.pop(0)
    def close(self):self.closes+=1;self.sock=None

class Persistent(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=pathlib.Path(__file__).parent);self.addCleanup(self.tmp.cleanup);self.path=pathlib.Path(self.tmp.name)
        self.guard=mock.patch.object(c.socket,'create_connection',side_effect=AssertionError('OFFLINE_NETWORK_FORBIDDEN'));self.guard.start();self.addCleanup(self.guard.stop)
        self.ep=c.SecretEndpoint('https://eth-mainnet.g.alchemy.com/v2/'+FAKE);self.e=c.Evidence(self.path,self.path);self.b=c.Budget(state={'cu':160,'methods':10,'cpu':6200});self.rpc=c.RPC(self.ep,self.b,self.e,{'eth_chainId':0})
        self.conns=[]
    def factory(self,sets,fail=None):
        def build(host,port,timeout,context):
            conn=Conn(host,port,timeout,context,sets.pop(0),fail);self.conns.append(conn);return conn
        return mock.patch.object(c.http.client,'HTTPSConnection',side_effect=build)
    def text(self):return b''.join(gzip.decompress(p.read_bytes()) for p in self.path.glob('*.gz'))
    def rows(self):
        s=self.text().decode();decoder=json.JSONDecoder();i=0;out=[]
        while i<len(s):v,i=decoder.raw_decode(s,i);out.append(v)
        return out
    def test_two_new_methods_reuse_one_strict_connection(self):
        with self.factory([[Response({'jsonrpc':'2.0','id':1,'result':'0x1'}),Response({'jsonrpc':'2.0','id':2,'result':'0x1'})]]):
            self.assertEqual(self.rpc.call('eth_chainId',[]),'0x1');self.assertEqual(self.rpc.call('eth_chainId',[]),'0x1')
        conn=self.conns[0];self.assertEqual(len(self.conns),1);self.assertEqual(conn.connections,1);self.assertEqual(len(conn.requests),2);self.assertEqual(conn.host,c.HOST);self.assertEqual(conn.port,443);self.assertEqual(conn.debug,0)
        self.assertTrue(conn.context.check_hostname);self.assertEqual(conn.context.verify_mode,c.ssl.CERT_REQUIRED);self.assertTrue(all(0<n<=15 for n in conn.sock.timeouts));self.assertNotIn(FAKE.encode(),self.text());self.assertEqual([r['transport_connection_reused'] for r in self.rows()],[False,True]);self.assertEqual((self.b.cu,self.b.methods),(160,12))
    def test_normal_server_close_new_method_new_connection_not_replay(self):
        with self.factory([[Response({'jsonrpc':'2.0','id':1,'result':'0x1'},will_close=True)],[Response({'jsonrpc':'2.0','id':2,'result':'0x1'})]]):
            self.rpc.call('eth_chainId',[]);self.rpc.call('eth_chainId',[])
        self.assertEqual([len(x.requests) for x in self.conns],[1,1]);self.assertEqual([x.connections for x in self.conns],[1,1])
    def test_OPEN_TLS_failure_closes_latches_and_never_replays(self):
        with self.factory([[]],fail=c.ssl.SSLEOFError(8,FAKE)):
            with self.assertRaisesRegex(c.Stop,'SSLEOFError'):self.rpc.call('eth_chainId',[])
            with self.assertRaisesRegex(c.Stop,'SESSION_STOPPED'):self.rpc.call('eth_chainId',[])
        self.assertEqual(self.conns[0].connections,1);self.assertEqual(len(self.conns[0].requests),0);self.assertEqual(self.b.methods,11);row=self.rows()[0];self.assertEqual(row['transport_diagnostic']['phase'],'OPEN');self.assertTrue(row['transport_diagnostic']['TLS']);self.assertNotIn(FAKE.encode(),self.text());self.assertIsNone(self.rpc._connection)
    def test_READ_failure_drops_partial_body_closes_no_retry(self):
        response=Response(body=FAKE.encode(),fail_read=c.http.client.IncompleteRead(FAKE.encode(),10))
        with self.factory([[response]]):
            with self.assertRaisesRegex(c.Stop,'IncompleteRead'):self.rpc.call('eth_chainId',[])
        row=self.rows()[0];self.assertEqual(row['transport_diagnostic']['phase'],'READ');self.assertEqual(row['transport_diagnostic']['bytes_received'],len(FAKE));self.assertNotIn('body_utf8',row);self.assertNotIn(FAKE.encode(),self.text());self.assertEqual(len(self.conns[0].requests),1);self.assertTrue(response.closed);self.assertIsNone(self.rpc._connection)
    def test_HTTP_refusal_and_redirect_stop_never_follow(self):
        for status in [302,403,429]:
            rpc=c.RPC(self.ep,c.Budget(),self.e,{'eth_chainId':0})
            with self.factory([[Response(status=status,body=FAKE.encode())]]):
                with self.assertRaisesRegex(c.Stop,'HTTP_REFUSAL'):rpc.call('eth_chainId',[])
                with self.assertRaisesRegex(c.Stop,'SESSION_STOPPED'):rpc.call('eth_chainId',[])
            self.assertEqual(len(self.conns[-1].requests),1);self.assertIsNone(rpc._connection)
        self.assertNotIn(FAKE.encode(),self.text())
    def test_error_null_invalid_schema_drop_body_close(self):
        for obj in [{'jsonrpc':'2.0','id':1,'error':{'message':FAKE}},{'jsonrpc':'2.0','id':1,'result':None,'reflect':FAKE},{'jsonrpc':'2.0','id':1,'result':FAKE}]:
            rpc=c.RPC(self.ep,c.Budget(),self.e,{'eth_chainId':0})
            with self.factory([[Response(obj)]]):
                with self.assertRaises(c.Stop):rpc.call('eth_chainId',[])
            self.assertIsNone(rpc._connection)
        self.assertNotIn(FAKE.encode(),self.text())
    def test_body_cap_and_method_allowlist_before_network(self):
        rpc=c.RPC(self.ep,c.Budget(),self.e,{'eth_chainId':0},max_body=4)
        with self.factory([[Response(body=b'12345')]]):
            with self.assertRaisesRegex(c.Stop,'BODY_CAP'):rpc.call('eth_chainId',[])
        self.assertIsNone(rpc._connection)
        with mock.patch.object(c.http.client,'HTTPSConnection') as connect:
            for method in ['eth_sendTransaction','eth_sign','wallet_sendCalls','eth_estimateGas']:
                with self.assertRaises(c.Stop):self.rpc.call(method,[])
            connect.assert_not_called()
    def test_timeout_before_connect_no_open_and_failed_latch(self):
        with mock.patch.object(self.rpc,'_remaining',side_effect=c.Stop('RPC_TIMEOUT')),mock.patch.object(c.http.client,'HTTPSConnection') as connect:
            with self.assertRaisesRegex(c.Stop,'RPC_TIMEOUT'):self.rpc.call('eth_chainId',[])
            connect.assert_not_called()
        self.assertTrue(self.rpc._failed)
    def test_unknown_dynamic_exception_class_name_not_saved(self):
        def never(self):raise AssertionError('TEXT_WAS_READ')
        Custom=type(FAKE,(Exception,),{'__str__':never,'__repr__':never})
        with self.factory([[]],fail=Custom(FAKE)):
            with self.assertRaisesRegex(c.Stop,'TRANSPORT_OTHER'):self.rpc.call('eth_chainId',[])
        self.assertNotIn(FAKE.encode(),self.text());self.assertEqual(self.rows()[0]['transport_diagnostic']['exception_type'],'OTHER')
    def test_successful_explicit_close_before_wait_next_new_method(self):
        with self.factory([[Response({'jsonrpc':'2.0','id':1,'result':'0x1'})],[Response({'jsonrpc':'2.0','id':2,'result':'0x1'})]]):
            self.rpc.call('eth_chainId',[]);self.rpc.close();self.rpc.call('eth_chainId',[])
        self.assertEqual([len(x.requests) for x in self.conns],[1,1]);self.assertFalse(self.rpc._failed)
    def test_detached_response_socket_retains_per_read_timeout(self):
        import types
        response=Response({'jsonrpc':'2.0','id':1,'result':'0x1'},will_close=True);socket=Sock();response.fp=types.SimpleNamespace(raw=types.SimpleNamespace(_sock=socket))
        with self.factory([[response]]):
            original=c.http.client.HTTPSConnection.side_effect
            def detached(*args,**kwargs):
                conn=original(*args,**kwargs);get=conn.getresponse
                def getresponse():result=get();conn.sock=None;return result
                conn.getresponse=getresponse;return conn
            c.http.client.HTTPSConnection.side_effect=detached
            self.rpc.call('eth_chainId',[])
        self.assertTrue(socket.timeouts);self.assertTrue(all(0<n<=15 for n in socket.timeouts));self.assertIsNone(self.rpc._connection)
    def test_evidence_failure_also_closes_and_latches(self):
        with self.factory([[Response({'jsonrpc':'2.0','id':1,'result':'0x1'})]]),mock.patch.object(self.e,'save',side_effect=c.Stop('DISK_BUDGET')):
            with self.assertRaisesRegex(c.Stop,'DISK_BUDGET'):self.rpc.call('eth_chainId',[])
            with self.assertRaisesRegex(c.Stop,'SESSION_STOPPED'):self.rpc.call('eth_chainId',[])
        self.assertIsNone(self.rpc._connection);self.assertEqual(self.b.methods,11);self.assertEqual(len(self.conns[0].requests),1)
    def real_response(self,id=1,truncated=False):
        import io
        body=json.dumps({'jsonrpc':'2.0','id':id,'result':'0x1'}).encode()
        class File(io.BytesIO):
            def __init__(self,data,socket):super().__init__(data);self._sock=socket;self.raw=self
        class FakeSocket(Sock):
            def makefile(self,mode):return File(b'HTTP/1.1 200 OK\r\nConnection: close\r\nContent-Length: '+str(len(body)+(5 if truncated else 0)).encode()+b'\r\n\r\n'+body,self)
        socket=FakeSocket();response=c.http.client.HTTPResponse(socket);response.begin();return response,socket
    def test_real_HTTPResponse_close_length_complete_then_new_method(self):
        first,sock1=self.real_response(1);second,sock2=self.real_response(2)
        with self.factory([[first],[second]]):
            original=c.http.client.HTTPSConnection.side_effect
            def detached(*args,**kwargs):
                conn=original(*args,**kwargs);get=conn.getresponse
                def response():r=get();conn.sock=None;return r
                conn.getresponse=response;return conn
            c.http.client.HTTPSConnection.side_effect=detached
            self.assertEqual(self.rpc.call('eth_chainId',[]),'0x1');self.assertIsNone(first.fp);self.assertEqual(first.length,0)
            self.assertEqual(self.rpc.call('eth_chainId',[]),'0x1')
        self.assertEqual([len(x.requests) for x in self.conns],[1,1]);self.assertFalse(self.rpc._failed);self.assertTrue(sock1.timeouts and sock2.timeouts)
    def test_real_HTTPResponse_truncated_length_never_success(self):
        response,socket=self.real_response(1,truncated=True)
        with self.factory([[response]]):
            original=c.http.client.HTTPSConnection.side_effect
            def detached(*args,**kwargs):
                conn=original(*args,**kwargs);conn.getresponse=lambda:(setattr(conn,'sock',None) or response);return conn
            c.http.client.HTTPSConnection.side_effect=detached
            with self.assertRaisesRegex(c.Stop,'INCOMPLETE_BODY'):self.rpc.call('eth_chainId',[])
            with self.assertRaisesRegex(c.Stop,'SESSION_STOPPED'):self.rpc.call('eth_chainId',[])
        self.assertTrue(self.rpc._failed);self.assertIsNone(self.rpc._connection);self.assertEqual(len(self.conns[0].requests),1);self.assertNotIn('body_utf8',self.rows()[0])
    def test_collector_close_changes_only_group_lifecycle(self):
        text=(pathlib.Path(__file__).parent/'candidate_readonly_collector.py').read_text();tree=ast.parse(text)
        self.assertIn('RUN_ID="remaining-preflight-20261020-02"',text);self.assertIn("not 6117<=prior_cpu<7200",text);self.assertIn("state.get('cu')!=160 or state.get('methods')!=10",text);self.assertIn('root/remaining-preflight-run02-release.json',text);
        self.assertIn('self.rpc.close()  # Successful snapshot ends',text);self.assertIn('rpc.close()  # Successful audit group',text);self.assertIn('rpc.close()  # Successful identity group',text)
        self.assertIn("if stream:stream.close()\n        rpc.close()",text);self.assertEqual(sum(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='close' for n in ast.walk(tree)),5)

if __name__=='__main__':unittest.main(verbosity=2)

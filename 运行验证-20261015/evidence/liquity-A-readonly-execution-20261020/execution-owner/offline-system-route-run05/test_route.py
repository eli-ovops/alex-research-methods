import unittest,unittest.mock as mock,types,inspect,socket,ssl,json
import readonly_core as c
import readonly_collector as collector
class Raw:
    def __init__(self,header=b'HTTP/1.1 200 OK\r\n\r\n'):self.header=header;self.sent=[];self.closed=False
    def settimeout(self,t):assert 0<t<=5
    def sendall(self,b):self.sent.append(b)
    def recv(self,n):x=self.header[:n];self.header=self.header[n:];return x
    def close(self):self.closed=True
class Context:
    check_hostname=True;verify_mode=ssl.CERT_REQUIRED
    def __init__(self,fail=False):self.calls=[];self.fail=fail
    def wrap_socket(self,raw,server_hostname):
        self.calls.append(server_hostname)
        if self.fail:raise ssl.SSLEOFError(8,'PSEUDO_SECRET_NOT_SAVED')
        return raw
class Route(unittest.TestCase):
    def test_config_rejection_and_read_once_without_env(self):
        for text in ['HTTPSEnable : 0','HTTPSEnable : 1\nHTTPSProxy : localhost\nHTTPSPort : 1234','HTTPSEnable : 1\nHTTPSProxy : [REDACTED_HOST]\nHTTPSPort : 1234','HTTPSEnable : 1\nHTTPSProxy : 127.0.0.1\nHTTPSPort : 1234\nProxyAutoConfigEnable : 1']:
            with mock.patch.object(c.subprocess,'run',return_value=types.SimpleNamespace(returncode=0,stdout=text.encode())),mock.patch.object(socket,'create_connection') as net:
                with self.assertRaises(c.Stop):c.SystemHTTPSRoute.from_system()
                net.assert_not_called()
        text=b'HTTPSEnable : 1\nHTTPSProxy : 127.0.0.1\nHTTPSPort : 1234\nProxyAutoConfigEnable : 0'
        with mock.patch.object(c.subprocess,'run',return_value=types.SimpleNamespace(returncode=0,stdout=text)) as read:
            route=c.SystemHTTPSRoute.from_system();read.assert_called_once();self.assertGreaterEqual(route.config_child_CPU_seconds,0)
    def test_single_CONNECT_no_API_path_and_strict_TLS(self):
        raw=Raw();ctx=Context();route=c.SystemHTTPSRoute('127.0.0.1',1234)
        with mock.patch.object(socket,'create_connection',return_value=raw) as create:
            self.assertIs(route.open_tls(ctx),raw);create.assert_called_once()
        self.assertEqual(ctx.calls,[c.HOST]);self.assertEqual(len(raw.sent),1);self.assertEqual(raw.sent[0],b'CONNECT eth-mainnet.g.alchemy.com:443 HTTP/1.1\r\nHost: eth-mainnet.g.alchemy.com:443\r\n\r\n')
        self.assertNotIn(b'/v2/',raw.sent[0]);self.assertNotIn(b'Authorization',raw.sent[0])
    def test_non200_TLSfail_no_retry_no_business_and_close(self):
        route=c.SystemHTTPSRoute('127.0.0.1',1234)
        for status in [302,403,407,429]:
            raw=Raw(('HTTP/1.1 '+str(status)+' No\r\n\r\n').encode());ctx=Context()
            with mock.patch.object(socket,'create_connection',return_value=raw) as net:
                with self.assertRaisesRegex(c.Stop,'NON200'):route.open_tls(ctx)
                net.assert_called_once();self.assertEqual(ctx.calls,[]);self.assertTrue(raw.closed)
        raw=Raw();ctx=Context(fail=True)
        with mock.patch.object(socket,'create_connection',return_value=raw) as net:
            with self.assertRaises(ssl.SSLEOFError):route.open_tls(ctx)
            net.assert_called_once();self.assertTrue(raw.closed);self.assertEqual(len(raw.sent),1)
    def test_headercap_and_no_direct_fallback(self):
        raw=Raw(b'x'*8192);route=c.SystemHTTPSRoute('127.0.0.1',1234)
        with mock.patch.object(socket,'create_connection',return_value=raw) as net:
            with self.assertRaisesRegex(c.Stop,'HEADER_CAP'):route.open_tls(Context())
            net.assert_called_once();self.assertTrue(raw.closed)
        with self.assertRaisesRegex(c.Stop,'NO_DIRECT_FALLBACK'):c.RPC(None,None,None,{})
        with self.assertRaisesRegex(c.Stop,'NO_DIRECT_FALLBACK'):c.HeadStream(None,None,None,10,'0.04')
    def test_both_channels_share_route_TLS_before_business_and_guards(self):
        route=types.SimpleNamespace(open_tls=mock.Mock(return_value=object()))
        conn=c.RouteHTTPSConnection(route,15,ssl.create_default_context());conn.connect();route.open_tls.assert_called_once()
        source=inspect.getsource(c.HeadStream.__init__);self.assertLess(source.index('self.route.open_tls'),source.index("'GET '+endpoint._path"))
        source=inspect.getsource(c.RPC.call);self.assertLess(source.index('connection.connect()'),source.index("connection.request('POST'"))
        live=inspect.getsource(collector.run_live);self.assertEqual(live.count('SystemHTTPSRoute.from_system()'),1);self.assertEqual(live.count('route=route'),2);self.assertIn('route.config_child_CPU_seconds',live)
        self.assertEqual(collector.RUN_ID,'remaining-preflight-20261020-05');self.assertIn("state.get('methods')!=20",inspect.getsource(collector.load_admission));self.assertIn('6425<=prior_cpu',inspect.getsource(collector.load_admission))
        self.assertEqual(c.Budget().peak,100);self.assertEqual(c.Budget(peak=300).peak,300);self.assertNotIn('eth_sendTransaction',c.ALLOWED)
if __name__=='__main__':
    with mock.patch.object(socket,'create_connection',side_effect=AssertionError('OFFLINE_NETWORK_FORBIDDEN')):unittest.main(verbosity=2)

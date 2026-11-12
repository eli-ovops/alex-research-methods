import sys,ssl,pathlib,json,unittest,socket,unittest.mock as mock,ast
import readonly_core as c
import readonly_collector as collector
from test_compatibility import Persistent
class Metadata(unittest.TestCase):
    def test_runtime_and_guards(self):
        self.assertGreaterEqual(sys.version_info,(3,11));self.assertTrue(ssl.OPENSSL_VERSION.startswith('OpenSSL 3.'))
        self.assertNotIn('site',sys.modules);self.assertNotIn('torch',sys.modules)
        self.assertEqual(sys.flags.no_site,1);self.assertEqual(sys.flags.ignore_environment,1)
        context=ssl.create_default_context();self.assertTrue(context.check_hostname);self.assertEqual(context.verify_mode,ssl.CERT_REQUIRED)
        self.assertIn('eth_chainId',c.ALLOWED);self.assertNotIn('eth_sendTransaction',c.ALLOWED)
        self.assertEqual(collector.RUN_ID,'remaining-preflight-20261020-03')
        text=pathlib.Path(collector.__file__).read_text()
        self.assertIn('not 6228<=prior_cpu<7200',text);self.assertIn("state.get('methods')!=11",text)
        self.assertIn("usage.get('retained_local_method_attempts')!=11",text)
        self.assertIn('2026-10-20T08:10:50Z',text)
if __name__=='__main__':
    names=['test_real_HTTPResponse_close_length_complete_then_new_method','test_real_HTTPResponse_truncated_length_never_success','test_normal_server_close_new_method_new_connection_not_replay','test_detached_response_socket_retains_per_read_timeout','test_completed_response_still_checks_elapsed_deadline']
    suite=unittest.TestSuite([Persistent(n) for n in names]+[Metadata('test_runtime_and_guards')])
    with mock.patch.object(socket,'create_connection',side_effect=AssertionError('OFFLINE_NETWORK_FORBIDDEN')):
        result=unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps({'version':sys.version,'ssl':ssl.OPENSSL_VERSION,'site_loaded':'site' in sys.modules,'torch_loaded':'torch' in sys.modules,'ssl_module':ssl.__file__,'http_client':c.http.client.__file__}))
    sys.exit(0 if result.wasSuccessful() else 1)

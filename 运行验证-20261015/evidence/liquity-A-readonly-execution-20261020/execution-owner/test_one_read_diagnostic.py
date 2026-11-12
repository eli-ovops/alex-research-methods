"""Offline driver safety checks, never a real RPC/error reproduction."""
import unittest,unittest.mock as mock,tempfile,pathlib,json,ast
import one_read_diagnostic as d

class Driver(unittest.TestCase):
    def setUp(self):
        patch=mock.patch.object(d.socket,'create_connection',side_effect=AssertionError('NETWORK_FORBIDDEN'));patch.start();self.addCleanup(patch.stop)
    def test_only_fixed_method_once_budget_and_separate_lock(self):
        with tempfile.TemporaryDirectory(dir=d.HERE) as tmp,mock.patch.object(d,'HERE',pathlib.Path(tmp)),mock.patch.object(d,'phase'):
            b=d.Budget(state={'cu':120,'methods':7,'cpu':5936});e=mock.Mock();endpoint=mock.Mock()
            class FakeRPC:
                def __init__(self,ep,budget,evidence,costs):self.b=budget;self.seq=0;self.last_artifact={'safe':'mock'};self.calls=[];self.costs=costs;self.__class__.instance=self
                def call(self,method,params):self.calls.append((method,params,self.seq));self.b.charge(self.costs[method]);return '0x11'
            with mock.patch.object(d,'RPC',FakeRPC):r=d.execute_once(endpoint,b,e,'0x11')
            self.assertEqual(FakeRPC.instance.calls,[('eth_getCode',[d.ADDRESS,'0x19043c9'],6)])
            self.assertEqual((b.cu,b.methods,b.cpu_prior),(140,8,5936));self.assertTrue(r['runtime_exact_bytes_match'])
            self.assertTrue((pathlib.Path(tmp)/'one-read-diagnostic.once.lock').exists());self.assertFalse((pathlib.Path(tmp)/'live-once.lock').exists())
            with mock.patch.object(d,'RPC',FakeRPC):
                with self.assertRaises(FileExistsError):d.execute_once(endpoint,b,e,'0x11')
            self.assertEqual((b.cu,b.methods),(140,8))
    def test_failure_is_one_call_no_fallback(self):
        with tempfile.TemporaryDirectory(dir=d.HERE) as tmp,mock.patch.object(d,'HERE',pathlib.Path(tmp)),mock.patch.object(d,'phase'):
            rpc=mock.Mock();rpc.call.side_effect=d.Stop('TRANSPORT_URLError')
            with mock.patch.object(d,'RPC',return_value=rpc):
                with self.assertRaisesRegex(d.Stop,'URLError'):d.execute_once(mock.Mock(),d.Budget(state={'cu':120,'methods':7,'cpu':5936}),mock.Mock(),'0x11')
            rpc.call.assert_called_once_with('eth_getCode',[d.ADDRESS,d.BLOCK])
    def test_expired_deadline_before_auth_or_prompt(self):
        end=d.dt.datetime(2026,10,20,6,4,55,tzinfo=d.dt.timezone.utc).timestamp()
        with mock.patch.object(d.time,'time',return_value=end+1),mock.patch.object(d,'load_inputs') as load,mock.patch.object(d,'prompt_endpoint') as prompt,mock.patch.object(d,'phase'),mock.patch('builtins.print'):
            d.main();load.assert_not_called();prompt.assert_not_called()
    def test_no_collector_import_and_single_literal_RPC_site(self):
        tree=ast.parse(pathlib.Path(d.__file__).read_text());imports=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)];self.assertNotIn('readonly_collector',imports)
        calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='call'];self.assertEqual(len(calls),1)
        self.assertEqual(ast.literal_eval(calls[0].args[0]),'eth_getCode')
    def test_release_hash_and_exact_scope_before_prompt(self):
        # Static validator paths, using entirely local synthetic authorization/releases.
        with tempfile.TemporaryDirectory(dir=d.HERE) as tmp:
            root=pathlib.Path(tmp);(root/'root').mkdir();home=root/'owner';home.mkdir();runtime=root/'record.json';runtime.write_text(json.dumps({'chainId':'1','address':d.ADDRESS,'runtimeBytecode':{'onchainBytecode':'0x11'}}))
            source={'record_path':str(runtime),'record_sha256':d.digest(runtime.read_bytes())};(home/'bindings.json').write_text(json.dumps({'contracts':{'multicall':source}}))
            for name in ['readonly_core.py','one_read_diagnostic.py','start-one-read-diagnostic.command']:(home/name).write_text('offline fake file')
            auth={'status':'AUTHORIZED_SINGLE_FIXED_GETCODE_DIAGNOSTIC','deadline_UTC':d.DEADLINE,'method':'eth_getCode','address':d.ADDRESS,'block':d.BLOCK,'max_RPC_methods':1,'no_retry':True,'no_payment':True,'prior_usage':{'cu':120,'methods':7,'cpu':5836},'verified_remaining_CU':30000000};ap=root/'root/one-read-diagnostic-auth.json';ap.write_text(json.dumps(auth))
            release={'status':'RELEASED_SINGLE_FIXED_GETCODE_DIAGNOSTIC','auth_sha256':d.digest(ap.read_bytes()),'reviewed_code_sha256':{name:d.digest((home/name).read_bytes()) for name in ['readonly_core.py','one_read_diagnostic.py','start-one-read-diagnostic.command']},'binding_sha256':d.digest((home/'bindings.json').read_bytes()),'runtime_source_sha256':d.digest(runtime.read_bytes()),'prior_CPU_upper_bound_seconds':5936};rp=root/'root/one-read-diagnostic-release.json';rp.write_text(json.dumps(release))
            with mock.patch.object(d,'HERE',home),mock.patch.object(d,'UNIT',root):
                a,prior,limit,expected=d.load_inputs();self.assertEqual((prior['cpu'],limit,expected),(5936,25000000,'0x11'))
                release['prior_CPU_upper_bound_seconds']=0;rp.write_text(json.dumps(release))
                with self.assertRaisesRegex(d.Stop,'PRIOR_CPU'):d.load_inputs()
                release['prior_CPU_upper_bound_seconds']=5936;release['reviewed_code_sha256']['one_read_diagnostic.py']='0'*64;rp.write_text(json.dumps(release))
                with self.assertRaisesRegex(d.Stop,'REVIEW_HASH'):d.load_inputs()
if __name__=='__main__':unittest.main(verbosity=2)

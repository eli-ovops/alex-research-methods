import unittest,unittest.mock as mock,tempfile,pathlib,json,hashlib,socket,inspect
import readonly_core as core
import readonly_collector as collector
class Gates(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=pathlib.Path(__file__).parent);self.addCleanup(self.temp.cleanup);self.unit=pathlib.Path(self.temp.name);(self.unit/'root').mkdir()
        self.patch=mock.patch.object(collector,'UNIT',self.unit);self.patch.start();self.addCleanup(self.patch.stop)
        self.guard=mock.patch.object(socket,'create_connection',side_effect=AssertionError('OFFLINE_NETWORK_FORBIDDEN'));self.guard.start();self.addCleanup(self.guard.stop)
        self.original={'path':'SYNTHETIC_PARENT_PATH_NOT_REAL_APPROVAL','sha256':'9db20a81259f7574dac7755cfff92515008787317b7b71831181c9c5737600dd'}
        self.c={'resource_authorization':self.original,'supplemental_peak_authorization':{'path':str(self.unit/'root/peak300-supplemental-authorization.json'),'sha256':'PENDING'}}
        self.a={'synthetic_fixture_only':True,'status':'APPROVED_PEAK300_ONLY','human_approved':True,'approved_peak_CU_per_second':300,'prior_usage_reset':False,'other_caps_unchanged':True,'deadline_UTC':'2026-10-20T08:10:50Z','original_resource_authorization':self.original}
    def fixture(self,a=None):
        raw=json.dumps(self.a if a is None else a).encode();path=pathlib.Path(self.c['supplemental_peak_authorization']['path']);path.write_bytes(raw);h=hashlib.sha256(raw).hexdigest();self.c['supplemental_peak_authorization']['sha256']=h
        return {'supplemental_peak_authorization_sha256':h,'authorized_peak_CU_per_second':300}
    def test_missing_or_pending_auth_fails(self):
        with self.assertRaisesRegex(core.Stop,'PEAK_AUTHORIZATION_MISSING'):collector.authorized_peak(self.c,{})
        r=self.fixture();self.c['supplemental_peak_authorization']['sha256']='PENDING'
        with self.assertRaisesRegex(core.Stop,'PEAK_AUTHORIZATION_HASH'):collector.authorized_peak(self.c,r)
    def test_parent_human_deadline_other_caps_fail_closed(self):
        for key,value in [('human_approved',False),('approved_peak_CU_per_second',301),('status','PENDING'),('deadline_UTC','2099-01-01T00:00:00Z'),('other_caps_unchanged',False),('prior_usage_reset',True),('original_resource_authorization',{})]:
            with self.subTest(key=key):
                a=dict(self.a);a[key]=value;r=self.fixture(a)
                with self.assertRaises(core.Stop):collector.authorized_peak(self.c,r)
    def test_missing_wrong_release_peak_binding_fails(self):
        r=self.fixture()
        for release in [{},{**r,'supplemental_peak_authorization_sha256':'WRONG'},{**r,'authorized_peak_CU_per_second':100}]:
            with self.assertRaisesRegex(core.Stop,'PEAK_RELEASE_BINDING'):collector.authorized_peak(self.c,release)
        self.assertEqual(collector.authorized_peak(self.c,r),300)
    def test_default100_and_explicit300_still_account_then_stop(self):
        b=core.Budget(state={'cu':447,'methods':19,'cpu':6319});self.assertEqual(b.peak,100)
        with mock.patch.object(b,'resource_check'):
            with self.assertRaisesRegex(core.Stop,'ACTUAL_DELIVERY_PEAK'):b.delivered(154,10)
        self.assertEqual(b.cu,601);self.assertEqual(b.methods,19)
        b=core.Budget(peak=300,state={'cu':447,'methods':19,'cpu':6319})
        with mock.patch.object(b,'resource_check'):
            b.delivered(154,10)
            with self.assertRaisesRegex(core.Stop,'ACTUAL_DELIVERY_PEAK'):b.delivered(154,10.5)
        self.assertEqual(b.cu,755);self.assertEqual(b.peak,300)
    def test_totalcaps_and_collector_guard_order_unchanged(self):
        b=core.Budget(cu_limit=999999999,method_limit=999999,peak=999,cpu=99999,ram=999999999999)
        self.assertEqual((b.cu_limit,b.method_limit,b.peak,b.cpu_limit,b.ram_limit),(25000000,400000,300,7200,1024**3))
        text=inspect.getsource(collector.load_admission);self.assertLess(text.index('verify_release'),text.index('authorized_peak'));self.assertIn('load_resource_amendment',text)
        amendment=inspect.getsource(collector.load_resource_amendment)
        for v in ['2026-10-20T08:10:50Z',"'peak_CU_per_second':100","'CPU_total_seconds':7200","'shared_A_B_CU':25000000"]:self.assertIn(v,amendment)
        self.assertEqual(collector.RUN_ID,'remaining-preflight-20261020-04')
        live=inspect.getsource(collector.run_live);self.assertIn('peak=b.authorized_peak',live)
if __name__=='__main__':unittest.main(verbosity=2)

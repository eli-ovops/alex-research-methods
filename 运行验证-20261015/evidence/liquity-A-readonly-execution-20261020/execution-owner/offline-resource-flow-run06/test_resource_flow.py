import unittest,unittest.mock as mock,pathlib,json,tempfile,types,datetime,copy,inspect,socket,resource
import readonly_core as core
import readonly_collector as c
P=pathlib.Path(__file__).resolve().parent.parent
REALUNIT=P.parent
AUTH=REALUNIT/'root/resource-flow-run06-supplemental-authorization.json'
class Flow(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=pathlib.Path(__file__).parent);self.addCleanup(self.tmp.cleanup);self.run=pathlib.Path(self.tmp.name)
        self.guard=mock.patch.object(socket,'create_connection',side_effect=AssertionError('OFFLINE_NETWORK_FORBIDDEN'));self.guard.start();self.addCleanup(self.guard.stop)
        self.conf=json.loads((pathlib.Path(__file__).parent/'bindings-remaining-preflight-run06.json.template').read_text());self.limits=json.loads(AUTH.read_text())['effective_limits'];self.conf['effective_limits']=self.limits
        self.release={'effective_limits':self.limits,'resource_flow_authorization_sha256':self.conf['resource_flow_authorization']['sha256'],'prior_CPU_upper_bound_seconds':6676,'new_active_work_budget':{'used_seconds_conservative':1200,'input_preflight_and_closeout_reserved_seconds':1200}}
    def test_effective_overlay_exact_and_invalid_release_fail(self):
        with mock.patch.object(c,'UNIT',REALUNIT):
            self.assertEqual(c.effective_resource_limits(self.conf,self.release),self.limits)
            for change in [{'resource_flow_authorization_sha256':'WRONG'},{'effective_limits':{**self.limits,'CPU_total_seconds_cumulative':7200}},{'new_active_work_budget':{'used_seconds_conservative':2401,'input_preflight_and_closeout_reserved_seconds':1200}}]:
                with self.subTest(change=list(change)):
                    with self.assertRaises(core.Stop):c.effective_resource_limits(self.conf,{**self.release,**change})
    def test_runtime_caps_OS_limit_and_writecap_consistent(self):
        self.assertEqual(core.Budget().cpu_limit,7200);self.assertEqual(core.Budget(cpu=18000).cpu_limit,18000);self.assertEqual(core.Budget(cpu=999999).cpu_limit,18000)
        e=core.Evidence(self.run/'evidence',self.run,cap=self.limits['new_disk_bytes_cumulative']);self.assertEqual(e.cap,8*1024**3)
        with mock.patch.object(e,'used',return_value=e.cap-1048576):
            with self.assertRaisesRegex(core.Stop,'DISK_BUDGET'):e.save('synthetic',{'a':1})
        with mock.patch.object(c.resource,'setrlimit') as setlimit,mock.patch.object(c.time,'process_time',return_value=1):
            c.set_process_CPU_limit(self.limits,6676,.5)
            setlimit.assert_called_once_with(resource.RLIMIT_CPU,(11323,11323))
    def test_old_sample_fullforecast_pass_newcaps_and_fail_oldcaps(self):
        old=json.loads(pathlib.Path(self.conf['historical_preinput_sample']['path']).read_text());sample=old['forecast_original'];measured=sample['full_measured_cycles']
        b=core.Budget(cpu=18000,state={'cu':1824,'methods':41,'cpu':6676})
        kwargs=dict(notification_bytes=sample['actual_notification_sample_bytes'],wait_seconds=4761*12,measured=measured,already_disk=sample['already_disk'],wait_disk=65536,wait_cpu=max(x['cpu']for x in measured))
        r=c.forecast(self.conf,b,0,0,**kwargs);self.assertLess(r['disk_including_already_and_wait_and_audit'],8*1024**3-1048576);self.assertLess(r['CPU_including_prior_and_wait_and_audit'],18000)
        oldc=copy.deepcopy(self.conf);oldc['effective_limits']['new_disk_bytes_cumulative']=2*1024**3
        with self.assertRaisesRegex(core.Stop,'FORECAST_DISK'):c.forecast(oldc,b,0,0,**kwargs)
        b.cpu_limit=7200
        with self.assertRaisesRegex(core.Stop,'FORECAST_CPU'):c.forecast(self.conf,b,0,0,**kwargs)
    def test_entry_halfwindow_and_remaining20min(self):
        at=lambda s:datetime.datetime.fromisoformat(s).timestamp()
        c.check_input_window(self.limits,now=at('2026-10-20T09:00:00+00:00'))
        for late in ['2026-10-20T09:29:59+00:00','2026-10-20T10:10:00+00:00']:
            with self.assertRaises(core.Stop):c.check_input_window(self.limits,now=at(late))
        with mock.patch.object(c.time,'time',return_value=at('2026-10-20T09:00:00+00:00')),mock.patch.object(c.signal,'signal'),mock.patch.object(c.signal,'alarm')as alarm:
            c.arm_startup_alarm(c.startup_timestamp(self.limits));self.assertEqual(alarm.call_args.args[0],5398)
        source=inspect.getsource(c.run_live);self.assertLess(source.index('signal.alarm(0)'),source.index("status='ARMED_ACTIVE_PROCESS'"));self.assertEqual(source.count('prompt_endpoint()'),1)
        self.assertIn('verify_no_key_preparation(b)',source);self.assertIn('old_sample_prescreen(b)',source);self.assertIn('input-entry.once.lock',source)
    def test_prescreen_is_no_network_and_actual_disk_checked(self):
        binding=types.SimpleNamespace(config=self.conf,limits=self.limits,release=self.release,authorized_peak=300)
        with mock.patch.object(c,'RUN_DIR',self.run),mock.patch.object(c,'UNIT',REALUNIT),mock.patch.object(c,'check_input_window'),mock.patch.object(c.os,'statvfs',return_value=types.SimpleNamespace(f_bavail=20*1024**3,f_frsize=1)):
            result=c.old_sample_prescreen(binding);self.assertIn('NOT_NEW_BLOCK',result['status']);self.assertGreater(result['actual_available_disk_bytes'],result['required_additional_disk_with_safety_bytes'])
            with mock.patch.object(c.os,'statvfs',return_value=types.SimpleNamespace(f_bavail=1,f_frsize=1)):
                with self.assertRaisesRegex(core.Stop,'AVAILABLE_DISK'):c.old_sample_prescreen(binding)
    def test_preparation_identity_expiry_failures(self):
        binding=types.SimpleNamespace(config=self.conf,limits=self.limits,release=self.release,raw=b'SYNTHETIC_BINDING')
        with mock.patch.object(c,'RUN_DIR',self.run):
            with self.assertRaisesRegex(core.Stop,'MISSING'):c.verify_no_key_preparation(binding)
            path=self.run/'no-key-preparation-receipt.json';path.write_text('{}');self.release['no_key_preparation']={'path':str(path),'sha256':'WRONG'}
            with self.assertRaisesRegex(core.Stop,'HASH'):c.verify_no_key_preparation(binding)
            self.release['no_key_preparation']['sha256']=core.digest(path.read_bytes())
            with self.assertRaisesRegex(core.Stop,'IDENTITY'):c.verify_no_key_preparation(binding)
            code={}
            for name in ['readonly_core.py','readonly_collector.py','start-A-remaining-preflight-run06.command']:
                (self.run/name).write_bytes(b'SYNTHETIC_SOURCE_ONLY');code[name]=core.digest(b'SYNTHETIC_SOURCE_ONLY')
            record={'status':'PASSED_NO_KEY_PREPARATION_ONLY','run_id':c.RUN_ID,'binding_sha256':core.digest(binding.raw),'resource_flow_authorization_sha256':self.conf['resource_flow_authorization']['sha256'],'code_sha256':code,'valid_until_UTC':'2026-10-20T09:00:00+00:00','public_TLS':{'status':'ONE_STRICT_TLS_SUCCESS','attempts':1}}
            path.write_text(json.dumps(record));self.release['no_key_preparation']['sha256']=core.digest(path.read_bytes())
            with mock.patch.object(c,'HERE',self.run),mock.patch.object(c.time,'time',return_value=datetime.datetime(2026,10,20,8,59,tzinfo=datetime.timezone.utc).timestamp()):
                c.verify_no_key_preparation(binding)
            with mock.patch.object(c,'HERE',self.run),mock.patch.object(c.time,'time',return_value=datetime.datetime(2026,10,20,9,0,1,tzinfo=datetime.timezone.utc).timestamp()):
                with self.assertRaisesRegex(core.Stop,'EXPIRED'):c.verify_no_key_preparation(binding)

    def test_publicprobe_once_before_key_and_legacy_auth_kept(self):
        prep=inspect.getsource(c.prepare_input);live=inspect.getsource(c.run_live)
        self.assertEqual(prep.count('route.open_tls('),1);self.assertNotIn('prompt_endpoint',prep);self.assertIn('no-key-preparation.once.lock',prep);self.assertIn('signal.alarm(min(10',prep)
        self.assertNotIn('route.open_tls(',live);self.assertIn("except Stop as ex:state.update(status='STOPPED_INCONCLUSIVE'",live)
        self.assertIn('CPU_total_seconds_cumulative',live);self.assertIn("cap=limits['new_disk_bytes_cumulative']",live)
        self.assertIn('2026-10-20T08:10:50Z',inspect.getsource(c.load_resource_amendment));self.assertIn('2026-10-20T08:10:50Z',inspect.getsource(c.authorized_peak))
        self.assertEqual(self.conf['shared_prior_usage'],{'cu':1824,'methods':41,'cpu':None});self.assertEqual(c.RUN_ID,'remaining-preflight-20261020-06');self.assertNotIn('torch',__import__('sys').modules)
if __name__=='__main__':unittest.main(verbosity=2)

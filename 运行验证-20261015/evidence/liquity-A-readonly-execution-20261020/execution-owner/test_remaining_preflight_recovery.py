"""Affected recovery checks only, offline and no collector main/driver launch."""
import pathlib,tempfile,json,unittest,unittest.mock as mock,ast
import readonly_collector as c

class Recovery(unittest.TestCase):
    def setUp(self):
        patch=mock.patch.object(c.socket,'create_connection',side_effect=AssertionError('OFFLINE_NO_NETWORK'));patch.start();self.addCleanup(patch.stop)
    def released(self,b):
        return {'prior_CPU_upper_bound_seconds':6060}
    def test_new_inputs_full_static_and_retained_prior(self):
        with mock.patch.object(c,'verify_release',side_effect=self.released):b=c.load_admission(c.HERE/'bindings-remaining-preflight.json')
        self.assertEqual(b.config['shared_prior_usage'],{'cu':140,'methods':8,'cpu':None});self.assertEqual(b.release['prior_CPU_upper_bound_seconds'],6060)
        self.assertEqual(b.config['verified_free_working_ceiling_CU'],25000000)
        self.assertEqual(b.config['static_release_required_at'],str(c.UNIT/'root/remaining-preflight-release.json'))
        self.assertEqual(b.config['shared_prior_usage_scope'],'Retain cumulative local140CU/8methods; CPU comes from root/remaining-preflight-release.json latest prior debit, with all subsequent local and process costs appended; never reset to0.')
    def test_prior_CPU_cannot_reset_to_zero(self):
        with mock.patch.object(c,'verify_release',return_value={'prior_CPU_upper_bound_seconds':0}):
            with self.assertRaisesRegex(c.Stop,'PRIOR_CPU'):c.load_admission(c.HERE/'bindings-remaining-preflight.json')
    def test_phase_CPU_and_lock_paths_separate_preserve_old(self):
        with tempfile.TemporaryDirectory(dir=c.HERE) as tmp:
            run=pathlib.Path(tmp)/'runs/recovery';old=pathlib.Path(tmp)/'live-once.lock';old.write_text('PRESERVE_OLD_LOCK')
            with mock.patch.object(c,'RUN_DIR',run):c.stage('WAITING_LOCAL_INPUT')
            row=json.loads((run/'runtime-stage.jsonl').read_text());self.assertEqual(row['status'],'WAITING_LOCAL_INPUT');self.assertIsInstance(row['process_CPU_seconds'],float);self.assertFalse(row['credential_saved']);self.assertEqual(old.read_text(),'PRESERVE_OLD_LOCK')
            with (run/'live-once.lock').open('x') as f:f.write('one')
            with self.assertRaises(FileExistsError):
                with (run/'live-once.lock').open('x'):pass
    def test_new_deadline_expires_before_prompt_or_network(self):
        end=c.dt.datetime(2026,10,20,8,10,50,tzinfo=c.dt.timezone.utc).timestamp()
        with mock.patch.object(c.time,'time',return_value=end+1),mock.patch.object(c,'prompt_endpoint') as prompt,mock.patch.object(c,'load_admission') as load:
            with self.assertRaisesRegex(c.Stop,'DEADLINE'):c.run_live(c.HERE/'bindings-remaining-preflight.json')
            prompt.assert_not_called();load.assert_not_called()
    def test_release_exact_new_run_binding_and_launcher(self):
        b=mock.Mock();b.raw=b'{}'
        with tempfile.TemporaryDirectory(dir=c.HERE) as tmp:
            root=pathlib.Path(tmp);(root/'root').mkdir();path=root/'root/remaining-preflight-release.json'
            r={'status':'RELEASED_READONLY_A_PREFLIGHT','run_id':c.RUN_ID,'bindings_sha256':c.digest(b.raw),'reviewed_code_sha256':{p.name:c.digest(p.read_bytes()) for p in [c.HERE/'readonly_core.py',c.HERE/'readonly_collector.py',c.HERE/'start-A-remaining-preflight.command']}}
            path.write_text(json.dumps(r))
            with mock.patch.object(c,'UNIT',root):
                self.assertEqual(c.verify_release(b)['run_id'],c.RUN_ID)
                r['run_id']='other';path.write_text(json.dumps(r))
                with self.assertRaisesRegex(c.Stop,'BINDING'):c.verify_release(b)
                r['run_id']=c.RUN_ID;r['reviewed_code_sha256']['readonly_collector.py']='0'*64;path.write_text(json.dumps(r))
                with self.assertRaisesRegex(c.Stop,'CODE_HASH'):c.verify_release(b)
    def test_budget_carries_old_usage_and_prebudget_CPU(self):
        b=c.Budget(state={'cu':140,'methods':8,'cpu':6060.125});b.charge(20)
        self.assertEqual((b.cu,b.methods,b.cpu_prior),(160,9,6060.125));self.assertLessEqual(b.cpu_limit,7200)
        text=(c.HERE/'readonly_collector.py').read_text();self.assertIn("b.release['prior_CPU_upper_bound_seconds']+time.process_time()",text)
        tree=ast.parse(text);self.assertNotIn('one_read_diagnostic',[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)])
if __name__=='__main__':unittest.main(verbosity=2)

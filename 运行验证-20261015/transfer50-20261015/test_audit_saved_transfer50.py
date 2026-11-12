"""Audit admission tests use metadata fixtures, never models or market outcomes."""
from contextlib import contextmanager
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('saved_artifact_auditor', HERE/'audit_saved_transfer50.py')
auditor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auditor)


class AdmissionTests(unittest.TestCase):
    @contextmanager
    def work_space(self):
        base = HERE/'audit-admission-tests'
        base.mkdir(exist_ok=True)
        root = Path(tempfile.mkdtemp(prefix='case-',dir=base))
        (root/'results').mkdir()
        with (base/'intermediates.jsonl').open('a') as handle:
            handle.write(json.dumps({'directory':str(root),'purpose':'audit-admission metadata fixtures only',
                                     'retention':'retained software evidence'})+'\n')
        yield root

    def test_live_or_unstarted_run_is_not_audited(self):
        with self.work_space() as root:
            self.assertEqual(auditor.audit(root),3)
            (root/'launch-attempt.json').write_text(json.dumps({'status':'RUNNING'}))
            self.assertEqual(auditor.audit(root),3)
            self.assertFalse((root/'independent-artifact-audit.json').exists())

    def test_terminal_failure_is_incomplete_not_waiting_or_passed(self):
        with self.work_space() as root:
            (root/'launch-attempt.json').write_text(json.dumps({'status':'DEADLINE_STOP','child_exit_code':-9}))
            self.assertEqual(auditor.audit(root),4)
            self.assertFalse((root/'independent-artifact-audit.json').exists())

    def test_normal_exit_with_partial_panel_cannot_be_audited(self):
        with self.work_space() as root:
            (root/'launch-attempt.json').write_text(json.dumps({'status':'CHILD_EXITED','child_exit_code':0}))
            (root/'results/state.json').write_text(json.dumps({'status':'completed'}))
            (root/'results/summary.json').write_text(json.dumps({'complete_panel':False}))
            self.assertFalse(auditor.ready(root))
            self.assertEqual(auditor.audit(root),4)
            self.assertFalse((root/'independent-artifact-audit.json').exists())


if __name__=='__main__':
    unittest.main()

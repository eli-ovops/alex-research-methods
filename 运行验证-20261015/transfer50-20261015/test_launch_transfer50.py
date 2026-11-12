"""Launcher lifecycle tests use toy child processes, never a model."""
import importlib.util
import json
import os
import signal
import subprocess
from contextlib import contextmanager
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location('transfer_launcher', Path(__file__).with_name('launch_transfer50.py'))
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


class DeadlineTests(unittest.TestCase):
    @contextmanager
    def work_space(self):
        base = Path(__file__).parent / 'launcher-software-tests'
        base.mkdir(exist_ok=True)
        root = Path(tempfile.mkdtemp(prefix='case-', dir=base))
        with (base/'intermediates.jsonl').open('a') as manifest:
            manifest.write(json.dumps({'directory':str(root),
                'files':[str(root/'receipt.json'),str(root/'child.log')],
                'purpose':'toy process lifecycle evidence; no model or market data',
                'retention':'retained for test audit'})+'\n')
        yield root

    def test_terminal_child_and_duplicate_attempt_refused(self):
        with self.work_space() as root:
            args = ([sys.executable, '-c', 'print("software-only")'], root,
                    root/'receipt.json', root/'child.log', 5)
            result = launcher.bounded_run(*args, interval=.02)
            self.assertEqual(result['child_exit_code'], 0)
            self.assertEqual(result['status'], 'CHILD_EXITED')
            self.assertIn('software-only', (root/'child.log').read_text())
            with self.assertRaises(FileExistsError):
                launcher.bounded_run(*args, interval=.02)

    def test_deadline_terminates_owned_process(self):
        with self.work_space() as root:
            result = launcher.bounded_run(
                [sys.executable, '-c', 'import time; time.sleep(60)'], root,
                root/'receipt.json', root/'child.log', .15, interval=.04)
            self.assertEqual(result['status'], 'DEADLINE_STOP')
            self.assertLess(result['child_exit_code'], 0)
            self.assertLess(result['wall_seconds'], 3)
            self.assertEqual(json.loads((root/'receipt.json').read_text())['status'], 'DEADLINE_STOP')

    def test_interrupt_during_process_creation_stops_new_child(self):
        with self.work_space() as root:
            original_popen = subprocess.Popen

            def interrupted_creation(*args, **kwargs):
                os.kill(os.getpid(), signal.SIGTERM)
                return original_popen(*args, **kwargs)

            with mock.patch.object(launcher.subprocess, 'Popen', side_effect=interrupted_creation):
                result = launcher.bounded_run(
                    [sys.executable, '-c', 'import time; time.sleep(60)'], root,
                    root/'receipt.json', root/'child.log', 5, interval=.02)
            self.assertEqual(result['status'], 'INTERRUPTED')
            self.assertEqual(result['received_signal'], signal.SIGTERM)
            self.assertLess(result['child_exit_code'], 0)
            self.assertLess(result['wall_seconds'], 1)


if __name__ == '__main__':
    unittest.main()

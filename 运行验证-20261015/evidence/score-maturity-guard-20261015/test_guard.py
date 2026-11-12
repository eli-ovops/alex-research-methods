"""Software-only rejection/constraint tests. No model, market API or scoring run.

Packages below are deliberately constructed test metadata, NOT completion proof.
The existing source metadata is used only to exercise local original/hash checks.
No unmodified synthetic package is submitted to the real CLI for scoring.
"""
import ast
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'score_endpoint_observation.py'
spec = importlib.util.spec_from_file_location('guard_review_only', SCRIPT)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)  # definitions only; __main__ is not invoked


class RejectionTests(unittest.TestCase):
    def setUp(self):
        self.source = ROOT / 'evidence/prospective-readiness-20261015/current-dataset-metadata.json'
        self.original = json.loads(self.source.read_text())
        self.now = datetime.now(timezone.utc)
        self.receipt = {
            'dataset_revision': self.original['sha'],
            'retrieved_at_utc': '2026-10-15T02:12:17.997142+00:00',
        }
        self.obs = {'terminal_bar_start': '2026-10-13T15:30:00-04:00',
                    'terminal_bar_end': '2026-10-13T16:00:00-04:00'}
        self.data_hash = '9aa5e309ab3661c78a0c06b05ae6cc04fdf944eb962a5861c972d81ecf704c73'
        source = {
            'source_url': 'https://huggingface.co/api/datasets/twelvedata/financial-world-model?blobs=true',
            'artifact_path': str(self.source),
            'artifact_sha256': hashlib.sha256(self.source.read_bytes()).hexdigest(),
        }
        # Artificial event/review declarations exercise structure only. They do
        # not assert that the source metadata proves an actual fetch/completion.
        self.package = {
            'dataset_id': 'twelvedata/financial-world-model',
            'dataset_revision': self.receipt['dataset_revision'],
            'relative_file': 'bars_1h/test.parquet', 'data_sha256': self.data_hash,
            'symbol': 'AAPL', 'timeframe': '1h',
            'target_bar_start': self.obs['terminal_bar_start'],
            'target_bar_end': self.obs['terminal_bar_end'],
            'file_publication': dict(source, event_at_utc='2026-10-14T12:08:57+00:00'),
            'completion': dict(source, type='post_end_source_fetch', event_at_utc='2026-10-14T06:00:00+00:00'),
        }
        self.package['independent_review'] = {
            'reviewer': 'SOFTWARE_TEST_NOT_A_REAL_REVIEW',
            'reviewed_at_utc': '2026-10-15T02:13:00+00:00', 'decision': 'accepted',
            'source_content_finding': 'SOFTWARE FIXTURE ONLY: no claim that this source proves completion.',
            'reviewed_payload_sha256': guard.digest(self.package),
        }

    def rejected(self, package=None, receipt=None, obs=None):
        with self.assertRaises((guard.CompletionEvidencePending, KeyError, TypeError, ValueError, AttributeError)):
            guard.validate_completion(self.package if package is None else package,
                self.receipt if receipt is None else receipt,
                self.obs if obs is None else obs, self.data_hash, self.source.parent, self.now)

    def test_download_after_end_does_not_rescue_old_file(self):
        obs = {'terminal_bar_start': '2026-10-14T13:30:00-04:00',
               'terminal_bar_end': '2026-10-14T14:30:00-04:00'}
        p = copy.deepcopy(self.package)
        p.update(target_bar_start=obs['terminal_bar_start'], target_bar_end=obs['terminal_bar_end'])
        self.rejected(p, obs=obs)

    def test_missing_completion(self):
        p = copy.deepcopy(self.package); del p['completion']; self.rejected(p)

    def test_wrong_revision(self):
        p = copy.deepcopy(self.package); p['dataset_revision'] = '0' * 40; self.rejected(p)

    def test_wrong_data_hash(self):
        p = copy.deepcopy(self.package); p['data_sha256'] = '0' * 64; self.rejected(p)

    def test_wrong_target(self):
        p = copy.deepcopy(self.package); p['target_bar_start'] = '2026-10-13T14:30:00-04:00'; self.rejected(p)

    def test_naive_dates_rejected(self):
        for section, field in [('completion', 'event_at_utc'), ('file_publication', 'event_at_utc'),
                               ('independent_review', 'reviewed_at_utc')]:
            with self.subTest(section=section):
                p = copy.deepcopy(self.package); p[section][field] = '2026-10-14T12:00:00'; self.rejected(p)
        receipt = dict(self.receipt, retrieved_at_utc='2026-10-15T02:12:17'); self.rejected(receipt=receipt)

    def test_only_lastmodified_download_successor_or_true_not_supported(self):
        for evidence_type in ['repository_lastModified', 'download_time', 'successor_bar', True]:
            with self.subTest(evidence_type=evidence_type):
                p = copy.deepcopy(self.package); p['completion']['type'] = evidence_type; self.rejected(p)

    def test_source_missing(self):
        p = copy.deepcopy(self.package); p['completion']['artifact_path'] = str(self.source.parent / 'MISSING_SOFTWARE_FIXTURE'); self.rejected(p)

    def test_source_hash_wrong(self):
        p = copy.deepcopy(self.package); p['completion']['artifact_sha256'] = '0' * 64; self.rejected(p)

    def test_review_missing(self):
        p = copy.deepcopy(self.package); del p['independent_review']; self.rejected(p)

    def test_review_true_is_not_substantive_finding(self):
        for v in [True, 'true', '', 'accepted']:
            with self.subTest(value=v):
                p = copy.deepcopy(self.package); p['independent_review']['source_content_finding'] = v; self.rejected(p)

    def test_review_binding_wrong(self):
        p = copy.deepcopy(self.package); p['independent_review']['reviewed_payload_sha256'] = '0' * 64; self.rejected(p)

    def test_future_dated_event_rejected(self):
        p = copy.deepcopy(self.package); p['completion']['event_at_utc'] = '2099-01-01T00:00:00Z'; self.rejected(p)

    def test_aware_time_constraint(self):
        self.assertEqual(guard.aware_time('2026-10-13T16:00:00-04:00'),
                         guard.aware_time('2026-10-13T20:00:00Z'))

    def test_guard_precedes_parquet_read(self):
        source = SCRIPT.read_text(); ast.parse(source)
        self.assertLess(source.index('guard = validate_completion('), source.index('data = pd.read_parquet('))
        self.assertNotIn('torch', sys.modules)


if __name__ == '__main__':
    unittest.main(verbosity=2)

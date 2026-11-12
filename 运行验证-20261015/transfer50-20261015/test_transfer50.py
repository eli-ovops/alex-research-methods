#!/usr/bin/env python3
"""Pure software/QC tests. Synthetic cases are not model or investment evidence."""
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
BASE = HERE.parent
spec = importlib.util.spec_from_file_location("transfer50_adapter_tested", HERE / "evaluate_transfer50.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
import numpy as np
import pandas as pd
import exchange_calendars as xcals


def protocol():
    p = json.loads((BASE / "protocol.json").read_text())
    p.pop("symbol", None)
    p.update(deepcopy(m.FIXED))
    p["adapter_sha256"] = m.file_hash(HERE / "evaluate_transfer50.py")
    p["authorization"] = "Software-only fixture; never execute a model under this fixture"
    return p


def short_protocol():
    p = protocol()
    p.update(symbols=["A", "B"], expected_time_windows=4, expected_records=8)
    p["CI"] = dict(p["CI"], block_length=2, resamples=100)
    return p


def entries(n=4):
    return [{"window_index": i, "last_input": f"history-{i}", "target_timestamps": [f"future-{i}"]} for i in range(n)]


def fixture_rows(p, es, forecasts=None):
    rows = []
    for i, entry in enumerate(es):
        for j, symbol in enumerate(p["symbols"]):
            actual = 110 if j == 0 else 120
            forecast = actual if forecasts is None else forecasts[i][j]
            r, rh = actual/100-1, forecast/100-1
            row = dict(entry, symbol=symbol, seed=m.seed_for(p, symbol, i), p0=100,
                       actual_terminal_close=actual, terminal_close_10sample_mean=forecast,
                       r=r, r_hat=rh, zero_squared_error=r*r,
                       model_squared_error=(rh-r)**2, d=r*r-(rh-r)**2)
            row["record_sha256"] = m.digest_obj(row)
            rows.append(row)
    return rows


def reseal(row):
    row.pop("record_sha256", None)
    row["record_sha256"] = m.digest_obj(row)


class TransferSoftwareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Every temporary file has an owned, retained, task-local path.
        cls.directory = Path(tempfile.mkdtemp(prefix="software-cases-", dir=HERE))

    def temp(self, name):
        return self.directory / (self._testMethodName + "-" + name)

    def test_import_has_no_torch_or_model(self):
        self.assertNotIn("torch", sys.modules)
        self.assertNotIn("model.kronos", sys.modules)

    def test_valid_frozen_protocol(self):
        path = self.temp("protocol.json")
        m.write_json(path, protocol())
        self.assertEqual(m.load_protocol(path)["expected_records"], 9400)

    def test_protocol_rejects_setting_change(self):
        path = self.temp("protocol.json")
        for field, value in [("horizon", 1), ("threads", 7), ("expected_records", 9399), ("max_inference_seconds", 14401),
                             ("symbols", list(reversed(m.SYMBOLS))), ("source_commit", "changed")]:
            p = protocol()
            p[field] = value
            m.write_json(path, p)
            with self.assertRaises(m.StopRun, msg=field):
                m.load_protocol(path)

    def test_protocol_rejects_artifact_and_adapter_change(self):
        path = self.temp("protocol.json")
        for section, key in [("dataset", "sha256"), ("model", "revision"), ("tokenizer", "weights_sha256")]:
            p = protocol()
            p[section][key] = "0"*64
            m.write_json(path, p)
            with self.assertRaises(m.StopRun):
                m.load_protocol(path)
        p = protocol()
        p["adapter_sha256"] = "0"*64
        m.write_json(path, p)
        with self.assertRaises(m.StopRun):
            m.load_protocol(path)

    def test_protocol_rejects_unfrozen_or_unauthorized(self):
        path = self.temp("protocol.json")
        for field, value in [("frozen_at_utc", "2026-10-15T00:00:00"), ("authorization", ""), ("symbol", "AAPL")]:
            p = protocol()
            p[field] = value
            m.write_json(path, p)
            with self.assertRaises(m.StopRun):
                m.load_protocol(path)

    def test_seed_mapping_stable_and_unique(self):
        p = protocol()
        seeds = [m.seed_for(p, s, i) for s in p["symbols"] for i in range(188)]
        self.assertEqual(len(set(seeds)), 9400)
        self.assertEqual(m.seed_for(p, "ABBV", 0), 21261015)
        self.assertEqual(m.seed_for(p, "XOM", 187), 70261202)

    def test_one_attempt_no_resume(self):
        out = self.temp("out")
        m.prepare_out(out, {"experiment": "software-only"}, False)
        self.assertTrue((out / "attempt.json").exists())
        before = (out / "attempt.json").read_bytes()
        with self.assertRaises(m.StopRun):
            m.prepare_out(out, {"experiment": "software-only"}, False)
        self.assertEqual((out / "attempt.json").read_bytes(), before)

    def test_preflight_has_no_attempt(self):
        out = self.temp("out")
        m.prepare_out(out, {"experiment": "software-only"}, True)
        self.assertFalse((out / "attempt.json").exists())

    def test_complete_good_fixture_passes_only_software_gate(self):
        p, es = short_protocol(), entries()
        summary, _, ts = m.summarize(fixture_rows(p, es), p, np, es)
        self.assertTrue(summary["complete_panel"])
        self.assertTrue(summary["gate_passed"])
        self.assertEqual(summary["n_complete_time_windows"], 4)
        self.assertEqual(len(ts), 4)

    def test_complete_bad_fixture_fails(self):
        p, es = short_protocol(), entries()
        summary, _, _ = m.summarize(fixture_rows(p, es, [[80, 80]]*4), p, np, es)
        self.assertFalse(summary["gate_passed"])
        self.assertEqual(summary["status"], "prediction_gate_not_passed")

    def test_time_cross_section_aggregation_and_total_ratio(self):
        p, es = short_protocol(), entries()
        rows = fixture_rows(p, es, [[110, 100], [100, 120], [110, 100], [105, 120]])
        summary, by_symbol, ts = m.summarize(rows, p, np, es)
        direct = [np.mean([rows[2*i]["d"], rows[2*i+1]["d"]]) for i in range(4)]
        np.testing.assert_allclose([r["paired_d_mean"] for r in ts], direct)
        rng = np.random.default_rng(p["CI"]["seed"])
        means = []
        for _ in range(100):
            starts = rng.integers(0, 4, size=2)
            idx = ((starts[:, None] + np.arange(2)) % 4).reshape(-1)[:4]
            means.append(np.array(direct)[idx].mean())
        np.testing.assert_allclose(summary["circular_block_bootstrap_95CI"], np.quantile(means, [.025, .975]))
        z = np.mean([r["zero_squared_error"] for r in rows])
        mm = np.mean([r["model_squared_error"] for r in rows])
        self.assertAlmostEqual(summary["relative_mse_improvement"], (z-mm)/z)
        self.assertNotAlmostEqual(summary["relative_mse_improvement"], np.mean([s["relative_mse_improvement"] for s in by_symbol.values()]))

    def test_chronological_half_must_pass(self):
        p, es = short_protocol(), entries()
        rows = fixture_rows(p, es, [[110, 120], [110, 120], [80, 80], [80, 80]])
        summary, _, _ = m.summarize(rows, p, np, es)
        self.assertLess(summary["chronological_halves_mean_d"][1], 0)
        self.assertFalse(summary["gate_passed"])

    def test_missing_record_never_passes(self):
        p, es = short_protocol(), entries()
        summary, _, ts = m.summarize(fixture_rows(p, es)[:-1], p, np, es)
        self.assertFalse(summary["gate_passed"])
        self.assertFalse(summary["complete_panel"])
        self.assertEqual(summary["n_complete_time_windows"], 3)
        self.assertIsNone(summary["circular_block_bootstrap_95CI"])

    def test_qc_failure_or_termination_never_passes(self):
        p, es = short_protocol(), entries()
        for qc, why in [("STOP", None), ("PASS", {"type": "resource_cap"})]:
            summary, _, _ = m.summarize(fixture_rows(p, es), p, np, es, qc, why)
            self.assertFalse(summary["gate_passed"])
            self.assertEqual(summary["status"], "incomplete")

    def test_duplicate_identity_rejected(self):
        p, es = short_protocol(), entries()
        rows = fixture_rows(p, es)
        rows[-1] = deepcopy(rows[0])
        with self.assertRaises(m.StopRun):
            m.summarize(rows, p, np, es)

    def test_wrong_timestamp_seed_symbol_or_window_rejected(self):
        p, es = short_protocol(), entries()
        for field, value in [("last_input", "wrong"), ("target_timestamps", ["wrong"]), ("seed", 1), ("symbol", "AAPL"), ("window_index", 188)]:
            rows = fixture_rows(p, es)
            rows[0][field] = value
            reseal(rows[0])
            with self.assertRaises(m.StopRun, msg=field):
                m.summarize(rows, p, np, es)

    def test_checksum_and_score_corruption_rejected(self):
        p, es = short_protocol(), entries()
        rows = fixture_rows(p, es)
        rows[0]["d"] = 999
        with self.assertRaises(m.StopRun):
            m.summarize(rows, p, np, es)
        reseal(rows[0])
        with self.assertRaises(m.StopRun):
            m.summarize(rows, p, np, es)

    def test_input_hash_changes_with_history(self):
        helper = m.load_helper(protocol())
        dates = pd.date_range("2025-07-01 09:30", periods=2, freq="h", tz="America/New_York")
        x = pd.DataFrame({"open": [100., 100.], "high": [101., 101.], "low": [99., 99.], "close": [100., 100.]}, index=dates)
        before = helper.input_hash(x)
        x.iloc[0, 0] = 100.5
        self.assertNotEqual(before, helper.input_hash(x))

    def qc_fixture(self, change=None):
        p = short_protocol()
        p.update(context=2, horizon=2, stride=2, expected_time_windows=6, expected_records=12)
        dates = pd.date_range("2025-07-01 09:30", periods=7, freq="h", tz="America/New_York").append(
            pd.date_range("2025-07-02 09:30", periods=7, freq="h", tz="America/New_York"))
        data = pd.DataFrame([{"symbol": s, "datetime": t, "open": 100., "high": 101., "low": 99., "close": 100.} for s in p["symbols"] for t in dates])
        if change:
            data = change(data)
        source = self.temp("data.parquet")
        data.to_parquet(source, index=False)
        out = self.temp("qc")
        out.mkdir(exist_ok=True)
        helper = m.load_helper(protocol())
        from argparse import Namespace
        return m.qc_data(Namespace(data=source), p, out, pd, np, xcals, helper)

    def test_qc_valid_synthetic_grid(self):
        frames, windows, qc = self.qc_fixture()
        self.assertEqual(qc["status"], "PASS")
        self.assertEqual(len(windows), 6)
        self.assertEqual(len(frames), 2)

    def test_qc_duplicate_rejected(self):
        with self.assertRaises(m.StopRun):
            self.qc_fixture(lambda df: pd.concat([df.iloc[:1], df], ignore_index=True))

    def test_qc_missing_common_row_rejected(self):
        with self.assertRaises(m.StopRun):
            self.qc_fixture(lambda df: df.loc[~df["datetime"].eq(df["datetime"].iloc[1])])

    def test_qc_invalid_price_rejected(self):
        def change(df):
            df.loc[0, "low"] = 102
            return df
        with self.assertRaises(m.StopRun):
            self.qc_fixture(change)

    def test_qc_naive_time_rejected(self):
        def change(df):
            df["datetime"] = df["datetime"].dt.tz_localize(None)
            return df
        with self.assertRaises(m.StopRun):
            self.qc_fixture(change)

    def test_actual_data_preflight_no_model_import_or_prediction(self):
        p = protocol()
        path = self.temp("protocol.json")
        m.write_json(path, p)
        out = self.temp("preflight")
        cmd = [sys.executable, str(HERE / "evaluate_transfer50.py"), "--protocol", str(path),
               "--data", str(BASE / "data/hourly.parquet"), "--source-root", str(BASE / "vendor/Kronos"),
               "--model-dir", str(BASE / "weights/small"), "--tokenizer-dir", str(BASE / "weights/tokenizer"),
               "--out", str(out), "--preflight"]
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        (self.temp("preflight-stdout.txt")).write_text(process.stdout)
        (self.temp("preflight-stderr.txt")).write_text(process.stderr)
        self.assertEqual(process.returncode, 0, process.stderr)
        receipt = json.loads((out / "preflight.json").read_text())
        self.assertEqual(receipt["common_time_windows"], 188)
        self.assertEqual(receipt["symbols"], 50)
        self.assertEqual(receipt["planned_records"], 9400)
        self.assertFalse(receipt["model_imported"])
        self.assertFalse(receipt["torch_imported"])
        self.assertFalse((out / "predictions.jsonl").exists())
        self.assertFalse((out / "attempt.json").exists())


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TransferSoftwareTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    receipt = {"generated_at_utc": m.utc_now(), "status": "PASS" if result.wasSuccessful() else "FAIL",
               "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
               "adapter_sha256": m.file_hash(HERE / "evaluate_transfer50.py"),
               "test_sha256": m.file_hash(__file__), "model_predictions_generated": 0,
               "torch_imported_in_test_process": "torch" in sys.modules,
               "synthetic_cases": "software constraints only; not predictive/financial evidence",
               "test_intermediate_directory": str(TransferSoftwareTests.directory),
               "temporary_file_policy": "retained as reproducible test evidence; no original assets changed"}
    m.write_json(HERE / "software-test-receipt.json", receipt)
    sys.exit(0 if result.wasSuccessful() else 1)

#!/usr/bin/env python3
"""Human-checkable, in-memory accounting tests, not strategy-performance evidence."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import importlib.util
import io
import math
from pathlib import Path
import sys
import time
import unittest

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("economic_adapter_under_test", HERE / "replay_economics.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
import numpy as np
import pandas as pd
import exchange_calendars as xcals


def toy_market(n=1, count=10):
    # All timestamps/prices/signals below are synthetic software fixtures.
    symbols = [f"S{i:02}" for i in range(count)]
    times = [datetime(2025, 7, 1, 9, 30, tzinfo=timezone.utc)+timedelta(hours=i) for i in range(n+3)]
    return {"symbols": symbols, "times": times, "bar_end_times": [t+timedelta(hours=1) for t in times],
            "opens": [{s: 100. for s in symbols} for _ in times],
            "closes": [{s: 100. for s in symbols} for _ in times],
            "rebalance_indices": list(range(1, n+1)), "final_index": n+1,
            "scores": [{s: -i for i, s in enumerate(symbols)} for _ in range(n)]}


class AccountingTests(unittest.TestCase):
    def test_no_model_imports(self):
        self.assertNotIn("torch", sys.modules)
        self.assertNotIn("model.kronos", sys.modules)

    def test_negative_signal_still_selects_top_and_ties_by_symbol(self):
        self.assertEqual(m.rank_top({"Z": -1, "B": -1, "A": -1, "C": -3}, 2), ["A", "B"])

    def test_flat_two_asset_ledger_commission(self):
        cash, positions, rows, event = m.trade_event(5000., {"A": 0., "B": 0.}, {"A": 100., "B": 100.}, ["A", "B"], 1, 0)
        self.assertEqual(positions, {"A": 23.75, "B": 23.75})
        self.assertEqual(cash, 248.)
        self.assertEqual(event["posttrade_nav"], 4998.)
        cash, positions, rows, event = m.trade_event(cash, positions, {"A": 100., "B": 100.}, [], 1, 0, True)
        self.assertEqual(cash, 4996.)
        self.assertEqual(positions, {"A": 0., "B": 0.})
        self.assertEqual(event["fee_order_count"], 2)

    def test_flat_two_asset_slippage_and_cash_identity(self):
        cash, positions, rows, event = m.trade_event(5000., {"A": 0., "B": 0.}, {"A": 100., "B": 100.}, ["A", "B"], 1, 5)
        self.assertAlmostEqual(cash, 245.625)
        self.assertAlmostEqual(event["slippage_USD"], 2.375)
        self.assertAlmostEqual(event["posttrade_nav"], 4995.625)
        self.assertTrue(all(row["fill_price"] == 100.05 for row in rows))
        cash, positions, rows, event = m.trade_event(cash, positions, {"A": 100., "B": 100.}, [], 1, 5, True)
        self.assertAlmostEqual(cash, 4991.25)
        self.assertTrue(all(row["fill_price"] == 99.95 for row in rows))

    def test_one_asset_trend_continuous_hold(self):
        cash, positions, _, _ = m.trade_event(5000., {"A": 0.}, {"A": 100.}, ["A"], 0, 0)
        self.assertEqual(cash, 250.)
        self.assertEqual(positions["A"], 47.5)
        self.assertEqual(m.mark_nav(cash, positions, {"A": 110.}), 5475.)
        cash, positions, rows, event = m.trade_event(cash, positions, {"A": 110.}, ["A"], 0, 0)
        self.assertAlmostEqual(event["pretrade_nav"], 5475.)
        self.assertEqual(rows[0]["side"], "sell")
        cash, _, _, _ = m.trade_event(cash, positions, {"A": 110.}, [], 0, 0, True)
        self.assertAlmostEqual(cash, 5475.)

    def test_independent_decimal_reference_one_asset_main_cost(self):
        # Root's separate Decimal calculation: 5000,95%,100->110,$1,5bps.
        cash, positions, rows, first = m.trade_event(5000., {"A": 0.}, {"A": 100.}, ["A"], 1, 5)
        self.assertAlmostEqual(first["posttrade_nav"], 4996.625)
        pre_exit = m.mark_nav(cash, positions, {"A": 110.})
        cash, positions, rows, last = m.trade_event(cash, positions, {"A": 110.}, [], 1, 5, True)
        self.assertAlmostEqual(cash, 5468.0125)
        samples = [{"NAV": n} for n in [5000., first["posttrade_nav"], pre_exit, cash]]
        self.assertAlmostEqual(m.drawdown(samples)["maximum_drawdown_fraction"], .000675)

    def test_mixed_dst_offset_targets_are_same_instants(self):
        targets = m.parse_targets(["2025-10-31T15:30:00-04:00", "2025-11-03T09:30:00-05:00"], pd)
        self.assertEqual(targets[0].utcoffset(), timedelta(hours=-4))
        self.assertEqual(targets[1].utcoffset(), timedelta(hours=-5))
        self.assertLess(targets[0], targets[1])

    def test_net_sell_precedes_buy_even_reverse_alphabetical(self):
        cash, positions, rows, _ = m.trade_event(0., {"A": 0., "Z": 10.}, {"A": 100., "Z": 100.}, ["A"], 1, 0)
        self.assertEqual([(r["symbol"], r["side"]) for r in rows], [("Z", "sell"), ("A", "buy")])
        self.assertEqual(cash, 48.)
        self.assertEqual(positions, {"A": 9.5, "Z": 0.})
        self.assertTrue(all(r["cash_after"] >= 0 for r in rows))

    def test_unchanged_position_no_roundtrip_fee(self):
        cash, positions, rows, event = m.trade_event(250., {"A": 47.5}, {"A": 100.}, ["A"], 1, 10)
        self.assertEqual(rows, [])
        self.assertEqual(cash, 250.)
        self.assertEqual(event["fee_order_count"], 0)

    def test_cash_infeasible_is_atomic_and_not_resized(self):
        old = {"A": 0.}
        with self.assertRaises(m.InfeasibleCash) as context:
            m.trade_event(5., old, {"A": 100.}, ["A"], 1, 0)
        self.assertEqual(old, {"A": 0.})
        self.assertFalse(context.exception.details["state_changed"])
        self.assertAlmostEqual(context.exception.details["projected_cash_after"], -.75)
        self.assertAlmostEqual(context.exception.details["desired_stock_notional_before_costs"], 4.75)

    def test_epsilon_only_suppresses_fee_and_count_not_math(self):
        cash, positions, rows, event = m.trade_event(5., {"A": 5e-11}, {"A": 100.}, [], 2, 5, True)
        self.assertEqual(positions["A"], 0.)
        self.assertEqual(event["fee_order_count"], 0)
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["epsilon_suppressed_fee"])
        self.assertEqual(rows[0]["commission_USD"], 0)
        self.assertGreater(rows[0]["slippage_USD"], 0)
        self.assertGreater(cash, 5.)
        cash, _, rows, event = m.trade_event(5., {"A": 2e-10}, {"A": 100.}, [], 2, 5, True)
        self.assertEqual(event["fee_order_count"], 1)
        self.assertEqual(rows[0]["commission_USD"], 2.)

    def test_final_fee_in_W_and_sampled_drawdown(self):
        result = m.simulate_scenario(toy_market(), 1, 0)
        self.assertEqual(result["W"], [5000., 4980.])
        self.assertEqual(result["summary"]["fee_order_count"], 20)
        self.assertAlmostEqual(result["summary"]["drawdown"]["maximum_drawdown_fraction"], .004)
        self.assertEqual(result["NAV_samples"][-1]["event"], "final_posttrade")
        self.assertEqual(result["NAV_samples"][-1]["cash"], 4980.)
        self.assertEqual(result["NAV_samples"][-1]["stock_value"], 0.)

    def test_simulation_infeasible_case_retained(self):
        result = m.simulate_scenario(toy_market(), 1000, 0)
        self.assertEqual(result["summary"]["status"], "infeasible")
        self.assertFalse(result["summary"]["complete"])
        self.assertIsNone(result["summary"]["final_post_liquidation_cash_USD"])
        self.assertEqual(result["orders"], [])
        self.assertIsNone(result["window_log_returns"])

    def test_close_before_same_time_open_trade_and_no_post_exit_close(self):
        market = toy_market(2)
        market["closes"][market["final_index"]] = {s: .0001 for s in market["symbols"]}
        result = m.simulate_scenario(market, 0, 0)
        finish = market["times"][market["final_index"]]
        self.assertTrue(all(datetime.fromisoformat(r["timestamp"]) <= finish for r in result["NAV_samples"]))
        at_second = [r["event"] for r in result["NAV_samples"] if datetime.fromisoformat(r["timestamp"]) == market["times"][2]]
        self.assertEqual(at_second, ["hour_close", "rebalance_pretrade", "rebalance_posttrade"])
        self.assertEqual(result["summary"]["final_post_liquidation_cash_USD"], 5000.)

    def test_real_calendar_normal_and_half_day_last_bar_ends(self):
        for date, periods, expected_end in [("2025-07-01", 7, "16:00"), ("2025-11-28", 4, "13:00")]:
            times = pd.date_range(date+" 09:30", periods=periods, freq="h", tz="America/New_York")
            grid, ends = m.calendar_clock(times, pd, xcals)
            self.assertEqual(len(grid), periods)
            self.assertEqual(ends[times[-1]].strftime("%H:%M"), expected_end)
            self.assertEqual(ends[times[-1]].date(), times[-1].date())

    def test_half_boundary_continuity_and_log_telescope(self):
        market = toy_market(188)
        result = m.simulate_scenario(market, 1, 0)
        reference = m.simulate_scenario(market, 0, 0, benchmark=True)
        self.assertEqual(len(result["W"]), 189)
        self.assertAlmostEqual(result["W"][94], 4060.)
        self.assertAlmostEqual(result["W"][-1], 3110.)
        self.assertAlmostEqual(math.fsum(result["window_log_returns"]), math.log(3110/5000))
        m.compare_with_benchmark(result, reference, np)
        halves = result["summary"]["chronological_halves"]
        self.assertEqual(halves[0]["end_NAV"], halves[1]["start_NAV"])
        self.assertAlmostEqual(halves[0]["hypothetical_price_NAV_return"], 4060/5000-1)
        self.assertAlmostEqual(halves[1]["hypothetical_price_NAV_return"], 3110/4060-1)
        self.assertFalse(halves[1]["capital_reset"])

    def test_bootstrap_uses_188_time_window_excesses(self):
        market = toy_market(188)
        result = m.simulate_scenario(market, 1, 0)
        reference = m.simulate_scenario(market, 0, 0, benchmark=True)
        m.compare_with_benchmark(result, reference, np)
        excess = np.array(result["window_log_returns"])-np.array(reference["window_log_returns"])
        rng, means = np.random.default_rng(20261015), []
        for _ in range(5000):
            starts = rng.integers(0, 188, size=19)
            idx = ((starts[:, None]+np.arange(10)) % 188).reshape(-1)[:188]
            means.append(excess[idx].mean())
        np.testing.assert_allclose(result["summary"]["excess_log_95CI"], np.quantile(means, [.025, .975]))
        self.assertEqual(len(result["paired_window_excess_log_returns"]), 188)
        self.assertAlmostEqual(math.fsum(result["paired_window_excess_log_returns"]), math.log(result["summary"]["relative_wealth"]))

    def test_decision_required_cases_no_cherry_pick(self):
        summary = {"complete": True, "relative_wealth": 1.1, "hypothetical_net_dollar_change": 10.,
                   "excess_log_95CI": [.001, .002], "chronological_halves": [{"excess_log_return": .01}, {"excess_log_return": .02}]}
        cases = {f"commission{c}_slippage{s}bps": {"summary": deepcopy(summary)} for c in [0, 1, 2] for s in [0, 5, 10]}
        self.assertEqual(m.decision(cases)["status"], "candidate_only")
        cases["commission1_slippage5bps"]["summary"]["relative_wealth"] = .99
        self.assertEqual(m.decision(cases)["status"], "failed_candidate")
        cases["commission1_slippage5bps"]["summary"]["relative_wealth"] = 1.1
        cases["commission0_slippage5bps"]["summary"]["complete"] = False
        self.assertEqual(m.decision(cases)["status"], "candidate_only")
        cases["commission2_slippage10bps"]["summary"]["complete"] = False
        self.assertEqual(m.decision(cases)["status"], "inconclusive")
        cases["commission1_slippage5bps"]["summary"]["relative_wealth"] = .99
        self.assertEqual(m.decision(cases)["status"], "failed_candidate")

    def test_deadline_is_terminal_without_retry(self):
        with self.assertRaises(m.StopReplay):
            m.check_clock(time.monotonic()-1)
        with self.assertRaises(m.StopReplay):
            m.simulate_scenario(toy_market(), 0, 0, deadline=time.monotonic()-1)


if __name__ == "__main__":
    log = io.StringIO()
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(AccountingTests))
    output = log.getvalue()
    (HERE / "unit-test-stdout.txt").write_text(output, encoding="utf-8")
    print(output, end="")
    m.write_json(HERE / "unit-test-receipt.json", {"generated_at_utc": m.utc_now(),
        "status": "PASS" if result.wasSuccessful() else "FAIL", "tests_run": result.testsRun,
        "failures": len(result.failures), "errors": len(result.errors), "adapter_sha256": m.file_hash(HERE / "replay_economics.py"),
        "test_sha256": m.file_hash(__file__), "stdout_sha256": m.file_hash(HERE / "unit-test-stdout.txt"),
        "real_replay_started": False, "real_strategy_returns_calculated": False,
        "model_imported": "torch" in sys.modules or "model.kronos" in sys.modules,
        "fixture_scope": "in-memory hand-checkable synthetic arithmetic only; no predictive or financial evidence",
        "created_test_files": [str(HERE / "unit-test-stdout.txt"), str(HERE / "unit-test-receipt.json")]})
    sys.exit(0 if result.wasSuccessful() else 1)

#!/usr/bin/env python3
"""Fixed, private, offline arithmetic replay of already sealed forecasts.

This is an exploratory calculation on supplied historical prices. No model is
imported, no signal is regenerated, and no trade/account/network operation exists.
--preflight checks identities and event coverage without calculating portfolio
returns. --run consumes exactly one local attempt, including failed attempts.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time

for _variable in ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
                  "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS"]:
    os.environ[_variable] = "1"
os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", HF_DATASETS_OFFLINE="1",
                  HF_HUB_DISABLE_TELEMETRY="1", DO_NOT_TRACK="1")
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
PROTOCOL_SHA256 = "eaf5c13a9875564baad4bd52e92150ce50aa04b6032546444a09a10f0dc78779"
EPS_SHARES = 1e-10
CASH_ROUNDING_TOLERANCE_USD = 1e-8
SYMBOLS = ["ABBV", "ADBE", "AMD", "AMZN", "AVGO", "BA", "BAC", "BLK", "BRK.B", "CAT", "COP", "COST", "CRM", "CSCO", "CVX", "DIS", "GE", "GOOGL", "GS", "HD", "JNJ", "JPM", "KO", "LIN", "LLY", "MA", "MCD", "META", "MRK", "MS", "MSFT", "NFLX", "NKE", "NVDA", "ORCL", "PEP", "PFE", "PG", "RTX", "SBUX", "T", "TMO", "TMUS", "TSLA", "UNH", "V", "VZ", "WFC", "WMT", "XOM"]
LIMITS = [
    "Exploratory reuse of outcomes already inspected; neither unseen nor prospective confirmation.",
    "Original FAILED predictive MSE gate remains FAILED; this is a different hypothesis.",
    "Conditional mathematical accounting on frozen supplier open/close price series only.",
    "OHLC corporate-action adjustment, volume units and cross-timeframe price basis remain unresolved; no total-return claim.",
    "No reconstructed historical publication latency, bid/ask, available size, full fills, spread or market impact evidence.",
    "Slippage and commission are hypothetical fixed assumptions, not verified uSMART charges.",
    "Fractional units, contemporaneous open sizing and full proxy fills are mathematical assumptions, not demonstrated account capabilities.",
    "One-bar delay is an allowance, not proof that all signals/prices were available by the trading clock.",
    "Hourly-close and event-sampled drawdown excludes unobserved intrabar risk and actual account behavior.",
    "No taxes, dividends, interest, FX, borrow, production data rights, actual profit, exact capacity or wealth inference."]


class StopReplay(RuntimeError):
    pass


class InfeasibleCash(StopReplay):
    def __init__(self, details):
        super().__init__("Frozen target trades and costs exceed available cash; no scaling/leverage permitted")
        self.details = details


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def digest_obj(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(4*1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, value):
    path = Path(path)
    temp = path.with_name(path.name + ".tmp")
    with temp.open("w", encoding="utf-8") as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    temp.replace(path)


def write_jsonl(path, rows):
    path = Path(path)
    with path.open("x", encoding="utf-8") as stream:
        for row in rows:
            stream.write(canonical(row) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def forbid_network():
    def audit(event, args):
        if event in {"socket.connect", "socket.connect_ex", "socket.getaddrinfo", "socket.sendto", "socket.bind"}:
            raise StopReplay("Network operation forbidden: " + event)
    sys.addaudithook(audit)


def check_clock(deadline):
    if time.monotonic() >= deadline:
        raise StopReplay("Frozen work/calculation deadline reached; partial results cannot pass")


def load_authorization(protocol_path, authorization_path):
    if file_hash(protocol_path) != PROTOCOL_SHA256:
        raise StopReplay("Frozen protocol byte hash mismatch")
    p = json.loads(Path(protocol_path).read_text(encoding="utf-8"))
    auth = json.loads(Path(authorization_path).read_text(encoding="utf-8"))
    if auth.get("proposal_sha256") != PROTOCOL_SHA256 or auth.get("source") != "direct human reply in this conversation":
        raise StopReplay("Authorization is not tied to the frozen direct-human proposal")
    if auth.get("question_call_id") != "call_3a7bf8ebf3604370ada26d482f260aeb" or auth.get("answer") != "允许 。继续":
        raise StopReplay("Human authorization reference mismatch")
    deadline = datetime.fromisoformat(auth["work_deadline_utc"])
    if deadline.tzinfo is None or deadline.utcoffset().total_seconds() != 0:
        raise StopReplay("Work deadline must be timezone-aware UTC")
    if datetime.now(timezone.utc) >= deadline:
        raise StopReplay("Authorized four-hour work budget has expired")
    return p, auth, deadline


def rank_top(scores, count):
    if not 0 < count <= len(scores) or any(not math.isfinite(float(v)) for v in scores.values()):
        raise StopReplay("Invalid fixed signal universe/ranking")
    return sorted(scores, key=lambda symbol: (-float(scores[symbol]), symbol))[:count]


def parse_targets(values, pd):
    # A forecast spanning a DST weekend can contain both -04:00 and -05:00.
    return pd.to_datetime(values, utc=True).tz_convert("America/New_York")


def mark_nav(cash, positions, prices):
    if not math.isfinite(cash) or cash < -CASH_ROUNDING_TOLERANCE_USD:
        raise StopReplay("Invalid negative/nonfinite cash")
    for symbol, quantity in positions.items():
        if not math.isfinite(quantity) or quantity < 0 or not math.isfinite(prices[symbol]) or prices[symbol] <= 0:
            raise StopReplay("Invalid long-only position or valuation price")
    return cash + math.fsum(positions[s] * prices[s] for s in positions)


def trade_event(cash, positions, prices, selected, commission, slippage_bps, liquidate=False):
    """Atomic sell-first/buy-second net rebalance with no cash-buffer optimization."""
    before = mark_nav(cash, positions, prices)
    if before <= 0 or commission < 0 or not 0 <= slippage_bps < 10000:
        raise StopReplay("Invalid NAV or frozen cost inputs")
    if not liquidate and (not selected or len(selected) != len(set(selected)) or not set(selected).issubset(positions)):
        raise StopReplay("Invalid target universe")
    notional = 0 if liquidate else .95 * before / len(selected)
    target = {s: notional / prices[s] if s in selected and not liquidate else 0.0 for s in positions}
    slippage = slippage_bps / 10000
    changes = [(s, target[s]-positions[s]) for s in positions if target[s] != positions[s]]
    changes.sort(key=lambda item: (0 if item[1] < 0 else 1, item[0]))
    plan, flows = [], []
    for symbol, delta in changes:
        side = "sell" if delta < 0 else "buy"
        fill = prices[symbol] * (1-slippage if side == "sell" else 1+slippage)
        fee_eligible = abs(delta) > EPS_SHARES
        fee = float(commission) if fee_eligible else 0.0
        flow = -delta*fill-fee
        flows.append(flow)
        plan.append({"symbol": symbol, "side": side, "net_quantity_change": delta,
                     "quantity": abs(delta), "position_before": positions[symbol], "position_after": target[symbol],
                     "proxy_open": prices[symbol], "fill_price": fill,
                     "proxy_notional": abs(delta)*prices[symbol], "fill_notional": abs(delta)*fill,
                     "commission_USD": fee, "slippage_USD": abs(delta)*prices[symbol]*slippage,
                     "fee_order_counted": fee_eligible, "epsilon_suppressed_fee": not fee_eligible,
                     "cash_flow": flow})
    projected_cash = math.fsum([cash] + flows)
    if projected_cash < -CASH_ROUNDING_TOLERANCE_USD:
        raise InfeasibleCash({"pretrade_nav": before, "cash_before": cash,
                              "projected_cash_after": projected_cash,
                              "desired_stock_notional_before_costs": 0 if liquidate else .95*before,
                              "planned_commission_USD": math.fsum(r["commission_USD"] for r in plan),
                              "planned_slippage_USD": math.fsum(r["slippage_USD"] for r in plan),
                              "planned_changes": len(plan), "state_changed": False})
    working_cash = cash
    prefix = []
    for row in plan:
        row["cash_before"] = working_cash
        prefix.append(row["cash_flow"])
        working_cash = math.fsum([cash] + prefix)
        if working_cash < -CASH_ROUNDING_TOLERANCE_USD:
            raise StopReplay("Sell-first/buy-second cash prefix unexpectedly negative")
        row["cash_after"] = max(0.0, working_cash)
    rounding = max(0.0, -projected_cash)
    after_cash = max(0.0, projected_cash)
    after_positions = dict(target)
    after = mark_nav(after_cash, after_positions, prices)
    costs = math.fsum(r["commission_USD"] + r["slippage_USD"] for r in plan)
    if not math.isclose(after, before-costs+rounding, rel_tol=1e-12, abs_tol=1e-8):
        raise StopReplay("Rebalance accounting fails pre-NAV minus explicit costs identity")
    if liquidate and (any(q != 0 for q in after_positions.values()) or after != after_cash):
        raise StopReplay("Final liquidation does not end in cash only")
    event = {"pretrade_nav": before, "posttrade_nav": after, "cash_before": cash, "cash_after": after_cash,
             "stock_value_after": after-after_cash, "stock_exposure_after": (after-after_cash)/after,
             "commission_USD": math.fsum(r["commission_USD"] for r in plan),
             "slippage_USD": math.fsum(r["slippage_USD"] for r in plan),
             "gross_proxy_turnover_USD": math.fsum(r["proxy_notional"] for r in plan),
             "gross_proxy_turnover_fraction_of_pretrade_nav": math.fsum(r["proxy_notional"] for r in plan)/before,
             "fee_order_count": sum(r["fee_order_counted"] for r in plan), "ledger_net_changes": len(plan),
             "epsilon_share_threshold": EPS_SHARES, "cash_rounding_correction_USD": rounding,
             "selected_symbols": list(selected), "liquidation": liquidate, "positions_after": after_positions}
    return after_cash, after_positions, plan, event


def drawdown(samples):
    peak, maximum = None, 0.0
    trough, prior_peak = None, None
    for index, row in enumerate(samples):
        value = row["NAV"]
        if not math.isfinite(value) or value <= 0:
            raise StopReplay("Nonpositive/nonfinite sampled NAV cannot support log-return accounting")
        if peak is None or value > peak:
            peak, peak_index = value, index
        decline = 1-value/peak
        if decline > maximum:
            maximum, trough, prior_peak = decline, index, peak_index
    return {"maximum_drawdown_fraction": maximum, "peak_sample_index": prior_peak,
            "trough_sample_index": trough, "sample_count": len(samples),
            "scope": "initial, hourly-close, pre/post-rebalance and terminal liquidation samples only"}


def build_event_clock(market):
    times = market["times"]
    start, finish = times[market["rebalance_indices"][0]], times[market["final_index"]]
    events = [(start, 0, "initial", -1, None)]
    for i, end in enumerate(market["bar_end_times"]):
        if start <= end <= finish:
            events.append((end, 10, "hour_close", i, None))
    for window, index in enumerate(market["rebalance_indices"]):
        events.append((times[index], 20, "rebalance", index, window))
    events.append((finish, 20, "liquidate", market["final_index"], len(market["rebalance_indices"])))
    events.sort(key=lambda item: (item[0], item[1], item[3]))
    return events


def calendar_clock(times, pd, xcals):
    """Exact session close for short final bars; never use next-day open as close."""
    first_date, last_date = times[0].date(), times[-1].date()
    cal = xcals.get_calendar("XNYS", start=(first_date-timedelta(days=1)).isoformat(),
                             end=(last_date+timedelta(days=1)).isoformat())
    expected, end_by_start = [], {}
    for session in cal.sessions_in_range(first_date.isoformat(), last_date.isoformat()):
        opening = pd.Timestamp(cal.session_open(session)).tz_convert("America/New_York")
        close = pd.Timestamp(cal.session_close(session)).tz_convert("America/New_York")
        for timestamp in pd.date_range(opening, close, freq="h", inclusive="left"):
            expected.append(timestamp)
            end_by_start[timestamp] = min(timestamp+pd.Timedelta(hours=1), close)
    grid = pd.DatetimeIndex(expected)
    return grid[grid <= times[-1]], end_by_start


def simulate_scenario(market, commission, slippage_bps, benchmark=False, deadline=None):
    symbols = market["symbols"]
    cash, positions = 5000.0, {s: 0.0 for s in symbols}
    samples, orders, rebalances, W = [], [], [], []
    status, infeasible = "completed", None
    for timestamp, priority, kind, index, window in build_event_clock(market):
        if deadline is not None:
            check_clock(deadline)
        if kind == "initial":
            samples.append({"timestamp": timestamp.isoformat(), "event": "initial", "priority": 0,
                            "NAV": cash, "cash": cash, "stock_value": 0.0})
            continue
        prices = market["closes"][index] if kind == "hour_close" else market["opens"][index]
        nav = mark_nav(cash, positions, prices)
        if kind == "hour_close":
            samples.append({"timestamp": timestamp.isoformat(), "bar_start": market["times"][index].isoformat(),
                            "event": "hour_close", "priority": 10, "NAV": nav, "cash": cash,
                            "stock_value": nav-cash, "source_bar_index": index})
            continue
        liquidate = kind == "liquidate"
        samples.append({"timestamp": timestamp.isoformat(), "event": "final_pretrade" if liquidate else "rebalance_pretrade",
                        "priority": 20, "window_index": window, "NAV": nav, "cash": cash, "stock_value": nav-cash})
        if not liquidate:
            W.append(nav)
        selected = [] if liquidate else list(symbols) if benchmark else rank_top(market["scores"][window], 10)
        try:
            new_cash, new_positions, plan, event = trade_event(cash, positions, prices, selected,
                commission, slippage_bps, liquidate)
        except InfeasibleCash as exc:
            status = "infeasible"
            infeasible = dict(exc.details, timestamp=timestamp.isoformat(), window_index=window, liquidation=liquidate)
            break
        for row in plan:
            row.update(timestamp=timestamp.isoformat(), window_index=window, liquidation=liquidate,
                       ledger_index=len(orders))
            orders.append(row)
        cash, positions = new_cash, new_positions
        event.update(timestamp=timestamp.isoformat(), window_index=window, source_bar_index=index)
        rebalances.append(event)
        samples.append({"timestamp": timestamp.isoformat(), "event": "final_posttrade" if liquidate else "rebalance_posttrade",
                        "priority": 30, "window_index": window, "NAV": event["posttrade_nav"],
                        "cash": cash, "stock_value": event["stock_value_after"]})
        if liquidate:
            W.append(cash)
    n = len(market["rebalance_indices"])
    complete = status == "completed" and len(W) == n+1 and len(rebalances) == n+1
    if not complete:
        status = "infeasible" if status == "infeasible" else "incomplete"
    logs = [math.log(W[i+1]/W[i]) for i in range(n)] if complete else None
    if complete and not math.isclose(math.fsum(logs), math.log(cash/5000), rel_tol=1e-12, abs_tol=1e-12):
        raise StopReplay("Window log returns do not telescope to final post-liquidation cash")
    # ISO offsets can change at DST. Compare actual instants, never strings.
    for previous, current in zip(samples, samples[1:]):
        if (datetime.fromisoformat(previous["timestamp"]), previous["priority"]) > (datetime.fromisoformat(current["timestamp"]), current["priority"]):
            raise StopReplay("Valuation events are not chronological")
    summary = {"status": status, "complete": complete, "benchmark": benchmark,
               "commission_USD_per_changed_stock": commission, "slippage_bps_per_side": slippage_bps,
               "initial_notional_USD": 5000.0, "final_post_liquidation_cash_USD": cash if complete else None,
               "hypothetical_net_dollar_change": cash-5000 if complete else None,
               "hypothetical_price_NAV_return": cash/5000-1 if complete else None,
               "commission_total_USD": math.fsum(r["commission_USD"] for r in orders),
               "slippage_total_USD": math.fsum(r["slippage_USD"] for r in orders),
               "fee_order_count": sum(r["fee_order_counted"] for r in orders), "ledger_net_changes": len(orders),
               "gross_proxy_turnover_total_USD": math.fsum(r["proxy_notional"] for r in orders),
               "mean_rebalance_gross_proxy_turnover_fraction": math.fsum(r["gross_proxy_turnover_fraction_of_pretrade_nav"] for r in rebalances[:-1])/n if complete else None,
               "infeasibility": infeasible, "drawdown": drawdown(samples), "limits": LIMITS}
    return {"summary": summary, "W": W, "window_log_returns": logs, "orders": orders,
            "rebalance_events": rebalances, "NAV_samples": samples}


def compare_with_benchmark(result, benchmark, np, deadline=None):
    summary = result["summary"]
    if not summary["complete"] or not benchmark["summary"]["complete"]:
        summary.update(relative_wealth=None, excess_log_return=None, excess_log_95CI=None,
                       chronological_halves=None, paired_window_excess_log_returns=None)
        return
    logs, base_logs = result["window_log_returns"], benchmark["window_log_returns"]
    if len(logs) != 188 or len(base_logs) != 188:
        raise StopReplay("Real benchmark comparison requires original188 continuous windows")
    excess = np.array(logs)-np.array(base_logs)
    rng = np.random.default_rng(20261015)
    means = np.empty(5000)
    offsets = np.arange(10)
    for b in range(5000):
        if deadline is not None and b % 100 == 0:
            check_clock(deadline)
        starts = rng.integers(0, 188, size=math.ceil(188/10))
        indices = ((starts[:, None]+offsets) % 188).reshape(-1)[:188]
        means[b] = excess[indices].mean()
    halves = []
    for left, right in [(0, 94), (94, 188)]:
        wealth = result["W"][right]/result["W"][left]
        base_wealth = benchmark["W"][right]/benchmark["W"][left]
        half_excess = math.fsum(logs[left:right])-math.fsum(base_logs[left:right])
        halves.append({"intervals_start_inclusive": left, "intervals_end_exclusive": right,
                       "start_NAV": result["W"][left], "end_NAV": result["W"][right],
                       "hypothetical_price_NAV_return": wealth-1,
                       "benchmark_price_NAV_return": base_wealth-1,
                       "relative_wealth": wealth/base_wealth, "excess_log_return": half_excess,
                       "capital_reset": False})
    relative = result["W"][-1]/benchmark["W"][-1]
    if not math.isclose(math.fsum(excess.tolist()), math.log(relative), abs_tol=1e-12, rel_tol=1e-12):
        raise StopReplay("Paired excess logs do not close to relative terminal wealth")
    summary.update(relative_wealth=relative, excess_log_return=math.log(relative),
                   mean_window_excess_log_return=float(excess.mean()),
                   excess_log_95CI=np.quantile(means, [.025, .975]).tolist(),
                   CI_unit="mean paired excess log return per original synchronous window",
                   bootstrap={"method": "circular synchronous time-window blocks", "block_length": 10,
                              "resamples": 5000, "confidence": .95, "seed": 20261015, "exploratory_only": True},
                   chronological_halves=halves)
    result["paired_window_excess_log_returns"] = excess.tolist()


def decision(cases):
    main, gross, stress = cases["commission1_slippage5bps"]["summary"], cases["commission0_slippage0bps"]["summary"], cases["commission2_slippage10bps"]["summary"]
    if ((gross["complete"] and gross["relative_wealth"] <= 1)
            or (main["complete"] and (main["hypothetical_net_dollar_change"] <= 0 or main["relative_wealth"] <= 1))):
        status, reason = "failed_candidate", "Frozen gross benchmark or primary net/relative condition failed; no automatic tuning"
    elif not main["complete"] or not gross["complete"] or not stress["complete"]:
        status, reason = "inconclusive", "A required main/gross/stress case is infeasible or incomplete"
    elif (main["excess_log_95CI"][0] > 0
          and all(h["excess_log_return"] > 0 for h in main["chronological_halves"])
          and stress["relative_wealth"] >= 1):
        status, reason = "candidate_only", "All fixed exploratory conditions met; qualifies only for genuinely new evidence"
    else:
        status, reason = "inconclusive", "One or more remaining fixed exploratory candidate conditions failed"
    return {"status": status, "reason": reason, "original_predictive_MSE_gate": "FAILED",
            "proven_actual_profit": False, "proven_capacity": False, "wealth_goal_achieved": False,
            "limits": LIMITS}


def load_market(p, deadline):
    """Validate sealed source identities and reconstruct clock; no portfolio returns."""
    import pandas as pd
    import numpy as np
    import exchange_calendars as xcals
    import pyarrow as pa
    pa.set_cpu_count(1)
    pa.set_io_thread_count(1)
    source = p["inputs"]
    for path_key, sha_key in [("data_path", "data_sha256"), ("predictions_path", "predictions_sha256")]:
        if file_hash(source[path_key]) != source[sha_key]:
            raise StopReplay("Frozen input file mismatch: " + path_key)
    records, identity, per_window = {}, None, {}
    with Path(source["predictions_path"]).open(encoding="utf-8") as stream:
        for line in stream:
            check_clock(deadline)
            row = json.loads(line)
            checksum = row.pop("record_sha256", None)
            if checksum != digest_obj(row):
                raise StopReplay("Sealed prediction record checksum mismatch")
            row["record_sha256"] = checksum
            symbol, window = row["symbol"], row["window_index"]
            if symbol not in SYMBOLS or type(window) is not int or not 0 <= window < 188 or (window, symbol) in records:
                raise StopReplay("Duplicate/invalid prediction symbol/window")
            if row["seed"] != 20261015+1000000*(SYMBOLS.index(symbol)+1)+window:
                raise StopReplay("Frozen seed identity mismatch")
            if identity is None:
                identity = row["source_identity_sha256"]
            elif row["source_identity_sha256"] != identity:
                raise StopReplay("Predictions originate from mixed source identities")
            actual, forecast, p0 = row["actual_terminal_close"], row["terminal_close_10sample_mean"], row["p0"]
            if any(not math.isfinite(float(v)) or v <= 0 for v in [actual, forecast, p0]):
                raise StopReplay("Nonpositive/nonfinite sealed prices")
            r, rh = actual/p0-1, forecast/p0-1
            values = {"r": r, "r_hat": rh, "zero_squared_error": r*r, "model_squared_error": (rh-r)**2, "d": r*r-(rh-r)**2}
            if any(not math.isclose(row[k], value, abs_tol=1e-15, rel_tol=1e-12) for k, value in values.items()):
                raise StopReplay("Sealed score formula mismatch")
            if len(row["target_timestamps"]) != 12 or row["prediction_features"] != ["open", "high", "low", "close"]:
                raise StopReplay("Sealed target/features identity mismatch")
            key = (row["last_input"], tuple(row["target_timestamps"]), row["forecast_origin_bar_end"])
            if window in per_window and per_window[window] != key:
                raise StopReplay("Symbols do not share the exact forecast time identity")
            per_window[window] = key
            records[(window, symbol)] = row
    if len(records) != 9400 or len(per_window) != 188 or any((i, s) not in records for i in range(188) for s in SYMBOLS):
        raise StopReplay("Incomplete original50 x188 prediction panel")
    check_clock(deadline)
    df = pd.read_parquet(source["data_path"], columns=["symbol", "datetime", "open", "high", "low", "close"], use_threads=False)
    frames, times = {}, None
    for symbol in SYMBOLS:
        frame = df.loc[df["symbol"] == symbol, ["datetime", "open", "high", "low", "close"]].copy()
        dates = pd.to_datetime(frame["datetime"], errors="raise")
        if dates.dt.tz is None:
            raise StopReplay("Naive source timestamps; timezone cannot be guessed")
        frame["datetime"] = dates.dt.tz_convert("America/New_York")
        frame = frame.set_index("datetime")
        if frame.empty or frame.index.has_duplicates or not frame.index.is_monotonic_increasing:
            raise StopReplay("Missing/duplicated/nonchronological source rows")
        if times is None:
            times = frame.index
        elif len(times) != len(frame) or not (times == frame.index).all():
            raise StopReplay("50 symbols have unequal source time grids")
        oc = frame[["open", "close"]].to_numpy(dtype="float64")
        if not np.isfinite(oc).all() or (oc <= 0).any():
            raise StopReplay("Invalid execution/valuation open or close price")
        frames[symbol] = frame
    expected, end_by_start = calendar_clock(times, pd, xcals)
    if len(times) != len(expected) or not (times == expected).all():
        raise StopReplay("Source grid not complete XNYS hourly starts; no time offsets guessed")
    rebalances, scores = [], []
    history_hashes_checked = 0
    for i in range(188):
        check_clock(deadline)
        origin, targets_raw, origin_end = per_window[i]
        origin_time = pd.Timestamp(origin)
        targets = parse_targets(targets_raw, pd)
        origin_position = int(times.get_indexer([origin_time])[0])
        if origin_position < 79 or origin_position+12 >= len(times):
            raise StopReplay("Source does not cover complete history/forecast horizon")
        real_targets = times[origin_position+1:origin_position+13]
        if len(real_targets) != 12 or not (targets == real_targets).all() or pd.Timestamp(origin_end) != end_by_start[times[origin_position]]:
            raise StopReplay("Source/forecast history or target time identity mismatch")
        if i and origin_position != previous_origin_position+12:
            raise StopReplay("Original windows do not preserve stride12")
        previous_origin_position = origin_position
        rebalance = origin_position+2
        if end_by_start[targets[0]] > times[rebalance]:
            raise StopReplay("Rebalance precedes completion of the first target bar")
        rebalances.append(rebalance)
        scores.append({s: float(records[(i, s)]["r_hat"]) for s in SYMBOLS})
        history = times[origin_position-79:origin_position+1]
        for symbol in SYMBOLS:
            row, frame = records[(i, symbol)], frames[symbol]
            if not math.isclose(float(frame.loc[origin_time, "close"]), row["p0"], rel_tol=1e-12, abs_tol=1e-12):
                raise StopReplay("Sealed p0 and source close differ in price/unit")
            if not math.isclose(float(frame.loc[targets[-1], "close"]), row["actual_terminal_close"], rel_tol=1e-12, abs_tol=1e-12):
                raise StopReplay("Sealed endpoint and source close differ in price/unit")
            expected_hash = digest_obj({"timestamps": [t.isoformat() for t in history],
                                       "features": ["open", "high", "low", "close"],
                                       "values": frame.loc[history, ["open", "high", "low", "close"]].to_numpy(dtype="float64").tolist()})
            if expected_hash != row["input_sha256"]:
                raise StopReplay("Sealed historical input values do not match frozen source")
            history_hashes_checked += 1
    final_index = int(previous_origin_position+14)
    if final_index >= len(times) or final_index != rebalances[-1]+12:
        raise StopReplay("Missing second source open after final target; final clock inconsistent")
    opens = [{s: float(frames[s].iloc[i]["open"]) for s in SYMBOLS} for i in range(len(times))]
    closes = [{s: float(frames[s].iloc[i]["close"]) for s in SYMBOLS} for i in range(len(times))]
    market = {"symbols": SYMBOLS, "times": list(times), "bar_end_times": [end_by_start[t] for t in times],
              "opens": opens, "closes": closes, "rebalance_indices": rebalances,
              "final_index": final_index, "scores": scores}
    report = {"status": "preflight_pass", "recorded_at_utc": utc_now(), "records": 9400, "symbols": SYMBOLS,
              "windows": 188, "source_rows_per_symbol": len(times), "source_identity_sha256": identity,
              "history_input_hashes_checked": history_hashes_checked, "score_formulas_checked": 9400,
              "rebalance_indices": rebalances, "rebalance_timestamps": [times[k].isoformat() for k in rebalances],
              "first_rebalance": times[rebalances[0]].isoformat(), "final_exit": times[final_index].isoformat(),
              "final_source_bar_index": final_index, "source_hashes": {"data": source["data_sha256"], "predictions": source["predictions_sha256"]},
              "model_imported": False, "predictions_generated": 0, "portfolio_returns_calculated": False,
              "pyarrow_threads": {"cpu_count": pa.cpu_count(), "io_thread_count": pa.io_thread_count(), "read_parquet_use_threads": False},
              "causal_clock_scope": "first complete target bar ends before or at delayed open; historical vendor availability not reconstructed",
              "limits": LIMITS}
    return market, report


def prepare_out(path, mode):
    out = Path(path).resolve()
    if out == HERE or not out.is_relative_to(HERE):
        raise StopReplay("Outputs must be an isolated child of this economic-replay folder")
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise StopReplay("Output already exists; no rerun, resume or overwrite allowed")
    out.mkdir(parents=True, exist_ok=True)
    if mode == "run":
        # Global to this fixed experiment, not bypassable by choosing a new out.
        with (HERE / "formal-attempt.json").open("x", encoding="utf-8") as stream:
            stream.write(canonical({"consumed_at_utc": utc_now(), "pid": os.getpid(), "out": str(out),
                                    "adapter_sha256": file_hash(__file__), "retry_permitted": False})+"\n")
            stream.flush()
            os.fsync(stream.fileno())
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", required=True)
    parser.add_argument("--authorization", required=True)
    parser.add_argument("--out", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--run", action="store_true")
    args = parser.parse_args()
    p, auth, work_deadline = load_authorization(args.protocol, args.authorization)
    remaining = (work_deadline-datetime.now(timezone.utc)).total_seconds()
    deadline = time.monotonic()+min(remaining, 1800)
    forbid_network()
    out = prepare_out(args.out, "run" if args.run else "preflight")
    started = time.monotonic()
    try:
        market, report = load_market(p, deadline)
        if "torch" in sys.modules or "model.kronos" in sys.modules:
            raise StopReplay("Forbidden model/torch import")
        write_json(out / "preflight.json", report)
        metadata = {"created_at_utc": utc_now(), "mode": "run" if args.run else "preflight",
                    "protocol_sha256": file_hash(args.protocol), "authorization_sha256": file_hash(args.authorization),
                    "adapter_sha256": file_hash(__file__), "source_hashes": report["source_hashes"],
                    "threads_environment": {k: os.environ[k] for k in ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS"]},
                    "pyarrow_threads": report["pyarrow_threads"],
                    "work_deadline_utc": work_deadline.isoformat(), "max_calculation_seconds": 1800,
                    "model_inference_starts": 0, "orders_sent": 0, "scope": LIMITS}
        write_json(out / "metadata.json", metadata)
        if args.preflight:
            print(canonical({"status": "preflight_pass", "returns_calculated": False, "out": str(out)}), flush=True)
            return 0
        import numpy as np
        benchmark = simulate_scenario(market, 0, 0, benchmark=True, deadline=deadline)
        if not benchmark["summary"]["complete"]:
            raise StopReplay("Frictionless all50 benchmark could not complete")
        benchmark_out = out / "benchmark"
        benchmark_out.mkdir()
        write_json(benchmark_out / "summary.json", benchmark["summary"])
        write_json(benchmark_out / "event-wealth.json", {"W": benchmark["W"], "window_log_returns": benchmark["window_log_returns"]})
        write_jsonl(benchmark_out / "order-ledger.jsonl", benchmark["orders"])
        write_jsonl(benchmark_out / "rebalance-events.jsonl", benchmark["rebalance_events"])
        write_jsonl(benchmark_out / "NAV-samples.jsonl", benchmark["NAV_samples"])
        cases = {}
        for commission in [0, 1, 2]:
            for slip in [0, 5, 10]:
                check_clock(deadline)
                label = f"commission{commission}_slippage{slip}bps"
                result = simulate_scenario(market, commission, slip, deadline=deadline)
                compare_with_benchmark(result, benchmark, np, deadline)
                cases[label] = result
                case_out = out / label
                case_out.mkdir()
                write_json(case_out / "summary.json", result["summary"])
                write_json(case_out / "event-wealth.json", {"W": result["W"], "window_log_returns": result["window_log_returns"],
                                                           "paired_window_excess_log_returns": result.get("paired_window_excess_log_returns")})
                write_jsonl(case_out / "order-ledger.jsonl", result["orders"])
                write_jsonl(case_out / "rebalance-events.jsonl", result["rebalance_events"])
                write_jsonl(case_out / "NAV-samples.jsonl", result["NAV_samples"])
                print(canonical({"scenario": label, "status": result["summary"]["status"]}), flush=True)
        verdict = decision(cases)
        check_clock(deadline)
        write_json(out / "all-scenarios.json", {label: value["summary"] for label, value in cases.items()})
        write_json(out / "decision.json", verdict)
        write_json(out / "state.json", {"status": "completed", "ended_at_utc": utc_now(), "wall_seconds": time.monotonic()-started,
                                        "scenarios": 9, "decision": verdict["status"], "actual_profit_proven": False,
                                        "model_inference_starts": 0, "orders_sent": 0, "retry_permitted": False})
        print(canonical({"status": "completed", "decision": verdict["status"], "out": str(out)}), flush=True)
        return 0
    except BaseException as exc:
        write_json(out / "state.json", {"status": "incomplete", "at_utc": utc_now(), "error_type": type(exc).__name__,
                                        "reason": str(exc), "wall_seconds": time.monotonic()-started,
                                        "candidate_passed": False, "retry_permitted": False})
        print("STOP "+str(exc), file=sys.stderr, flush=True)
        return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"STOP {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
        raise SystemExit(2)

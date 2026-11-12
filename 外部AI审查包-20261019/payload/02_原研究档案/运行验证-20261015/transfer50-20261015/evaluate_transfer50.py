#!/usr/bin/env python3
"""One local-only, fixed 50-symbol Kronos-small transfer assessment.

No model is imported by this module or by --preflight. A full invocation consumes
one exclusive attempt, never resumes, and cannot produce a passed partial panel.
The original AAPL harness and all earlier experiment files remain read-only.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import random
import sys
import time

sys.dont_write_bytecode = True

FEATURES = ["open", "high", "low", "close"]
SYMBOLS = ["ABBV", "ADBE", "AMD", "AMZN", "AVGO", "BA", "BAC", "BLK", "BRK.B", "CAT",
           "COP", "COST", "CRM", "CSCO", "CVX", "DIS", "GE", "GOOGL", "GS", "HD",
           "JNJ", "JPM", "KO", "LIN", "LLY", "MA", "MCD", "META", "MRK", "MS",
           "MSFT", "NFLX", "NKE", "NVDA", "ORCL", "PEP", "PFE", "PG", "RTX", "SBUX",
           "T", "TMO", "TMUS", "TSLA", "UNH", "V", "VZ", "WFC", "WMT", "XOM"]
FIXED = {
    "symbols": SYMBOLS, "start_date": "2025-07-01", "timezone": "America/New_York",
    "calendar": "XNYS", "context": 80, "horizon": 12, "stride": 12,
    "features": FEATURES, "device": "cpu", "threads": 6,
    "sampling": {"T": 0.6, "top_p": 0.9, "top_k": 0, "sample_count": 10,
                 "max_context": 512, "seed_base": 20261015},
    "CI": {"method": "circular/moving block bootstrap", "block_length": 10,
           "resamples": 5000, "confidence": 0.95, "seed": 20261015},
    "expected_time_windows": 188, "expected_records": 9400,
    "max_inference_seconds": 14400, "max_wall_seconds": 14400,
    "seed_symbol_stride": 1000000,
    "source_commit": "67b630e67f6a18c9e9be918d9b4337c960db1e9a",
    "helper_sha256": "ba17b247150fadd4bcaead2e21ace91241d7a599dfa38e98b1e19283732e3936",
    "source_files_sha256": {
        "model/__init__.py": "f8f856ca3fedadcaac97e196be23d1aeda1c3c9ffe8903d66d43ea3bcac6240c",
        "model/kronos.py": "0a5f90282e2039c2de0771473419715c845def154896dbd0f5747837e6241032",
        "model/module.py": "a07edbadc0e96804c8158c021bbc6063bb7cc43b34d7fc470d5c8ff2005a409f"},
    "source_tree_sha256": "dc8ecf717645a3880b96957dacd0b8a771e133fb0b4235524d658530efee2425",
    "model_config_sha256": "5e0f6a605d5f81b5c9b559fe5cf716a1acb041c744e6f41bd05b097b7a685396",
    "tokenizer_config_sha256": "2366e7ccfec76cbc19cf3c4c1b9c5d901be336ca1e83f2d2292c9bff381b77a2"}
ARTIFACT_FIXED = {
    "dataset": {"id": "twelvedata/financial-world-model", "revision": "0fb1fa4a54d92475fa599cd95536d31d918930bf",
                "file": "bars_1h/test.parquet", "sha256": "9aa5e309ab3661c78a0c06b05ae6cc04fdf944eb962a5861c972d81ecf704c73"},
    "model": {"repository": "NeoQuasar/Kronos-small", "revision": "ac5c409a313c4eadd1ca78201322f5cadb9c34ab",
              "weights_sha256": "b082dfcbd8e8c142a725c8bbb99781802f38fec81210e13479effb32b3c3e020"},
    "tokenizer": {"repository": "NeoQuasar/Kronos-Tokenizer-base", "revision": "9ef143b98ee3c2488eebd85404e0c215c112b46a",
                  "weights_sha256": "59d85f6af76a2c3b8240ea06cb21db4213b4eeca053f246b23e29cf832fc6bee"}}


class StopRun(RuntimeError):
    pass


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def digest_obj(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, value):
    path = Path(path)
    temp = path.with_name(path.name + ".tmp")
    with temp.open("w", encoding="utf-8") as f:
        f.write(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
    temp.replace(path)


def load_protocol(path):
    p = json.loads(Path(path).read_text(encoding="utf-8"))
    for key, value in FIXED.items():
        if p.get(key) != value:
            raise StopRun(f"Frozen protocol mismatch: {key}")
    for section, fields in ARTIFACT_FIXED.items():
        for key, value in fields.items():
            if p.get(section, {}).get(key) != value:
                raise StopRun(f"Frozen artifact mismatch: {section}.{key}")
    if p.get("adapter_sha256") != file_hash(__file__):
        raise StopRun("Adapter does not match frozen SHA256")
    frozen = datetime.fromisoformat(p.get("frozen_at_utc", ""))
    if frozen.tzinfo is None or frozen.utcoffset().total_seconds() != 0:
        raise StopRun("Protocol freeze timestamp must specify UTC")
    if frozen > datetime.now(timezone.utc):
        raise StopRun("Protocol freeze timestamp is in the future")
    if not isinstance(p.get("authorization"), str) or not p["authorization"].strip():
        raise StopRun("Missing explicit human authorization reference")
    if "symbol" in p:
        raise StopRun("Single-symbol protocol cannot identify this panel")
    return p


def load_helper(p):
    helper_path = Path(__file__).resolve().parent.parent / "evaluate_kronos.py"
    if file_hash(helper_path) != p["helper_sha256"]:
        raise StopRun("Read-only original helper hash mismatch")
    spec = importlib.util.spec_from_file_location("transfer50_frozen_helpers", helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    return helper


def artifacts(args, p, helper):
    identity, paths, source = helper.artifacts(
        argparse.Namespace(data=args.data, source_root=args.source_root, model_dir=args.model_dir,
                           tokenizer_dir=args.tokenizer_dir, smoke=False, limit=188), p)
    hashes = identity["hashes"]
    if hashes["source_files"] != p["source_files_sha256"] or hashes["source_tree_sha256"] != p["source_tree_sha256"]:
        raise StopRun("Model source files differ from the frozen source tree")
    for key in ["model_config", "tokenizer_config"]:
        if hashes[key] != p[key + "_sha256"]:
            raise StopRun("Frozen configuration hash mismatch: " + key)
    # The original helper's identity must not label this as the AAPL harness.
    hashes["helper_sha256"] = hashes.pop("harness_sha256")
    hashes["adapter_sha256"] = file_hash(__file__)
    identity.update(mode="preflight_only" if args.preflight else "one_attempt_transfer50",
                    inference_unit="188 common time windows; keep 50-symbol cross-section together",
                    selection="all 50 predeclared symbols at all 188 common calendar windows; no replacements",
                    protocol_file_sha256=file_hash(args.protocol))
    identity.pop("limit", None)
    return identity, paths, source


def prepare_out(path, identity, preflight):
    out = Path(path).resolve()
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise StopRun("Output must be a new/empty directory; no resume or overwrite")
    out.mkdir(parents=True, exist_ok=True)
    if not preflight:
        with (out / "attempt.json").open("x", encoding="utf-8") as f:
            f.write(canonical({"consumed_at_utc": utc_now(), "pid": os.getpid(),
                               "identity_sha256": digest_obj(identity), "retry_permitted": False}) + "\n")
            f.flush()
            os.fsync(f.fileno())
    write_json(out / "metadata.json", {"created_at_utc": utc_now(), "identity": identity,
                                       "scope": "retrospective prediction errors only; no trading/profit/capacity evidence"})
    return out


def seed_for(p, symbol, window_index):
    return p["sampling"]["seed_base"] + p["seed_symbol_stride"] * (p["symbols"].index(symbol) + 1) + window_index


def qc_data(args, p, out, pd, np, xcals, helper):
    raw = pd.read_parquet(args.data, columns=["symbol", "datetime"] + FEATURES)
    qc = {"checked_at_utc": utc_now(), "status": "STOP", "issues": [], "per_symbol": {},
          "retrospective_limit": "historical first-publication times and revision histories not reconstructed"}

    def stop(reason, evidence=None):
        qc["issues"].append({"reason": reason, "evidence": evidence})
        write_json(out / "qc.json", qc)
        raise StopRun(reason)

    frames, common = {}, None
    for symbol in p["symbols"]:
        df = raw.loc[raw["symbol"] == symbol, ["datetime"] + FEATURES].copy()
        if df.empty:
            stop("Missing predeclared symbol", symbol)
        try:
            dates = pd.to_datetime(df["datetime"], errors="raise")
            if dates.dt.tz is None:
                stop("Naive timestamps; no timezone guessed", symbol)
            dates = dates.dt.tz_convert(p["timezone"])
            df["datetime"] = dates
        except StopRun:
            raise
        except Exception as exc:
            stop("Timestamp parse error", {"symbol": symbol, "exception": str(exc)})
        if dates.isna().any() or dates.duplicated().any() or not dates.is_monotonic_increasing:
            stop("Missing, duplicated or non-chronological timestamps", symbol)
        try:
            values = df[FEATURES].to_numpy(dtype="float64")
        except (TypeError, ValueError) as exc:
            stop("Non-numeric OHLC", {"symbol": symbol, "exception": str(exc)})
        bad = (~np.isfinite(values)).any(axis=1) | (values <= 0).any(axis=1)
        bad |= values[:, 1] < np.maximum.reduce([values[:, 0], values[:, 2], values[:, 3]])
        bad |= values[:, 2] > np.minimum.reduce([values[:, 0], values[:, 1], values[:, 3]])
        if bad.any():
            stop("Invalid finite/positive/OHLC ordering", {"symbol": symbol, "rows": df.loc[bad].head(20).astype(str).to_dict("records")})
        df[FEATURES] = values
        df = df.set_index("datetime")
        if common is None:
            common = df.index
        elif not common.equals(df.index):
            stop("Symbols do not share the complete identical time grid", symbol)
        frames[symbol] = df
        qc["per_symbol"][symbol] = {"rows": len(df), "first": df.index[0].isoformat(), "last": df.index[-1].isoformat()}
    grid, ends = helper.calendar_grid(pd, xcals, common[0].date().isoformat(), common[-1].date().isoformat(), p["timezone"])
    if (~common.isin(grid)).any():
        stop("Timestamps are not XNYS hourly interval starts")
    last_pos = grid.get_indexer([common[-1]])[0]
    grid, ends = grid[:last_pos + 1], ends[:last_pos + 1]
    # Arrow may preserve microsecond units while the calendar uses nanoseconds;
    # compare actual instants rather than pandas dtype-sensitive .equals().
    if len(common) != len(grid) or not (common == grid).all():
        stop("Missing grid rows; no replacements or favorable subset", {"missing": grid[~grid.isin(common)].astype(str).tolist()[:20]})
    if (ends > pd.Timestamp.now(tz=p["timezone"])).any():
        stop("Dataset contains unfinished bars")
    threshold = pd.Timestamp(p["start_date"], tz=p["timezone"])
    first_anchor = max(p["context"] - 1, int(grid.searchsorted(threshold)) - 1)
    windows = []
    for index, anchor in enumerate(range(first_anchor, len(grid) - p["horizon"], p["stride"])):
        hist = grid[anchor - p["context"] + 1:anchor + 1]
        future = grid[anchor + 1:anchor + 1 + p["horizon"]]
        if len(hist) != p["context"] or len(future) != p["horizon"] or future[0] < threshold or hist[-1] >= future[0]:
            stop("Invalid history/target separation")
        entry = {"window_index": index, "last_input": hist[-1].isoformat(),
                 "target_timestamps": [t.isoformat() for t in future]}
        windows.append((entry, hist, future, ends[anchor]))
    if len(windows) != p["expected_time_windows"]:
        stop("Unexpected common window count", len(windows))
    qc.update(status="PASS", expected_grid_rows=len(grid), symbols=len(frames), common_windows=len(windows),
              planned_records=len(windows) * len(frames), missing_grid_rows=0,
              selection="all predeclared symbols, complete common panel; no dropped rows",
              interval="XNYS session-open hourly interval starts; final bar may be shorter than an hour")
    write_json(out / "qc.json", qc)
    write_json(out / "window-manifest.json", {"entries": [w[0] for w in windows],
                                              "symbols": p["symbols"], "seeds": {s: {"first": seed_for(p, s, 0), "last": seed_for(p, s, len(windows) - 1)} for s in p["symbols"]}})
    return frames, windows, qc


def validate_panel(records, p, entries):
    """Return complete time-by-symbol records; reject duplicates/misalignment/arithmetic corruption."""
    panel, expected = {}, p["expected_records"]
    for row in records:
        symbol, index = row["symbol"], row["window_index"]
        if symbol not in p["symbols"] or not isinstance(index, int) or not 0 <= index < len(entries):
            raise StopRun("Record symbol/window identity invalid")
        key = (index, symbol)
        if key in panel:
            raise StopRun("Duplicate symbol/window record")
        entry = entries[index]
        if (row["last_input"] != entry["last_input"] or row["target_timestamps"] != entry["target_timestamps"]
                or row["seed"] != seed_for(p, symbol, index)):
            raise StopRun("Record seed/time identity mismatch")
        copy = dict(row)
        checksum = copy.pop("record_sha256", None)
        if checksum != digest_obj(copy):
            raise StopRun("Record checksum mismatch")
        for field in ["p0", "actual_terminal_close", "terminal_close_10sample_mean", "r", "r_hat", "d", "zero_squared_error", "model_squared_error"]:
            if not isinstance(row[field], (int, float)) or not math.isfinite(row[field]):
                raise StopRun("Record has nonfinite/non-numeric fields")
        if row["p0"] <= 0 or row["actual_terminal_close"] <= 0 or row["terminal_close_10sample_mean"] <= 0:
            raise StopRun("Record has nonpositive price")
        r, rh = row["actual_terminal_close"] / row["p0"] - 1, row["terminal_close_10sample_mean"] / row["p0"] - 1
        values = {"r": r, "r_hat": rh, "zero_squared_error": r*r, "model_squared_error": (rh-r)**2, "d": r*r-(rh-r)**2}
        if any(not math.isclose(row[k], v, rel_tol=1e-12, abs_tol=1e-15) for k, v in values.items()):
            raise StopRun("Record score arithmetic mismatch")
        panel[key] = row
    complete = (len(records) == expected and len(entries) == p["expected_time_windows"]
                and all((i, s) in panel for i in range(len(entries)) for s in p["symbols"]))
    return panel, complete


def summarize(records, p, np, entries, qc_status="PASS", termination=None):
    panel, complete = validate_panel(records, p, entries)
    complete = complete and qc_status == "PASS" and termination is None
    by_symbol = {}
    for symbol in p["symbols"]:
        rows = [panel[(i, symbol)] for i in range(len(entries)) if (i, symbol) in panel]
        z = float(np.mean([r["zero_squared_error"] for r in rows])) if rows else None
        m = float(np.mean([r["model_squared_error"] for r in rows])) if rows else None
        by_symbol[symbol] = {"n": len(rows), "coverage": len(rows) / len(entries), "zero_mse": z, "model_mse": m,
                             "relative_mse_improvement": (z-m)/z if z is not None and z > 0 else None,
                             "descriptive_only": True}
    time_means = []
    for i in range(len(entries)):
        if all((i, s) in panel for s in p["symbols"]):
            time_means.append({"window_index": i, "paired_d_mean": float(np.mean([panel[(i, s)]["d"] for s in p["symbols"]]))})
    summary = {"generated_at_utc": utc_now(), "status": "incomplete", "gate_passed": False,
               "complete_panel": bool(complete), "n_records": len(records), "planned_records": p["expected_records"],
               "n_complete_time_windows": len(time_means), "planned_time_windows": p["expected_time_windows"],
               "n_symbols": len(p["symbols"]), "qc_status": qc_status, "termination": termination,
               "inference_unit": "synchronous time window, not symbol-window row", "bootstrap": p["CI"],
               "paired_d_mean": None, "zero_mse": None, "model_mse": None, "relative_mse_improvement": None,
               "circular_block_bootstrap_95CI": None, "chronological_halves_mean_d": None,
               "limits": ["retrospective transfer screen; not true prospective validation or full paper reproduction",
                          "historical publication times, revisions and full training manifest not independently reconstructed",
                          "equal asset weights do not remove larger squared-return contribution of volatile assets",
                          "uncertainty depends on predeclared circular time-block assumptions",
                          "no fees, executable fills, profit curve, drawdown or capacity evaluated",
                          "forecast MSE improvement is neither necessary nor sufficient for trading profitability"]}
    if complete:
        d = np.array([r["paired_d_mean"] for r in time_means], dtype=float)
        z = float(np.mean([r["zero_squared_error"] for r in records]))
        m = float(np.mean([r["model_squared_error"] for r in records]))
        split = len(d) // 2
        halves = [float(d[:split].mean()), float(d[split:].mean())]
        rng = np.random.default_rng(p["CI"]["seed"])
        length, draws = p["CI"]["block_length"], p["CI"]["resamples"]
        offsets, count = np.arange(length), math.ceil(len(d) / length)
        means = np.empty(draws)
        for b in range(draws):
            starts = rng.integers(0, len(d), size=count)
            indexes = ((starts[:, None] + offsets) % len(d)).reshape(-1)[:len(d)]
            means[b] = d[indexes].mean()
        alpha = (1-p["CI"]["confidence"]) / 2
        ci = np.quantile(means, [alpha, 1-alpha]).tolist()
        passed = ci[0] > 0 and all(value > 0 for value in halves)
        summary.update(status="prediction_gate_pass" if passed else "prediction_gate_not_passed", gate_passed=bool(passed),
                       paired_d_mean=float(d.mean()), zero_mse=z, model_mse=m,
                       relative_mse_improvement=(z-m)/z if z > 0 else None,
                       circular_block_bootstrap_95CI=ci, chronological_halves_mean_d=halves)
    return summary, by_symbol, time_means


def finalize(out, records, p, np, windows, qc_status, termination=None):
    summary, by_symbol, time_means = summarize(records, p, np, [w[0] for w in windows], qc_status, termination)
    write_json(out / "per-symbol-descriptive.json", by_symbol)
    write_json(out / "time-window-means.json", {"rows": time_means, "cross_section_kept_together": True})
    write_json(out / "summary.json", summary)
    return summary


def main():
    started = time.perf_counter()
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["protocol", "data", "model-dir", "tokenizer-dir", "source-root", "out"]:
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--preflight", action="store_true", help="Validate/QC only; no torch/model import or prediction")
    args = parser.parse_args()
    p = load_protocol(args.protocol)
    helper = load_helper(p)
    helper.forbid_network()
    identity, paths, source = artifacts(args, p, helper)
    out = prepare_out(args.out, identity, args.preflight)
    import numpy as np
    import pandas as pd
    import exchange_calendars as xcals
    records, windows, qc, inference_seconds = [], [], {"status": "STOP"}, 0.0
    try:
        frames, windows, qc = qc_data(args, p, out, pd, np, xcals, helper)
        if args.preflight:
            if "torch" in sys.modules or "model.kronos" in sys.modules:
                raise StopRun("Preflight unexpectedly imported model/torch")
            result = {"status": "preflight_pass", "generated_at_utc": utc_now(), "model_imported": False,
                      "torch_imported": False, "model_predictions_generated": 0,
                      "common_time_windows": len(windows), "symbols": len(p["symbols"]),
                      "planned_records": len(windows)*len(p["symbols"]), "identity_sha256": digest_obj(identity)}
            write_json(out / "preflight.json", result)
            print(canonical(result), flush=True)
            return 0
        if time.perf_counter()-started >= p["max_wall_seconds"]:
            raise StopRun("Wall-clock cap reached before model loading")
        import torch
        torch.set_num_threads(p["threads"])
        torch.set_num_interop_threads(1)
        torch.use_deterministic_algorithms(True)
        predictor = helper.local_predictor(source, paths, p, torch)
        runtime = {"started_at_utc": utc_now(), "pid": os.getpid(), "device": "cpu",
                   "torch_threads": torch.get_num_threads(), "torch_interop_threads": torch.get_num_interop_threads(),
                   "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
                   "model_training": predictor.model.training, "tokenizer_training": predictor.tokenizer.training,
                   "identity_sha256": digest_obj(identity), "new_training_steps": 0, "network_forbidden": True}
        if runtime["model_training"] or runtime["tokenizer_training"] or runtime["torch_threads"] > 6:
            raise StopRun("Runtime violates eval-only/CPU-thread constraint")
        write_json(out / "runtime.json", runtime)
        with (out / "predictions.jsonl").open("x", encoding="utf-8") as output:
            for entry, hist, future, origin_end in windows:
                for symbol in p["symbols"]:
                    if inference_seconds >= p["max_inference_seconds"] or time.perf_counter()-started >= p["max_wall_seconds"]:
                        raise StopRun("Resource cap reached; no retry or partial-panel pass")
                    seed = seed_for(p, symbol, entry["window_index"])
                    random.seed(seed)
                    np.random.seed(seed)
                    torch.manual_seed(seed)
                    # Future OHLC is never passed to the predictor. Only future calendar timestamps are known.
                    x = frames[symbol].loc[hist, FEATURES].copy()
                    p0 = float(x.iloc[-1]["close"])
                    input_sha = helper.input_hash(x)
                    start_utc, tick = utc_now(), time.perf_counter()
                    try:
                        with torch.inference_mode():
                            pred = predictor.predict(df=x, x_timestamp=pd.Series(hist), y_timestamp=pd.Series(future),
                                pred_len=p["horizon"], T=p["sampling"]["T"], top_p=p["sampling"]["top_p"],
                                top_k=p["sampling"]["top_k"], sample_count=p["sampling"]["sample_count"], verbose=False)
                    finally:
                        elapsed = time.perf_counter()-tick
                        inference_seconds += elapsed
                    finish_utc = utc_now()
                    pv = pred[FEATURES].to_numpy(dtype="float64")
                    if pv.shape != (12, 4) or not np.isfinite(pv).all() or (pv <= 0).any():
                        raise StopRun("Invalid prediction shape, nonfinite or nonpositive OHLC; no retry")
                    # Read target price for scoring only after prediction has returned.
                    actual = float(frames[symbol].loc[future[-1], "close"])
                    terminal = float(pv[-1, 3])
                    rh, r = terminal/p0-1, actual/p0-1
                    zse, mse = r*r, (rh-r)**2
                    row = dict(entry, symbol=symbol, seed=seed, input_sha256=input_sha,
                               source_identity_sha256=digest_obj(identity), forecast_origin_bar_end=origin_end.isoformat(),
                               prediction_started_at_utc=start_utc, prediction_finished_at_utc=finish_utc,
                               p0=p0, prediction_features=FEATURES, prediction_12step_ohlc=pv.tolist(),
                               terminal_close_10sample_mean=terminal, actual_terminal_close=actual,
                               r_hat=rh, r=r, zero_squared_error=zse, model_squared_error=mse, d=zse-mse,
                               inference_seconds=elapsed, cumulative_inference_seconds=inference_seconds,
                               scope="retrospective prediction errors only; no future prices supplied to predictor")
                    row["record_sha256"] = digest_obj(row)
                    output.write(canonical(row) + "\n")
                    output.flush()
                    os.fsync(output.fileno())
                    records.append(row)
                    if len(records) % 50 == 0:
                        progress = {"updated_at_utc": utc_now(), "status": "running", "records": len(records),
                                    "complete_time_windows": len(records)//50, "planned_records": p["expected_records"],
                                    "cumulative_inference_seconds": inference_seconds, "wall_seconds": time.perf_counter()-started,
                                    "last_record_sha256": row["record_sha256"]}
                        write_json(out / "progress.json", progress)
                        print(canonical(progress), flush=True)
        summary = finalize(out, records, p, np, windows, qc["status"])
        write_json(out / "state.json", {"status": "completed", "ended_at_utc": utc_now(),
                                        "records": len(records), "cumulative_inference_seconds": inference_seconds,
                                        "wall_seconds": time.perf_counter()-started,
                                        "predictions_sha256": file_hash(out / "predictions.jsonl"),
                                        "gate_passed": summary["gate_passed"], "scope": "no profitability evaluation"})
        print(canonical({"status": summary["status"], "records": len(records), "out": str(out)}), flush=True)
        return 0
    except BaseException as exc:
        termination = {"type": type(exc).__name__, "reason": str(exc), "at_utc": utc_now()}
        if windows:
            finalize(out, records, p, np, windows, qc["status"], termination)
        write_json(out / "state.json", {"status": "incomplete", "termination": termination, "records": len(records),
                                        "cumulative_inference_seconds": inference_seconds,
                                        "wall_seconds": time.perf_counter()-started, "gate_passed": False,
                                        "retry_permitted": False})
        print("STOP " + canonical(termination), file=sys.stderr, flush=True)
        return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"STOP {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
        raise SystemExit(2)

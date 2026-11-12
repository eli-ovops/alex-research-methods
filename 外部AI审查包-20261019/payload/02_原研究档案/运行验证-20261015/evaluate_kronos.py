#!/usr/bin/env python3
"""Frozen local-only AAPL forecast assessment. No trading or training.

Requires an explicit protocol.json. This module does not load data/models on import.
An existing output directory is reusable only when its metadata and every record
match this exact run. Use a distinct directory for --smoke.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import random
import sys
import time
from datetime import datetime, timezone


FEATURES = ["open", "high", "low", "close"]
FIXED = {
    "symbol": "AAPL", "start_date": "2025-07-01",
    "timezone": "America/New_York", "calendar": "XNYS", "context": 80,
    "horizon": 12, "stride": 12, "max_windows": 300, "features": FEATURES,
    "device": "cpu", "threads": 6,
    "sampling": {"T": 0.6, "top_p": 0.9, "top_k": 0, "sample_count": 10,
                 "max_context": 512, "seed_base": 20261015},
    "CI": {"method": "circular/moving block bootstrap", "block_length": 10,
           "resamples": 5000, "confidence": 0.95, "seed": 20261015},
}


class StopRun(RuntimeError):
    pass


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False)


def digest_obj(obj):
    return hashlib.sha256(canonical(obj).encode()).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, obj):
    # Atomic replacement is confined to this run's own output files.
    p = Path(path)
    tmp = p.with_name(p.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        f.write(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(p)


def forbid_network():
    os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1",
                      HF_DATASETS_OFFLINE="1", HF_HUB_DISABLE_TELEMETRY="1",
                      DO_NOT_TRACK="1")

    def audit(event, args):
        if event in {"socket.connect", "socket.connect_ex", "socket.getaddrinfo",
                     "socket.sendto", "socket.bind"}:
            raise StopRun("Network operation forbidden: " + event)
    sys.addaudithook(audit)


def load_protocol(path):
    p = json.loads(Path(path).read_text(encoding="utf-8"))
    for key, expected in FIXED.items():
        if p.get(key) != expected:
            raise StopRun(f"Protocol mismatch {key}: expected {expected!r}")
    for key in ["dataset", "model", "tokenizer"]:
        hash_key = "sha256" if key == "dataset" else "weights_sha256"
        value = p.get(key, {}).get(hash_key, "")
        if len(value) != 64:
            raise StopRun(f"Missing protocol {key}.{hash_key}")
    if not p.get("frozen_at_utc") or not p.get("source_commit"):
        raise StopRun("Missing protocol freeze time/source commit")
    return p


def artifacts(args, p):
    data = Path(args.data).resolve(strict=True)
    source = Path(args.source_root).resolve(strict=True)
    model = Path(args.model_dir).resolve(strict=True)
    tok = Path(args.tokenizer_dir).resolve(strict=True)
    paths = {"data": data, "model_weights": model / "model.safetensors",
             "tokenizer_weights": tok / "model.safetensors",
             "model_config": model / "config.json",
             "tokenizer_config": tok / "config.json"}
    hashes = {k: file_hash(v) for k, v in paths.items()}
    for actual, expected in [(hashes["data"], p["dataset"]["sha256"]),
                             (hashes["model_weights"], p["model"]["weights_sha256"]),
                             (hashes["tokenizer_weights"], p["tokenizer"]["weights_sha256"])]:
        if actual != expected:
            raise StopRun("Artifact SHA256 does not match frozen protocol")
    py_files = sorted((source / "model").rglob("*.py"))
    if not py_files or not (source / "model" / "kronos.py").is_file():
        raise StopRun("Missing local official model sources")
    hashes["source_files"] = {str(f.relative_to(source)): file_hash(f) for f in py_files}
    hashes["source_tree_sha256"] = digest_obj(hashes["source_files"])
    hashes["harness_sha256"] = file_hash(__file__)
    versions = {}
    for name in ["numpy", "pandas", "torch", "safetensors", "pyarrow",
                 "exchange-calendars", "huggingface-hub", "einops"]:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "NOT_INSTALLED"
    identity = {"protocol": p, "protocol_sha256": digest_obj(p), "hashes": hashes,
                "paths": {k: str(v) for k, v in paths.items()},
                "source_root": str(source), "versions": versions,
                "python": sys.version, "platform": sys.platform,
                "mode": "smoke" if args.smoke else "full", "limit": args.limit,
                "bootstrap_implementation": "circular; concatenate length-10 blocks, truncate to n",
                "selection": "chronological calendar anchors stride12; missing windows logged; first limit scorable"}
    return identity, paths, source


def prepare_out(out, identity):
    p = Path(out).resolve()
    if p.exists():
        meta = p / "metadata.json"
        if not meta.is_file():
            raise StopRun("Output exists without matching metadata; use a new directory")
        old = json.loads(meta.read_text(encoding="utf-8"))
        if old.get("identity") != identity:
            raise StopRun("Existing output metadata mismatch; no files changed")
    else:
        p.mkdir(parents=True)
        write_json(p / "metadata.json", {"created_at_utc": utc_now(), "identity": identity,
                                         "scope": "prediction errors only; no trading/profit evidence"})
    return p


def calendar_grid(pd, xcals, start, end, tz):
    cal = xcals.get_calendar("XNYS", start=start, end=end)
    sessions = cal.sessions_in_range(start, end)
    starts, ends = [], []
    for session in sessions:
        op = pd.Timestamp(cal.session_open(session)).tz_convert(tz)
        cl = pd.Timestamp(cal.session_close(session)).tz_convert(tz)
        for ts in pd.date_range(op, cl, freq="h", inclusive="left"):
            starts.append(ts)
            ends.append(min(ts + pd.Timedelta(hours=1), cl))
    return pd.DatetimeIndex(starts), pd.DatetimeIndex(ends)


def qc_data(args, p, out, pd, np, xcals):
    # Read only the protocol's four raw OHLC fields; never features/adjusted close.
    df = pd.read_parquet(args.data, columns=["symbol", "datetime"] + FEATURES)
    df = df.loc[df["symbol"] == p["symbol"], ["datetime"] + FEATURES].copy()
    qc = {"checked_at_utc": utc_now(), "status": "STOP", "symbol": p["symbol"],
          "rows": len(df), "issues": [], "unscored": []}

    def stop(msg, evidence=None):
        qc["issues"].append({"reason": msg, "evidence": evidence})
        write_json(out / "qc.json", qc)
        raise StopRun(msg)

    if df.empty:
        stop("No AAPL rows")
    try:
        dates = pd.to_datetime(df["datetime"], errors="raise")
        if dates.dt.tz is None:
            stop("Naive timestamps: timezone must not be guessed")
        dates = dates.dt.tz_convert(p["timezone"])
    except StopRun:
        raise
    except Exception as exc:
        stop("Timestamp parse failure", str(exc))
    df["datetime"] = dates
    if dates.isna().any() or dates.duplicated().any():
        stop("Missing or duplicate timestamps", dates[dates.isna() | dates.duplicated(False)].astype(str).head(20).tolist())
    if not dates.is_monotonic_increasing:
        stop("Input rows are not chronological; no silent sorting")
    try:
        values = df[FEATURES].to_numpy(dtype="float64")
    except (TypeError, ValueError) as exc:
        stop("Non-numeric OHLC", str(exc))
    bad = (~np.isfinite(values)).any(axis=1) | (values <= 0).any(axis=1)
    bad |= values[:, 1] < np.maximum.reduce([values[:, 0], values[:, 2], values[:, 3]])
    bad |= values[:, 2] > np.minimum.reduce([values[:, 0], values[:, 1], values[:, 3]])
    if bad.any():
        stop("Invalid finite/positive/OHLC ordering", df.loc[bad].head(20).astype(str).to_dict("records"))
    for col in FEATURES:
        df[col] = df[col].astype("float64")
    first = dates.iloc[0].date().isoformat()
    last = dates.iloc[-1].date().isoformat()
    grid, bar_ends = calendar_grid(pd, xcals, first, last, p["timezone"])
    non_grid = ~dates.isin(grid)
    if non_grid.any():
        stop("STOP time fields do not match XNYS 09:30 hourly interval-start grid; no offset guessed",
             dates[non_grid].astype(str).head(30).tolist())
    # End the historical assessment at the last observed bar, not a hypothetical future session.
    last_pos = grid.get_indexer([dates.iloc[-1]])[0]
    grid, bar_ends = grid[:last_pos + 1], bar_ends[:last_pos + 1]
    now = pd.Timestamp.now(tz=p["timezone"])
    incomplete = dates.map(dict(zip(grid, bar_ends))) > now
    if incomplete.any():
        stop("Dataset includes unfinished bars", dates[incomplete].astype(str).tolist())
    qc.update(status="PASS", first_timestamp=dates.iloc[0].isoformat(),
              last_timestamp=dates.iloc[-1].isoformat(), expected_grid_rows=len(grid),
              missing_grid_rows=len(grid) - len(df),
              calendar="XNYS session opens + hourly starts strictly before session close",
              interval="start timestamp; final daily bar may be shorter than one hour")
    df = df.set_index("datetime")
    threshold = pd.Timestamp(p["start_date"], tz=p["timezone"])
    # First target starts at/after July 1; its history may precede that date.
    target_pos = int(grid.searchsorted(threshold))
    first_anchor = max(p["context"] - 1, target_pos - 1)
    windows = []
    for index, anchor in enumerate(range(first_anchor, len(grid) - p["horizon"], p["stride"])):
        hist = grid[anchor - p["context"] + 1:anchor + 1]
        future = grid[anchor + 1:anchor + 1 + p["horizon"]]
        missing_hist = hist[~hist.isin(df.index)]
        missing_future = future[~future.isin(df.index)]
        entry = {"window_index": index, "last_input": hist[-1].isoformat(),
                 "target_timestamps": [t.isoformat() for t in future]}
        if len(missing_hist) or len(missing_future):
            entry.update(status="unscored", missing_input=[t.isoformat() for t in missing_hist],
                         missing_target=[t.isoformat() for t in missing_future])
            qc["unscored"].append(entry)
            continue
        if future[0] < threshold:
            stop("Target precedes frozen evaluation start")
        windows.append((entry, hist, future, bar_ends[anchor]))
        if len(windows) >= args.limit:
            break
    qc["planned_scorable_windows"] = len(windows)
    qc["candidate_windows_considered"] = (index + 1) if 'index' in locals() else 0
    qc["trailing_incomplete_horizon_not_scored"] = True
    write_json(out / "qc.json", qc)
    if not windows:
        raise StopRun("No scorable windows; see qc.json")
    return df, windows, qc


def local_predictor(source, paths, p, torch):
    # Import only the operator-supplied fixed local source tree.
    sys.path.insert(0, str(source))
    from model.kronos import Kronos, KronosTokenizer, KronosPredictor
    from safetensors.torch import load_model
    import model.kronos as source_module
    if not Path(source_module.__file__).resolve().is_relative_to(source):
        raise StopRun("Imported model does not originate in --source-root")
    model_cfg = json.loads(paths["model_config"].read_text())
    tok_cfg = json.loads(paths["tokenizer_config"].read_text())
    model = Kronos(**model_cfg)
    tokenizer = KronosTokenizer(**tok_cfg)
    load_model(model, str(paths["model_weights"]), strict=True, device="cpu")
    load_model(tokenizer, str(paths["tokenizer_weights"]), strict=True, device="cpu")
    model.eval()
    tokenizer.eval()
    for obj in [model, tokenizer]:
        for param in obj.parameters():
            param.requires_grad_(False)
    return KronosPredictor(model, tokenizer, device="cpu", max_context=p["sampling"]["max_context"])


def input_hash(hist_df):
    return digest_obj({"timestamps": [t.isoformat() for t in hist_df.index],
                       "features": FEATURES, "values": hist_df[FEATURES].values.tolist()})


def read_existing(path):
    records = []
    if path.exists():
        with path.open(encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                try:
                    row = json.loads(line)
                    checksum = row.pop("record_sha256")
                    if digest_obj(row) != checksum:
                        raise ValueError("record checksum mismatch")
                    row["record_sha256"] = checksum
                    records.append(row)
                except Exception as exc:
                    raise StopRun(f"Existing JSONL line {line_no} invalid; retained unchanged: {exc}") from exc
    return records


def summarize(records, p, np, smoke, limit):
    n = len(records)
    d = np.array([r["d"] for r in records], dtype=float)
    r = np.array([x["r"] for x in records], dtype=float)
    rh = np.array([x["r_hat"] for x in records], dtype=float)
    zmse = float(np.mean(r * r))
    mmse = float(np.mean((rh - r) ** 2))
    split = n // 2
    halves = [float(d[:split].mean()) if split else None,
              float(d[split:].mean()) if n else None]
    ci = None
    if n >= 20:
        rng = np.random.default_rng(p["CI"]["seed"])
        length, draws = p["CI"]["block_length"], p["CI"]["resamples"]
        count = math.ceil(n / length)
        offsets = np.arange(length)
        means = np.empty(draws)
        for b in range(draws):
            starts = rng.integers(0, n, size=count)
            idx = ((starts[:, None] + offsets) % n).reshape(-1)[:n]
            means[b] = d[idx].mean()
        ci = np.quantile(means, [0.025, 0.975]).tolist()
    partial = limit < p["max_windows"]
    passed = (not smoke and not partial and n >= 20 and ci[0] > 0
              and all(x is not None and x > 0 for x in halves))
    return {"generated_at_utc": utc_now(), "n": n,
            "status": "smoke_only" if smoke else "undetermined" if n < 20 or partial else
                      "prediction_gate_pass" if passed else "prediction_gate_not_passed",
            "gate_passed": bool(passed), "paired_d_mean": float(d.mean()),
            "zero_mse": zmse, "model_mse": mmse,
            "relative_mse_improvement": (zmse - mmse) / zmse if zmse > 0 else None,
            "circular_block_bootstrap_95CI": ci, "bootstrap": p["CI"],
            "chronological_halves_mean_d": halves,
            "descriptive_only": {"model_mae": float(np.abs(rh-r).mean()),
                                 "zero_mae": float(np.abs(r).mean()),
                                 "direction_agreement_including_zero": float(np.mean(np.sign(rh) == np.sign(r)))},
            "partial_limit_run": partial,
            "limits": ["retrospective prediction assessment; not true prospective validation",
                       "10-sample Monte Carlo approximation of conditional mean",
                       "CI depends on block assumption; missing windows and sample dependence remain relevant",
                       "no executable decision, fees, fills, returns curve, drawdown or capacity evaluated",
                       "MSE improvement neither necessary nor sufficient for trading profitability"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True)
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--model-dir", required=True)
    parser.add_argument("--tokenizer-dir", required=True)
    parser.add_argument("--protocol", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--limit", type=int, default=300)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.limit <= 300:
        parser.error("--limit must be 1..300; reduced limits cannot pass the final gate")
    forbid_network()
    p = load_protocol(args.protocol)
    identity, paths, source = artifacts(args, p)
    out = prepare_out(args.out, identity)
    import numpy as np
    import pandas as pd
    import exchange_calendars as xcals
    df, windows, qc = qc_data(args, p, out, pd, np, xcals)
    if args.smoke:
        windows = windows[:1]
    existing = read_existing(out / "predictions.jsonl")
    if len(existing) > len(windows):
        raise StopRun("Existing output has excess windows")
    for old, (entry, hist, future, origin_end) in zip(existing, windows):
        current = df.loc[hist, FEATURES]
        if (old["window_index"] != entry["window_index"] or old["input_sha256"] != input_hash(current)
                or old["target_timestamps"] != entry["target_timestamps"]
                or old["seed"] != p["sampling"]["seed_base"] + entry["window_index"]
                or old["actual_terminal_close"] != float(df.loc[future[-1], "close"])):
            raise StopRun("Existing window does not match current frozen inputs/targets")
    records = list(existing)
    predictor = None
    if len(records) < len(windows):
        import torch
        torch.set_num_threads(p["threads"])
        torch.set_num_interop_threads(1)
        torch.use_deterministic_algorithms(True)
        predictor = local_predictor(source, paths, p, torch)
        write_json(out / "runtime.json", {"started_at_utc": utc_now(), "device": "cpu",
                                         "torch_threads": torch.get_num_threads(),
                                         "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
                                         "model_training": predictor.model.training,
                                         "tokenizer_training": predictor.tokenizer.training})
        with (out / "predictions.jsonl").open("a", encoding="utf-8") as f:
            for entry, hist, future, origin_end in windows[len(records):]:
                seed = p["sampling"]["seed_base"] + entry["window_index"]
                random.seed(seed)
                np.random.seed(seed)
                torch.manual_seed(seed)
                x = df.loc[hist, FEATURES].copy()
                p0 = float(x.iloc[-1]["close"])
                t0 = time.perf_counter()
                generated_start = utc_now()
                with torch.inference_mode():
                    pred = predictor.predict(df=x, x_timestamp=pd.Series(hist),
                        y_timestamp=pd.Series(future), pred_len=p["horizon"],
                        T=p["sampling"]["T"], top_p=p["sampling"]["top_p"],
                        top_k=p["sampling"]["top_k"], sample_count=p["sampling"]["sample_count"],
                        verbose=False)
                pv = pred[FEATURES].to_numpy(dtype="float64")
                if pv.shape != (12, 4) or not np.isfinite(pv).all():
                    raise StopRun("Invalid prediction shape or nonfinite output; no scoring")
                actual = float(df.loc[future[-1], "close"])
                end_mean = float(pv[-1, 3])
                r_hat, r = end_mean / p0 - 1, actual / p0 - 1
                zse, mse = r*r, (r_hat-r)**2
                row = dict(entry, seed=seed, input_sha256=input_hash(x),
                           forecast_origin_bar_end=origin_end.isoformat(),
                           prediction_started_at_utc=generated_start, prediction_finished_at_utc=utc_now(),
                           p0=p0, prediction_features=FEATURES, prediction_12step_ohlc=pv.tolist(),
                           terminal_close_10sample_mean=end_mean, actual_terminal_close=actual,
                           r_hat=r_hat, r=r, zero_squared_error=zse, model_squared_error=mse,
                           d=zse-mse, elapsed_seconds=time.perf_counter()-t0,
                           predicted_nonpositive_values=int((pv <= 0).sum()),
                           scope="prediction only; future OHLC never supplied to predictor")
                row["record_sha256"] = digest_obj(row)
                f.write(canonical(row) + "\n")
                f.flush()
                os.fsync(f.fileno())
                records.append(row)
                print(f"saved window={entry['window_index']} scored={len(records)}", flush=True)
    summary = summarize(records, p, np, args.smoke, args.limit)
    summary["qc_status"] = qc["status"]
    summary["unscored_count"] = len(qc["unscored"])
    summary["resumed_records"] = len(existing)
    write_json(out / "summary.json", summary)
    print(canonical({"status": summary["status"], "n": len(records), "out": str(out)}))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"STOP {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
        raise SystemExit(2)

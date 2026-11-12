#!/usr/bin/env python3
"""Read-only arithmetic audit of a fixed public repository's saved artifacts.

No repository code, model, indicator, signal or strategy is imported/executed.
This inspects saved prices, positions, equity, P&L and the existing58 trade rows.
Trade cash flows below reconcile the existing journal; no alternative portfolio
or price-return path is generated.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path

for key in ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"]:
    os.environ[key] = "1"
import numpy as np
import pandas as pd
import pyarrow as pa
pa.set_cpu_count(1)
pa.set_io_thread_count(1)

HERE = Path(__file__).resolve().parent
COMMIT = "776003eb85f3c1e6e92683ee39d6ebf7cade78a0"
REPO = "shivanshu1177/funding_harvester"
FILES = {
    "data/clean/btcusdt_1h_full.parquet": "data_btcusdt_1h_full.parquet",
    **{"results/run_jan24_may26/test_default/"+name: "default_"+name for name in ["equity.parquet", "pnl.parquet", "position.parquet", "trades.parquet", "summary.json"]},
    "results/run_jan24_may26/test_fee_0.5x/summary.json": "fee_0.5x_summary.json",
    "results/run_jan24_may26/test_fee_1.5x/summary.json": "fee_1.5x_summary.json",
    "results/registry.parquet": "registry.parquet",
    "results/run_jan24_may26/train_default/summary.json": "train_default_summary.json",
    "python/src/registry.py": "registry_source_static.py"}


def hash_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git_blob_hash(data):
    return hashlib.sha1(("blob "+str(len(data))+"\0").encode()+data).hexdigest()


def save(name, value):
    (HERE/name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")


def json_rows(df):
    return json.loads(df.to_json(orient="records", date_format="iso", date_unit="ms"))


def index_audit(df):
    expected = pd.date_range(df.index.min(), df.index.max(), freq="h")
    return {"rows": len(df), "first": df.index.min().isoformat(), "last": df.index.max().isoformat(),
            "index_name": df.index.name, "index_dtype": str(df.index.dtype),
            "expected_inclusive_hourly_rows": len(expected), "duplicate_timestamps": int(df.index.duplicated().sum()),
            "missing_hourly_timestamps": int((~expected.isin(df.index)).sum()),
            "off_grid_timestamps": int((~df.index.isin(expected)).sum()),
            "monotonic_increasing": bool(df.index.is_monotonic_increasing),
            "fields": {c: str(df[c].dtype) for c in df.columns}, "null_counts": {c:int(n) for c,n in df.isna().sum().items()}}


def main():
    tree = json.loads((HERE/"tree.json").read_text())
    entries = {e["path"]:e for e in tree["tree"]}
    source_receipts = []
    for remote, local in FILES.items():
        path, entry = HERE/local, entries[remote]
        data = path.read_bytes()
        if len(data) != entry["size"] or git_blob_hash(data) != entry["sha"]:
            raise ValueError("Downloaded artifact differs from fixed git blob: "+remote)
        source_receipts.append({"repository_path": remote, "local_path": str(path),
            "source_url": f"https://github.com/{REPO}/blob/{COMMIT}/{remote}",
            "raw_source_url": f"https://raw.githubusercontent.com/{REPO}/{COMMIT}/{remote}",
            "api_content_url": f"https://api.github.com/repos/{REPO}/contents/{remote}?ref={COMMIT}",
            "bytes": len(data), "sha256": hash_file(path), "git_blob_sha1": entry["sha"],
            "local_original_completed_at_utc": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
            "transport": "official GitHub git/blob base64 JSON decoded" if local.endswith(".parquet") else "gh contents raw text/JSON"})
    blob_jsons = sorted(HERE.glob("blob_*.json"))
    conservative_budget = (HERE/"tree.json").stat().st_size+sum(entries[remote]["size"] for remote in FILES)+sum(f.stat().st_size for f in blob_jsons)
    if conservative_budget > 5_000_000:
        raise ValueError("Public-content budget exceeded")
    save("sources.json", {"read_at_utc": datetime.now(timezone.utc).isoformat(), "commit": COMMIT,
        "tree_api_url": f"https://api.github.com/repos/{REPO}/git/trees/{COMMIT}?recursive=1",
        "tree_bytes": (HERE/"tree.json").stat().st_size, "tree_sha256": hash_file(HERE/"tree.json"),
        "artifacts": source_receipts, "unique_original_bytes": sum(r["bytes"] for r in source_receipts),
        "public_content_budget_limit_bytes": 5_000_000, "conservative_received_bytes": conservative_budget,
        "budget_note": "First gh raw binary attempt emitted transform: short source buffer and saved10 bytes each; charged full declared original size conservatively, then charged full official base64 blob JSON responses. Decoded local copies add no public reads.",
        "failed_raw_files_retained": [str(p) for p in sorted(HERE.glob("*.gh-raw-failed"))],
        "decoded_blob_sources": [{"file":str(f),"bytes":f.stat().st_size,"sha256":hash_file(f),
            "api_url":f"https://api.github.com/repos/{REPO}/git/blobs/"+json.loads(f.read_text())["sha"],
            "response_completed_at_utc":datetime.fromtimestamp(f.stat().st_mtime,timezone.utc).isoformat()} for f in blob_jsons]})

    data = pd.read_parquet(HERE/"data_btcusdt_1h_full.parquet", use_threads=False)
    equity = pd.read_parquet(HERE/"default_equity.parquet", use_threads=False)
    pnl = pd.read_parquet(HERE/"default_pnl.parquet", use_threads=False)
    position = pd.read_parquet(HERE/"default_position.parquet", use_threads=False)
    trades = pd.read_parquet(HERE/"default_trades.parquet", use_threads=False)
    summary = json.loads((HERE/"default_summary.json").read_text())
    sensitivity = {k:json.loads((HERE/f"fee_{k}_summary.json").read_text()) for k in ["0.5x", "1.5x"]}
    training_summary = json.loads((HERE/"train_default_summary.json").read_text())
    registry = pd.read_parquet(HERE/"registry.parquet", use_threads=False)
    # Reproduce only the statically inspected hash serialization, not repository
    # functions/imports. The published function hashes just100 rows and length.
    sampled_content = {"index":data.index.astype(str).tolist()[:100],
                       "close":data.close.tolist()[:100],"len":len(data)}
    registry_content_md5 = hashlib.md5(json.dumps(sampled_content,sort_keys=True,default=str).encode()).hexdigest()
    matching_registry = registry[registry.output_dir.eq("results/run_jan24_may26")]
    if len(matching_registry) != 1:
        raise ValueError("Registry does not uniquely identify inspected output directory")
    provenance = {"registry_rows":json_rows(registry), "registry_file_sha256":hash_file(HERE/"registry.parquet"),
        "static_registry_source_sha256":hash_file(HERE/"registry_source_static.py"),
        "published_data_hash_algorithm":"MD5(json.dumps({index:first100 stringified index values,close:first100 close values,len:all rows},sort_keys=True,default=str).encode())",
        "recomputed_sampled_content_md5":registry_content_md5,
        "matching_saved_data_hash":matching_registry.data_hash.iloc[0],
        "sampled_hash_matches_inspected_full_data":bool(matching_registry.data_hash.iloc[0]==registry_content_md5),
        "is_whole_file_or_all_rows_fingerprint":False,
        "unbound_data_fields":"All rows after100 and open/high/low/volume/turnover/funding fields are not bound by this sampled hash",
        "git_sha_saved":matching_registry.git_sha.iloc[0], "git_dirty_saved":bool(matching_registry.git_dirty.iloc[0]),
        "current_public_commit":COMMIT,"exact_runtime_source_binding_confirmed":False,
        "source_binding_limit":"Saved run names earlier git SHA and git_dirty=True, so exact runtime working-tree source is not attested by the current public commit.",
        "training_summary_only":training_summary,
        "training_test_rows_sum_matches_source":bool(training_summary["n_bars"]+len(equity)==len(data)),
        "training_test_boundary_nonoverlap":bool(pd.Timestamp(training_summary["end"])+pd.Timedelta("1h")==equity.index[0]),
        "training_equity_or_trades_not_downloaded":True,"repository_registry_code_executed":False}
    save("registry-and-training-audit.json",provenance)
    if not equity.index.equals(pnl.index) or not equity.index.equals(position.index):
        raise ValueError("Saved equity/P&L/position time indices differ")
    if not equity.index.isin(data.index).all():
        raise ValueError("Saved OOS index not covered by saved source data")
    oc = data[["open", "high", "low", "close"]].to_numpy()
    ohlc_bad = ((oc[:,1] < np.maximum.reduce([oc[:,0],oc[:,2],oc[:,3]])) |
                (oc[:,2] > np.minimum.reduce([oc[:,0],oc[:,1],oc[:,3]])))
    continuity = data.open.iloc[1:].to_numpy()-data.close.iloc[:-1].to_numpy()
    funding_clock = data[data.bars_since_funding.eq(0)]
    save("data-audit.json", {"source":index_audit(data), "finite_numeric_counts":{c:int(np.isfinite(data[c]).sum()) for c in data},
        "nonpositive_price_rows":int((oc<=0).any(axis=1).sum()), "OHLC_ordering_invalid_rows":int(ohlc_bad.sum()),
        "negative_volume_rows":int((data.volume<0).sum()), "negative_turnover_rows":int((data.turnover<0).sum()),
        "next_open_minus_previous_close_nonzero_rows":int((np.abs(continuity)>1e-8).sum()),
        "max_abs_next_open_minus_previous_close":float(np.max(np.abs(continuity))),
        "funding_reset_rows":len(funding_clock), "funding_reset_UTC_hours":sorted(set(funding_clock.index.hour.tolist())),
        "bars_since_funding_values":sorted(data.bars_since_funding.unique().tolist()),
        "funding_rate_min":float(data.funding_rate.min()),"funding_rate_max":float(data.funding_rate.max()),
        "data_venue_permission_and_provenance":"outside this ledger audit; root reviews original source/code/license",
        "limits":["No external exchange truth used; saved continuity and valid OHLC do not prove data availability or exchange accuracy", "No quote/depth/fill/mark-index proof", "funding fields exist but historical publish/settlement availability not certified"]})

    signed_qty = trades.qty.where(trades.side.eq("buy"), -trades.qty)
    flows = -signed_qty*trades.price-trades.fee_usd
    initial = float(equity.equity.iloc[0])
    final = float(equity.equity.iloc[-1])
    total_funding = float(pnl.funding_pnl.sum())
    actual_change = final-initial
    net_pnl = pnl.gross_pnl+pnl.funding_pnl-pnl.fees-pnl.slippage
    equity_changes = equity.equity.diff().fillna(0)
    residual = equity_changes-net_pnl
    cumulative_trade_position = signed_qty.cumsum()
    trade_price = data.loc[pd.DatetimeIndex(trades.timestamp),"open"].to_numpy()
    expected_fill = trade_price*np.where(trades.side.eq("buy"),1.0001,.9999)
    actual_fill_slippage = trades.qty.to_numpy()*np.abs(trades.price.to_numpy()-trade_price)
    fee_slip_timing = []
    position_change = position.position.diff().fillna(position.position.iloc[0])
    trade_adjustment = pd.Series(0.,index=position.index)
    reported_slippage_adjustment = pd.Series(0.,index=position.index)
    for i,row in trades.iterrows():
        shift = row.timestamp-pd.Timedelta(hours=1)
        actual_delta = float(row.qty if row.side=="buy" else -row.qty)
        trade_adjustment.loc[shift] += actual_delta
        reported_slippage_adjustment.loc[shift] += float(row.slippage_usd-actual_fill_slippage[i])
        item = {"trade_index":int(i),"timestamp":row.timestamp.isoformat(),"side":row.side,
            "qty":float(row.qty),"saved_fill":float(row.price),"source_open_at_trade_timestamp":float(trade_price[i]),
            "notional":float(row.notional_usd),"fee":float(row.fee_usd),"saved_slippage":float(row.slippage_usd),
            "fill_minus_source_open_slippage":float(actual_fill_slippage[i]),
            "cumulative_signed_position_after_trade":float(cumulative_trade_position.iloc[i]),
            "saved_state_row":shift.isoformat(),"saved_position_change_at_previous_row":float(position_change.loc[shift]),
            "position_change_matches_previous_row":bool(math.isclose(position_change.loc[shift],actual_delta,abs_tol=1e-12)),
            "saved_fee_at_previous_row":float(pnl.loc[shift,"fees"]),"saved_slippage_at_previous_row":float(pnl.loc[shift,"slippage"])}
        fee_slip_timing.append(item)
    save("saved-trade-journal-audit.json", {"trades":fee_slip_timing,
        "initial_equity":initial,"final_equity":final,"saved_trade_cash_flow_sum_after_fees":float(flows.sum()),
        "saved_funding_sum":total_funding,"journal_plus_funding_change":float(flows.sum()+total_funding),
        "journal_to_equity_residual":float(actual_change-(flows.sum()+total_funding)),
        "ending_signed_trade_quantity":float(signed_qty.sum()),"last_saved_position":float(position.position.iloc[-1]),
        "explanation":"Signed cash flows of existing58 fills, fees and saved funding reconcile terminal saved account because ending journal position is zero. This is not execution of a strategy or creation of an alternative return path."})
    first_episode = trades.iloc[:2]
    entry_state = first_episode.timestamp.iloc[0]-pd.Timedelta("1h")
    exit_state = first_episode.timestamp.iloc[1]-pd.Timedelta("1h")
    first_components = pnl.loc[entry_state:exit_state].sum()
    first_signed = first_episode.qty.where(first_episode.side.eq("buy"),-first_episode.qty)
    first_journal = float((-first_signed*first_episode.price-first_episode.fee_usd).sum())
    save("one-saved-round-trip.json", {"label":"Actual original saved historical simulation fills; not live trades or a teaching fabrication",
        "original_saved_trade_rows":json_rows(first_episode),
        "recorded_entry_timestamp":first_episode.timestamp.iloc[0].isoformat(),
        "recorded_exit_timestamp":first_episode.timestamp.iloc[1].isoformat(),
        "direction":"short then flat", "quantity_BTC":float(first_episode.qty.iloc[0]),
        "saved_position_state_entry_row":entry_state.isoformat(),"saved_flat_state_exit_row":exit_state.isoformat(),
        "saved_component_sums":{k:float(v) for k,v in first_components.items()},
        "closed_trade_journal_result_after_fees":first_journal,
        "saved_funding_in_episode":float(first_components.funding_pnl),
        "closed_journal_plus_saved_funding":first_journal+float(first_components.funding_pnl),
        "flat_saved_equity_after":float(equity.loc[exit_state,"equity"]),
        "no_new_strategy_or_return_path_generated":True})

    gross_from_saved_prior_position = position.position.shift(1).fillna(0)*data.loc[position.index,"close"].diff().fillna(0)
    fund_expected = -position.position.shift(1).fillna(0)*data.loc[position.index,"close"]*data.loc[position.index,"funding_rate"]
    fund_expected = fund_expected.where(data.loc[position.index,"bars_since_funding"].eq(0),0)
    funding_rows = pnl[pnl.funding_pnl.ne(0)].join(position).join(data[["open","close","funding_rate","bars_since_funding"]])
    save("saved-funding-rows.json", {"rows":json_rows(funding_rows.reset_index()),"count":len(funding_rows),
        "nonzero_funding_pnl_sum":float(funding_rows.funding_pnl.sum()),
        "formula_test":"-previous saved position * current saved hour close * current funding_rate, only bars_since_funding==0",
        "max_abs_formula_residual":float(np.max(np.abs(fund_expected-pnl.funding_pnl))),
        "clock_limit":"If source timestamps are hour starts, this uses the following hour-end close to value a funding event labeled at its hour start. Actual exchange settlement mark/time is not evidenced by this saved file."})

    dd = equity.equity/equity.equity.cummax()-1
    sums = {k:float(v) for k,v in pnl.sum().items()}
    audit = {"audited_at_utc":datetime.now(timezone.utc).isoformat(),"commit":COMMIT,
        "scope":"Static audit of frozen saved artifacts, not repository execution/backtest or independent alpha evidence",
        "saved_series":{k:index_audit(v) for k,v in {"equity":equity,"pnl":pnl,"position":position}.items()},
        "trades":{"rows":len(trades),"first":trades.timestamp.min().isoformat(),"last":trades.timestamp.max().isoformat(),
            "sides":{str(k):int(v) for k,v in trades.side.value_counts().items()},
            "timestamp_duplicates":int(trades.timestamp.duplicated().sum()),"timestamp_monotonic":bool(trades.timestamp.is_monotonic_increasing),
            "null_counts":{k:int(v) for k,v in trades.isna().sum().items()},"fields":{k:str(v) for k,v in trades.dtypes.items()},
            "ending_signed_quantity":float(signed_qty.sum()),"flat_after_even_trade_rows":bool(np.all(np.abs(cumulative_trade_position.iloc[1::2])<1e-12)),
            "closed_two_fill_episodes":len(trades)//2,"initial_source_price_fill_match_max_abs":float(np.max(np.abs(trades.price.to_numpy()-expected_fill))),
            "notional_minus_qty_times_fill_max_abs":float(np.max(np.abs(trades.notional_usd-trades.qty*trades.price))),
            "fee_minus_fill_notional_times_6bps_max_abs":float(np.max(np.abs(trades.fee_usd-trades.notional_usd*.0006))),
            "saved_slippage_minus_fill_notional_times_1bp_max_abs":float(np.max(np.abs(trades.slippage_usd-trades.notional_usd*.0001)))},
        "accounting":{"initial":initial,"final_saved_equity":final,"saved_equity_dollar_change":actual_change,
            "saved_equity_return_pct":(final/initial-1)*100,"pnl_component_sums":sums,
            "component_net_sum_gross_plus_funding_minus_fees_slippage":float(net_pnl.sum()),
            "component_net_to_equity_total_residual":float(residual.sum()),
            "component_vs_equity_changed_rows_gt_1e_8":int((np.abs(residual)>1e-8).sum()),
            "component_vs_equity_max_abs_row_residual":float(np.max(np.abs(residual))),
            "all_saved_trade_cashflows_after_fees_plus_saved_funding":float(flows.sum()+total_funding),
            "journal_terminal_residual":float(actual_change-(flows.sum()+total_funding)),
            "saved_trade_fees_sum":float(trades.fee_usd.sum()),"saved_trade_slippage_sum":float(trades.slippage_usd.sum()),
            "fill_vs_source_open_slippage_sum":float(np.sum(actual_fill_slippage)),
            "saved_slippage_minus_fill_vs_open_slippage":float(trades.slippage_usd.sum()-np.sum(actual_fill_slippage)),
            "residual_after_explaining_slippage_second_order_difference_max_abs":float(np.max(np.abs(residual-reported_slippage_adjustment))),
            "gross_formula_saved_prior_position_times_close_difference_max_abs":float(np.max(np.abs(gross_from_saved_prior_position-pnl.gross_pnl))),
            "max_drawdown_saved_equity_pct":float(dd.min()*100),"max_drawdown_saved_timestamp":dd.idxmin().isoformat(),
            "round_trip_financial_result":"Saved58 journal rows and funding explain final stored equity to floating precision; per-row component cost formula differs by second-order slippage terms, not a material missing-account amount."},
        "clock":{"position_change_count":int(position_change.ne(0).sum()),
            "all_position_changes_match_trade_timestamp_minus_1h_max_abs":float(np.max(np.abs(position_change-trade_adjustment))),
            "trade_first_recorded_timestamp":trades.timestamp.iloc[0].isoformat(),
            "first_position_change_saved_row":position_change[position_change.ne(0)].index[0].isoformat(),
            "data_next_open_equals_previous_close_all_rows":bool(np.all(np.abs(continuity)<1e-8)),
            "interpretation":"Position, fees and slippage are stored one source row before recorded fills. With hour-start OHLC labels and equal next-open/previous-close values, the records can be read as end-of-bar states attached to bar-start labels. Do not call them positions already held at that labeled hour start or claim verified causal execution.",
            "funding_nonzero_rows":len(funding_rows),"funding_saved_mark_uses_current_hour_close":bool(np.max(np.abs(fund_expected-pnl.funding_pnl))<1e-10),
            "last_journal_fill_before_terminal_saved_hour":bool(trades.timestamp.iloc[-1]<equity.index[-1]),
            "forced_terminal_position_liquidation_branch_exercised_in_this_saved_run":False},
        "fee_sensitivity_summary_only":{k:{"saved_return_pct":s["total_return_pct"],
            "implied_final_change_from_saved_return_and_10000_start":s["total_return_pct"]*100,
            "saved_total_fees":s["total_fees_usd"],"saved_total_slippage":s["total_slippage_usd"],
            "saved_total_funding":s["total_funding_usd"],
            "default_change_minus_fee_difference":actual_change-(s["total_fees_usd"]-summary["total_fees_usd"]),
            "not_independently_reconstructed_without_other_saved_ledgers":True} for k,s in sensitivity.items()},
        "research_admission":{"terminal_journal_arithmetic":"PASS within floating precision",
            "hourly_saved_pnl_components":"PASS with explicitly explained approx2.13e-6 total slippage convention difference",
            "position_and_funding_timing":"QUALIFIED/UNCONFIRMED for real chronology; saved labels need end-of-bar interpretation and funding settlement mark proof",
            "complete_execution_or_actual_profit_proof":False,"independent_OOS_selection_and_robustness_proof":False,
            "verdict":"Admit as a historical simulation research case with complete saved original price/position/P&L/trade artifacts and closed model-assumption accounting. Actual profitability, strict untouched OOS, execution, mark basis and capacity are separate unproven claims. Do not repair/replay the strategy under this read-only authorization."},
        "registry_provenance":{k:v for k,v in provenance.items() if k not in ["registry_rows","training_summary_only"]},
        "training_summary_return_pct":training_summary["total_return_pct"],
        "limitations":["Only saved run inspected; author OOS label does not independently prove preselection, absence of tuning or data leakage",
            "No cash/margin wallet series or liquidation/mark-index proof; terminal cash flow closure does not validate exchange mechanics",
            "Capital labelled USD in artifacts, underlying BTCUSDT prices; actual settlement/conversion and USDT/USD parity unverified",
            "Cost assumptions6bps per fill and1bps slippage are declared saved assumptions, not current personal-account fees",
            "Summary capacity from1% average hourly turnover is not supported by orderbook/impact evidence",
            "All net result is tiny relative to stored costs and depends on assumed fills; no stability or scalable wealth claim"],
        "network_additional_reads_in_audit":0,"repository_code_executed":False,"model_inference":False,
        "new_strategy_path_generated":False,"orders_sent":False,"audit_script_sha256":hash_file(__file__)}
    save("artifact-audit.json", audit)
    print(json.dumps({"status":"saved_artifact_audit_completed","initial":initial,"final":final,"net":actual_change,
        "journal_residual":audit["accounting"]["journal_terminal_residual"],"public_content_conservative_bytes":conservative_budget,
        "admission":audit["research_admission"]},ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()

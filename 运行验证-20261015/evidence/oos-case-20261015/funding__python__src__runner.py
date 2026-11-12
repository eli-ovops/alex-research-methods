from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import structlog

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "strategies"))

from backtester import Backtester, BacktestConfig, BacktestResult, FeeModel
from data_loader import load_multi_asset
from funding_arb import FundingArbConfig, FundingArbStrategy
from logging_setup import configure_logging
from portfolio import PortfolioResult, portfolio_metrics
from registry import append_run, config_hash, data_hash

logger = structlog.get_logger(__name__)


# -----------------------------------------------------------------------------
# Train / OOS split
# -----------------------------------------------------------------------------
def split_oos(
    data: pd.DataFrame,
    oos_start: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split data at an explicit calendar date.

    Args:
        oos_start: ISO date string, e.g. '2025-10-01'

    Returns:
        (train, oos) DataFrames.  The split is strict: train < oos_start <= oos.
    """
    cutoff = pd.Timestamp(oos_start, tz="UTC")
    train = data[data.index < cutoff].copy()
    oos   = data[data.index >= cutoff].copy()
    logger.info(
        "OOS split at %s: train=%d bars [%s → %s], oos=%d bars [%s → %s]",
        oos_start,
        len(train), train.index.min(), train.index.max(),
        len(oos),   oos.index.min(),   oos.index.max(),
    )
    return train, oos


# -----------------------------------------------------------------------------
# Run one backtest + persist
# -----------------------------------------------------------------------------
def run_one(
    name: str,
    data: pd.DataFrame,
    strat_cfg: FundingArbConfig,
    bt_cfg: BacktestConfig,
    output_root: Path,
    label: str = "",          # e.g. "IN-SAMPLE" or "OUT-OF-SAMPLE"
    context_data: pd.DataFrame | None = None,
    initial_state: dict | None = None,
) -> dict:
    logger.info("running %s (%s) on %d bars", name, label or "–", len(data))
    engine   = Backtester(bt_cfg)
    strategy = FundingArbStrategy(strat_cfg)
    result   = engine.run(data, strategy, context_data=context_data, initial_state=initial_state)

    out_dir = output_root / name
    out_dir.mkdir(parents=True, exist_ok=True)

    result.equity.to_frame("equity").to_parquet(out_dir / "equity.parquet")
    result.position.to_frame("position").to_parquet(out_dir / "position.parquet")
    result.pnl_decomposition.to_parquet(out_dir / "pnl.parquet")
    if not result.trades.empty:
        result.trades.to_parquet(out_dir / "trades.parquet")

    summary = result.summary()
    summary["name"]            = name
    summary["label"]           = label
    summary["n_bars"]          = len(data)
    summary["start"]           = str(data.index.min())
    summary["end"]             = str(data.index.max())
    summary["strategy_config"] = strat_cfg.to_dict()
    summary["fee_taker_bps"]   = bt_cfg.fee_model.taker_bps
    summary["slippage_bps"]    = bt_cfg.fee_model.slippage_bps

    with open(out_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)

    logger.info(
        "%s [%s]: return=%.2f%% sharpe=%.3f max_dd=%.2f%% trades=%d",
        name, label,
        summary["total_return_pct"],
        summary["sharpe_ratio"],
        summary["max_drawdown_pct"],
        summary["n_trades"],
    )
    return summary


# -----------------------------------------------------------------------------
# Buy-and-hold benchmark
# -----------------------------------------------------------------------------
def buy_and_hold(data: pd.DataFrame, starting_cash: float = 10_000.0) -> dict:
    first_close  = data["close"].iloc[0]
    last_close   = data["close"].iloc[-1]
    qty          = starting_cash / first_close
    total_return = qty * last_close / starting_cash - 1

    rets          = data["close"].pct_change().fillna(0.0)
    annualization = np.sqrt(24 * 365)
    sharpe        = (rets.mean() / rets.std() * annualization) if rets.std() > 0 else 0.0

    eq  = qty * data["close"]
    max_dd = ((eq - eq.cummax()) / eq.cummax()).min()

    return {
        "name": "buy_and_hold",
        "total_return_pct": total_return * 100,
        "sharpe_ratio":     sharpe,
        "max_drawdown_pct": max_dd * 100,
        "n_trades":         1,
    }


# -----------------------------------------------------------------------------
# Capacity estimate
# -----------------------------------------------------------------------------
def estimate_capacity(
    result_summary: dict,
    data: pd.DataFrame,
    base_notional_usd: float,
) -> dict:
    """
    Rough capacity estimate for the strategy.

    Method: volume-based market-impact model.
      - Assume we want our trade to be < 1% of average hourly volume
        (conservative to avoid moving the market).
      - Scale base_notional linearly to find the threshold.
      - At > 5× base_notional, slippage assumption of 1 bps breaks down —
        flag that explicitly.

    Returns a dict with capacity fields added to the summary.
    """
    avg_hourly_vol_usd = (data["close"] * data["volume"]).mean()
    max_notional_1pct  = avg_hourly_vol_usd * 0.01   # 1% of avg hourly volume
    scale_factor       = max_notional_1pct / base_notional_usd

    capacity_usd = base_notional_usd * scale_factor
    # Account for concurrent positions (strategy runs one at a time):
    capacity_aum = capacity_usd  # single-position strategy, notional = deployed AUM

    return {
        "avg_hourly_vol_usd":   round(avg_hourly_vol_usd),
        "capacity_1pct_vol_usd": round(capacity_usd),
        "capacity_note": (
            f"At ${capacity_usd:,.0f} notional per trade (<1% avg hourly vol), "
            f"slippage assumption of {result_summary.get('slippage_bps', 1):.1f} bps "
            f"remains valid. Above this level, use a non-linear impact model."
        ),
    }


# -----------------------------------------------------------------------------
# Hyperparameter sweep (Phase 1)
# -----------------------------------------------------------------------------

# Grid definition — kept at module level so _run_sweep_single can be pickled.
_SWEEP_GRID: dict[str, list[Any]] = {
    "z_window":        [45, 60, 75],
    "momentum_window": [3, 5, 7],
    "vol_window":      [12, 24, 36],
    "vol_pct_lookback": [360, 720, 1080],
}


def _run_sweep_single(
    data_bytes: bytes,
    base_cfg_dict: dict[str, Any],
    bt_cfg_dict: dict[str, Any],
    z_window: int,
    momentum_window: int,
    vol_window: int,
    vol_pct_lookback: int,
) -> dict[str, Any]:
    """
    Run a single sweep configuration.  Module-level so it is picklable for
    ProcessPoolExecutor workers.

    Args:
        data_bytes:      pickled pd.DataFrame (IS / train slice).
        base_cfg_dict:   asdict(FundingArbConfig) for the baseline.
        bt_cfg_dict:     BacktestConfig fields (without fee_model object).
        z_window, momentum_window, vol_window, vol_pct_lookback: sweep values.

    Returns:
        dict of metrics plus the four sweep parameter values.
    """
    import pickle

    data: pd.DataFrame = pickle.loads(data_bytes)  # noqa: S301

    # Reconstruct configs
    fee_dict = bt_cfg_dict.get("fee_model", {})
    fee_model = FeeModel(
        taker_bps=fee_dict.get("taker_bps", 6.0),
        slippage_bps=fee_dict.get("slippage_bps", 1.0),
    )
    bt_cfg = BacktestConfig(
        starting_cash=bt_cfg_dict.get("starting_cash", 10_000.0),
        fee_model=fee_model,
        max_leverage=bt_cfg_dict.get("max_leverage", 3.0),
        next_bar_execution=bt_cfg_dict.get("next_bar_execution", True),
        funding_enabled=bt_cfg_dict.get("funding_enabled", True),
    )

    # Warmup must cover the longest lookback window.
    warmup = vol_pct_lookback + vol_window
    cfg_kwargs = {**base_cfg_dict,
                  "z_window":         z_window,
                  "momentum_window":  momentum_window,
                  "vol_window":       vol_window,
                  "vol_pct_lookback": vol_pct_lookback,
                  "warmup_bars":      warmup}
    strat_cfg = FundingArbConfig(**cfg_kwargs)

    engine   = Backtester(bt_cfg)
    strategy = FundingArbStrategy(strat_cfg)
    result   = engine.run(data, strategy)
    summary  = result.summary()

    # Gross Sharpe (inline to avoid circular import issues in worker)
    import math
    pnl = result.pnl_decomposition
    start_cash = bt_cfg.starting_cash
    gross_eq = (start_cash + (pnl["gross_pnl"] + pnl["funding_pnl"]).cumsum()).clip(lower=1e-9)
    gross_rets = gross_eq.pct_change().fillna(0.0)
    std = float(gross_rets.std())
    g_sr = float(gross_rets.mean() / std * math.sqrt(24 * 365)) if std > 1e-15 else 0.0

    return {
        "z_window":         z_window,
        "momentum_window":  momentum_window,
        "vol_window":       vol_window,
        "vol_pct_lookback": vol_pct_lookback,
        "warmup_bars":      warmup,
        "net_sharpe":       summary["sharpe_ratio"],
        "gross_sharpe":     g_sr,
        "n_trades":         summary["n_trades"],
        "max_dd_pct":       summary["max_drawdown_pct"],
        "total_return_pct": summary["total_return_pct"],
        "total_fees_usd":   summary["total_fees_usd"],
        "total_slippage_usd": summary["total_slippage_usd"],
    }


def _compute_stability_flags(
    results_df: pd.DataFrame,
    metric: str = "net_sharpe",
) -> pd.DataFrame:
    """
    For each sweep parameter, flag whether any adjacent grid values reverse
    the sign of the mean metric (marginalizing over the other 3 parameters).

    Returns the results_df with boolean '{param}_unstable' columns appended.
    """
    df = results_df.copy()
    params = list(_SWEEP_GRID.keys())

    for param in params:
        grid_vals = sorted(_SWEEP_GRID[param])
        mean_by_val = (
            df.groupby(param)[metric].mean()
              .reindex(grid_vals)
        )
        unstable = False
        for i in range(len(grid_vals) - 1):
            a = mean_by_val.iloc[i]
            b = mean_by_val.iloc[i + 1]
            if not (pd.isna(a) or pd.isna(b)):
                if (a > 0) != (b > 0):
                    unstable = True
                    break
        df[f"{param}_unstable"] = unstable

    return df


def _run_grid_on_is(
    is_data: pd.DataFrame,
    base_cfg: FundingArbConfig,
    bt_cfg: BacktestConfig,
    n_jobs: int = -1,
) -> tuple[FundingArbConfig, pd.DataFrame]:
    """
    Run the 81-config grid on pre-split IS data.

    Args:
        is_data:  Training slice only (no OOS — caller is responsible for split).
        base_cfg: Baseline FundingArbConfig; non-swept params held fixed.
        bt_cfg:   BacktestConfig applied to all configs.
        n_jobs:   Parallel workers (-1 = all CPUs, 1 = serial).

    Returns:
        (best_cfg, sweep_df) where best_cfg is the config with highest IS
        gross_sharpe and sweep_df has one row per config with metrics and
        stability flags.
    """
    import pickle

    n_workers = n_jobs if n_jobs > 0 else (os.cpu_count() or 1)
    logger.info(
        "sweep: %d configs × %d bars IS, %d workers",
        81, len(is_data), n_workers,
    )

    base_dict = asdict(base_cfg)
    bt_dict   = {
        "starting_cash":      bt_cfg.starting_cash,
        "max_leverage":       bt_cfg.max_leverage,
        "next_bar_execution": bt_cfg.next_bar_execution,
        "funding_enabled":    bt_cfg.funding_enabled,
        "fee_model": {
            "taker_bps":    bt_cfg.fee_model.taker_bps,
            "slippage_bps": bt_cfg.fee_model.slippage_bps,
        },
    }

    data_bytes = pickle.dumps(is_data)

    configs = list(itertools.product(
        _SWEEP_GRID["z_window"],
        _SWEEP_GRID["momentum_window"],
        _SWEEP_GRID["vol_window"],
        _SWEEP_GRID["vol_pct_lookback"],
    ))

    results: list[dict[str, Any]] = []

    if n_workers == 1:
        for z, mom, vol, lbk in configs:
            r = _run_sweep_single(data_bytes, base_dict, bt_dict, z, mom, vol, lbk)
            results.append(r)
            logger.debug("sweep config z=%d mom=%d vol=%d lbk=%d → net_sr=%.3f",
                         z, mom, vol, lbk, r["net_sharpe"])
    else:
        futures = {}
        with ProcessPoolExecutor(max_workers=n_workers) as pool:
            for z, mom, vol, lbk in configs:
                fut = pool.submit(
                    _run_sweep_single, data_bytes, base_dict, bt_dict, z, mom, vol, lbk
                )
                futures[fut] = (z, mom, vol, lbk)
            for fut in as_completed(futures):
                z, mom, vol, lbk = futures[fut]
                try:
                    r = fut.result()
                    results.append(r)
                    logger.debug(
                        "sweep z=%d mom=%d vol=%d lbk=%d → net_sr=%.3f",
                        z, mom, vol, lbk, r["net_sharpe"],
                    )
                except Exception as exc:
                    logger.warning(
                        "sweep config z=%d mom=%d vol=%d lbk=%d failed: %s",
                        z, mom, vol, lbk, exc,
                    )

    sweep_df = pd.DataFrame(results)
    sweep_df = _compute_stability_flags(sweep_df)

    best_row = sweep_df.loc[sweep_df["gross_sharpe"].idxmax()]
    best_cfg = FundingArbConfig(**{
        **asdict(base_cfg),
        "z_window":         int(best_row["z_window"]),
        "momentum_window":  int(best_row["momentum_window"]),
        "vol_window":       int(best_row["vol_window"]),
        "vol_pct_lookback": int(best_row["vol_pct_lookback"]),
        "warmup_bars":      int(best_row["warmup_bars"]),
    })
    logger.info(
        "best IS config: z=%d mom=%d vol=%d lbk=%d → gross_sr=%.3f net_sr=%.3f",
        best_cfg.z_window, best_cfg.momentum_window,
        best_cfg.vol_window, best_cfg.vol_pct_lookback,
        float(best_row["gross_sharpe"]), float(best_row["net_sharpe"]),
    )
    return best_cfg, sweep_df


def run_hyperparameter_sweep(
    data: pd.DataFrame,
    base_cfg: FundingArbConfig,
    bt_cfg: BacktestConfig,
    output_root: Path,
    oos_start: str,
    n_jobs: int = -1,
) -> pd.DataFrame:
    """
    Run a 3^4 = 81-config grid search over signal hyperparameters.

    Sweep dimensions:
      z_window        ∈ {45, 60, 75}
      momentum_window ∈ {3, 5, 7}
      vol_window      ∈ {12, 24, 36}
      vol_pct_lookback ∈ {360, 720, 1080}

    **Partition**: trains on IS (train) data only.  OOS is not touched.

    Args:
        data:        Full dataset (unsplit).  Function handles IS/OOS split.
        base_cfg:    Baseline FundingArbConfig; non-swept params are held fixed.
        bt_cfg:      BacktestConfig (fees, starting_cash, etc.).
        output_root: Directory where sweep_results.csv and heatmaps are saved.
        oos_start:   ISO date string for IS/OOS split (OOS excluded from sweep).
        n_jobs:      Parallel workers.  -1 = all CPUs, 1 = serial.

    Returns:
        pd.DataFrame with one row per config and columns for all params +
        metrics + stability flags.
    """
    train, _ = split_oos(data, oos_start)
    _, sweep_df = _run_grid_on_is(train, base_cfg, bt_cfg, n_jobs)

    sweep_dir = output_root / "sweep"
    sweep_dir.mkdir(parents=True, exist_ok=True)
    sweep_df.to_csv(sweep_dir / "sweep_results.csv", index=False)
    logger.info("sweep complete: %d results saved to %s", len(sweep_df), sweep_dir)

    # Generate heatmaps for all 6 parameter pairs
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from reporting import plot_hyperparameter_heatmap

        param_pairs = list(itertools.combinations(list(_SWEEP_GRID.keys()), 2))
        for x_p, y_p in param_pairs:
            for metric in ["net_sharpe", "gross_sharpe"]:
                fname = f"heatmap_{y_p}_vs_{x_p}_{metric}.png"
                plot_hyperparameter_heatmap(
                    sweep_df, x_p, y_p, metric,
                    sweep_dir / fname,
                )
    except Exception as exc:
        logger.warning("heatmap generation failed: %s", exc)

    # Log stability flags
    for param in _SWEEP_GRID:
        flag_col = f"{param}_unstable"
        if flag_col in sweep_df.columns and sweep_df[flag_col].iloc[0]:
            logger.warning(
                "UNSTABLE: parameter '%s' has sign-reversal in net_sharpe "
                "across adjacent grid values — treat baseline result cautiously",
                param,
            )

    return sweep_df


# -----------------------------------------------------------------------------
# Multi-asset portfolio backtest
# -----------------------------------------------------------------------------

def run_portfolio_backtest(
    symbols: list[str],
    data_dict: dict[str, pd.DataFrame],
    strat_cfg: FundingArbConfig,
    bt_cfg: BacktestConfig,
    output_root: Path,
    oos_start: str,
    n_bootstrap: int = 10_000,
) -> tuple[dict[str, BacktestResult], PortfolioResult]:
    """
    Run per-asset OOS backtests and aggregate into portfolio metrics.

    Each asset is backtested independently (no shared capital pool).
    Portfolio P&L = sum of per-asset dollar P&L.

    Args:
        symbols:      Ordered list of asset symbols to backtest.
        data_dict:    Pre-loaded data for each symbol (full history).
        strat_cfg:    Strategy config applied to every asset.
        bt_cfg:       Backtest config (fees, starting_cash) applied to every asset.
        output_root:  Root directory; per-asset results written to output_root/<symbol>/.
        oos_start:    ISO date string for OOS split (same for all assets).
        n_bootstrap:  Resamples for portfolio Sharpe bootstrap CI.

    Returns:
        (results_by_asset, portfolio_result)
    """
    results_by_asset: dict[str, BacktestResult] = {}

    for sym in symbols:
        data = data_dict[sym]
        _, oos = split_oos(data, oos_start)
        # Run once, persist artifacts, and keep result in memory.
        engine   = Backtester(bt_cfg)
        strategy = FundingArbStrategy(strat_cfg)
        result   = engine.run(oos, strategy)
        results_by_asset[sym] = result

        out_dir = output_root / "portfolio" / sym
        out_dir.mkdir(parents=True, exist_ok=True)
        result.equity.to_frame("equity").to_parquet(out_dir / "equity.parquet")
        result.position.to_frame("position").to_parquet(out_dir / "position.parquet")
        result.pnl_decomposition.to_parquet(out_dir / "pnl.parquet")
        if not result.trades.empty:
            result.trades.to_parquet(out_dir / "trades.parquet")
        summary = result.summary()
        summary.update({
            "name": sym, "label": "OOS-PORTFOLIO",
            "n_bars": len(oos),
            "start": str(oos.index.min()), "end": str(oos.index.max()),
            "strategy_config": strat_cfg.to_dict(),
            "fee_taker_bps": bt_cfg.fee_model.taker_bps,
            "slippage_bps":  bt_cfg.fee_model.slippage_bps,
        })
        with open(out_dir / "summary.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)
        logger.info(
            "%s [OOS-PORTFOLIO]: return=%.2f%% sharpe=%.3f trades=%d",
            sym, summary["total_return_pct"],
            summary["sharpe_ratio"], summary["n_trades"],
        )

    pm = portfolio_metrics(results_by_asset, n_bootstrap=n_bootstrap)

    # Persist portfolio summary
    port_dir = output_root / "portfolio"
    port_dir.mkdir(parents=True, exist_ok=True)
    with open(port_dir / "portfolio_summary.json", "w") as f:
        import json as _json
        _json.dump(pm.model_dump(), f, indent=2, default=str)
    logger.info("portfolio summary written to %s", port_dir / "portfolio_summary.json")

    return results_by_asset, pm


# -----------------------------------------------------------------------------
# Extended main pipeline
# -----------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser()
    # Single-asset mode (backward compat)
    p.add_argument("--data",          default=None, type=Path,
                   help="Path to single-asset parquet (single-asset mode)")
    # Multi-asset mode
    p.add_argument("--data-dir",      default=None, type=Path,
                   help="Directory containing per-asset parquets (multi-asset mode)")
    p.add_argument("--assets",        default="",
                   help="Comma-separated asset symbols, e.g. BTCUSDT,ETHUSDT")
    p.add_argument("--output-dir",    default=Path("results"), type=Path)
    p.add_argument("--oos-start",     default="2025-10-01",
                   help="ISO date for OOS split, e.g. 2025-01-01")
    p.add_argument("--starting-cash", default=10_000.0, type=float)
    p.add_argument("--verbose",       action="store_true")
    p.add_argument("--run-sweep",     action="store_true",
                   help="Run 81-config hyperparameter sweep on IS data")
    p.add_argument("--n-jobs",        default=-1, type=int,
                   help="Parallel workers for sweep (-1 = all CPUs, 1 = serial)")
    p.add_argument("--run-wf",            action="store_true",
                   help="Run walk-forward CV on IS data")
    p.add_argument("--wf-n-folds",        default=3, type=int,
                   help="Number of WF folds (default 3)")
    p.add_argument("--wf-min-train-bars", default=2_000, type=int,
                   help="Minimum IS bars in the first (or each rolling) train window (default 2000)")
    p.add_argument("--wf-rolling",        action="store_true",
                   help="Use rolling fixed-size window (default: anchored/expanding)")
    p.add_argument("--allocation",        default="fixed",
                   choices=["fixed", "kelly", "risk_parity", "kelly_risk_parity"],
                   help="Position sizing / portfolio weighting method (default: fixed)")
    p.add_argument("--kelly-fractional",  default=0.5, type=float,
                   help="Kelly fraction multiplier (default 0.5 = half-Kelly)")
    args = p.parse_args()

    configure_logging(level="DEBUG" if args.verbose else "INFO")
    _run_start = time.time()

    # Validate argument combinations
    symbols = [s.strip() for s in args.assets.split(",") if s.strip()]
    multi_asset_mode = bool(symbols) and len(symbols) > 1

    if multi_asset_mode:
        if args.data_dir is None:
            p.error("--data-dir is required when --assets has multiple symbols")
        data_dict = load_multi_asset(symbols, args.data_dir)
        # Use BTCUSDT (or first symbol) as the representative single-asset for
        # sensitivity tests and sweep (IS partition is per-asset, but sweep
        # uses first symbol for IS exploration).
        df = data_dict[symbols[0]]
    elif args.data is not None:
        df = pd.read_parquet(args.data)
        if not symbols:
            symbols = ["BTCUSDT"]
        data_dict = {symbols[0]: df}
    else:
        p.error("Either --data or (--data-dir + --assets) must be specified")

    logger.info("loaded %d bars from primary asset [%s → %s]",
                len(df), df.index.min(), df.index.max())

    train, oos = split_oos(df, args.oos_start)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    summaries: list[dict] = []

    # Benchmarks
    bh_oos   = buy_and_hold(oos,   starting_cash=args.starting_cash)
    bh_train = buy_and_hold(train, starting_cash=args.starting_cash)
    summaries.extend([bh_oos, bh_train])

    # Default strategy config
    default_strat = FundingArbConfig(
        name="default",
        z_window=60, z_threshold=2.0,
        momentum_window=5, vol_window=24, vol_pct_lookback=720,
        vol_filter_pct=0.90,
        max_hold_bars=10, entry_min_bars_before_snapshot=1,
        stop_loss_pct=0.015,
        notional_per_trade_usd=5_000,
        warmup_bars=720,
    )
    default_bt = BacktestConfig(starting_cash=args.starting_cash)

    # In-sample (parameter validation only)
    s = run_one("train_default", train, default_strat, default_bt,
                args.output_dir, label="IN-SAMPLE")
    summaries.append(s)

    # Out-of-sample (headline result)
    s = run_one("test_default", oos, default_strat, default_bt,
                args.output_dir, label="OUT-OF-SAMPLE")
    summaries.append(s)

    # Capacity estimate for the OOS run
    oos_result_dir = args.output_dir / "test_default"
    capacity = estimate_capacity(s, oos, default_strat.notional_per_trade_usd)
    s["capacity"] = capacity
    with open(oos_result_dir / "summary.json", "w") as f:
        json.dump(s, f, indent=2, default=str)

    # Sensitivity: fees
    for fee_mult, label in [(0.5, "test_fee_0.5x"),
                            (1.5, "test_fee_1.5x"),
                            (2.0, "test_fee_2.0x")]:
        bt_cfg = BacktestConfig(
            starting_cash=args.starting_cash,
            fee_model=FeeModel(taker_bps=6.0 * fee_mult, use_taker=True),
        )
        summaries.append(run_one(label, oos, default_strat, bt_cfg,
                                 args.output_dir, label="OOS-SENSITIVITY"))

    # Sensitivity: z-threshold
    for z in [1.5, 2.5]:
        s_cfg = FundingArbConfig(**{**asdict(default_strat), "name": f"z{z}",
                                    "z_threshold": z})
        summaries.append(run_one(f"test_z_{z}", oos, s_cfg, default_bt,
                                 args.output_dir, label="OOS-SENSITIVITY"))

    # Sensitivity: stop-loss
    for sl in [0.010, 0.025]:
        s_cfg = FundingArbConfig(**{**asdict(default_strat), "name": f"sl{sl}",
                                    "stop_loss_pct": sl})
        summaries.append(run_one(f"test_sl_{sl}", oos, s_cfg, default_bt,
                                 args.output_dir, label="OOS-SENSITIVITY"))

    # Hyperparameter sweep (IS only)
    if args.run_sweep:
        logger.info("running hyperparameter sweep (IS partition)…")
        run_hyperparameter_sweep(
            df, default_strat, default_bt,
            args.output_dir, args.oos_start,
            n_jobs=args.n_jobs,
        )

    # Walk-forward CV (IS data only)
    if args.run_wf:
        from walk_forward import run_walk_forward_cv
        logger.info(
            "running walk-forward CV (n_folds=%d, min_train=%d, anchored=%s)…",
            args.wf_n_folds, args.wf_min_train_bars, not args.wf_rolling,
        )
        wf_result = run_walk_forward_cv(
            data=train,
            strat_cfg=default_strat,
            bt_cfg=default_bt,
            output_root=args.output_dir,
            n_folds=args.wf_n_folds,
            min_train_bars=args.wf_min_train_bars,
            anchored=not args.wf_rolling,
            sweep_n_jobs=args.n_jobs,
        )
        print("\n" + "=" * 60)
        print("WALK-FORWARD SUMMARY")
        print("=" * 60)
        print(f"  WF Net Sharpe:      {wf_result.wf_net_sharpe:.3f}")
        print(f"  WF Gross Sharpe:    {wf_result.wf_gross_sharpe:.3f}")
        print(f"  Overfitting Ratio:  {wf_result.overfitting_ratio:.3f}")
        print(f"  95% CI:             [{wf_result.bootstrap_ci_lo:.3f}, {wf_result.bootstrap_ci_hi:.3f}]")
        print(f"  Total Return:       {wf_result.wf_total_return_pct:.2f}%")
        print(f"  Max Drawdown:       {wf_result.wf_max_dd_pct:.2f}%")
        print(f"  Folds:              {wf_result.n_folds}")
        print("=" * 60)

    # Multi-asset portfolio backtest
    if multi_asset_mode:
        logger.info("running multi-asset portfolio backtest (%d assets)…", len(symbols))
        _, pm = run_portfolio_backtest(
            symbols=symbols,
            data_dict=data_dict,
            strat_cfg=default_strat,
            bt_cfg=default_bt,
            output_root=args.output_dir,
            oos_start=args.oos_start,
        )
        print("\n" + "=" * 60)
        print("PORTFOLIO SUMMARY")
        print("=" * 60)
        print(f"  Net Sharpe:    {pm.portfolio_net_sharpe:.3f}")
        print(f"  Gross Sharpe:  {pm.portfolio_gross_sharpe:.3f}")
        print(f"  95% CI:        [{pm.bootstrap_ci_lo:.3f}, {pm.bootstrap_ci_hi:.3f}]")
        print(f"  Total Return:  {pm.portfolio_total_return_pct:.2f}%")
        print(f"  Max Drawdown:  {pm.portfolio_max_dd_pct:.2f}%")
        print(f"  Total Trades:  {pm.total_trades}")
        print(f"  Total Fees:    ${pm.total_fees_usd:.0f}")
        print("\n  Per-asset:")
        for a in pm.assets:
            print(f"    {a.symbol:<12} net_sr={a.net_sharpe:.3f}  "
                  f"return={a.total_return_pct:.2f}%  trades={a.n_trades}")
        print("=" * 60)

    # Dynamic allocation (Kelly + risk-parity) — only when requested
    if multi_asset_mode and args.allocation != "fixed":
        from allocation import run_dynamic_portfolio_backtest
        logger.info(
            "running dynamic allocation backtest (method=%s, kelly_frac=%.2f)…",
            args.allocation, args.kelly_fractional,
        )
        _, pm_dyn, alloc = run_dynamic_portfolio_backtest(
            symbols=symbols,
            data_dict=data_dict,
            strat_cfg=default_strat,
            bt_cfg=default_bt,
            output_root=args.output_dir,
            oos_start=args.oos_start,
            method=args.allocation,
            kelly_fractional=args.kelly_fractional,
        )
        print("\n" + "=" * 60)
        print("DYNAMIC ALLOCATION SUMMARY")
        print("=" * 60)
        print(f"  Method:            {alloc.method}")
        for sym in symbols:
            print(
                f"  {sym:<12} Kelly={alloc.kelly_fractions[sym]:.3f}  "
                f"RW={alloc.rp_weights[sym]:.3f}  "
                f"Notional=${alloc.adjusted_notionals[sym]:,.0f}"
            )
        print(f"  Dynamic Net SR:    {pm_dyn.portfolio_net_sharpe:.3f}")
        print(f"  Dynamic Gross SR:  {pm_dyn.portfolio_gross_sharpe:.3f}")
        print(f"  95% CI:            [{pm_dyn.bootstrap_ci_lo:.3f}, {pm_dyn.bootstrap_ci_hi:.3f}]")
        print(f"  Total Return:      {pm_dyn.portfolio_total_return_pct:.2f}%")
        print(f"  Max Drawdown:      {pm_dyn.portfolio_max_dd_pct:.2f}%")
        print("=" * 60)

    # Summary table
    cmp_rows = []
    for s in summaries:
        cmp_rows.append({
            "name":            s["name"],
            "label":           s.get("label", ""),
            "total_return_pct": s.get("total_return_pct", 0.0),
            "sharpe":          s.get("sharpe_ratio", 0.0),
            "max_dd_pct":      s.get("max_drawdown_pct", 0.0),
            "n_trades":        s.get("n_trades", 0),
            "fees_usd":        s.get("total_fees_usd", 0.0),
            "slippage_usd":    s.get("total_slippage_usd", 0.0),
            "funding_usd":     s.get("total_funding_usd", 0.0),
        })
    cmp_df = pd.DataFrame(cmp_rows)
    cmp_df.to_csv(args.output_dir / "comparison.csv", index=False)

    print("\n" + "=" * 90)
    print("RESULTS COMPARISON")
    print("=" * 90)
    print(cmp_df.to_string(index=False, float_format="%.3f"))
    print("=" * 90)
    print(f"\nArtifacts: {args.output_dir}/")
    print(f"OOS split date: {args.oos_start}")

    # Append run to the results registry
    oos_row = next((s for s in summaries if s.get("label") == "OUT-OF-SAMPLE"), {})
    _run_id = append_run(
        runtime_s=time.time() - _run_start,
        output_dir=args.output_dir,
        cfg_dict=asdict(default_strat),
        data_df=df,
        oos_sharpe=float(oos_row.get("sharpe_ratio", float("nan"))),
        n_trades=int(oos_row.get("n_trades", 0)),
        assets=symbols,
        oos_start=args.oos_start,
    )
    logger.info("run recorded", run_id=_run_id, registry=str("results/registry.parquet"))


if __name__ == "__main__":
    main()

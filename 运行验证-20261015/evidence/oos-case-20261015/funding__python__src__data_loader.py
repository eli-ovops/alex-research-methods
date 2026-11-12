import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def load_klines_csv(path: Path) -> pd.DataFrame:
    """Read the C++-produced klines CSV into a tz-aware DataFrame."""
    df = pd.read_csv(path)
 
    required = {"open_time_ms", "open", "high", "low", "close", "volume", "turnover"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"klines CSV missing columns: {missing}")
 
    df["timestamp"] = pd.to_datetime(df["open_time_ms"], unit="ms", utc=True)
    df = df.drop(columns=["open_time_ms"]).set_index("timestamp").sort_index()
    return df
 
 
def load_funding_csv(path: Path) -> pd.DataFrame:
    """Read the C++-produced funding CSV into a tz-aware DataFrame."""
    df = pd.read_csv(path)
 
    required = {"timestamp_ms", "funding_rate"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"funding CSV missing columns: {missing}")
 
    df["timestamp"] = pd.to_datetime(df["timestamp_ms"], unit="ms", utc=True)
    df = df.drop(columns=["timestamp_ms"]).set_index("timestamp").sort_index()
    return df
 
 
# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------
def validate_klines(df: pd.DataFrame) -> None:
    """Hard-fail on data quality issues. Better to crash now than later."""
    if df.empty:
        raise ValueError("klines DataFrame is empty")
 
    if df.index.duplicated().any():
        n_dup = df.index.duplicated().sum()
        raise ValueError(f"klines have {n_dup} duplicate timestamps")
 
    if df.isna().any().any():
        raise ValueError(f"klines contain NaN: {df.isna().sum().to_dict()}")
 
    # Hourly bars should be exactly 1 hour apart. Find any gaps.
    expected_freq = pd.Timedelta(hours=1)
    gaps = df.index.to_series().diff().dropna()
    bad_gaps = gaps[gaps != expected_freq]
    if len(bad_gaps) > 0:
        # Bybit occasionally has missing bars during exchange downtime — log
        # but don't fail. Forward-filling 1-2 missing bars is acceptable.
        # If > 1% of bars are gapped, fail loud.
        gap_pct = 100 * len(bad_gaps) / len(df)
        if gap_pct > 1.0:
            raise ValueError(
                f"too many gaps in klines: {len(bad_gaps)} ({gap_pct:.2f}%)"
            )
        logger.warning(
            "klines have %d gaps (%.3f%%) — will forward-fill",
            len(bad_gaps), gap_pct,
        )
 
    # Sanity: no negative prices, high >= low, close within [low, high]
    if (df[["open", "high", "low", "close"]] <= 0).any().any():
        raise ValueError("klines contain non-positive prices")
 
    bad_hl = (df["high"] < df["low"]).sum()
    if bad_hl > 0:
        raise ValueError(f"{bad_hl} bars have high < low")
 
    bad_close = ((df["close"] < df["low"]) | (df["close"] > df["high"])).sum()
    if bad_close > 0:
        raise ValueError(f"{bad_close} bars have close outside [low, high]")
 
 
def validate_funding(df: pd.DataFrame) -> None:
    if df.empty:
        raise ValueError("funding DataFrame is empty")
 
    if df.index.duplicated().any():
        raise ValueError("funding has duplicate timestamps")
 
    if df["funding_rate"].isna().any():
        raise ValueError("funding contains NaN rates")
 
    # Bybit funding rates are typically in [-0.0075, +0.0075] per 8h.
    # Anything outside [-0.05, +0.05] is suspicious — fail.
    if df["funding_rate"].abs().max() > 0.05:
        bad = df[df["funding_rate"].abs() > 0.05]
        raise ValueError(f"funding rate sanity check failed:\n{bad}")
 
 
# -----------------------------------------------------------------------------
# Alignment
# -----------------------------------------------------------------------------
def align_funding_to_bars(
    klines: pd.DataFrame,
    funding: pd.DataFrame,
) -> pd.DataFrame:
    """
    Forward-fill funding onto each hourly bar.
 
    Logic: for each hourly bar at time T, look up the most recent
    funding observation at time <= T. This is what the strategy
    would "know" at the open of bar T.
 
    We use pd.merge_asof which is the canonical pandas tool for
    point-in-time joins. Direction='backward' = forward-fill.
    """
    klines_reset = klines.reset_index()
    funding_reset = funding.reset_index()
 
    merged = pd.merge_asof(
        klines_reset.sort_values("timestamp"),
        funding_reset.sort_values("timestamp"),
        on="timestamp",
        direction="backward",  # use the most recent prior funding obs
    )
    merged = merged.set_index("timestamp")
 
    # Bars before the first funding observation will have NaN.
    # Drop those — strategy can't operate without a funding rate.
    n_dropped = merged["funding_rate"].isna().sum()
    if n_dropped > 0:
        logger.info(
            "dropping %d leading bars with no prior funding rate", n_dropped
        )
        merged = merged.dropna(subset=["funding_rate"])
 
    return merged
 
 
def add_bars_since_funding(
    df: pd.DataFrame,
    funding_timestamps: pd.DatetimeIndex | None = None,
) -> pd.DataFrame:
    """
    Add a column counting hours elapsed since the last 8h funding snapshot.

    0 = this bar IS the funding snapshot bar (payment applied here)
    1 = 1 hour after the snapshot
    ...up to 7, then resets to 0 at the next snapshot.

    Uses actual funding snapshot timestamps when available (accurate even when
    the funding RATE is unchanged across consecutive periods). Falls back to
    rate-change detection only when timestamps are not provided.
    """
    df = df.copy()

    if funding_timestamps is not None and len(funding_timestamps) > 0:
        # Primary path: mark bars whose timestamp appears in the funding schedule.
        # This is correct regardless of whether the rate value changed.
        is_snapshot = df.index.isin(funding_timestamps)
    else:
        # Fallback: detect by rate change (inaccurate when rate is stable across periods).
        is_snapshot = df["funding_rate"] != df["funding_rate"].shift(1)
        is_snapshot.iloc[0] = True

    group_id = is_snapshot.cumsum()
    df["bars_since_funding"] = df.groupby(group_id).cumcount()
    return df
 
 
# -----------------------------------------------------------------------------
# Pipeline entry point
# -----------------------------------------------------------------------------
def build_clean_dataset(
    klines_csv: Path,
    funding_csv: Path,
    output_parquet: Path,
) -> pd.DataFrame:
    logger.info("loading %s", klines_csv)
    klines = load_klines_csv(klines_csv)
    validate_klines(klines)
    logger.info("klines: %d rows, %s → %s", len(klines), klines.index.min(), klines.index.max())
 
    logger.info("loading %s", funding_csv)
    funding = load_funding_csv(funding_csv)
    validate_funding(funding)
    logger.info(
        "funding: %d obs, rate range [%.4f%%, %.4f%%]",
        len(funding),
        funding["funding_rate"].min() * 100,
        funding["funding_rate"].max() * 100,
    )
 
    # Reindex klines to a strict hourly grid before merging.
    full_index = pd.date_range(
        start=klines.index.min(),
        end=klines.index.max(),
        freq="1h",
        tz="UTC",
        name="timestamp",
    )
    klines = klines.reindex(full_index)
 
    # Forward-fill OHLCV across any gaps. Volume of gap bars set to 0.
    klines[["open", "high", "low", "close"]] = klines[
        ["open", "high", "low", "close"]
    ].ffill()
    klines[["volume", "turnover"]] = klines[["volume", "turnover"]].fillna(0.0)
 
    merged = align_funding_to_bars(klines, funding)
    merged = add_bars_since_funding(merged, funding_timestamps=funding.index)
 
    output_parquet.parent.mkdir(parents=True, exist_ok=True)
    merged.to_parquet(output_parquet, compression="zstd")
    logger.info("wrote %s (%d rows, %.1f KB)",
                output_parquet, len(merged),
                output_parquet.stat().st_size / 1024)
 
    return merged
 
 
# -----------------------------------------------------------------------------
# Multi-asset loader
# -----------------------------------------------------------------------------
_EXPECTED_COLUMNS: frozenset[str] = frozenset({
    "open", "high", "low", "close", "volume", "turnover",
    "funding_rate", "bars_since_funding",
})


def load_multi_asset(
    symbols: list[str],
    data_dir: Path,
    suffix: str = "1h_2yr",
) -> dict[str, pd.DataFrame]:
    """
    Load per-asset parquets from data_dir.

    Naming convention: ``{symbol.lower()}_{suffix}.parquet``.

    Returns dict mapping symbol → DataFrame.  Raises ``FileNotFoundError``
    if any parquet is missing, ``ValueError`` if the 8-column schema differs
    from the expected set across any asset.
    """
    result: dict[str, pd.DataFrame] = {}
    for sym in symbols:
        path = data_dir / f"{sym.lower()}_{suffix}.parquet"
        if not path.exists():
            raise FileNotFoundError(
                f"No data found for {sym}: expected {path}. "
                "Run scripts/fetch_multi_asset.sh to fetch and clean data."
            )
        df = pd.read_parquet(path)
        actual = frozenset(df.columns)
        if actual != _EXPECTED_COLUMNS:
            extra = actual - _EXPECTED_COLUMNS
            missing = _EXPECTED_COLUMNS - actual
            raise ValueError(
                f"{sym}: schema mismatch. Extra cols: {extra or '∅'}, "
                f"missing cols: {missing or '∅'}"
            )
        result[sym] = df
        logger.info(
            "loaded %s: %d bars [%s → %s]",
            sym, len(df), df.index.min(), df.index.max(),
        )
    return result


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------
def main() -> int:
    p = argparse.ArgumentParser(description="Clean and align Bybit data")
    p.add_argument("--klines",  required=True, type=Path, help="C++ klines CSV")
    p.add_argument("--funding", required=True, type=Path, help="C++ funding CSV")
    p.add_argument("--output",  required=True, type=Path, help="Output Parquet")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()
 
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
 
    df = build_clean_dataset(args.klines, args.funding, args.output)
 
    print(f"\nFinal dataset: {len(df):,} rows × {len(df.columns)} cols")
    print(f"Period: {df.index.min()} → {df.index.max()}")
    print(f"\nFirst 3 rows:\n{df.head(3)}")
    print(f"\nFunding stats:\n{df['funding_rate'].describe()}")
    return 0
 
 
if __name__ == "__main__":
    sys.exit(main())
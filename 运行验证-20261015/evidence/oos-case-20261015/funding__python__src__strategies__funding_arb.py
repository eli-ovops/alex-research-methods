from __future__ import annotations
 
import logging
from dataclasses import dataclass
 
import numpy as np
import pandas as pd
 
# Import the base classes from the parent src/
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from strategy import Strategy, StrategyConfig  # noqa: E402
 
logger = logging.getLogger(__name__)
 
 
# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
@dataclass
class FundingArbConfig(StrategyConfig):
    # Signal thresholds
    z_window:        int   = 60     # rolling window for funding z-score (3/day × 20 = 60)
    z_threshold:     float = 2.0    # |z| above this triggers entry consideration
 
    # Momentum confirmation (avoid trading INTO the trend)
    momentum_window: int   = 5      # 5h return for momentum filter
 
    # Volatility regime filter
    vol_window:        int   = 24    # 24h realized vol
    vol_pct_lookback:  int   = 720   # 30-day rolling percentile reference
    vol_filter_pct:    float = 0.90  # skip entries above this percentile
 
    # Holding logic
    max_hold_bars:                  int   = 10
    entry_min_bars_before_snapshot: int   = 1
    stop_loss_pct:                  float = 0.015   # 1.5% adverse move = cut
 
    # Sizing
    notional_per_trade_usd: float = 5_000.0
 
    # Warmup: longest of all windows
    warmup_bars: int = 720
 
 
# -----------------------------------------------------------------------------
# Strategy
# -----------------------------------------------------------------------------
class FundingArbStrategy(Strategy):
    """
    Funding-rate mean-reversion with momentum and vol filters.
 
    State:
        entry_price: float — price at which current position was opened
        entry_bar:   int   — bar index when current position was opened
        entry_side:  +1 long / -1 short / 0 flat
    """
 
    def __init__(self, config: FundingArbConfig):
        super().__init__(config)
        self.cfg: FundingArbConfig = config
        self.reset()
 
    def reset(self) -> None:
        self._entry_price: float = 0.0
        self._entry_bar:   int   = -1
        self._entry_side:  int   = 0  # -1, 0, +1
        self._bar_idx:     int   = -1
        self._vol_cache:   list[float] = []  # incremental realized-vol history
        self._seeded:      bool  = False

    def get_state(self) -> dict:
        return {"vol_cache": list(self._vol_cache)}

    def set_state(self, state: dict) -> None:
        self._vol_cache = list(state.get("vol_cache", []))
        self._seeded = True
 
    # ------------------------------------------------------------------
    # Vol cache — updated every bar (before warmup gate) so the cache
    # has enough history when _compute_features is first called.
    # ------------------------------------------------------------------
    def _update_vol_cache(self, history: pd.DataFrame) -> None:
        close = history["close"]
        cfg = self.cfg
        if len(close) >= cfg.vol_window + 1:
            log_ret = np.log(
                close.iloc[-cfg.vol_window:] / close.iloc[-cfg.vol_window - 1: -1].values
            )
            rv = float(log_ret.std(ddof=1) * np.sqrt(24 * 365))
        else:
            rv = float("nan")
        self._vol_cache.append(rv)

    # ------------------------------------------------------------------
    # Feature computation (computed once per bar from history)
    # ------------------------------------------------------------------
    def _compute_features(self, history: pd.DataFrame) -> dict:
        """Compute the four signal features from history. Returns NaN-safe dict."""
        cfg = self.cfg
 
        # We always look at history.iloc[-1] = current bar.
        funding = history["funding_rate"]
        close   = history["close"]
 
        # Funding z-score over rolling z_window
        if len(funding) < cfg.z_window:
            funding_z = np.nan
        else:
            window = funding.iloc[-cfg.z_window:]
            mean = window.mean()
            std  = window.std(ddof=1)
            funding_z = (funding.iloc[-1] - mean) / std if std > 1e-12 else 0.0
 
        # Momentum: 5h log return
        if len(close) < cfg.momentum_window + 1:
            momentum = np.nan
        else:
            momentum = np.log(close.iloc[-1] / close.iloc[-cfg.momentum_window - 1])
 
        # Realized vol over vol_window bars (annualized to be intuitive)
        if len(close) < cfg.vol_window + 1:
            realized_vol = np.nan
        else:
            log_ret = np.log(close.iloc[-cfg.vol_window:] / close.iloc[-cfg.vol_window - 1: -1].values)
            realized_vol = log_ret.std(ddof=1) * np.sqrt(24 * 365)
 
        # Vol percentile — O(vol_window + vol_pct_lookback) via incremental cache
        # _vol_cache is populated every bar by _update_vol_cache() before warmup
        # check, so it has enough history by the time _compute_features is called.
        _cache_ready = len(self._vol_cache) >= cfg.vol_pct_lookback + cfg.vol_window
        if not _cache_ready or np.isnan(realized_vol):
            vol_pct = np.nan
        else:
            recent = np.array(self._vol_cache[-cfg.vol_pct_lookback:], dtype=float)
            valid = recent[~np.isnan(recent)]
            vol_pct = float((realized_vol >= valid).mean()) if len(valid) > 0 else np.nan
 
        return {
            "funding_z":    funding_z,
            "momentum":     momentum,
            "realized_vol": realized_vol,
            "vol_pct":      vol_pct,
            "current_close":  close.iloc[-1],
            "bars_since_funding": int(history["bars_since_funding"].iloc[-1]),
        }
 
    # ------------------------------------------------------------------
    # Decision
    # ------------------------------------------------------------------
    def on_bar(self, history: pd.DataFrame, current_position: float) -> float:
        self._bar_idx += 1

        # Update vol cache every bar (even during warmup) so that enough
        # realized-vol history accumulates before the first trade signal.
        self._update_vol_cache(history)

        # During warmup, do nothing (skip if state was seeded from IS).
        if not self._seeded and len(history) < self.cfg.warmup_bars:
            return 0.0
 
        feats = self._compute_features(history)
        # If any feature is NaN, sit out.
        if any(
            (isinstance(v, float) and np.isnan(v))
            for v in feats.values()
        ):
            return current_position
 
        # ----- exit logic (we have an open position) -----
        if self._entry_side != 0:
            should_exit = self._check_exit(feats)
            if should_exit:
                self._entry_side  = 0
                self._entry_price = 0.0
                self._entry_bar   = -1
                return 0.0
            return current_position  # keep position
 
        # ----- entry logic (we are flat) -----
        return self._check_entry(feats)
 
    def _check_exit(self, feats: dict) -> bool:
        """Return True if we should exit the current position."""
        cfg = self.cfg
 
        bars_held = self._bar_idx - self._entry_bar
 
        # 1. Time stop (safety net)
        if bars_held >= cfg.max_hold_bars:
            logger.debug("exit: max_hold_bars reached (%d)", bars_held)
            return True
 
        # 2. Funding-snapshot exit: we entered before the snapshot, want
        #    to exit right after. bars_since_funding == 0 means the snapshot
        #    just happened on this bar.
        # We need bars_held >= 1 to avoid exiting on the same bar we entered
        # if we happened to enter on a snapshot bar.
        if bars_held >= 1 and feats["bars_since_funding"] == 0:
            logger.debug("exit: collected funding at snapshot")
            return True
 
        # 3. Stop-loss: adverse move > stop_loss_pct
        price_change_pct = (feats["current_close"] - self._entry_price) / self._entry_price
        adverse_pct = -self._entry_side * price_change_pct  # positive = adverse
        if adverse_pct > cfg.stop_loss_pct:
            logger.debug(
                "exit: stop-loss hit, adverse=%.3f%%", adverse_pct * 100
            )
            return True
 
        return False
 
    def _check_entry(self, feats: dict) -> float:
        """Return target position size (signed BTC). 0 = no entry."""
        cfg = self.cfg
 
        # Vol filter: skip if vol regime is in the top decile
        if feats["vol_pct"] >= cfg.vol_filter_pct:
            return 0.0
 
        # Don't enter too close to (or on) a funding snapshot — we want
        # at least one bar of holding period to elapse before snapshot.
        # Since we hold UNTIL the snapshot, we must enter when there's
        # still time before it. bars_since_funding == 0 means snapshot
        # just happened; we want to enter shortly after.
        # If bars_since_funding is very high (close to 8), the snapshot
        # is imminent → entry might fill, then snapshot, then we'd exit
        # in the same bar essentially. Skip the last bar before snapshot.
        # Funding cycle is 8h, so bars_since_funding goes 0..7.
        if feats["bars_since_funding"] >= 7:
            return 0.0
        if feats["bars_since_funding"] < cfg.entry_min_bars_before_snapshot:
            return 0.0
 
        z   = feats["funding_z"]
        mom = feats["momentum"]
 
        target_btc = 0.0
        side: int = 0
 
        # SHORT: funding extremely positive (longs crowded), no upward momentum
        if z > cfg.z_threshold and mom <= 0:
            side = -1
            qty_btc = cfg.notional_per_trade_usd / feats["current_close"]
            target_btc = -qty_btc
 
        # LONG: funding extremely negative (shorts crowded), no downward momentum
        elif z < -cfg.z_threshold and mom >= 0:
            side = +1
            qty_btc = cfg.notional_per_trade_usd / feats["current_close"]
            target_btc = +qty_btc
 
        if side != 0:
            self._entry_side  = side
            self._entry_price = feats["current_close"]
            self._entry_bar   = self._bar_idx
            logger.debug(
                "entry: side=%d z=%.2f mom=%.4f vol_pct=%.2f price=%.2f",
                side, z, mom, feats["vol_pct"], feats["current_close"],
            )
 
        return target_btc
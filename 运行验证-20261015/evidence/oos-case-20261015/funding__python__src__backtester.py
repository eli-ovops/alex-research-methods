from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
import structlog

from strategy import Strategy

logger = structlog.get_logger(__name__)


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
@dataclass
class FeeModel:
    """
    Transaction cost model for Bybit USDT perpetuals.

    Assumptions (state explicitly for PM review):
      taker_bps=6.0    — Bybit VIP0 taker rate (0.06%). Reduce to 4.0 for VIP1+.
      slippage_bps=1.0 — Conservative half-spread for BTC/USDT perp.
                         Bybit bid-ask is typically 0.1-0.5 bps at mid for small
                         orders; 1 bps adds a buffer for queue position and
                         execution uncertainty. Scale up for notional > $500k.
    Total round-trip cost: 2 × (taker + slippage) = 14 bps at defaults.
    """
    taker_bps:    float = 6.0
    maker_bps:    float = -1.0   # rebate (unused — always use taker for conservatism)
    slippage_bps: float = 1.0
    use_taker:    bool  = True

    def fee_for_trade(self, notional_usd: float) -> float:
        """Exchange fee only (positive number)."""
        bps = self.taker_bps if self.use_taker else self.maker_bps
        return abs(notional_usd) * bps / 10_000

    def slippage_for_trade(self, notional_usd: float) -> float:
        """Half-spread cost (positive number, tracked separately for attribution)."""
        return abs(notional_usd) * self.slippage_bps / 10_000

    def total_cost_bps(self) -> float:
        """Total one-way cost in bps (fee + slippage)."""
        bps = self.taker_bps if self.use_taker else self.maker_bps
        return bps + self.slippage_bps


@dataclass
class BacktestConfig:
    starting_cash:      float    = 10_000.0
    fee_model:          FeeModel = field(default_factory=FeeModel)
    max_leverage:       float    = 3.0
    next_bar_execution: bool     = True   # fill at next bar OPEN (conservative)
    funding_enabled:    bool     = True


# -----------------------------------------------------------------------------
# Result container
# -----------------------------------------------------------------------------
@dataclass
class BacktestResult:
    """Everything the report generator needs."""
    equity:            pd.Series
    returns:           pd.Series
    position:          pd.Series
    trades:            pd.DataFrame
    pnl_decomposition: pd.DataFrame   # gross_pnl, fees, slippage, funding_pnl per bar
    config:            dict[str, Any]
    strategy_config:   dict[str, Any]

    def summary(self) -> dict[str, float]:
        eq  = self.equity
        ret = self.returns.dropna()
        annualization = np.sqrt(24 * 365)

        total_return = eq.iloc[-1] / eq.iloc[0] - 1
        sharpe = (ret.mean() / ret.std() * annualization) if ret.std() > 0 else 0.0
        max_dd = ((eq - eq.cummax()) / eq.cummax()).min()

        return {
            "total_return_pct":   total_return * 100,
            "sharpe_ratio":       sharpe,
            "max_drawdown_pct":   max_dd * 100,
            "n_trades":           len(self.trades),
            "total_fees_usd":     self.pnl_decomposition["fees"].sum(),
            "total_slippage_usd": self.pnl_decomposition["slippage"].sum(),
            "total_funding_usd":  self.pnl_decomposition["funding_pnl"].sum(),
        }


# -----------------------------------------------------------------------------
# Engine
# -----------------------------------------------------------------------------
class Backtester:
    """Event-loop backtest. Drives a Strategy across a DataFrame of bars."""

    def __init__(self, config: BacktestConfig):
        self.config = config

    def run(
        self,
        data: pd.DataFrame,
        strategy: Strategy,
        context_data: pd.DataFrame | None = None,
        initial_state: dict | None = None,
    ) -> BacktestResult:
        """
        Run the strategy across `data`.

        `data` schema (from data_loader):
            index: tz-aware UTC, hourly
            columns: open, high, low, close, volume, turnover,
                     funding_rate, bars_since_funding

        Optional seeding args (used by walk-forward to eliminate OOS warmup):
            context_data  — IS tail prepended for feature history; not traded
            initial_state — dict from strategy.get_state(); restores _vol_cache
        """
        self._validate_input(data)
        strategy.reset()
        if initial_state is not None:
            strategy.set_state(initial_state)

        if context_data is not None:
            full_data   = pd.concat([context_data, data])
            context_len = len(context_data)
            effective_warmup = 0
        else:
            full_data        = data
            context_len      = 0
            effective_warmup = strategy.config.warmup_bars

        n        = len(data)
        cash     = self.config.starting_cash
        position = 0.0

        equity_arr    = np.zeros(n)
        position_arr  = np.zeros(n)
        gross_pnl_arr = np.zeros(n)
        fees_arr      = np.zeros(n)
        slippage_arr  = np.zeros(n)
        funding_arr   = np.zeros(n)

        trade_records: list[dict] = []

        opens           = data["open"].to_numpy()
        closes          = data["close"].to_numpy()
        funding_rates   = data["funding_rate"].to_numpy()
        bars_since_fund = data["bars_since_funding"].to_numpy()
        timestamps      = data.index
        prev_close      = closes[0]

        for i in range(n):
            close = closes[i]

            # 1. Funding payment at snapshot bars.
            funding_pay = 0.0
            if self.config.funding_enabled and bars_since_fund[i] == 0 and i > 0:
                funding_pay = -position * close * funding_rates[i]
                cash += funding_pay

            # 2. Mark-to-market gross P&L (attribution only; not added to cash —
            #    equity = cash + position × close already captures it).
            gross_pnl = position * (close - prev_close)

            # 3. Strategy signal.
            target_position = position
            if i >= effective_warmup and i < n - 1:
                history = full_data.iloc[: context_len + i + 1]
                target_position = strategy.on_bar(history, position)
                current_equity  = cash + position * close
                target_position = self._enforce_leverage_cap(
                    target_position, close, current_equity,
                )

            # 4. Execute at NEXT bar's open with half-spread slippage.
            #    Buys fill above open, sells fill below — models adverse selection.
            trade_fee  = 0.0
            trade_slip = 0.0
            if (
                self.config.next_bar_execution
                and i < n - 1
                and not np.isclose(target_position, position, atol=1e-9)
            ):
                qty_delta  = target_position - position
                raw_price  = opens[i + 1]
                slip_sign  = 1 if qty_delta > 0 else -1
                slip_frac  = self.config.fee_model.slippage_bps / 10_000
                exec_price = raw_price * (1 + slip_sign * slip_frac)
                notional   = qty_delta * exec_price
                trade_fee  = self.config.fee_model.fee_for_trade(notional)
                trade_slip = self.config.fee_model.slippage_for_trade(notional)

                cash     -= qty_delta * exec_price
                cash     -= trade_fee
                position  = target_position

                trade_records.append({
                    "timestamp":    timestamps[i + 1],
                    "side":         "buy" if qty_delta > 0 else "sell",
                    "qty":          abs(qty_delta),
                    "price":        exec_price,
                    "notional_usd": abs(notional),
                    "fee_usd":      trade_fee,
                    "slippage_usd": trade_slip,
                })

            # 5. Equity = cash + MTM position.
            equity = cash + position * close

            equity_arr[i]    = equity
            position_arr[i]  = position
            gross_pnl_arr[i] = gross_pnl
            fees_arr[i]      = trade_fee
            slippage_arr[i]  = trade_slip
            funding_arr[i]   = funding_pay

            prev_close = close

        # Force-close any open position at end-of-data.
        if abs(position) > 1e-9:
            final_close = closes[-1]
            qty_delta   = -position
            notional    = qty_delta * final_close
            close_fee   = self.config.fee_model.fee_for_trade(notional)
            close_slip  = self.config.fee_model.slippage_for_trade(notional)
            cash       -= qty_delta * final_close
            cash       -= close_fee
            position    = 0.0
            fees_arr[-1]     += close_fee
            slippage_arr[-1] += close_slip
            equity_arr[-1]    = cash
            trade_records.append({
                "timestamp":    timestamps[-1],
                "side":         "sell" if qty_delta < 0 else "buy",
                "qty":          abs(qty_delta),
                "price":        final_close,
                "notional_usd": abs(notional),
                "fee_usd":      close_fee,
                "slippage_usd": close_slip,
            })
            logger.info("force-closed position at final bar: qty=%.6f", -qty_delta)

        equity    = pd.Series(equity_arr, index=timestamps, name="equity")
        returns   = equity.pct_change().fillna(0.0)
        position_s = pd.Series(position_arr, index=timestamps, name="position")
        trades    = pd.DataFrame(trade_records)
        pnl_decomp = pd.DataFrame({
            "gross_pnl":   gross_pnl_arr,
            "fees":        fees_arr,
            "slippage":    slippage_arr,
            "funding_pnl": funding_arr,
        }, index=timestamps)

        return BacktestResult(
            equity=equity,
            returns=returns,
            position=position_s,
            trades=trades,
            pnl_decomposition=pnl_decomp,
            config=self.config.__dict__ | {"fee_model": self.config.fee_model.__dict__},
            strategy_config=strategy.config.to_dict(),
        )

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------
    def _validate_input(self, data: pd.DataFrame) -> None:
        required = {"open", "high", "low", "close", "funding_rate", "bars_since_funding"}
        missing  = required - set(data.columns)
        if missing:
            raise ValueError(f"data missing required columns: {missing}")
        if data.isna().any().any():
            raise ValueError("data contains NaN — clean it first via data_loader")

    def _enforce_leverage_cap(
        self,
        target_position: float,
        price: float,
        equity: float,
    ) -> float:
        """Clip target so |notional| <= equity × max_leverage."""
        max_notional    = abs(equity) * self.config.max_leverage
        target_notional = target_position * price
        if abs(target_notional) > max_notional:
            sign = np.sign(target_notional) or 1.0
            return sign * max_notional / price
        return target_position

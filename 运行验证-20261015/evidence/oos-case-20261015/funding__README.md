# Funding Harvester

A production-grade backtesting research platform for a **funding-rate mean-reversion strategy** on BTCUSDT perpetual futures (Bybit). Built for rigorous quantitative research with full reproducibility, walk-forward validation, and statistical overfitting controls.

---

## What's Inside

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Data** | C++ fetcher | Pulls OHLCV + funding history from Bybit v5 REST API |
| **Data** | `data_loader.py` | Validates, aligns, and produces clean Parquet |
| **Strategy** | `funding_arb.py` | Funding z-score mean-reversion signal with filters |
| **Engine** | `backtester.py` | Event-loop simulation with realistic costs |
| **Stats** | `quant_stats.py` | Sharpe, Sortino, PSR, DSR, bootstrap CI |
| **Analysis** | `diagnostics.py` | Regime breakdown, cost attribution, momentum ablation |
| **Sizing** | `allocation.py` | Fixed / Kelly / Risk-Parity / combined sizing |
| **Validation** | `walk_forward.py` | Anchored/rolling walk-forward cross-validation |
| **Portfolio** | `portfolio.py` | Multi-asset aggregation and correlation |
| **Orchestration** | `runner.py` | Full pipeline: split → sweep → WF → sensitivity → reports |
| **Reporting** | `reporting.py` | Charts, HTML tearsheet, methodology doc |
| **Registry** | `registry.py` | Append-only run ledger (git SHA + config hash + data hash) |
| **Experiments** | `experiments/schema.py` | YAML-based declarative experiment spec (Pydantic) |

---

## Strategy Logic

The strategy exploits funding-rate mean reversion on perpetual futures:

- Funding z-score > +2.0 (longs crowded, perp at premium) **and** no upward momentum → **short** to receive funding
- Funding z-score < -2.0 (shorts crowded) **and** no downward momentum → **long** to receive funding

### Entry filters (all must pass)

| Filter | Logic |
|--------|-------|
| Z-score trigger | `abs(funding_z_score) > 2.0` over 60-bar rolling window |
| Momentum filter | 5h log-return must not oppose the trade direction |
| Volatility regime | Realized vol (24-bar) ≤ 90th percentile of 30-day distribution |
| Timing | `bars_since_funding ∈ [1, 6]` — avoids entering right at or 1 bar before a snapshot |

### Exit conditions (first hit wins)

| Trigger | Logic |
|---------|-------|
| Funding snapshot | `bars_since_funding == 0` after ≥ 1 bar held — funding collected |
| Time stop | 10 bars (10 hours) maximum hold |
| Stop-loss | Adverse price move > 1.5% |

---

## Full Pipeline

```
Bybit REST API
      │
      ▼ (C++ fetcher — paginated, rate-limited)
BTCUSDT_klines.csv + BTCUSDT_funding.csv
      │
      ▼ (data_loader.py — validate, forward-fill, merge, bars_since_funding)
btcusdt_1h.parquet  [open/high/low/close/volume/turnover/funding_rate/bars_since_funding]
      │
      ▼ (runner.py — IS/OOS split at --oos-start)
 ┌──────────────────────────────────┐
 │  In-Sample (train)  │  OOS (test)│
 └──────────────────────────────────┘
      │
      ├── Baseline IS + OOS runs
      ├── Buy-and-hold benchmark
      ├── 81-config hyperparameter sweep (3⁴ grid)
      ├── Sensitivity: fee × {0.5, 1.5, 2.0}, z ∈ {1.5, 2.5}, sl ∈ {1%, 2.5%}
      ├── 3-fold walk-forward CV (anchored or rolling)
      │
      └── results/{run_name}/
          ├── equity.parquet
          ├── pnl.parquet
          ├── position.parquet
          ├── trades.parquet
          ├── summary.json
          ├── comparison.csv
          ├── sweep/
          │   ├── sweep_results.csv
          │   └── heatmap_*.png  (12 parameter-pair heatmaps)
          ├── walk_forward/
          │   ├── walk_forward_summary.json
          │   ├── wf_equity_curve.png
          │   ├── wf_fold_performance.png
          │   ├── wf_param_stability.png
          │   └── wf_fold_{n}/
          └── report/
              ├── equity_curve.png
              ├── drawdown.png
              ├── pnl_decomposition.png
              ├── monthly_returns.png
              ├── trade_pnl_distribution.png
              ├── bootstrap_distribution.png
              ├── regime_performance.png
              ├── REPORT.md
              ├── METHODOLOGY.md
              └── {name}_tearsheet.html
```

---

## Project Structure

```
funding_harvester/
├── cpp/
│   ├── src/
│   │   ├── main.cpp              # CLI entry point
│   │   ├── bybit_client.cpp      # Bybit v5 REST API (pagination, rate-limiting)
│   │   └── csv_writer.cpp        # CSV serialisation
│   ├── include/
│   ├── third_party/nlohmann/     # JSON header (auto-downloaded)
│   ├── CMakeLists.txt
│   └── bootstrap.sh
├── python/
│   ├── src/
│   │   ├── backtester.py         # Event-loop simulation engine
│   │   ├── data_loader.py        # CSV → clean Parquet
│   │   ├── runner.py             # Full pipeline orchestration
│   │   ├── reporting.py          # Charts, tearsheet, methodology doc
│   │   ├── allocation.py         # Fixed / Kelly / Risk-Parity sizing
│   │   ├── diagnostics.py        # Regime, cost attribution, ablation
│   │   ├── walk_forward.py       # Walk-forward cross-validation
│   │   ├── portfolio.py          # Multi-asset aggregation
│   │   ├── quant_stats.py        # Sharpe, Sortino, PSR, DSR, bootstrap CI
│   │   ├── registry.py           # Append-only run provenance ledger
│   │   ├── logging_setup.py      # Structured logging (console + JSON file)
│   │   ├── strategy.py           # Abstract Strategy base class
│   │   ├── strategies/
│   │   │   └── funding_arb.py    # FundingArbStrategy
│   │   └── experiments/
│   │       ├── schema.py         # Pydantic experiment spec (YAML-driven)
│   │       └── runner.py         # Experiment runner
│   ├── tests/
│   │   ├── test_backtester.py
│   │   ├── test_funding_arb.py
│   │   ├── test_data_loader.py
│   │   ├── test_allocation.py
│   │   ├── test_diagnostics.py
│   │   ├── test_portfolio.py
│   │   ├── test_statistics.py
│   │   ├── test_walk_forward.py
│   │   └── test_warmup_seeding.py
│   └── requirements.txt
├── data/
│   ├── raw/                      # C++ output CSVs
│   └── clean/                    # Processed Parquet files
├── results/                      # Backtest output (auto-generated)
├── scripts/                      # Utility scripts
├── .github/workflows/            # CI (on push) + nightly backtest
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
└── .pre-commit-config.yaml
```

---

## Setup

### Option A — Docker (recommended)

```bash
docker-compose up --build
```

This builds the C++ fetcher and installs all Python dependencies in an isolated container.

### Option B — Local

**Prerequisites:** CMake ≥ 3.16, C++17 compiler, libcurl, Python ≥ 3.10

```bash
# 1. Build the C++ fetcher
cd cpp
bash bootstrap.sh
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
cd ..

# 2. Install Python dependencies
pip install -r python/requirements.txt
```

---

## Usage

### Step 1 — Fetch data from Bybit

```bash
./cpp/build/bybit_fetcher \
  --symbol      BTCUSDT \
  --start       2024-01-01 \
  --end         2026-05-01 \
  --kline-out   data/raw/btcusdt_1h.csv \
  --funding-out data/raw/btcusdt_funding.csv \
  --interval    1h
```

| Flag | Description |
|------|-------------|
| `--symbol` | Trading pair, e.g. `BTCUSDT` |
| `--start` / `--end` | Date range `YYYY-MM-DD` |
| `--kline-out` | Output path for klines CSV |
| `--funding-out` | Output path for funding CSV |
| `--interval` | Candle size: `1h`, `4h`, or `1d` (default `1h`) |

### Step 2 — Clean and align data

```bash
python python/src/data_loader.py \
  --klines  data/raw/btcusdt_1h.csv \
  --funding data/raw/btcusdt_funding.csv \
  --output  data/clean/btcusdt_1h.parquet \
  --verbose
```

Validates OHLC ordering, checks funding rate range, forward-fills gaps, aligns funding to hourly bars via point-in-time join, and adds `bars_since_funding`.

### Step 3 — Run the full pipeline

```bash
python python/src/runner.py \
  --data          data/clean/btcusdt_1h.parquet \
  --output-dir    results/run_jan24_may26 \
  --oos-start     2025-10-01 \
  --starting-cash 10000 \
  --run-sweep \
  --run-wf \
  --wf-n-folds    3 \
  --allocation    kelly_risk_parity \
  --verbose
```

| Flag | Description | Default |
|------|-------------|---------|
| `--data` | Path to clean Parquet | required |
| `--output-dir` | Results directory | `results/` |
| `--oos-start` | Train / OOS split date | `2025-10-01` |
| `--starting-cash` | Initial capital (USD) | `10000.0` |
| `--run-sweep` | Run 81-config hyperparameter sweep on IS data | off |
| `--n-jobs` | Parallel workers for sweep (`-1` = all CPUs) | `-1` |
| `--run-wf` | Run walk-forward cross-validation | off |
| `--wf-n-folds` | Number of WF folds | `3` |
| `--wf-rolling` | Use rolling window instead of anchored/expanding | off |
| `--allocation` | Position sizing: `fixed`, `kelly`, `risk_parity`, `kelly_risk_parity` | `fixed` |
| `--assets` | Comma-separated symbols for multi-asset mode | — |
| `--data-dir` | Directory of per-asset Parquets (multi-asset mode) | — |
| `--verbose` | Enable DEBUG logging | off |

### Step 4 — Run tests

```bash
cd python && pytest tests/ -v
```

---

## Key Parameters (default config)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `z_window` | 60 bars | Rolling lookback for funding z-score |
| `z_threshold` | 2.0 | Entry trigger magnitude |
| `momentum_window` | 5 bars | Log-return window for momentum filter |
| `vol_window` | 24 bars | Realized volatility window |
| `vol_pct_lookback` | 720 bars | 30-day reference for vol percentile |
| `vol_filter_pct` | 0.90 | Skip if vol > 90th percentile |
| `max_hold_bars` | 10 | Time stop (hours) |
| `stop_loss_pct` | 1.5% | Adverse move exit |
| `notional_per_trade_usd` | $5,000 | Fixed position size |
| `warmup_bars` | 720 | Bars before trading begins (30 days) |
| `fee_taker_bps` | 6.0 bps | Bybit VIP0 taker fee |
| `slippage_bps` | 1.0 bps | Half-spread slippage estimate |
| `max_leverage` | 3× | Notional cap relative to equity |

---

## Advanced Features

### Hyperparameter Sweep

Runs a 3⁴ = 81-config grid over `z_window`, `momentum_window`, `vol_window`, `vol_pct_lookback` on in-sample data. Produces 12 heatmaps and a `sweep_results.csv` with gross/net Sharpe per config. Flags configs where the signal sign reverses across the parameter space (overfitting indicator).

```bash
python python/src/runner.py --data ... --run-sweep --n-jobs -1
```

### Walk-Forward Cross-Validation

Splits the IS period into N folds. Each fold: sweep 81 configs → pick best IS config → run OOS. Uses **state seeding** (carries the IS strategy end-state into OOS) to eliminate warmup penalty. Computes overfitting ratio = OOS Sharpe / IS Sharpe.

```bash
python python/src/runner.py --data ... --run-wf --wf-n-folds 3
# Add --wf-rolling for fixed-size rolling windows instead of expanding
```

### Dynamic Position Sizing

```bash
# Kelly fraction from IS equity returns
--allocation kelly

# Inverse-vol risk parity
--allocation risk_parity

# Both combined
--allocation kelly_risk_parity
```

### Multi-Asset Portfolio

```bash
python python/src/runner.py \
  --data-dir data/clean/ \
  --assets   BTCUSDT,ETHUSDT,SOLUSDT \
  --output-dir results/portfolio/
```

Runs per-asset backtests, combines with equal-dollar weighting, and produces portfolio-level Sharpe, correlation matrix, and drawdown.

### Experiment Schema (YAML-driven)

Define experiments declaratively in YAML for reproducible multi-run studies. See `python/src/experiments/schema.py` for the Pydantic spec.

---

## Statistical Metrics

All metrics are annualized for 24/7 crypto markets (factor = √(24 × 365)).

| Metric | Description |
|--------|-------------|
| **Sharpe** | Annualized risk-adjusted return |
| **Sortino** | Sharpe penalising only downside volatility |
| **PSR** | Probabilistic Sharpe — P(true Sharpe > 0), accounts for non-normality |
| **DSR** | Deflated Sharpe — PSR corrected for multiple-testing across sweep configs |
| **CAGR** | Compound annual growth rate |
| **Max Drawdown** | Largest peak-to-trough decline |
| **Bootstrap CI** | 95% confidence interval via stationary block bootstrap (Politis & Romano 1994) |

---

## Reproducibility

Every run appends a row to `results/registry.parquet` containing:

- Git SHA of the code at run time
- SHA256 hash of the strategy config
- SHA256 hash of the input data
- Runtime and peak memory usage
- IS and OOS Sharpe, CAGR, and drawdown

This guarantees any result in `results/` can be exactly reproduced.

---

## Output Files

Each run directory (e.g. `results/test_default/`) contains:

| File | Description |
|------|-------------|
| `summary.json` | Sharpe, CAGR, max drawdown, trade count, fees, capacity estimate |
| `equity.parquet` | Hourly equity curve |
| `pnl.parquet` | Per-bar: gross_pnl, fees, slippage, funding_pnl |
| `position.parquet` | Hourly BTC position |
| `trades.parquet` | Trade log: timestamp, side, qty, price, fees, exit reason |
| `report/equity_curve.png` | Strategy vs buy-and-hold |
| `report/drawdown.png` | Drawdown over time |
| `report/pnl_decomposition.png` | Cumulative P&L components |
| `report/monthly_returns.png` | Monthly returns heatmap |
| `report/trade_pnl_distribution.png` | Per-trade net P&L histogram |
| `report/bootstrap_distribution.png` | Bootstrap Sharpe CI distribution |
| `report/regime_performance.png` | Sharpe by bull/bear/chop regime |
| `report/REPORT.md` | Full narrative performance report |
| `report/METHODOLOGY.md` | Signal, entry/exit, cost assumptions |
| `report/{name}_tearsheet.html` | QuantStats HTML tearsheet |
| `sweep/sweep_results.csv` | All 81 configs with IS metrics |
| `sweep/heatmap_*.png` | Parameter-pair heatmaps (12 total) |
| `walk_forward/wf_equity_curve.png` | Stitched OOS equity across folds |
| `walk_forward/wf_fold_performance.png` | Per-fold Sharpe bar chart |
| `walk_forward/wf_param_stability.png` | Best params per fold |

---

## Backtest Results (Jan 2024 – May 2026)

Run on 20,425 hourly bars. OOS period: Oct 2025 – May 2026 (7 months).

| Period | Return | Sharpe | Max DD | Trades |
|--------|--------|--------|--------|--------|
| In-sample | -9.3% | -1.08 | -14.2% | 264 |
| Out-of-sample | +0.1% | +0.06 | -3.9% | 58 |
| OOS at 0.5× fees | +1.0% | +0.39 | -3.7% | 58 |

**P&L decomposition (OOS):** Gross +$214 — Fees -$174 — Slippage -$29 = Net +$11 on $10k capital.

The gross signal is real (IS gross Sharpe +1.09 across 81 configs), but taker fees consume the edge at $5k notional. Half-fee execution (maker orders or VIP tier) produces a viable OOS Sharpe of +0.39.

---

## CI / Automation

`.github/workflows/ci.yml` runs on every push:
- Lint with ruff
- Type-check with mypy
- Full pytest suite

`.github/workflows/nightly.yml` runs a scheduled backtest on the latest data.

Pre-commit hooks (`.pre-commit-config.yaml`) enforce formatting and linting locally before commit.

---

## Dependencies

**C++:** CMake ≥ 3.16, C++17, libcurl, nlohmann/json (header-only, auto-downloaded)

**Python:** pandas, pyarrow, numpy, scipy, matplotlib, seaborn, pydantic, structlog, psutil, quantstats (optional, for HTML tearsheet)

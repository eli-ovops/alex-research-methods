# Cross-Sectional Momentum Strategy

A systematic ETF momentum strategy using elastic net regression to predict forward active returns.

## Strategy Overview

**Investment Universe**: 15-16 liquid ETFs covering global equities, bonds, sectors, and real assets

**Signal Generation**:
- Elastic net model predicts 10-day forward active returns (vs cross-sectional mean)
- Fixed feature dictionary: momentum, volatility, drawdown, relative returns, correlations, macro/regime indicators
- Time-series cross-validation for hyperparameter selection

**Portfolio Construction**:
- Long-only K-of-N (base K=6)
- Position caps: 25% per ETF, 70% equities, 20% HY, 40% real assets
- No-trade bands to control turnover
- Cash allocation for excess capital

**Risk Management**:
- Crash regime: Reduce K, tighten caps, boost defensives (bonds/gold)
- Melt-up regime: Allow slightly higher K
- Regime detection via VIX z-score and market shock flags

**Backtesting Framework**:
- Walk-forward validation (5Y train / 1Y test / 1Y slide)
- No look-ahead bias
- Transaction costs: 3 bps per side
- Daily rebalancing with execution lag

## Directory Structure

```
crosssecmom/
├── data/                    # Data loading and labels
│   ├── data_manager.py      # ETF + macro data loader
│   └── labels.py            # Forward active return computation
├── features/                # Feature engineering
│   ├── feature_engineering.py
│   └── scalers.py
├── models/                  # Prediction models
│   └── elastic_net_model.py
├── portfolio/               # Portfolio construction
│   ├── k_of_n_allocator.py
│   └── transaction_costs.py
├── risk/                    # Risk management
│   └── risk_overrides.py
├── backtest/                # Backtesting engine
│   ├── walkforward.py
│   ├── benchmarks.py
│   └── performance_metrics.py
├── utils/                   # Utilities
│   ├── config.py
│   └── reporting.py
├── crosssecmom_config.yaml  # Configuration file
├── run_crosssecmom.py       # Main runner script
└── README.md
```

## Configuration

All parameters are specified in `crosssecmom_config.yaml`:

**Key parameters**:
- `data.universe`: List of ETF tickers
- `portfolio.base_k`: Target number of positions (default: 6)
- `labels.forecast_horizon`: Forward return period (default: 10 days)
- `walk_forward.train_years`: Training window (default: 5 years)
- `model.hyperparam_grid`: Elastic net hyperparameter search space
- `portfolio.limits`: Position and asset class caps
- `risk_overrides`: Crash/melt-up regime rules

## Usage

### Basic Execution

```bash
cd /path/to/Morias/Quant/strategies/crosssecmom
python run_crosssecmom.py
```

### Custom Configuration

```bash
python run_crosssecmom.py --config /path/to/custom_config.yaml
```

### Output

Results are saved to `results/` directory:
- `oos_returns_net.csv`: Out-of-sample net returns
- `oos_positions.csv`: Position weights over time
- `performance_metrics.csv`: Performance metrics comparison
- `crosssecmom_report.pdf`: Comprehensive PDF report with charts

## ETF Universe

**Core Global** (2):
- VT: Total world equities
- BNDW: Global bonds

**Regional Equities** (3):
- VTI: US total market
- IEFA: Developed ex-US
- IEMG: Emerging markets

**Sectors** (4):
- XLK: Technology
- XLE: Energy
- XLF: Financials
- VNQ: US REITs

**Rates/Credit** (4):
- IEF: 7-10Y Treasuries
- SHY: Short Treasuries
- LQD: Investment-grade credit
- HYG: High-yield credit

**Real Assets** (2):
- GLD: Gold
- DBC: Broad commodities

## Feature Dictionary

### Per-ETF Features (computed for each ETF)

**Momentum** (6 features):
- `mom_Xd`: X-day cumulative log returns (X = 3, 5, 10, 20, 60, 120)

**Volatility** (3 features):
- `vol_Xd`: X-day realized volatility (X = 5, 20, 60)

**Max Drawdown** (2 features):
- `dd_Xd`: X-day maximum drawdown (X = 20, 60)

**Shock** (2 features):
- `ret_1d`: 1-day log return
- `ret_1d_z`: 1-day return scaled by 60d volatility

**Relative Returns** (6 features):
- `rel_X_vs_VT`: X-day return vs VT (X = 5, 20, 60)
- `rel_X_vs_basket`: X-day return vs equal-weight basket (X = 5, 20, 60)

**Correlations** (2 features):
- `corr_20_VT`: 20-day correlation with VT
- `corr_20_BNDW`: 20-day correlation with BNDW

**Asset Type Flags** (4 features):
- `is_equity`, `is_bond`, `is_real_asset`, `is_sector`

### Macro/Regime Features (same across all ETFs per date)

**Macro** (5 features):
- `vix_level`: VIX index level
- `vix_z_1y`: VIX z-score (1-year rolling)
- `yc_slope`: 10Y - 2Y yield spread
- `short_rate`: 3M T-bill rate
- `credit_proxy_20`: 20d return spread (HYG - LQD)

**Regime Flags** (4 features):
- `crash_flag`: VT return < -2.5σ (60d)
- `meltup_flag`: VT return > +2.5σ (60d)
- `high_vol`: VIX z-score > 1
- `low_vol`: VIX z-score < -1

**Total**: ~35 features per (date, ETF) observation

## Model Details

**Elastic Net Regression**:
- Combines L1 (lasso) and L2 (ridge) penalties
- Sparse feature selection via L1 penalty
- Hyperparameters: `l1_ratio` ∈ {0.1, 0.5, 0.9}, `alpha` ∈ {1e-4, ..., 10}
- Time-series CV (5 folds) for selection
- Refit on full training window with best parameters

**Feature Scaling**:
- Per-ETF standardization for continuous features
- Global standardization for macro features
- Binary flags not scaled

## Portfolio Rules

**Selection**:
1. Rank ETFs by predicted alpha (descending)
2. Filter: predicted alpha > `alpha_min` (default: 0)
3. Select top K (default: 6)

**Weighting**:
- Equal weight among selected ETFs
- Apply position caps:
  - 25% max per ETF
  - 70% max equity exposure
  - 20% max HYG
  - 40% max real assets (GLD + DBC)
- Leftover capital held as cash

**Trading**:
- 2% no-trade band to reduce turnover
- 3 bps transaction cost per side

**Risk Overrides**:
- **Crash regime** (VIX z > 2 or crash flag):
  - Reduce K to min 3
  - Tighten equity cap to 30%
  - Max 50% invested
  - Boost defensive ETFs (BNDW, IEF, SHY, LQD, GLD)
- **Melt-up regime** (melt-up flag and VIX z not too high):
  - Allow K = base_k + 1 (e.g., 7)

## Benchmarks

**Equal Weight**:
- Monthly rebalanced equal-weight all ETFs

**Simple Momentum**:
- Rank by 60d return
- Top 6 equal-weighted
- Monthly rebalanced
- No ML, no feature engineering

## Performance Metrics

- Sharpe ratio
- Sortino ratio
- Calmar ratio (CAGR / max drawdown)
- CAGR
- Volatility
- Maximum drawdown
- Win rate
- Profit factor

## Data Requirements

**ETF Prices**: Adjusted close prices from yfinance

**Macro Data**:
- VIX: `^VIX`
- 10Y Treasury: `^TNX`
- 3M T-bill: `^IRX` (proxy for 2Y and short rate)

**Cache**: All data cached in `D:\REPOSITORY\Data\crosssecmom`

## Dependencies

```
pandas
numpy
scikit-learn
yfinance
matplotlib
reportlab
pyyaml
```

## Implementation Notes

1. **No look-ahead**: All features use data up to time t; labels measure t+1 to t+1+H
2. **Return clipping**: Daily returns clipped to ±5σ for feature calculation only
3. **Execution lag**: 1 day lag between signal and execution (t → t+1 close)
4. **Forward filling**: Macro data forward-filled for missing dates
5. **NaN handling**: Observations with NaN features excluded from training; filled with 0 for prediction

## Development

Based on `alpha_signals` utilities structure:
- `data_manager.py`: Incremental data downloads with caching
- `walk_forward.py`: Walk-forward validation framework
- `performance.py`: Performance metrics calculation
- `reporting.py`: PDF report generation

## Future Enhancements

- [ ] Add leverage / short positions
- [ ] Expand universe to sector/country ETFs
- [ ] Alternative models (XGBoost, LightGBM)
- [ ] Ensemble predictions
- [ ] Volatility targeting
- [ ] Dynamic K based on volatility regime
- [ ] Multi-horizon forecasts

## References

- Jegadeesh & Titman (1993): Returns to Buying Winners and Selling Losers
- Moskowitz, Ooi, Pedersen (2012): Time Series Momentum
- Zou & Hastie (2005): Regularization and Variable Selection via the Elastic Net

## License

Internal research use only.

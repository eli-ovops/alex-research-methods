# Momentum ETF Rotation, Research, Backtest, and Live Trading

<details open>
<summary> <b>Brief Review<b></summary>

A cross-sectional momentum ETF rotation strategy, built end-to-end: research and signal design,
a risk-managed event-driven backtest engine, and a live trading system that talks to Interactive
Brokers (single or multiple portfolios, paper or real accounts). The strategy logic itself is
simple, rank a universe of sector/asset-class ETFs by trailing momentum, hold the top N, rotate
monthly, the bulk of the engineering is in making that simple idea safe to run unattended:
circuit breakers, idempotent scheduling, tamper-evident audit logs, email-commanded remote
control, and a config-approval gate before any real order can be placed.

Below is a real backtest (2006-2025, real ETF price history, the project's own
`run_custom_backtest()`) of the rotation strategy against a plain buy-and-hold SPY benchmark,
across three scenarios that vary signal concentration (`top_n`) and rebalance cadence
(`holding_period`), the two structural dimensions this project's own research notebooks already
study, not a search across many configs for a flattering one, see
`notebooks/research/DHI0016_notebook3_full_backtest_IMPROVED.ipynb`'s "Multi-Scenario Equity
Curve" cell for the exact reproducible source:

<p align="center">
<img src="docs/img/equity_curve.png?raw=true" alt="Momentum ETF rotation scenarios vs buy-and-hold SPY equity curve" width="85%"/>
</p>

| Scenario | CAGR | Ann. Vol | Sharpe | Max Drawdown |
|---|---|---|---|---|
| Default (`top_n=10`, `holding_period=1`) | 6.79% | 10.17% | 0.70 | -27.48% |
| Concentrated (`top_n=5`, `holding_period=1`) | 7.07% | 12.12% | 0.63 | -32.37% |
| Concentrated + Quarterly (`top_n=5`, `holding_period=3`) | 6.64% | 12.19% | 0.59 | -22.03% |
| SPY (buy-and-hold benchmark) | 10.67% | 15.20% | 0.75 | -50.78% |

**Read this chart honestly, not optimistically:** none of these three scenarios beat SPY's raw
CAGR or Sharpe over this ~19.6-year window, that's reported plainly here, not hidden. What
concentration and cadence changes DO buy is meaningfully lower volatility and a substantially
shallower max drawdown (-22% to -32% vs. SPY's -51%), consistent with this being a
lower-volatility rotation strategy, not a return-maximizing one, at least in this backtest
window. That's not a bug being hidden, it's the whole point of the "Project Maturity & Safety"
section below. This project is a well-tested *trading system*, not a proven *edge*, and the
README says so on purpose.

**What's actually here:**
- Risk-managed backtest engine, correlation-spike detection, liquidity-stress-aware slippage,
  time-based stops, VaR/CVaR, scenario shocks, capacity checks
- Resilient price-vendor fetching (FMP -> EODHD -> yfinance auto-fallback cascade): bounded
  retry-with-backoff on transient failures (HTTP 429/5xx, network-level errors) before falling
  through to the next vendor, plus rate-limit-aware pacing between per-ticker requests so a
  larger portfolio doesn't burst-fire requests at a free-tier vendor's rate limit, see
  `CLAUDE.md`'s `core/functions.py` bullet
- Live execution against IBKR (`ibapi`), connection retry, fill confirmation, sells-before-buys
  sequencing, cash-aware buy sizing, slippage-tolerance checks, whole-share flooring at
  submission time (IBKR's API has no fractional equity/ETF order support at all, see
  `docs/DEPLOYMENT.md`), optional extended-hours (pre-market/after-hours) trading via
  `allow_extended_hours` (switches to LMT + `outsideRth`, since MKT never works outside RTH)
- Multi-portfolio orchestration on one shared IBKR account, with capital-allocation and
  ticker-overlap safety checks. Any number of portfolios may use `total_value: null` ("give me
  capital"); fixed (non-null) portfolios reserve their capital first, and if multiple portfolios
  are null, they split the remaining account value equally, the resolved sum across every
  portfolio can never exceed the real account value, see `docs/RUNNING.md`
- Portfolio-level AND account-wide circuit breakers (% and $ drawdown), idempotent daily
  scheduling, config-approval gate before `--live` will run. Monthly (default) or weekly
  rebalancing, both targeting the first real NYSE trading day of the period via
  `pandas_market_calendars`, automatically rolling forward past weekends/holidays rather than
  firing on a fixed calendar date. Long-term (monthly-scale, the academically-studied default)
  or short-term (weekly-scale, an unvalidated variant) momentum lookback windows, both
  configurable via `holding_period`/`lookback_period` in `config.example.yaml`. An 11-way
  selectable `strategy_type` field (`config.yaml`'s `default_risk`/`risk_overrides`, independent
  per portfolio on a shared account, `risk_monitor.py` stays unaware of it by design): the base
  cross-sectional signal plus Dual, Volatility-Scaled, Correlation-Weighted, and Rank & Sign
  Momentum (config presets over existing fields), Multi-Timeframe Composite, Absolute
  (Time-Series), Residual, and Path-Dependent Momentum (new ranking/selection logic, live AND
  backtest parity), and Hybrid Multi-Factor (momentum + fundamentals blend, LIVE-ONLY, no
  point-in-time historical fundamentals source exists to backtest it honestly), see
  `docs/MOMENTUM_STRATEGIES.md`. A full
  Mandatory/Recommended/Nice-to-Have risk-strategy tier map (portfolio- and account-level
  volatility targeting, an Antonacci-style absolute-momentum overlay, a flat position-size cap,
  both circuit breakers, a correlation-spike monitor, and a pre-trade real-time bid-ask spread
  gate), plus the original six long-term/short-term advisory warnings and config toggles
  (Momentum Persistence, Lookback-to-Hold Ratio, Turnover Limit, Skip-Month Guardrail,
  per-position Volatility-Adjustment budget), see `docs/RISK_CONSTRAINTS.md`. An opt-in
  broker-side protective stop (`attach_broker_stop_loss`, LIVE-ONLY): a REAL IBKR bracket order
  (parent BUY + child STP SELL) attached at BUY time, protecting the position at the BROKER
  ITSELF even when this app isn't running, belt-and-suspenders alongside the pre-existing
  Python-side `auto_execute_stop_loss` check (which only ever runs when this app is actually
  invoked), with a broker-truth-based cancel-before-sell mechanism so this app's own rebalance
  and the broker's own triggered stop can never both try to sell the same shares, see
  `docs/RISK_CONSTRAINTS.md`'s "Broker-Side Protective Stop" section. Per-ticker stop-loss
  override (`ticker_risk_overrides`, `{}` default = no change): independently enable/disable the
  stop-loss check for any single ticker, or give it its own width instead of the portfolio-wide
  `stop_loss_pct`, honored everywhere `stop_loss_pct` is consulted (the daily drawdown check,
  reporting, and the broker-side bracket above), see `docs/RISK_CONSTRAINTS.md`'s "Per-Ticker
  Stop-Loss Override" section. Trailing stop-loss (`use_trailing_stop`/`trailing_stop_pct`,
  opt-in, LIVE + BACKTEST): distinct from the fixed-from-entry `stop_loss_pct` above, exits once
  price has fallen `trailing_stop_pct` from a position's OWN highest price since entry, locking
  in gains as a position runs up rather than only capping losses; a Python-side daily ratchet
  (works in dry-run), see `docs/RISK_CONSTRAINTS.md`'s "Trailing Stop-Loss" section. Broker-native
  trailing stop (`attach_broker_trailing_stop`, LIVE-ONLY, opt-in): a REAL IBKR `TRAIL` order
  attached at BUY time, the broker-native counterpart to the Python-side ratchet above, protecting
  continuously at the broker even while this app isn't running. When combined with
  `attach_broker_stop_loss` above, the two children attach as an IBKR One-Cancels-All (OCA) pair,
  whichever triggers first cancels the other at the broker, matching `trailing_stop_pct`'s own
  "whichever triggers first wins" semantics extended to the broker level, see
  `docs/RISK_CONSTRAINTS.md`'s "Broker-Native Trailing Stop" section. Flooring remainder redeployment
  (`redeploy_flooring_remainder`,
  opt-in): since IBKR has no fractional equity order support, every BUY floors to a whole share
  count, leaving a small per-ticker leftover unused, this pools that leftover across the
  rebalance's BUYs and redeploys it as extra whole shares of the single top-ranked pick, see
  `docs/RISK_CONSTRAINTS.md`'s "Flooring Remainder Redeployment" section. Liquidity/universe
  filter (`use_liquidity_filter`, opt-in, LIVE + BACKTEST): excludes a ticker from selection
  entirely (not just an advisory warning) on any rebalance its trailing average dollar volume
  falls below a threshold, see `docs/RISK_CONSTRAINTS.md`'s "Liquidity / Universe Filter"
  section (including a documented caveat: not effective under the `absolute_momentum`
  `strategy_type`, which selects by score, not rank). Technical-indicator entry confirmation
  (`use_technical_confirmation`, opt-in, LIVE + BACKTEST): an opt-in hard gate excluding a
  ticker from selection if it fails an enabled SMA-trend, RSI-overbought, or MACD-bullish
  sub-check, close-price-only so it works identically live and backtest, motivated by a real gap
  found reviewing IBKR's own Quant momentum-trading articles against this codebase (SMA/RSI/MACD
  were computed for the email report only, never wired into a selection decision before this),
  see `docs/RISK_CONSTRAINTS.md`'s "Technical-Indicator Entry Confirmation" section. Risk-based
  ("fixed-fractional") position sizing (`sizing_method: risk_based`, a 4th sizing option
  alongside `inverse_vol`/`score_proportional`/`equal_weight`): sizes each position off its own
  stop-loss distance and `risk_per_trade_pct` so a full stop-out loses a fixed fraction of
  capital (the standard CTA/Van Tharp "risk 1-2% per trade" rule), the only one of the four that
  doesn't force full investment, aggregate exposure emerges from the risk budget instead, see
  `docs/RISK_CONSTRAINTS.md`'s "Risk-Based Position Sizing" section. Volume-confirmed signal
  quality (`use_volume_confirmation`, opt-in, LIVE + BACKTEST): distinct from the liquidity
  filter's absolute dollar-volume threshold, this is a relative volume-TREND confirmation of the
  price move itself, a ticker's recent trading volume must be at least
  `volume_confirmation_min_ratio` times its own earlier volume to remain eligible, reusing the
  same fetched volume data as the liquidity filter, no extra API calls, see
  `docs/RISK_CONSTRAINTS.md`'s "Volume-Confirmed Signal Quality" section. Regime
  filter volatility dimension
  (`regime_vol_threshold`, opt-in, `None` default byte-identical to before, LIVE + BACKTEST):
  blends the regime benchmark's own trailing realized volatility into the existing SMA-trend
  regime scalar, so a bullish-but-suddenly-volatile market also gets throttled, not just a
  bearish one, with a dedicated `MARKET_VOLATILITY_REGIME_DEFENSIVE` alert when volatility alone
  is what triggered it, see `docs/RISK_CONSTRAINTS.md`'s "Regime Filter: Volatility Dimension"
  section. Whole-book negative momentum cash filter (`use_negative_universe_cash_filter`,
  opt-in, LIVE + BACKTEST): holds literal cash instead of the "least bad" pick or a
  defensive-ticker swap when NOTHING in the eligible universe shows positive momentum, distinct
  from and takes precedence over `use_absolute_momentum`'s per-ticker swap when both trigger at
  once, with a dedicated `MARKET_WIDE_NEGATIVE_MOMENTUM_CASH` alert, see
  `docs/RISK_CONSTRAINTS.md`'s "Whole-Book Negative Momentum Cash Filter" section. Also a
  distinct `NO_ELIGIBLE_TICKERS` alert (any cause) plus a differently-worded no-action email when
  zero tickers pass selection, see `docs/ALERT_LOG.md`. Sector/asset-class concentration cap
  (`ticker_sectors` + `max_sector_weight`, opt-in, LIVE + BACKTEST, Nice-to-Have tier): caps the
  SUMMED weight of every ticker mapped to the same sector (a manual mapping, no vendor
  sector-data source exists in this project), scaling an over-cap sector down to exactly the
  limit without redistributing the freed weight elsewhere, left as unallocated cash instead, see
  `docs/RISK_CONSTRAINTS.md`'s "Sector / Asset-Class Concentration Cap" section. Equal Risk
  Contribution (ERC/risk-parity) sizing (`sizing_method: equal_risk_contribution`, LIVE +
  BACKTEST): a 5th sizing option alongside `inverse_vol`/`score_proportional`/`equal_weight`/
  `risk_based`, every pick contributes an equal share of total portfolio risk rather than an
  equal dollar amount or a volatility-only weight, backed by a new Ledoit-Wolf-style shrinkage
  covariance estimator (`core/covariance.py`, also optionally usable by the existing correlation
  penalty via `use_shrinkage_covariance`) for a better-conditioned covariance matrix than raw
  sample covariance. VaR/CVaR Budget (`enabled_risk_strategies: [var_cvar_budget]`, opt-in, LIVE
  + BACKTEST): an active pre-trade gross-exposure throttle using `historical_var_cvar()`
  (previously fully coded but wired into nothing anywhere in the codebase), a new multiplicative
  scalar alongside the existing volatility-targeting/momentum-crash scalars. Liquidity-Adjusted
  Position Sizing (`enabled_risk_strategies: [liquidity_adjusted_sizing]`, opt-in, LIVE +
  BACKTEST): continuous ADV-based position-size scaling, distinct from the pre-existing advisory-
  only capacity check (which only warns, never resizes), scales any oversized target allocation
  down to exactly its ADV cap. All three verified end-to-end (2026-08-05) against a real IBKR
  paper account and inside a rebuilt Docker container, real BUY fills confirmed for each feature
  individually and combined, see `docs/RISK_CONSTRAINTS.md`'s "Opt-in overlay strategies"
  section for the full verification writeup. Cost-vs-Edge Hurdle Filter
  (`cost_edge_hurdle_multiplier`, opt-in, LIVE-ONLY): a relative pre-trade check alongside the
  existing absolute `max_bid_ask_spread_pct` ceiling, drops an order whose estimated round-trip
  transaction cost (2x the real-time spread) exceeds a multiplier of the signal's own strength,
  reusing the same real-time quote fetch, zero extra IBKR calls when both are set. Execution
  Participation-Rate Limits (`use_participation_rate_limit`/`max_participation_pct`, opt-in,
  LIVE-ONLY): delegates to IBKR's native `PctVol` execution algo, attached directly to the parent
  order rather than any local TWAP/multi-run slicing (this app has no intraday scheduling loop to
  build real slicing against). Both close the full 24-item institutional risk-management audit
  (Epic 4, the final epic in this program), see `docs/RISK_CONSTRAINTS.md`'s "Cost-vs-Edge Hurdle
  Filter"/"Execution Participation-Rate Limits" sections, including two real bugs found and fixed
  via live paper-account testing (a wrong IBKR algo-param tag name, and a real RTH/algo-order
  incompatibility) and an honestly disclosed limitation (the actual intraday fill behavior was
  never observed, both live tests ran after market close). Restart-safe by
  construction in `--live` mode (broker-sourced
  holdings, calendar-derived scheduling, persisted local/bind-mounted state, both native Python
  and Docker), plus a non-blocking `MISSED_REBALANCE_DAY` warning if a scheduled rebalance was
  missed entirely while the app was off, automatic safe reconciliation of a ticker orphaned from
  its own portfolio's history (`ORPHANED_POSITION`) versus one that may belong to a sibling
  portfolio sharing the account (`UNRECOGNIZED_POSITION`, left untouched), a `total_value` drift
  warning for fixed-capital portfolios, and an opt-in `persist_dry_run_state` flag for a
  no-IBKR-required persistent paper ledger, see `docs/RUNNING.md`'s "Restart and Resume Behavior"
- Hash-chained, tamper-evident audit logs for trades, email commands, and alerts, three
  separate logs, kept deliberately apart. The alert log records which outbound email account
  (`SMTP_USER`) would notify each alert, self-resolving from the environment, no call site
  changes needed, see `docs/ALERT_LOG.md`
- Opt-in time-based log retention (`enable_log_retention`, default off, byte-identical when
  disabled): archives, never deletes, rows older than `3*(lookback_period+holding_period)` (in
  calendar days) out of the trade log, signal rankings log, portfolio snapshot, and (using the
  largest window across every opted-in portfolio) the shared alert/email-command logs. A
  still-open position's archived entry lot is never lost from FIFO P&L/cost-basis calculations,
  and every archive remains independently hash-chain-verifiable, see `docs/LOG_RETENTION.md`
- Categorized email notifications (CRITICAL/STANDARD/PERIODIC/DAILY/WARNING, plus Epic 10's
  WEEKLY/QUARTERLY/ANNUAL/SUMMARY) and pydantic-
  validated, fail-safe email-commanded remote actions (pause/resume/liquidate/adjust risk
  params/report), the rebalance summary email includes a "What Actually Happened" column
  showing the real fill outcome per ticker (filled, dropped, rejected, still open, dry-run), not
  just the intended signal action. Every email command gets a three-way ACCEPTED/REJECTED/ERROR
  outcome, logged unconditionally and, by default, replied to by email
  (`notifications.send_email_command_feedback`, gates the email only), a command that parses
  successfully but fails while being applied is isolated to itself, not aborting the rest of
  that run's batch, see `docs/EMAIL_COMMANDS.md`
- Monthly and (opt-in, off by default) daily performance reports per portfolio, technical
  indicators (trend/momentum/volatility/volume) and fundamental indicators (P/E, PEG, ROE,
  Debt-to-Equity, Current Ratio) for currently held positions, macro context (Fed Funds Rate,
  CPI), per-ticker position performance since entry (`--live` mode only), strategy
  performance indicators since inception (Total Return, CAGR, Max Drawdown, Std Dev, Sharpe,
  Sortino), and trailing-window benchmark comparison charts (1/3/6-month/YTD/1-year for the
  monthly report, 1-day/1/2/3-week for the daily report). Every rebalance email that produces
  orders also includes a "Full Signal Universe" second table, and a matching
  `logs/signal_rankings_log_<portfolio>.csv`, covering the FULL ranked universe (Momentum Rank,
  Rank Delta, Lookback Return, Current Close Price, Selection Status, Stop-Loss Price) for every
  configured ticker, not just the `top_n` actually selected, "Watchlist / Reserve" tickers
  included, see `docs/SIGNAL_RANKINGS_LOG.md`. Rank Delta (opt-in per portfolio via
  `use_rank_delta`, `false` default) shows each ticker's rank exactly `lookback_period` ago vs.
  today as colored rich text (`▲ +N`/`▼ -N`/`-`/`N/A`), widening that portfolio's price fetch
  when enabled so the historical comparison point is real, not NaN
- Dockerized, self-scheduling deployment (`docker compose up -d`, internal cron, no manual
  triggering needed for normal operation). `config.yaml` is bind-mounted (not baked into the
  image), so a live edit takes effect on the very next scheduled run automatically, no rebuild,
  no restart, no manual `docker cp`, both `daily-runner` and `risk_monitor.py` already re-read it
  fresh every invocation (stateless CLI processes, not a daemon). A `CONFIG_CHANGED` alert
  (`detect_and_log_config_change()`) logs a full field-by-field diff whenever a portfolio's
  effective config changes between runs, see `docs/DEPLOYMENT.md`'s "What needs what" section
  for the complete restart-vs-nothing matrix (`config.yaml`/`.env`/Dockerfile changes each need a
  different action, or none at all)
- 935-test pytest suite covering code mechanics, order sizing, config validation, audit-log
  integrity, multi-portfolio capital math, entirely on synthetic/mocked data, no live broker
  required to run it

**Recommended config presets** (LIVE-ONLY, tunes `daily_runner.py`'s signal generation, has no
effect on the backtest engine), warning-free starting points for each cadence, full field list
and rationale in `docs/RISK_CONSTRAINTS.md`'s "Recommended Config Presets" section:

| Preset | `holding_period` | `lookback_period` | `top_n` | Notes |
|---|---|---|---|---|
| Long-Term Momentum (Monthly) | `1` | `12` | `10` | Academically-studied default cadence |
| Short-Term Momentum (Weekly) | `0.25` | `1.0` | `5` | Unvalidated variant, see `docs/STRATEGY_THEORY.md` |

This is a curated subset (the fields most worth tuning to pick a cadence); both presets also
specify `target_portfolio_vol`, `portfolio_vol_lookback`, `use_absolute_momentum`,
`defensive_ticker`, and `max_bid_ask_spread_pct`, see `docs/RISK_CONSTRAINTS.md`'s
"Recommended Config Presets" section for the complete field list, per-field rationale, and the
full Mandatory/Recommended/Nice-to-Have risk-strategy tier map. Selecting a `strategy_type` (see
above) adds its own few strategy-specific fields on top of whichever base preset you start from,
per-strategy long-term/short-term additions and rationale are in `docs/MOMENTUM_STRATEGIES.md`'s
"Best Parameters (Long-Term vs. Short-Term) Per Strategy" section.

The project tree:

```
momentum-trading/
├── README.md                     <- you are here (only doc kept at root, as the entry point)
├── pyproject.toml                 package metadata, dependencies (uv/pip compatible)
├── requirements.txt                generated export of pyproject.toml's deps, for
│                                    pip-only/Docker environments not using uv/editable installs
├── requirements-dev.txt            adds pytest
├── Dockerfile                      containerized daily_runner.py + cron
├── docker-compose.yml              one-command container startup
├── config.example.yaml             copy to config.yaml and edit (config.yaml is gitignored);
│                                    ships Epic 9's best-validated recommendation as its own
│                                    example portfolios, see Known Gaps below
├── .gitignore
│
├── docs/                          structural governance & operational guides
│   ├── img/
│   │   ├── equity_curve.png        multi-scenario backtest vs SPY chart, shown above
│   │   ├── momentum_winners_vs_losers.png   Notebook 1 EDA: top vs bottom decile evidence
│   │   ├── momentum_win_rate_heatmap.png    Notebook 1 EDA: win rate by lookback/holding
│   │   └── momentum_decile_returns.png      Notebook 1 EDA: avg forward return by decile
│   ├── DEPLOYMENT.md               one-time setup on a new machine
│   ├── RUNNING.md                  day-to-day run commands
│   ├── TESTING.md                  how to run/interpret the test suite
│   ├── STRATEGY_THEORY.md          momentum theory + worked numeric example
│   ├── EMAIL_REPORTING.md          notification categories, monthly report config
│   ├── EMAIL_COMMANDS.md           remote email commands: syntax, security model
│   ├── ALERT_LOG.md                alert log schema, every alert_type, how it differs
│   │                                 from the trade log and email command log
│   ├── RISK_CONSTRAINTS.md         long-term/short-term momentum risk constraints,
│   │                                 advisory warnings and opt-in config toggles
│   ├── MOMENTUM_STRATEGIES.md      selectable `strategy_type` field: 11 momentum variants
│   │                                 (Dual, Volatility-Scaled, Residual, Absolute,
│   │                                 Rank & Sign, Hybrid Multi-Factor, Path-Dependent,
│   │                                 Correlation-Weighted, Multi-Timeframe Composite), how
│   │                                 presets compose, per-strategy best-parameter tables
│   ├── SIGNAL_RANKINGS_LOG.md      full ranked-universe log schema (selected + watchlist
│   │                                 tickers every rebalance), how it differs from the trade log
│   ├── LOG_RETENTION.md            opt-in archive-and-rotate log retention, the
│   │                                 3*(lookback_period+holding_period) window formula, the
│   │                                 FIFO cost-basis safety guarantee
│   └── ORPHAN_TRACKING.md          Epic 12: persisted first-detected-date tracking + the
│                                     Summary report's Orphaned Positions section, informational
│                                     only, never auto-applies a config.yaml change
│
├── notebooks/
│   ├── research/                  strategy design, signal research, backtesting
│   │   ├── DHI0016_notebook1_research_and_EDA_IMPROVED.ipynb    lookback/holding
│   │   │                           grid, walk-forward validation
│   │   ├── DHI0016_notebook2_strategy_coding_IMPROVED.ipynb     signal construction,
│   │   │                           liquidity filter
│   │   ├── DHI0016_notebook3_full_backtest_IMPROVED.ipynb       full backtest, factor
│   │   │                           decomposition, regime breakdown, dual momentum overlay
│   │   ├── crash_period_stress_test.ipynb   real 2008/2020/2022 crash replay on a
│   │   │                           long-history ETF proxy universe, risk-managed vs. naive
│   │   │                           baseline (Epic 13, see README's Known Gaps)
│   │   ├── out_of_sample_validation.ipynb   real pre-registered walk-forward +
│   │   │                           holdout validation via the real signal/execution pipeline,
│   │   │                           monthly regime (Epic 15, see README's Known Gaps)
│   │   ├── out_of_sample_validation_weekly.ipynb   same methodology, weekly regime
│   │   │                           (Epic 16, see README's Known Gaps)
│   │   ├── out_of_sample_validation_strategy_types.ipynb   same methodology, the other
│   │   │                           10 selectable strategy_type variants, monthly regime
│   │   │                           (Epic 17, see README's Known Gaps)
│   │   ├── out_of_sample_validation_strategy_types_weekly.ipynb   same methodology,
│   │   │                           weekly regime (Epic 18, see README's Known Gaps)
│   │   ├── out_of_sample_validation_new_strategy_types.ipynb   same methodology, the 2 NEW
│   │   │                           strategy_type values (proximity_52w_high,
│   │   │                           sector_relative_momentum), both regimes (Epic 7, see
│   │   │                           README's Known Gaps)
│   │   ├── parametric_stress_test.ipynb   hypothetical/forward-looking factor-shock
│   │   │                           scenario engine, complements crash_period_stress_test.ipynb's
│   │   │                           real historical replay (Epic 7, see README's Known Gaps)
│   │   ├── capacity_aum_analysis.ipynb   real capacity/AUM scaling curve (Epic 7,
│   │   │                           see README's Known Gaps)
│   │   ├── ensemble_signal_correlation_analysis.ipynb   real pairwise correlation of
│   │   │                           validated strategy_type variants, informs ensemble_momentum's
│   │   │                           default component selection (Epic 8, see README's Known Gaps)
│   │   ├── ensemble_weighting_scheme_search.ipynb   real walk-forward comparison of
│   │   │                           equal/confidence/inverse-correlation weighting schemes for
│   │   │                           ensemble_momentum (Epic 8, see README's Known Gaps)
│   │   ├── out_of_sample_validation_ensemble_momentum.ipynb   real pre-registered
│   │   │                           holdout validation of the final ensemble_momentum
│   │   │                           configuration (Epic 8, see README's Known Gaps)
│   │   └── out_of_sample_validation_best_practice_config.ipynb   real baseline-vs-
│   │                               full-protective-bundle holdout comparison, both regimes
│   │                               (Epic 9, see README's Known Gaps)
│   └── operational/               interactive validation & run walkthroughs (safe, dry-run only)
│       ├── live_signal_walkthrough.ipynb
│       ├── daily_runner_walkthrough.ipynb
│       ├── email_commands_walkthrough.ipynb
│       ├── portfolio_snapshot_report.ipynb   investor-facing view: positions,
│       │                           value over time, benchmark comparison, plus every measure
│       │                           the email reports show, position performance since entry
│       │                           (real, FIFO-reconstructed from the trade log, and an
│       │                           illustrative example), technical/fundamental indicators,
│       │                           macro context, since-inception stats, trailing-window chart
│       └── live_vs_backtest_reconciliation.ipynb   real live P&L vs. backtested P&L
│
├── src/momentum_trading/          installable package (`pip install -e .`)
│   ├── __init__.py
│   ├── daily_runner.py             CLI entry point / orchestrator (also registered as
│   │                                the `daily-runner` console script)
│   │
│   ├── core/                      pure data/signal logic, no execution or I/O side effects
│   │   ├── functions.py             data fetching (multi-vendor fallback), tear_sheet,
│   │   │                             shared helpers
│   │   ├── functions_quant_extensions.py   liquidity filter, walk-forward, bootstrap CI,
│   │   │                             factor decomposition, regime breakdown, dual momentum,
│   │   │                             VaR/CVaR, scenario shocks, capacity checks, multi-lookback,
│   │   │                             since-inception + trailing-window live performance stats
│   │   ├── technical_indicators.py  hand-rolled SMA/EMA/RSI/MACD/ATR/Bollinger/ADX/VWAP/OBV,
│   │   │                             not pandas-ta (dependency-conflicts with pandas>=3.0.3)
│   │   ├── fundamentals.py          P/E, PEG, ROE, Debt-to-Equity, Current Ratio for held
│   │   │                             positions, FMP `/stable/` first, EODHD fallback, file-cached
│   │   ├── macro_data.py            Fed Funds Rate, CPI via FRED, needs FRED_API_KEY,
│   │   │                             portfolio-wide (one fetch per run), file-cached
│   │   ├── strategy_signals.py      selectable strategy_type dispatch (see
│   │   │                             docs/MOMENTUM_STRATEGIES.md), the shared router BOTH
│   │   │                             live and backtest call so they can't diverge on which
│   │   │                             tickers get selected for a given strategy
│   │   ├── paths.py                 PROJECT_ROOT resolution, single source of truth for
│   │   │                             where config.yaml/data/logs live, regardless of CWD
│   │   ├── smtp_auth.py             shared SMTP auth for email sending, password-based
│   │   │                             (Gmail) or XOAUTH2 (Outlook/Microsoft 365)
│   │   └── audit_log.py             shared hash-chain append helper + the alert log
│   │                                 (logs/alerts_log.csv), every alert/warning event,
│   │                                 kept separate from the trade log and email command log
│   │
│   ├── backtest/
│   │   └── momentum_backtest.py     risk-managed backtest engine: BacktestConfig
│   │                                 (strategy_type selector, sizing_method incl.
│   │                                 equal_weight), run_custom_backtest, resolve_target_weights
│   │                                 (shared sizing logic also used by execution/), crash
│   │                                 protection (correlation-spike detection, liquidity-stress
│   │                                 handling, time-based stops)
│   │
│   ├── execution/
│   │   └── live_signal.py           live signal generation, order generation, IBKR
│   │                                 integration (with connection retry), multi-portfolio
│   │                                 orchestration, real P&L measurement, stale-price and
│   │                                 slippage-tolerance checks, per-ticker position
│   │                                 performance since entry (build_position_performance())
│   │
│   ├── risk/
│   │   ├── circuit_breaker.py       portfolio-level circuit breaker (%  and $ thresholds,
│   │   │                             email-override tightening-only enforcement),
│   │   │                             extracted from daily_runner.py so risk logic has no
│   │   │                             dependency on interfaces/ (alerting is dependency-injected)
│   │   └── risk_monitor.py          independent, read-only oversight process, watches
│   │                                 trade logs, can halt trading, cannot place orders
│   │
│   └── interfaces/
│       ├── notifications.py         categorized email notifications (CRITICAL/STANDARD/
│       │                             PERIODIC/DAILY/WARNING) + monthly & daily HTML report
│       │                             generation (shared builder, see CLAUDE.md)
│       ├── email_commands.py        pydantic-validated, fail-safe remote email commands
│       │                             (PAUSE/RESUME/LIQUIDATE/SKIP_NEXT_REBALANCE/
│       │                             TRIGGER_REPORT/ADJUST_PARAM/STATUS/SET_MAX_DRAWDOWN/
│       │                             ALERTS_REPORT)
│       └── email_diagnostics.py     backs `daily-runner --test-email`, live SMTP+IMAP
│                                     check independent of config.yaml
│
└── tests/                         pytest suite (935 tests), mirrors src/ layout where a
    ├── conftest.py                  test's primary subject is a single sub-package;
    ├── test_architecture.py         cross-cutting/integration tests stay at tests/ root
    ├── test_daily_runner.py
    ├── test_docker_entrypoint.py     docker-entrypoint.sh's crontab generation,
    │                                  run as a real subprocess
    ├── test_governance.py
    ├── test_reporting.py
    ├── test_execution_safety.py
    ├── backtest/
    │   └── test_momentum_backtest.py
    ├── core/
    │   ├── test_audit_log.py        hash-chain helper + alert log
    │   ├── test_technical_indicators.py
    │   ├── test_functions.py        vendor fallback cascade, retry-with-backoff +
    │   │                              rate-limit pacing (Epic 10)
    │   ├── test_functions_quant_extensions.py   since-inception + trailing-window stats
    │   ├── test_fundamentals.py       P/E, PEG, ROE, Debt-to-Equity, Current Ratio
    │   ├── test_macro_data.py         Fed Funds Rate, CPI (FRED)
    │   └── test_strategy_signals.py   selectable strategy_type dispatch (11 momentum
    │                                    variants), live/backtest parity
    ├── execution/
    │   └── test_live_signal.py
    └── interfaces/
        ├── test_email_diagnostics.py
        ├── test_notifications.py
        └── test_email_commands.py
```

</details>

<details open>
<summary> <b>Project Maturity & Safety<b></summary>

### Infrastructure safety ≠ strategy safety

These are two separate questions. This project answers the first one well; **the second one has
not been answered at all yet**:

| Question | Status |
|---|---|
| Does the code have circuit breakers, idempotency, alerting, audit logging? | ✅ Yes, tested |
| Has the strategy shown a positive out-of-sample (holdout) return on real data? | ⚠️ Run for real for both regimes (2026-08-04, see Known Gaps below). **Monthly** (`portfolio1`, Epic 15): walk-forward validation shows the shipped `lookback_period: 12` is genuinely robust (5 real historical folds, test-period Sharpe *not* degraded vs. train), but the single pre-registered 2015-2026 holdout shows only a modest Sharpe (0.39) with a **negative annualized alpha** (-2.63%) vs. SPY, and a 90% bootstrap CI that includes zero. **Weekly** (`portfolio2`, Epic 16): also robust on walk-forward (mean test Sharpe 1.34 vs. train 0.76, not degraded), but the search converged to a *longer* lookback (8 weeks) than the shipped default (4 weeks), a real, honest divergence from the monthly regime's result. The weekly holdout Sharpe (0.53) is modest but its 90% bootstrap CI is entirely positive (`[0.08, 1.05]`), a stronger statistical result than the monthly regime's, though its annualized alpha is still slightly negative (-0.70%). Positive on parameter robustness in both regimes, mixed on whether either shows a real edge beyond market-beta exposure. **The other 6 backtestable strategy variants, both regimes** (Epic 17 monthly, Epic 18 weekly): mostly cluster close to plain `momentum`'s own result in each regime (with 2-3 confirmed no-ops where a preset had nothing left to change). `residual_momentum` is the standout, consistently: strongest monthly result in the project (holdout Sharpe 0.46, alpha -0.17%, CI `[0.08, 0.96]`) and the closest-to-zero alpha of any weekly variant too (-0.09%, CI `[0.12, 1.14]`), a repeated pattern across regimes, not a one-off. `rank_sign_momentum` produced the best weekly holdout Sharpe (0.63) of the full-search batch. |
| Has it been validated against real 2008/2020/2022 history? | ⚠️ The risk-control *mechanism* has, using a long-history ETF proxy universe (see Known Gaps below), not the exact currently-configured portfolios (most of their tickers didn't exist in 2008). Real result: the risk-managed variant beat a naive-momentum baseline on max drawdown in all 6 head-to-head runs (both a monthly and weekly cadence, across 2008/2020/2022), most dramatically in 2008 (weekly regime: -11.5% vs. -26.0% max drawdown), at a real cost to upside capture during 2020's fast V-shaped recovery, and was actually worse than baseline on both metrics for 2022's monthly regime specifically, an honest, mixed result, not a uniform win. |
| Has it connected to a real broker even once? | ✅ Yes, paper (port 7497) connection, account summary, position fetch, and **confirmed real BUY and SELL order fills** (verified directly in TWS's own execution log across two portfolios, real prices, matching quantities). Getting here surfaced and fixed three real bugs (every order silently rejected while the run logged success; a misleadingly-short fill-confirmation poll window; an informational per-order notice mistaken for a rejection, causing an already-filled order to be logged as failed) and one hard IBKR platform limitation worked around (no fractional equity orders via API, ever, floored to whole shares). The live/real-money port (7496) is still unexercised |
| Has real live-vs-backtest divergence been measured? | ⚠️ Attempted for real (2026-08-03) against all three real portfolios' actual `dry_run=False` trade history; the notebook's methodology bugs are fixed and verified (real config load, `dry_run=False` filtering, `strategy_type`-aware signal reproduction, `custom_weights` sizing parity), and real Live P&L was computed successfully for all three. The head-to-head Backtest number itself is still blocked, not by a code defect but by real trading history simply being too young: `_build_report()`'s monthly-return diffing needs at least two completed calendar-month buckets to produce a non-NaN return, and the real history (~1-2 weeks old as of this writing, entirely inside one still-open month) can't supply that yet. See the Known Gaps entry below and `notebooks/operational/live_vs_backtest_reconciliation.ipynb`; rerun once real trading has spanned at least one full month-end. |

**Do not treat a well-tested codebase as a validated strategy.** See `docs/RUNNING.md`'s staged
rollout plan (Historical Validation → Paper → Small Live → Full Live) before allocating real
capital, and follow it in order, each stage exists because the previous one alone doesn't
answer whether the strategy actually works.

### ⚠️ Before you do anything live

- Everything defaults to **dry-run**, no real orders are ever placed unless you explicitly
  pass `--live`.
- **Paper-trade first.** See `docs/RUNNING.md` Section 3 before Section 4.
- Real-money trading requires two separate explicit flags together
  (`--port 7496 --confirm-live-trading`), this is intentional friction, not a bug.
- **Paper vs. live is not a stored "mode"**, the app is stateless per invocation. `--port 7497`
  vs. `--port 7496` just picks which TWS/IB Gateway port to connect to, and whichever account
  happens to be logged in on that port is what actually trades. This is an IBKR *convention*
  (7497 = paper, 7496 = live), not something the code verifies. Always confirm in TWS itself
  which account is logged in on the port you're about to use, especially before `--live`.
- `daily-runner --force-rebalance` (dry-run) is a fast sanity check for signal/sizing logic,
  it is **not** an all-in-one functionality test. It never opens an IBKR connection, never
  fetches real positions (so stop-loss/time-stop checks never even run), and never exercises
  the `--live` safety gates. Complete the paper-trading stage before trusting the broker-facing
  paths.
- Nothing here is investment advice. Momentum strategies carry real crash risk; past backtest
  performance is not a guarantee of future results.

### Known Gaps (read this before trusting a backtest number)

- **No point-in-time universe**, ETF picks use today's known survivors, backtested into the
  past; survivorship bias is not corrected.
- **Momentum crowding risk**, cross-sectional momentum is widely traded by CTAs/quant funds;
  when many players hold similar positions, momentum reversals ("crashes") tend to be sharper
  and faster than your own backtest can show, because it's a market-structure risk sitting
  outside any single account's data.
- **No tax modeling**, see `docs/RUNNING.md`'s tax-awareness note; realistic after-tax returns
  in a taxable account could be materially lower than any number shown here.
- **No capacity/market-impact validation on real order books**, the capacity check
  (`max_pct_of_adv`) is advisory and based on historical average volume, not real-time
  order-book depth.
- **The trade log never recorded a real fill price until Epic 7**, a real, confirmed gap found
  while designing that epic's slippage-calibration framework: `log_orders()` has always written
  the PRE-TRADE reference price (before the broker call even runs), never the real IBKR
  `avg_fill_price`, which previously only ever lived transiently in memory for the rebalance
  email. `execution/live_signal.py`'s new `log_fill_confirmations()` (a separate,
  `logs/fill_log_<portfolio>.csv` log, hash-chained) fixes this GOING FORWARD only, it cannot
  retroactively recover fill prices for any of this project's existing real trade history.
  `core/functions_quant_extensions.py`'s new `calibrate_slippage_model()` is the calibration loop
  this project's slippage model (`base_slippage_bps`/`vol_slippage_multiplier`) never had, but it
  starts with ZERO real fill data to fit against on day one, a prospective framework, not a
  retroactive fix, honestly disclosed as such. See `docs/RISK_CONSTRAINTS.md`'s "Real Fill-Price
  Logging + Slippage Model Calibration" section, including a separate, still-unfixed
  inconsistency it surfaced: the backtest engine's own slippage model has two divergent code
  paths (vol-scaled in the main day-loop, flat-rate in 4 exit branches).
- **IBKR's API has no fractional equity/ETF order support, period**, not an `ibapi` version
  issue, not fixable by this codebase. Confirmed both empirically (setting `cashQty` alongside
  `totalQuantity`, exactly per IBKR's own official sample code, still failed with `error 10243`
  for `STK` contracts, `cashQty` only works for forex/CASH-pair orders) and by direct API
  community confirmation. `place_orders_ibkr()` floors fractional share counts to whole shares
  immediately before submission (dropping the order, with a warning, if it floors to 0), the
  only way a live rebalance can place ETF orders at all. `allow_fractional_shares: true` still
  fully applies to backtest sizing and live drift/order-generation math; only the final IBKR
  submission is forced whole. See `DEPLOYMENT.md`'s "Troubleshooting: IBKR order placement".
- **Real paper fills now confirmed (BUY and SELL), but only very recently and only in this
  narrow path**, `get_ibkr_positions()`, `get_ibkr_account_value()`, and `place_orders_ibkr()`
  have all been exercised against a real paper (port 7497) connection, and rebalance orders on
  both portfolios were verified to actually fill (confirmed directly in TWS's own execution log,
  both BUYs and SELLs, real prices, matching quantities). Getting here took four fixes, in
  order: every order was first silently rejected (`error 10268`, an `ibapi`/TWS version
  incompatibility); then every fractional-share order was still rejected (`error 10243`, the
  platform limitation above) until whole-share flooring landed; then real fills were
  misreported as unconfirmed because `place_orders_ibkr()`'s fill-poll window (15s) was shorter
  than actual paper-fill latency (now 60s, configurable via `fill_poll_timeout`); then an
  informational per-order notice (`error 10349`, "Order TIF was set to DAY based on order
  preset") was found to be incorrectly overwriting a real, filled order's tracked status to
  `"ERROR: ..."`, making the poll loop give up watching it, confirmed against a real case where
  the order had genuinely filled in TWS despite being logged as failed. This has been confirmed
  for `--force-rebalance` runs on one paper account, a handful of times, the real-money port,
  sustained/scheduled (non-forced) operation, and behavior across many cycles are all still
  unexercised.
- **Multi-portfolio ticker leakage on a shared account is not just theoretical**, observed
  directly: portfolio2 (tickers `XLF`/`XLE`/`GLD`/`TLT`) inherited a stray `BIL` position from
  portfolio1 via `reqPositions()` (which returns every position on the shared IBKR account, not
  filtered per portfolio). The single-portfolio version of this (a ticker held from a past
  broader `tickers:` list, then removed from config while still open) is now automatically
  reconciled, priced and made eligible for exit again, with a non-blocking `ORPHANED_POSITION`
  WARNING, see `docs/RUNNING.md`'s "Restart and Resume Behavior" section. The genuinely
  cross-portfolio case (a position not confirmed by THIS portfolio's own trade log, likely
  belonging to a sibling portfolio) still correctly refuses to trade it blind, that's the safe,
  intended behavior, not an unhandled gap, now surfaced explicitly as a non-blocking
  `UNRECOGNIZED_POSITION` WARNING instead of a bare, unexplained `HOLD, no live price
  available`. This is the real-world shape of the `TICKER OVERLAP` warning every run already
  prints when portfolios share tickers; worth understanding before running multiple portfolios
  against one real account.
- **A real, confirmed cross-portfolio destructive sell (2026-07-16), now fixed**: distinct from
  the orphaned/unrecognized-ticker case above (that's about a ticker no longer in a portfolio's
  CURRENT config), this was a ticker legitimately configured in TWO portfolios sharing one real
  account at once. `get_ibkr_positions()`'s whole-account result flowed into `generate_orders()`'s
  drift math with zero per-portfolio scoping, so one portfolio's rebalance saw a SIBLING
  portfolio's legitimately-held shares of the shared ticker as its own over-allocation and sold
  them down, confirmed directly against real trade-log timestamps and share counts.
  `daily_runner.py`'s `scope_overlapping_holdings()` fixes this: for any ticker configured in
  more than one portfolio, each portfolio's view of it is capped at `min(broker-reported shares,
  that portfolio's own trade-log-derived shares)`, so a portfolio can never generate a SELL sized
  off a sibling's shares. The `TICKER OVERLAP` warning above still fires exactly as before
  (advisory visibility that two portfolios share exposure to a name), a new
  `OVERLAPPING_TICKER_SCOPED` alert fires specifically when the cap actually activates on a
  given run.
- **A real, confirmed cross-CONFIG-FILE variant of the same destructive-sell class, found during
  Epic 2's own live paper-account verification (2026-08-05), FIXED in Epic 5 ("Cross-Config
  Ticker Safety & Portfolio Snapshot Accuracy Fixes" plan, 2026-08-05)**: the same-file fix above
  (`scope_overlapping_holdings()`) only ever protected against ticker overlap BETWEEN PORTFOLIOS
  WITHIN ONE LOADED `config.yaml`, confirmed by reading `check_ticker_overlap()` directly, it only
  inspects the currently-loaded file's own `portfolios:` dict, with no way to know about a ticker
  configured in a DIFFERENT config file/process trading the same real IBKR account. Confirmed
  directly, not theoretical: a throwaway `--config <test>.yaml` used to verify the ATR-Based
  Trailing Stop feature (a single-ticker test portfolio for `NVDA`, a ticker also configured in
  this project's own real `config.yaml`'s `portfolio1`) saw the REAL, whole-account `NVDA`
  position (66 shares, from real `portfolio1` activity) as entirely its own via
  `get_ibkr_positions()`'s whole-account result, and its own small target weight drove a real
  (paper account, no financial loss) full-liquidation SELL of all 66 shares. **Fixed**: a
  persisted, cross-process `data/ticker_ownership_registry.json` registry (`daily_runner.py`'s
  `update_ticker_ownership_registry()`/`detect_cross_config_ticker_overlap()`), guarded by the
  existing `acquire_log_lock()` primitive, written atomically, read failures fail SAFE
  (conservative capping, not silent-empty). See `docs/RISK_CONSTRAINTS.md`'s "Cross-Config-File
  Ticker Ownership Registry" section for the full mechanism and its own honestly-disclosed
  residual risk: this closes the documented stale/infrequently-run-config incident class above,
  it does NOT close a true simultaneous-execution race between two config processes launched
  within the same few seconds, that remains a real, stated, open scope boundary, not a claimed
  complete fix.
- **`positions_value`/`unrealized_pnl`/`cash` in the portfolio snapshot CSV (and the email
  report's "Cash"/"Unrealized P&L" rows) double-counted a ticker legitimately shared between two
  portfolios (the TICKER_OVERLAP scenario), a real, confirmed bug distinct from the destructive-
  sell class above, purely a reporting-accuracy issue with ZERO trading-safety blast radius
  (confirmed: no circuit breaker, drawdown calc, or order sizing reads `positions_value`, and
  Total Return/CAGR/Sharpe/Sortino/Max Drawdown are all built from `portfolio_period_return`,
  derived independently from `total_value`). **Fixed in Epic 5**: `write_portfolio_snapshot()`
  gained an explicit `scoped_tickers` param, and `daily_runner.py`'s own snapshot block now
  reuses the already-existing `_compute_scoped_positions_value()` (previously used only for the
  `TOTAL_VALUE_DRIFT` warning), so both computations agree for the same run. See
  `docs/RISK_CONSTRAINTS.md`'s "Cross-Config-File Ticker Ownership Registry" section context and
  `CLAUDE.md`'s `execution/live_signal.py` bullet for the full writeup.
- **Execution Participation-Rate Limits (`use_participation_rate_limit`) has two real, honestly
  disclosed verification gaps, found during Epic 4's own live paper-account testing
  (2026-08-05), not glossed over**: (1) the actual INTRADAY percentage-of-volume fill behavior
  (whether IBKR's native `PctVol` algo genuinely paces the fill against real-time volume as
  configured) was never observed, both live test runs happened after regular trading hours, so
  the order only confirmed as ACCEPTED and correctly queued for the next session, not as filled
  under real algo pacing. (2) whether an `algoStrategy`-bearing order composes cleanly with
  `attach_broker_stop_loss`/`attach_broker_trailing_stop` brackets on the SAME parent order was
  also not exercised, only a plain, non-bracket order was tested. Two real, confirmed bugs WERE
  found and fixed getting to this point: a wrong IBKR algo-param tag name (`maxPctVol` instead
  of the actual documented `pctVol`, rejected by a real submission with IBKR error 443), and a
  genuine IBKR constraint not anticipated in advance (an algo order combined with
  `outsideRth=True` is rejected outright, IBKR error 201, "Only RTH orders are allowed for IB
  algorithmic orders"), both fixed and confirmed accepted by a real paper account afterward, see
  `docs/RISK_CONSTRAINTS.md`'s "Execution Participation-Rate Limits" section for the full
  writeup. Until exercised during a live RTH session, treat the actual fill-pacing behavior and
  bracket composition as unverified, not assumed to work.
- **`config.example.yaml` previously under-documented 20 of `BacktestConfig`'s 58 fields**, now
  closed, confirmed by enumerating the dataclass directly. The 10 LIVE-relevant ones (`exchange`,
  `correlation_lookback_days`/`correlation_penalty_strength`, `correlation_spike_short_window`/
  `correlation_spike_baseline_window`/`correlation_spike_threshold`, `max_pct_of_adv`,
  `attach_broker_stop_loss`, `multi_timeframe_lookbacks`/`multi_timeframe_weights`) and the 10
  BACKTEST-ONLY research/notebook ones (`initial_capital`, `base_slippage_bps`/
  `vol_slippage_multiplier`, `random_seed`, `monthly_contribution`, `log_file_path`, the 4
  `liquidity_stress_*` crash-protection fields) are all documented now, every `BacktestConfig`
  field has a comment in `config.example.yaml`.
- **A real, confirmed 100%-of-attempts SMTP send failure inside Docker (2026-07-19), now
  fixed**: every notification/alert/report was timing out, regardless of category or portfolio.
  Root-caused, not guessed: a raw TCP probe from inside the container showed port 587
  (STARTTLS, the previous only-supported mode) hanging the full timeout while port 465
  (implicit TLS) connected in under a second against the same host, IMAP on 993 connecting
  instantly too, ruling out a general network problem. `core/smtp_auth.py`'s `connect()` now
  supports both (`SMTP_PORT=465` picks `smtplib.SMTP_SSL`), plus a configurable
  `SMTP_TIMEOUT_SECONDS` (default `30`) and one bounded retry, shared by every SMTP call site
  in the project. See `docs/DEPLOYMENT.md`'s "Troubleshooting: SMTP timeouts".
- **A real, confirmed silent-zero-picks failure for a larger `lookback_period` (2026-07-20), now
  fixed**: the LIVE price fetch's window was hardcoded at 400 days regardless of the portfolio's
  configured `lookback_period`/`holding_period`. Reproduced directly, not guessed: the shipped
  default (`lookback_period=12`) only had a 1-monthly-bar margin under the old fixed window, and
  a monthly `lookback_period` as unremarkable as `18`, or a weekly one around `15` (60 weeks),
  produced an entirely NaN latest-row momentum score, silently resolving to ZERO picks, no
  exception, no warning, and (worse) `generate_orders()` would then SELL every currently-held
  position too, since its target universe would be empty. `execution/live_signal.py`'s
  `compute_required_lookback_days()` now sizes the fetch to what the portfolio's actual config
  needs (covering momentum ranking, the regime filter, vol targeting, and correlation checks,
  every real consumer of the fetched price history, not just ranking), wired into both real
  fetch call sites, plus a defensive `INSUFFICIENT_PRICE_HISTORY` warning for the residual edge
  case (a vendor genuinely lacking that much real history for a ticker) that sizing alone can't
  fix. LIVE-ONLY, `lookback_period` has no effect on the backtest engine.
- **Stop-loss is fixed-from-entry, not trailing (a trailing option now exists, opt-in), and
  `risk_monitor.py`'s Docker schedule is one value shared by every portfolio, now documented**:
  `stop_loss_pct` is measured from each position's entry price in both the backtest and live
  paths, confirmed by reading both, it never ratchets up as a position gains, so widening it to
  15-20% for a long-term/monthly portfolio (as literature recommends) gives room to breathe
  through normal pullbacks but does NOT lock in gains the way a genuine trailing stop would.
  `use_trailing_stop`/`trailing_stop_pct` (opt-in, `false`/`None` default byte-identical to
  before) now closes this gap: a Python-side daily high-water-mark ratchet, LIVE + BACKTEST, see
  `docs/RISK_CONSTRAINTS.md`'s "Trailing Stop-Loss". A broker-native IBKR `TRAIL` order also now
  exists (`attach_broker_trailing_stop`, opt-in, LIVE-ONLY), see the "Broker-Native Trailing
  Stop" bullet further down this list and `docs/RISK_CONSTRAINTS.md`'s section of the same name.
  Separately, Docker's
  `RISK_MONITOR_CRON` applies one schedule to every portfolio in `RISK_MONITOR_PORTFOLIOS`, so a
  container mixing a short-term portfolio (recommended: check twice daily, 10:00 AM + 3:30 PM ET)
  with a long-term one (recommended: closing-bell only, 3:45 PM ET) can't express both schedules
  via `.env` alone. Recommended widths/timings and a zero-code-change host-cron workaround for
  the scheduling gap are documented in `docs/RISK_CONSTRAINTS.md`'s "Stop-Loss Width" section and
  `docs/DEPLOYMENT.md`'s "Recommended `risk_monitor.py` timing" section.
- **A real, confirmed `NaN`-price crash in `generate_orders()`, found during Epic 1's
  ("Institutional Momentum Best-Practice Gaps" plan) real paper-account trailing-stop
  verification, now fixed**: a vendor's most recent trading-day row can be `NaN` (confirmed
  directly, not synthetic: yfinance returned a `NaN` close for XLRE's latest row, a data-lag
  case), which the price-validity guard `if price is None or price <= 0:` did not catch (`NaN`
  comparisons are always `False` in Python), silently flowing through to `int(shares)` and
  crashing with `ValueError: cannot convert float NaN to integer` on an otherwise-normal
  rebalance. Fixed with an explicit `pd.isna(price)` check; a `NaN` price now resolves to the
  same safe `"no live price available"` HOLD every other missing-price case already gets. See
  `docs/RISK_CONSTRAINTS.md`'s "Trailing Stop-Loss" for the full incident writeup.
- **A real, confirmed hash-chain race in the trade/alert/email-command logs (2026-07-21), now
  fixed**: two `daily-runner --force-rebalance` invocations run seconds apart broke a real
  trade log's tamper-evident hash chain, both read the same "last row hash" before either had
  written, producing two rows chained from the SAME predecessor rather than one after the
  other, confirmed directly via `verify_log_integrity()` flagging the exact break. All three
  hash-chained logs (trade, alert, email-command) shared this same unguarded read-then-write
  critical section. `core/audit_log.py`'s new `acquire_log_lock()`/`release_log_lock()` (a
  portable exclusive-create file lock, no new dependency) now guards all three; a regression
  test reproducing the exact race (many threads writing the same log concurrently) confirms the
  fix holds under real contention, including a real Windows-specific finding along the way
  (contended lock creation raises `PermissionError` there, not `FileExistsError` like POSIX).
- **A real, confirmed backtest/live parity gap on an explicit empty-picks period, now fixed**:
  `run_risk_managed_backtest()` used to skip its entire position-sizing/order block whenever a
  rebalance date's `target_tickers` was an explicit empty list (the whole-book negative-momentum
  cash filter, or the liquidity filter, zeroing out every pick), silently carrying the previously
  held position forward instead of selling it, unlike live's `generate_orders()`, which already
  correctly liquidates to cash in this case. Fixed: an empty `target_tickers` now flows through
  the exact same sell/buy pipeline as any other rebalance. See `docs/RISK_CONSTRAINTS.md`'s
  "Whole-Book Negative Momentum Cash Filter".
- **A separate, minor quirk found while building the fix above, now also fixed (Epic 11, "Fix
  First-Rebalance-Date Collision" plan)**: the very FIRST signal date in any `monthly_picks`
  series could have its computed rebalance date collide with `run_risk_managed_backtest()`'s own
  simulation-window start date, which the day-loop then silently excluded, so the first rebalance
  in a short/synthetic `monthly_picks` series could silently never fire, depending on exact
  calendar alignment (confirmed reproducible, depended on weekend/NYSE-holiday placement relative
  to that first signal's month boundary). Real, multi-year `monthly_picks` series (this project's
  own actual usage) never surfaced this, losing only the very first of many rebalances doesn't
  visibly affect a long backtest, which is presumably why it went uncaught for a while. Fixed by
  widening the day-loop to process every day in the simulation window (previously skipped the
  first one unconditionally); confirmed safe for the common case via `_build_report()`'s
  pre-existing exact-duplicate-date dedup. See `CLAUDE.md`'s `backtest/momentum_backtest.py`
  bullet for the full mechanism.
- **A real, confirmed crash in the daily/monthly report's window-comparison stats, now fixed**:
  `notifications.send_daily` had never been turned on against real accumulated deployment
  history before (confirmed, first time this session), crashing with `TypeError: float()
  argument must be a string or a real number, not 'Series'`. `write_portfolio_snapshot()` writes
  one row per RUN, not per calendar day, so more than one manual run on the same day (routine
  during testing) produces multiple `portfolio_snapshot_<name>.csv` rows sharing a date
  (confirmed directly: one real file had 36 rows for a single date). `daily_window_comparison()`/
  `monthly_window_comparison()` (`core/functions_quant_extensions.py`) both index by date and do
  a scalar lookup for the latest value, which breaks on a duplicate date. Fixed by keeping only
  the most recent same-day row before that lookup in both functions; deliberately NOT applied to
  the two sibling functions in the same file that aggregate every row via a cumulative product
  instead, doing so there would have silently discarded real return data (caught by an existing
  test before it shipped). See `CLAUDE.md`'s `daily_runner.py` bullet for the full detail.
- **A real, confirmed, ongoing Yahoo Finance data-quality gap, found while investigating a
  `$nan` "Current Close Price" in a real portfolio's Full Signal Universe report, now given a
  reporting-only fallback**: confirmed directly (not guessed), `yf.download()` currently returns
  `NaN` OHLC for the most recent trading day across multiple/most tickers at once (AMD, ASML,
  SPY, and MSFT all affected simultaneously when checked), an external vendor issue, not a bug in
  this codebase and not a regression from any prior epic. Momentum SCORES stay valid despite this
  (the monthly-resample step's `.last()` already skips the trailing `NaN` day and uses the last
  real value), but the raw `close_price` DISPLAY did not, rendering a bare `"$nan"` with no
  indication anything was wrong. `execution/live_signal.py`'s `full_signal_universe` now falls
  back to the last known-good close for DISPLAY purposes only, with a `close_price_as_of` date so
  the staleness is explicit, not silently hidden; the real trading-decision path
  (`latest_prices`, `generate_orders()`, the daily stop-loss check) is completely unaffected by
  this fallback, still sees the genuine `NaN` and still correctly holds/skips exactly as before.
  See `docs/SIGNAL_RANKINGS_LOG.md`'s `close_price_as_of` documentation and `CLAUDE.md`'s
  `execution/live_signal.py` bullet.
- **Live price-vendor priority, a deliberate, informed reversal, not an oversight, plus a
  second real bug found and fixed via its own real-key production verification**: the
  momentum-ranking/reporting price feed (`fetch_live_prices()`) previously always fell through to
  `yfinance` regardless of whether `FMP_API_KEY`/`EODHD_API_KEY` were configured, confirmed by
  reading every real `daily_runner.py` call site, none of them ever passed real keys in.
  `daily_runner.py`'s three `fetch_live_prices()`/`run()` call sites now read
  `FMP_API_KEY`/`EODHD_API_KEY` from the environment and pass them through, closing that gap.
  Testing this against the REAL `.env` keys surfaced a genuine, previously-invisible bug in
  `core/functions.py`'s `get_bulk_prices()` (invisible only because no real call site had ever
  passed real FMP/EODHD keys through before this epic): the vendor is auto-detected from ONE
  ticker only, but a real key can fail for a SUBSET of tickers under that same vendor even after
  the first one succeeded, confirmed directly: the real FMP key returned `402 Payment Required`
  for several symbols (a plan-tier limitation) while succeeding for others in the exact same
  batch. The old per-ticker loop had NO fallback for an individual ticker's failure, silently
  dropping it from the result entirely; with enough tickers dropped, `daily_prices` no longer
  covered every configured ticker, crashing with a `KeyError` several frames away, confirmed via
  a real `daily-runner --force-rebalance` crash against production `config.yaml`. Fixed: each
  ticker's fetch now cascades through the remaining vendors in priority order before giving up
  on that specific ticker (only when the vendor was auto-detected, an explicit single-vendor
  request is unaffected), plus a related column-naming bug (the adjusted-close column name is
  vendor-specific but was computed once for the whole batch, now resolved per ticker from
  whichever vendor actually answered for it). Scoped to `fetch_live_prices()` only;
  `fetch_ohlcv_for_tickers()` (technical indicators, liquidity filter, technical-confirmation
  volume) is untouched, still `yfinance`-only from every `daily_runner.py` call site, a
  documented, deliberate scope boundary, not an oversight. See `CLAUDE.md`'s `daily_runner.py`
  bullet.
- **"Stop-Loss Price" reporting formula, a deliberate, informed reversal, not a bug fix**: this
  column (the Full Signal Universe table/log) previously reported a dollar-amount-at-risk figure
  (`Money Invest * stop_loss_pct`), a documented, deliberate design choice at the time. It now
  reports a real per-share trigger price instead (`close_price * (1 - stop_loss_pct)` for a
  `BUY`, `avg_entry_price * (1 - stop_loss_pct)` for a `HOLD` when a real entry price is known,
  falling back to `close_price` otherwise), on a new, explicit instruction, matching what the
  two real stop-loss enforcement mechanisms (the daily drawdown check and the broker-side
  bracket order) already independently compute. Reporting-only, still not wired into either real
  mechanism. See `docs/SIGNAL_RANKINGS_LOG.md`'s `stop_loss_price` entry and `CLAUDE.md`'s
  `execution/live_signal.py` bullet.
- **A real, confirmed IBKR platform constraint found via the broker-native trailing stop's
  (`attach_broker_trailing_stop`) own real paper-account verification, now fixed**: a `TRAIL`
  child order attached to a plain `MKT` parent (the same shape the existing `attach_broker_
  stop_loss` STP bracket already uses successfully) failed with IBKR error 328, "Trailing stop
  orders can be attached to limit or stop-limit orders only." Unlike the STP child, a `TRAIL`
  child specifically requires its parent to be `LMT` or `STP LMT`. Fixed: the parent is now
  forced to `LMT` whenever a TRAIL child will attach, using the same buffer-based limit price
  computation `allow_extended_hours` already uses elsewhere in this function. Confirmed
  end-to-end against a real IBKR paper account after the fix: a real BUY + TRAIL bracket
  attached successfully, and (when combined with `attach_broker_stop_loss`) both children
  attached as a real IBKR One-Cancels-All (OCA) pair. See `docs/RISK_CONSTRAINTS.md`'s
  "Broker-Native Trailing Stop" section.
- **A real, confirmed data bug found via the live-vs-backtest reconciliation notebook's own
  real-data run (2026-08-03), now fixed**: `core/functions.py`'s `_fetch_yf()` passed `end_date`
  (computed as literally "today" by every real caller, e.g. `fetch_live_prices()`) straight into
  `yf.download(end=...)`. Confirmed directly against a real yfinance call that yfinance's own
  `end` parameter is EXCLUSIVE (`end="2026-08-03"` never returns `2026-08-03`'s own row), unlike
  FMP's/EODHD's `to` REST params in the same function, both confirmed inclusive. This meant the
  yfinance vendor path silently NEVER included today's own close, even fetched well after market
  close, for as long as this project has existed, affecting every real caller that falls back to
  (or exclusively uses) yfinance: `daily_runner.py`'s live rebalance signal, stop-loss checks,
  and portfolio snapshots. Fixed: `_fetch_yf()` now requests `end_date + 1 day`, making the
  yfinance call effectively inclusive, matching FMP/EODHD. See `tests/core/test_functions.py`'s
  `TestFetchYfEndDateInclusive`.
- **The reconciliation notebook's methodology bugs are fixed, but a real head-to-head number is
  still blocked, by data recency, not a code defect**: fixing the yfinance bug above resolved
  the reconciliation's initial "no trading days found" failure for `portfolio1`/`portfolio2`
  (their most recent real signal date's price data now exists), but `run_custom_backtest()`'s
  own `_build_report()` still returned an empty DataFrame for all three portfolios, traced
  directly (not assumed) to `report["Portfolio Monthly Return"] = report["Month End Portfolio
  Value"].pct_change()` immediately followed by `report.dropna(subset=["Portfolio Monthly
  Return"])`: a `pct_change()` on a single month-end bucket is always `NaN` (nothing to diff
  against), so with only one calendar month of simulated history (all real trading here started
  within the last ~2 weeks, entirely inside the still-open month at the time), the sole row gets
  dropped, leaving nothing to report. This is a deliberate, load-bearing convention (every
  CAGR/vol/Sharpe/Sortino/Calmar figure in this report needs month-over-month returns), not
  something Epic 12 changed or should change, it just makes this specific reconciliation
  technique premature until real trading has survived at least one full month-end transition.
  The notebook itself is fixed and ready (config loaded from the real `config.yaml`, `dry_run`
  correctly filtered, signal reproduced via the same `strategy_type`-aware
  `generate_strategy_monthly_picks()` both live and backtest already share, `custom_weights`
  sizing parity for `portfolio1`), and real Live P&L was computed successfully for all three
  portfolios from their actual trade logs; only the Backtest side of the comparison is waiting
  on real calendar time to pass.
- **Real historical crash-period stress test (2008 GFC / 2020 COVID / 2022 Bear), Epic 13**: the
  currently-configured tickers can't be used for this directly, confirmed by checking IPO dates,
  not assumed: `portfolio1` includes `ARM` (IPO 2023) and `PLTR` (IPO 2020), `portfolio3`
  includes `ASTS`/`CPA`/`SWMR` (all recent), none of which existed in 2008 and several didn't
  exist in 2020. Instead, `notebooks/research/crash_period_stress_test.ipynb` uses a long-history,
  liquid ETF proxy universe (17 tickers, confirmed via a real `yfinance` check to have data back
  to 2005: `SPY, QQQ, DIA, XLK, XLF, XLE, XLI, XLP, XLU, XLV, XLY, GLD, TLT, IEF, SHY, LQD, IWM`)
  with this project's two REAL risk regimes (`portfolio1`'s actual monthly `default_risk`,
  `portfolio2`'s actual weekly `risk_overrides`, both loaded from `config.yaml` via
  `daily_runner.load_config()`, not hand-typed), each run twice per crash period: once "as
  configured" (regime filter, volatility targeting, and stop-loss all on, plus a representative
  `max_portfolio_drawdown_pct: 0.20` circuit breaker, since the real `config.yaml` ships that
  disabled by default) and once as a naive-momentum "baseline" with every defensive mechanism
  neutralized. This validates the risk-control *mechanism*, not a claim about what the exact
  current portfolios would have returned in 2008.

  **Real results** (18 backtests: 2 regimes x 3 variants x 3 crash periods, run 2026-08-04).
  **Superseded once, honestly**: the numbers below replace an earlier version of this table,
  corrected after Epic 14's own real-data verification found and fixed two real bugs in
  `run_risk_managed_backtest()` (the regime/vol precompute was silently starved of history in
  short-window tests, see the `momentum_crash_lookback_days` bullet below) that also changed the
  "full" variant's own numbers, not just the new third variant's, confirmed by rerunning this
  exact comparison before and after the fix. Publishing corrected numbers rather than leaving the
  original ones stand, per this project's own documentation standards.

  | Period | Regime | Baseline max DD | Full max DD | Full+MC max DD | Baseline return | Full return | Full+MC return | SPY buy-hold |
  |---|---|---|---|---|---|---|---|---|
  | 2008 GFC | monthly | -10.0% | -1.7% | -1.6% | -3.6% | -2.1% | -3.0% | -37.9% |
  | 2008 GFC | weekly | **-26.0%** | -11.5% | -10.1% | -14.8% | -10.9% | -11.2% | -37.9% |
  | 2020 COVID | monthly | -6.4% | -5.3% | -5.3% | +18.3% | +12.2% | +11.1% | +17.2% |
  | 2020 COVID | weekly | -9.5% | -9.2% | -9.2% | +14.8% | +7.6% | +7.2% | +17.2% |
  | 2022 Bear | monthly | -12.0% | -10.0% | -9.5% | -3.1% | -11.7% | -10.0% | -18.7% |
  | 2022 Bear | weekly | -10.7% | -7.6% | -7.6% | -4.1% | -5.5% | -7.2% | -18.7% |

  ("Full+MC" = `full` plus `momentum_crash_lookback_days=504`/`derate=0.5`, Epic 14, see that
  bullet below; also turns on `regime_vol_threshold=0.25` as a prerequisite, so this specific
  3-way table can't fully isolate momentum-crash-protection's own marginal effect in isolation,
  see that bullet's own deterministic unit tests for the clean, isolated proof.)

  Honest reading, not oversold: `full` beats `baseline` on max drawdown in all 6 regime/period
  combinations, most dramatically in 2008 (weekly: -11.5% vs. -26.0%). But it's not a clean win
  across the board the way the drawdown numbers alone suggest: in 2020 COVID (fast, V-shaped
  recovery), `full`'s total return is materially *lower* than baseline's for both regimes, the
  same defensive de-risking that helps in a slow bear market misses part of a sharp rebound. In
  **2022 Bear's monthly regime specifically**, `full` is now WORSE than baseline on BOTH
  drawdown and return (-10.0%/-11.7% vs. -12.0%/-3.1%), a real, honest result that only emerged
  after the bugfix above, not something to paper over. The circuit breaker
  (`max_portfolio_drawdown_pct: 0.20`) never tripped in any run, not a bug, the regime filter +
  volatility targeting combination alone kept every real-crash drawdown well inside that
  threshold. Recovery-time comparison (`core/functions_quant_extensions.py`'s new
  `compute_drawdown_episodes()`, added for Epic 13) was mostly inconclusive within these short
  (9-21 month) windows, most episodes hadn't fully recovered to a new high before the window
  ended, not enough data points to draw a real recovery-time conclusion yet.

- **Momentum-crash-specific dynamic scaling, Epic 14 (Daniel & Moskowitz 2016 "Momentum
  Crashes")**: `momentum_crash_lookback_days`/`momentum_crash_derate`, an ADDITIONAL
  multiplicative derate stacked on top of the existing regime/vol scalars, specifically for the
  joint "sustained prior downturn AND currently volatile" regime DM identify as momentum's real
  crash risk, distinct from (and not redundant with, a design trap found and avoided while
  planning this) the existing `regime_vol_threshold`'s OR-based high-vol check. See
  `docs/RISK_CONSTRAINTS.md`'s "Momentum-Crash-Specific Dynamic Scaling" for the full mechanism,
  the two real gaps found and fixed while validating it against real historical data
  (`compute_required_lookback_days()` didn't cover this field's own long lookback need; the
  backtest engine's regime/vol precompute silently used the already-window-masked price panel
  instead of the caller's full history), and a real paper-account regression test (2026-08-04,
  `portfolio2`, port 7497) confirming correct order generation with these fields active, which
  also surfaced a new, previously-uncatalogued IBKR informational code (`2109`) now added to
  `IBKR_INFORMATIONAL_CODES`. Real validation result: fired 9/39/1/2 times across the four
  2008/2020 monthly/weekly scenarios (0 times in 2022's slower decline), modestly improving max
  drawdown at a modest cost to return when it fired, an honest, mixed result, not a clean win,
  left disabled by default in both `docs/RISK_CONSTRAINTS.md` presets for that reason.
- **Forward-looking / parametric stress testing, Epic 7**: `crash_period_stress_test.ipynb`
  above only replays REAL 2008/2020/2022 windows, it can't answer "what if rates rise 100bps and
  equities fall 20% simultaneously," a combination that may never have literally happened in the
  fetchable historical record. `notebooks/research/parametric_stress_test.ipynb` (new) fits real
  betas of each real regime's own strategy returns (`factor_decomposition()`, existed before this
  epic, notebook-only, zero production callers, the same "scaffold exists, never wired in"
  pattern this project has closed before) against 4 real factor proxies already in the cached
  universe (`SPY`/`TLT`/`GLD`/`XLE`), then runs hypothetical shocks through those betas
  (`estimate_factor_shock_impact()`, new). **Real results, run 2026-08-08**: monthly regime
  (`portfolio1`) fitted alpha_annualized 0.40% (r_squared 0.42, betas `SPY=0.385, TLT=0.082,
  GLD=0.071, XLE=0.003`); weekly regime (`portfolio2`) fitted alpha_annualized -0.64% (r_squared
  0.45, betas `SPY=0.344, TLT=0.064, GLD=0.048, XLE=-0.039`). Against a representative $100,000
  portfolio: a "2008-style tail risk" shock (SPY -40%, TLT +20%) estimates -13.36%/-$13,356
  (monthly) and -13.09%/-$13,091 (weekly); a "simultaneous rate + equity shock" (SPY -10%, TLT
  -15%) estimates -4.68%/-$4,681 (monthly) and -5.04%/-$5,038 (weekly); a "stagflation shock"
  (SPY -15%, GLD +25%, TLT -10%, XLE +20%) estimates -4.36%/-$4,357 (monthly) and
  -6.02%/-$6,025 (weekly). **Honest methodological caveat, stated plainly**: betas are fit from
  MONTHLY returns, applying them to an instantaneous shock is a real simplification, and
  momentum's own documented crash nonlinearity (the `momentum_crash_lookback_days` bullet above)
  means this linear approach likely UNDERSTATES real tail risk, it complements, not replaces,
  the historical replay above.
- **Capacity / AUM scaling analysis, Epic 7**: there's a per-trade ADV cap (`max_pct_of_adv`,
  advisory) but there was no "at what AUM does this strategy's own sizing start running into that
  cap" curve, standard due-diligence material for an institutional allocator.
  `notebooks/research/capacity_aum_analysis.ipynb` (new) builds that curve using only existing,
  unmodified functions (`generate_strategy_monthly_picks()`, `resolve_target_weights()`,
  `check_capacity()`), at `gross_exposure = 1.0` (a deliberate, disclosed "worst case / fully
  invested" simplification, capacity constraints bind hardest exactly when fully invested).
  **A real, confirmed methodological finding while building this, not a code bug**: both real
  portfolios' shipped `default_risk` set `max_pct_of_adv: 0.0` ("disabled"), and under
  `check_capacity()`'s own literal `pct_of_adv > max_pct_of_adv` comparison, an exact `0.0`
  threshold flags nearly every nonzero position regardless of AUM, a meaningless, constant
  capacity curve; fixed by using an illustrative `CAPACITY_MAX_PCT_OF_ADV = 0.05` (5%,
  `check_capacity()`'s own docstring's "conservative retail-scale default") for this analysis
  only, matching the SAME "real config ships a mechanism off by default, illustrate the
  mechanism with a representative value" precedent `crash_period_stress_test.ipynb` already
  established. **Real results, run 2026-08-08**, 5 AUM levels ($10K/$100K/$1M/$10M/$100M) against
  the real cached 17-ticker proxy universe and real historical volume (fetched once, cached to
  `crash_test_daily_volume.pkl`): monthly regime (`portfolio1`) shows 0% of (date, ticker)
  observations flagged at $10K/$100K/$1M, rising to 4.27% at $10M and 25.89% at $100M; weekly
  regime (`portfolio2`) shows 0% at $10K/$100K, 0.02% at $1M, rising to 4.32% at $10M and 20.75%
  at $100M. A real, sensible, monotonically increasing capacity curve, both regimes start binding
  meaningfully somewhere between $1M-$10M on this large-cap/broad-ETF proxy universe, still under
  a quarter of observations flagged even at $100M given how liquid this particular universe is.
- **Real out-of-sample walk-forward + pre-registered holdout validation, Epic 15**: the same
  "scaffold exists, never executed" pattern as Epic 12/13: `core/functions_quant_extensions.py`
  already had `pre_registered_split()`/`walk_forward_lookback_holding()`/`bootstrap_sharpe_ci()`,
  fully coded and wired into `notebooks/research/DHI0016_notebook1_research_and_EDA_
  IMPROVED.ipynb`'s cells 49-57, but never actually run against real data. A real design gap was
  found in that scaffold before running it: its `_quick_backtest()` helper was a simplified
  mean-monthly-return approximation (no regime filter, no volatility targeting, no stop-loss, no
  slippage/commission), and it reimplemented picks selection without `.dropna()` before
  `.nsmallest()`, the exact real bug `get_top_etfs()`'s own docstring documents and fixes
  elsewhere in this codebase. `notebooks/research/out_of_sample_validation.ipynb` (new) instead
  uses a new `run_walk_forward_lookback_search()` (`core/functions_quant_extensions.py`), which
  wires the walk-forward search through the REAL `generate_strategy_monthly_picks()` +
  `run_custom_backtest()` pipeline, `portfolio1`'s real config, on Epic 13's already-cached
  17-ticker long-history proxy universe (no new fetch), same documented ticker-availability
  scope boundary as Epic 13/14 (most of `portfolio1`'s real tickers didn't exist in 2005).

  **Real results** (run 2026-08-04): pre-registered split at `2015-01-01` (`train` 2005-2014,
  `holdout` 2015-2026, committed to before any tuning). Walk-forward search across 5 real,
  independent folds within `train` (`lookback_candidates=[6,9,12,15,18]`):

  | Fold (train → test) | Chosen lookback | Train Sharpe | Test Sharpe | Test CAGR |
  |---|---|---|---|---|
  | 2005-2009 → 2009-2010 | 9 | 1.14 | 1.58 | 12.2% |
  | 2006-2010 → 2010-2011 | 9 | 0.86 | 0.51 | 6.8% |
  | 2007-2011 → 2011-2012 | 12 | 0.82 | 0.03 | -0.0% |
  | 2008-2012 → 2012-2013 | 12 | 0.70 | 0.41 | 1.9% |
  | 2009-2013 → 2013-2014 | 12 | 0.67 | 2.21 | 23.5% |

  Mean train Sharpe 0.84, mean test Sharpe **0.95**, test *not* degraded relative to train (the
  overfitting signature the methodology explicitly warns about never showed up, if anything the
  reverse), and the walk-forward search independently converged on `lookback_period=12` (3 of 5
  folds) — the exact value `portfolio1` already ships with, not picked in advance to match.

  The single, pre-registered `holdout` evaluation (2015-01-02 to 2026-08-04, reported exactly
  once, `lookback_period=12`): CAGR 3.49%, Annualized Vol 10.26%, **Sharpe 0.39**, Sortino 0.50,
  Max Drawdown -20.08%, Win Rate 60.1%, Beta vs. SPY 0.47, **Annualized Alpha -2.63%**.
  Block-bootstrap 90% confidence interval on the holdout Sharpe: **[-0.11, 0.95]** (90% of
  resamples positive, but the interval itself includes zero).

  Honest reading, not oversold: this is genuinely mixed, not a clean answer either way. The
  walk-forward evidence is real and positive — the shipped parameter is independently robust
  across historical folds, not overfit to one lucky sample. But the pre-registered holdout's
  **negative alpha** means the strategy's real-world outperformance over 2015-2026 is not
  clearly distinguishable from its ~0.47 market-beta exposure alone, and the bootstrap CI
  spanning zero means a real, non-zero edge cannot be confidently claimed at 90% confidence from
  this one holdout window. This is the project's first genuine out-of-sample evidence on this
  question, not a final verdict, and it argues for caution, not confidence, before allocating
  real capital.

- **Real out-of-sample walk-forward + pre-registered holdout validation, short-term (weekly)
  regime, Epic 16**: Epic 15 above only validated `portfolio1`'s monthly regime; `docs/
  STRATEGY_THEORY.md` still flagged short-term/weekly momentum as untested by this project's own
  walk-forward tooling, a real, live gap since `portfolio2` (58 tickers) and `portfolio3` (11
  tickers) both run this exact weekly regime (`holding_period: 0.25`, `lookback_period: 1.0`)
  today. Reuses `run_walk_forward_lookback_search()` (Epic 15) unchanged, since
  `backtest/momentum_backtest.py`'s `_build_report()` always resamples to month-end for
  reporting regardless of `holding_period`, confirmed by reading it before writing the plan, not
  guessed, so the reported Sharpe/CAGR/monthly-return series and its `sqrt(12)` annualization are
  valid unchanged for a weekly-rebalanced equity curve. `portfolio2`'s real weekly config
  (`use_correlation_penalty=True`, plus `default_risk`'s `top_n=10`, `stop_loss_pct=0.12`,
  regime filter, vol targeting) applied to the same cached 17-ticker long-history proxy universe
  as Epic 13/14/15, same documented scope boundary. `lookback_candidates` in week-quarter units
  (`0.5`/`0.75`/`1.0`/`1.5`/`2.0` -> 2/3/4/6/8 weeks via the existing `round(x * 4)` formula),
  same `pre_registered_split(split_date="2015-01-01")` as Epic 15 for direct comparability. A
  real test gap was found and closed before running this: `TestRunWalkForwardLookbackSearch`
  only exercised `holding_period=1` (monthly), the weekly/`round(x*4)` branch through
  `run_walk_forward_lookback_search()` had zero test coverage before this epic.

  **Real results** (run 2026-08-04), same 5-fold structure as Epic 15's monthly search:

  | Fold (train -> test) | Chosen lookback (wks) | Train Sharpe | Test Sharpe | Test CAGR |
  |---|---|---|---|---|
  | 2005-2009 -> 2009-2010 | 6 | 0.30 | 1.61 | 11.7% |
  | 2006-2010 -> 2010-2011 | 8 | 0.60 | 2.34 | 17.7% |
  | 2007-2011 -> 2011-2012 | 8 | 0.74 | -0.15 | -1.4% |
  | 2008-2012 -> 2012-2013 | 8 | 0.86 | 0.91 | 5.6% |
  | 2009-2013 -> 2013-2014 | 8 | 1.27 | 1.98 | 16.0% |

  Mean train Sharpe 0.76, mean test Sharpe **1.34**, test again *not* degraded relative to train
  (the same non-overfitting signature Epic 15 found for the monthly regime). **A real, honest
  divergence from Epic 15's monthly result, though**: the walk-forward search converged to an
  8-week lookback (4 of 5 folds), *longer* than `portfolio2`'s shipped `lookback_period: 1.0`
  (4 weeks), not toward it, the opposite of the monthly regime's own result, which converged
  toward its shipped default. Not evidence the shipped weekly default is wrong, a single
  proxy-universe walk-forward search isn't grounds to change a live config, but a real,
  worth-noting data point, not glossed over.

  The single, pre-registered `holdout` evaluation (2015-01-02 to 2026-08-04, reported exactly
  once, `lookback_period=2.0` i.e. 8 weeks): CAGR 3.72%, Annualized Vol 7.49%, **Sharpe 0.53**,
  Sortino 0.77, Max Drawdown -16.66%, Win Rate 59.4%, Beta vs. SPY 0.33, **Annualized Alpha
  -0.70%**. Block-bootstrap 90% confidence interval on the holdout Sharpe: **[0.08, 1.05]**
  (97.2% of resamples positive, the interval itself does NOT include zero).

  Honest reading, not oversold: directionally similar to Epic 15's monthly result (walk-forward
  robust, holdout alpha slightly negative), but statistically stronger on ONE dimension, the
  weekly regime's bootstrap CI is entirely positive, unlike the monthly regime's, which spanned
  zero. That's a real, non-zero risk-adjusted return (Sharpe) with reasonable confidence at 90%,
  even though the small negative alpha means most of that return still traces to market-beta
  exposure (0.33 beta) rather than a clearly momentum-specific edge. Same proxy-universe scope
  caveat as every prior crash/validation epic: this is `portfolio2`'s real risk regime applied to
  a 17-ticker long-history universe, not its exact 58-ticker live universe. Not a final verdict,
  argues for the same caution as the monthly result before allocating real capital.

- **Real out-of-sample validation for the other selectable momentum strategies, Epic 17**: Epic
  15/16 only validated `strategy_type: momentum` (monthly and weekly regimes). `docs/
  MOMENTUM_STRATEGIES.md` documents 11 selectable strategies total; the other 9 had never been
  run against real out-of-sample data. Of those, `relative_momentum` (documented alias for
  `momentum`, byte-identical) and `volatility_scaled_momentum` (preset is `sizing_method:
  inverse_vol`, already `portfolio1`'s own default) need no separate run, and `hybrid_multi_factor`
  cannot be backtested at all (`generate_strategy_monthly_picks()` raises `NotImplementedError`,
  no point-in-time fundamentals source exists). That leaves 6 real variants for a full walk-forward
  + pre-registered holdout run (`dual_momentum`, `correlation_weighted_momentum`,
  `rank_sign_momentum`, `absolute_momentum`, `residual_momentum`, `path_dependent_momentum`) plus
  `multi_timeframe_composite`, handled separately: its own scoring function never reads
  `lookback_period` at all (uses `cfg.multi_timeframe_lookbacks` instead), so a lookback grid
  search would be a meaningless no-op for it, it gets a single pre-registered holdout evaluation
  instead. Monthly regime only, `portfolio1`'s config, same cached 17-ticker proxy universe as
  Epic 13-16, `SHY` substituted for the default `defensive_ticker` (`"BIL"`, not in the cached
  panel) for `dual_momentum`/`absolute_momentum`.

  **A real methodological bug found and fixed while building this, a test-harness issue, not a
  production code bug**: building each variant's `BacktestConfig` from
  `dataclasses.asdict(portfolio1_cfg)` (every field materialized, including ones at their default
  value) silently defeats `apply_strategy_type_preset()`'s "only fill in fields the user hasn't
  already set" contract, since a fully materialized dict can't distinguish "explicitly set" from
  "happens to equal the default". Confirmed directly: the first run produced BYTE-IDENTICAL
  results for `dual_momentum`/`correlation_weighted_momentum`/`rank_sign_momentum` vs. plain
  `momentum`, traced to `portfolio1`'s own `default_risk` already explicitly pinning every field
  these 3 presets would otherwise set. **This is real, confirmed live-config behavior too, not
  just a test artifact**: selecting one of these 3 `strategy_type` values on a portfolio relying
  on the shipped `default_risk` block AS-IS has zero effect vs. plain `momentum` unless that
  portfolio's own `risk_overrides` ALSO explicitly re-overrides the differing field (`portfolio2`
  does this correctly for `use_correlation_penalty`). Fixed for this validation by setting each
  preset's own field value directly; see `docs/MOMENTUM_STRATEGIES.md`'s updated "How presets
  compose" section for the full writeup and the live-config implication.

  **Real results** (run 2026-08-05), 5-fold walk-forward within `train` for the 6 full-search
  variants, `lookback_candidates=[6, 9, 12, 15, 18]` months, same `pre_registered_split(
  split_date="2015-01-01")` as Epic 15:

  | `strategy_type` | Chosen lookback | Mean train Sharpe | Mean test Sharpe | Holdout Sharpe | Holdout CAGR | Holdout Alpha | 90% Bootstrap CI |
  |---|---|---|---|---|---|---|---|
  | `dual_momentum` | 12mo | 0.84 | 0.95 | 0.39 | 3.49% | -2.63% | [-0.11, 0.95] |
  | `correlation_weighted_momentum` | 12mo | 0.85 | 1.02 | 0.38 | 3.41% | -2.48% | [-0.11, 0.96] |
  | `rank_sign_momentum` | 12mo | 0.83 | 0.93 | 0.40 | 3.71% | -2.70% | [-0.10, 0.98] |
  | `absolute_momentum` | 12mo | 1.31 | 1.24 | 0.30 | 1.79% | -2.55% | [-0.20, 0.87] |
  | `residual_momentum` | 12mo | 1.22 | 1.25 | **0.46** | 3.55% | **-0.17%** | **[0.08, 0.96]** |
  | `path_dependent_momentum` | 9mo | 0.84 | 0.86 | 0.37 | 3.24% | -2.75% | [-0.13, 0.97] |
  | `multi_timeframe_composite` (holdout-only, no search) | n/a | n/a | n/a | 0.55 | 5.21% | -0.92% | [0.07, 1.10] |

  Honest reading, not oversold: `dual_momentum`'s backtest results are byte-identical to plain
  `momentum` (`use_absolute_momentum` is documented LIVE-ONLY, no backtest effect, and
  `use_regime_filter` was already on in `portfolio1`'s config, nothing left to differ at the
  backtest level, this is correct/expected, not a bug). `correlation_weighted_momentum`,
  `rank_sign_momentum`, and `path_dependent_momentum` all cluster close to plain `momentum`'s own
  already-published result (walk-forward robust, small negative holdout alpha, bootstrap CI
  spanning zero). `absolute_momentum` shows the strongest walk-forward Sharpe of the base-score
  types but the weakest holdout CAGR and widest, most-negative CI, a real, honest divergence
  between train/test robustness and the single holdout outcome. **`residual_momentum` produced
  the strongest result of any out-of-sample run in this project so far**: holdout Sharpe 0.46,
  alpha nearly zero (-0.17%, the closest to zero of any variant tested), and a bootstrap CI
  entirely above zero, a genuinely more confident positive signal than plain `momentum`'s own
  result. `multi_timeframe_composite`'s holdout (Sharpe 0.55, CI entirely positive) is the
  second-strongest number here, but rests on weaker evidence than the others, a single holdout
  only, no walk-forward robustness check applies to it. None of this changes the shipped
  `strategy_type: momentum` default; it's real, additional evidence for anyone considering one of
  these alternatives, not a recommendation to switch. Same proxy-universe scope caveat as every
  prior validation epic. **Weekly-regime coverage for these 6 strategies, previously flagged
  here as a separate, un-closed gap, is now closed, see Epic 18 below.**

- **Real out-of-sample validation for the other selectable momentum strategies, weekly regime,
  Epic 18**: closes the gap Epic 17 above explicitly flagged, mirroring Epic 16's own
  monthly-to-weekly extension of Epic 15, applied here to Epic 17 instead. Same 6 full-search
  variants + `multi_timeframe_composite` holdout-only, `portfolio2`'s real weekly config
  (`holding_period: 0.25`), week-quarter `lookback_candidates` (`0.5`/`0.75`/`1.0`/`1.5`/`2.0` ->
  2/3/4/6/8 weeks), same cached proxy universe, same `SHY` defensive-ticker substitution. Two
  real mechanical facts confirmed by reading the code directly before running anything: (1)
  `resolve_path_dependent_momentum_scores()` already correctly branches on `holding_period < 1`,
  no special handling needed; (2) `multi_timeframe_composite`'s scoring ALWAYS resamples to
  monthly regardless of `holding_period`, so this variant's weekly-regime run tests "a
  monthly-timeframe-blended signal, rebalanced weekly," not a weekly signal, a real, distinct
  scenario from Epic 17's monthly-rebalance version. **A real no-op case anticipated in advance,
  not stumbled into**: `portfolio2`'s own `risk_overrides` already sets `use_correlation_penalty:
  true` directly, so `correlation_weighted_momentum`'s preset has zero effect vs. `portfolio2`'s
  own already-published Epic 16 weekly `momentum` baseline, confirmed by the real run (`dual_
  momentum` and `correlation_weighted_momentum` both came back byte-identical to each other AND
  to Epic 16's own baseline).

  **Real results** (run 2026-08-05), 5-fold walk-forward within `train`, `lookback_candidates=
  [0.5, 0.75, 1.0, 1.5, 2.0]` week-quarters, same `pre_registered_split(split_date="2015-01-01")`:

  | `strategy_type` | Chosen lookback (wks) | Mean train Sharpe | Mean test Sharpe | Holdout Sharpe | Holdout CAGR | Holdout Alpha | 90% Bootstrap CI |
  |---|---|---|---|---|---|---|---|
  | `dual_momentum` | 8 | 0.76 | 1.34 | 0.52 | 3.71% | -0.72% | [0.08, 1.04] |
  | `correlation_weighted_momentum` | 8 | 0.76 | 1.34 | 0.52 | 3.71% | -0.72% | [0.08, 1.04] |
  | `rank_sign_momentum` | 8 | 0.72 | 1.39 | **0.63** | **5.27%** | -0.50% | [0.19, 1.13] |
  | `absolute_momentum` | 3 | 0.96 | 1.14 | 0.29 | 1.93% | -1.76% | [-0.16, 0.75] |
  | `residual_momentum` | 8 | 1.08 | 1.34 | 0.59 | 3.28% | **-0.09%** | [0.12, 1.14] |
  | `path_dependent_momentum` | 6 | 0.81 | 0.98 | 0.41 | 2.85% | -1.73% | [-0.06, 0.91] |
  | `multi_timeframe_composite` (holdout-only) | n/a | n/a | n/a | 0.61 | 5.07% | -0.63% | [0.11, 1.15] |

  Honest reading, not oversold: `dual_momentum` and `correlation_weighted_momentum` are both
  byte-identical to Epic 16's own weekly `momentum` baseline, the anticipated no-op, correct and
  expected, not a bug. `rank_sign_momentum` (equal-weight sizing) produced the best full-search
  holdout Sharpe (0.63) and CAGR (5.27%) of the batch, with a solidly positive CI.
  `residual_momentum` again shows the closest-to-zero alpha (-0.09%) of any variant tested across
  Epic 15-18 combined, consistent with its monthly-regime result (Epic 17), a genuinely repeated
  pattern, not a one-off. `absolute_momentum` and `path_dependent_momentum` are the weakest of
  the batch, both with CIs spanning (or nearly spanning) zero, echoing the monthly regime's own
  weaker showing for `absolute_momentum`. `multi_timeframe_composite`'s holdout (Sharpe 0.61, CI
  entirely positive) is again strong, but still rests on a single holdout only, no walk-forward
  robustness check applies to it, and its signal here is monthly, not weekly, despite the weekly
  rebalance cadence, see the mechanical fact above. Same proxy-universe scope caveat as every
  prior validation epic. This closes the out-of-sample validation program for the 6 real
  non-alias `strategy_type` variants across both regimes; `hybrid_multi_factor` remains
  permanently un-backtestable (see Epic 17's own entry), and `momentum`/`relative_momentum`/
  `volatility_scaled_momentum` were covered or ruled out earlier (Epic 15/16/17).

- **Real out-of-sample validation for the two NEW selectable momentum strategies, Epic 7,
  "Institutional Momentum Strategy & Execution-Quality Enhancements" plan**: extends the same
  walk-forward + pre-registered holdout methodology to `proximity_52w_high` (George & Hwang 2004
  distance-from-52-week-high signal) and `sector_relative_momentum` (ranks within sector, not the
  whole universe), both new in this epic, both regimes, same cached 17-ticker proxy universe and
  `pre_registered_split(split_date="2015-01-01")`
  (`notebooks/research/out_of_sample_validation_new_strategy_types.ipynb`, run 2026-08-08).

  | `strategy_type` | Regime | Chosen lookback | Mean train Sharpe | Mean test Sharpe | Holdout Sharpe | Holdout CAGR | Holdout Alpha | 90% Bootstrap CI |
  |---|---|---|---|---|---|---|---|---|
  | `proximity_52w_high` | Monthly | 6 mo | 0.88 | 1.26 | 0.49 | 4.13% | -0.73% | [-0.02, 1.08] |
  | `sector_relative_momentum` | Monthly | 18 mo | 1.28 | 1.22 | 0.55 | 4.08% | -0.57% | [0.13, 1.07] |
  | `proximity_52w_high` | Weekly | 8 wk | 0.65 | 1.40 | 0.34 | 1.81% | -1.64% | [-0.08, 0.84] |
  | `sector_relative_momentum` | Weekly | 4 wk | 1.00 | 1.23 | **0.60** | **3.65%** | -0.33% | [0.17, 1.08] |

  Honest reading: `proximity_52w_high` sits in a similar quality range to `absolute_momentum`/
  `path_dependent_momentum` from Epic 17/18, both regimes' CIs span (or nearly span) zero, not a
  standout. `sector_relative_momentum` produced the strongest result of this pair in BOTH
  regimes, CIs entirely above zero, on par with `residual_momentum`'s own Epic 17/18 standout
  result. **Real, honestly disclosed caveat specific to this result, not glossed over**: this run
  used an ASSET-CLASS-level `ticker_sectors` grouping (Broad Equity / Fixed Income / Sector
  Equity / Commodities, see the notebook's own intro cell), not a true multi-ticker-per-GICS-
  sector mapping, since the cached proxy universe has roughly one ticker per real GICS sector
  (mostly single-sector SPDRs), not genuine same-sector peer groups. It's plausible this result
  partly reflects a genuine diversification-across-asset-classes effect rather than a pure
  George & Hwang-style sector-relative momentum signal; a real test on individual stocks with
  several genuine peers per GICS sector would be needed before treating this as confirmed
  evidence for the strategy specifically, not just for the broader "compare within a peer group"
  idea. Same proxy-universe scope caveat as every prior validation epic otherwise.

- **Ensemble momentum, Epic 8, "Ensemble Momentum Strategy" plan, a real, honest NEGATIVE
  result, not glossed over**: every individual `strategy_type` validated so far (Epic 15-18, 7)
  shows the same pattern, a decent Sharpe but near-zero or negative alpha with a CI often
  spanning zero, most of the measured return traces to market-beta exposure. The
  architecture-compatible fix considered here (real breadth + market-neutral shorting was
  explicitly rejected, it contradicts this project's long-only scope): blend several
  individually-validated, imperfectly-correlated `strategy_type`s into one `strategy_type:
  ensemble_momentum` score. Built with real, data-driven steps at every stage, not guessed:
  `notebooks/research/ensemble_signal_correlation_analysis.ipynb` computed REAL pairwise
  correlation across 6 candidates, picking `residual_momentum`/`sector_relative_momentum`/
  `multi_timeframe_composite` (the 3 CI-clears-zero candidates, correlated 0.74-0.78 in the
  monthly regime); `notebooks/research/ensemble_weighting_scheme_search.ipynb` ran a real
  walk-forward TRAIN-fold-only search across equal/confidence-weighted/inverse-correlation-
  weighted schemes, picking `equal` (monthly) and `confidence_weighted` (weekly).

  **The single pre-registered holdout result** (`notebooks/research/out_of_sample_validation_
  ensemble_momentum.ipynb`, run 2026-08-08): monthly holdout Sharpe 0.44 (alpha -1.63%, CI
  `[0.03, 0.96]`), weekly holdout Sharpe 0.37 (alpha -1.59%, CI `[-0.04, 0.85]`, **spans zero**).
  **Honestly, this is WORSE than every one of the 3 individual components on their own**:
  monthly `residual_momentum` alone scored alpha -0.17% (CI `[0.08, 0.96]`), `sector_relative_
  momentum` alone -0.57% (CI `[0.13, 1.07]`); weekly `residual_momentum` alone -0.09% (CI
  `[0.12, 1.14]`), `sector_relative_momentum` alone -0.33% (CI `[0.17, 1.08]`), all clearing
  zero, none of which the ensemble matched. Ensembling, despite a real, theoretically sound
  motivation and a rigorous, fully data-driven construction at every step, did NOT reduce noise
  or improve the result here, it diluted it. A plausible explanation, not confirmed: percentile-
  normalizing and averaging discards each component's own raw-magnitude conviction, smoothing
  toward a "consensus mediocre" pick rather than preserving what made each component's own
  strongest signals work. **This does not change the shipped default** (`strategy_type:
  momentum`), it's a real, honestly-reported negative result for anyone considering the ensemble
  approach specifically, not a recommendation to use it. The mechanism itself
  (`resolve_ensemble_momentum_scores()`, `strategy_type: ensemble_momentum`) remains available
  and fully tested for anyone who wants to try a different component/weighting combination.

- **Best-practice protective config, Epic 9, a real, regime-dependent result, not glossed
  over**: stacks every real, already-individually-tested protective mechanism this project has
  (regime filter vol dimension, momentum-crash protection, circuit breaker, correlation-spike
  regime, correlation penalty + shrinkage covariance, ERC sizing, tighter position/sector caps,
  both trailing-stop types plus broker-native brackets with auto-execution, a time-based
  backstop, liquidity/volume/technical selection filters, VaR/CVaR + liquidity-adjusted sizing)
  on top of `strategy_type: residual_momentum` (the single best-validated signal), never jointly
  tested before, no new production code, pure config recombination.
  `notebooks/research/out_of_sample_validation_best_practice_config.ipynb` (run 2026-08-08)
  compares this bundle against `residual_momentum`'s own already-published baseline, both
  regimes, single pre-registered holdout:

  | Regime | Metric | Baseline | + Full Bundle |
  |---|---|---|---|
  | Monthly | Sharpe | 0.46 | **0.53** |
  | Monthly | Alpha | -0.17% | **+0.80%** |
  | Monthly | Max Drawdown | -13.16% | **-6.63%** |
  | Monthly | 90% Bootstrap CI | `[0.08, 0.96]` | `[0.13, 1.03]` |
  | Weekly | Sharpe | 0.59 | 0.06 |
  | Weekly | Alpha | -0.10% | -1.90% |
  | Weekly | Max Drawdown | -12.26% | -12.54% |
  | Weekly | 90% Bootstrap CI | `[0.12, 1.14]` | `[-0.40, 0.56]` |

  **Monthly: a real, clear improvement**, including the first genuinely POSITIVE alpha result
  anywhere in this project, max drawdown nearly halved, both CIs clear zero with the bundle's own
  sitting higher. The stacked selection filters do hold the book in cash 20.7% of rebalance dates
  (29 of 140), a real, disclosed contributor to the drawdown improvement.

  **Weekly: a real regression, diagnosed, not just observed.** Removing
  `use_technical_confirmation` alone (a 50-day SMA condition, too slow for an 8-week signal)
  recovers about half the damage (Sharpe 0.06 -> 0.26), but the bundle remains worse than
  baseline on every metric even then (still CI-spans-zero, max drawdown actually worse than
  baseline), not a one-field fix. The remaining stacked selection filters and monthly-tuned
  circuit-breaker/momentum-crash thresholds don't transfer cleanly to the weekly cadence.

  **Final recommendation**: adopt the full protective bundle for the MONTHLY regime; keep the
  simpler, already-validated `residual_momentum` baseline for the WEEKLY regime rather than this
  bundle. A properly weekly-tuned protective bundle (its own dedicated search over which subset
  of mechanisms actually helps at that cadence) is real, valuable future work, not attempted
  here. See `docs/RISK_CONSTRAINTS.md`'s "Maximum Protective" preset for the full YAML.
  **A second real, viable strategy option, confirmed NOT to be blended**: `sector_relative_
  momentum` also clears zero in both regimes on its own; Epic 8 already showed blending it WITH
  `residual_momentum` into one ensemble score makes results worse, so if you want exposure to
  both, run them as separate portfolios/books, not a blended score.

  **`config.example.yaml` now ships this recommendation directly**, not just described here:
  its `portfolios:` block was rewritten to `portfolio_monthly_protected` (the full bundle above,
  a real `ticker_sectors` mapping included) and `portfolio_weekly_baseline` (`residual_momentum`
  alone, deliberately without the bundle, per the weekly result above), plus a commented-out
  `portfolio_sector_relative_alt` showing the second-book option. Confirmed to build valid
  `BacktestConfig` objects with zero errors through the real `load_config()` pipeline before
  shipping, not just YAML-syntax-checked. Copying `config.example.yaml` to `config.yaml` now
  starts a new deployment from this validated recommendation instead of a bare-bones example.

- **Institutional-Grade Reporting Cadence Expansion, Epic 10**: this project only ever emailed
  daily and monthly reports; real institutional/hedge-fund reporting uses genuinely different
  cadences for genuinely different purposes (a PM/trading-desk weekly check-in, a risk/
  attribution quarterly deep-dive, a full-year annual strategic review), not the same report
  re-sent on a different clock. Adds four new report cadences (Weekly/Quarterly/Annual/Summary)
  plus four new metric functions (Calmar Ratio, week-scale best/worst rolling periods, safely-
  scaffolded 3/5/10-Year long-horizon windows, and live-wired drawdown-episode history), **with
  an explicit, honored constraint: the pre-existing daily/monthly report code
  (`_build_report_html()`, `build_monthly_report_html()`, `build_daily_report_html()`,
  `send_monthly_report()`, `send_daily_report()`) is completely untouched**, every new report is
  new, additive code, confirmed by dedicated regression tests asserting byte-identical
  `"monthly"`/`"daily"` dispatch behavior in `daily_runner.py`'s `build_and_send_portfolio_
  report()`.

  | Cadence | Institutional analog | Key additions |
  |---|---|---|
  | Weekly | PM/trading-desk check-in | 1W/1M/3M windows, Calmar Ratio, best/worst 1-week return. Deliberately LEAN: no technical/fundamental indicators, no OHLCV fetch at all |
  | Quarterly | Risk/attribution deep-dive | QTD/YTD/1-Year windows, Calmar, drawdown-episode summary, best/worst 12-week return, same indicators as monthly |
  | Annual | Full-year strategic review | 3/5/10-Year trailing windows (shown once real history supports them), Calmar, FULL drawdown-episode history, best/worst 36-week return. A data rollup, deliberately not a free-text investor-letter narrative (no LLM-integration precedent in this project) |
  | Summary | Cross-cadence "at a glance" digest | Current value, recent deltas, since-inception headline, WARNING/CRITICAL alert count since last summary, orphan-position count (0 until Epic 12). Chart-free, its own configurable cadence |

  All four hook into the EXISTING daily cron trigger via their own day-check, the identical
  pattern `monthly_report_day_of_month` already established, no new cron line needed. All four
  are also reachable on-demand via `TRIGGER_REPORT` email command's `REPORT_TYPE:` field,
  extended from `MONTHLY`/`DAILY` to include `WEEKLY`/`QUARTERLY`/`ANNUAL`/`SUMMARY`.

  **Real verification, run 2026-08-08**: full pytest suite 1213 passed (up from 1156 pre-Epic-10,
  +57 new tests), zero regressions, native and inside a Docker image rebuilt with this epic's
  code. A dry-run smoke test (`daily-runner --force-rebalance`, throwaway config reusing the
  real, already-accumulated `portfolio1` name so the new reports had real history to render
  against) ran clean both natively and in Docker. All four new report types were confirmed
  sending REAL emails via real SMTP against real accumulated data, both natively and inside
  Docker. **A real, unplanned bonus confirmation inside Docker**: a real `TRIGGER_REPORT`
  command email (`REPORT_TYPE: SUMMARY`) was sent, then found and correctly processed via a
  real IMAP poll INSIDE the container end-to-end (accepted, dispatched, a real summary email
  sent), the same real-pipeline standard Epic 6's own `TRIGGER_REPORT` verification already
  set. **A real, honest, pre-existing issue surfaced by this same test, unrelated to Epic 10's
  own code**: the identical command failed with `POLL_ERROR: could not connect to IMAP server`
  when attempted natively on this Windows dev box, confirmed to predate this epic by weeks (the
  alerts log's first occurrence is 2026-07-23), a native-environment network/IMAP connectivity
  issue Docker's own network stack doesn't share, not a regression introduced here.

  **Real `--live --port 7497` paper-account verification, run 2026-08-08, native AND Docker**
  (closing a real gap in the first verification pass, which only covered dry-run + SMTP/IMAP):
  a throwaway `epic10_live_verify` portfolio (`JNJ`/`PG`/`KO`/`PEP`) ran a real
  `--force-rebalance --live --port 7497` rebalance against the real IBKR paper account
  (`DUQ168660`), both natively and inside the rebuilt Docker image, real `BUY` orders reached
  the broker and were accepted (informational code `399`, correctly queued for the next real
  session since both runs happened outside market hours). `get_ibkr_positions()` was then
  called for real (19 real positions on that account, accumulated from prior epics' own
  testing), and the new report builders were called directly with these REAL, non-empty
  positions for `"weekly"`/`"quarterly"`, confirming the Position Performance section and the
  held-ticker indicator fetch (real Yahoo Finance/FMP calls) work correctly against real
  broker data, not just the empty/synthetic inputs the first pass used, native and Docker both.

  **Per-portfolio isolation, explicitly confirmed**: every new report's day-check sits at the
  same nesting level as the pre-existing `monthly_report_day_of_month` check, inside the
  per-portfolio loop, so each cadence fires once per portfolio using only that portfolio's own
  data, never mixed. Verified empirically: building the Summary report for the real
  `config.yaml`'s own `portfolio1`/`portfolio2`/`portfolio3` produced three distinct, correctly
  labeled reports showing each portfolio's own real total value (`$1,500`/`$1,000`/`$100,000`).

- **Overnight Gap-Risk Detection & Alerting, Epic 11**: a real, previously-unaddressed gap,
  every existing stop-loss/trailing-stop/time-stop check compares only entry price (or a running
  high) against TODAY's fetched price, never yesterday's close against today's, so a stop could
  silently fill below its intended level on an overnight gap with no distinct signal that a gap
  specifically was the cause. Adds `gap_alert_threshold_pct` (opt-in, `None` default), wiring a
  new `detect_overnight_gap()` pure function into a fourth member of the daily exit-check
  family, `check_and_handle_overnight_gaps()`, which reads (never writes) the SAME shared
  `already_flagged` set the other three checks already populate, so its `OVERNIGHT_GAP_DETECTED`
  `WARNING` alert can explicitly say when a stop-loss/trailing-stop/time-stop check ALSO fired
  for the same ticker the same run, the exit fill may have occurred beyond its intended level
  because of the same gap.

  **Detection only, not prevention, honestly disclosed, not oversold**: every price vendor this
  project uses is strictly EOD daily-bar data (confirmed by reading all three fetchers
  directly), there is no way to react to a gap WHILE it happens with this architecture, the same
  "cannot be fully solved without intraday data" limitation the backtest engine's own GAP-RISK
  LIMITATION comment already discloses for simulated fills, extended to the live path here for
  the first time. A true gap-PREVENTION mechanism would need a paid real-time IBKR market-data
  subscription plus an intraday-polling process, a genuinely different architecture from this
  once-daily cron app, out of scope, a considered exclusion.

  **Real verification, run 2026-08-08, native AND Docker**: a deliberately tiny
  `gap_alert_threshold_pct=0.001` (0.1%, same "force a near-certain trigger from ordinary
  day-to-day price movement" precedent Epic 2's own ATR trailing-stop verification already
  established) called directly against the real IBKR paper account's 19 real held positions and
  real freshly-fetched prices correctly flagged 18 of 19 tickers, real
  `OVERNIGHT_GAP_DETECTED` alerts written to the real hash-chained alerts log with real
  ticker/direction/gap%/price detail (e.g. `"ASML gapped up 2.1% overnight ($1704.37 ->
  $1740.99)"`), identical results natively and inside a Docker image rebuilt with this epic's
  code. A dry-run smoke test (`daily-runner --force-rebalance` with this field enabled) also ran
  clean, no crash in the integrated per-portfolio-loop call site, both natively and in Docker.
  Full pytest suite 1231 passed (up from 1213 pre-Epic-11, +18 new tests), zero regressions.

  **Real `--live --port 7497` INTEGRATED pipeline verification, run 2026-08-08, native AND
  Docker**: a throwaway `epic11_gap_verify` portfolio with `gap_alert_threshold_pct` set ran a
  real `--force-rebalance --live --port 7497` rebalance against the real IBKR paper account,
  both natively and inside the rebuilt Docker image, real `BUY` orders placed and queued
  (informational code `399`, outside market hours), identical in both environments. **A real,
  honest, informative finding, not a bug**: for this brand-new throwaway portfolio (zero prior
  trades of its own), the account's 19 other real positions correctly surfaced as
  `UNRECOGNIZED_POSITION` rather than being treated as this portfolio's own, the SAME
  cross-config ticker-ownership protection Epic 5 already built working exactly as designed, so
  `current_positions` reaching the gap check inside this specific run was correctly empty. This
  confirms the integrated call site wires correctly and never crashes; a demonstration of it
  actually firing within one real `--live` run needs a portfolio with already-confirmed real
  holdings of its own (either waiting for queued orders to fill on the next real session, or
  running against a real, already-established portfolio, deliberately not done here without
  being asked). All 6 test orders across both verification rounds were cancelled afterward.

- **Orphan Portfolio Tracking & Reporting, Epic 12**: a `confirmed_orphaned` ticker (held on the
  real account but no longer in a portfolio's own `tickers:` config, this portfolio's own trade
  log confirms it was legitimately held here) was already priced/reconciled every run before
  this epic, but nothing PERSISTED anything about it or SURFACED it to a human beyond a per-run
  `WARNING` alert, no way to see "how long has this been orphaned" or "return since entry"
  without reading the trade log by hand. Adds `update_orphan_state()`, persisting ONLY each
  orphaned ticker's `first_detected_date` (`data/orphan_positions_<portfolio>.json`), and
  `build_orphan_report_data()`, which reuses `build_position_performance()` UNCHANGED (the SAME
  FIFO machinery already powering the Position Performance report section) for entry/current
  price/return, so there's no second cost-basis implementation and no risk of a stale persisted
  copy drifting from real state. Shows up as a new detail table in Epic 10's Summary report
  (ticker/shares/entry date/entry price/current price/return/days orphaned/a plain-language
  assessment), deliberately not a new email category (a sub-section of an existing digest).
  **INFORMATIONAL ONLY, confirmed design decision**: nothing here proposes or applies a
  `config.yaml` change automatically, the human reads the assessment and edits `config.yaml`
  themselves, matching this project's existing "human approves capital-affecting config
  changes" pattern everywhere else.

  **A real mechanical subtlety found via direct live-account testing, not assumed**: because a
  `confirmed_orphaned` ticker is priced AND made eligible for exit in the SAME run it's first
  detected, it can be classified, recorded, and sold by the normal rotation logic all within one
  invocation if that run is also a rebalance day, this is the pre-existing `confirmed_orphaned`
  behavior this epic builds on top of, not a new bug; a separate later invocation can find the
  position already reconciled away. See `docs/ORPHAN_TRACKING.md` for the full writeup.

  **Real verification, run 2026-08-08, native AND Docker**: a throwaway `epic12_orphan_verify`
  portfolio constructed a REAL `confirmed_orphaned` scenario against the real IBKR paper account
  (`DUQ168660`), not synthetic: `--live --force-rebalance` with `tickers: [KO]` placed a real
  BUY (logged in this portfolio's own trade log), then a second run with `KO` removed from
  `tickers:` correctly classified it as `confirmed_orphaned`, and `update_orphan_state()` wrote
  a real state file with today's real date. Calling `build_and_send_portfolio_report(...,
  report_type="summary", confirmed_orphaned=["KO"])` directly (avoiding the same-run
  rotation-sell timing subtlety above) sent a REAL email via real SMTP containing the real
  Orphaned Positions detail table for KO, with real entry price, real current price, real
  return %, and real days-orphaned count, confirmed identically both natively and inside a
  Docker image rebuilt with this epic's code. All test orders placed during verification were
  cancelled afterward. Full pytest suite 1247 passed (up from 1231 pre-Epic-12, +16 new tests),
  zero regressions.
- **Several real risk/sizing mechanisms used to act completely silently, no email, no alert-log
  entry, only a smaller final number, fixed by Epic 13, "Risk & Sizing Mechanism Transparency
  Alerts" plan**: direct investigation found `backtest/momentum_backtest.py` had **zero**
  `log_alert()` calls anywhere, so `max_position_weight`/`position_vol_budget`/
  `max_sector_weight`/`max_factor_exposure` all silently trimmed a position; the ACTIVE
  liquidity-adjusted-sizing mechanism (`enabled_risk_strategies: [liquidity_adjusted_sizing]`)
  silently shrank a target dollar allocation; and the regime filter's SMA-trend-bearish case was
  visible only via a `logger.info()` file line, never emailed, unlike its own volatility-driven
  sibling alert. Built test-first throughout (TDD, every new alert's test written and confirmed
  failing before the code existed): `resolve_target_weights()` now returns a `WeightsResult`
  (a `dict` subclass, byte-identical to a plain dict for every existing caller, the same safe
  pattern `execution/live_signal.py`'s `OrdersResult` already established) recording what each
  cap step actually trimmed, and `execution/live_signal.py`'s `compute_target_weights()`/`run()`
  fire 5 new real alerts off it: `POSITION_CAP_APPLIED`, `SECTOR_CAP_APPLIED`,
  `FACTOR_CAP_APPLIED`, `LIQUIDITY_ADJUSTED_SIZING_APPLIED`, and `MARKET_TREND_REGIME_DEFENSIVE`.
  The shared, backtest-called functions stay pure/alert-free by design, alerting lives entirely
  on the live side, the same precedent every other regime/momentum-crash/correlation-spike alert
  in this project already follows. **Real verification, run 2026-08-09**: full pytest suite 1260
  passed (up from 1247 pre-Epic-13, +13 new tests), zero regressions. A throwaway
  `epic13_verify` portfolio with deliberately tight thresholds confirmed all 5 alerts fired for
  real, with real numbers, via `daily-runner --force-rebalance` (dry-run) AND `--live --port
  7497` against the real IBKR paper account (`DUQ168660`), identically both natively and inside
  a Docker image rebuilt with this epic's code; a real `BUY 3 SPY` order reached the broker in
  both environments (informational code `399`, correctly queued for the next real session).
  **Honestly disclosed**: cancelling those two queued test orders afterward hit a real,
  reproducible IBKR paper-account quirk (`cancelOrder()` error `10147`, "order not found",
  regardless of `clientId`), matching several other long-uncancellable orders already sitting on
  this same paper account from unrelated prior epics' own sessions, a pre-existing environment
  limitation, not caused by this epic's code, zero real financial risk (paper account, unfilled,
  outside RTH). See `CLAUDE.md`'s `execution/live_signal.py` bullet for the full mechanism.
- **A real production exception (`resolve_residual_momentum_scores(): benchmark 'SPY' is not
  priced in daily_prices`) hit `portfolio1`, fixed by Epic 14, "Auto-Widen Price Fetch for
  regime_benchmark / defensive_ticker" plan**: `strategy_type: residual_momentum` needs
  `regime_benchmark` priced to compute a score at all, but nothing anywhere ever widened the
  live price fetch to include it when it wasn't independently already in a portfolio's own
  `tickers:` list, confirmed by direct investigation, not assumed. A second, related, SILENT gap
  shared the identical root cause: `use_regime_filter` defaults to `True`, and the plain SMA
  regime filter silently no-ops (rather than raising) when its benchmark is unpriced, so
  `portfolio1`'s regime filter had likely never actually done anything either. A third,
  currently-dormant gap (`defensive_ticker`/`use_absolute_momentum`) shares the exact same shape
  and was closed for free. Fixed via a new pure resolver, `resolve_extra_required_price_tickers
  (cfg)`, feeding a small, SEPARATE, best-effort supplemental fetch inside `run()` (NOT merged
  into the primary fetch, a deliberate choice: `use_regime_filter` defaulting `True` would have
  made that widen the requested ticker set for nearly every `run()` call across the whole test
  suite, confirmed to be a real risk before choosing this design), wrapped in a `try/except` so
  a genuine vendor gap or an unrelated test's mock degrades to EXACTLY the pre-existing behavior
  (the regime filter's own silent no-op, or `residual_momentum`'s own existing clear error),
  never a new failure mode. **Real verification, run 2026-08-09**: full pytest suite 1271 passed
  (up from 1260 pre-Epic-14, +11 new tests), zero regressions. A throwaway portfolio reproducing
  the exact original production shape confirmed the fix via `daily-runner --force-rebalance`
  (dry-run, no exception, a real, now-functional regime filter scalar) AND `--live --port 7497`
  against the real IBKR paper account, identically both natively and inside a Docker image
  rebuilt with this epic's code; real `BUY` orders for both picks reached the broker in both
  environments. See `CLAUDE.md`'s `execution/live_signal.py` bullet for the full mechanism.
- **A real, live cross-portfolio SELL risk (portfolio1 could sell portfolio2's real SPY
  position), fixed by Epic 15, "Scope current_holdings to Exclude Unrecognized Positions"
  plan, found investigating a rebalance-email discrepancy the very next day**: `daily_runner.py`
  built `current_holdings` from the ENTIRE unscoped real broker account before classifying
  held-but-unconfigured tickers into `confirmed_orphaned`/`unrecognized`, and never actually
  filtered it afterward, despite the code's own comment claiming otherwise. Harmless before
  Epic 14 (nothing ever priced an `unrecognized` ticker), but Epic 14's own supplemental price
  fetch for `regime_benchmark`/`defensive_ticker` closed exactly that gap, and confirmed via the
  real `config.yaml`: `portfolio1`'s `regime_benchmark` is `SPY`, `portfolio2` legitimately
  trades `SPY`, so portfolio1 could generate and submit a real `SELL` for portfolio2's real
  position. Fixed via a new, small, independently-tested helper filtering `current_holdings` at
  its one true source. **Real verification, run 2026-08-09**: full pytest suite 1277 passed (up
  from 1271 pre-Epic-15, +6 new tests, including a regression test that reproduces the exact
  incident end-to-end through a real `run()` call before proving the fix prevents it), zero
  regressions. A throwaway portfolio pointed at a real, already-held, unconfigured position
  confirmed the fix via `--live --port 7497` against the real IBKR paper account, identically
  both natively and inside a Docker image rebuilt with this epic's code: the position was
  correctly classified `UNRECOGNIZED_POSITION`, still correctly priced for the regime filter
  (confirming Epic 14's own mechanism stayed intact), but generated no order at all. **A
  separate, honestly-disclosed finding surfaced during this same verification, not part of this
  epic's own scope**: the real paper account was found to be carrying several pre-existing,
  unfilled, plain `SELL` orders for unrelated tickers that look like residue from this exact bug
  class, generated by an earlier session before this fix existed, left uncancelled (unfilled,
  paper account, zero real financial risk, not reliably targetable via the API). See
  `CLAUDE.md`'s `daily_runner.py` bullet for the full mechanism and the complete disclosure.
- **`cron` inside the Docker container had never actually executed a single scheduled job, ever,
  fixed by "Fix cron Never Actually Executing Any Scheduled Job" plan**: confirmed by direct
  live testing against the real running container, not guessed, investigating whether the daily
  rebalance/risk-monitor cron jobs had actually been running. Two independent, compounding bugs
  in `docker-entrypoint.sh`: an unescaped `%` in every generated crontab line's `$(date
  +%Y%m%d)` log-path substitution (crontab file syntax treats an unescaped `%` as a
  newline/stdin separator, silently truncating every one of the three real job lines before the
  shell ever reaches its own log redirect, so nothing was ever logged, ever, regardless of how
  many times the schedule fired), and cron's own hardcoded minimal job `PATH=/usr/bin:/bin`,
  which doesn't include `/usr/local/bin`, where `daily-runner`/`python` actually live (unlike
  the container's own interactive-shell PATH, which does, the reason manual `docker exec`
  invocations always worked while cron's own scheduled jobs never did). Fixed by escaping every
  `%` as `\%` and prepending a `PATH=` directive line to the generated crontab. **Real
  verification, run 2026-08-10**: full pytest suite 1281 passed (up from 1277, +4 new tests),
  zero regressions. A real, rebuilt Docker container's real crontab (`daily-runner --live --port
  7497`, `risk_monitor.py --portfolio portfolio1`, and the `--check-commands-only` email-check
  poll) was confirmed, for the first time in this container's history, to actually execute all
  three job types on real triggers, each producing a real, correctly date-named log file with
  real successful output (including a real IBKR connection attempt and a real P&L computation
  across 133 real trades), the natural, un-forced `*/5 * * * *` schedule included, not just a
  forced test. See `CLAUDE.md`'s `risk/risk_monitor.py` bullet for the full mechanism.
- **cron-spawned jobs never received the container's own SMTP/IMAP/IBKR/API-key environment,
  fixed by "Propagate Full Container Environment to Cron Jobs" plan**: a real, user-reported
  incident (2026-08-11, "why didn't today's report email arrive") traced to a gap the cron-PATH
  fix above didn't cover: `crond` hands a spawned job ONLY `HOME`/`LOGNAME`/`PATH`/`SHELL`/`PWD`,
  confirmed directly with a throwaway test cron job dumping its own environment, none of the
  container's real `SMTP_*`/`IMAP_*`/`IBKR_*`/`*_API_KEY`/`ALERT_TO_EMAIL` vars reached it, even
  though `docker exec` misleadingly makes it look like cron should see them too (`docker exec`
  inherits PID 1's environment directly, cron's own children never do). Real consequence: the
  scheduled `daily-runner --live` run crashed connecting to IBKR at the wrong fallback host
  (`IBKR_HOST` unset under cron defaults to `127.0.0.1`, not the real `host.docker.internal`),
  and the crash-alert email meant to report even that failure also silently failed to send
  (`SMTP_HOST`/`SMTP_USER`/`SMTP_PASS`/`ALERT_TO_EMAIL` also unset), so nothing reached the
  inbox at all, no rebalance and no failure notice either. Fixed: `docker-entrypoint.sh` now
  snapshots the full container environment once at startup into a shell-sourceable file, and
  every cron job sources it before running. A second, real bug found while building this: not
  every environment variable name is a valid POSIX shell identifier (Windows sets
  `COMMONPROGRAMFILES(X86)`, confirmed via a real generated file on the dev machine), and
  emitting it literally would abort the entire cron job with a shell syntax error, the same
  failure class this fix exists to close; fixed by filtering variable names to valid shell
  identifiers before writing them. **Real verification, run 2026-08-11**: full pytest suite 1293
  passed (up from 1281, +12 new tests), zero regressions. A rebuilt container's cron-sourced
  environment was confirmed to include the real `SMTP_HOST`/`IBKR_HOST`/`FMP_API_KEY`/etc. (33
  vars, up from 5), the exact cron-invoked command now reaches a real, successful IBKR handshake
  against the real paper account and a real `SMTP: OK`/`IMAP: OK` result, and all six report
  cadences (daily/weekly/monthly/quarterly/annual/summary) were confirmed sending real emails
  under the fixed environment. See `CLAUDE.md`'s `risk/risk_monitor.py` bullet for the full
  mechanism.
- **A real deployed rebalance email surfaced two real, confirmed "Full Signal Universe"
  reporting bugs plus one real, confirmed table-ordering inconsistency, fixed by "Full Signal
  Universe Reporting Accuracy Fixes" plan**: found by investigating a real production email, not
  guessed. (1) A non-selected ticker's stated exclusion reason (`"Excluded (Illiquid)"` etc.)
  used to be wrong whenever more than one selection-time filter was enabled: each check compared
  against the FINAL rank rather than its own immediate downstream filter's snapshot, so whichever
  filter came first in the chain (`use_liquidity_filter`) won for virtually any exclusion cause.
  Confirmed against real config/data: a highly-liquid real ticker (`MU`, ~$47.8B trailing dollar
  volume) was reported `"Excluded (Illiquid)"` when it had actually only failed
  `use_technical_confirmation`. (2) Rank Delta (`use_rank_delta`) was silently `None` for EVERY
  ticker whenever `use_liquidity_filter`/`use_technical_confirmation`/`use_volume_confirmation`
  was also enabled, exactly a real deployed portfolio's own config, because the historical
  comparison point was read off the same fully-filtered ranks, and the liquidity/volume filters'
  own volume-data window is nowhere near wide enough to re-evaluate months back. (3) The
  Rebalance Summary email table (Table 1) had no defined sort order at all (an unordered Python
  `set` under the hood), inconsistent with the Full Signal Universe table (Table 2) right below
  it in the same email, which IS explicitly rank-sorted. All three fixed: exclusion-reason
  checks now compare against their own immediate downstream snapshot; Rank Delta's historical
  side now reads off a raw, pre-any-filter ranks snapshot captured before any selection-time
  filter runs (a deliberate, honestly-documented semantic: it now measures the ticker's
  underlying score trend, not "would it also have passed today's filters back then"); Table 1
  now sorts by the same rank-ascending/score-descending key Table 2 already used. **Real
  verification, run 2026-08-10**: full pytest suite 1287 passed (up from 1281, +6 new tests
  covering all three fixes), zero regressions. A dry-run smoke test against the actual
  production `config.yaml` confirmed both reporting fixes against real, live-fetched data: `MU`
  (a real, highly-liquid portfolio1 ticker) now correctly shows `"Excluded (Technical)"`, not
  `"Excluded (Illiquid)"`; several real currently-ranked tickers now show real, non-blank
  `rank_delta` values instead of universally `None`; and Table 1's ticker order, rebuilt from
  this run's real trade-log rows, matched ascending rank exactly. A throwaway 4-ticker portfolio
  mirroring portfolio1's own filter combination confirmed the fixed code end-to-end via
  `--live --port 7497` against the real IBKR paper account, a real `BUY` order reached the
  broker and FILLED identically both natively and inside a rebuilt Docker container. See
  `CLAUDE.md`'s `execution/live_signal.py` and `interfaces/notifications.py` bullets and
  `docs/SIGNAL_RANKINGS_LOG.md`'s "Rank Delta" column for the full mechanism.

### Who should allocate capital here

Momentum strategies have real, sometimes multi-year, underperformance periods even when the
long-run edge is genuine, this isn't a flaw specific to this implementation, it's inherent to
the factor (the chart above is a live example of that). Only allocate capital that:
- You can leave systematically managed through a genuinely bad multi-month or multi-year
  stretch without needing to intervene emotionally.
- You won't need for at least 1-2 years.
- Represents a deliberate allocation decision, not money you're testing this system with
  because it happens to be available.

</details>

<details open>
<summary> <b>Using The Package<b></summary>

- Clone the repo:
~~~bash
    git clone https://github.com/issaiass/momentum-trading.git
    cd momentum-trading
~~~
- Install (editable install, `uv` or plain `pip`):
~~~bash
    uv sync                                    # if using uv (uv.lock present)
    # or
    pip install -e ".[dev]"                    # dev deps add pytest
~~~
- Copy the example config and edit it (tickers, portfolios, risk settings):
~~~bash
    cp config.example.yaml config.yaml
~~~
- If using email notifications/commands, copy `.env.example` to `.env`, fill in real values, then
  verify them for real before trusting cron/`--live` with them:
~~~bash
    daily-runner --test-email
~~~
- Test signal/order generation, safe, no broker connection, never places an order:
~~~bash
    daily-runner --force-rebalance
~~~
- Paper trade (requires TWS/IB Gateway running, paper account logged in on port 7497):
~~~bash
    daily-runner --live --port 7497
~~~
- Go live, both flags are required together, on purpose:
~~~bash
    daily-runner --live --port 7496 --confirm-live-trading
~~~
- Clear a circuit-breaker halt after reviewing what tripped it:
~~~bash
    daily-runner --resume-trading <portfolio_name>
~~~
- Run the independent, read-only risk monitor:
~~~bash
    python -m momentum_trading.risk.risk_monitor --portfolio <name> --max-loss-pct 0.25
~~~
- Or run it all in Docker, self-scheduling via internal cron, no manual triggering needed:
~~~bash
    docker compose up -d --build
    docker exec -it momentum-signal crontab -l              # verify the schedule
    docker exec -it momentum-signal daily-runner --force-rebalance   # one-off manual check
~~~
- Run the test suite (no network/broker required, synthetic/mocked data throughout):
~~~bash
    pip install -r requirements-dev.txt
    pytest tests/ -v
~~~

Full argument reference: `daily-runner --help`. Day-to-day commands, the staged rollout plan,
and multi-portfolio/Docker specifics live in `docs/RUNNING.md` and `docs/DEPLOYMENT.md`.

</details>

<details open>
<summary> <b>Documentation Map<b></summary>

| I want to... | Read |
|---|---|
| Understand what each file does | This README (above) |
| Install this on a new machine | `docs/DEPLOYMENT.md` |
| Actually run it (single/multi-portfolio, paper/live) | `docs/RUNNING.md` |
| Understand the research/signal methodology | `notebooks/research/DHI0016_notebook1_research_and_EDA_IMPROVED.ipynb` (start there) |
| Understand the momentum strategy's theory + a worked example | `docs/STRATEGY_THEORY.md` |
| Run or understand the test suite | `docs/TESTING.md` |
| Configure/understand email notifications and monthly reports | `docs/EMAIL_REPORTING.md` |
| Configure/understand email-commanded remote actions (PAUSE/RESUME/etc.) | `docs/EMAIL_COMMANDS.md` |
| Understand the alert log (what's recorded, how it differs from the trade/email-command logs) | `docs/ALERT_LOG.md` |
| Understand the signal rankings log / "Full Signal Universe" email table (rank, rank delta, lookback return, selection status, stop-loss price for every ranked ticker) | `docs/SIGNAL_RANKINGS_LOG.md` |
| Understand the long-term/short-term momentum risk constraints (turnover, skip-month, vol budget) | `docs/RISK_CONSTRAINTS.md` |
| Choose/understand a selectable momentum `strategy_type` (Dual, Residual, Absolute, Hybrid Multi-Factor, etc.), per-strategy best-parameter presets | `docs/MOMENTUM_STRATEGIES.md` |
| Configure/understand opt-in log retention (archive-and-rotate, the retention window formula, the FIFO cost-basis safety guarantee) | `docs/LOG_RETENTION.md` |
| Understand orphan ticker tracking (a held-but-unconfigured position's own first-detected-date, entry/return, the Summary report's Orphaned Positions section) | `docs/ORPHAN_TRACKING.md` |

</details>

<details open>
<summary> <b>Results<b></summary>

The chart in "Brief Review" above is the current representative result: a real ETF price
history backtest, run through this project's own backtest engine, not a hand-tuned or
cherry-picked window. Further validation (walk-forward, regime-conditional breakdown,
out-of-sample holdout) is available via `core/functions_quant_extensions.py` and Notebook 1, see
`docs/STRATEGY_THEORY.md`.

### Underlying Momentum Evidence (Notebook 1 EDA)

The equity-curve chart above is this project's own backtested strategy scenarios against SPY,
specific configurations' outcomes. The three charts below are a different, earlier kind of
evidence: the classic academic cross-sectional momentum anomaly itself, measured directly on
this project's own ETF universe and price history in `notebooks/research/
DHI0016_notebook1_research_and_EDA_IMPROVED.ipynb`, before any of this project's own risk
overlays, sizing, or execution logic are applied. Don't conflate the two, a real anomaly existing
in this universe/history is not the same claim as "this project's specific live configuration
beats SPY."

<p align="center">
<img src="docs/img/momentum_winners_vs_losers.png?raw=true" alt="Cumulative performance of top vs. bottom momentum deciles" width="80%"/>
</p>

**Winners vs. losers**: every month, ETFs are ranked into deciles by trailing 12-month return,
this chart tracks the cumulative, indexed-to-100 performance of the top decile (recent winners)
against the bottom decile (recent losers). The winner decile compounding visibly above the loser
decile over time is the core cross-sectional momentum effect this whole strategy is built on.

<p align="center">
<img src="docs/img/momentum_win_rate_heatmap.png?raw=true" alt="Momentum win rate by lookback and holding period" width="80%"/>
</p>

**Does it hold across parameter choices?**: a lookback-period x holding-period grid, each cell is
the percentage of months the top decile actually beat the bottom decile at that specific
combination. A grid dominated by win rates comfortably above 2.06% across most combinations is
evidence the effect isn't an artifact of one specific lookback/holding choice.

<p align="center">
<img src="docs/img/momentum_decile_returns.png?raw=true" alt="Average 1-month forward return by momentum decile" width="80%"/>
</p>

**The plainest picture**: average 1-month forward return by decile (12-month lookback), decile 1
being the recent losers, decile 10 the recent winners. A roughly monotonic increase from decile
1 to decile 10 is the textbook signature of the momentum anomaly.

</details>

<details open>
<summary> <b>Issues<b></summary>

- No open code defects. The honest open items are the strategy-validation gaps listed under
  "Known Gaps" above, those are tracked as maturity gaps, not bugs.

</details>

<details open>
<summary> <b>Future Work<b></summary>

- Real out-of-sample validation against historical crash periods (2008/2020/2022), not just
  synthetic crash-shaped test data
- A tested live TWS/IB Gateway connection, and measured live-vs-backtest divergence once real
  trades exist
- Point-in-time universe construction to remove survivorship bias
- Tax-aware return modeling for taxable accounts
- Real order-book-based capacity/market-impact validation, beyond the current ADV-based
  advisory check

</details>

<details open>
<summary> <b>Contributing<b></summary>

Your contributions are always welcome! Please feel free to fork and modify the content but
remember to finally do a pull request.

</details>

<details open>
<summary> :iphone: <b>Having Problems?<b></summary>

<p align = "center">

[<img src="https://img.shields.io/badge/linkedin-%230077B5.svg?&style=for-the-badge&logo=linkedin&logoColor=white" />](https://www.linkedin.com/in/riawa)
[<img src="https://img.shields.io/badge/telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white"/>](https://t.me/issaiass)
[<img src="https://img.shields.io/badge/instagram-%23E4405F.svg?&style=for-the-badge&logo=instagram&logoColor=white">](https://www.instagram.com/daqsyspty/)
[<img src="https://img.shields.io/badge/twitter-%231DA1F2.svg?&style=for-the-badge&logo=twitter&logoColor=white" />](https://twitter.com/daqsyspty)
[<img src ="https://img.shields.io/badge/facebook-%233b5998.svg?&style=for-the-badge&logo=facebook&logoColor=white%22">](https://www.facebook.com/daqsyspty)
[<img src="https://img.shields.io/badge/linkedin-%230077B5.svg?&style=for-the-badge&logo=linkedin&logoColor=white" />](https://www.linkedin.com/in/riawe)
[<img src="https://img.shields.io/badge/tiktok-%23000000.svg?&style=for-the-badge&logo=tiktok&logoColor=white" />](https://www.linkedin.com/in/riawe)
[<img src="https://img.shields.io/badge/whatsapp-%23075e54.svg?&style=for-the-badge&logo=whatsapp&logoColor=white" />](https://wa.me/50766168542?text=Hello%20Rangel)
[<img src="https://img.shields.io/badge/hotmail-%23ffbb00.svg?&style=for-the-badge&logo=hotmail&logoColor=white" />](mailto:[REDACTED_EMAIL])
[<img src="https://img.shields.io/badge/gmail-%23D14836.svg?&style=for-the-badge&logo=gmail&logoColor=white" />](mailto:[REDACTED_EMAIL])

</p>

</details>

<details open>
<summary> <b>License<b></summary>
<p align = "center">
No LICENSE file is included in this repository yet, treat the code as all-rights-reserved
until one is added.
</p>
</details>

# Hyperliquid Microstructure

A research pipeline that turns the public level-4 message streams of the Hyperliquid perpetual-futures exchange
into a queryable database of fills, order books and market makers, plus the analysis scripts I use on top of it.

Starting from raw order-status records, book diffs and trades (about 250 GB compressed for one month), the code
recovers timestamps the raw data does not have, replays the full limit order book of BTC, ETH and SOL for every
block of December 2025, attaches the book state and signed price markouts to 22 million fills, scores taker wallets
by how much the price moves against the makers they trade with, builds an event panel of what makers do in the
seconds around a fill, and reconstructs maker-by-maker ledgers of spread revenue, adverse selection, fees and funding.

The repository contains code and documentation only. The data is the open Zenodo release described below; the
databases the code builds are large (about 150 GB) and stay on the machine that builds them.

## Hyperliquid and the data

[Hyperliquid](https://hyperliquid.xyz) is a decentralized exchange for perpetual futures that runs its own
layer-1 blockchain. Unlike most decentralized venues it operates a central limit order book: orders, cancellations
and matches are all executed on-chain by the matching engine, and the entire state of every order is public.
Trading is batched into blocks a fraction of a second apart (about 90 ms between blocks in the sample), traders
are identified by Ethereum-style addresses, and the fee schedule depends on a wallet's trailing 14-day volume with
rebates for the largest liquidity providers. Together this makes it one of the very few venues where the complete
message flow of a large derivatives market can be studied with the identity of every counterparty.

The data is the December 2025 release *An Open Book: Level 4 Order Book Data from the Hyperliquid Exchange*
(Albers, Cucuringu, Howison and Shestopaloff, 2026, Zenodo, [doi:10.5281/zenodo.18184441](https://doi.org/10.5281/zenodo.18184441),
CC BY 4.0). It has three streams:

| stream | what one record is | format | month |
|---|---|---|---|
| order statuses | one event in an order's life (open, filled, canceled, and 15 kinds of rejection) with the block time, user, side, price, sizes, order type and time-in-force | 54-byte packed binary records, one file per coin and hour | Dec 2025, BTC / ETH / SOL, including rejected orders |
| book diffs | one change to the visible book: a new order, a size update after a partial fill, or a removal, with user, order id and price but **no timestamp** | gzip JSON lines, all coins interleaved | Dec 2025, BTC / ETH / SOL |
| trades | one match with price, size, the aggressor side and both counterparties (address, order id, TWAP id, position before the trade) | gzip JSON lines, one file per hour | Oct 2025 – Jan 2026, all 250+ perpetual contracts |

The three streams share the order id, which is what makes the reconstruction below possible.

## What the pipeline builds

Eight stages under [`pipeline/`](pipeline), run in order by [`scripts/run_build.sh`](scripts/run_build.sh):

| stage | script | what it does | output |
|---|---|---|---|
| 1 | `01_parse_book_diffs.py` | parse the diff stream into typed parquet, one file per coin and hour, keeping file order | `derived/diffs/` |
| 2 | `02_parse_order_statuses.py` | decode the binary status records (fixed-point prices, code tables) | `derived/statuses/` |
| 3 | `03_parse_trades.py` | parse the trades of BTC / ETH / SOL with both counterparties | `derived/trades_raw/` |
| 4 | `04_recover_diff_timestamps.py` | give every diff a block time by matching order ids to the status and trade streams; detect re-emitted history after collector restarts | `derived/diffs_ts/` |
| 5 | `05_replay_book.py` | replay the whole month through a numba order-book engine: block-close BBO and depth, and a lifecycle row per order with its queue position at placement | `derived/book/` |
| 6 | `06_build_fills.py` | the fill-level master table: aggressor identification, pre-trade book state, effective half-spread and signed markouts at ten horizons from 0.5 s to 30 min | `derived/fills/` |
| 7 | `07_fetch_funding.py` | hourly funding rates from the public info API | `derived/funding_*.parquet` |
| 8 | `08_user_volume.py` | taker and maker notional per wallet and day across all perps, for fee-tier imputation | `derived/user_volume_*.parquet` |

The result is a layered database: parsed streams, the reconstructed book, fills, and the analysis tables built
from them. [`docs/DATABASE.md`](docs/DATABASE.md) documents every table column by column; the row counts and
sizes of the December 2025 build are at the end of that file. The three tables most analyses start from:

* **`fills/<coin>.parquet`** — one row per fill: who traded with whom, the order each side used, the book just
  before the trade, and how the mid moved afterwards (signed so that a positive markout is a loss for the maker).
* **`book/orders_<coin>.parquet`** — one row per order: when it was placed and removed and why, how much was
  queued ahead of it, and where it sat relative to the spread.
* **`hits/<coin>_*.parquet`** — one row per (maker, aggressive order, block): what the maker's own orders did in
  the seconds before and after being hit, with placebo windows and the maker's next actual quotes.

## The analysis

The scripts under [`analysis/`](analysis) (run by [`scripts/run_analysis.sh`](scripts/run_analysis.sh)) each
answer one question and write CSV tables under `tables/`:

| script | question | tables |
|---|---|---|
| `01_sample_and_validation.py` | What is in the sample, and does the reconstructed book agree with the trades? | `t1_*` |
| `02_toxicity_scores.py` | Is a wallet's tendency to trade ahead of price moves a persistent trait? Scores per formation window, persistence across horizons, thresholds, units and window schemes, placebos, shrinkage, a specification ladder | `t2_*`, `derived/scores/` |
| `03_concentration.py` | How concentrated is adverse selection across takers relative to volume? | `t3_*` |
| `04_incidence.py` | Who bears the cost: within-maker versus between-maker components, clustering choices, a block bootstrap, cross-asset scores, spread compensation | `t4_*` |
| `05_hit_events.py` | Build the event panel of maker behaviour around hits | `derived/hits/` |
| `05b_nonhit_makers.py` | Do makers who were *not* hit react to the same print? | `t5b_*` |
| `06_hit_regressions.py` | Cancellation, re-quoting and market-wide responses by taker score, with placebo windows and within-event differences | `t6_*` |
| `07_maker_ledger.py` | Maker economics: spread revenue, adverse selection, imputed fees and rebates, inventory P&L, funding | `t7_*`, `derived/ledger/` |
| `08_results_digest.py` | Collect every table and note into one Markdown digest | `RESULTS.md` |

Result tables are not part of this repository; running the chain regenerates them.

## Design decisions worth knowing

[`docs/DESIGN_NOTES.md`](docs/DESIGN_NOTES.md) explains each of these in detail.

* **Timestamps for the diff stream are recovered, not observed.** A `new` diff takes the open time of its order
  from the status stream, a cancel takes the cancel time, partial fills take the matching trade, and everything
  else falls back to the previous anchor. Every row records which rule timed it.
* **Collector restarts are handled explicitly.** Re-emitted history is detected as long runs of anchors that run
  backwards in time and is skipped by the replay; duplicate trades are dropped; a gap of more than five seconds
  resets the book and gates the next two minutes. Nothing is imputed: fills in gated windows get null markouts.
* **All times are block times.** "Within 100 ms" means the next block; ordering inside a block is file order.
* **Markouts are block-close to block-close.** The pre-trade mid is the last block strictly before the fill, the
  endpoint is the latest block committed by t + h.
* **Events collapse sweeps.** One aggressive order hitting one maker in one block is one observation, however
  many fills it produced, and the maker's reaction is measured on orders that were already resting before the hit.
* **Fees are imputed** from trailing 14-day volume with the exchange's published tier schedule; positions are
  only observed at fills; wallets are addresses. The limitations section of the design notes lists what the data
  cannot identify.

## Repository map

```text
hyperliquid_microstructure/
├── src/hlmicro/              the library: everything the scripts share
│   ├── config.py             paths (HL_RAW_DIR, HL_WORK_DIR, HL_MONTH), calendar, horizons, window schemes
│   ├── orderstatus.py        54-byte record layout, fixed-point price decoding, code tables
│   ├── timestamps.py         block-time recovery for the diff stream
│   ├── book.py               the numba order-book replay engine
│   ├── markouts.py           pre-trade book state and signed markouts
│   ├── fills.py              loading fills, sample filters, wallet toxicity scores
│   ├── events.py             per-maker scans of cancellations and re-quotes around hits
│   ├── regression.py         fixed-effects OLS with clustered standard errors on large panels
│   └── reporting.py          result tables and notes
├── pipeline/                 stages 1-8 (data build)
├── analysis/                 A1-A8 (research tables)
├── probes/                   exploratory checks that shaped the design (status semantics, a pure-Python book
│                             prototype, book validation, crossed-book diagnosis)
├── scripts/                  run_build.sh, run_analysis.sh, run_smoke_test.sh, run_test_sample.sh
├── tests/                    unit tests on synthetic data for every library module
└── docs/                     DATABASE.md (schema reference), DESIGN_NOTES.md (method and limitations)
```

## Running it

Python 3.11 or newer. The heavy dependencies are polars, pyarrow, numba, duckdb and pyfixest.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
python -m pip install -e ".[test]"
pytest                      # unit tests, synthetic data only, about a minute
```

Download the release from Zenodo and extract it so that `HL_RAW_DIR` contains `order_statuses/`, `book_diffs/`,
`trades/` and `mapdir/` (the Zenodo README gives the `tar` commands). Then:

```bash
export HL_RAW_DIR=/data/hyperliquid/raw       # the extracted release
export HL_WORK_DIR=/data/hyperliquid/work     # where everything below is written
bash scripts/run_smoke_test.sh                # stages 1-6 on three hours of one coin: about a minute
bash scripts/run_build.sh                     # the full month, three coins
bash scripts/run_test_sample.sh               # a 20-day one-coin sample + the analysis chain on it (--test)
bash scripts/run_analysis.sh                  # the analysis chain on the full build
```

Every script is also a command-line tool with `--help`; the pipeline stages skip outputs that already exist, so an
interrupted build resumes where it stopped. On a laptop with 16 cores and 32 GB of RAM the full December 2025
build takes a few hours (the book replays are 7-14 minutes per coin; parsing dominates), and the analysis chain
another few hours, the event panels being the slowest part. Disk: about 150 GB for a complete build.

Using the library directly:

```python
import polars as pl
from hlmicro.fills import load_fills, add_time_cols, clean_mask, wallet_scores

fills = add_time_cols(load_fills(["SOL"]))
clean = fills.filter(clean_mask(fills) & pl.col("mid_pre").is_not_null())
scores = wallet_scores(clean.filter(pl.col("day") <= 15), ["10s", "60s"])   # one row per taker wallet
```

## Tests

`pytest` checks each library module on hand-built inputs: the 54-byte record decoding round-trips; the timestamp
recovery times anchors, trades, fallbacks, demoted anchors and re-emitted runs as documented; the book engine
tracks BBO, depth, queue position, partial fills, duplicates, gap resets and gating; markouts use the right blocks
and return nulls when they should; the event scans count cancels, placebos and re-quotes correctly; wallet scores
agree with hand calculations for order, equal-weighted and fill units; and the fixed-effects estimator reproduces
dummy-variable OLS and pyfixest's clustered standard errors. The refactored stages were also checked against a
full earlier build: on a three-hour slice they reproduce every parsed row, every block of the replayed book and
every fill column exactly.

## Roadmap

* Multi-month builds once further months of the diff and status streams are released.
* Queue-position and fill-probability models from the order lifecycle table.
* A small dashboard over the fill table (spread, depth and toxicity by hour of day).

## Citation

If you use the data, cite the release:

> Albers, J., Cucuringu, M., Howison, S. and Shestopaloff, A. Y. (2026). *An Open Book: Level 4 Order Book Data
> from the Hyperliquid Exchange.* Zenodo. doi:10.5281/zenodo.18184441.

## License

MIT, see [LICENSE](LICENSE). The data release is CC BY 4.0 and is not redistributed here.

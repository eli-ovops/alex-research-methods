<div align="center">

<h1>Polymarket Data</h1>

<h3>Complete Data Infrastructure for Polymarket — Fetch, Process, Analyze</h3>

<p style="max-width: 750px; margin: 0 auto;">
A comprehensive dataset of 6.6 billion on-chain trading records from Polymarket, processed into multiple analysis-ready formats. Features cleaned data, unified token perspectives, and user-level transformations — ready for market research, behavioral studies, and quantitative analysis.
</p>

<p>
<b>Zhengjie Wang</b><sup>1,2</sup>, <b>Leiyu Chao</b><sup>1,3</sup>, <b>Yu Bao</b><sup>1,4</sup>, <b>Lian Cheng</b><sup>1,3</sup>, <b>Jianhan Liao</b><sup>1,5</sup>, <b>Yikang Li</b><sup>1,†</sup>
</p>

<p>
<sup>1</sup>Shanghai Innovation Institute &nbsp;&nbsp; <sup>2</sup>Westlake University &nbsp;&nbsp; <sup>3</sup>Shanghai Jiao Tong University
<br>
<sup>4</sup>Harbin Institute of Technology &nbsp;&nbsp; <sup>5</sup>Fudan University
</p>

<p>
<sup>†</sup>Corresponding author
</p>

</div>

<p align="center">
  <a href="https://huggingface.co/datasets/SII-WANGZJ/Polymarket_data">
    <img src="https://img.shields.io/badge/Hugging%20Face-Dataset-yellow.svg" alt="HuggingFace Dataset"/>
  </a>
  <a href="https://github.com/SII-WANGZJ/Polymarket_data">
    <img src="https://img.shields.io/badge/GitHub-Code-black.svg?logo=github" alt="GitHub Repository"/>
  </a>
  <a href="https://github.com/SII-WANGZJ/Polymarket_data/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License"/>
  </a>
  <a href="#data-quality">
    <img src="https://img.shields.io/badge/Data-Verified-green.svg" alt="Data Quality"/>
  </a>
</p>

---

## TL;DR

We provide **279GB of historical on-chain trading data** from Polymarket, containing **6.6 billion records** across 4.0M markets, from the CLOB launch (2022-11-21) through **2026-10-04 23:59:59 UTC**. The dataset is directly fetched from Polygon blockchain, verified against on-chain data, and ready for analysis. Perfect for market research, behavioral studies, data science projects, and academic research.

## What's New (2026-10-05 release)

- **Data through 2026-10-04 23:59:59 UTC** — all five files share the same cutoff, so they join consistently.
- **Polymarket V2 exchanges included** — the two V2 exchange contracts (live since 2026-04-28) are now covered alongside the original two. Earlier snapshots were missing the sell-side V2 fills in `trades` / `quant` / `users`; these are now included.
- **Re-verified against the chain** — fills that the live collector had silently missed (blocks for which an RPC node returned incomplete logs) were re-fetched from Polygon RPC.
- **Deduplicated** — every table has exactly one row per fill (the previous `users.parquet` contained ~0.16% duplicate rows).
- **Consistent formats** — `transaction_hash` / `order_hash` are now always `0x`-prefixed lowercase hex (older rows previously lacked the `0x`), and wallet addresses are lowercase. If you join on hashes, re-download all files from this release together.
- **`markets.parquet`** has one row per market (latest metadata) and now includes `neg_risk`.

## Highlights

- **Complete CLOB Trading History**: Every `OrderFilled` event from Polymarket's CLOB exchange contracts (two V1 contracts, plus two V2 contracts since April 2026), from the CLOB launch (first record 2022-11-21 UTC) onward. Note: this covers the on-chain CLOB era only — earlier FPMM/AMM-era trades (2020–Nov 2022), which predate these contracts, are not included.

- **Multiple Analysis Perspectives**: 5 structured datasets at different abstraction levels — raw blockchain events, processed trades with market linkage, market metadata, and derived quantitative views — serving diverse research needs.

- **Production Ready**: Clean, validated data with proper schema documentation. All trades are verified against blockchain RPC, with market metadata linked and ready to use.

- **Open Source Pipeline**: Fully reproducible data collection process. Our open-source tools allow you to verify, update, or extend the dataset independently.

## Dataset Overview

| File | Size | Records | Description |
|------|------|---------|-------------|
| `trades.parquet` | 45.8GB | 1,266,885,846 | **Recommended.** Processed trades with market metadata linkage |
| `orderfilled.parquet` | 127.2GB | 2,026,704,633 | Raw blockchain events from OrderFilled logs |
| `markets.parquet` | 0.5GB | 4,049,900 | Market information and metadata |
| `quant.parquet` | 44.7GB | 1,266,885,845 | Derived: unified YES perspective (for quant research) |
| `users.parquet` | 60.8GB | 2,026,673,731 | Derived: every fill keyed by the trader's wallet address (for user-level research) |

**Total**: 279GB, 6.6 billion records

## Use Cases

### Market Research & Analysis
- Study prediction market dynamics and price discovery mechanisms
- Analyze market efficiency and information aggregation
- Research crowd wisdom and forecasting accuracy

### Behavioral Studies
- Track individual user trading patterns and decision-making
- Study market participant behavior under different conditions
- Analyze risk preferences and trading strategies

### Data Science & Machine Learning
- Train models for price prediction and market forecasting
- Feature engineering for time-series analysis
- Develop algorithms for market analysis

### Academic Research
- Economics and finance research on prediction markets
- Social science studies on collective intelligence
- Computer science research on blockchain data analysis

## Quick Start

### Installation

```bash
# Using pip
pip install pandas pyarrow

# Optional: for faster parquet reading
pip install fastparquet
```

### Load Data with Pandas

```python
import pandas as pd

# Load trades (recommended for most users)
df = pd.read_parquet('trades.parquet')
print(f"Total trades: {len(df):,}")

# Load market metadata
markets = pd.read_parquet('markets.parquet')
print(f"Total markets: {len(markets):,}")
```

### Load from HuggingFace Datasets

```python
from datasets import load_dataset

# Load trades
dataset = load_dataset(
    "SII-WANGZJ/Polymarket_data",
    data_files="trades.parquet"
)

# Load multiple files
dataset = load_dataset(
    "SII-WANGZJ/Polymarket_data",
    data_files=["trades.parquet", "markets.parquet"]
)
```

### Download Specific Files

```bash
# Download using HuggingFace CLI
pip install huggingface_hub

# Download a specific file
hf download SII-WANGZJ/Polymarket_data quant.parquet --repo-type dataset

# Download all files
hf download SII-WANGZJ/Polymarket_data --repo-type dataset
```

## File Selection Guide

> **We recommend `trades.parquet` as the primary dataset for most use cases.** It preserves all original trade semantics with market metadata linked, requiring no assumptions about token normalization.

`quant.parquet` and `users.parquet` are derived datasets designed for our internal research. `quant.parquet` normalizes every trade to the YES (token1) perspective; `users.parquet` re-keys every fill by the trader's wallet address. These transformations may not suit every analysis scenario — detailed logic is documented below.

## Data Structure

### trades.parquet - Processed Trades (Recommended)

Trade records with market metadata linkage, one row per matched fill. Prices and directions keep their original on-chain meaning (no YES/NO normalization). When a taker order is matched, the exchange emits one `OrderFilled` event per maker order plus one summary event for the taker order (whose `taker` is the exchange contract itself); the summary events are omitted here so that each fill is counted once. They are kept in `orderfilled.parquet` and `users.parquet`.

**Best for:** General-purpose analysis, custom research, building your own pipelines.

**Schema:**
| Column | Type | Description |
|--------|------|-------------|
| `timestamp` | uint64 | Unix timestamp (seconds, UTC) |
| `block_number` | uint64 | Polygon block number |
| `transaction_hash` | string | Transaction hash (`0x`-prefixed lowercase hex) |
| `log_index` | uint32 | Log index within the transaction |
| `contract` | string | Exchange contract: `CTF_EXCHANGE`, `NEGRISK_CTF_EXCHANGE` (V1), `CTF_EXCHANGE_V2`, `NEGRISK_CTF_EXCHANGE_V2` |
| `market_id` | string | Polymarket market identifier |
| `condition_id` | string | CTF condition ID |
| `event_id` | string | Event group identifier |
| `maker` | string | Maker wallet address (lowercase) |
| `taker` | string | Taker wallet address (lowercase) |
| `price` | float64 | Trade price (0–1) |
| `usd_amount` | float64 | USD (USDC) value of the trade |
| `token_amount` | float64 | Number of outcome tokens traded |
| `maker_direction` | string | Maker's direction: `BUY` or `SELL` |
| `taker_direction` | string | Taker's direction: `BUY` or `SELL` |
| `nonusdc_side` | string | Which outcome token was traded: `token1` (YES) or `token2` (NO) |
| `asset_id` | string | The non-USDC token's asset ID |

### orderfilled.parquet - Raw Blockchain Events

Unprocessed `OrderFilled` events directly from Polygon blockchain logs. No decoding, no market linkage — pure on-chain data.

**Best for:** Blockchain research, data verification, building custom processing pipelines from scratch.

**Schema:**
| Column | Type | Description |
|--------|------|-------------|
| `timestamp` | uint64 | Unix timestamp (seconds, UTC) |
| `block_number` | uint64 | Polygon block number |
| `transaction_hash` | string | Transaction hash (`0x`-prefixed lowercase hex) |
| `log_index` | uint32 | Log index within the transaction |
| `contract` | string | Exchange contract: `CTF_EXCHANGE`, `NEGRISK_CTF_EXCHANGE` (V1), `CTF_EXCHANGE_V2`, `NEGRISK_CTF_EXCHANGE_V2` |
| `order_hash` | string | Order hash (`0x`-prefixed lowercase hex) |
| `maker` | string | Maker wallet address (lowercase) |
| `taker` | string | Taker wallet address (lowercase; the exchange contract for a taker-order summary event) |
| `maker_asset_id` | string | Asset ID the maker gave (`0` = collateral, i.e. USDC) |
| `taker_asset_id` | string | Asset ID the taker gave (`0` = collateral, i.e. USDC) |
| `maker_amount_filled` | fixed_size_binary[32] | Amount filled for maker (uint256, 32-byte little-endian) |
| `taker_amount_filled` | fixed_size_binary[32] | Amount filled for taker (uint256, 32-byte little-endian) |
| `maker_fee` | fixed_size_binary[32] | Maker fee (uint256, 32-byte little-endian) |
| `taker_fee` | fixed_size_binary[32] | Taker fee (uint256, 32-byte little-endian) |
| `protocol_fee` | fixed_size_binary[32] | Protocol fee (uint256, 32-byte little-endian) |

> Note: Amount and fee fields are raw uint256 values from the blockchain, stored as 32-byte little-endian binary because they exceed the standard integer range. Both USDC and outcome tokens use 6 decimals:
>
> ```python
> df['maker_amount'] = df['maker_amount_filled'].map(lambda b: int.from_bytes(b, 'little') / 1e6)
> ```

### markets.parquet - Market Metadata

Market information, outcome token details, and event grouping. One row per market, with its latest metadata.

**Best for:** Linking trades to market context, filtering by market attributes, understanding market outcomes.

**Schema:**
| Column | Type | Description |
|--------|------|-------------|
| `id` | string | Market identifier (join key with `market_id` in other tables) |
| `question` | string | Market question text |
| `slug` | string | URL slug |
| `condition_id` | string | CTF condition ID |
| `token1` | string | Asset ID of outcome token 1 (YES) |
| `token2` | string | Asset ID of outcome token 2 (NO) |
| `answer1` | string | Label for token1 outcome (e.g., "Yes") |
| `answer2` | string | Label for token2 outcome (e.g., "No") |
| `closed` | uint8 | 0 = active, 1 = settled |
| `active` | uint8 | Whether the market is currently active |
| `archived` | uint8 | Whether the market is archived |
| `outcome_prices` | string | JSON array of final prices, e.g. `["0.99", "0.01"]` means answer1 won |
| `volume` | float64 | Total traded volume (USD) |
| `event_id` | string | Parent event identifier |
| `event_slug` | string | Parent event URL slug |
| `event_title` | string | Parent event title |
| `created_at` | timestamp (ms, UTC) | Market creation time |
| `end_date` | timestamp (ms, UTC) | Market end / resolution time |
| `updated_at` | timestamp (ms, UTC) | Last metadata update time |
| `neg_risk` | uint8 | 1 = negative-risk (multi-outcome) market, traded on the NegRisk exchange |

### quant.parquet - Unified YES Perspective (For Quantitative Research)

> **Note:** This is a derived dataset built for our own quantitative research. It normalizes all trades to the YES (token1) perspective: for trades originally on token2 (NO), the price is converted to `1 - price`, and the buy/sell direction is flipped. Trades whose taker is an exchange contract are filtered out, keeping only real user trades. **If you need the original trade semantics, use `trades.parquet` instead.**

**Schema:**
| Column | Type | Description |
|--------|------|-------------|
| `timestamp` | uint64 | Unix timestamp (seconds, UTC) |
| `block_number` | uint64 | Polygon block number |
| `transaction_hash` | string | Transaction hash (`0x`-prefixed lowercase hex) |
| `log_index` | uint32 | Log index within the transaction |
| `market_id` | string | Market identifier |
| `condition_id` | string | CTF condition ID |
| `event_id` | string | Event group identifier |
| `price` | float64 | YES token price (0–1). For original token2 trades: `1 - original_price` |
| `usd_amount` | float64 | USD value |
| `token_amount` | float64 | Token amount |
| `side` | string | `BUY` or `SELL` (from YES token perspective). For original token2 trades: direction is flipped |
| `maker` | string | Maker wallet address (lowercase) |
| `taker` | string | Taker wallet address (lowercase) |

### users.parquet - User-Level Behavior Data (For User-Level Research)

> **Note:** This is a derived dataset built for our own research. It contains one record for **every** `OrderFilled` event (including the taker-order summary events that `trades.parquet` omits), keyed by the wallet whose order was filled. Because both sides of every match appear, each trader's full activity can be aggregated by `address`. Prices and amounts are the raw values of the traded outcome token (no YES/NO normalization; amounts are positive and `direction` gives buy/sell). **If you need one row per trade, use `trades.parquet` instead.**

**Schema:**
| Column | Type | Description |
|--------|------|-------------|
| `timestamp` | uint64 | Unix timestamp (seconds, UTC) |
| `block_number` | uint64 | Polygon block number |
| `transaction_hash` | string | Transaction hash (`0x`-prefixed lowercase hex) |
| `log_index` | uint32 | Log index within the transaction |
| `address` | string | Wallet whose order was filled (the event's maker, lowercase) |
| `role` | string | `taker` if this was the taker order of the match (event's taker is the exchange contract), otherwise `maker` |
| `direction` | string | `BUY` or `SELL` of the outcome token, from this wallet's perspective |
| `usd_amount` | float64 | USD (USDC) value |
| `token_amount` | float64 | Number of outcome tokens (positive) |
| `price` | float64 | Price of the traded outcome token (0–1) |
| `market_id` | string | Market identifier |
| `condition_id` | string | CTF condition ID |
| `event_id` | string | Event group identifier |
| `nonusdc_side` | string | Which outcome token was traded: `token1` (YES) or `token2` (NO) |

## Example Analysis

### 1. Calculate Market Statistics

```python
import pandas as pd

df = pd.read_parquet('trades.parquet')

# Market-level statistics
market_stats = df.groupby('market_id').agg({
    'usd_amount': ['sum', 'mean'],     # Total volume and average trade size
    'price': ['mean', 'std', 'min', 'max'],  # Price statistics
    'transaction_hash': 'count'         # Number of trades
}).round(4)

print(market_stats.head())
```

### 2. Track Price Evolution

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_parquet('trades.parquet')
df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')

# Select a specific market
market_id = 'your-market-id'
market_data = df[df['market_id'] == market_id].sort_values('timestamp')

# Plot price over time
plt.figure(figsize=(12, 6))
plt.plot(market_data['datetime'], market_data['price'])
plt.title(f'Price Evolution - Market {market_id}')
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()
```

### 3. Market Volume Analysis

```python
import pandas as pd

df = pd.read_parquet('trades.parquet')
markets = pd.read_parquet('markets.parquet')

# Join with market metadata (markets uses 'id', trades uses 'market_id')
df = df.merge(markets[['id', 'question']], left_on='market_id', right_on='id', how='left')

# Top markets by volume
top_markets = df.groupby(['market_id', 'question']).agg({
    'usd_amount': 'sum'
}).sort_values('usd_amount', ascending=False).head(20)

print(top_markets)
```

### 4. Analyze by Token Side

```python
import pandas as pd

df = pd.read_parquet('trades.parquet')

# Compare YES vs NO token trading activity
side_stats = df.groupby('nonusdc_side').agg({
    'usd_amount': ['sum', 'mean'],
    'transaction_hash': 'count'
})
print(side_stats)

# Filter for only YES token trades on a specific market
market_id = 'your-market-id'
yes_trades = df[(df['market_id'] == market_id) & (df['nonusdc_side'] == 'token1')]
print(f"YES trades: {len(yes_trades):,}")
```

## Data Processing Pipeline

```
Polygon Blockchain (RPC)                 Polymarket Gamma API
         ↓                                        ↓
  orderfilled.parquet (Raw events)         markets.parquet
         ↓  (+ market linkage)
         ├─→ trades.parquet (one row per matched fill)
         │        └─→ quant.parquet (unified YES perspective)
         │
         └─→ users.parquet (every fill, keyed by trader address)
```

**Key Transformations:**

1. **trades.parquet**:
   - Decode each `OrderFilled` event into price, USD amount, token amount and directions
   - Link the outcome token to its market via `markets.parquet`
   - Omit the taker-order summary events (taker = exchange contract) so each fill is counted once
   - Result: 1,266,885,846 records

2. **quant.parquet**:
   - Filter out trades whose taker is an exchange contract (keep only user trades)
   - Normalize all trades to YES token perspective
   - Preserve maker/taker information
   - Result: 1,266,885,845 records

3. **users.parquet**:
   - One record per `OrderFilled` event, keyed by the wallet whose order was filled
   - `role` marks whether that order was the maker or the taker side of the match
   - Result: 2,026,673,731 records

Fills whose outcome token does not belong to any market listed by the Polymarket Gamma API (about 31K `OrderFilled` events, i.e. ~18K trades, over the whole history) remain in `orderfilled.parquet` only.

## Documentation

- **[DATA_DESCRIPTION.md](DATA_DESCRIPTION.md)** - Comprehensive documentation
  - Detailed schema for all 5 files
  - Data cleaning and transformation process
  - Usage examples and best practices
  - Comparison between different files

## Data Quality

- **Complete History**: All `OrderFilled` events from the 4 official exchange contracts below
- **Blockchain Verified**: Blocks with no recorded fills were re-checked against Polygon RPC and any missing fills re-fetched; random block-level audits (on-chain logs vs. dataset, event by event) found no missing or extra events
- **No Duplicates**: Exactly one row per fill in every table (checked across the full history by transaction hash + log index)
- **Consistent Cutoff**: All files end at 2026-10-04 23:59:59 UTC
- **Reproducible Pipeline**: Fully open-source collection process; refreshes are run on an as-needed basis rather than a fixed schedule

**Contracts Tracked:**
- CTF Exchange (V1): `0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E`
- NegRisk CTF Exchange (V1): `0xC5d563A36AE78145C45a50134d48A1215220f80a`
- CTF Exchange (V2, since 2026-04-28): `0xE111180000d2663C0091e4f400237545B87B996B`
- NegRisk CTF Exchange (V2, since 2026-04-28): `0xe2222d279d744050d28e00520010520000310F59`

## Collection Tools

Data collected using our open-source toolkit: [polymarket-data](https://github.com/SII-WANGZJ/Polymarket_data)

**Features:**
- Direct blockchain RPC integration
- Efficient batch processing
- Automatic retry and error handling
- Data validation and verification

## Dataset Statistics

**Last Updated**: 2026-10-05

**Coverage**:
- Time Range: CLOB launch (2022-11-21 UTC) to 2026-10-04 23:59:59 UTC (CLOB `OrderFilled` events only; pre-CLOB FPMM/AMM-era trades not included)
- Total Markets: 4,049,900
- Total Trades: 1.27 billion (processed), 2.03 billion (raw OrderFilled)

**Data Freshness**: Refreshed on an as-needed basis (no fixed schedule); the pipeline is open-source, so you can also update or extend the dataset yourself

## Contributing

We welcome contributions to improve the dataset and tools:

1. **Report Issues**: Found data quality issues? [Open an issue](https://github.com/SII-WANGZJ/Polymarket_data/issues)
2. **Suggest Features**: Ideas for new data transformations? Let us know!
3. **Contribute Code**: Improve our collection pipeline via pull requests

## License

MIT License - Free for commercial and research use.

See [LICENSE](LICENSE) file for details.

## Contact & Support

- **Email**: [[REDACTED_EMAIL]](mailto:[REDACTED_EMAIL])
- **Issues**: [GitHub Issues](https://github.com/SII-WANGZJ/Polymarket_data/issues)
- **Dataset**: [HuggingFace](https://huggingface.co/datasets/SII-WANGZJ/Polymarket_data)
- **Code**: [GitHub Repository](https://github.com/SII-WANGZJ/Polymarket_data)

## Citation

If you use this dataset in your research, please cite:

```bibtex
@misc{polymarket_data_2026,
  title={Polymarket Data: Complete Data Infrastructure for Polymarket},
  author={Wang, Zhengjie and Chao, Leiyu and Bao, Yu and Cheng, Lian and Liao, Jianhan and Li, Yikang},
  year={2026},
  howpublished={\url{https://huggingface.co/datasets/SII-WANGZJ/Polymarket_data}},
  note={A comprehensive dataset and toolkit for Polymarket prediction markets}
}
```

## Acknowledgments

- **Polymarket** for building the leading prediction market platform
- **Polygon** for providing reliable blockchain infrastructure
- **HuggingFace** for hosting and distributing large datasets
- The open-source community for tools and libraries

---

<div align="center">

**Built for the research and data science community**

[HuggingFace](https://huggingface.co/datasets/SII-WANGZJ/Polymarket_data) • [GitHub](https://github.com/SII-WANGZJ/Polymarket_data) • [Documentation](DATA_DESCRIPTION.md)

</div>

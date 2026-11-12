---
pretty_name: Polymarket CLOB V2 OrderFilled (Polygon)
language:
  - en
  - zh
tags:
  - polymarket
  - polygon
  - blockchain
  - prediction-markets
  - parquet
size_categories:
  - 100M<n<1B
configs:
  - config_name: default
    data_files:
      - split: train
        path: "event_month=*/*.parquet"
---

# Polymarket CLOB V2 OrderFilled (Polygon)

[中文说明](README.zh-CN.md) · [CLOB V1 dataset](https://huggingface.co/datasets/wzsg/polymarket-orderfilled-v1)

[![Live analytics](https://img.shields.io/badge/analytics-live%20dashboard-FF4B4B?logo=huggingface&logoColor=white)](https://huggingface.co/spaces/wzsg/polymarket-orderfilled-analytics) [![Open-source project](https://img.shields.io/badge/source-GitHub-181717?logo=github&logoColor=white)](https://github.com/wzsg/polymarket-analytics)
![Polygon](https://img.shields.io/badge/chain-Polygon%20%7C%20137-8247E5?logo=polygon&logoColor=white) ![Format](https://img.shields.io/badge/format-Parquet%20%7C%20ZSTD-50ABF1) ![Updates](https://img.shields.io/badge/updates-daily-brightgreen)

This dataset contains `OrderFilled` events emitted by Polymarket CLOB V2 Exchange contracts on Polygon mainnet. It covers both standard CTF markets and Neg Risk markets, follows the V2 event ABI, and is stored as ZSTD-compressed Parquet files partitioned by UTC month.

Explore V1 and V2 activity, trends, and summary metrics in the interactive [live analytics dashboard](https://huggingface.co/spaces/wzsg/polymarket-orderfilled-analytics).

The collection, processing, and dashboard source code is available in the [open-source GitHub repository](https://github.com/wzsg/polymarket-analytics).

<!-- BEGIN AUTO-GENERATED V2 STATS -->
## Updated daily

> The incremental collector runs at 00:00 UTC and atomically publishes new Parquet shards together with the latest dataset state.

| Item | Value |
|---|---:|
| Last updated (UTC) | 2026-08-04 00:10:40 UTC |
| Total rows | 575,630,861 |
| Standard CTF Exchange V2 rows | 478,388,740 |
| Neg Risk CTF Exchange V2 rows | 97,242,121 |
| BUY (`side = 0`) rows | 494,473,779 |
| SELL (`side = 1`) rows | 81,157,082 |
| UTC event time range | 2026-04-28 11:04:48 UTC to 2026-08-03 23:47:33 UTC |
| Polygon event block range | 86,127,122 to 91,397,218 |
| Latest event month | 2026-08 |
| Latest safely scanned block | 91,397,218 |
| Safe block hash | `0x4def3112eb625eb1596b9ea089107d8e8361ef5b43a841f67874c21d54875745` |
| Next block to scan | 91,397,219 |
| Confirmation depth | 512 blocks |
| Monthly partitions | 5 |
| Parquet files | 123 |
| Parquet data size | 33,617,734,086 bytes (31.31 GiB) |
<!-- END AUTO-GENERATED V2 STATS -->

Polymarket moved its production trading system from CLOB V1 to CLOB V2 on April 28, 2026. V2 introduced new Exchange contracts, pUSD collateral, a new order format, and a new on-chain fee model. See the [official CLOB V2 migration guide](https://docs.polymarket.com/v2-migration) for details.

## Related dataset

- [Polymarket CLOB V1 OrderFilled](https://huggingface.co/datasets/wzsg/polymarket-orderfilled-v1): V1 historical events from November 21, 2022 through April 28, 2026.
- This dataset: V2 events beginning on April 28, 2026.

The V1 and V2 `OrderFilled` ABIs differ. Do not concatenate identically named fields across versions without first normalizing asset and side semantics.

## V2 contracts and event

| Contract | Polygon address | Dataset `contract` value |
|---|---|---|
| CTF Exchange V2 | `0xE111180000d2663C0091e4f400237545B87B996B` | `CTF_EXCHANGE_V2` |
| Neg Risk CTF Exchange V2 | `0xe2222d279d744050d28e00520010520000310F59` | `NEGRISK_CTF_EXCHANGE_V2` |

V2 `OrderFilled` event:

```solidity
event OrderFilled(
    bytes32 indexed orderHash,
    address indexed maker,
    address indexed taker,
    Side side,
    uint256 tokenId,
    uint256 makerAmountFilled,
    uint256 takerAmountFilled,
    uint256 fee,
    bytes32 builder,
    bytes32 metadata
);
```

`Side` is ABI-encoded as `uint8`. Event `topic0`:

```text
0xd543adfd945773f1a62f74f0ee55a5e3b9b1a28262980ba90b1a89f2ea84d8ee
```

The field layout is defined in the [official Polymarket CTF Exchange V2 source](https://github.com/Polymarket/ctf-exchange-v2/blob/main/src/exchange/mixins/Events.sol).

## Schema

Each Parquet file contains 16 physical columns:

| Column | Parquet / DuckDB type | Description |
|---|---|---|
| `timestamp` | `uint64` / `UBIGINT` | Unix timestamp in seconds |
| `datetime` | `timestamp[us, UTC]` | Event time in UTC |
| `block_number` | `uint64` / `UBIGINT` | Polygon block number |
| `transaction_hash` | `string` | Transaction hash |
| `log_index` | `uint32` / `UINTEGER` | Log index |
| `contract` | `string` | `CTF_EXCHANGE_V2` or `NEGRISK_CTF_EXCHANGE_V2` |
| `order_hash` | `string` | V2 order hash |
| `maker` | `string` | Maker of the filled order |
| `taker` | `string` | Counterparty or Exchange execution address |
| `side` | `uint8` / `UTINYINT` | Maker order side: `0 = BUY`, `1 = SELL` |
| `token_id` | `string` | Conditional Token ERC-1155 token ID |
| `maker_amount_filled` | `string` | Raw integer amount paid by the maker |
| `taker_amount_filled` | `string` | Raw integer amount received by the maker |
| `fee` | `string` | Raw V2 `OrderFilled.fee` value |
| `builder` | `string` | Canonical `bytes32`: `0x` plus 64 lowercase hex digits |
| `metadata` | `string` | Canonical `bytes32`: `0x` plus 64 lowercase hex digits |

`event_month` is a Hive partition column derived from the directory name and is not stored inside each Parquet file:

```text
event_month=2026-07/data_0.parquet
```

## Side, asset, and price semantics

`side` is the side of the maker order:

- `side = 0` (BUY): the maker pays pUSD collateral and receives the outcome token identified by `token_id`.
- `side = 1` (SELL): the maker pays the outcome token identified by `token_id` and receives pUSD collateral.

Amounts and fees are stored as decimal strings to preserve full `uint256` precision. pUSD and outcome token amounts normally use six raw decimal places.

Execution price can be calculated as:

```sql
CASE
    WHEN side = 0 THEN
        TRY_CAST(maker_amount_filled AS DECIMAL(38, 0)) /
        NULLIF(TRY_CAST(taker_amount_filled AS DECIMAL(38, 0)), 0)
    WHEN side = 1 THEN
        TRY_CAST(taker_amount_filled AS DECIMAL(38, 0)) /
        NULLIF(TRY_CAST(maker_amount_filled AS DECIMAL(38, 0)), 0)
END AS price
```

Do not assume that `taker` is always an end user. One matching transaction can contain multiple maker fills, and mint, merge, and direct transfer paths may expose different counterparties.

## Partition layout

```text
.
├── event_month=2026-04/
│   ├── data_0.parquet
│   └── ...
├── event_month=2026-05/
├── event_month=2026-06/
├── event_month=2026-07/
├── manifest.json
├── README.md
└── README.en.md
```

Storage settings:

- Parquet
- ZSTD compression
- UTC monthly partitions
- 1,048,576-row row groups
- Historical export shards target about 1 GiB; block-bounded incremental shards can be smaller

## DuckDB example

```python
import duckdb

dataset = "event_month=*/*.parquet"

con = duckdb.connect()
con.execute("SET TimeZone='UTC'")

result = con.sql(f"""
    SELECT
        event_month,
        contract,
        side,
        count(*) AS fills,
        min(datetime) AS first_fill,
        max(datetime) AS last_fill
    FROM read_parquet(
        '{dataset}',
        hive_partitioning=true,
        union_by_name=false
    )
    WHERE event_month = '2026-07'
    GROUP BY event_month, contract, side
    ORDER BY contract, side
""")

print(result)
```

The dataset is large and continues to grow. See the live status section above for its current size. Filter by `event_month`, `datetime`, `block_number`, or `contract` as early as possible.

## V2 filtering and field processing

The dataset was selected from a combined V1/V2 archive using:

```sql
WHERE contract IN ('CTF_EXCHANGE_V2', 'NEGRISK_CTF_EXCHANGE_V2')
```

The combined source archive retained V1-style physical column names. They were losslessly mapped to the V2 ABI during export:

| Combined source column | V2 dataset column |
|---|---|
| `maker_asset_id` | `side` |
| `taker_asset_id` | `token_id` |
| `maker_amount_filled` | `maker_amount_filled` |
| `taker_amount_filled` | `taker_amount_filled` |
| `maker_fee` | `fee` |
| `taker_fee` | `builder` |
| `protocol_fee` | `metadata` |

In the source archive, `builder` and `metadata` were stored as unsigned decimal representations of their corresponding 32-byte values. They were losslessly restored to canonical 66-character `bytes32` hex strings during export. No other normalization was applied to hashes, address casing, amounts, or timestamps.

## Validation

The initial historical export and every incremental release validate that:

- V2 ABI-mapped fields contain no NULL values
- `builder` and `metadata` match `0x[0-9a-f]{64}`
- every new Parquet shard uses the same 16-column schema and ZSTD compression
- contract, side, row, block, and timestamp totals agree with cumulative shard statistics
- the stored safe block hash can be verified again through Polygon RPC

The initial export also compared BUY, SELL, non-zero `builder`, and non-zero `metadata` samples against raw Polygon RPC logs. Indexed fields and all seven non-indexed data words matched the dataset mapping.

Current cumulative statistics are in the live status section above. See `manifest.json` for per-month row counts, time ranges, block ranges, file counts, and byte sizes.

## Incremental updates

The incremental collector scans confirmed Polygon blocks every day and adds schema-compatible immutable Parquet shards under the corresponding `event_month=YYYY-MM` directory. Existing shards are never overwritten. Events are deduplicated with a key containing `transaction_hash`, `log_index`, and `contract`.

Parquet shards, `manifest.json`, `collector_state.json`, and the live status blocks in both Data Cards are published in the same atomic Hub commit. The current progress and latest event boundary are recorded in the live status section and those two JSON files.

## Known limitations

1. The current UTC month partition is still growing and does not represent a complete calendar month.
2. `timestamp` and `datetime` are preserved from the upstream archive. This dataset does not re-fetch every block timestamp.
3. The dataset contains on-chain fills only. It does not include market questions, outcome labels, categories, or Gamma API metadata. Join `token_id` to Polymarket market/token metadata when those fields are needed.
4. A single on-chain matching transaction can emit multiple `OrderFilled` events. A row should not automatically be interpreted as an independent user-to-user trade.
5. Polygon can experience short chain reorganizations. Incremental collectors should overlap the confirmed boundary by a small number of blocks and deduplicate by event key.
6. The data is derived from public blockchain events. This dataset description does not grant additional rights to underlying contract source code, platform trademarks, or third-party material. Users are responsible for determining applicable terms.

## Sources

- [Polymarket contract documentation](https://docs.polymarket.com/resources/contracts)
- [Polymarket CLOB V2 migration guide](https://docs.polymarket.com/v2-migration)
- [Polymarket CTF Exchange V2 source](https://github.com/Polymarket/ctf-exchange-v2)
- Polygon Mainnet, chain ID `137`

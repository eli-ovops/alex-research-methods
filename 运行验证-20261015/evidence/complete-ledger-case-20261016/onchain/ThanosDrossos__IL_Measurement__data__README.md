# Datasets

Every file here is produced by `notebooks/IL_Data_Extraction.ipynb`. They are
committed so the notebook reproduces the thesis figures without network access —
the subgraph endpoints the extraction code was written against have since been
retired (see the main [README](../README.md#re-fetching-data-from-the-graph)).

## Files

| File | Produced by | Contents |
| --- | --- | --- |
| `pool_id_database.pkl` | Part 1.1, `Extract_data` | `dict[pool_name, Series[int]]` — Uniswap v3 position IDs per pool |
| `pool_id_database.csv` | Part 1.1, `Extract_data` | The same mapping as CSV, one row per pool, IDs comma-joined |
| `pool_data_TVL.pkl` | Part 1.1, `get_pool_TVL` | `dict[pool_name, DataFrame]` — daily pool aggregates: `date`, `txCount`, `tvlUSD`, `token0Price`, `token1Price`, `feesUSD`, `volumeUSD` |
| `full/<pool>_normalized_dataframes.pkl` | Part 1.2, `process_and_normalize_data` | Per-pool position results, one row per burn event, 50 columns |
| `full/<pool>_normalized_data.csv` | Part 1.2, `process_and_normalize_data` | The same table as CSV |
| `sample/…` | Same, run over `head(100)` of each pool's IDs | 100 positions per pool — a fast smoke-test subset |

`full/` holds 30,058 observations, `sample/` holds 1,121. Both carry the same
50 columns; only the row coverage differs.

### CSV format

The CSVs are written for a German Excel locale — **semicolon separator, comma
decimal mark**. Read them with:

```python
pd.read_csv(path, sep=";", decimal=",")
```

The `.pkl` files hold the same tables with dtypes intact and need no such
handling; the notebook itself always reads the pickles.

## Row semantics

One row is **one burn event**, not one position. A position closed in several
steps contributes one row per step, which is why the observation count (30,058)
exceeds the number of position IDs queried (26,279). Mint and pure-collect
events are consumed during the calculation and dropped from the output; fees
from a collect that is not paired with a burn are carried forward onto the next
burn.

Liquidity is matched from each burn back to the earlier mints it withdraws from,
first-in-first-out. Value, holding period and mint prices are then computed over
that matched liquidity, weighted by the amount assigned to each mint.

## Columns

### Identity

| Column | Meaning |
| --- | --- |
| `id` | Event identifier, `<position_id>#<block>` |
| `owner` | Address that owns the position |
| `pool_id` | Pool address |
| `position_id` | Uniswap v3 position (NFT) ID |
| `position_token0.id`, `position_token1.id` | Token addresses |
| `event_timestamp` | Unix timestamp of the burn |

### Position-level fields (as reported by the subgraph)

| Column | Meaning |
| --- | --- |
| `position_amountDepositedUSD` | Total deposited over the position's life |
| `position_amountWithdrawnUSD` | Total withdrawn |
| `position_amountCollectedUSD` | Total collected (withdrawals plus fees) |
| `position_liquidity` | Liquidity remaining on the position |
| `position_withdrawnToken0`, `position_withdrawnToken1` | Totals withdrawn per token |

### The burn event

| Column | Meaning |
| --- | --- |
| `event_amount` | Liquidity burned |
| `event_amount0`, `event_amount1` | Token amounts withdrawn |
| `event_amountUSD` | USD value withdrawn — the position size used throughout Part 2 |
| `price_0`, `price_1` | Token USD prices at the hour of the burn |
| `event_fees0`, `event_fees1`, `event_feesUSD` | Fees attributed to this burn, from its paired collect event plus any carried-forward collects |
| `relativeBurnSize` | `event_amountUSD / position_amountWithdrawnUSD` — this burn's share of the position |
| `weightedDurationSeconds` | Liquidity-weighted holding period of the burned liquidity |

### Valuation

| Column | Meaning |
| --- | --- |
| `initialValue` | Matched liquidity valued at the prices when it was minted |
| `HODLValue` | The same token amounts valued at burn prices — the buy-and-hold counterfactual |
| `finalValue` | `price_0 · event_amount0 + price_1 · event_amount1` |
| `average_mint_price0`, `average_mint_price1` | Liquidity-weighted mint prices |
| `priceQuotient0` | `(price_0/price_1) / (average_mint_price0/average_mint_price1)` — change in the token0/token1 ratio |
| `priceQuotient1` | The same, inverted |
| `price0_lower`, `price0_upper`, `price1_lower`, `price1_upper` | Position range bounds, converted from ticks. Note the inversion: `tickLower` yields `price0_lower` **and** `price1_upper` |

### Impermanent loss and return

All IL figures are negative for a loss.

| Column | Definition |
| --- | --- |
| `lossVersusHODLExact` | `event_amountUSD − HODLValue` — the headline IL in USD |
| `lossVersusHODLEst` | `finalValue − HODLValue`, using reconstructed rather than reported USD |
| `lossVersusHODLFees` | `lossVersusHODLExact + event_feesUSD` — IL net of fees |
| `IL_initial` | `lossVersusHODLExact / initialValue` |
| `IL_final` | `lossVersusHODLExact / event_amountUSD` |
| `IL_fees` | `lossVersusHODLFees / event_amountUSD` |
| `IL_annualized` | `(IL_final + 1)^(1 / years) − 1`, years from `weightedDurationSeconds` |
| `IL_formula` | Closed-form Uniswap v3 IL from the range bounds and the price ratio change, taking token1 as reference. Where the closed form returns a positive value (IL numerically at zero) it falls back to `IL_final` |
| `IL_formula_annualized` | `(IL_formula + 1)^(1 / years) − 1` |
| `absolute_return` | `position_amountCollectedUSD − position_amountDepositedUSD` |
| `relative_return` | `absolute_return / position_amountDepositedUSD` |

### Position-level aggregates

These four are computed per position and then repeated on every row belonging to
that position, so **do not sum them across rows**:

| Column | Definition |
| --- | --- |
| `IL_total_abs` | Sum of `lossVersusHODLExact` over the position |
| `IL_total_rel` | `IL_total_abs / position_amountDepositedUSD` |
| `IL_annualized_total` | Sum of `relativeBurnSize · IL_annualized` |
| `IL_formula_total` | Sum of `relativeBurnSize · IL_formula` |

### Derived in Part 2, not stored

The visualisation section adds three more columns after loading:

| Column | Definition |
| --- | --- |
| `relativeFees` | `event_feesUSD / event_amountUSD` |
| `percentageReturn` | `relativeFees + IL_formula` — net outcome for the liquidity provider |
| `durationDays` | `weightedDurationSeconds / 3600 / 24` |

It also builds `combined_df` (all pools, filtered to `-1 ≤ IL_final ≤ 0` and
non-zero position size) and `risky_combined_df` (the same, excluding the two
stablecoin-only pools).

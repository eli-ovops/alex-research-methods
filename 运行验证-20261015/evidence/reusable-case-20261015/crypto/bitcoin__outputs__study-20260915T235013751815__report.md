# BTC/USD backtesting report

**Decision: reanalysis — not fresh holdout evidence**

- Previously accessed holdout; descriptive results only

These are historical simulations, not evidence of live execution or guaranteed returns.

## Data review

Reviewed no-candle intervals: no fills, carried valuation only. Within-gap prices and drawdowns remain unobserved.

No executions during missing intervals. Last observed price is used only for valuation; intragap prices and drawdowns remain unknown. Positive research gates remain inconclusive until independently valued.

## Walk

| Scenario | CAGR | Max drawdown | End equity | Fees |
|---|---:|---:|---:|---:|
| base | 1.24% | 13.83% | $10,374.89 | $618.73 |
| base_40_60 | 10.01% | 42.05% | $13,309.52 | $161.17 |
| base_btc | 12.12% | 77.84% | $14,092.39 | $267.07 |
| base_cash | 0.00% | 0.00% | $10,000.00 | $0.00 |
| base_matched | 1.24% | 7.02% | $10,377.83 | $23.10 |
| cash4 | 5.01% | 12.33% | $11,578.63 | $662.44 |
| cash4_40_60 | 12.61% | 40.57% | $14,277.68 | $166.57 |
| cash4_btc | 12.12% | 77.84% | $14,092.43 | $267.07 |
| cash4_cash | 4.00% | 0.00% | $11,247.73 | $0.00 |
| cash4_matched | 5.07% | 4.36% | $11,598.03 | $24.43 |
| cost20 | -1.28% | 15.62% | $9,621.99 | $591.21 |
| cost50 | -5.30% | 23.75% | $8,492.65 | $549.92 |
| stress | 0.43% | 10.35% | $10,128.86 | $436.45 |
| tax35 | 0.33% | 13.81% | $10,100.22 | $611.14 |

![walk equity and drawdown](walk.png)

### Conditional uncertainty

```json
{
  "annualized_mean_daily_excess": 0.003064190660492274,
  "block_days": 30,
  "high": 0.0692511027285316,
  "low": -0.06214599188382067,
  "note": "Conditional circular block-bootstrap interval, not proof of persistence.",
  "samples": 2000,
  "seed": 42
}
```


Reviewed no-candle intervals: no fills, carried valuation only. Within-gap prices and drawdowns remain unobserved.

## Holdout

| Scenario | CAGR | Max drawdown | End equity | Fees |
|---|---:|---:|---:|---:|
| base | -1.61% | 12.05% | $9,681.30 | $608.03 |
| base_40_60 | 18.44% | 15.57% | $14,031.58 | $70.50 |
| base_btc | 42.98% | 36.10% | $20,452.82 | $121.98 |
| base_cash | 0.00% | 0.00% | $10,000.00 | $0.00 |
| base_matched | 3.29% | 2.84% | $10,668.86 | $12.86 |
| cash4 | 1.98% | 8.73% | $10,401.04 | $622.75 |
| cash4_40_60 | 21.23% | 15.31% | $14,700.04 | $71.98 |
| cash4_btc | 42.98% | 36.10% | $20,452.83 | $121.98 |
| cash4_cash | 4.00% | 0.00% | $10,816.58 | $0.00 |
| cash4_matched | 7.12% | 2.39% | $11,474.87 | $13.24 |
| cost20 | -3.97% | 15.35% | $9,221.70 | $598.18 |
| cost50 | -7.62% | 21.19% | $8,533.46 | $582.59 |
| stress | -2.20% | 8.41% | $9,563.65 | $387.39 |
| tax35 | -1.80% | 12.02% | $9,643.79 | $604.49 |

![holdout equity and drawdown](holdout.png)

### Conditional uncertainty

```json
{
  "annualized_mean_daily_excess": -0.04671147821159316,
  "block_days": 30,
  "high": 0.035578585077596474,
  "low": -0.12173990930030329,
  "note": "Conditional circular block-bootstrap interval, not proof of persistence.",
  "samples": 2000,
  "seed": 42
}
```

## Final training candidates (not holdout results)

| Candidate | CAGR | Drawdown | Turnover |
|---|---:|---:|---:|
| donchian-10d-2.0x | 5.72% | 11.48% | 20.0x |
| donchian-10d-2.5x | 4.17% | 14.19% | 15.7x |
| donchian-10d-3.0x | 3.07% | 15.77% | 13.3x |
| donchian-20d-2.0x | 3.51% | 13.99% | 15.9x |
| donchian-20d-2.5x | 2.35% | 16.94% | 12.0x |
| donchian-20d-3.0x | 0.54% | 20.00% | 9.7x |
| donchian-50d-2.0x | 2.78% | 9.79% | 13.6x |
| donchian-50d-2.5x | 2.99% | 11.82% | 10.1x |
| donchian-50d-3.0x | 1.86% | 13.83% | 7.9x |

## Interpretation and limitations

- One-minute candles cannot establish queue position or every intrabar price path. Limit fills require penetration; adverse ambiguous exits take precedence.
- Fold boundaries use explicitly labeled hypothetical liquidation at the final close with fees and slippage; those settlements bypass the per-minute volume cap.
- 40% is a buy-time deployment limit; price appreciation may raise exposure. The 15% drawdown criterion is an evaluation gate, not a stop guarantee.
- Tax sensitivity reserves 35% of positive annual FIFO realized gains, without loss credits. It is strategy-only and is not tax advice.
- Cash interest and execution costs are scenario assumptions, not historical account rates.
- Parameter stability is checked in final training data; holdout parameters are never retuned.
- At least two independent market venues and small live execution tests would strengthen a positive conclusion.

## Reproduction

Saved research directory: `work/runs/study-20260915T235013751815`. Config, environment, data hashes, selection, and source-code hash are recorded in its manifests.

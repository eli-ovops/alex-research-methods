# BTC/USD backtesting report

**Decision: not supported**

- walk-forward: nonpositive return
- walk-forward: fails exposure benchmark
- walk-forward: fails 40/60 Calmar benchmark
- walk-forward: fails cost stress
- walk-forward: fails $20/month operating cost
- holdout: nonpositive return
- holdout: fails exposure benchmark
- holdout: fails 40/60 Calmar benchmark
- holdout: fails cost stress
- holdout: fails $20/month operating cost
- Fewer than two walk-forward years beat the matched benchmark

Reviewed same-source no-candle intervals; independent within-gap prices remain unobserved.

These are historical simulations, not evidence of live execution or guaranteed returns.

## Data review

Reviewed no-candle intervals: no fills, carried valuation only. Within-gap prices and drawdowns remain unobserved.

No executions during missing intervals. Last observed price is used only for valuation; intragap prices and drawdowns remain unknown. Positive research gates remain inconclusive until independently valued.

## Walk

| Scenario | CAGR | Max drawdown | End equity | Fees |
|---|---:|---:|---:|---:|
| base | 0.00% | 0.00% | $10,000.00 | $0.00 |
| base_40_60 | 10.01% | 42.05% | $13,309.52 | $161.17 |
| base_btc | 12.12% | 77.84% | $14,092.39 | $267.07 |
| base_cash | 0.00% | 0.00% | $10,000.00 | $0.00 |
| base_matched | 0.00% | 0.00% | $10,000.00 | $0.00 |
| cash4 | 4.00% | 0.00% | $11,247.73 | $0.00 |
| cash4_40_60 | 12.61% | 40.57% | $14,277.68 | $166.57 |
| cash4_btc | 12.12% | 77.84% | $14,092.43 | $267.07 |
| cash4_cash | 4.00% | 0.00% | $11,247.73 | $0.00 |
| cash4_matched | 4.00% | 0.00% | $11,247.73 | $0.00 |
| cost20 | -2.46% | 7.20% | $9,280.00 | $0.00 |
| cost50 | -6.41% | 18.00% | $8,200.00 | $0.00 |
| stress | 0.00% | 0.00% | $10,000.00 | $0.00 |
| tax35 | 0.00% | 0.00% | $10,000.00 | $0.00 |

![walk equity and drawdown](walk.png)

### Conditional uncertainty

```json
{
  "annualized_mean_daily_excess": 0.0,
  "block_days": 30,
  "high": 0.0,
  "low": 0.0,
  "note": "Conditional circular block-bootstrap interval, not proof of persistence.",
  "samples": 2000,
  "seed": 42
}
```


Reviewed no-candle intervals: no fills, carried valuation only. Within-gap prices and drawdowns remain unobserved.

## Holdout

| Scenario | CAGR | Max drawdown | End equity | Fees |
|---|---:|---:|---:|---:|
| base | 0.00% | 0.00% | $10,000.00 | $0.00 |
| base_40_60 | 18.44% | 15.57% | $14,031.58 | $70.50 |
| base_btc | 42.98% | 36.10% | $20,452.82 | $121.98 |
| base_cash | 0.00% | 0.00% | $10,000.00 | $0.00 |
| base_matched | 0.00% | 0.00% | $10,000.00 | $0.00 |
| cash4 | 4.00% | 0.00% | $10,816.58 | $0.00 |
| cash4_40_60 | 21.23% | 15.31% | $14,700.04 | $71.98 |
| cash4_btc | 42.98% | 36.10% | $20,452.83 | $121.98 |
| cash4_cash | 4.00% | 0.00% | $10,816.58 | $0.00 |
| cash4_matched | 4.00% | 0.00% | $10,816.58 | $0.00 |
| cost20 | -2.43% | 4.80% | $9,520.00 | $0.00 |
| cost50 | -6.19% | 12.00% | $8,800.00 | $0.00 |
| stress | 0.00% | 0.00% | $10,000.00 | $0.00 |
| tax35 | 0.00% | 0.00% | $10,000.00 | $0.00 |

![holdout equity and drawdown](holdout.png)

### Conditional uncertainty

```json
{
  "annualized_mean_daily_excess": 0.0,
  "block_days": 30,
  "high": 0.0,
  "low": 0.0,
  "note": "Conditional circular block-bootstrap interval, not proof of persistence.",
  "samples": 2000,
  "seed": 42
}
```

## Final training candidates (not holdout results)

| Candidate | CAGR | Drawdown | Turnover |
|---|---:|---:|---:|
| fixed-0.02 | -30.59% | 68.19% | 65.9x |
| fixed-0.03 | -16.48% | 46.31% | 44.3x |
| fixed-0.04 | -7.45% | 28.38% | 30.0x |
| adaptive-0.02 | -21.53% | 54.47% | 62.1x |
| adaptive-0.03 | -12.86% | 39.21% | 41.7x |
| adaptive-0.04 | -6.87% | 26.97% | 27.7x |
| filtered-0.02 | -13.08% | 38.14% | 49.3x |
| filtered-0.03 | -6.86% | 25.51% | 31.9x |
| filtered-0.04 | -3.64% | 18.02% | 19.9x |

## Interpretation and limitations

- One-minute candles cannot establish queue position or every intrabar price path. Limit fills require penetration; adverse ambiguous exits take precedence.
- Fold boundaries use explicitly labeled hypothetical liquidation at the final close with fees and slippage; those settlements bypass the per-minute volume cap.
- 40% is a buy-time deployment limit; price appreciation may raise exposure. The 15% drawdown criterion is an evaluation gate, not a stop guarantee.
- Tax sensitivity reserves 35% of positive annual FIFO realized gains, without loss credits. It is strategy-only and is not tax advice.
- Cash interest and execution costs are scenario assumptions, not historical account rates.
- Parameter stability is checked in final training data; holdout parameters are never retuned.
- At least two independent market venues and small live execution tests would strengthen a positive conclusion.

## Reproduction

Saved research directory: `work/runs/study-20260915T195232860878`. Config, environment, data hashes, selection, and source-code hash are recorded in its manifests.

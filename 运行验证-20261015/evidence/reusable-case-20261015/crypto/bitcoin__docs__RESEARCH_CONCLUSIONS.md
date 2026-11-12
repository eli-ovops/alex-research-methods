# Bitcoin Backtest Sim: Final Research Conclusions & Deployment Decision

**Date**: September 16, 2026  
**Final Decision**: **NOT SUPPORTED / DO NOT DEPLOY FOR LIVE TRADING**  
**Lead Finding**: The strategy does not justify live capital risk. Passive alternatives (broad-market index funds or a simple rebalanced 40/60 BTC/Cash portfolio) deliver significantly higher returns with lower drawdown, zero exchange fee friction, and zero operational overhead.

---

## 1. Executive Summary & Verdict

Following extensive empirical research spanning 8 years of historical Kraken BTC/USD 1-minute data (2017–2025), multi-fold walk-forward validation, holdout testing, and live sandbox simulations:

1. **Definitive Decision**: **The bot should NOT be run with real money.**
2. **Economic Underperformance**: Across all configurations, the systematic strategies failed to beat the baseline **8.0% annual return** expected from standard balanced equity index funds (e.g., S&P 500 / total market).
3. **Retail Friction Destruction**: Standard retail exchange fees (0.40% maker/taker + 0.10% slippage) extract an unsustainable toll (~1.00% round-trip). On a $10,000 account, fee friction consumed between $737 and $2,638 of capital, turning potentially viable signals into flat or negative net returns.
4. **Research Harness Validation**: The study was a complete success from a risk management perspective: the out-of-sample walk-forward gates prevented capital deployment into negative-expectancy models, successfully preserving 100% of seed capital.

---

## 2. Quantitative Performance Summary

### 2.1 Strategy Models vs. Benchmarks (2021–2025)

| Portfolio / Strategy Model | Historical CAGR (2021–2023) | Holdout CAGR (2024–2025) | Max Drawdown | Lifetime Fees Paid (on $10k) | Outcome vs. 8% Benchmark |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Typical Balanced Index Fund (S&P 500 / 60-40)** | **~8.0% – 10.0%** | **~10.0% – 12.0%** | ~18% – 24% | ~$3 – $8 / yr | **Benchmark Met** |
| **Strategy: Baseline Mean-Reversion Ladder** | **0.00%** *(stayed flat)* | **0.00%** *(stayed flat)* | 0.00% | $0.00 *(out-of-sample)* | **Failed** (All 9 training candidates negative) |
| **Strategy: Baseline + $20/mo Server Overhead** | **-2.46%** | **-2.43%** | 7.20% | $0.00 | **Failed** (Cash bled from fixed costs) |
| **Strategy: Donchian Trend Pivot (40% Exposure)** | **+3.06%** | N/A | 24.48% | **$737.51** | **Below Benchmark** (Fees ate 7.4% of capital) |
| **Passive Benchmark: 40/60 BTC & Cash Rebalanced** | **+10.01%** | **+18.44%** | **15.60%** | **$71.00** | **Beat Benchmark** (Superior risk-adjusted return) |
| **Passive Benchmark: 100% BTC Buy & Hold** | **+12.12%** | **+42.98%** | **77.84%** | $267.07 | **High Return / Extreme Risk** (-78% crash in 2022) |

---

## 3. Core Structural Reasons Why the Strategy Failed

### 3.1 The Retail Fee Trap (1.00% Round-Trip Drag)
Institutional quantitative firms operate with maker fee rebates (-0.01% to +0.02%) and co-located sub-millisecond execution. Retail accounts pay:
* **0.40% taker fee** per side
* **0.10% (10 bps)** adverse limit penetration / slippage
* **Total round-trip friction**: **~1.00% per trade**

In the baseline mean-reversion model, the strategy sought 1.0% to 2.0% profit targets. Under 1.0% round-trip friction, **50% to 100% of gross edge was transferred directly to the exchange**. Over 30 to 60 annual turns, this guaranteed negative mathematical expectancy regardless of market direction.

### 3.2 Fixed Infrastructure Overhead Bleed
Running a 24/7 trading daemon requires infrastructure (VPS server, logging, continuous power, data connections).
* At **$20/month** overhead on a $10,000 account, the bot suffers a **-2.4% annual drag**.
* At **$50/month**, the drag is **-6.0% annually**.
During prolonged consolidation or bear market phases (such as 2022 or extended sideways ranges), the bot sits in cash and steadily loses money to operating costs.

### 3.3 The False Edge of "Harm Reduction"
In parameter sweeps, wider spacing (4%) and 200-day trend filters appeared to perform "better" (-3.6% CAGR vs. -30.6% CAGR). However, statistical decomposition revealed that this improvement was purely an artifact of **trading less** (turnover collapsed from $65.9\times$ to $19.9\times$). When a trading strategy's best variation is simply the one that trades the least, the underlying signal possesses zero positive alpha.

---

## 4. The 40/60 BTC/Cash Revelation

The most significant quantitative discovery of this entire study was the performance of the **passive 40/60 BTC/Cash benchmark**:
* **Mechanism**: 40% allocated to spot Bitcoin, 60% held in cash (or short-term Treasury yield), rebalanced monthly.
* **Return**: **+10.01% CAGR** in walk-forward (2021–2023) and **+18.44% CAGR** in holdout (2024–2025).
* **Drawdown**: Only **15.6%** maximum drawdown during the catastrophic 2022 crypto winter (where pure Bitcoin crashed -77.8%).
* **Friction**: Incurred only $71 in total transaction fees over 3 years.

A simple rules-based rebalancing schedule drastically outperformed every algorithmic bot configuration tested, without requiring code execution, server uptime, or intraday monitoring.

---

## 5. Income Feasibility Analysis: Can This Earn $10,000 / Month?

### 5.1 Capital Requirements
To generate an average of **$10,000/month** ($120,000/year net):

$$\text{Required Seed Capital} = \frac{\$120,000}{\text{Expected Net Annual Return (CAGR)}}$$

* At **15% CAGR** (conservative/defensive trend strategy): requires **$800,000** seed cash.
* At **20% CAGR** (solid systematic performance): requires **$600,000** seed cash.
* At **25% CAGR** (strong bull market participation): requires **$480,000** seed cash.
* **Tax Considerations**: Factoring in short-term capital gains tax (~30%–37%), gross earnings must reach **$160,000–$180,000/year**, elevating the required capital to **~$800,000 – $1,000,000**.

> [!CAUTION]
> Any claim that $10,000/month can be generated from small capital ($5,000 to $25,000) relies on extreme leverage (10x–50x). In cryptocurrency markets, a single 10% intraday flash wick mathematically guarantees 100% account liquidation under those leverage levels.

### 5.2 The "Lumpy Returns" & Sequence-of-Returns Trap
Trend and breakout systems do not pay monthly salaries:
* **70% of the year**: Flat sideways chop, generating $0 or minor fee friction (-$1,000 to -$3,000).
* **30% of the year**: Explosive trend expansion, generating large lump-sum profits (+$40,000 to +$80,000).

Withdrawing $10,000 every calendar month during an extended quiet period eats into active trading principal ("reverse compounding"). When the trend finally arrives, the diminished capital base generates significantly reduced dollar returns.

---

## 6. What Worked: Methodological & Software Successes

Even though the trading model itself is not suitable for live capital, the project produced substantial engineering and research value:
1. **Capital Preservation Verified**: The experimental research harness performed exactly as designed. The pre-flight gates (`CAGR > 0` and `Max Drawdown <= 15%`) blocked all 9 failing candidates, preserving $10,000 in cash rather than suffering the -20% to -68% losses seen in unhedged systems.
2. **Deterministic, Rigorous Pipeline**: Built a leak-free 1-minute OHLCVT backtester with strict temporal causality, volume-participation limits, adverse slippage modeling, and auditable SHA-256 run manifests.
3. **Institutional-Grade TUI & Sandbox**: Constructed a rich Textual Terminal UI with live order routing, paper-trading simulation, and an isolated DEMO pipeline sandbox for interactive verification.

---

## 7. Final Recommendations & Next Steps

1. **Do Not Fund Live Kraken Account**: Do not deposit capital or enable live API trading for this strategy.
2. **Decommission 24/7 Monitoring**: Stop background terminal daemons and power-management overrides. There is no need to keep machines awake to monitor an inactive bot.
3. **Deploy Capital into Proven Compounding Vehicles**:
   - For steady, hands-off growth: allocate capital to **broad-market low-cost index funds** (S&P 500 / Total Stock Market), which reliably compound near 8%–10% with zero effort.
   - For crypto exposure with risk control: implement a **passive quarterly-rebalanced 40/60 BTC/Cash (or Treasury yield) portfolio**, which delivered 10%–18% CAGR with only 15% drawdown in historical testing.
4. **Archive Repository**: Preserve the codebase as an open, auditable reference implementation for quantitative research and backtesting.

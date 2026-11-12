# Transaction Cost Sensitivity Analysis

**Research ID:** RQ-001  
**Strategy Family:** TREND_PULLBACK  
**Execution Timeframe:** 30m  
**Market:** Cryptocurrency Futures  
**Historical Period:** 15 January 2024 – 28 September 2026  
**Symbol Universe:** 50 trading pairs

## 1. Research Objective

The objective of this study is to evaluate the sensitivity of a systematic trading strategy to transaction fees and execution slippage.

A strategy may demonstrate positive performance under ideal execution assumptions but experience significant deterioration when realistic trading costs are incorporated.

This research investigates how different combinations of transaction fees and slippage affect net profitability, win rate, profit factor and realised drawdown.

## 2. Research Questions

1. How significantly do transaction fees affect net strategy profitability?
2. How does increasing slippage affect trading performance?
3. How do combined transaction fees and slippage influence net P&L?
4. At what tested execution-cost scenario does the strategy lose profitability?
5. How does execution-cost deterioration affect profit factor and realised drawdown?

## 3. Experimental Configuration

Seven backtesting scenarios were evaluated.

| Scenario | Fee per Side | Slippage per Side |
|---|---:|---:|
| A | 0.00% | 0.00% |
| B | 0.00% | 0.05% |
| C | 0.05% | 0.00% |
| D | 0.05% | 0.05% |
| E | 0.05% | 0.10% |
| F | 0.05% | 0.15% |
| G | 0.05% | 0.20% |

The scenarios were generated using the same strategy family, execution timeframe, historical period and symbol universe.

The fee and slippage assumptions are applied per side, covering entry and exit execution.

## 4. Performance Evaluation Metrics

**Net P&L**

Total reported profit or loss after transaction costs.

**Win Rate**

Percentage of closed trades with positive net P&L.

**Profit Factor**

Sum of positive net P&L divided by the absolute sum of negative net P&L.

**Maximum Realised Drawdown**

Maximum peak-to-trough decline calculated from cumulative net P&L ordered by exit timestamp.

The drawdown reported in this study is an absolute P&L value, not a percentage of initial account equity.

## 5. Experimental Results

| Fee | Slippage | Net P&L | Win Rate | Profit Factor | Max Drawdown |
|---:|---:|---:|---:|---:|---:|
| 0.00% | 0.00% | +454.06 | 49.05% | 1.276 | -67.39 |
| 0.00% | 0.05% | +341.70 | 48.37% | 1.210 | -77.36 |
| 0.05% | 0.00% | +348.41 | 49.05% | 1.214 | -73.72 |
| 0.05% | 0.05% | +247.89 | 48.42% | 1.154 | -79.30 |
| 0.05% | 0.10% | +111.31 | 47.08% | 1.070 | -86.21 |
| 0.05% | 0.15% | -5.98 | 45.82% | 0.996 | -95.50 |
| 0.05% | 0.20% | -81.48 | 45.14% | 0.947 | -112.03 |

## 6. Key Research Findings

### 6.1 Transaction Fee Sensitivity

Introducing a 0.05% transaction fee per side reduced reported net P&L from +454.06 to +348.41 under the zero-slippage scenario.

This represents an approximately 23.27% reduction compared with the zero-cost baseline.

Transaction fees therefore have a material impact on the strategy's profitability.

### 6.2 Slippage Sensitivity

Under zero-fee assumptions, increasing slippage to 0.05% per side reduced net P&L from +454.06 to +341.70.

This represents an approximately 24.75% reduction.

The findings indicate that execution-price deterioration can materially weaken the strategy even without transaction fees.

### 6.3 Combined Execution Cost Impact

With transaction fees fixed at 0.05% per side, increasing slippage produced the following net P&L:

- 0.05% slippage: +247.89
- 0.10% slippage: +111.31
- 0.15% slippage: -5.98
- 0.20% slippage: -81.48

The strategy crossed from positive to negative net profitability between the tested 0.10% and 0.15% slippage scenarios.

This is the principal finding of the experiment.

### 6.4 Profitability Quality

Profit factor declined from 1.276 under zero-cost assumptions to 0.947 under the highest tested execution-cost scenario.

A profit factor below 1 indicates that aggregate losing net P&L exceeds aggregate winning net P&L.

This confirms that the deterioration is not limited to the final net P&L figure.

### 6.5 Drawdown Deterioration

Maximum realised drawdown increased from -67.39 to -112.03 across the zero-cost and highest-cost scenarios.

The strategy therefore experiences greater realised peak-to-trough losses under higher execution-cost assumptions.

## 7. Research Interpretation

The results demonstrate that execution costs are a material determinant of the TREND_PULLBACK 30m strategy's performance.

The strategy produces positive reported net P&L under lower-cost assumptions, but its profitability deteriorates significantly as slippage increases.

Under the highest tested slippage assumption, the strategy produces negative net P&L and a profit factor below 1.

These findings support incorporating execution-cost sensitivity into strategy validation, strategy selection and portfolio-level risk assessment.

## 8. Research Limitations

1. The experiments are independently generated backtest scenarios. The trade outcomes and execution paths may differ across scenarios.
2. The results therefore represent full scenario performance rather than a pure fixed-trade cost deduction.
3. The CSV logs do not provide enough information to independently reconstruct every gross fill and verify all slippage calculations.
4. Maximum drawdown is calculated from realised closed-trade P&L, not mark-to-market equity.
5. The exact initial capital and P&L currency are not explicitly established by the exported files.
6. The tested slippage assumptions are experimental scenarios and should not be interpreted as measured live-market execution costs.

## 9. Conclusion

This research demonstrates that transaction costs and execution slippage can materially affect the profitability of systematic trading strategies.

For the TREND_PULLBACK 30m strategy, reported net P&L declined from +454.06 under zero-cost assumptions to -81.48 under the highest tested execution-cost scenario.

The profitability crossover occurred between the tested 0.10% and 0.15% slippage assumptions when transaction fees were fixed at 0.05% per side.

The study highlights the importance of execution-aware backtesting and realistic transaction-cost modelling when evaluating systematic trading strategies.

## 10. Future Research

- Perform fixed-trade replay to isolate direct fee and slippage deductions.
- Compare transaction-cost sensitivity across strategy families.
- Investigate cost sensitivity across execution timeframes.
- Evaluate execution costs by symbol and liquidity characteristics.
- Compare backtest slippage assumptions against paper-trading execution.
- Investigate cost-aware trade selection and minimum cost-coverage requirements.

**Research Status:** Scenario comparison completed. Fixed-trade replay and live-execution validation remain future research activities.
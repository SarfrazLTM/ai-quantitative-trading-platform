# Multi-Strategy Correlation Analysis

## 1. Research Overview

This research investigates the relationship between three algorithmic trading strategy families:

- **TREND_PULLBACK**
- **TREND_CONTINUATION**
- **BREAKOUT_CONTINUATION**

The objective is to understand whether these strategy families provide genuine portfolio diversification or whether they generate overlapping market exposure and similar return patterns.

Having multiple strategy families does not automatically mean a portfolio is diversified. Strategies may use different entry conditions but still participate in the same market movements, trade the same symbols, and experience drawdowns during similar periods.

This study evaluates their return correlation, trade overlap, drawdown behaviour, and combined portfolio performance.

## 2. Research Objectives

The research focuses on four primary questions:

1. **Return Correlation:** Do the strategy families generate profits and losses during similar market periods?
2. **Trade Overlap:** How frequently do different families hold positions in the same symbol at overlapping times?
3. **Drawdown Overlap:** Do the strategies experience losses and drawdowns simultaneously?
4. **Portfolio Diversification:** Does combining the strategy families improve portfolio performance and reduce risk?

## 3. Dataset Description

The analysis uses independently generated backtest results for each strategy family.

| Parameter | Configuration |
|---|---|
| Strategy families | 3 |
| Execution timeframe | 30 minutes |
| Trading universe | 50 symbols |
| Historical period | 15 January 2024 – 29 September 2026 |
| Initial capital | Same across all three runs |
| Base risk per trade | 0.25% |
| Trading fee per side | 0.05% |
| Slippage per side | 0.05% |

### Dataset summary

| Strategy family | Number of trades |
|---|---:|
| TREND_PULLBACK | 1,328 |
| TREND_CONTINUATION | 1,167 |
| BREAKOUT_CONTINUATION | 2,085 |
| **Total** | **4,580** |

The original CSV files are stored under `data/raw/`.

## 4. Research Methodology

The research is divided into four analytical stages.

### 4.1 Return Correlation Analysis

Measure the relationship between strategy-family returns using aligned daily, weekly, and monthly return series.

Planned measurements:

- Pearson correlation
- Spearman rank correlation
- Daily return correlation matrix
- Weekly return correlation matrix
- Monthly return correlation matrix

The return series must use a consistent capital and return calculation methodology. Realised P&L grouped by exit date will be treated as a diagnostic measure, not as a substitute for mark-to-market portfolio returns.

### 4.2 Trade Overlap Analysis

Identify trades that overlap between strategy families.

The analysis considers:

- Same-symbol overlapping positions
- Same-direction overlapping positions
- Opposite-direction overlapping positions
- Overlapping trade duration
- Frequency of simultaneous exposure

This helps identify whether separate strategy families are independently identifying opportunities or repeatedly participating in the same market movement.

### 4.3 Drawdown Analysis

Evaluate the timing and severity of drawdowns across strategy families.

Planned measurements:

- Maximum drawdown
- Drawdown duration
- Drawdown recovery period
- Simultaneous drawdown periods
- Drawdown overlap between strategy pairs

### 4.4 Portfolio Diversification Analysis

Evaluate individual and combined strategy portfolios.

Portfolio configurations:

1. TREND_PULLBACK
2. TREND_CONTINUATION
3. BREAKOUT_CONTINUATION
4. TREND_PULLBACK + TREND_CONTINUATION
5. TREND_PULLBACK + BREAKOUT_CONTINUATION
6. TREND_CONTINUATION + BREAKOUT_CONTINUATION
7. All three strategy families combined

Combined portfolios will be evaluated under a consistent capital and risk-allocation policy.

The simulation will account for simultaneous positions and available capital rather than simply adding independent strategy P&L figures.

## 5. Preliminary Findings

The initial dataset inspection produced the following observations.

### 5.1 Individual Strategy Performance

| Metric | TREND_PULLBACK | TREND_CONTINUATION | BREAKOUT_CONTINUATION |
|---|---:|---:|---:|
| Net P&L | +320.20 | +132.37 | +520.40 |
| Win rate | 48.27% | 46.44% | 48.68% |
| Profit factor | 1.148 | 1.074 | 1.144 |
| Maximum realised drawdown | -95.98 | -119.54 | -118.44 |
| Total trades | 1,328 | 1,167 | 2,085 |

*Note: Maximum realised drawdown is calculated from chronological cumulative realised net P&L. It is expressed in P&L units, not as a percentage of account equity.*

### 5.2 Preliminary Daily P&L Correlation

| Strategy pair | Pearson correlation |
|---|---:|
| TREND_PULLBACK vs TREND_CONTINUATION | 0.649 |
| TREND_PULLBACK vs BREAKOUT_CONTINUATION | 0.664 |
| TREND_CONTINUATION vs BREAKOUT_CONTINUATION | 0.671 |

These preliminary values use daily realised P&L grouped by exit date, with zero assigned on days without recorded exits.

They are diagnostic results only. They do not represent final mark-to-market return correlations.

### 5.3 Preliminary Trade Overlap

| Strategy pair | Overlapping trade pairs | Same direction | Opposite direction |
|---|---:|---:|---:|
| TREND_PULLBACK vs TREND_CONTINUATION | 251 | 250 | 1 |
| TREND_PULLBACK vs BREAKOUT_CONTINUATION | 360 | 359 | 1 |
| TREND_CONTINUATION vs BREAKOUT_CONTINUATION | 415 | 415 | 0 |

The initial overlap analysis indicates that most simultaneous same-symbol positions are in the same direction.

This may indicate concentration of directional exposure across strategy families.

## 6. Key Research Questions

The final analysis will determine:

- Which strategy pair has the strongest return correlation?
- Which family contributes the most independent return behaviour?
- Do the strategies experience drawdowns at the same time?
- Does combining two or three families improve portfolio drawdown?
- Does the combined portfolio improve risk-adjusted performance?
- Are there strategy combinations that create excessive directional concentration?

## 7. Expected Deliverables

The research will generate the following outputs:

| Output | Description |
|---|---|
| `correlation_matrix.csv` | Daily, weekly and monthly correlation results |
| `strategy_comparison.csv` | Individual and combined portfolio performance |
| `pnl_correlation_heatmap.png` | Visual representation of return correlations |
| `drawdown_comparison.png` | Drawdown comparison across strategies |
| `portfolio_equity_curve.png` | Individual and combined portfolio equity curves |

All results will be generated through the reproducible Python script `analysis.py`.

## 8. Limitations and Assumptions

- The three strategy runs use the same initial capital, execution timeframe, base risk percentage, fee assumptions and slippage assumptions.
- Individual strategy runs may have different trade counts and capital utilisation.
- Exit-date realised P&L correlation can be influenced by differences in trade duration and exit timing.
- Trade overlap does not necessarily imply identical market exposure or identical risk.
- Portfolio results depend on capital allocation, simultaneous position limits, and available capital.
- Final conclusions will depend on aligned return series and a consistent combined-portfolio simulation.

## 9. Conclusion

The preliminary analysis indicates positive return relationships and substantial same-symbol directional trade overlap among the three strategy families.

This raises an important portfolio-design question: are these families providing independent sources of returns, or are they increasing exposure to similar market conditions?

The next stage of the research will evaluate drawdown overlap and simulate combined portfolios under consistent capital and risk constraints.

The ultimate objective is to identify strategy combinations that improve portfolio-level performance, rather than simply increasing the number of active strategies.

---

**Research Category:** Quantitative Trading Research  
**Execution Timeframe:** 30m  
**Strategy Families:** TREND_PULLBACK, TREND_CONTINUATION, BREAKOUT_CONTINUATION  
**Status:** Preliminary analysis completed; portfolio diversification analysis pending.
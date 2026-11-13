# Methodology — Multi-Strategy Correlation Analysis

## 1. Research Objective

The objective of this research is to evaluate the diversification characteristics of three algorithmic trading strategy families:

- TREND_PULLBACK
- TREND_CONTINUATION
- BREAKOUT_CONTINUATION

The analysis investigates whether these strategy families generate independent trading opportunities or whether they share similar market exposure, return behaviour, and drawdown patterns.

The central research question is:

**Does combining multiple strategy families improve portfolio-level performance and reduce risk, or does it increase exposure to similar market movements?**

---

## 2. Dataset Configuration

### 2.1 Dataset Overview

Three independent backtest CSV files are used as input.

| Parameter | Configuration |
|---|---|
| Strategy families | 3 |
| Execution timeframe | 30m |
| Trading universe | 50 symbols |
| Historical start | 15 January 2024 |
| Historical end | 29 September 2026 |
| Initial capital | Same across all strategy runs |
| Base risk per trade | 0.25% |
| Trading fee per side | 0.05% |
| Slippage per side | 0.05% |

### 2.2 Input Datasets

| Strategy family | Input file |
|---|---|
| TREND_PULLBACK | `trend_pullback.csv` |
| TREND_CONTINUATION | `trend_continuation.csv` |
| BREAKOUT_CONTINUATION | `breakout_continuation.csv` |

The original datasets are stored in:

```text
data/raw/
```

Original input files must remain unchanged throughout the research process.

---

## 3. Data Validation and Preparation

Before performing correlation calculations, the input datasets must pass validation.

### 3.1 Schema Validation

Validate the availability and consistency of the following fields:

- Trade identifier
- Symbol
- Strategy family
- Timeframe
- Trade direction
- Entry timestamp
- Exit timestamp
- Entry price
- Exit price
- Position size
- Risk amount
- Net P&L
- Fee
- Slippage

The analysis must use the actual CSV column names and must not silently substitute missing fields.

### 3.2 Data Quality Checks

The following checks are performed:

1. Validate entry and exit timestamps.
2. Confirm exit timestamp is not earlier than entry timestamp.
3. Identify missing or invalid symbol values.
4. Identify duplicate trade records.
5. Validate numeric fields such as position size and net P&L.
6. Confirm that all datasets use the expected execution timeframe.
7. Check that fee and slippage assumptions are consistent.
8. Compare the historical coverage of all three datasets.

Invalid records should be reported separately rather than silently removed.

### 3.3 Timestamp Normalisation

All timestamps must be converted into a consistent timezone before comparing trade intervals or aggregating returns.

Daily, weekly, and monthly aggregation must use consistent calendar boundaries.

---

## 4. Individual Strategy Performance Analysis

Before evaluating diversification, calculate the independent performance of each family.

### 4.1 Performance Metrics

| Metric | Description |
|---|---|
| Total trades | Number of completed trades |
| Winning trades | Trades with positive net P&L |
| Losing trades | Trades with negative net P&L |
| Win rate | Winning trades / Total trades |
| Net P&L | Sum of net trade P&L |
| Gross profit | Sum of positive net trade P&L |
| Gross loss | Absolute sum of negative net trade P&L |
| Profit factor | Gross profit / Gross loss |
| Maximum drawdown | Largest peak-to-trough decline in cumulative realised P&L |

Break-even trades should be treated separately from winning and losing trades.

### 4.2 Purpose

This analysis establishes the individual performance baseline against which combined portfolios will be evaluated.

A strategy with higher standalone P&L is not necessarily the best diversification contributor.

---

## 5. Return Correlation Analysis

### 5.1 Objective

Measure how the returns of different strategy families move relative to each other.

A positive correlation indicates that the strategies tend to move in the same direction. A negative correlation indicates that they tend to move in opposite directions.

Low correlation may indicate diversification potential, but does not by itself establish improved portfolio performance.

### 5.2 Return Series Construction

Construct aligned return series for each strategy family.

The preferred approach is to use timestamp-aligned equity or mark-to-market returns.

If only closed-trade records are available, realised P&L can be aggregated by exit date as a preliminary diagnostic. However, this approach has limitations because:

- Trade exits may occur on different dates.
- Open positions are not represented by realised P&L.
- Periods without closed trades may still have active market exposure.
- Different capital utilisation can affect comparisons.

Therefore, exit-date P&L correlation must not be treated as final portfolio return correlation.

### 5.3 Return Frequency

Calculate correlation at three aggregation frequencies:

- Daily
- Weekly
- Monthly

The same historical observation window must be used for every strategy pair at each frequency.

### 5.4 Pearson Correlation

Pearson correlation measures the strength and direction of a linear relationship between two return series.

$$
\rho_{X,Y} = \frac{\operatorname{Cov}(X,Y)}{\sigma_X \sigma_Y}
$$

Interpretation:

| Correlation | Interpretation |
|---:|---|
| +0.80 to +1.00 | Very strong positive relationship |
| +0.50 to +0.80 | Strong positive relationship |
| +0.20 to +0.50 | Moderate positive relationship |
| -0.20 to +0.20 | Weak linear relationship |
| -0.50 to -0.20 | Moderate negative relationship |
| -0.80 to -0.50 | Strong negative relationship |
| -1.00 to -0.80 | Very strong negative relationship |

These ranges are descriptive conventions, not universal statistical thresholds.

### 5.5 Spearman Correlation

Spearman rank correlation measures the strength of a monotonic relationship between two return series.

It is included because strategy returns may contain outliers and nonlinear relationships that Pearson correlation does not fully describe.

### 5.6 Correlation Outputs

Generate:

- Daily Pearson correlation matrix
- Weekly Pearson correlation matrix
- Monthly Pearson correlation matrix
- Spearman correlation matrix
- Return correlation heatmap

The final analysis must document how missing observations and periods without trades are handled.

---

## 6. Trade Overlap Analysis

### 6.1 Objective

Determine whether different strategy families hold positions in the same symbol during overlapping time intervals.

This analysis helps identify duplicated directional exposure across strategy families.

### 6.2 Overlap Definition

Two trades overlap when:

- Both trades belong to different strategy families.
- Both trades involve the same symbol.
- Their position intervals intersect.

For trades A and B, the overlap duration is:

\[
Overlap =
\max\left(
0,\,
\min(Exit_A,Exit_B)
-
\max(Entry_A,Entry_B)
\right)
\]

A positive duration indicates overlapping exposure.

### 6.3 Directional Classification

Classify each overlapping trade pair into:

1. Same-direction overlap
2. Opposite-direction overlap

For example:

| Strategy A | Strategy B | Classification |
|---|---|---|
| LONG | LONG | Same direction |
| SHORT | SHORT | Same direction |
| LONG | SHORT | Opposite direction |
| SHORT | LONG | Opposite direction |

### 6.4 Overlap Metrics

Calculate:

- Total overlapping trade pairs
- Same-direction overlapping pairs
- Opposite-direction overlapping pairs
- Unique trades involved in overlap
- Overlap duration
- Percentage of trades involved in overlap

Trade-pair counts must not be confused with unique trade counts. A single trade can overlap with multiple trades from another family.

---

## 7. Drawdown Analysis

### 7.1 Objective

Determine whether strategy families experience losses during similar market periods.

Two strategies can have positive long-term correlation but still provide diversification during specific drawdown periods. Therefore, drawdown timing must be analysed independently.

### 7.2 Equity and Drawdown Calculation

For a portfolio equity series:

\[
Drawdown_t =
\frac{Equity_t - PeakEquity_t}
{PeakEquity_t}
\]

Where:

\[
PeakEquity_t = \max(Equity_0,\ldots,Equity_t)
\]

Maximum drawdown is the largest peak-to-trough percentage decline.

For the preliminary realised-P&L analysis, cumulative realised P&L drawdown can also be calculated in absolute P&L units.

These two measures must be labelled separately.

### 7.3 Drawdown Metrics

Calculate:

- Maximum drawdown
- Drawdown duration
- Recovery duration
- Number of drawdown periods
- Simultaneous drawdown periods
- Drawdown overlap between strategy pairs

A simultaneous drawdown should be defined using a consistent equity peak and drawdown-state methodology.

---

## 8. Portfolio Diversification Simulation

### 8.1 Objective

Evaluate whether combining strategy families produces better portfolio-level performance than running each family independently.

### 8.2 Portfolio Configurations

Seven configurations will be evaluated:

| Portfolio | Included strategy families |
|---|---|
| P1 | TREND_PULLBACK |
| P2 | TREND_CONTINUATION |
| P3 | BREAKOUT_CONTINUATION |
| P4 | TREND_PULLBACK + TREND_CONTINUATION |
| P5 | TREND_PULLBACK + BREAKOUT_CONTINUATION |
| P6 | TREND_CONTINUATION + BREAKOUT_CONTINUATION |
| P7 | TREND_PULLBACK + TREND_CONTINUATION + BREAKOUT_CONTINUATION |

### 8.3 Capital Allocation

All combined portfolios must use a consistent capital-allocation framework.

The simulation must account for:

- Shared initial capital
- Strategy-level risk allocation
- Simultaneous open positions
- Available capital
- Position sizing
- Maximum portfolio risk
- Capital utilisation
- Overlapping exposure

The independent backtest P&Ls must not simply be added together and presented as a combined portfolio result.

The combined portfolio must be reconstructed under an explicitly documented allocation policy.

### 8.4 Portfolio Performance Metrics

Evaluate:

| Metric | Purpose |
|---|---|
| Net P&L | Overall profitability |
| Total return | Return relative to initial capital |
| Profit factor | Profitability of winning versus losing trades |
| Maximum drawdown | Worst peak-to-trough decline |
| Return-to-drawdown ratio | Return relative to drawdown |
| Return volatility | Variability of periodic returns |
| Capital utilisation | Percentage of capital deployed |
| Exposure concentration | Risk concentrated in overlapping positions |

Where sufficient periodic return observations are available, additional risk-adjusted measures may be calculated.

---

## 9. Comparative Analysis

The final research will compare individual and combined portfolios to identify:

- Which family contributes the most standalone return?
- Which family has the lowest correlation with the others?
- Which family contributes the least overlapping exposure?
- Which combination reduces maximum drawdown?
- Which combination improves return-to-drawdown ratio?
- Does adding a third family improve diversification or merely increase exposure?

The objective is to identify the most effective portfolio combination, not necessarily the combination with the highest number of strategies.

---

## 10. Reproducibility

The analysis will be implemented in:

```text
analysis.py
```

The script will:

1. Load the three original CSV files.
2. Validate dataset schemas and values.
3. Calculate individual strategy metrics.
4. Generate aligned return series.
5. Calculate correlation matrices.
6. Identify overlapping trades.
7. Calculate drawdown statistics.
8. Simulate combined portfolios under the selected allocation policy.
9. Export CSV results.
10. Generate research charts.

### Expected Outputs

```text
results/
├── correlation_matrix.csv
├── strategy_comparison.csv
└── charts/
    ├── pnl_correlation_heatmap.png
    ├── drawdown_comparison.png
    └── portfolio_equity_curve.png
```

The same input datasets and configuration should produce reproducible results.

---

## 11. Limitations

The following limitations must be considered when interpreting results:

1. Historical correlation does not guarantee future correlation.
2. Strategy relationships may change across market regimes.
3. Exit-date realised P&L correlation does not fully capture open-position exposure.
4. Trade overlap does not necessarily imply identical risk.
5. Portfolio results depend on the capital-allocation and position-sizing policy.
6. Correlation alone cannot establish whether a portfolio is diversified.
7. Backtest results may differ from live execution due to liquidity, slippage, funding, and market impact.

---

## 12. Research Conclusion Criteria

A strategy family will be considered a potentially valuable diversification contributor when it demonstrates one or more of the following:

- Lower correlation with existing portfolio returns.
- Limited overlap in simultaneous market exposure.
- Different drawdown timing.
- Improvement in portfolio return-to-drawdown ratio.
- Reduction in portfolio maximum drawdown without an unacceptable reduction in return.

The final conclusion will be based on combined portfolio simulation and not solely on correlation coefficients.

**Research principle: The goal is not to maximize the number of strategies, but to maximize the quality and diversification of portfolio returns.**
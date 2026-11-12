# Research Methodology: Transaction Cost Sensitivity Analysis

## 1. Research Scope

This experiment evaluates the impact of transaction fees and execution slippage on the performance of the TREND_PULLBACK strategy family.

| Parameter | Configuration |
|---|---|
| Strategy Family | TREND_PULLBACK |
| Execution Timeframe | 30m |
| Market | Cryptocurrency Futures |
| Historical Period | 15 January 2024 – 28 September 2026 |
| Symbol Universe | 50 trading pairs |
| Experiment Type | Transaction Cost Sensitivity Analysis |

## 2. Experimental Design

Seven independent backtesting scenarios were evaluated using different transaction fee and slippage assumptions.

| Scenario | Transaction Fee Per Side | Slippage Per Side |
|---|---:|---:|
| A | 0.00% | 0.00% |
| B | 0.00% | 0.05% |
| C | 0.05% | 0.00% |
| D | 0.05% | 0.05% |
| E | 0.05% | 0.10% |
| F | 0.05% | 0.15% |
| G | 0.05% | 0.20% |

Transaction fees and slippage are expressed as percentages of execution notional per side.

Both entry and exit execution costs are considered by the backtesting engine.

## 3. Transaction Cost Components

### 3.1 Transaction Fee

Transaction fees represent exchange commissions charged when opening and closing positions.

For each execution:

Transaction Fee = Executed Notional × Fee Rate

Round-trip transaction fees include both entry and exit commissions.

### 3.2 Execution Slippage

Slippage represents the difference between the expected execution price and the actual simulated execution price.

For each execution:

Slippage Cost = Executed Notional × Slippage Rate

Both entry and exit slippage assumptions are included.

### 3.3 Total Transaction Cost

Total Transaction Cost = Entry Fee + Exit Fee + Entry Slippage Cost + Exit Slippage Cost

The backtesting engine accounts for these costs when determining trade-level net P&L.

## 4. Performance Metrics

The following metrics are used to evaluate each scenario.

### 4.1 Net Profit and Loss

Aggregate net P&L after transaction costs.

Net P&L = Sum of all closed-trade net P&L values.

### 4.2 Win Rate

Win Rate = (Number of Trades with Positive Net P&L / Total Closed Trades) × 100

### 4.3 Profit Factor

Profit Factor = Gross Winning Net P&L / Absolute Gross Losing Net P&L

A profit factor above 1 indicates that aggregate winning net P&L exceeds aggregate losing net P&L.

A profit factor below 1 indicates negative aggregate trade profitability.

### 4.4 Maximum Realised Drawdown

Trades are ordered chronologically by exit timestamp.

Cumulative realised P&L is calculated, followed by the peak-to-trough decline.

Maximum Realised Drawdown = Maximum Decline from a Previous Cumulative P&L Peak.

This is an absolute P&L measure, not a percentage of account equity or mark-to-market drawdown.

## 5. Scenario Comparison Method

Each scenario is evaluated independently using its corresponding backtesting trade log.

The resulting performance metrics are compared to understand how changing transaction fee and slippage assumptions affects the strategy's reported performance.

The zero-fee, zero-slippage scenario is used as the idealised baseline.

The combined-cost scenarios are used to evaluate performance deterioration under progressively higher execution-cost assumptions.

**Important:** The scenarios are independently generated backtests. Their trade populations and execution outcomes may differ. Consequently, differences in net P&L represent overall scenario performance changes and should not be interpreted as pure cost deductions from an identical set of trades.

## 6. Assumptions

1. Transaction fee and slippage rates are applied per execution side.
2. Both entry and exit costs are included.
3. The same strategy family, execution timeframe, historical period and symbol universe are used across scenarios.
4. The backtesting engine determines the resulting trade outcomes under each scenario's execution assumptions.
5. Net P&L values are taken from the exported closed-trade logs.
6. P&L currency and initial account capital must be established separately before reporting percentage returns or equity-based drawdown.

## 7. Data Processing

The exported closed-trade CSV files are used as the input dataset.

The analysis process consists of:

1. Loading the seven scenario-specific CSV files.
2. Extracting transaction fee and slippage assumptions.
3. Validating trade-level net P&L values.
4. Ordering trades by exit timestamp.
5. Calculating net P&L, win rate, profit factor and realised drawdown.
6. Comparing performance across execution-cost scenarios.
7. Generating summary tables and visualisations.

## 8. Reproducibility

The analysis is implemented in Python using pandas and NumPy.

The analysis script should accept the scenario CSV files as inputs and generate:

- Scenario comparison table.
- Net P&L comparison.
- Profit factor comparison.
- Realised drawdown comparison.
- Summary results in CSV format.

All scenario assumptions should be explicitly documented to ensure reproducibility.

## 9. Research Limitations

This experiment evaluates independently generated backtesting scenarios.

It does not isolate the direct cost impact on an identical set of historical trades.

A separate fixed-trade replay experiment is required to measure direct transaction-cost deductions while holding trade entry and exit events constant.

The experiment also does not establish that the assumed slippage rates represent actual live-market execution.

## 10. Future Methodological Extensions

- Fixed-trade replay under alternative cost assumptions.
- Symbol-level transaction-cost sensitivity.
- Strategy-family cost sensitivity comparison.
- Execution-timeframe sensitivity analysis.
- Comparison of simulated slippage with paper-trading execution.
- Minimum cost-coverage threshold evaluation.
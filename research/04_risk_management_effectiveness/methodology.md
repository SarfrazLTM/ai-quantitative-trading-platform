# Research 04 — Risk Management Effectiveness
# Methodology

## 1. Research objective

The objective of this research is to evaluate the effectiveness, consistency, and reliability of the trading platform's risk-management framework.

The methodology examines five dimensions:

1. Trade-level risk performance
2. Portfolio equity and drawdown behaviour
3. Risk allocation and approval decisions
4. Aggregate open-position exposure
5. Risk-limit compliance and control validation

The analysis uses historical execution outcomes, portfolio equity snapshots, risk-engine decision logs, and open-position snapshots.

The primary research period is 15 January 2024 to 30 September 2026.

## 2. Research inputs

Four datasets are used.

| Dataset | Input file | Analytical purpose |
|---|---|---|
| Trade execution outcomes | `01_trade_execution_outcomes.csv` | Measure realized trade performance and trade-level risk |
| Portfolio equity history | `02_portfolio_equity_history.csv` | Calculate equity growth and drawdown |
| Risk allocation decisions | `03_risk_allocation_decisions.csv` | Evaluate risk-engine approvals and rejections |
| Open-position snapshots | `04_open_position_snapshots.csv` | Measure aggregate portfolio exposure |

Each dataset is normalized before analysis. Column names, timestamps, numeric fields, and categorical values must be standardized to ensure consistent calculations.

## 3. Data preparation methodology

### 3.1 Column normalization

Input columns are mapped to standardized analytical fields.

Examples include:

- Trade identifier
- Entry timestamp
- Exit timestamp
- Symbol
- Timeframe
- Strategy family
- Strategy
- Trade status
- Net P&L
- Risk amount
- Portfolio equity
- Requested risk
- Approved risk
- Portfolio risk
- Risk percentage
- Decision status
- Rejection reason

The analysis should retain the original input files unchanged and create normalized datasets for downstream calculations.

### 3.2 Timestamp normalization

All timestamps must be converted to a consistent timezone before joining datasets.

The methodology must distinguish:

- Trade entry time
- Trade exit time
- Risk decision time
- Equity snapshot time
- Open-position snapshot time

Where timestamps are used for matching, the matching rule must be documented.

### 3.3 Trade status filtering

Only completed trades are included in realized trade-performance calculations.

Open, pending, active, cancelled, or otherwise incomplete records must not be treated as completed trade outcomes.

However, open positions remain relevant to portfolio exposure analysis.

### 3.4 Numeric validation

Validate the following fields before calculation:

- Net P&L
- Risk amount
- Equity
- Requested risk
- Approved risk
- Portfolio exposure
- Risk percentage

Invalid numeric values, missing timestamps, duplicate identifiers, and negative or zero denominators must be flagged.

Missing values must not silently be converted into valid-looking risk measurements.

## 4. Trade-level risk methodology

### 4.1 Net P&L

Net P&L represents the realized financial result of a completed trade.

The analysis uses the exported net P&L field rather than reconstructing trade profit from entry and exit prices, unless a separate price-based validation is explicitly performed.

### 4.2 Monetary risk

Monetary risk is the initial risk amount associated with a trade.

The analysis uses the recorded risk amount and checks whether it is positive and valid.

If the exported field represents something other than initial planned monetary risk, that semantic difference must be documented before calculating R-multiples.

### 4.3 R-multiple

R-multiple measures realized net P&L relative to the initial monetary risk.

\[
R_i = \frac{Net\ P\&L_i}{|Initial\ Risk_i|}
\]

Interpretation:

| R-multiple | Meaning |
|---|---|
| +2.0R | Profit equal to twice the initial risk |
| +1.0R | Profit equal to the initial risk |
| 0R | Break-even |
| -0.5R | Loss equal to half the initial risk |
| -1.0R | Loss equal to the initial risk |
| -2.0R | Loss equal to twice the initial risk |

Trades with missing or zero initial risk must be excluded from R-multiple calculations and reported separately.

### 4.4 Win rate

\[
Win\ Rate =
\frac{Number\ of\ Winning\ Trades}
{Total\ Completed\ Trades}
\times 100
\]

A winning trade is a completed trade with positive net P&L.

A zero-P&L trade should be classified separately as breakeven rather than automatically counted as a winner or loser.

### 4.5 Profit factor

\[
Profit\ Factor =
\frac{Gross\ Profit}{|Gross\ Loss|}
\]

Where:

- Gross profit is the sum of positive net P&L.
- Gross loss is the sum of negative net P&L.

Interpretation:

| Profit factor | Interpretation |
|---|---|
| Greater than 1.0 | Profitable over the measured sample |
| Equal to 1.0 | Gross profits and losses are equal |
| Below 1.0 | Losses exceed profits |

If there are no losing trades, profit factor should be reported as undefined or not applicable rather than treated as an ordinary finite value.

### 4.6 Average trade P&L

\[
Average\ P\&L =
\frac{Total\ Net\ P\&L}{Completed\ Trades}
\]

This measures the average monetary outcome per completed trade.

### 4.7 Family-level performance

Trade outcomes should also be grouped by strategy family.

For each family, calculate:

- Completed trade count
- Net P&L
- Gross profit
- Gross loss
- Win rate
- Profit factor
- Average P&L
- Average R-multiple
- Median R-multiple

This helps identify whether risk-adjusted performance differs across strategy families.

A family with positive total P&L is not automatically considered consistently profitable. Trade count, drawdown contribution, and outcome distribution should also be considered.

## 5. Portfolio equity and drawdown methodology

### 5.1 Equity curve

Portfolio equity snapshots are ordered chronologically to construct the equity curve.

The analysis uses the recorded equity values. It does not assume that trade P&L alone explains every equity movement.

### 5.2 Running peak equity

For each timestamp, calculate the highest equity observed up to that point.

\[
Peak_t = \max(Equity_1, Equity_2, \ldots, Equity_t)
\]

### 5.3 Drawdown amount

\[
Drawdown\ Amount_t = Equity_t - Peak_t
\]

A negative value indicates that the portfolio is below its previous observed peak.

### 5.4 Drawdown percentage

\[
Drawdown\ Percentage_t =
\frac{Equity_t - Peak_t}{Peak_t}
\times 100
\]

The maximum drawdown is the most negative observed drawdown percentage.

### 5.5 Drawdown recovery

A drawdown episode begins when equity falls below a previous peak.

Recovery occurs when equity reaches or exceeds that peak again.

The analysis should identify:

- Peak timestamp
- Drawdown trough timestamp
- Recovery timestamp
- Maximum drawdown amount
- Maximum drawdown percentage
- Peak-to-trough duration
- Trough-to-recovery duration

If recovery does not occur within the analysis period, the episode should be reported as unrecovered.

### 5.6 Snapshot limitation

The calculated drawdown is based on recorded equity observations.

If snapshots are not continuous, the true intraperiod maximum drawdown may be larger than the measured value.

The snapshot frequency should therefore be documented alongside the drawdown results.

## 6. Risk-engine decision methodology

### 6.1 Decision classification

Each risk-engine decision must be classified into one of the following categories:

| Classification | Definition |
|---|---|
| `APPROVED_AT_REQUESTED_RISK` | Candidate approved at the requested risk amount |
| `APPROVED_AT_REDUCED_RISK` | Candidate approved at a lower risk amount than requested |
| `REJECTED` | Candidate rejected by the risk engine |
| `APPROVED_BUT_ACTUAL_RISK_MISMATCH` | Approved decision cannot be reconciled with the actual recorded trade risk |

The classification must use decision status and comparable risk amounts.

A rejected decision with zero approved risk is not a reduced-risk approval.

### 6.2 Requested versus approved risk

For approved decisions:

\[
Risk\ Reduction =
Requested\ Risk - Approved\ Risk
\]

\[
Risk\ Reduction\ Percentage =
\frac{Requested\ Risk - Approved\ Risk}
{Requested\ Risk}
\times 100
\]

These calculations apply only when:

- The decision is approved.
- Requested and approved risk use the same unit.
- Requested risk is positive.
- Both values are valid.

Rejected candidates must be analyzed separately.

### 6.3 Approval rate

\[
Approval\ Rate =
\frac{Approved\ Decisions}{Total\ Decisions}
\times 100
\]

### 6.4 Rejection rate

\[
Rejection\ Rate =
\frac{Rejected\ Decisions}{Total\ Decisions}
\times 100
\]

Approval and rejection rates measure the frequency of recorded engine decisions. They do not independently measure whether those decisions improved trading performance.

### 6.5 Rejection reason distribution

Group rejected decisions by their recorded rejection reason.

For each reason, calculate:

- Rejection count
- Percentage of all rejections
- Percentage of all risk decisions

This identifies which risk controls account for the largest share of recorded rejections.

Rejection labels must be treated as logged reasons. The deployed source code and configuration must be checked before claiming that a particular control was active and correctly enforced.

## 7. Risk decision-to-trade reconciliation

The risk decision log and completed-trade dataset must be reconciled to verify that approved decisions correspond to actual executions.

### 7.1 Matching priority

Use the following matching hierarchy where the required fields exist:

1. Exact trade identifier
2. Symbol and strategy/family consistency
3. Decision timestamp before or sufficiently close to entry timestamp
4. Approved decision status
5. Explicit documented time tolerance

The actual matching rules and time tolerance must be recorded in the analysis manifest.

### 7.2 Multiple decisions per trade

A trade may have multiple decision records, for example because of retries or repeated candidate evaluations.

The analysis must not blindly count every approved decision as a separate completed trade.

Where multiple records map to one trade, identify the relevant approval event using the trade identifier and event timestamps. Preserve the full decision history for audit.

### 7.3 Reconciliation categories

The reconciliation report should distinguish:

- Approved decision matched to completed trade
- Approved decision without completed trade
- Completed trade without matching approval
- Duplicate or multiple decision records
- Approved decision associated with an open position
- Invalid or missing identifiers

The observed difference between approved decisions and completed trades must be investigated rather than assumed to be an error.

## 8. Entry-time risk percentage methodology

The recorded risk percentage should be validated against portfolio equity immediately before each trade entry.

### 8.1 Entry equity matching

For each completed trade:

1. Read its entry timestamp.
2. Locate the latest portfolio equity snapshot strictly before that timestamp.
3. Use that snapshot as the entry equity reference.
4. Record the time difference between the snapshot and trade entry.
5. Flag trades without a valid prior equity observation.

A future equity snapshot must never be used to calculate entry-time risk.

### 8.2 Entry risk percentage

\[
Entry\ Risk\ Percentage =
\frac{Initial\ Monetary\ Risk}
{Equity\ Immediately\ Before\ Entry}
\times 100
\]

This provides a more meaningful comparison across trades than using a fixed monetary risk amount.

### 8.3 Comparison with configured base risk

The calculated entry-time risk percentage should be compared with the configured base risk per trade.

For this platform, the previously stated base risk setting is 0.25%.

However, differences can arise due to:

- Adaptive allocation
- Position sizing
- Portfolio constraints
- Equity changes
- Risk caps
- Execution-level adjustments

The analysis should report the distribution of actual entry risk rather than assume that every trade must equal the base risk setting.

## 9. Portfolio exposure methodology

### 9.1 Aggregate open risk

Open-position snapshots are grouped by portfolio snapshot timestamp.

Where the source data provides individual position risk, aggregate open monetary risk using the documented portfolio aggregation rule.

Do not sum repeated portfolio-level totals from individual position rows.

The analysis must identify whether a field represents:

- Individual position risk
- Family-level risk
- Group-level risk
- Total portfolio open risk

These fields are not interchangeable.

### 9.2 Portfolio risk percentage

Where portfolio open monetary risk and portfolio equity are available and compatible:

\[
Portfolio\ Risk\ Percentage =
\frac{Total\ Open\ Monetary\ Risk}
{Portfolio\ Equity}
\times 100
\]

If a trusted portfolio risk percentage is already exported, validate its units and calculation semantics before using it.

### 9.3 Exposure distribution

Calculate:

- Average portfolio risk
- Maximum portfolio risk
- Median portfolio risk
- 95th percentile portfolio risk
- Average portfolio risk percentage
- Maximum portfolio risk percentage
- 95th percentile portfolio risk percentage

This provides a view of normal exposure and high-exposure periods.

## 10. Portfolio risk-limit compliance methodology

The configured maximum portfolio risk reference for this research is 5%.

### 10.1 Compliance calculation

For each valid portfolio snapshot:

\[
Risk\ Headroom =
Configured\ Risk\ Limit - Observed\ Portfolio\ Risk\ Percentage
\]

A positive result indicates headroom below the configured limit.

A negative result indicates an observed breach.

### 10.2 Breach identification

A breach is recorded when:

\[
Observed\ Portfolio\ Risk\ Percentage >
Configured\ Risk\ Limit
\]

The analysis should calculate:

- Number of snapshots above the limit
- Maximum observed risk percentage
- Maximum breach magnitude
- First breach timestamp
- Last breach timestamp
- Breach duration, where snapshot frequency permits
- Available headroom during compliant periods

### 10.3 Important unit validation

The risk engine may store monetary limits while portfolio snapshots store percentages.

Never compare monetary risk directly with a percentage limit.

All compliance comparisons must use the same unit and a clearly documented denominator.

### 10.4 Observed versus continuous compliance

Snapshot compliance is not proof of continuous compliance.

A breach may occur between snapshots and disappear before the next recorded observation.

Decision-time risk logs and higher-frequency exposure snapshots should be used to strengthen the audit.

## 11. Trade P&L and equity reconciliation

Trade-level net P&L and portfolio equity change should be compared.

\[
Equity\ Change =
Ending\ Equity - Starting\ Equity
\]

\[
Reconciliation\ Difference =
Equity\ Change - Total\ Trade\ Net\ P\&L
\]

The difference should be investigated using available accounting fields, such as:

- Trading commissions
- Exchange fees
- Funding payments
- Realized adjustments
- Deposits
- Withdrawals
- Other balance adjustments
- Equity snapshot timing

The analysis must not automatically attribute the difference to fees or funding without supporting records.

## 12. Risk-control effectiveness methodology

Risk-control effectiveness must be evaluated separately from raw approval and rejection counts.

For each control, examine:

1. Whether the control was configured and active.
2. Whether the decision log records the control's intervention.
3. Whether the recorded decision was consistent with the configured limit.
4. Whether the resulting portfolio exposure remained within limits.
5. Whether the corresponding trade or portfolio outcome can be observed.

### 12.1 Control-level audit

The analysis should examine:

- Portfolio maximum open risk
- Family risk cap
- Group risk caps
- Maximum positions per symbol
- Existing portfolio risk at cap
- Health gate

The health gate requires explicit source/configuration validation because its recorded rejection label may be inconsistent with the stated source status.

### 12.2 Counterfactual limitations

A rejected candidate has no actual completed-trade outcome in the normal execution dataset.

Therefore, the analysis cannot conclude whether rejecting that candidate prevented a loss or missed a profitable opportunity.

A defensible counterfactual study requires one of the following:

- Historical outcome labels for rejected candidates
- A shadow execution system that tracks rejected signals without placing trades
- A controlled backtest that applies alternative risk-control configurations
- A replay simulation using the original market data and decision-time state

Until such data is available, report control activity and observed exposure rather than claiming causal performance improvement.

## 13. Statistical and reporting methodology

The reports should include both aggregate and distribution-based metrics.

Recommended descriptive statistics include:

- Count
- Mean
- Median
- Standard deviation
- Minimum
- Maximum
- 95th percentile

Where appropriate, group results by:

- Strategy family
- Symbol
- Timeframe
- Month
- Risk decision category
- Rejection reason

Avoid drawing conclusions from very small samples without clearly showing the sample count.

If statistical significance or confidence intervals are later introduced, document the sampling assumptions and account for dependence between trades from the same symbol or time period.

## 14. Data-quality and audit controls

Every analysis run should validate:

| Validation | Expected behaviour |
|---|---|
| Missing trade IDs | Flag and report |
| Duplicate trade IDs | Identify and investigate |
| Missing entry timestamps | Exclude from timestamp-based matching and report |
| Invalid or zero risk amount | Exclude from R calculations and report |
| Missing equity match | Flag affected trades |
| Equity timestamp after trade entry | Must not be used as entry equity |
| Risk-unit mismatch | Stop or flag the affected calculation |
| Unknown decision status | Preserve and report as unclassified |
| Missing rejection reason | Report separately |
| Missing exposure percentage | Do not assume zero |
| Inconsistent trade and equity P&L | Generate reconciliation report |

The run manifest should record:

- Analysis execution timestamp
- Input filenames
- Input row counts
- Analysis period
- Key configuration values
- Risk percentage unit assumptions
- Output filenames
- Validation warnings
- Script version, where available

## 15. Expected research outputs

| Output | Methodology |
|---|---|
| `risk_performance.csv` | Trade P&L, win rate, profit factor, and R-multiple |
| `drawdown_analysis.csv` | Maximum drawdown and recovery episodes |
| `equity_curve_with_drawdown.csv` | Equity, running peak, and drawdown time series |
| `risk_allocation_analysis.csv` | Requested-versus-approved risk classification |
| `risk_decision_distribution.csv` | Approval and rejection distribution |
| `risk_rejection_reasons.csv` | Rejection reason frequency |
| `trade_level_risk_audit.csv` | Individual trade risk audit |
| `portfolio_exposure_analysis.csv` | Aggregate portfolio exposure metrics |
| `portfolio_open_position_snapshots_aggregated.csv` | Timestamp-level open-position exposure |
| `normalized_trade_data.csv` | Standardized trade dataset |
| `normalized_equity_data.csv` | Standardized equity dataset |
| `normalized_risk_decisions.csv` | Standardized risk-decision dataset |
| `normalized_position_snapshots.csv` | Standardized position snapshot dataset |
| `risk_limit_compliance.csv` | Proposed portfolio limit compliance report |
| `risk_decision_trade_reconciliation.csv` | Proposed decision-to-trade reconciliation |
| `risk_control_effectiveness.csv` | Proposed control-level audit |

The final three reports are recommended extensions and should not be considered available unless implemented in the analysis script.

## 16. Research conclusion criteria

The research should only conclude that the risk-management framework is operating effectively when the evidence supports all of the following:

1. Trade-level risk is measured consistently against entry-time equity.
2. Risk decisions reconcile with actual executions.
3. Approved risk is consistent with actual recorded trade risk.
4. Portfolio exposure is measured using validated units.
5. The configured maximum portfolio risk is respected in the available observations and decision logs.
6. Drawdown and equity changes reconcile with the underlying accounting records.
7. Risk-control configuration and logging behaviour are verified.
8. Control effectiveness claims are supported by outcome data or controlled counterfactual testing.

A high rejection rate or a low observed portfolio risk percentage alone is not sufficient evidence of effective risk management.

---

**Research:** 04 — Risk Management Effectiveness  
**Methodology version:** 1.0  
**Research period:** 2024-01-15 to 2026-09-30  
**Primary objective:** Audit trade-level risk, portfolio exposure, drawdown, and risk-engine control behaviour.
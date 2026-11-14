# Research 04 — Risk Management Effectiveness

## 1. Objective

This research evaluates how effectively the trading platform's risk-management layer controls trade-level risk and aggregate portfolio exposure.

The analysis uses four exported datasets:

1. Trade execution and outcome records
2. Portfolio equity history
3. Risk-allocation decision logs
4. Open-position risk snapshots

The study assesses realized trading performance, observed drawdown, risk-engine decisions, and portfolio exposure. It is an observational analysis; it does not, by itself, prove the causal effectiveness of each risk control.

## 2. Research period and scope

| Item | Value |
|---|---|
| Analysis period | 2024-01-15 to 2026-09-30 |
| Execution environment | Binance Futures algorithmic trading platform |
| Completed trades in reviewed run | 3,401 |
| Equity observations | 47,473 |
| Risk-allocation decisions | 23,782 |
| Open-position snapshot rows | 209,828 |
| Configured maximum portfolio risk reference | 5.0% |

These counts and metrics describe the reviewed run and should be refreshed whenever the input exports or analysis code change.

## 3. Directory structure

```text
04_risk_management_effectiveness/
├── README.md
├── analysis.py
├── input/
│   ├── 01_trade_execution_outcomes.csv
│   ├── 02_portfolio_equity_history.csv
│   ├── 03_risk_allocation_decisions.csv
│   └── 04_open_position_snapshots.csv
└── output/
    ├── charts/
    ├── risk_performance.csv
    ├── drawdown_analysis.csv
    ├── equity_curve_with_drawdown.csv
    ├── risk_allocation_analysis.csv
    ├── risk_decision_distribution.csv
    ├── risk_rejection_reasons.csv
    ├── trade_level_risk_audit.csv
    ├── portfolio_exposure_analysis.csv
    ├── portfolio_open_position_snapshots_aggregated.csv
    ├── normalized_trade_data.csv
    ├── normalized_equity_data.csv
    ├── normalized_risk_decisions.csv
    ├── normalized_position_snapshots.csv
    ├── run_manifest.json
    └── analysis.log
```

The exact output set depends on the version of `analysis.py`. The list above reflects the initial Research 05 run.

## 4. Input datasets

Place the four CSV files in `input/`. Keep the filenames unchanged unless the corresponding paths in `analysis.py` are updated.

### 4.1 `01_trade_execution_outcomes.csv`

Trade-level execution and outcome data used to calculate realized P&L, win rate, profit factor, average trade result, risk amount, and R-multiple.

Expected information includes trade identifier, entry and exit timestamps, symbol, timeframe, strategy family, strategy, status, net P&L, and initial monetary risk.

Completed trades should be used for realized performance; open or pending records are not closed-trade outcomes.

### 4.2 `02_portfolio_equity_history.csv`

Time-series portfolio equity snapshots used to construct the equity curve, running peak, drawdown amount, and drawdown percentage.

Snapshot frequency matters: a snapshot-based maximum drawdown can miss lows occurring between observations.

### 4.3 `03_risk_allocation_decisions.csv`

Risk-engine decision logs containing candidate trade risk requests, decisions, available limits, and rejection reasons.

These records support analysis of approvals, rejections, requested versus approved risk, and decision-to-trade reconciliation where identifiers and timestamps permit.

A rejected decision with zero approved risk is a rejection, not a reduced-risk approval. Keep these categories separate.

### 4.4 `04_open_position_snapshots.csv`

Snapshots of open-position and portfolio exposure used to aggregate recorded open risk over time.

Monetary risk and risk percentage are different units and must not be compared directly. A percentage limit check must use a verified percentage field or calculate a percentage from compatible monetary risk and equity values.

## 5. Running the analysis

1. Create the directory structure shown above.
2. Copy the four input CSV files into `input/`.
3. Place `analysis.py` in the project root.
4. Install the dependencies used by the script. The initial analysis uses common data-analysis and plotting libraries, including `pandas`, `numpy`, and `matplotlib`.
5. Run from the project root:

```bash
python analysis.py
```

6. Review the generated CSV reports, charts, `run_manifest.json`, and `analysis.log` in `output/`.

## 6. Reviewed baseline results

The following results were observed in the reviewed run. They are a baseline for investigation, not guaranteed results for future runs.

### 6.1 Portfolio performance

| Metric | Observed result |
|---|---:|
| Starting equity | $1,000.00 |
| Ending equity | $1,975.72 |
| Equity change | +$975.72 |
| Total return | +97.57% |
| Maximum observed drawdown | -14.21% |
| Maximum drawdown amount | -$297.03 |
| Peak before maximum drawdown | 2026-02-19 |
| Trough | 2026-05-14 |
| Recovery | 2026-06-06 |
| Trough-to-recovery duration | Approximately 22.4 days |

These drawdown figures are based on the supplied equity snapshots and may not capture intraday extremes between snapshots.

### 6.2 Completed-trade performance

| Metric | Observed result |
|---|---:|
| Completed trades | 3,401 |
| Net trade P&L | +$977.44 |
| Gross profit | $9,828.44 |
| Gross loss | $8,851.00 |
| Win rate | 48.10% |
| Profit factor | 1.1104 |
| Average P&L per trade | +$0.2874 |
| Average recorded monetary risk | $4.74 |
| Average recorded risk percentage | 0.3042% |
| Average R-multiple | +0.0768R |
| Median R-multiple | -1.0186R |

The positive mean R-multiple alongside a negative median indicates an asymmetric outcome distribution. Review the full R-multiple distribution and family-level results before drawing conclusions.

### 6.3 Risk-engine decisions

| Decision | Count | Share |
|---|---:|---:|
| Approved | 3,403 | 14.31% |
| Rejected | 20,379 | 85.69% |
| Total | 23,782 | 100.00% |

Recorded rejection reasons:

| Reason | Count |
|---|---:|
| Portfolio maximum open risk | 11,631 |
| Health gate | 5,077 |
| Family risk cap | 1,963 |
| Maximum positions per symbol | 716 |
| Existing portfolio risk at cap | 676 |
| Group 1 risk cap | 163 |
| Group 2 risk cap | 145 |
| Group 3 risk cap | 8 |

The health-gate rejection label includes wording indicating that the gate was disabled in source. The export alone cannot establish whether the gate was active at decision time. Confirm the deployed source/configuration and logging behavior before interpreting these as actual health-gate interventions.

### 6.4 Observed portfolio exposure

| Metric | Observed result |
|---|---:|
| Average portfolio risk | $22.69 |
| Maximum portfolio risk | $78.12 |
| Average portfolio risk percentage | 1.44% |
| 95th percentile portfolio risk percentage | 2.66% |
| Maximum recorded portfolio risk percentage | 4.06% |
| Configured reference limit | 5.00% |

The maximum recorded snapshot percentage was 0.94 percentage points below the 5% reference limit. This describes the supplied snapshots only; it does not prove that no decision-time or intraperiod breach occurred.

## 7. Important validation findings

Resolve the following items before treating the results as a final risk-control audit.

### 7.1 Risk reductions versus rejections

The initial risk-allocation report counted decisions with zero approved risk as reduced-risk decisions. Since rejected candidates have zero approved risk, this inflates the reduction count.

A corrected classification should distinguish:

- `APPROVED_AT_REQUESTED_RISK`
- `APPROVED_AT_REDUCED_RISK`
- `REJECTED`
- `APPROVED_BUT_ACTUAL_RISK_MISMATCH`

A rejection must not be reported as an approved risk reduction.

### 7.2 Decision-to-trade reconciliation

The reviewed export contains 3,403 approved risk decisions and 3,401 completed trades. Reconcile identifiers and timestamps to identify unmatched approvals, duplicate decisions, still-open positions, or missing trade records.

Do not assume one risk-decision row always maps one-to-one to one completed trade. Where multiple candidate decisions exist, make the matching rule explicit and use identifiers and event time.

### 7.3 Risk percentage at trade entry

The recorded average risk percentage is 0.3042%. Compare it with the configured base-risk setting only after recalculating each trade's monetary risk as a percentage of portfolio equity immediately before entry:

```text
entry_risk_pct = trade_risk_amount / equity_immediately_before_entry * 100
```

Use the latest equity observation strictly before the entry timestamp. Report missing equity matches and the time gap between the equity observation and trade entry.

### 7.4 Portfolio risk-limit compliance

Test the 5% reference limit only against a verified percentage measure. Do not compare a monetary `Max_Portfolio_Risk` field with a percentage-valued exposure field.

A robust compliance report should identify the maximum observed percentage, number of snapshots above the limit, breach timestamps and duration where supported by snapshot cadence, headroom to the limit, and missing or invalid observations.

### 7.5 Trade P&L versus equity change

Trade-level net P&L totals +$977.44, while portfolio equity changed by +$975.72. The difference is approximately $1.72.

Reconcile this using available accounting fields and timestamps. If present, inspect commissions, fees, funding, realized adjustments, deposits, withdrawals, and final equity snapshot timing. Do not assign a cause without supporting records.

### 7.6 Health-gate status

The rejection log contains 5,077 health-gate reason records, while the reason text indicates that the health gate may have been disabled in source.

Validate the deployed version, configuration, and logging implementation. Until then, describe these as records carrying a health-gate rejection label, not confirmed health-gate interventions.

## 8. Recommended next analysis outputs

| Report | Purpose |
|---|---|
| `risk_limit_compliance.csv` | Verify observed exposure against the configured portfolio risk limit |
| `risk_decision_trade_reconciliation.csv` | Match approvals and trade records; expose unmatched or duplicate records |
| `risk_control_effectiveness.csv` | Summarize control decisions and observed outcomes without overstating causality |
| Entry-equity risk audit | Calculate risk percentage using equity immediately before each trade entry |
| P&L-to-equity reconciliation | Explain the difference between trade P&L and portfolio equity change using exported accounting data |

A counterfactual estimate of how rejected candidates would have performed requires outcomes for rejected candidates or a controlled shadow simulation. The four current exports alone do not establish those hypothetical outcomes.

## 9. Interpretation boundaries

Keep these distinctions explicit in reports and presentations:

- **Observed snapshot exposure** is not the same as continuous exposure.
- **Recorded rejection reason** is not proof that the corresponding control was active and correctly enforced.
- **Approved risk** is not the same as actual realized loss.
- **Rejected candidates** are not completed trades.
- **Risk reduction** means an approved trade received less risk than requested; it does not mean the candidate was rejected.
- **Association between a control decision and subsequent performance** does not establish the control's causal effect.
- **Portfolio return and drawdown metrics** depend on equity-series quality, cash-flow treatment, and timestamp alignment.

## 10. Research status

The initial analysis run completed and produced its reports. The results are useful as a first-pass diagnostic, but the validation items in Section 7 should be resolved before publishing a final conclusion about risk-management effectiveness.

---

**Research:** 04 — Risk Management Effectiveness  
**Primary artifacts:** `analysis.py`, four input CSV exports, generated CSV reports, charts, run manifest, and analysis log  
**Baseline period:** 2024-01-15 to 2026-09-30
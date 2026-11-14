
from pathlib import Path
import logging
import json
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
CHART_DIR = OUTPUT_DIR / "charts"

TRADE_FILE = INPUT_DIR / "01_trade_execution_outcomes.csv"
EQUITY_FILE = INPUT_DIR / "02_portfolio_equity_history.csv"
RISK_FILE = INPUT_DIR / "03_risk_allocation_decisions.csv"
POSITION_FILE = INPUT_DIR / "04_open_position_snapshots.csv"

# Percentage representation:
# 0.25 means 0.25% if percent_points is selected.
# 0.0025 means 0.25% if fraction is selected.
RISK_PERCENT_UNIT = "auto"  # auto / fraction / percent_points

# Your previously configured portfolio risk limit.
# Used for reference only. Prefer the actual recorded limit
# from the risk decision or equity data when available.
CONFIGURED_MAX_PORTFOLIO_RISK_PCT = 5.0

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(
            OUTPUT_DIR / "analysis.log",
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("risk_analysis")


# ============================================================
# GENERAL HELPERS
# ============================================================

def normalize_name(value):
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def find_column(df, aliases, required=False):
    lookup = {
        normalize_name(column): column
        for column in df.columns
    }

    for alias in aliases:
        key = normalize_name(alias)

        if key in lookup:
            return lookup[key]

    if required:
        raise ValueError(
            f"Required column not found.\n"
            f"Expected one of: {aliases}\n"
            f"Available columns: {list(df.columns)}"
        )

    return None


def read_input(path, name):
    if not path.exists():
        raise FileNotFoundError(
            f"{name} not found: {path}"
        )

    df = pd.read_csv(path, low_memory=False)

    if df.empty:
        raise ValueError(f"{name} is empty.")

    logger.info(
        "%s loaded: %s rows, %s columns",
        name, len(df), len(df.columns)
    )

    logger.info("%s columns: %s", name, list(df.columns))

    return df


def parse_datetime(series):
    return pd.to_datetime(
        series,
        errors="coerce",
        utc=True
    ).dt.tz_convert(None)


def numeric(series):
    return pd.to_numeric(series, errors="coerce")


def normalize_percent(series):
    values = numeric(series)

    if RISK_PERCENT_UNIT == "fraction":
        return values * 100

    if RISK_PERCENT_UNIT == "percent_points":
        return values

    valid = values.dropna()

    if len(valid) and valid.abs().quantile(0.95) <= 0.05:
        return values * 100

    return values


def profit_factor(values):
    values = numeric(pd.Series(values)).dropna()

    gross_profit = values[values > 0].sum()
    gross_loss = abs(values[values < 0].sum())

    if gross_loss == 0:
        return np.inf if gross_profit > 0 else np.nan

    return gross_profit / gross_loss


def performance_summary(group):
    pnl = numeric(group["Net_PNL"]).dropna()

    if pnl.empty:
        return pd.Series({
            "Trade_Count": 0,
            "Net_PNL": 0,
            "Gross_Profit": 0,
            "Gross_Loss": 0,
            "Win_Rate_Pct": np.nan,
            "Profit_Factor": np.nan,
            "Average_PNL": np.nan,
            "Expectancy": np.nan
        })

    wins = pnl[pnl > 0]
    losses = pnl[pnl < 0]

    return pd.Series({
        "Trade_Count": len(pnl),
        "Net_PNL": pnl.sum(),
        "Gross_Profit": wins.sum(),
        "Gross_Loss": abs(losses.sum()),
        "Win_Rate_Pct": (pnl > 0).mean() * 100,
        "Profit_Factor": profit_factor(pnl),
        "Average_PNL": pnl.mean(),
        "Expectancy": pnl.mean()
    })


def save_csv(df, filename):
    path = OUTPUT_DIR / filename
    df.to_csv(path, index=False)
    logger.info("Created %s", filename)


def save_chart(filename):
    plt.tight_layout()
    plt.savefig(
        CHART_DIR / filename,
        dpi=160,
        bbox_inches="tight"
    )
    plt.close()


# ============================================================
# 1. TRADE EXECUTION DATA
# ============================================================

def load_trades():

    df = read_input(TRADE_FILE, "Trade execution outcomes")

    aliases = {
        "Trade_ID": ["Trade Id", "Trade_ID", "TradeID"],
        "Entry_Time": ["Entry time", "Entry_Time", "EntryTime"],
        "Exit_Time": ["Exit time", "Exit_Time", "ExitTime"],
        "Symbol": ["Symbol", "Pair"],
        "Family": ["Family", "Strategy Family"],
        "Strategy": ["Strategy", "Strategy Name"],
        "Timeframe": ["Timeframe", "Time Frame"],
        "Side": ["Side", "Direction"],
        "Entry_Price": ["Entry price", "Entry_Price"],
        "Exit_Price": ["Exit price", "Exit_Price"],
        "Stop_Loss": ["Stop loss", "Stop_Loss"],
        "Take_Profit": ["Take profit", "Take_Profit"],
        "Position_Size": ["Position size", "Position_Size"],
        "Risk_Amount": ["Risk amount", "Risk_Amount"],
        "Risk_Percent": ["Risk percent", "Risk_Percent"],
        "Net_PNL": ["Net PNL", "Net_PNL", "NetPnL"],
        "Entry_Fee": ["Entry fee", "Entry_Fee"],
        "Exit_Fee": ["Exit fee", "Exit_Fee"],
        "Trade_Status": ["Trade status", "Trade_Status", "Status"]
    }

    output = pd.DataFrame(index=df.index)

    for target, candidates in aliases.items():
        col = find_column(
            df,
            candidates,
            required=target in [
                "Trade_ID", "Entry_Time", "Symbol", "Net_PNL"
            ]
        )

        output[target] = df[col] if col else np.nan

    output["Entry_Time"] = parse_datetime(output["Entry_Time"])
    output["Exit_Time"] = parse_datetime(output["Exit_Time"])

    numeric_columns = [
        "Entry_Price", "Exit_Price", "Stop_Loss",
        "Take_Profit", "Position_Size", "Risk_Amount",
        "Net_PNL", "Entry_Fee", "Exit_Fee"
    ]

    for col in numeric_columns:
        output[col] = numeric(output[col])

    output["Risk_Percent"] = normalize_percent(
        output["Risk_Percent"]
    )

    output["Symbol"] = (
        output["Symbol"].astype(str).str.upper().str.strip()
    )

    output["Family"] = (
        output["Family"].fillna("UNKNOWN").astype(str).str.upper()
    )

    output["Trade_ID"] = output["Trade_ID"].astype(str)

    # Exclude open and pending trades.
    if output["Trade_Status"].notna().any():
        status = output["Trade_Status"].astype(str).str.lower()

        output = output[
            ~status.str.contains(
                r"open|pending|active",
                na=False
            )
        ].copy()

    output = output.dropna(
        subset=["Trade_ID", "Entry_Time", "Symbol", "Net_PNL"]
    )

    # R-multiple = realized net P&L / planned monetary risk.
    output["R_Multiple"] = np.where(
        output["Risk_Amount"].abs() > 0,
        output["Net_PNL"] / output["Risk_Amount"].abs(),
        np.nan
    )

    logger.info("Valid completed trades: %s", len(output))

    return output.reset_index(drop=True)


# ============================================================
# 2. PORTFOLIO EQUITY HISTORY
# ============================================================

def load_equity():

    df = read_input(EQUITY_FILE, "Portfolio equity history")

    time_col = find_column(
        df,
        ["Timestamp", "Time", "Date", "Snapshot time"],
        required=True
    )

    equity_col = find_column(
        df,
        ["Equity", "Account Equity", "Total Equity"],
        required=True
    )

    optional = {
        "Balance": ["Balance", "Account Balance"],
        "Realized_PNL": ["Realized PNL", "Realized_PnL"],
        "Unrealized_PNL": ["Unrealized PNL", "Unrealized_PnL"],
        "Used_Margin": ["Used margin", "Used_Margin"],
        "Available_Margin": ["Available margin", "Available_Margin"],
        "Portfolio_Exposure": ["Portfolio exposure", "Portfolio_Exposure"],
        "Portfolio_Risk": ["Portfolio risk", "Portfolio_Risk"],
        "Portfolio_Risk_Percent": [
            "Portfolio risk percent",
            "Portfolio_Risk_Percent"
        ],
        "Open_Positions": ["Open positions", "Open_Positions"]
    }

    result = pd.DataFrame({
        "Timestamp": parse_datetime(df[time_col]),
        "Equity": numeric(df[equity_col])
    })

    for target, candidates in optional.items():
        col = find_column(df, candidates)
        result[target] = (
            numeric(df[col]) if col else np.nan
        )

    result["Portfolio_Risk_Percent"] = normalize_percent(
        result["Portfolio_Risk_Percent"]
    )

    result = result.dropna(
        subset=["Timestamp", "Equity"]
    )

    result = result.sort_values("Timestamp")
    result = result.drop_duplicates(
        "Timestamp",
        keep="last"
    ).reset_index(drop=True)

    result["Peak_Equity"] = result["Equity"].cummax()

    result["Drawdown_Amount"] = (
        result["Equity"] - result["Peak_Equity"]
    )

    result["Drawdown_Pct"] = np.where(
        result["Peak_Equity"] > 0,
        result["Drawdown_Amount"]
        / result["Peak_Equity"] * 100,
        np.nan
    )

    result["Underwater"] = result["Drawdown_Amount"] < 0

    return result


# ============================================================
# 3. RISK ALLOCATION DECISIONS
# ============================================================

def load_risk_decisions():

    df = read_input(RISK_FILE, "Risk allocation decisions")

    aliases = {
        "Trade_ID": ["Trade Id", "Trade_ID", "TradeID"],
        "Timestamp": ["Timestamp", "Decision time", "Decision_Time"],
        "Base_Risk": ["Base risk per trade", "Base_Risk_Per_Trade"],
        "Requested_Risk": ["Requested risk", "Requested_Risk"],
        "Approved_Risk": ["Approved risk", "Approved_Risk"],
        "Actual_Risk": ["Actual risk", "Actual_Risk"],
        "Family_Allocation": ["Family allocation", "Family_Allocation"],
        "Meta_Allocation": ["Meta allocation", "Meta_Allocation"],
        "Portfolio_Risk_Before": [
            "Current portfolio risk",
            "Current_Portfolio_Risk",
            "Portfolio_Risk_Before"
        ],
        "Max_Portfolio_Risk": [
            "Max portfolio risk",
            "Max_Portfolio_Risk"
        ],
        "Allocation_Factor": ["Allocation factor", "Allocation_Factor"],
        "Health_Score": ["Health score", "Health_Score"],
        "Health_Threshold": ["Health threshold", "Health_Threshold"],
        "Risk_Decision": ["Risk decision", "Risk_Decision", "Decision"],
        "Rejection_Reason": [
            "Risk rejection reason",
            "Risk_Rejection_Reason",
            "Rejection Reason"
        ],
        "Symbol": ["Symbol", "Pair"],
        "Family": ["Family", "Strategy Family"]
    }

    result = pd.DataFrame(index=df.index)

    for target, candidates in aliases.items():
        col = find_column(df, candidates)
        result[target] = df[col] if col else np.nan

    result["Timestamp"] = parse_datetime(result["Timestamp"])

    result["Trade_ID"] = result["Trade_ID"].astype(str)

    for col in result.columns:
        if col in ["Timestamp", "Trade_ID", "Risk_Decision",
                   "Rejection_Reason", "Symbol", "Family"]:
            continue

        if col in ["Base_Risk", "Family_Allocation", "Meta_Allocation",
                   "Max_Portfolio_Risk"]:
            result[col] = normalize_percent(result[col])
        else:
            result[col] = numeric(result[col])

    return result


# ============================================================
# 4. OPEN POSITION SNAPSHOTS
# ============================================================

def load_positions():

    df = read_input(POSITION_FILE, "Open position snapshots")

    aliases = {
        "Timestamp": ["Timestamp", "Snapshot time", "Snapshot_Time"],
        "Trade_ID": ["Trade Id", "Trade_ID", "TradeID"],
        "Symbol": ["Symbol", "Pair"],
        "Family": ["Family", "Strategy Family"],
        "Side": ["Side", "Direction"],
        "Position_Size": ["Position size", "Position_Size"],
        "Entry_Price": ["Entry price", "Entry_Price"],
        "Mark_Price": ["Mark price", "Mark_Price"],
        "Stop_Loss": ["Stop loss", "Stop_Loss"],
        "Remaining_Risk": ["Remaining risk", "Remaining_Risk"],
        "Unrealized_PNL": ["Unrealized PNL", "Unrealized_PNL"],
        "Margin_Used": ["Margin used", "Margin_Used"]
    }

    result = pd.DataFrame(index=df.index)

    for target, candidates in aliases.items():
        col = find_column(
            df,
            candidates,
            required=(target == "Timestamp")
        )
        result[target] = df[col] if col else np.nan

    result["Timestamp"] = parse_datetime(result["Timestamp"])

    for col in [
        "Position_Size", "Entry_Price", "Mark_Price",
        "Stop_Loss", "Remaining_Risk",
        "Unrealized_PNL", "Margin_Used"
    ]:
        result[col] = numeric(result[col])

    for col in ["Symbol", "Family", "Side"]:
        result[col] = result[col].fillna("UNKNOWN").astype(str).str.upper()

    result = result.dropna(subset=["Timestamp"])
    return result


# ============================================================
# REPORT 1: RISK PERFORMANCE
# ============================================================

def create_risk_performance(trades):

    reports = []

    summary = performance_summary(trades)
    summary["Group_Type"] = "OVERALL"
    summary["Group"] = "ALL"
    reports.append(summary)

    for dimension in ["Family", "Symbol", "Timeframe", "Side"]:

        if dimension not in trades.columns:
            continue

        if trades[dimension].isna().all():
            continue

        for key, group in trades.groupby(
            dimension,
            dropna=False
        ):

            row = performance_summary(group)
            row["Group_Type"] = dimension.upper()
            row["Group"] = str(key)

            reports.append(row)

    report = pd.DataFrame(reports)

    overall_mask = report["Group_Type"] == "OVERALL"

    report["Average_R_Multiple"] = np.nan
    report["Median_R_Multiple"] = np.nan
    report["Average_Risk_Amount"] = np.nan
    report["Average_Risk_Percent"] = np.nan

    r = trades["R_Multiple"].dropna()

    report.loc[overall_mask, "Average_R_Multiple"] = (
        r.mean() if len(r) else np.nan
    )

    report.loc[overall_mask, "Median_R_Multiple"] = (
        r.median() if len(r) else np.nan
    )

    report.loc[overall_mask, "Average_Risk_Amount"] = (
        trades["Risk_Amount"].abs().mean()
    )

    report.loc[overall_mask, "Average_Risk_Percent"] = (
        trades["Risk_Percent"].mean()
    )

    save_csv(report, "risk_performance.csv")

    return report


# ============================================================
# REPORT 2: DRAWDOWN ANALYSIS
# ============================================================

def create_drawdown_analysis(equity):

    if equity.empty:
        raise ValueError("No valid equity records found.")

    worst_idx = equity["Drawdown_Pct"].idxmin()
    worst = equity.loc[worst_idx]

    previous = equity.loc[:worst_idx]
    peak_idx = previous["Equity"].idxmax()

    peak_time = equity.loc[peak_idx, "Timestamp"]
    trough_time = worst["Timestamp"]

    recovery_rows = equity.loc[worst_idx + 1:]

    recovery_rows = recovery_rows[
        recovery_rows["Equity"] >= worst["Peak_Equity"]
    ]

    recovery_time = (
        recovery_rows.iloc[0]["Timestamp"]
        if len(recovery_rows)
        else pd.NaT
    )

    recovery_hours = (
        (recovery_time - trough_time).total_seconds() / 3600
        if pd.notna(recovery_time)
        else np.nan
    )

    summary = pd.DataFrame([{
        "Start_Equity": equity.iloc[0]["Equity"],
        "End_Equity": equity.iloc[-1]["Equity"],
        "Net_Equity_Change": (
            equity.iloc[-1]["Equity"] - equity.iloc[0]["Equity"]
        ),
        "Total_Return_Pct": (
            (equity.iloc[-1]["Equity"] / equity.iloc[0]["Equity"] - 1) * 100
            if equity.iloc[0]["Equity"] > 0 else np.nan
        ),
        "Maximum_Drawdown_Pct": worst["Drawdown_Pct"],
        "Maximum_Drawdown_Amount": worst["Drawdown_Amount"],
        "Peak_Time": peak_time,
        "Trough_Time": trough_time,
        "Recovery_Time": recovery_time,
        "Recovery_Hours": recovery_hours,
        "Equity_Observations": len(equity)
    }])

    save_csv(summary, "drawdown_analysis.csv")
    save_csv(equity, "equity_curve_with_drawdown.csv")

    return summary


# ============================================================
# REPORT 3: RISK ALLOCATION ANALYSIS
# ============================================================

def create_risk_allocation_analysis(trades, decisions):

    report_rows = []

    # Compare requested risk against approved risk.
    for first, second, label in [
        ("Requested_Risk", "Approved_Risk", "REQUESTED_VS_APPROVED"),
        ("Approved_Risk", "Actual_Risk", "APPROVED_VS_ACTUAL")
    ]:

        valid = decisions[[first, second]].dropna()

        if valid.empty:
            continue

        report_rows.append({
            "Comparison": label,
            "Observation_Count": len(valid),
            "Mean_First_Value": valid[first].mean(),
            "Mean_Second_Value": valid[second].mean(),
            "Mean_Difference": (
                valid[second] - valid[first]
            ).mean(),
            "Reduced_Count": int(
                (valid[second] < valid[first]).sum()
            ),
            "Increased_Count": int(
                (valid[second] > valid[first]).sum()
            ),
            "Unchanged_Count": int(
                (valid[second] == valid[first]).sum()
            )
        })

    report = pd.DataFrame(report_rows)

    save_csv(report, "risk_allocation_analysis.csv")

    # Risk decision distribution.
    if decisions["Risk_Decision"].notna().any():

        distribution = (
            decisions["Risk_Decision"]
            .astype(str)
            .str.upper()
            .value_counts()
            .rename_axis("Risk_Decision")
            .reset_index(name="Decision_Count")
        )

        distribution["Decision_Pct"] = (
            distribution["Decision_Count"]
            / distribution["Decision_Count"].sum() * 100
        )

        save_csv(
            distribution,
            "risk_decision_distribution.csv"
        )

    # Rejection reasons.
    if decisions["Rejection_Reason"].notna().any():

        rejection = (
            decisions["Rejection_Reason"]
            .dropna()
            .astype(str)
            .value_counts()
            .rename_axis("Rejection_Reason")
            .reset_index(name="Count")
        )

        save_csv(
            rejection,
            "risk_rejection_reasons.csv"
        )

    # Trade-level risk audit.
    audit_columns = [
        "Trade_ID", "Family", "Symbol",
        "Risk_Amount", "Risk_Percent",
        "Net_PNL", "R_Multiple"
    ]

    audit = trades[audit_columns].copy()

    save_csv(audit, "trade_level_risk_audit.csv")

    return report


# ============================================================
# REPORT 4: PORTFOLIO EXPOSURE ANALYSIS
# ============================================================

def create_portfolio_exposure_analysis(equity, positions):

    rows = []

    equity_metrics = [
        "Portfolio_Exposure",
        "Portfolio_Risk",
        "Portfolio_Risk_Percent",
        "Used_Margin",
        "Available_Margin",
        "Open_Positions"
    ]

    for col in equity_metrics:

        values = numeric(equity[col]).dropna()

        if values.empty:
            continue

        rows.append({
            "Metric": col,
            "Observation_Count": len(values),
            "Mean": values.mean(),
            "Median": values.median(),
            "Maximum": values.max(),
            "Minimum": values.min(),
            "P95": values.quantile(0.95)
        })

    if not positions.empty:

        snapshot = (
            positions.groupby("Timestamp")
            .agg(
                Open_Position_Count=("Timestamp", "size"),
                Total_Remaining_Risk=("Remaining_Risk", "sum"),
                Total_Unrealized_PNL=("Unrealized_PNL", "sum"),
                Total_Margin_Used=("Margin_Used", "sum")
            )
            .reset_index()
        )

        save_csv(
            snapshot,
            "portfolio_open_position_snapshots_aggregated.csv"
        )

        for col in [
            "Remaining_Risk",
            "Unrealized_PNL",
            "Margin_Used"
        ]:

            values = numeric(positions[col]).dropna()

            if values.empty:
                continue

            rows.append({
                "Metric": f"Position_{col}",
                "Observation_Count": len(values),
                "Mean": values.mean(),
                "Median": values.median(),
                "Maximum": values.max(),
                "Minimum": values.min(),
                "P95": values.quantile(0.95)
            })

    report = pd.DataFrame(rows)

    save_csv(
        report,
        "portfolio_exposure_analysis.csv"
    )

    return report


# ============================================================
# CHARTS
# ============================================================

def create_charts(trades, equity, decisions, positions):

    logger.info("Generating charts...")

    # 1. Equity curve
    plt.figure(figsize=(12, 5))
    plt.plot(equity["Timestamp"], equity["Equity"])
    plt.title("Portfolio Equity Curve")
    plt.xlabel("Time")
    plt.ylabel("Equity")
    plt.xticks(rotation=20)
    save_chart("01_portfolio_equity_curve.png")

    # 2. Drawdown
    plt.figure(figsize=(12, 4))
    plt.fill_between(
        equity["Timestamp"],
        equity["Drawdown_Pct"],
        0
    )
    plt.title("Portfolio Drawdown")
    plt.xlabel("Time")
    plt.ylabel("Drawdown (%)")
    plt.xticks(rotation=20)
    save_chart("02_portfolio_drawdown.png")

    # 3. R-multiple distribution
    r = trades["R_Multiple"].dropna()

    if len(r):
        lower = r.quantile(0.01)
        upper = r.quantile(0.99)

        plt.figure(figsize=(9, 5))
        plt.hist(r.clip(lower=lower, upper=upper), bins=40)
        plt.axvline(0, linewidth=0.8)
        plt.title("Trade R-Multiple Distribution")
        plt.xlabel("R-Multiple (1st–99th percentile clipped)")
        plt.ylabel("Trade Count")
        save_chart("03_r_multiple_distribution.png")

    # 4. Family P&L
    family_pnl = (
        trades.groupby("Family")["Net_PNL"]
        .sum()
        .sort_values()
    )

    plt.figure(figsize=(11, 6))
    plt.barh(family_pnl.index.astype(str), family_pnl.values)
    plt.axvline(0, linewidth=0.8)
    plt.title("Net P&L by Strategy Family")
    plt.xlabel("Net P&L")
    save_chart("04_net_pnl_by_family.png")

    # 5. Trade risk percentage
    risk_pct = trades["Risk_Percent"].dropna()

    if len(risk_pct):
        plt.figure(figsize=(9, 5))
        plt.hist(risk_pct, bins=30)
        plt.title("Risk per Trade Distribution")
        plt.xlabel("Risk per Trade (%)")
        plt.ylabel("Trade Count")
        save_chart("05_trade_risk_percent_distribution.png")

    # 6. Risk engine decisions
    if decisions["Risk_Decision"].notna().any():

        counts = (
            decisions["Risk_Decision"]
            .astype(str)
            .str.upper()
            .value_counts()
        )

        plt.figure(figsize=(8, 5))
        plt.bar(counts.index, counts.values)
        plt.title("Risk Engine Decision Distribution")
        plt.xlabel("Risk Decision")
        plt.ylabel("Count")
        plt.xticks(rotation=20)
        save_chart("06_risk_decision_distribution.png")

    # 7. Remaining open risk
    if (
        not positions.empty
        and positions["Remaining_Risk"].notna().any()
    ):

        snapshot = (
            positions.groupby("Timestamp")["Remaining_Risk"]
            .sum()
            .reset_index()
        )

        plt.figure(figsize=(12, 5))
        plt.plot(
            snapshot["Timestamp"],
            snapshot["Remaining_Risk"]
        )
        plt.title("Aggregate Remaining Open Risk")
        plt.xlabel("Time")
        plt.ylabel("Remaining Risk")
        plt.xticks(rotation=20)
        save_chart("07_aggregate_open_risk.png")

    logger.info("Charts saved: %s", CHART_DIR)


# ============================================================
# MAIN
# ============================================================

def main():

    logger.info("=" * 65)
    logger.info("RESEARCH 05 - RISK MANAGEMENT EFFECTIVENESS")
    logger.info("=" * 65)

    trades = load_trades()
    equity = load_equity()
    decisions = load_risk_decisions()
    positions = load_positions()

    logger.info(
        "Trades=%s | Equity=%s | Risk decisions=%s | Positions=%s",
        len(trades),
        len(equity),
        len(decisions),
        len(positions)
    )

    # Preserve normalized source data for audit.
    save_csv(trades, "normalized_trade_data.csv")
    save_csv(equity, "normalized_equity_data.csv")
    save_csv(decisions, "normalized_risk_decisions.csv")
    save_csv(positions, "normalized_position_snapshots.csv")

    create_risk_performance(trades)

    create_drawdown_analysis(equity)

    create_risk_allocation_analysis(
        trades,
        decisions
    )

    create_portfolio_exposure_analysis(
        equity,
        positions
    )

    create_charts(
        trades,
        equity,
        decisions,
        positions
    )

    manifest = {
        "research": "05_risk_management_effectiveness",
        "trade_count": int(len(trades)),
        "equity_observation_count": int(len(equity)),
        "risk_decision_count": int(len(decisions)),
        "position_snapshot_count": int(len(positions)),
        "trade_start": str(trades["Entry_Time"].min()),
        "trade_end": str(trades["Entry_Time"].max()),
        "equity_start": str(equity["Timestamp"].min()),
        "equity_end": str(equity["Timestamp"].max()),
        "risk_percent_unit": RISK_PERCENT_UNIT,
        "configured_max_portfolio_risk_pct": (
            CONFIGURED_MAX_PORTFOLIO_RISK_PCT
        ),
        "notes": [
            "Drawdown is calculated from recorded equity observations.",
            "R-multiple uses Net_PNL divided by recorded Risk_Amount.",
            "Position snapshot aggregation assumes each row is one open position.",
            "Risk limit breaches require comparable risk units and matching timestamps.",
            "A risk-control counterfactual is not calculated by this script."
        ]
    }

    with open(
        OUTPUT_DIR / "run_manifest.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(manifest, f, indent=4)

    logger.info("=" * 65)
    logger.info("RESEARCH 05 COMPLETED")
    logger.info("Output directory: %s", OUTPUT_DIR)
    logger.info("=" * 65)


if __name__ == "__main__":
    main()

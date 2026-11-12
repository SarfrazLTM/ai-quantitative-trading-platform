#!/usr/bin/env python3
"""Transaction-cost sensitivity analysis for closed-trade backtest CSV files.

Expected input:
    data/raw/*.csv

Each CSV must contain at least:
    Net PNL, Exit time, Fee per side, Slippage per side

The fee/slippage columns in the supplied exports are expressed in percentage
points (for example, 0.05 means 0.05%, not 5%). The script preserves those
values and labels them accordingly; it does not re-apply costs to Net PNL.

Outputs:
    results/scenario_comparison.csv
    results/charts/net_pnl_comparison.png
    results/charts/profit_factor_comparison.png
    results/charts/realised_drawdown_comparison.png
    results/charts/cumulative_realised_pnl.png

Important:
    Each input CSV is treated as an independently generated backtest scenario.
    Trade populations can differ between scenarios. Therefore this script
    compares reported scenario outcomes; it does not claim to isolate the
    direct cost deduction on an identical set of trades.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REQUIRED_COLUMNS = {
    "Net PNL",
    "Exit time",
    "Fee per side",
    "Slippage per side",
}

OPTIONAL_METADATA_COLUMNS = ["Family", "Timeframe", "Symbol", "Entry time"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare backtest performance across fee/slippage CSV scenarios."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/raw"),
        help="Directory containing one CSV per fee/slippage scenario (default: data/raw).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results"),
        help="Directory for summary CSV and charts (default: results).",
    )
    parser.add_argument(
        "--family",
        default=None,
        help="Optional expected strategy family, e.g. TREND_PULLBACK.",
    )
    parser.add_argument(
        "--timeframe",
        default=None,
        help="Optional expected execution timeframe, e.g. 30m.",
    )
    return parser.parse_args()


def _single_numeric_value(series: pd.Series, column: str, file_path: Path) -> float:
    values = pd.to_numeric(series, errors="coerce").dropna().unique()
    if len(values) != 1:
        raise ValueError(
            f"{file_path.name}: expected exactly one distinct {column} value; "
            f"found {values.tolist()}"
        )
    return float(values[0])


def _profit_factor(pnl: pd.Series) -> float:
    gross_profit = pnl[pnl > 0].sum()
    gross_loss = -pnl[pnl < 0].sum()
    if gross_loss == 0:
        return math.inf if gross_profit > 0 else math.nan
    return float(gross_profit / gross_loss)


def _realised_equity_and_drawdown(df: pd.DataFrame) -> tuple[pd.Series, float]:
    """Return cumulative closed-trade P&L and absolute peak-to-trough drawdown.

    This is a realised-P&L curve starting at zero. It is not a mark-to-market
    account-equity curve and must not be reported as percentage drawdown.
    """
    ordered = df.sort_values(["_exit_time", "_source_row"], kind="stable")
    cumulative_pnl = ordered["_net_pnl"].cumsum()
    running_peak = cumulative_pnl.cummax().clip(lower=0)
    drawdown = cumulative_pnl - running_peak
    max_drawdown = float(drawdown.min()) if len(drawdown) else 0.0
    return cumulative_pnl.reset_index(drop=True), max_drawdown


def load_scenario(file_path: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    df = pd.read_csv(file_path)
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"{file_path.name}: missing required columns: {sorted(missing)}")

    df = df.copy()
    df["_source_row"] = np.arange(len(df))
    df["_net_pnl"] = pd.to_numeric(df["Net PNL"], errors="coerce")
    df["_exit_time"] = pd.to_datetime(df["Exit time"], errors="coerce")
    df["_fee_rate_pct"] = pd.to_numeric(df["Fee per side"], errors="coerce")
    df["_slippage_rate_pct"] = pd.to_numeric(df["Slippage per side"], errors="coerce")

    # Drop rows that cannot contribute to the requested closed-trade metrics.
    valid = df["_net_pnl"].notna() & df["_exit_time"].notna()
    invalid_rows = int((~valid).sum())
    df = df.loc[valid].copy()
    if df.empty:
        raise ValueError(f"{file_path.name}: no rows with valid Net PNL and Exit time.")

    fee_pct = _single_numeric_value(df["_fee_rate_pct"], "Fee per side", file_path)
    slippage_pct = _single_numeric_value(
        df["_slippage_rate_pct"], "Slippage per side", file_path
    )

    # Validate optional metadata, but do not infer missing metadata.
    metadata: dict[str, Any] = {}
    for col in OPTIONAL_METADATA_COLUMNS:
        if col in df.columns:
            non_null = df[col].dropna().astype(str).unique()
            metadata[col] = non_null[0] if len(non_null) == 1 else ", ".join(sorted(non_null))

    pnl = df["_net_pnl"]
    wins = pnl[pnl > 0]
    losses = pnl[pnl < 0]
    cumulative_pnl, max_drawdown = _realised_equity_and_drawdown(df)

    summary = {
        "source_file": file_path.name,
        "fee_per_side_pct": fee_pct,
        "slippage_per_side_pct": slippage_pct,
        "net_pnl": float(pnl.sum()),
        "win_rate_pct": float((pnl > 0).mean() * 100),
        "profit_factor": _profit_factor(pnl),
        "max_realised_drawdown_abs": max_drawdown,
        "gross_winning_net_pnl": float(wins.sum()),
        "gross_losing_net_pnl_abs": float(-losses.sum()),
        "average_net_pnl_per_trade": float(pnl.mean()),
        "median_net_pnl_per_trade": float(pnl.median()),
        "first_exit_time": df["_exit_time"].min(),
        "last_exit_time": df["_exit_time"].max(),
        "invalid_rows_excluded": invalid_rows,
        **{f"{k.lower().replace(' ', '_')}": v for k, v in metadata.items()},
    }
    return df, {**summary, "_cumulative_pnl": cumulative_pnl}


def format_scenario_label(row: pd.Series) -> str:
    return (
        f"Fee {row['fee_per_side_pct']:g}%\n"
        f"Slip {row['slippage_per_side_pct']:g}%"
    )


def save_bar_chart(
    summary: pd.DataFrame,
    metric: str,
    ylabel: str,
    title: str,
    output_path: Path,
    zero_line: bool = False,
) -> None:
    ordered = summary.sort_values(["fee_per_side_pct", "slippage_per_side_pct"])
    labels = [format_scenario_label(row) for _, row in ordered.iterrows()]
    values = ordered[metric].astype(float).to_numpy()

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.bar(labels, values)
    if zero_line:
        ax.axhline(0, linewidth=1)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Transaction fee and slippage assumptions (per side)")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def save_cumulative_chart(
    scenarios: list[tuple[pd.DataFrame, dict[str, Any]]], output_path: Path
) -> None:
    fig, ax = plt.subplots(figsize=(12, 6))
    for _, result in scenarios:
        cumulative = result["_cumulative_pnl"]
        label = (
            f"Fee {result['fee_per_side_pct']:g}% / "
            f"Slippage {result['slippage_per_side_pct']:g}%"
        )
        ax.plot(np.arange(len(cumulative)), cumulative.to_numpy(), label=label)
    ax.set_title("Cumulative Realised Net P&L by Cost Scenario")
    ax.set_xlabel("Closed trades ordered by exit time")
    ax.set_ylabel("Cumulative realised net P&L (reported P&L units)")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    if not args.input_dir.exists():
        raise SystemExit(
            f"Input directory not found: {args.input_dir}\n"
            "Create data/raw/ and place one CSV file for each scenario there."
        )

    csv_files = sorted(args.input_dir.glob("*.csv"))
    if not csv_files:
        raise SystemExit(f"No CSV files found in {args.input_dir}")

    loaded: list[tuple[pd.DataFrame, dict[str, Any]]] = []
    for file_path in csv_files:
        loaded.append(load_scenario(file_path))

    # Prevent accidental inclusion of multiple exports for the same cost setup.
    scenario_keys: dict[tuple[float, float], str] = {}
    for _, result in loaded:
        key = (result["fee_per_side_pct"], result["slippage_per_side_pct"])
        if key in scenario_keys:
            raise SystemExit(
                "Duplicate fee/slippage scenario detected: "
                f"{key}. Files: {scenario_keys[key]} and {result['source_file']}. "
                "Keep only one final CSV per scenario in data/raw/."
            )
        scenario_keys[key] = result["source_file"]

    summary = pd.DataFrame(
        [{k: v for k, v in result.items() if not k.startswith("_")} for _, result in loaded]
    )
    summary = summary.sort_values(
        ["fee_per_side_pct", "slippage_per_side_pct"]
    ).reset_index(drop=True)

    # Check strategy/timeframe consistency when those columns are available.
    for column, expected in [("family", args.family), ("timeframe", args.timeframe)]:
        if expected is not None:
            if column not in summary.columns:
                raise SystemExit(f"--{column} was supplied but CSV metadata is missing.")
            observed = set(summary[column].dropna().astype(str))
            if observed != {expected}:
                raise SystemExit(
                    f"Expected {column}={expected}, but found {sorted(observed)}"
                )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    charts_dir = args.output_dir / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)

    summary.to_csv(args.output_dir / "scenario_comparison.csv", index=False)

    save_bar_chart(
        summary,
        metric="net_pnl",
        ylabel="Net P&L (reported P&L units)",
        title="Net P&L Across Transaction-Cost Scenarios",
        output_path=charts_dir / "net_pnl_comparison.png",
        zero_line=True,
    )
    save_bar_chart(
        summary,
        metric="profit_factor",
        ylabel="Profit factor",
        title="Profit Factor Across Transaction-Cost Scenarios",
        output_path=charts_dir / "profit_factor_comparison.png",
    )
    save_bar_chart(
        summary,
        metric="max_realised_drawdown_abs",
        ylabel="Maximum realised drawdown (absolute P&L units)",
        title="Maximum Realised Drawdown Across Transaction-Cost Scenarios",
        output_path=charts_dir / "realised_drawdown_comparison.png",
        zero_line=True,
    )
    save_cumulative_chart(loaded, charts_dir / "cumulative_realised_pnl.png")

    display_columns = [
        "fee_per_side_pct",
        "slippage_per_side_pct",
        "net_pnl",
        "win_rate_pct",
        "profit_factor",
        "max_realised_drawdown_abs",
    ]
    print("\nTransaction Cost Sensitivity Results")
    print(summary[display_columns].to_string(index=False, float_format=lambda x: f"{x:,.4f}"))
    print(f"\nSummary written to: {args.output_dir / 'scenario_comparison.csv'}")
    print(f"Charts written to:  {charts_dir}")
    print("\nNote: Trade count is not used as a performance-ranking metric.")
    print("Note: Scenarios are independently generated; this is not fixed-trade cost attribution.")


if __name__ == "__main__":
    main()

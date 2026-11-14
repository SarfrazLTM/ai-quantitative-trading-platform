
from pathlib import Path
import json
import logging
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

MARKET_FILE = BASE_DIR / "RESEARCH_Jan2024_Sep2026_exported.parquet"
TRADES_DIR = BASE_DIR / "data" / "trades"
OUTPUT_DIR = BASE_DIR / "output"
CHART_DIR = OUTPUT_DIR / "charts"

START_DATE = pd.Timestamp("2024-01-15 00:00:00")
END_DATE = pd.Timestamp("2026-09-30 23:59:59")

MARKET_TIME_COL = "MergeTime"
TRADE_TIME_COL = "Entry_Time"
PNL_COL = "Net_PNL"
SYMBOL_COL = "Symbol"

# Preserve the previously discussed matching tolerance.
MAX_FEATURE_AGE_HOURS = 8

FAMILY_FILES = {
    "BREAKOUT_CONTINUATION": "breakout_continuation.csv",
    "COMPRESSION_BREAKOUT": "compression_breakout.csv",
    "LIQUIDITY_TRAP_REVERSAL": "liquidity_trap_reversal.csv",
    "MOMENTUM_REVERSION": "momentum_reversion.csv",
    "RANGE_REJECTION": "range_rejection.csv",
    "RANGE_REVERSION": "range_reversion.csv",
    "TREND_CONTINUATION": "trend_continuation.csv",
    "TREND_PULLBACK": "trend_pullback.csv",
}

# Set to True only if your Entry_Time values are UTC timestamps
# and you want to remove timezone information after conversion.
NORMALIZE_TO_UTC_NAIVE = True


# ============================================================
# LOGGING
# ============================================================

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(OUTPUT_DIR / "analysis.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=FutureWarning)


# ============================================================
# HELPERS
# ============================================================

def parse_datetime(series):
    """Parse timestamps and return consistent timezone-naive datetimes."""
    parsed = pd.to_datetime(series, errors="coerce", utc=True)

    if NORMALIZE_TO_UTC_NAIVE:
        return parsed.dt.tz_convert(None)

    return parsed


def find_column(df, candidates, required=False):

    def normalize(name):
        return "".join(
            char for char in str(name).lower()
            if char.isalnum()
        )

    lookup = {
        normalize(column): column
        for column in df.columns
    }

    for candidate in candidates:
        key = normalize(candidate)

        if key in lookup:
            return lookup[key]

    if required:
        raise ValueError(
            f"Required column not found. "
            f"Expected one of: {candidates}. "
            f"Available columns: {list(df.columns)}"
        )

    return None


def normalize_symbol(series):
    return series.astype(str).str.strip().str.upper()


def safe_profit_factor(pnl):
    pnl = pd.to_numeric(pnl, errors="coerce").dropna()

    gross_profit = pnl[pnl > 0].sum()
    gross_loss = abs(pnl[pnl < 0].sum())

    if gross_loss == 0:
        return np.inf if gross_profit > 0 else np.nan

    return gross_profit / gross_loss


def performance_summary(group):
    pnl = pd.to_numeric(group[PNL_COL], errors="coerce").dropna()

    if pnl.empty:
        return pd.Series({
            "Trade_Count": 0,
            "Net_PNL": 0.0,
            "Gross_Profit": 0.0,
            "Gross_Loss": 0.0,
            "Win_Rate": np.nan,
            "Profit_Factor": np.nan,
            "Average_PNL": np.nan,
            "Median_PNL": np.nan,
        })

    gross_profit = pnl[pnl > 0].sum()
    gross_loss = abs(pnl[pnl < 0].sum())

    return pd.Series({
        "Trade_Count": len(pnl),
        "Net_PNL": pnl.sum(),
        "Gross_Profit": gross_profit,
        "Gross_Loss": gross_loss,
        "Win_Rate": (pnl > 0).mean() * 100,
        "Profit_Factor": (
            gross_profit / gross_loss
            if gross_loss > 0
            else (np.inf if gross_profit > 0 else np.nan)
        ),
        "Average_PNL": pnl.mean(),
        "Median_PNL": pnl.median(),
    })


# ============================================================
# REGIME CLASSIFICATION
# ============================================================

def classify_direction(df):
    """
    Direction precedence:
    1. M30_Trend_Direction
    2. Trend_Direction
    3. Trend_Up / Trend_Down
    4. EMA20 versus EMA50
    """

    direction_col = find_column(
        df,
        ["M30_Trend_Direction", "Trend_Direction"]
    )

    if direction_col:
        direction = df[direction_col].astype(str).str.upper().str.strip()

        direction = direction.replace({
            "UP": "BULLISH",
            "DOWN": "BEARISH",
            "LONG": "BULLISH",
            "SHORT": "BEARISH",
            "1": "BULLISH",
            "-1": "BEARISH",
        })

        direction = direction.where(
            direction.isin(["BULLISH", "BEARISH"]),
            "UNKNOWN"
        )
        return direction

    up_col = find_column(df, ["Trend_Up"])
    down_col = find_column(df, ["Trend_Down"])

    if up_col and down_col:
        up = df[up_col].fillna(False).astype(bool)
        down = df[down_col].fillna(False).astype(bool)

        return pd.Series(
            np.select(
                [up, down],
                ["BULLISH", "BEARISH"],
                default="UNKNOWN",
            ),
            index=df.index,
        )

    ema20_col = find_column(df, ["EMA_20", "EMA20"])
    ema50_col = find_column(df, ["EMA_50", "EMA50"])

    if ema20_col and ema50_col:
        return pd.Series(
            np.select(
                [
                    df[ema20_col] > df[ema50_col],
                    df[ema20_col] < df[ema50_col],
                ],
                ["BULLISH", "BEARISH"],
                default="UNKNOWN",
            ),
            index=df.index,
        )

    logger.warning("No direction columns found. Direction set to UNKNOWN.")
    return pd.Series("UNKNOWN", index=df.index)


def classify_trend_state(df):
    """
    Precedence:
    TRANSITION -> RANGING -> TRENDING -> UNCLASSIFIED
    """

    transition_col = find_column(
        df, ["Is_Transition_Regime"]
    )

    ranging_col = find_column(
        df, ["Is_Ranging_Regime", "Sideways_Trend"]
    )

    trending_col = find_column(
        df, ["Is_Trending_Regime"]
    )

    if transition_col or ranging_col or trending_col:
        transition = (
            df[transition_col].fillna(False).astype(bool)
            if transition_col else pd.Series(False, index=df.index)
        )
        ranging = (
            df[ranging_col].fillna(False).astype(bool)
            if ranging_col else pd.Series(False, index=df.index)
        )
        trending = (
            df[trending_col].fillna(False).astype(bool)
            if trending_col else pd.Series(False, index=df.index)
        )

        return pd.Series(
            np.select(
                [transition, ranging, trending],
                ["TRANSITION", "RANGING", "TRENDING"],
                default="UNCLASSIFIED",
            ),
            index=df.index,
        )

    adx_col = find_column(df, ["ADX", "ADX_14"])
    threshold_col = find_column(
        df, ["Dynamic_ADX_Threshold", "ADX_Threshold"]
    )

    if adx_col:
        adx = pd.to_numeric(df[adx_col], errors="coerce")

        threshold = (
            pd.to_numeric(df[threshold_col], errors="coerce")
            if threshold_col
            else pd.Series(25.0, index=df.index)
        )

        return pd.Series(
            np.select(
                [
                    adx >= threshold,
                    adx < 25,
                ],
                ["TRENDING", "RANGING"],
                default="UNCLASSIFIED",
            ),
            index=df.index,
        )

    logger.warning("No trend-state columns found.")
    return pd.Series("UNCLASSIFIED", index=df.index)


def classify_volatility(df):
    """
    Primary:
    ATR_Percentile or BB_Width_Percentile.

    Fallback:
    ATR_Ratio.
    """

    percentile_col = find_column(
        df, ["ATR_Percentile", "BB_Width_Percentile"]
    )

    if percentile_col:
        percentile = pd.to_numeric(
            df[percentile_col], errors="coerce"
        )

        # Support percentile values represented as 0-100.
        if percentile.quantile(0.95) > 1.0:
            percentile = percentile / 100.0

        return pd.Series(
            np.select(
                [
                    percentile >= 0.80,
                    percentile <= 0.20,
                ],
                ["HIGH", "LOW"],
                default="NORMAL",
            ),
            index=df.index,
        ).where(percentile.notna(), "UNCLASSIFIED")

    atr_ratio_col = find_column(df, ["ATR_Ratio"])

    if atr_ratio_col:
        atr_ratio = pd.to_numeric(
            df[atr_ratio_col], errors="coerce"
        )

        return pd.Series(
            np.select(
                [
                    atr_ratio >= 1.25,
                    atr_ratio <= 0.80,
                ],
                ["HIGH", "LOW"],
                default="NORMAL",
            ),
            index=df.index,
        ).where(atr_ratio.notna(), "UNCLASSIFIED")

    logger.warning("No volatility columns found.")
    return pd.Series("UNCLASSIFIED", index=df.index)


def add_regime_columns(market):
    market["Direction"] = classify_direction(market)
    market["Trend_State"] = classify_trend_state(market)
    market["Volatility"] = classify_volatility(market)

    market["Combined_Regime"] = (
        market["Direction"].astype(str)
        + " | "
        + market["Trend_State"].astype(str)
        + " | "
        + market["Volatility"].astype(str)
    )

    return market


# ============================================================
# LOAD MARKET DATA
# ============================================================

def load_market_data():
    logger.info("Loading market parquet: %s", MARKET_FILE)

    if not MARKET_FILE.exists():
        raise FileNotFoundError(
            f"Market parquet not found: {MARKET_FILE}"
        )

    market = pd.read_parquet(MARKET_FILE)

    market_time_col = find_column(
        market,
        [MARKET_TIME_COL, "Merge_Time"],
        required=True,
    )

    symbol_col = find_column(
        market,
        [SYMBOL_COL, "symbol", "Pair"],
        required=True,
    )

    market = market.rename(columns={
        market_time_col: "_market_time",
        symbol_col: SYMBOL_COL,
    })

    market["_market_time"] = parse_datetime(
        market["_market_time"]
    )
    market[SYMBOL_COL] = normalize_symbol(
        market[SYMBOL_COL]
    )

    market = market.dropna(
        subset=["_market_time", SYMBOL_COL]
    )

    market = market[
        (market["_market_time"] >= START_DATE)
        & (market["_market_time"] <= END_DATE)
    ].copy()

    market = add_regime_columns(market)

    market = market.sort_values(
        ["_market_time", SYMBOL_COL]
    ).reset_index(drop=True)

    logger.info(
        "Market rows: %s | Symbols: %s",
        len(market),
        market[SYMBOL_COL].nunique(),
    )

    return market


# ============================================================
# LOAD FAMILY TRADES
# ============================================================

def load_family_trades():
    frames = []

    for family, filename in FAMILY_FILES.items():
        file_path = TRADES_DIR / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Trade file missing: {file_path}"
            )

        logger.info("Loading %s", filename)

        trades = pd.read_csv(file_path)

        entry_col = find_column(
            trades,
            [TRADE_TIME_COL, "EntryTime", "Entry Date"],
            required=True,
        )

        pnl_col = find_column(
            trades,
            [PNL_COL, "NetPnL", "Net PnL"],
            required=True,
        )

        symbol_col = find_column(
            trades,
            [SYMBOL_COL, "symbol", "Pair"],
            required=True,
        )

        trades = trades.rename(columns={
            entry_col: "_entry_time",
            pnl_col: PNL_COL,
            symbol_col: SYMBOL_COL,
        })

        trades["_entry_time"] = parse_datetime(
            trades["_entry_time"]
        )

        trades[SYMBOL_COL] = normalize_symbol(
            trades[SYMBOL_COL]
        )

        trades[PNL_COL] = pd.to_numeric(
            trades[PNL_COL], errors="coerce"
        )

        trades["Family"] = family

        # Exclude open, pending, and active trades when status exists.
        status_col = find_column(
            trades, ["Status", "Trade_Status"]
        )

        if status_col:
            status = (
                trades[status_col]
                .astype(str)
                .str.lower()
                .str.strip()
            )

            trades = trades[
                ~status.str.contains(
                    r"open|pending|active",
                    na=False,
                )
            ].copy()

        trades = trades.dropna(
            subset=["_entry_time", SYMBOL_COL, PNL_COL]
        )

        trades = trades[
            (trades["_entry_time"] >= START_DATE)
            & (trades["_entry_time"] <= END_DATE)
        ].copy()

        frames.append(trades)

    all_trades = pd.concat(
        frames,
        ignore_index=True,
        sort=False,
    )

    logger.info("Total closed trades: %s", len(all_trades))

    return all_trades


# ============================================================
# MATCH EACH TRADE TO ITS MARKET REGIME
# ============================================================

def match_trades_to_market(trades, market):
    logger.info("Matching trades with market regime data...")

    market_columns = [
        "_market_time",
        SYMBOL_COL,
        "Direction",
        "Trend_State",
        "Volatility",
        "Combined_Regime",
    ]

    market_subset = market[market_columns].copy()

    left = trades.copy()
    right = market_subset.copy()

    # Remove invalid timestamps before matching.
    left = left.dropna(subset=["_entry_time", SYMBOL_COL])
    right = right.dropna(subset=["_market_time", SYMBOL_COL])

    # Normalize symbol values.
    left[SYMBOL_COL] = normalize_symbol(left[SYMBOL_COL])
    right[SYMBOL_COL] = normalize_symbol(right[SYMBOL_COL])

    # IMPORTANT:
    # Sort globally by timestamp, not timestamp + symbol.
    left = left.sort_values(
        "_entry_time",
        kind="mergesort"
    ).reset_index(drop=True)

    right = right.sort_values(
        "_market_time",
        kind="mergesort"
    ).reset_index(drop=True)

    matched = pd.merge_asof(
        left,
        right,
        left_on="_entry_time",
        right_on="_market_time",
        by=SYMBOL_COL,
        direction="backward",
        tolerance=pd.Timedelta(
            hours=MAX_FEATURE_AGE_HOURS
        ),
        allow_exact_matches=True,
    )

    matched["Feature_Lag_Minutes"] = (
                                             matched["_entry_time"] - matched["_market_time"]
                                     ).dt.total_seconds() / 60.0

    matched["Match_Status"] = np.where(
        matched["_market_time"].notna(),
        "MATCHED",
        "UNMATCHED",
    )

    matched_count = matched["Match_Status"].eq("MATCHED").sum()
    unmatched_count = matched["Match_Status"].eq("UNMATCHED").sum()

    match_rate = (
        matched_count / len(matched) * 100
        if len(matched) else 0.0
    )

    logger.info(
        "Matched: %s | Unmatched: %s | Match rate: %.2f%%",
        matched_count,
        unmatched_count,
        match_rate,
    )

    return matched


# ============================================================
# REPORT 1: REGIME PERFORMANCE
# ============================================================

def create_regime_performance(matched):
    usable = matched[
        matched["Match_Status"] == "MATCHED"
    ].copy()

    dimensions = [
        "Direction",
        "Trend_State",
        "Volatility",
        "Combined_Regime",
    ]

    reports = []

    for dimension in dimensions:
        result = (
            usable.groupby(dimension, dropna=False)
            .apply(performance_summary)
            .reset_index()
        )

        result.insert(0, "Regime_Type", dimension)
        result = result.rename(
            columns={dimension: "Regime"}
        )

        reports.append(result)

    report = pd.concat(
        reports,
        ignore_index=True,
    )

    report.to_csv(
        OUTPUT_DIR / "regime_performance.csv",
        index=False,
    )

    logger.info("Created regime_performance.csv")

    return report


# ============================================================
# REPORT 2: FAMILY VS REGIME COMPARISON
# ============================================================

def create_family_regime_comparison(matched):
    usable = matched[
        matched["Match_Status"] == "MATCHED"
    ].copy()

    dimensions = [
        "Direction",
        "Trend_State",
        "Volatility",
        "Combined_Regime",
    ]

    reports = []

    for dimension in dimensions:
        result = (
            usable.groupby(
                ["Family", dimension],
                dropna=False,
            )
            .apply(performance_summary)
            .reset_index()
        )

        result.insert(1, "Regime_Type", dimension)
        result = result.rename(
            columns={dimension: "Regime"}
        )

        reports.append(result)

    report = pd.concat(
        reports,
        ignore_index=True,
    )

    report.to_csv(
        OUTPUT_DIR / "family_regime_comparison.csv",
        index=False,
    )

    logger.info("Created family_regime_comparison.csv")

    return report


# ============================================================
# REPORT 3: MARKET REGIME DISTRIBUTION
# ============================================================

def create_regime_distribution(market):
    dimensions = [
        "Direction",
        "Trend_State",
        "Volatility",
        "Combined_Regime",
    ]

    reports = []

    for dimension in dimensions:
        result = (
            market.groupby(dimension, dropna=False)
            .size()
            .reset_index(name="Observation_Count")
        )

        total = result["Observation_Count"].sum()

        result["Market_Distribution_Pct"] = (
            result["Observation_Count"] / total * 100
        )

        result.insert(0, "Regime_Type", dimension)
        result = result.rename(
            columns={dimension: "Regime"}
        )

        reports.append(result)

    report = pd.concat(
        reports,
        ignore_index=True,
    )

    report.to_csv(
        OUTPUT_DIR / "regime_distribution.csv",
        index=False,
    )

    logger.info("Created regime_distribution.csv")

    return report


# ============================================================
# CHARTS
# ============================================================

def save_chart(filename):
    plt.tight_layout()
    plt.savefig(
        CHART_DIR / filename,
        dpi=160,
        bbox_inches="tight",
    )
    plt.close()


def create_charts(
    regime_performance,
    family_comparison,
    regime_distribution,
    matched
):
    logger.info("Creating charts...")

    # --------------------------------------------------------
    # 1. Trend-state market distribution
    # --------------------------------------------------------

    dist = regime_distribution[
        regime_distribution["Regime_Type"] == "Trend_State"
    ].copy()

    dist = dist.sort_values(
        "Market_Distribution_Pct",
        ascending=False,
    )

    plt.figure(figsize=(9, 5))
    plt.bar(
        dist["Regime"].astype(str),
        dist["Market_Distribution_Pct"],
    )
    plt.title("Market Distribution by Trend State")
    plt.xlabel("Trend State")
    plt.ylabel("Market Observations (%)")
    plt.xticks(rotation=20)
    save_chart("01_trend_state_distribution.png")

    # --------------------------------------------------------
    # 2. Volatility distribution
    # --------------------------------------------------------

    dist = regime_distribution[
        regime_distribution["Regime_Type"] == "Volatility"
    ].copy()

    dist = dist.sort_values(
        "Market_Distribution_Pct",
        ascending=False,
    )

    plt.figure(figsize=(8, 5))
    plt.bar(
        dist["Regime"].astype(str),
        dist["Market_Distribution_Pct"],
    )
    plt.title("Market Distribution by Volatility")
    plt.xlabel("Volatility Regime")
    plt.ylabel("Market Observations (%)")
    save_chart("02_volatility_distribution.png")

    # --------------------------------------------------------
    # 3. Net P&L by trend state
    # --------------------------------------------------------

    perf = regime_performance[
        regime_performance["Regime_Type"] == "Trend_State"
    ].copy()

    perf = perf.sort_values("Net_PNL", ascending=False)

    plt.figure(figsize=(9, 5))
    plt.bar(
        perf["Regime"].astype(str),
        perf["Net_PNL"],
    )
    plt.axhline(0, linewidth=0.8)
    plt.title("Trading Performance by Trend State")
    plt.xlabel("Trend State")
    plt.ylabel("Net P&L")
    plt.xticks(rotation=20)
    save_chart("03_net_pnl_by_trend_state.png")

    # --------------------------------------------------------
    # 4. Profit factor by trend state
    # --------------------------------------------------------

    perf = regime_performance[
        regime_performance["Regime_Type"] == "Trend_State"
    ].copy()

    perf = perf.replace(
        [np.inf, -np.inf], np.nan
    ).dropna(subset=["Profit_Factor"])

    plt.figure(figsize=(9, 5))
    plt.bar(
        perf["Regime"].astype(str),
        perf["Profit_Factor"],
    )
    plt.axhline(1.0, linewidth=0.8)
    plt.title("Profit Factor by Trend State")
    plt.xlabel("Trend State")
    plt.ylabel("Profit Factor")
    save_chart("04_profit_factor_by_trend_state.png")

    # --------------------------------------------------------
    # 5. Family x trend-state profit factor
    # --------------------------------------------------------

    comp = family_comparison[
        family_comparison["Regime_Type"] == "Trend_State"
    ].copy()

    pivot = comp.pivot(
        index="Family",
        columns="Regime",
        values="Profit_Factor",
    )

    plt.figure(figsize=(11, 6))
    image = plt.imshow(
        pivot.replace([np.inf, -np.inf], np.nan),
        aspect="auto",
    )
    plt.colorbar(image, label="Profit Factor")
    plt.xticks(
        range(len(pivot.columns)),
        pivot.columns,
        rotation=20,
    )
    plt.yticks(
        range(len(pivot.index)),
        pivot.index,
    )
    plt.title("Strategy Family Profit Factor by Trend State")
    plt.xlabel("Trend State")
    plt.ylabel("Strategy Family")
    save_chart("05_family_trend_state_profit_factor.png")

    # --------------------------------------------------------
    # 6. Family x volatility profit factor
    # --------------------------------------------------------

    comp = family_comparison[
        family_comparison["Regime_Type"] == "Volatility"
    ].copy()

    pivot = comp.pivot(
        index="Family",
        columns="Regime",
        values="Profit_Factor",
    )

    plt.figure(figsize=(10, 6))
    image = plt.imshow(
        pivot.replace([np.inf, -np.inf], np.nan),
        aspect="auto",
    )
    plt.colorbar(image, label="Profit Factor")
    plt.xticks(
        range(len(pivot.columns)),
        pivot.columns,
        rotation=20,
    )
    plt.yticks(
        range(len(pivot.index)),
        pivot.index,
    )
    plt.title("Strategy Family Profit Factor by Volatility")
    plt.xlabel("Volatility")
    plt.ylabel("Strategy Family")
    save_chart("06_family_volatility_profit_factor.png")

    # --------------------------------------------------------
    # 7. Family net P&L comparison
    # --------------------------------------------------------

    overall = (
        matched[matched["Match_Status"] == "MATCHED"]
        .groupby("Family")
        .apply(performance_summary)
        .reset_index()
        .sort_values("Net_PNL", ascending=False)
    )

    plt.figure(figsize=(12, 6))
    plt.bar(
        overall["Family"],
        overall["Net_PNL"],
    )
    plt.axhline(0, linewidth=0.8)
    plt.title("Net P&L by Strategy Family")
    plt.xlabel("Strategy Family")
    plt.ylabel("Net P&L")
    plt.xticks(rotation=35, ha="right")
    save_chart("07_family_net_pnl.png")

    logger.info("Charts saved in %s", CHART_DIR)


# ============================================================
# MAIN
# ============================================================

def main():
    logger.info("=" * 65)
    logger.info("MARKET REGIME ANALYSIS")
    logger.info("Period: %s to %s", START_DATE, END_DATE)
    logger.info(
        "Maximum feature age: %s hours",
        MAX_FEATURE_AGE_HOURS,
    )
    logger.info("=" * 65)

    market = load_market_data()
    trades = load_family_trades()

    matched = match_trades_to_market(
        trades,
        market,
    )

    # Save trade-level matching output for audit.
    matched.to_csv(
        OUTPUT_DIR / "trades_with_entry_regime.csv",
        index=False,
    )

    unmatched = matched[
        matched["Match_Status"] == "UNMATCHED"
    ].copy()

    unmatched.to_csv(
        OUTPUT_DIR / "unmatched_trades.csv",
        index=False,
    )

    regime_performance = create_regime_performance(
        matched
    )

    family_comparison = create_family_regime_comparison(
        matched
    )

    regime_distribution = create_regime_distribution(
        market
    )

    create_charts(
        regime_performance,
        family_comparison,
        regime_distribution,
        matched
    )

    manifest = {
        "analysis_period": {
            "start": str(START_DATE),
            "end": str(END_DATE),
        },
        "market_file": str(MARKET_FILE),
        "market_rows": int(len(market)),
        "market_symbols": int(market[SYMBOL_COL].nunique()),
        "total_trades": int(len(matched)),
        "matched_trades": int(
            matched["Match_Status"].eq("MATCHED").sum()
        ),
        "unmatched_trades": int(
            matched["Match_Status"].eq("UNMATCHED").sum()
        ),
        "match_rate_pct": float(
            matched["Match_Status"].eq("MATCHED").mean() * 100
        ) if len(matched) else 0.0,
        "max_feature_age_hours": MAX_FEATURE_AGE_HOURS,
        "families": list(FAMILY_FILES.keys()),
    }

    with open(
        OUTPUT_DIR / "run_manifest.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(manifest, file, indent=4)

    logger.info("=" * 65)
    logger.info("ANALYSIS COMPLETED")
    logger.info("Output directory: %s", OUTPUT_DIR)
    logger.info("=" * 65)


if __name__ == "__main__":
    main()

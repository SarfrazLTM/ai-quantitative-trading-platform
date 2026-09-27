"""
Feature engineering pipeline.

Transforms validated market data into model-ready features.

The pipeline is responsible for orchestration and feature
lifecycle management. Exchange-specific logic and model-training
logic are intentionally kept outside this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

import pandas as pd

from ..data.schemas import MarketCandle


FeatureTransformer = Callable[[pd.DataFrame], pd.DataFrame]


@dataclass(frozen=True, slots=True)
class FeaturePipelineResult:
    """Result produced by the feature-engineering pipeline."""

    data: pd.DataFrame
    feature_columns: tuple[str, ...]


class FeaturePipeline:
    """
    Orchestrates quantitative feature generation.

    Feature transformations are supplied independently so that
    individual transformations can be tested and maintained
    without coupling the entire pipeline together.

    Example:

        pipeline = FeaturePipeline(
            transformers=[
                add_return_features,
                add_volatility_features,
            ]
        )

        result = pipeline.transform(candles)

        features = result.data
    """

    def __init__(
        self,
        transformers: Sequence[FeatureTransformer] | None = None,
    ) -> None:
        self.transformers = tuple(transformers or ())

    def transform(
        self,
        candles: Iterable[MarketCandle],
    ) -> FeaturePipelineResult:
        """
        Transform market candles into model-ready features.

        The pipeline performs:

        1. Market-candle normalization
        2. Transformer execution
        3. Feature-column identification
        """

        data = self._candles_to_dataframe(candles)

        if data.empty:
            return FeaturePipelineResult(
                data=data,
                feature_columns=(),
            )

        for transformer in self.transformers:
            data = transformer(data)

        feature_columns = self._identify_feature_columns(
            data
        )

        return FeaturePipelineResult(
            data=data,
            feature_columns=feature_columns,
        )

    @staticmethod
    def _candles_to_dataframe(
        candles: Iterable[MarketCandle],
    ) -> pd.DataFrame:
        """Convert canonical market candles into a DataFrame."""

        records = [
            {
                "symbol": candle.symbol,
                "timestamp": candle.timestamp,
                "open": candle.open,
                "high": candle.high,
                "low": candle.low,
                "close": candle.close,
                "volume": candle.volume,
                "timeframe": candle.timeframe,
            }
            for candle in candles
        ]

        if not records:
            return pd.DataFrame(
                columns=[
                    "symbol",
                    "timestamp",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "timeframe",
                ]
            )

        data = pd.DataFrame.from_records(records)

        return data.sort_values(
            ["symbol", "timestamp"],
            kind="stable",
        ).reset_index(drop=True)

    @staticmethod
    def _identify_feature_columns(
        data: pd.DataFrame,
    ) -> tuple[str, ...]:
        """Identify generated feature columns."""

        base_columns = {
            "symbol",
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "timeframe",
        }

        return tuple(
            column
            for column in data.columns
            if column not in base_columns
        )
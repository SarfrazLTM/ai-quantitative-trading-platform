"""
Canonical market-data schemas.

Defines the platform-level data contracts used across market-data
ingestion, validation, feature engineering, ML pipelines, and
runtime processing.

Exchange-specific adapters should convert external exchange
responses into these platform-level schemas.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class MarketEventType(StrEnum):
    """Supported real-time market event types."""

    TRADE = "trade"
    AGG_TRADE = "agg_trade"
    CANDLE = "candle"
    ORDER_BOOK = "order_book"
    MARK_PRICE = "mark_price"


@dataclass(frozen=True, slots=True)
class MarketCandle:
    """
    Canonical OHLCV candle representation.

    This model is independent of the exchange that supplied
    the market data.
    """

    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    timeframe: str

    def __post_init__(self) -> None:
        """Normalize basic fields after object creation."""

        object.__setattr__(
            self,
            "symbol",
            self.symbol.upper(),
        )

        object.__setattr__(
            self,
            "timeframe",
            self.timeframe.lower(),
        )


@dataclass(frozen=True, slots=True)
class MarketTick:
    """
    Canonical real-time trade event.

    Represents an individual trade or aggregated trade event
    received from a market-data source.
    """

    symbol: str
    price: float
    quantity: float
    timestamp: datetime
    event_type: MarketEventType = MarketEventType.AGG_TRADE

    def __post_init__(self) -> None:
        """Normalize the symbol."""

        object.__setattr__(
            self,
            "symbol",
            self.symbol.upper(),
        )


@dataclass(frozen=True, slots=True)
class MarketEvent:
    """
    Generic market event envelope.

    Provides a common representation for events entering the
    real-time quantitative runtime.
    """

    event_type: MarketEventType
    symbol: str
    timestamp: datetime
    payload: MarketCandle | MarketTick

    def __post_init__(self) -> None:
        """Normalize the symbol."""

        object.__setattr__(
            self,
            "symbol",
            self.symbol.upper(),
        )


@dataclass(frozen=True, slots=True)
class DataWindow:
    """
    Represents a requested historical market-data window.
    """

    symbol: str
    timeframe: str
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        """Normalize symbol and timeframe."""

        object.__setattr__(
            self,
            "symbol",
            self.symbol.upper(),
        )

        object.__setattr__(
            self,
            "timeframe",
            self.timeframe.lower(),
        )

        if self.end <= self.start:
            raise ValueError(
                "DataWindow end must be after start."
            )


@dataclass(frozen=True, slots=True)
class DataQualityStatus:
    """
    Represents the quality state of a market-data batch.
    """

    valid: bool
    record_count: int
    issue_count: int
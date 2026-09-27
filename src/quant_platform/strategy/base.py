"""
Core strategy abstractions.

Trading strategies consume market features and model predictions
and produce candidate trade decisions.

Proprietary strategy rules should be implemented separately and
are intentionally not included in this public repository.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

import pandas as pd


class SignalDirection(StrEnum):
    """Possible strategy directions."""

    LONG = "LONG"
    SHORT = "SHORT"
    NONE = "NONE"


@dataclass(frozen=True, slots=True)
class StrategyContext:
    """
    Context supplied to a trading strategy.

    The context intentionally separates market features from
    model predictions so that strategies can use both sources
    without owning the ML implementation.
    """

    symbol: str
    timeframe: str
    features: pd.DataFrame
    predictions: dict[str, Any]

    def __post_init__(self) -> None:
        """Normalize basic identifiers."""

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
class StrategyResult:
    """
    Result produced by a strategy evaluation.

    A strategy produces a candidate decision only.

    Portfolio allocation, risk approval, and execution happen
    downstream.
    """

    strategy_name: str
    symbol: str
    timeframe: str
    direction: SignalDirection
    confidence: float
    reason: str | None = None
    metadata: dict[str, Any] | None = None

    @property
    def is_candidate(self) -> bool:
        """Return whether the strategy produced a trade candidate."""

        return self.direction != SignalDirection.NONE


class TradingStrategy(ABC):
    """
    Abstract interface for systematic trading strategies.

    Implementations evaluate market context and return a candidate
    LONG, SHORT, or NONE decision.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the unique strategy name."""

        raise NotImplementedError

    @abstractmethod
    def evaluate(
        self,
        context: StrategyContext,
    ) -> StrategyResult:
        """
        Evaluate the strategy against the supplied context.
        """

        raise NotImplementedError
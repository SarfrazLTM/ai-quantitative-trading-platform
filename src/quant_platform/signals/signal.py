"""
Canonical trading signal models.

A TradingSignal represents an approved trade instruction produced
by the quantitative decision pipeline.

The signal is immutable after creation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True)
class TradingSignal:
    """
    Immutable canonical trading signal.

    A signal is generated only after portfolio and risk evaluation
    have approved the underlying candidate.
    """

    signal_id: UUID

    portfolio_id: str
    strategy_name: str

    symbol: str
    timeframe: str
    direction: str

    entry_price: float
    stop_loss: float
    take_profit: float

    quantity: float
    risk_amount: float

    created_at: datetime

    confidence: float

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """Validate and normalize signal fields."""

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

        direction = self.direction.upper()

        if direction not in {"LONG", "SHORT"}:
            raise ValueError(
                "direction must be LONG or SHORT."
            )

        object.__setattr__(
            self,
            "direction",
            direction,
        )

        if not self.portfolio_id:
            raise ValueError(
                "portfolio_id cannot be empty."
            )

        if not self.strategy_name:
            raise ValueError(
                "strategy_name cannot be empty."
            )

        if self.entry_price <= 0:
            raise ValueError(
                "entry_price must be greater than zero."
            )

        if self.stop_loss <= 0:
            raise ValueError(
                "stop_loss must be greater than zero."
            )

        if self.take_profit <= 0:
            raise ValueError(
                "take_profit must be greater than zero."
            )

        if self.quantity <= 0:
            raise ValueError(
                "quantity must be greater than zero."
            )

        if self.risk_amount < 0:
            raise ValueError(
                "risk_amount cannot be negative."
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0 and 1."
            )
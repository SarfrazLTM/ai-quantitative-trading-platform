"""
Position sizing.

Calculates position size from portfolio capital, configured
risk-per-trade, entry price, and stop-loss price.

This module does not determine whether a trade should be taken.
It only calculates the permitted position size.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PositionSize:
    """Result of a position-size calculation."""

    quantity: float
    notional_value: float
    risk_amount: float
    risk_per_unit: float
    entry_price: float
    stop_price: float

    @property
    def stop_distance(self) -> float:
        """Return absolute entry-to-stop distance."""

        return abs(
            self.entry_price - self.stop_price
        )


class PositionSizer:
    """
    Calculate position size using fixed-risk sizing.

    Formula:

        risk_amount =
            capital × risk_per_trade

        position_quantity =
            risk_amount / stop_distance

    Notional exposure is then:

        quantity × entry_price

    Leverage is not used to increase the allowed risk amount.
    It only affects the margin requirement at the execution venue.
    """

    def calculate(
        self,
        *,
        capital: float,
        risk_per_trade: float,
        entry_price: float,
        stop_price: float,
    ) -> PositionSize:
        """Calculate the permitted position size."""

        self._validate_inputs(
            capital=capital,
            risk_per_trade=risk_per_trade,
            entry_price=entry_price,
            stop_price=stop_price,
        )

        risk_amount = (
            capital * risk_per_trade
        )

        stop_distance = abs(
            entry_price - stop_price
        )

        quantity = (
            risk_amount / stop_distance
        )

        notional_value = (
            quantity * entry_price
        )

        return PositionSize(
            quantity=quantity,
            notional_value=notional_value,
            risk_amount=risk_amount,
            risk_per_unit=stop_distance,
            entry_price=entry_price,
            stop_price=stop_price,
        )

    @staticmethod
    def _validate_inputs(
        *,
        capital: float,
        risk_per_trade: float,
        entry_price: float,
        stop_price: float,
    ) -> None:
        """Validate position-sizing inputs."""

        if capital <= 0:
            raise ValueError(
                "capital must be greater than zero."
            )

        if not 0.0 < risk_per_trade <= 1.0:
            raise ValueError(
                "risk_per_trade must be between 0 and 1."
            )

        if entry_price <= 0:
            raise ValueError(
                "entry_price must be greater than zero."
            )

        if stop_price <= 0:
            raise ValueError(
                "stop_price must be greater than zero."
            )

        if entry_price == stop_price:
            raise ValueError(
                "entry_price and stop_price cannot be equal."
            )
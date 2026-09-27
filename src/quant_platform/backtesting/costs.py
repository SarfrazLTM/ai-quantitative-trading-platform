"""
Transaction-cost modelling.

Provides trading-fee and slippage calculations for historical
trade simulation.

Costs are deliberately separated from the simulator so that
different market assumptions can be tested without changing
trade-execution logic.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TransactionCost:
    """Transaction-cost breakdown for one execution."""

    notional: float
    fee: float
    slippage: float
    total: float


class CostModel:
    """
    Calculate transaction costs.

    Parameters are expressed as fractions:

        fee_rate = 0.0005
        0.05% per execution

        slippage_bps = 2
        2 basis points of slippage

    The model is deliberately simple and deterministic for
    backtesting.
    """

    def __init__(
        self,
        *,
        fee_rate: float = 0.0005,
        slippage_bps: float = 0.0,
    ) -> None:
        if fee_rate < 0:
            raise ValueError(
                "fee_rate cannot be negative."
            )

        if slippage_bps < 0:
            raise ValueError(
                "slippage_bps cannot be negative."
            )

        self.fee_rate = fee_rate
        self.slippage_bps = slippage_bps

    @property
    def slippage_rate(self) -> float:
        """Return slippage as a decimal fraction."""

        return self.slippage_bps / 10_000.0

    def calculate(
        self,
        *,
        notional: float,
    ) -> TransactionCost:
        """Calculate fee and slippage for an execution."""

        if notional < 0:
            raise ValueError(
                "notional cannot be negative."
            )

        fee = notional * self.fee_rate

        slippage = (
            notional * self.slippage_rate
        )

        return TransactionCost(
            notional=notional,
            fee=fee,
            slippage=slippage,
            total=fee + slippage,
        )

    def execution_price(
        self,
        *,
        price: float,
        side: str,
    ) -> float:
        """
        Apply execution slippage to a price.

        Buyers pay slightly more.

        Sellers receive slightly less.
        """

        if price <= 0:
            raise ValueError(
                "price must be greater than zero."
            )

        normalized_side = side.upper()

        if normalized_side == "BUY":
            return price * (
                1.0 + self.slippage_rate
            )

        if normalized_side == "SELL":
            return price * (
                1.0 - self.slippage_rate
            )

        raise ValueError(
            "side must be BUY or SELL."
        )
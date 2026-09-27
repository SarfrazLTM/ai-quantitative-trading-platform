"""
Adaptive portfolio allocation.

Determines a candidate allocation based on portfolio health and
configured allocation limits.

The allocation engine operates within portfolio constraints.
Final trade authorization belongs to the risk engine.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AllocationDecision:
    """Result of an adaptive allocation calculation."""

    portfolio_id: str
    allocation: float
    health_score: float
    reason: str


class AdaptiveAllocator:
    """
    Calculate adaptive portfolio allocation.

    Allocation is expressed as a fraction of the portfolio's
    configured allocation budget.

    Example:

        allocation = 0.60

        means 60% of the available allocation budget, not 60%
        of the entire trading account.
    """

    def __init__(
        self,
        minimum_allocation: float = 0.10,
        maximum_allocation: float = 1.00,
    ) -> None:

        if not 0.0 <= minimum_allocation <= 1.0:
            raise ValueError(
                "minimum_allocation must be between 0 and 1."
            )

        if not 0.0 <= maximum_allocation <= 1.0:
            raise ValueError(
                "maximum_allocation must be between 0 and 1."
            )

        if minimum_allocation > maximum_allocation:
            raise ValueError(
                "minimum_allocation cannot exceed "
                "maximum_allocation."
            )

        self.minimum_allocation = minimum_allocation
        self.maximum_allocation = maximum_allocation

    def calculate(
        self,
        *,
        portfolio_id: str,
        health_score: float,
        configured_allocation: float,
    ) -> AllocationDecision:
        """
        Calculate adaptive allocation.

        Health influences allocation within the configured
        allocation boundary.
        """

        health = self._bounded(
            health_score,
        )

        configured = self._bounded(
            configured_allocation,
        )

        allocation_range = (
            self.maximum_allocation
            - self.minimum_allocation
        )

        health_adjusted = (
            self.minimum_allocation
            + allocation_range * health
        )

        allocation = min(
            configured,
            health_adjusted,
        )

        return AllocationDecision(
            portfolio_id=portfolio_id,
            allocation=allocation,
            health_score=health,
            reason=(
                "Allocation adjusted according to portfolio "
                "health within configured limits."
            ),
        )

    @staticmethod
    def _bounded(
        value: float,
    ) -> float:
        """Clamp a value to the [0, 1] interval."""

        return max(
            0.0,
            min(1.0, value),
        )
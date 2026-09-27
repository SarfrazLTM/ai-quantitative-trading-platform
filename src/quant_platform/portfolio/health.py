"""
Portfolio health evaluation.

Calculates portfolio-level health metrics from runtime
performance information.

Health describes recent portfolio behaviour. It is distinct
from opportunity, which describes current market suitability.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HealthScore:
    """
    Represents a normalized portfolio health score.

    A score of 1.0 represents stronger observed health relative
    to the metrics supplied to the engine. It is not a prediction
    of future profitability.
    """

    value: float
    drawdown_component: float
    win_rate_component: float
    activity_component: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 1.0:
            raise ValueError(
                "Health score must be between 0 and 1."
            )


class PortfolioHealthEngine:
    """
    Calculate portfolio health from observed performance.

    This component does not predict market direction and does not
    decide whether an individual trade should be executed.
    """

    def calculate(
        self,
        *,
        current_drawdown: float,
        win_rate: float,
        trade_count: int,
        max_drawdown: float,
    ) -> HealthScore:
        """
        Calculate a normalized health score.

        The calculation is intentionally transparent for the
        public reference implementation.
        """

        drawdown_component = self._drawdown_score(
            current_drawdown,
            max_drawdown,
        )

        win_rate_component = self._bounded(
            win_rate,
        )

        activity_component = self._activity_score(
            trade_count,
        )

        value = (
            drawdown_component * 0.50
            + win_rate_component * 0.35
            + activity_component * 0.15
        )

        return HealthScore(
            value=self._bounded(value),
            drawdown_component=drawdown_component,
            win_rate_component=win_rate_component,
            activity_component=activity_component,
        )

    @staticmethod
    def _drawdown_score(
        current_drawdown: float,
        max_drawdown: float,
    ) -> float:
        """Convert drawdown into a normalized health component."""

        if max_drawdown <= 0:
            raise ValueError(
                "max_drawdown must be greater than zero."
            )

        current_drawdown = max(
            0.0,
            current_drawdown,
        )

        score = 1.0 - (
            current_drawdown / max_drawdown
        )

        return max(
            0.0,
            min(1.0, score),
        )

    @staticmethod
    def _activity_score(
        trade_count: int,
    ) -> float:
        """
        Produce a bounded activity component.

        The public implementation only distinguishes between
        insufficient and established activity.
        """

        if trade_count <= 0:
            return 0.0

        if trade_count >= 100:
            return 1.0

        return trade_count / 100.0

    @staticmethod
    def _bounded(
        value: float,
    ) -> float:
        """Clamp a value to the [0, 1] interval."""

        return max(
            0.0,
            min(1.0, value),
        )
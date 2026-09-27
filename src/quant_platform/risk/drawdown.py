"""
Portfolio drawdown management.

Tracks equity drawdown and determines the portfolio's current
drawdown state.

The drawdown controller does not generate trading signals.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DrawdownState(StrEnum):
    """Portfolio drawdown states."""

    NORMAL = "normal"
    REDUCED = "reduced"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class DrawdownResult:
    """Result of a drawdown evaluation."""

    state: DrawdownState
    current_drawdown: float
    peak_equity: float
    current_equity: float
    risk_multiplier: float


class DrawdownController:
    """
    Evaluate portfolio drawdown and determine risk state.

    Example:

        normal:
            full risk

        reduced:
            reduced risk

        blocked:
            no new trades
    """

    def __init__(
        self,
        *,
        reduced_threshold: float = 0.10,
        blocked_threshold: float = 0.20,
        reduced_risk_multiplier: float = 0.50,
    ) -> None:

        if not (
            0.0
            <= reduced_threshold
            < blocked_threshold
            <= 1.0
        ):
            raise ValueError(
                "Thresholds must satisfy "
                "0 <= reduced < blocked <= 1."
            )

        if not 0.0 <= reduced_risk_multiplier <= 1.0:
            raise ValueError(
                "reduced_risk_multiplier must be "
                "between 0 and 1."
            )

        self.reduced_threshold = (
            reduced_threshold
        )

        self.blocked_threshold = (
            blocked_threshold
        )

        self.reduced_risk_multiplier = (
            reduced_risk_multiplier
        )

    def evaluate(
        self,
        *,
        current_equity: float,
        peak_equity: float,
    ) -> DrawdownResult:
        """Evaluate current portfolio drawdown."""

        if current_equity < 0:
            raise ValueError(
                "current_equity cannot be negative."
            )

        if peak_equity <= 0:
            raise ValueError(
                "peak_equity must be greater than zero."
            )

        current_drawdown = (
            peak_equity - current_equity
        ) / peak_equity

        current_drawdown = max(
            0.0,
            current_drawdown,
        )

        if current_drawdown >= self.blocked_threshold:
            state = DrawdownState.BLOCKED
            multiplier = 0.0

        elif current_drawdown >= self.reduced_threshold:
            state = DrawdownState.REDUCED
            multiplier = (
                self.reduced_risk_multiplier
            )

        else:
            state = DrawdownState.NORMAL
            multiplier = 1.0

        return DrawdownResult(
            state=state,
            current_drawdown=current_drawdown,
            peak_equity=peak_equity,
            current_equity=current_equity,
            risk_multiplier=multiplier,
        )
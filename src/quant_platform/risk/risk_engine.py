"""
Centralized risk engine.

Coordinates position sizing, exposure validation, and drawdown
controls to determine whether a strategy candidate can proceed
toward signal generation.

The risk engine does not:
- Generate strategy signals
- Modify strategy logic
- Execute trades
- Dispatch webhooks
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..portfolio.portfolio import Portfolio, PortfolioRuntimeState
from ..strategy.base import SignalDirection, StrategyResult
from .drawdown import (
    DrawdownController,
    DrawdownResult,
    DrawdownState,
)
from .exposure import (
    ExposureCheckResult,
    ExposureManager,
    ExposureSnapshot,
)
from .position_sizing import (
    PositionSize,
    PositionSizer,
)


class RiskStatus(StrEnum):
    """Final risk-engine decision."""

    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class RiskDecision:
    """Final result of risk evaluation."""

    status: RiskStatus
    reason: str

    strategy_name: str
    symbol: str
    direction: SignalDirection

    position_size: PositionSize | None = None

    exposure: ExposureCheckResult | None = None

    drawdown: DrawdownResult | None = None

    @property
    def approved(self) -> bool:
        """Return whether the trade passed risk evaluation."""

        return self.status == RiskStatus.APPROVED


class RiskEngine:
    """
    Central risk-decision orchestrator.

    Processing order:

        1. Validate candidate
        2. Evaluate drawdown
        3. Calculate position size
        4. Apply drawdown risk multiplier
        5. Validate exposure
        6. Return APPROVED / REJECTED

    The engine does not send orders or webhooks.
    """

    def __init__(
        self,
        *,
        position_sizer: PositionSizer,
        exposure_manager: ExposureManager,
        drawdown_controller: DrawdownController,
    ) -> None:
        self.position_sizer = position_sizer
        self.exposure_manager = exposure_manager
        self.drawdown_controller = drawdown_controller

    def evaluate(
        self,
        *,
        candidate: StrategyResult,
        portfolio: Portfolio,
        runtime_state: PortfolioRuntimeState,
        exposure_snapshot: ExposureSnapshot,
        entry_price: float,
        stop_price: float,
    ) -> RiskDecision:
        """
        Evaluate a candidate trade against portfolio risk limits.
        """

        if candidate.direction == SignalDirection.NONE:
            return self._reject(
                candidate=candidate,
                reason="Strategy produced no trade candidate.",
            )

        if portfolio.state.value != "active":
            return self._reject(
                candidate=candidate,
                reason="Portfolio is not active.",
            )

        if candidate.symbol.upper() not in (
            portfolio.allowed_symbols
        ):
            return self._reject(
                candidate=candidate,
                reason=(
                    f"Symbol {candidate.symbol.upper()} "
                    "is not enabled for this portfolio."
                ),
            )

        # ----------------------------------------
        # 1. Drawdown evaluation
        # ----------------------------------------

        drawdown = self.drawdown_controller.evaluate(
            current_equity=runtime_state.equity,
            peak_equity=runtime_state.peak_equity,
        )

        if drawdown.state == DrawdownState.BLOCKED:
            return RiskDecision(
                status=RiskStatus.REJECTED,
                reason=(
                    "Portfolio is blocked because the current "
                    "drawdown exceeds the configured threshold."
                ),
                strategy_name=candidate.strategy_name,
                symbol=candidate.symbol,
                direction=candidate.direction,
                drawdown=drawdown,
            )

        # ----------------------------------------
        # 2. Position sizing
        # ----------------------------------------

        try:
            position_size = (
                self.position_sizer.calculate(
                    capital=runtime_state.equity,
                    risk_per_trade=portfolio.risk_per_trade,
                    entry_price=entry_price,
                    stop_price=stop_price,
                )
            )

        except ValueError as exc:
            return self._reject(
                candidate=candidate,
                reason=f"Position sizing failed: {exc}",
                drawdown=drawdown,
            )

        # ----------------------------------------
        # 3. Apply drawdown risk multiplier
        # ----------------------------------------

        adjusted_quantity = (
            position_size.quantity
            * drawdown.risk_multiplier
        )

        adjusted_notional = (
            position_size.notional_value
            * drawdown.risk_multiplier
        )

        adjusted_risk_amount = (
            position_size.risk_amount
            * drawdown.risk_multiplier
        )

        adjusted_position_size = PositionSize(
            quantity=adjusted_quantity,
            notional_value=adjusted_notional,
            risk_amount=adjusted_risk_amount,
            risk_per_unit=position_size.risk_per_unit,
            entry_price=position_size.entry_price,
            stop_price=position_size.stop_price,
        )

        # ----------------------------------------
        # 4. Exposure validation
        # ----------------------------------------

        exposure = self.exposure_manager.check(
            snapshot=exposure_snapshot,
            symbol=candidate.symbol,
            proposed_notional=(
                adjusted_position_size.notional_value
            ),
            capital=runtime_state.equity,
        )

        if not exposure.allowed:
            return RiskDecision(
                status=RiskStatus.REJECTED,
                reason=exposure.reason,
                strategy_name=candidate.strategy_name,
                symbol=candidate.symbol,
                direction=candidate.direction,
                position_size=adjusted_position_size,
                exposure=exposure,
                drawdown=drawdown,
            )

        # ----------------------------------------
        # 5. Final approval
        # ----------------------------------------

        return RiskDecision(
            status=RiskStatus.APPROVED,
            reason=(
                "Candidate passed drawdown, position-sizing, "
                "and exposure checks."
            ),
            strategy_name=candidate.strategy_name,
            symbol=candidate.symbol,
            direction=candidate.direction,
            position_size=adjusted_position_size,
            exposure=exposure,
            drawdown=drawdown,
        )

    @staticmethod
    def _reject(
        *,
        candidate: StrategyResult,
        reason: str,
        drawdown: DrawdownResult | None = None,
    ) -> RiskDecision:
        """Create a standardized rejected risk decision."""

        return RiskDecision(
            status=RiskStatus.REJECTED,
            reason=reason,
            strategy_name=candidate.strategy_name,
            symbol=candidate.symbol,
            direction=candidate.direction,
            drawdown=drawdown,
        )
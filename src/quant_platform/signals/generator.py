"""
Trading signal generation.

Converts an approved RiskDecision into a canonical TradingSignal.

Signal generation is intentionally downstream of portfolio and
risk evaluation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from ..risk.risk_engine import (
    RiskDecision,
    RiskStatus,
)
from ..strategy.base import SignalDirection
from .signal import TradingSignal


class SignalGenerator:
    """
    Generate canonical trading signals from approved risk decisions.

    Rejected risk decisions cannot be converted into trading
    signals.
    """

    def generate(
        self,
        *,
        decision: RiskDecision,
        portfolio_id: str,
        timeframe: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        confidence: float,
    ) -> TradingSignal:
        """
        Generate a TradingSignal from an approved risk decision.
        """

        self._validate_decision(
            decision,
        )

        if decision.position_size is None:
            raise ValueError(
                "Approved risk decision does not contain "
                "position-size information."
            )

        if decision.direction == SignalDirection.NONE:
            raise ValueError(
                "Cannot generate a signal with no direction."
            )

        return TradingSignal(
            signal_id=uuid4(),
            portfolio_id=portfolio_id,
            strategy_name=decision.strategy_name,
            symbol=decision.symbol,
            timeframe=timeframe,
            direction=decision.direction.value,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            quantity=decision.position_size.quantity,
            risk_amount=decision.position_size.risk_amount,
            created_at=datetime.now(
                timezone.utc,
            ),
            confidence=confidence,
            metadata={
                "risk_status": decision.status.value,
                "risk_reason": decision.reason,
                "notional_value": (
                    decision.position_size.notional_value
                ),
            },
        )

    @staticmethod
    def _validate_decision(
        decision: RiskDecision,
    ) -> None:
        """Ensure the risk decision is approved."""

        if decision.status != RiskStatus.APPROVED:
            raise ValueError(
                "Cannot generate a trading signal from "
                "a rejected risk decision."
            )
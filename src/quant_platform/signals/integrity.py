"""
Signal integrity.

Creates deterministic SHA-256 hashes for trading signals.

The hash provides tamper-evident integrity for the recorded
signal payload. It does not prove that a signal is correct,
profitable, or valid.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from .signal import TradingSignal


@dataclass(frozen=True, slots=True)
class SignalIntegrity:
    """Integrity information associated with a trading signal."""

    signal_id: str
    algorithm: str
    payload_hash: str


class SignalIntegrityService:
    """
    Generate deterministic cryptographic hashes for signals.

    SHA-256 is used for the public reference implementation.
    """

    ALGORITHM = "SHA-256"

    def create(
        self,
        signal: TradingSignal,
    ) -> SignalIntegrity:
        """Create an integrity record for a trading signal."""

        payload = self._canonical_payload(
            signal,
        )

        payload_bytes = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        digest = hashlib.sha256(
            payload_bytes
        ).hexdigest()

        return SignalIntegrity(
            signal_id=str(
                signal.signal_id
            ),
            algorithm=self.ALGORITHM,
            payload_hash=digest,
        )

    def verify(
        self,
        *,
        signal: TradingSignal,
        expected_hash: str,
    ) -> bool:
        """Verify that a signal matches a previously recorded hash."""

        integrity = self.create(signal)

        return integrity.payload_hash == expected_hash

    @staticmethod
    def _canonical_payload(
        signal: TradingSignal,
    ) -> dict[str, Any]:
        """
        Convert a signal into a deterministic JSON-compatible
        representation.
        """

        return {
            "signal_id": str(
                signal.signal_id
            ),
            "portfolio_id": signal.portfolio_id,
            "strategy_name": signal.strategy_name,
            "symbol": signal.symbol,
            "timeframe": signal.timeframe,
            "direction": signal.direction,
            "entry_price": signal.entry_price,
            "stop_loss": signal.stop_loss,
            "take_profit": signal.take_profit,
            "quantity": signal.quantity,
            "risk_amount": signal.risk_amount,
            "created_at": signal.created_at.isoformat(),
            "confidence": signal.confidence,
            "metadata": signal.metadata,
        }
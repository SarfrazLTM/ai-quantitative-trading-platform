"""
Webhook retry policies.

Provides bounded retry decisions and exponential backoff.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """
    Retry configuration for failed webhook deliveries.
    """

    max_attempts: int = 5
    initial_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    backoff_multiplier: float = 2.0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError(
                "max_attempts must be at least 1."
            )

        if self.initial_delay_seconds < 0:
            raise ValueError(
                "initial_delay_seconds cannot be negative."
            )

        if self.max_delay_seconds < 0:
            raise ValueError(
                "max_delay_seconds cannot be negative."
            )

        if self.backoff_multiplier < 1:
            raise ValueError(
                "backoff_multiplier must be >= 1."
            )

    def should_retry(
        self,
        attempt: int,
    ) -> bool:
        """
        Determine whether another attempt is allowed.

        `attempt` represents the attempt that just failed.
        """

        return attempt < self.max_attempts

    def delay_seconds(
        self,
        attempt: int,
    ) -> float:
        """Calculate exponential backoff delay."""

        delay = (
            self.initial_delay_seconds
            * (
                self.backoff_multiplier
                ** max(attempt - 1, 0)
            )
        )

        return min(
            delay,
            self.max_delay_seconds,
        )
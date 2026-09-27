"""
Trading strategy registry.

Maintains the collection of available strategies and provides
lookup by strategy name.
"""

from __future__ import annotations

from .base import TradingStrategy


class StrategyRegistry:
    """
    Registry of available trading strategies.

    The registry is responsible only for strategy discovery and
    lookup. It does not evaluate strategies.
    """

    def __init__(
        self,
        strategies: list[TradingStrategy] | None = None,
    ) -> None:
        self._strategies: dict[str, TradingStrategy] = {}

        for strategy in strategies or []:
            self.register(strategy)

    def register(
        self,
        strategy: TradingStrategy,
    ) -> None:
        """Register a strategy."""

        if strategy.name in self._strategies:
            raise ValueError(
                f"Strategy '{strategy.name}' is already registered."
            )

        self._strategies[strategy.name] = strategy

    def get(
        self,
        name: str,
    ) -> TradingStrategy:
        """Return a strategy by name."""

        try:
            return self._strategies[name]
        except KeyError as exc:
            raise KeyError(
                f"Strategy '{name}' is not registered."
            ) from exc

    def contains(
        self,
        name: str,
    ) -> bool:
        """Check whether a strategy exists."""

        return name in self._strategies

    def names(self) -> tuple[str, ...]:
        """Return registered strategy names."""

        return tuple(self._strategies.keys())

    def all(self) -> tuple[TradingStrategy, ...]:
        """Return all registered strategies."""

        return tuple(self._strategies.values())
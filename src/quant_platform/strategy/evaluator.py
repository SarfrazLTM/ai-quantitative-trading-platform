"""
Strategy evaluation engine.

Coordinates execution of registered trading strategies against
market context and model predictions.

This component produces candidate trade decisions only.
Portfolio and risk decisions occur downstream.
"""

from __future__ import annotations

from dataclasses import dataclass

from .base import StrategyContext, StrategyResult
from .registry import StrategyRegistry


@dataclass(frozen=True, slots=True)
class StrategyEvaluationResult:
    """Collection of strategy evaluation results."""

    results: tuple[StrategyResult, ...]

    @property
    def candidates(self) -> tuple[StrategyResult, ...]:
        """Return strategies that produced trade candidates."""

        return tuple(
            result
            for result in self.results
            if result.is_candidate
        )


class StrategyEvaluator:
    """
    Evaluate one or more registered strategies.

    The evaluator does not:
    - Allocate capital
    - Apply portfolio risk
    - Execute trades
    - Dispatch webhooks
    """

    def __init__(
        self,
        registry: StrategyRegistry,
    ) -> None:
        self.registry = registry

    def evaluate(
        self,
        context: StrategyContext,
        strategy_names: list[str] | None = None,
    ) -> StrategyEvaluationResult:
        """
        Evaluate selected strategies.

        If strategy_names is omitted, all registered strategies
        are evaluated.
        """

        names = (
            strategy_names
            if strategy_names is not None
            else list(self.registry.names())
        )

        results: list[StrategyResult] = []

        for name in names:
            strategy = self.registry.get(name)

            result = strategy.evaluate(context)

            self._validate_result(result)

            results.append(result)

        return StrategyEvaluationResult(
            results=tuple(results),
        )

    @staticmethod
    def _validate_result(
        result: StrategyResult,
    ) -> None:
        """Validate the basic strategy result contract."""

        if not 0.0 <= result.confidence <= 1.0:
            raise ValueError(
                f"Strategy '{result.strategy_name}' returned "
                f"invalid confidence: {result.confidence}"
            )
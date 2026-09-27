"""
Trading strategy evaluation.

Provides abstractions for evaluating market conditions and
machine-learning predictions against systematic trading strategies.
"""

from .base import (
    SignalDirection,
    StrategyContext,
    StrategyResult,
    TradingStrategy,
)
from .evaluator import StrategyEvaluator
from .registry import StrategyRegistry

__all__ = [
    "SignalDirection",
    "StrategyContext",
    "StrategyResult",
    "TradingStrategy",
    "StrategyEvaluator",
    "StrategyRegistry",
]
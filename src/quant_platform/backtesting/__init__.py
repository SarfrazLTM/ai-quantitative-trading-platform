"""
Backtesting infrastructure.

Provides historical strategy evaluation, trade simulation,
transaction-cost modelling, and performance analytics.

The backtesting layer reuses the platform's strategy, portfolio,
and risk abstractions rather than duplicating trading logic.
"""

from .costs import CostModel, TransactionCost
from .engine import BacktestEngine, BacktestResult
from .metrics import PerformanceMetrics, PerformanceReport
from .simulator import (
    BacktestSignal,
    SimulatedTrade,
    TradeSimulator,
)

__all__ = [
    "BacktestEngine",
    "BacktestResult",
    "BacktestSignal",
    "CostModel",
    "PerformanceMetrics",
    "PerformanceReport",
    "SimulatedTrade",
    "TradeSimulator",
    "TransactionCost",
]
"""
Backtest orchestration.

Coordinates historical signals, trade simulation, transaction
costs, and performance analysis.

The engine deliberately does not contain strategy rules.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .costs import CostModel
from .metrics import PerformanceMetrics, PerformanceReport
from .simulator import (
    BacktestSignal,
    SimulatedTrade,
    TradeSimulator,
)


@dataclass(frozen=True, slots=True)
class BacktestResult:
    """Complete result of a backtest."""

    trades: tuple[SimulatedTrade, ...]
    performance: PerformanceReport


class BacktestEngine:
    """
    Orchestrate historical strategy evaluation.

    The engine expects signals to have already been generated
    using point-in-time information.

    Responsibilities:

        Historical data
            ↓
        Signal collection
            ↓
        Trade simulation
            ↓
        Transaction costs
            ↓
        Performance metrics
    """

    def __init__(
        self,
        *,
        cost_model: CostModel | None = None,
        simulator: TradeSimulator | None = None,
        metrics: PerformanceMetrics | None = None,
    ) -> None:

        self.cost_model = (
            cost_model
            or CostModel()
        )

        self.simulator = (
            simulator
            or TradeSimulator(
                cost_model=self.cost_model,
            )
        )

        self.metrics = (
            metrics
            or PerformanceMetrics()
        )

    def run(
        self,
        *,
        candles: pd.DataFrame,
        signals: list[BacktestSignal],
        initial_capital: float,
    ) -> BacktestResult:
        """
        Run a complete backtest.

        Parameters
        ----------
        candles:
            Historical OHLCV data.

        signals:
            Strategy-generated historical signals.

        initial_capital:
            Starting portfolio capital.
        """

        if initial_capital <= 0:
            raise ValueError(
                "initial_capital must be greater than zero."
            )

        trades = self.simulator.simulate(
            candles=candles,
            signals=signals,
        )

        performance = self.metrics.calculate(
            trades=trades,
            initial_capital=initial_capital,
        )

        return BacktestResult(
            trades=tuple(trades),
            performance=performance,
        )
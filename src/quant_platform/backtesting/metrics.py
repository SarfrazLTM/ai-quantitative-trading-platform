"""
Backtest performance metrics.

Calculates standard quantitative performance statistics from
completed simulated trades and equity observations.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .simulator import SimulatedTrade


@dataclass(frozen=True, slots=True)
class PerformanceReport:
    """Summary of backtest performance."""

    initial_capital: float
    final_equity: float

    net_profit: float
    return_pct: float

    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float

    gross_profit: float
    gross_loss: float
    profit_factor: float

    max_drawdown: float
    max_drawdown_pct: float

    sharpe_ratio: float
    average_trade: float

    average_winner: float
    average_loser: float

    max_consecutive_wins: int
    max_consecutive_losses: int


class PerformanceMetrics:
    """
    Calculate performance metrics from simulated trades.
    """

    def calculate(
        self,
        *,
        trades: list[SimulatedTrade],
        initial_capital: float,
    ) -> PerformanceReport:
        """Calculate the complete performance report."""

        if initial_capital <= 0:
            raise ValueError(
                "initial_capital must be greater than zero."
            )

        if not trades:
            return PerformanceReport(
                initial_capital=initial_capital,
                final_equity=initial_capital,
                net_profit=0.0,
                return_pct=0.0,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                gross_profit=0.0,
                gross_loss=0.0,
                profit_factor=0.0,
                max_drawdown=0.0,
                max_drawdown_pct=0.0,
                sharpe_ratio=0.0,
                average_trade=0.0,
                average_winner=0.0,
                average_loser=0.0,
                max_consecutive_wins=0,
                max_consecutive_losses=0,
            )

        pnls = np.asarray(
            [trade.net_pnl for trade in trades],
            dtype=float,
        )

        final_equity = (
            initial_capital
            + float(pnls.sum())
        )

        net_profit = (
            final_equity
            - initial_capital
        )

        return_pct = (
            net_profit
            / initial_capital
        )

        winners = pnls[pnls > 0]
        losers = pnls[pnls < 0]

        gross_profit = float(
            winners.sum()
        )

        gross_loss = float(
            abs(losers.sum())
        )

        profit_factor = (
            gross_profit / gross_loss
            if gross_loss > 0
            else math.inf
            if gross_profit > 0
            else 0.0
        )

        win_rate = (
            len(winners)
            / len(pnls)
        )

        equity_curve = self._equity_curve(
            initial_capital,
            pnls,
        )

        max_drawdown, max_drawdown_pct = (
            self._drawdown(equity_curve)
        )

        returns = self._trade_returns(
            pnls,
            initial_capital,
        )

        sharpe_ratio = self._sharpe(
            returns,
        )

        return PerformanceReport(
            initial_capital=initial_capital,
            final_equity=final_equity,
            net_profit=net_profit,
            return_pct=return_pct,
            total_trades=len(pnls),
            winning_trades=len(winners),
            losing_trades=len(losers),
            win_rate=win_rate,
            gross_profit=gross_profit,
            gross_loss=gross_loss,
            profit_factor=profit_factor,
            max_drawdown=max_drawdown,
            max_drawdown_pct=max_drawdown_pct,
            sharpe_ratio=sharpe_ratio,
            average_trade=float(
                pnls.mean()
            ),
            average_winner=(
                float(winners.mean())
                if len(winners)
                else 0.0
            ),
            average_loser=(
                float(losers.mean())
                if len(losers)
                else 0.0
            ),
            max_consecutive_wins=(
                self._max_consecutive(
                    pnls,
                    positive=True,
                )
            ),
            max_consecutive_losses=(
                self._max_consecutive(
                    pnls,
                    positive=False,
                )
            ),
        )

    @staticmethod
    def _equity_curve(
        initial_capital: float,
        pnls: np.ndarray,
    ) -> np.ndarray:
        """Build an equity curve."""

        return initial_capital + np.cumsum(pnls)

    @staticmethod
    def _drawdown(
        equity_curve: np.ndarray,
    ) -> tuple[float, float]:
        """Calculate maximum absolute and percentage drawdown."""

        peaks = np.maximum.accumulate(
            equity_curve
        )

        drawdowns = (
            peaks - equity_curve
        )

        drawdown_pct = np.divide(
            drawdowns,
            peaks,
            out=np.zeros_like(drawdowns),
            where=peaks != 0,
        )

        return (
            float(drawdowns.max()),
            float(drawdown_pct.max()),
        )

    @staticmethod
    def _trade_returns(
        pnls: np.ndarray,
        initial_capital: float,
    ) -> np.ndarray:
        """Convert trade PnL into simple capital returns."""

        capital = initial_capital

        returns: list[float] = []

        for pnl in pnls:

            if capital <= 0:
                returns.append(0.0)
                continue

            trade_return = (
                pnl / capital
            )

            returns.append(trade_return)

            capital += pnl

        return np.asarray(
            returns,
            dtype=float,
        )

    @staticmethod
    def _sharpe(
        returns: np.ndarray,
    ) -> float:
        """Calculate a simple trade-level Sharpe ratio."""

        if len(returns) < 2:
            return 0.0

        std = float(
            np.std(
                returns,
                ddof=1,
            )
        )

        if std == 0:
            return 0.0

        return float(
            np.mean(returns) / std
            * math.sqrt(len(returns))
        )

    @staticmethod
    def _max_consecutive(
        pnls: np.ndarray,
        *,
        positive: bool,
    ) -> int:
        """Calculate maximum consecutive wins or losses."""

        maximum = 0
        current = 0

        for pnl in pnls:

            condition = (
                pnl > 0
                if positive
                else pnl < 0
            )

            if condition:
                current += 1
                maximum = max(
                    maximum,
                    current,
                )
            else:
                current = 0

        return maximum
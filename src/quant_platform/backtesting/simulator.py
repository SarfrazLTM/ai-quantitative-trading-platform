"""
Historical trade simulation.

Simulates position entry and exit using OHLC market data.

The simulator intentionally does not contain strategy logic.
It receives already-generated backtest signals and determines
how those positions would have behaved historically.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd

from .costs import CostModel


@dataclass(frozen=True, slots=True)
class BacktestSignal:
    """
    Strategy signal used by the backtest simulator.

    The signal is assumed to be generated at the close of the
    signal candle and therefore becomes executable on the next
    candle.
    """

    symbol: str
    timestamp: datetime
    direction: str
    entry_price: float
    stop_price: float
    take_profit: float
    quantity: float
    strategy_name: str
    timeframe: str

    def __post_init__(self) -> None:
        direction = self.direction.upper()

        if direction not in {"LONG", "SHORT"}:
            raise ValueError(
                "direction must be LONG or SHORT."
            )

        object.__setattr__(
            self,
            "direction",
            direction,
        )

        if self.entry_price <= 0:
            raise ValueError(
                "entry_price must be greater than zero."
            )

        if self.stop_price <= 0:
            raise ValueError(
                "stop_price must be greater than zero."
            )

        if self.take_profit <= 0:
            raise ValueError(
                "take_profit must be greater than zero."
            )

        if self.quantity <= 0:
            raise ValueError(
                "quantity must be greater than zero."
            )


@dataclass(frozen=True, slots=True)
class SimulatedTrade:
    """Completed historical trade."""

    symbol: str
    strategy_name: str
    timeframe: str
    direction: str

    signal_timestamp: datetime
    entry_timestamp: datetime
    exit_timestamp: datetime

    signal_entry_price: float
    entry_price: float
    exit_price: float

    stop_price: float
    take_profit: float

    quantity: float

    gross_pnl: float
    fees: float
    slippage: float
    net_pnl: float

    exit_reason: str

    @property
    def return_on_notional(self) -> float:
        """Return trade PnL relative to entry notional."""

        notional = (
            self.entry_price * self.quantity
        )

        if notional == 0:
            return 0.0

        return self.net_pnl / notional

    @property
    def is_winner(self) -> bool:
        """Return whether the trade produced positive net PnL."""

        return self.net_pnl > 0


@dataclass(slots=True)
class OpenPosition:
    """Internal representation of an open position."""

    signal: BacktestSignal
    entry_timestamp: datetime
    entry_price: float
    entry_fee: float
    entry_slippage: float


class TradeSimulator:
    """
    Simulate historical trade execution.

    Assumptions:

    - Signal is generated at the close of the signal candle.
    - Entry occurs on the next candle.
    - Stop loss and take profit are evaluated using OHLC.
    - If both SL and TP occur inside the same candle, SL is
      conservatively assumed to have occurred first.
    - Positions are one-directional.
    - One open position is handled at a time per simulator.
    """

    def __init__(
        self,
        *,
        cost_model: CostModel | None = None,
    ) -> None:
        self.cost_model = (
            cost_model
            or CostModel()
        )

    def simulate(
        self,
        *,
        candles: pd.DataFrame,
        signals: list[BacktestSignal],
    ) -> list[SimulatedTrade]:
        """
        Simulate a sequence of signals against historical candles.

        Required candle columns:

            timestamp
            open
            high
            low
            close
        """

        self._validate_candles(candles)

        if not signals:
            return []

        data = candles.sort_values(
            "timestamp",
            kind="stable",
        ).reset_index(drop=True)

        trades: list[SimulatedTrade] = []

        for signal in signals:
            trade = self._simulate_signal(
                data=data,
                signal=signal,
            )

            if trade is not None:
                trades.append(trade)

        return trades

    def _simulate_signal(
        self,
        *,
        data: pd.DataFrame,
        signal: BacktestSignal,
    ) -> SimulatedTrade | None:
        """Simulate one signal."""

        signal_rows = data[
            data["timestamp"] > signal.timestamp
        ]

        if signal_rows.empty:
            return None

        entry_row = signal_rows.iloc[0]

        entry_timestamp = entry_row["timestamp"]

        side = (
            "BUY"
            if signal.direction == "LONG"
            else "SELL"
        )

        entry_price = (
            self.cost_model.execution_price(
                price=float(entry_row["open"]),
                side=side,
            )
        )

        entry_notional = (
            entry_price * signal.quantity
        )

        entry_cost = (
            self.cost_model.calculate(
                notional=entry_notional,
            )
        )

        open_position = OpenPosition(
            signal=signal,
            entry_timestamp=entry_timestamp,
            entry_price=entry_price,
            entry_fee=entry_cost.fee,
            entry_slippage=entry_cost.slippage,
        )

        future_rows = data[
            data["timestamp"] >= entry_timestamp
        ]

        for _, row in future_rows.iterrows():

            exit_reason = self._check_exit(
                position=open_position,
                high=float(row["high"]),
                low=float(row["low"]),
            )

            if exit_reason is None:
                continue

            raw_exit_price = self._exit_price(
                position=open_position,
                row=row,
                reason=exit_reason,
            )

            exit_side = (
                "SELL"
                if signal.direction == "LONG"
                else "BUY"
            )

            exit_price = (
                self.cost_model.execution_price(
                    price=raw_exit_price,
                    side=exit_side,
                )
            )

            exit_notional = (
                exit_price * signal.quantity
            )

            exit_cost = (
                self.cost_model.calculate(
                    notional=exit_notional,
                )
            )

            gross_pnl = self._gross_pnl(
                position=open_position,
                exit_price=exit_price,
            )

            total_fees = (
                open_position.entry_fee
                + exit_cost.fee
            )

            total_slippage = (
                open_position.entry_slippage
                + exit_cost.slippage
            )

            net_pnl = (
                gross_pnl
                - total_fees
            )

            return SimulatedTrade(
                symbol=signal.symbol,
                strategy_name=signal.strategy_name,
                timeframe=signal.timeframe,
                direction=signal.direction,
                signal_timestamp=signal.timestamp,
                entry_timestamp=entry_timestamp,
                exit_timestamp=row["timestamp"],
                signal_entry_price=signal.entry_price,
                entry_price=entry_price,
                exit_price=exit_price,
                stop_price=signal.stop_price,
                take_profit=signal.take_profit,
                quantity=signal.quantity,
                gross_pnl=gross_pnl,
                fees=total_fees,
                slippage=total_slippage,
                net_pnl=net_pnl,
                exit_reason=exit_reason,
            )

        return None

    @staticmethod
    def _check_exit(
        *,
        position: OpenPosition,
        high: float,
        low: float,
    ) -> str | None:
        """Determine whether SL or TP was reached."""

        signal = position.signal

        if signal.direction == "LONG":

            stop_hit = low <= signal.stop_price
            target_hit = high >= signal.take_profit

        else:

            stop_hit = high >= signal.stop_price
            target_hit = low <= signal.take_profit

        # Conservative assumption when both are hit
        # inside the same candle.
        if stop_hit:
            return "STOP_LOSS"

        if target_hit:
            return "TAKE_PROFIT"

        return None

    @staticmethod
    def _exit_price(
        *,
        position: OpenPosition,
        row: pd.Series,
        reason: str,
    ) -> float:
        """Determine the raw historical exit price."""

        signal = position.signal

        if reason == "STOP_LOSS":
            return signal.stop_price

        if reason == "TAKE_PROFIT":
            return signal.take_profit

        raise ValueError(
            f"Unsupported exit reason: {reason}"
        )

    @staticmethod
    def _gross_pnl(
        *,
        position: OpenPosition,
        exit_price: float,
    ) -> float:
        """Calculate gross PnL before fees."""

        quantity = position.signal.quantity

        if position.signal.direction == "LONG":
            return (
                exit_price
                - position.entry_price
            ) * quantity

        return (
            position.entry_price
            - exit_price
        ) * quantity

    @staticmethod
    def _validate_candles(
        candles: pd.DataFrame,
    ) -> None:
        """Validate simulator input."""

        required = {
            "timestamp",
            "open",
            "high",
            "low",
            "close",
        }

        missing = required - set(
            candles.columns
        )

        if missing:
            raise ValueError(
                "Missing candle columns: "
                + ", ".join(sorted(missing))
            )

        if candles.empty:
            raise ValueError(
                "Cannot simulate against empty candle data."
            )
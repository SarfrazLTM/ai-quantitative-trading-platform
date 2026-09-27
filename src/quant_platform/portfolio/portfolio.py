"""
Portfolio domain models.

Defines the structures used to represent user portfolios,
portfolio groups, configuration, and runtime state.

A portfolio represents an independent user-defined trading
configuration. It does not directly execute trades.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class PortfolioState(StrEnum):
    """Runtime state of a portfolio."""

    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"
    DRAW_DOWN = "draw_down"


@dataclass(frozen=True, slots=True)
class PortfolioGroup:
    """
    Represents a logical group of strategies within a portfolio.

    Groups allow users to organize related strategy/timeframe
    combinations and apply group-level health and allocation.
    """

    group_id: str
    name: str
    strategy_names: tuple[str, ...]
    allocation_limit: float = 1.0
    enabled: bool = True

    def __post_init__(self) -> None:
        if not self.group_id:
            raise ValueError(
                "group_id cannot be empty."
            )

        if not self.name:
            raise ValueError(
                "group name cannot be empty."
            )

        if not 0.0 <= self.allocation_limit <= 1.0:
            raise ValueError(
                "allocation_limit must be between 0 and 1."
            )


@dataclass(frozen=True, slots=True)
class Portfolio:
    """
    Represents a user trading portfolio.

    The portfolio contains configuration and organizational
    information. Runtime performance is maintained separately
    from this immutable configuration object.
    """

    portfolio_id: str
    user_id: str
    name: str
    groups: tuple[PortfolioGroup, ...]

    initial_capital: float
    max_portfolio_risk: float
    risk_per_trade: float

    state: PortfolioState = PortfolioState.ACTIVE

    max_drawdown: float = 0.20
    max_open_positions: int = 10

    allowed_symbols: tuple[str, ...] = field(
        default_factory=tuple
    )

    def __post_init__(self) -> None:
        if not self.portfolio_id:
            raise ValueError(
                "portfolio_id cannot be empty."
            )

        if not self.user_id:
            raise ValueError(
                "user_id cannot be empty."
            )

        if self.initial_capital <= 0:
            raise ValueError(
                "initial_capital must be greater than zero."
            )

        if not 0.0 < self.risk_per_trade <= 1.0:
            raise ValueError(
                "risk_per_trade must be between 0 and 1."
            )

        if not 0.0 < self.max_portfolio_risk <= 1.0:
            raise ValueError(
                "max_portfolio_risk must be between 0 and 1."
            )

        if not 0.0 < self.max_drawdown <= 1.0:
            raise ValueError(
                "max_drawdown must be between 0 and 1."
            )

        if self.max_open_positions < 1:
            raise ValueError(
                "max_open_positions must be at least 1."
            )

        object.__setattr__(
            self,
            "allowed_symbols",
            tuple(
                symbol.upper()
                for symbol in self.allowed_symbols
            ),
        )


@dataclass(slots=True)
class PortfolioRuntimeState:
    """
    Mutable runtime state for a portfolio.

    This is deliberately separated from Portfolio configuration.

    Configuration answers:
        What is the portfolio supposed to do?

    Runtime state answers:
        What is happening to the portfolio right now?
    """

    portfolio_id: str

    equity: float
    peak_equity: float

    open_positions: int = 0
    current_drawdown: float = 0.0

    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0

    realized_pnl: float = 0.0

    def update_equity(
        self,
        equity: float,
    ) -> None:
        """Update current equity and drawdown."""

        if equity < 0:
            raise ValueError(
                "equity cannot be negative."
            )

        self.equity = equity

        if equity > self.peak_equity:
            self.peak_equity = equity

        if self.peak_equity > 0:
            self.current_drawdown = (
                self.peak_equity - self.equity
            ) / self.peak_equity
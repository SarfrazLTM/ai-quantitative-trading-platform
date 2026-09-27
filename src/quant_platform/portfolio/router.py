"""
Portfolio routing.

Routes strategy-generated candidate signals to eligible user
portfolios.

The router performs portfolio eligibility checks only. It does
not perform final risk approval or capital allocation.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..strategy.base import SignalDirection, StrategyResult
from .portfolio import Portfolio, PortfolioState


@dataclass(frozen=True, slots=True)
class PortfolioRoutingResult:
    """Result of routing a candidate signal."""

    candidate: StrategyResult
    portfolio_ids: tuple[str, ...]

    @property
    def routed(self) -> bool:
        """Return whether the candidate reached any portfolios."""

        return bool(self.portfolio_ids)


class PortfolioRouter:
    """
    Routes candidate strategy signals to eligible portfolios.

    Shared quantitative computation happens before this component.
    User-specific processing begins here.
    """

    def __init__(
        self,
        portfolios: list[Portfolio] | None = None,
    ) -> None:
        self._portfolios = {
            portfolio.portfolio_id: portfolio
            for portfolio in portfolios or []
        }

    def register(
        self,
        portfolio: Portfolio,
    ) -> None:
        """Register a portfolio."""

        if portfolio.portfolio_id in self._portfolios:
            raise ValueError(
                f"Portfolio '{portfolio.portfolio_id}' "
                "is already registered."
            )

        self._portfolios[
            portfolio.portfolio_id
        ] = portfolio

    def route(
        self,
        candidate: StrategyResult,
    ) -> PortfolioRoutingResult:
        """
        Route a strategy candidate to eligible portfolios.
        """

        if candidate.direction == SignalDirection.NONE:
            return PortfolioRoutingResult(
                candidate=candidate,
                portfolio_ids=(),
            )

        eligible: list[str] = []

        for portfolio in self._portfolios.values():

            if not self._is_eligible(
                portfolio,
                candidate,
            ):
                continue

            eligible.append(
                portfolio.portfolio_id
            )

        return PortfolioRoutingResult(
            candidate=candidate,
            portfolio_ids=tuple(eligible),
        )

    @staticmethod
    def _is_eligible(
        portfolio: Portfolio,
        candidate: StrategyResult,
    ) -> bool:
        """Determine whether a portfolio can receive a candidate."""

        if portfolio.state != PortfolioState.ACTIVE:
            return False

        if candidate.symbol.upper() not in portfolio.allowed_symbols:
            return False

        return any(
            candidate.strategy_name in group.strategy_names
            and group.enabled
            for group in portfolio.groups
        )

    def portfolios(self) -> tuple[Portfolio, ...]:
        """Return all registered portfolios."""

        return tuple(self._portfolios.values())
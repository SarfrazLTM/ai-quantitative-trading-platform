"""
Portfolio exposure management.

Tracks current positions and evaluates whether a new candidate
would exceed configured exposure limits.

This module does not determine strategy direction and does not
perform order execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, slots=True)
class ExposureSnapshot:
    """Current exposure state of a portfolio."""

    portfolio_id: str
    total_notional: float
    symbol_notional: dict[str, float]
    open_positions: int

    @property
    def symbols(self) -> tuple[str, ...]:
        """Return symbols currently carrying exposure."""

        return tuple(
            self.symbol_notional.keys()
        )


@dataclass(frozen=True, slots=True)
class ExposureCheckResult:
    """Result of checking a proposed trade against exposure limits."""

    allowed: bool
    proposed_notional: float
    resulting_total_notional: float
    resulting_symbol_notional: float
    reason: str


@dataclass(frozen=True, slots=True)
class PositionExposure:
    """Represents an individual position's notional exposure."""

    symbol: str
    notional: float


class ExposureManager:
    """
    Manage portfolio exposure.

    Exposure limits are expressed as fractions of portfolio
    capital.

    Example:

        max_portfolio_exposure = 0.50

        means total notional exposure cannot exceed 50% of the
        configured capital for this risk layer.
    """

    def __init__(
        self,
        *,
        max_portfolio_exposure: float = 1.0,
        max_symbol_exposure: float = 0.20,
        max_open_positions: int = 10,
        one_position_per_symbol: bool = True,
    ) -> None:

        if not 0.0 < max_portfolio_exposure:
            raise ValueError(
                "max_portfolio_exposure must be greater than zero."
            )

        if not 0.0 < max_symbol_exposure:
            raise ValueError(
                "max_symbol_exposure must be greater than zero."
            )

        if max_open_positions < 1:
            raise ValueError(
                "max_open_positions must be at least 1."
            )

        self.max_portfolio_exposure = (
            max_portfolio_exposure
        )

        self.max_symbol_exposure = (
            max_symbol_exposure
        )

        self.max_open_positions = (
            max_open_positions
        )

        self.one_position_per_symbol = (
            one_position_per_symbol
        )

    def snapshot(
        self,
        *,
        portfolio_id: str,
        positions: Iterable[PositionExposure],
    ) -> ExposureSnapshot:
        """Build a current exposure snapshot."""

        symbol_notional: dict[str, float] = {}

        for position in positions:

            if position.notional < 0:
                raise ValueError(
                    "Position notional cannot be negative."
                )

            symbol = position.symbol.upper()

            symbol_notional[symbol] = (
                symbol_notional.get(symbol, 0.0)
                + position.notional
            )

        return ExposureSnapshot(
            portfolio_id=portfolio_id,
            total_notional=sum(
                symbol_notional.values()
            ),
            symbol_notional=symbol_notional,
            open_positions=len(symbol_notional),
        )

    def check(
        self,
        *,
        snapshot: ExposureSnapshot,
        symbol: str,
        proposed_notional: float,
        capital: float,
    ) -> ExposureCheckResult:
        """
        Check whether a proposed position fits within
        portfolio exposure constraints.
        """

        if proposed_notional <= 0:
            return ExposureCheckResult(
                allowed=False,
                proposed_notional=proposed_notional,
                resulting_total_notional=(
                    snapshot.total_notional
                ),
                resulting_symbol_notional=(
                    snapshot.symbol_notional.get(
                        symbol.upper(),
                        0.0,
                    )
                ),
                reason="Proposed notional must be greater than zero.",
            )

        if capital <= 0:
            raise ValueError(
                "capital must be greater than zero."
            )

        normalized_symbol = symbol.upper()

        current_symbol_notional = (
            snapshot.symbol_notional.get(
                normalized_symbol,
                0.0,
            )
        )

        resulting_symbol_notional = (
            current_symbol_notional
            + proposed_notional
        )

        resulting_total_notional = (
            snapshot.total_notional
            + proposed_notional
        )

        if (
            self.one_position_per_symbol
            and current_symbol_notional > 0
        ):
            return ExposureCheckResult(
                allowed=False,
                proposed_notional=proposed_notional,
                resulting_total_notional=(
                    resulting_total_notional
                ),
                resulting_symbol_notional=(
                    resulting_symbol_notional
                ),
                reason=(
                    f"An existing position already exists "
                    f"for {normalized_symbol}."
                ),
            )

        max_symbol_notional = (
            capital * self.max_symbol_exposure
        )

        if resulting_symbol_notional > max_symbol_notional:
            return ExposureCheckResult(
                allowed=False,
                proposed_notional=proposed_notional,
                resulting_total_notional=(
                    resulting_total_notional
                ),
                resulting_symbol_notional=(
                    resulting_symbol_notional
                ),
                reason=(
                    f"Symbol exposure exceeds the configured "
                    f"limit for {normalized_symbol}."
                ),
            )

        max_total_notional = (
            capital * self.max_portfolio_exposure
        )

        if resulting_total_notional > max_total_notional:
            return ExposureCheckResult(
                allowed=False,
                proposed_notional=proposed_notional,
                resulting_total_notional=(
                    resulting_total_notional
                ),
                resulting_symbol_notional=(
                    resulting_symbol_notional
                ),
                reason=(
                    "Portfolio exposure exceeds the configured "
                    "maximum."
                ),
            )

        if (
            snapshot.open_positions
            >= self.max_open_positions
        ):
            return ExposureCheckResult(
                allowed=False,
                proposed_notional=proposed_notional,
                resulting_total_notional=(
                    resulting_total_notional
                ),
                resulting_symbol_notional=(
                    resulting_symbol_notional
                ),
                reason=(
                    "Maximum number of open positions "
                    "has been reached."
                ),
            )

        return ExposureCheckResult(
            allowed=True,
            proposed_notional=proposed_notional,
            resulting_total_notional=(
                resulting_total_notional
            ),
            resulting_symbol_notional=(
                resulting_symbol_notional
            ),
            reason="Exposure is within configured limits.",
        )
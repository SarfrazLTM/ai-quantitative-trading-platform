"""
Market-data validation.

Provides validation rules for historical and real-time market data
before it enters the quantitative processing pipeline.

Validation focuses on data integrity, including:

- Required fields
- Timestamp validity
- OHLC relationships
- Positive prices
- Non-negative volume
- Timeframe consistency
- Duplicate timestamps
- Chronological ordering
- Missing candles / gaps

This module does not perform:
- Feature engineering
- Indicator calculation
- Strategy evaluation
- ML inference
- Trading decisions
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, Sequence

from .ingestion import MarketCandle


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """Represents a single market-data validation issue."""

    symbol: str
    timestamp: datetime | None
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Result of validating a collection of market candles."""

    valid: bool
    issues: tuple[ValidationIssue, ...]

    @property
    def issue_count(self) -> int:
        """Return the number of validation issues."""

        return len(self.issues)


class MarketDataValidator:
    """
    Validate OHLCV market data.

    The validator is intentionally independent of the exchange
    that produced the data.

    Example:

        validator = MarketDataValidator()

        result = validator.validate(candles)

        if not result.valid:
            for issue in result.issues:
                print(issue)
    """

    def validate(
        self,
        candles: Sequence[MarketCandle],
    ) -> ValidationResult:
        """
        Run all configured validation checks.

        Checks:
        - Empty input
        - Individual candle integrity
        - Duplicate timestamps
        - Chronological ordering
        - Candle gaps
        """

        issues: list[ValidationIssue] = []

        if not candles:
            issues.append(
                ValidationIssue(
                    symbol="UNKNOWN",
                    timestamp=None,
                    code="EMPTY_DATASET",
                    message="No market candles were provided.",
                )
            )

            return ValidationResult(
                valid=False,
                issues=tuple(issues),
            )

        issues.extend(
            self._validate_candles(candles)
        )

        issues.extend(
            self._validate_duplicates(candles)
        )

        issues.extend(
            self._validate_order(candles)
        )

        issues.extend(
            self._validate_gaps(candles)
        )

        return ValidationResult(
            valid=not issues,
            issues=tuple(issues),
        )

    def _validate_candles(
        self,
        candles: Iterable[MarketCandle],
    ) -> list[ValidationIssue]:
        """Validate individual OHLCV candles."""

        issues: list[ValidationIssue] = []

        for candle in candles:

            if not candle.symbol:
                issues.append(
                    self._issue(
                        candle,
                        "MISSING_SYMBOL",
                        "Candle does not contain a symbol.",
                    )
                )

            if not candle.timeframe:
                issues.append(
                    self._issue(
                        candle,
                        "MISSING_TIMEFRAME",
                        "Candle does not contain a timeframe.",
                    )
                )

            if candle.timestamp.tzinfo is None:
                issues.append(
                    self._issue(
                        candle,
                        "NAIVE_TIMESTAMP",
                        "Candle timestamp must contain timezone information.",
                    )
                )

            prices = {
                "open": candle.open,
                "high": candle.high,
                "low": candle.low,
                "close": candle.close,
            }

            for name, value in prices.items():

                if value <= 0:
                    issues.append(
                        self._issue(
                            candle,
                            "INVALID_PRICE",
                            f"{name} price must be greater than zero.",
                        )
                    )

            if candle.volume < 0:
                issues.append(
                    self._issue(
                        candle,
                        "INVALID_VOLUME",
                        "Volume cannot be negative.",
                    )
                )

            if candle.high < candle.low:
                issues.append(
                    self._issue(
                        candle,
                        "INVALID_HIGH_LOW",
                        "High price cannot be lower than low price.",
                    )
                )

            if candle.high < max(candle.open, candle.close):
                issues.append(
                    self._issue(
                        candle,
                        "INVALID_HIGH",
                        "High price must be greater than or equal to "
                        "open and close.",
                    )
                )

            if candle.low > min(candle.open, candle.close):
                issues.append(
                    self._issue(
                        candle,
                        "INVALID_LOW",
                        "Low price must be less than or equal to "
                        "open and close.",
                    )
                )

        return issues

    def _validate_duplicates(
        self,
        candles: Sequence[MarketCandle],
    ) -> list[ValidationIssue]:
        """Detect duplicate candle timestamps."""

        issues: list[ValidationIssue] = []
        seen: set[tuple[str, datetime, str]] = set()

        for candle in candles:

            key = (
                candle.symbol,
                candle.timestamp,
                candle.timeframe,
            )

            if key in seen:
                issues.append(
                    self._issue(
                        candle,
                        "DUPLICATE_TIMESTAMP",
                        "Duplicate candle timestamp detected.",
                    )
                )

            seen.add(key)

        return issues

    def _validate_order(
        self,
        candles: Sequence[MarketCandle],
    ) -> list[ValidationIssue]:
        """Ensure candles are ordered chronologically."""

        issues: list[ValidationIssue] = []

        previous: MarketCandle | None = None

        for candle in candles:

            if previous is not None:

                if candle.timestamp < previous.timestamp:

                    issues.append(
                        self._issue(
                            candle,
                            "OUT_OF_ORDER",
                            "Candle timestamps are not chronological.",
                        )
                    )

            previous = candle

        return issues

    def _validate_gaps(
        self,
        candles: Sequence[MarketCandle],
    ) -> list[ValidationIssue]:
        """
        Detect unexpected gaps between candles.

        Gap validation is performed separately for each
        symbol/timeframe combination.
        """

        issues: list[ValidationIssue] = []

        grouped: dict[
            tuple[str, str],
            list[MarketCandle],
        ] = {}

        for candle in candles:

            key = (
                candle.symbol,
                candle.timeframe,
            )

            grouped.setdefault(key, []).append(candle)

        for (symbol, timeframe), group in grouped.items():

            ordered = sorted(
                group,
                key=lambda candle: candle.timestamp,
            )

            interval = self._timeframe_duration(timeframe)

            if interval is None:
                continue

            for previous, current in zip(
                ordered,
                ordered[1:],
            ):

                expected = previous.timestamp + interval

                if current.timestamp > expected:

                    issues.append(
                        ValidationIssue(
                            symbol=symbol,
                            timestamp=current.timestamp,
                            code="CANDLE_GAP",
                            message=(
                                f"Missing candle interval between "
                                f"{previous.timestamp.isoformat()} "
                                f"and "
                                f"{current.timestamp.isoformat()}."
                            ),
                        )
                    )

        return issues

    @staticmethod
    def _timeframe_duration(
        timeframe: str,
    ) -> timedelta | None:
        """Convert a supported timeframe into a duration."""

        normalized = timeframe.lower().strip()

        timeframe_map = {
            "1m": timedelta(minutes=1),
            "3m": timedelta(minutes=3),
            "5m": timedelta(minutes=5),
            "15m": timedelta(minutes=15),
            "30m": timedelta(minutes=30),
            "1h": timedelta(hours=1),
            "2h": timedelta(hours=2),
            "4h": timedelta(hours=4),
            "6h": timedelta(hours=6),
            "8h": timedelta(hours=8),
            "12h": timedelta(hours=12),
            "1d": timedelta(days=1),
        }

        return timeframe_map.get(normalized)

    @staticmethod
    def _issue(
        candle: MarketCandle,
        code: str,
        message: str,
    ) -> ValidationIssue:
        """Create a validation issue for a candle."""

        return ValidationIssue(
            symbol=candle.symbol,
            timestamp=candle.timestamp,
            code=code,
            message=message,
        )
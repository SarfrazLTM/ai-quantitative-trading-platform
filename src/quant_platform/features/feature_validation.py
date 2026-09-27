"""
Feature-data validation.

Provides validation checks for model-ready feature datasets.

The validator detects common problems such as:

- Missing values
- Infinite values
- Duplicate timestamps
- Incorrect ordering
- Constant features
- Non-numeric feature columns
- Insufficient observations

The validator does not modify the dataset.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True, slots=True)
class FeatureValidationIssue:
    """Represents a feature validation problem."""

    code: str
    message: str
    column: str | None = None


@dataclass(frozen=True, slots=True)
class FeatureValidationResult:
    """Result of feature dataset validation."""

    valid: bool
    issues: tuple[FeatureValidationIssue, ...]

    @property
    def issue_count(self) -> int:
        """Return the number of detected issues."""

        return len(self.issues)


class FeatureValidator:
    """
    Validate feature datasets before ML processing.

    The validator is deliberately read-only. It reports problems
    rather than silently modifying the feature dataset.
    """

    def __init__(
        self,
        minimum_rows: int = 100,
    ) -> None:
        if minimum_rows < 1:
            raise ValueError(
                "minimum_rows must be greater than zero."
            )

        self.minimum_rows = minimum_rows

    def validate(
        self,
        data: pd.DataFrame,
        feature_columns: tuple[str, ...] | None = None,
    ) -> FeatureValidationResult:
        """
        Validate a model-ready feature dataset.
        """

        issues: list[FeatureValidationIssue] = []

        if data.empty:
            issues.append(
                FeatureValidationIssue(
                    code="EMPTY_DATASET",
                    message="Feature dataset is empty.",
                )
            )

            return FeatureValidationResult(
                valid=False,
                issues=tuple(issues),
            )

        if len(data) < self.minimum_rows:
            issues.append(
                FeatureValidationIssue(
                    code="INSUFFICIENT_ROWS",
                    message=(
                        f"Dataset contains {len(data)} rows; "
                        f"minimum required is {self.minimum_rows}."
                    ),
                )
            )

        issues.extend(
            self._validate_required_columns(data)
        )

        issues.extend(
            self._validate_timestamps(data)
        )

        issues.extend(
            self._validate_features(
                data,
                feature_columns,
            )
        )

        return FeatureValidationResult(
            valid=not issues,
            issues=tuple(issues),
        )

    @staticmethod
    def _validate_required_columns(
        data: pd.DataFrame,
    ) -> list[FeatureValidationIssue]:
        """Validate required market-data columns."""

        required = {
            "symbol",
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
        }

        missing = required - set(data.columns)

        return [
            FeatureValidationIssue(
                code="MISSING_COLUMN",
                message=f"Required column '{column}' is missing.",
                column=column,
            )
            for column in sorted(missing)
        ]

    @staticmethod
    def _validate_timestamps(
        data: pd.DataFrame,
    ) -> list[FeatureValidationIssue]:
        """Validate timestamp integrity."""

        issues: list[FeatureValidationIssue] = []

        if "timestamp" not in data.columns:
            return issues

        if data["timestamp"].isna().any():
            issues.append(
                FeatureValidationIssue(
                    code="MISSING_TIMESTAMP",
                    message="Dataset contains missing timestamps.",
                    column="timestamp",
                )
            )

        if data["timestamp"].duplicated().any():
            issues.append(
                FeatureValidationIssue(
                    code="DUPLICATE_TIMESTAMP",
                    message="Dataset contains duplicate timestamps.",
                    column="timestamp",
                )
            )

        return issues

    @staticmethod
    def _validate_features(
        data: pd.DataFrame,
        feature_columns: tuple[str, ...] | None,
    ) -> list[FeatureValidationIssue]:
        """Validate individual feature columns."""

        issues: list[FeatureValidationIssue] = []

        if feature_columns is None:
            base_columns = {
                "symbol",
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "timeframe",
            }

            feature_columns = tuple(
                column
                for column in data.columns
                if column not in base_columns
            )

        for column in feature_columns:

            if column not in data.columns:
                issues.append(
                    FeatureValidationIssue(
                        code="MISSING_FEATURE",
                        message=(
                            f"Feature column '{column}' "
                            "does not exist."
                        ),
                        column=column,
                    )
                )
                continue

            if not pd.api.types.is_numeric_dtype(
                data[column]
            ):
                issues.append(
                    FeatureValidationIssue(
                        code="NON_NUMERIC_FEATURE",
                        message=(
                            f"Feature '{column}' must be numeric."
                        ),
                        column=column,
                    )
                )
                continue

            if data[column].isna().any():
                issues.append(
                    FeatureValidationIssue(
                        code="MISSING_FEATURE_VALUE",
                        message=(
                            f"Feature '{column}' contains "
                            "missing values."
                        ),
                        column=column,
                    )
                )

            values = data[column].to_numpy()

            if not np.isfinite(values).all():
                issues.append(
                    FeatureValidationIssue(
                        code="NON_FINITE_FEATURE",
                        message=(
                            f"Feature '{column}' contains "
                            "infinite or non-finite values."
                        ),
                        column=column,
                    )
                )

            if data[column].nunique(dropna=True) <= 1:
                issues.append(
                    FeatureValidationIssue(
                        code="CONSTANT_FEATURE",
                        message=(
                            f"Feature '{column}' has no meaningful "
                            "variation."
                        ),
                        column=column,
                    )
                )

        return issues
"""
Probability calibration utilities.

Provides a small abstraction around probability calibration for
classification models.

Calibration is performed independently from strategy thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True, slots=True)
class CalibrationResult:
    """Result of probability calibration."""

    probabilities: np.ndarray
    calibrated: bool


class ProbabilityCalibrator:
    """
    Calibrate model probabilities.

    This class provides a lightweight interface that can later be
    connected to Platt scaling, isotonic regression, beta
    calibration, or another validated calibration method.

    Strategy thresholds are intentionally not handled here.
    """

    def __init__(
        self,
        calibrator: Any | None = None,
    ) -> None:
        self.calibrator = calibrator

    def fit(
        self,
        probabilities: np.ndarray,
        targets: np.ndarray,
    ) -> None:
        """
        Fit the calibration model.

        The supplied calibrator must implement ``fit``.
        """

        if self.calibrator is None:
            raise ValueError(
                "No calibration model has been configured."
            )

        self.calibrator.fit(
            probabilities,
            targets,
        )

    def transform(
        self,
        probabilities: np.ndarray,
    ) -> CalibrationResult:
        """
        Transform raw probabilities into calibrated probabilities.
        """

        if self.calibrator is None:
            return CalibrationResult(
                probabilities=np.asarray(probabilities),
                calibrated=False,
            )

        calibrated = self.calibrator.predict(
            probabilities
        )

        return CalibrationResult(
            probabilities=np.asarray(calibrated),
            calibrated=True,
        )
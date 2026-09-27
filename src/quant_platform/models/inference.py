"""
Production model inference.

Provides a model-agnostic inference interface for generating
predictions from validated feature data.

Strategy decisions and trading signals are intentionally outside
this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

import numpy as np
import pandas as pd


class PredictiveModel(Protocol):
    """Protocol for models supporting prediction."""

    def predict(
        self,
        features: Any,
    ) -> Any:
        """Generate model predictions."""


class ProbabilisticModel(PredictiveModel, Protocol):
    """Protocol for models supporting probability predictions."""

    def predict_proba(
        self,
        features: Any,
    ) -> Any:
        """Generate class probabilities."""


@dataclass(frozen=True, slots=True)
class ModelPrediction:
    """Standardized model prediction."""

    model_name: str
    model_version: str
    prediction: Any
    probabilities: np.ndarray | None = None


class ModelInference:
    """
    Execute model inference.

    The inference layer does not know anything about:
    - Trading strategies
    - LONG/SHORT decisions
    - Portfolio allocation
    - Risk limits
    """

    def __init__(
        self,
        model: PredictiveModel,
        model_name: str,
        model_version: str,
    ) -> None:
        self.model = model
        self.model_name = model_name
        self.model_version = model_version

    def predict(
        self,
        features: pd.DataFrame,
    ) -> ModelPrediction:
        """
        Generate a prediction from model features.
        """

        if features.empty:
            raise ValueError(
                "Cannot run inference on an empty feature dataset."
            )

        prediction = self.model.predict(features)

        probabilities = None

        if hasattr(self.model, "predict_proba"):
            probabilities = np.asarray(
                self.model.predict_proba(features)
            )

        return ModelPrediction(
            model_name=self.model_name,
            model_version=self.model_version,
            prediction=prediction,
            probabilities=probabilities,
        )
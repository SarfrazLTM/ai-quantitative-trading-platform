"""
Risk management for the quantitative trading platform.

Provides position sizing, exposure management, drawdown control,
and centralized trade-risk evaluation.

The risk layer operates after strategy and portfolio evaluation
and before final signal generation.
"""

from .drawdown import (
    DrawdownController,
    DrawdownState,
)
from .exposure import (
    ExposureCheckResult,
    ExposureManager,
    ExposureSnapshot,
)
from .position_sizing import (
    PositionSize,
    PositionSizer,
)
from .risk_engine import (
    RiskDecision,
    RiskEngine,
    RiskStatus,
)

__all__ = [
    "DrawdownController",
    "DrawdownState",
    "ExposureCheckResult",
    "ExposureManager",
    "ExposureSnapshot",
    "PositionSize",
    "PositionSizer",
    "RiskDecision",
    "RiskEngine",
    "RiskStatus",
]
"""
Portfolio management for the quantitative trading platform.

Provides portfolio definitions, candidate-signal routing,
portfolio health evaluation, and adaptive capital allocation.

Portfolio management is intentionally separated from strategy
evaluation, risk management, and execution.
"""

from .allocation import AllocationDecision, AdaptiveAllocator
from .health import HealthScore, PortfolioHealthEngine
from .portfolio import (
    Portfolio,
    PortfolioGroup,
    PortfolioState,
)
from .router import PortfolioRouter, PortfolioRoutingResult

__all__ = [
    "AllocationDecision",
    "AdaptiveAllocator",
    "HealthScore",
    "PortfolioHealthEngine",
    "Portfolio",
    "PortfolioGroup",
    "PortfolioState",
    "PortfolioRouter",
    "PortfolioRoutingResult",
]
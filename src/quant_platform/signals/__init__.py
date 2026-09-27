"""
Trading signal generation.

Provides canonical signal contracts, signal generation from
approved risk decisions, and tamper-evident signal integrity.
"""

from .generator import SignalGenerator
from .integrity import SignalIntegrity, SignalIntegrityService
from .signal import TradingSignal

__all__ = [
    "SignalGenerator",
    "SignalIntegrity",
    "SignalIntegrityService",
    "TradingSignal",
]
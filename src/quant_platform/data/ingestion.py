"""
Binance Futures market-data ingestion.

Provides historical and real-time OHLCV market data for the
quantitative trading pipeline.

This module uses public market-data endpoints only.
User trading credentials and order execution are intentionally
outside this module.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterator, Sequence
from .schemas import MarketCandle

import requests


class BinanceFuturesIngestor:
    """
    Binance Futures market-data client.

    Uses Binance public REST APIs for historical candles.
    Real-time streaming can be added through the Binance WebSocket
    market-stream interface.
    """

    BASE_URL = "https://fapi.binance.com"

    def __init__(
        self,
        timeout: float = 10.0,
        session: requests.Session | None = None,
    ) -> None:
        self.timeout = timeout
        self.session = session or requests.Session()

    def historical(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
        limit: int = 1500,
    ) -> list[MarketCandle]:
        """
        Fetch historical Binance Futures candles.

        Binance returns OHLCV data as arrays. This method converts
        the response into the platform's MarketCandle representation.
        """

        params = {
            "symbol": symbol.upper(),
            "interval": timeframe,
            "startTime": self._to_milliseconds(start),
            "endTime": self._to_milliseconds(end),
            "limit": limit,
        }

        response = self.session.get(
            f"{self.BASE_URL}/fapi/v1/klines",
            params=params,
            timeout=self.timeout,
        )

        response.raise_for_status()

        return [
            self._parse_kline(row, symbol, timeframe)
            for row in response.json()
        ]

    def historical_batches(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
        limit: int = 1500,
    ) -> Iterator[MarketCandle]:
        """
        Yield historical candles in chronological batches.

        Useful for large historical datasets where loading all
        candles into memory at once is undesirable.
        """

        current_start = start

        while current_start < end:
            candles = self.historical(
                symbol=symbol,
                timeframe=timeframe,
                start=current_start,
                end=end,
                limit=limit,
            )

            if not candles:
                break

            for candle in candles:
                if candle.timestamp >= end:
                    return

                yield candle

            last_timestamp = candles[-1].timestamp

            if last_timestamp <= current_start:
                break

            current_start = last_timestamp

    @staticmethod
    def _parse_kline(
        row: list,
        symbol: str,
        timeframe: str,
    ) -> MarketCandle:
        """Convert a Binance kline response into MarketCandle."""

        return MarketCandle(
            symbol=symbol.upper(),
            timestamp=datetime.fromtimestamp(
                row[0] / 1000,
                tz=timezone.utc,
            ),
            open=float(row[1]),
            high=float(row[2]),
            low=float(row[3]),
            close=float(row[4]),
            volume=float(row[5]),
            timeframe=timeframe,
        )

    @staticmethod
    def _to_milliseconds(timestamp: datetime) -> int:
        """Convert datetime to Unix milliseconds."""

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        return int(timestamp.timestamp() * 1000)
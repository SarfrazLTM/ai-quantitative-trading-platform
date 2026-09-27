"""
Binance Futures real-time market-data WebSocket.

Provides a lightweight WebSocket client for receiving public
Binance Futures market-data streams.

This module is intentionally limited to market data.

It does not handle:
- Trading API credentials
- Account/user data
- Order execution
- Portfolio management
- Risk decisions

The received market events are forwarded to the quantitative
runtime through a callback.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

from .schemas import MarketTick

import websocket

logger = logging.getLogger(__name__)


class BinanceFuturesWebSocket:
    """
    Binance Futures public market-data WebSocket client.

    The client subscribes to one or more Binance market streams
    and converts incoming events into platform-level MarketTick
    objects.

    Example streams:

        btcusdt@aggTrade
        ethusdt@aggTrade

    The client does not contain trading or account functionality.
    """

    BASE_URL = "wss://fstream.binance.com/ws"

    def __init__(
        self,
        symbols: list[str],
        on_tick: Callable[[MarketTick], None],
        timeout: float = 30.0,
    ) -> None:
        if not symbols:
            raise ValueError("At least one symbol is required.")

        self.symbols = [symbol.lower() for symbol in symbols]
        self.on_tick = on_tick
        self.timeout = timeout

        self._socket: websocket.WebSocketApp | None = None

    def run(self) -> None:
        """
        Start the WebSocket connection.

        This method blocks while the connection is active.
        Reconnection policy can be added by the runtime layer.
        """

        stream_url = self._build_stream_url()

        logger.info(
            "Connecting to Binance Futures WebSocket: %s",
            stream_url,
        )

        self._socket = websocket.WebSocketApp(
            stream_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )

        self._socket.run_forever(
            ping_interval=20,
            ping_timeout=10,
        )

    def close(self) -> None:
        """Close the active WebSocket connection."""

        if self._socket is not None:
            logger.info("Closing Binance Futures WebSocket.")
            self._socket.close()

    def _build_stream_url(self) -> str:
        """
        Build a combined WebSocket stream URL.

        Multiple symbols are combined into a single connection.
        """

        streams = "/".join(
            f"{symbol}@aggTrade"
            for symbol in self.symbols
        )

        return f"wss://fstream.binance.com/stream?streams={streams}"

    def _on_open(
        self,
        ws: websocket.WebSocketApp,
    ) -> None:
        """Handle successful WebSocket connection."""

        logger.info(
            "Binance Futures WebSocket connected. "
            "Symbols=%s",
            self.symbols,
        )

    def _on_message(
        self,
        ws: websocket.WebSocketApp,
        message: str,
    ) -> None:
        """Process an incoming market-data message."""

        try:
            payload = json.loads(message)

            # Combined streams wrap the actual event inside "data".
            event = payload.get("data", payload)

            market_tick = self._parse_event(event)

            if market_tick is None:
                return

            self.on_tick(market_tick)

        except (json.JSONDecodeError, TypeError, ValueError):
            logger.exception(
                "Failed to process Binance WebSocket message."
            )

    def _on_error(
        self,
        ws: websocket.WebSocketApp,
        error: Exception,
    ) -> None:
        """Handle WebSocket errors."""

        logger.error(
            "Binance Futures WebSocket error: %s",
            error,
        )

    def _on_close(
        self,
        ws: websocket.WebSocketApp,
        close_status_code: int | None,
        close_msg: str | None,
    ) -> None:
        """Handle WebSocket connection closure."""

        logger.warning(
            "Binance Futures WebSocket closed. "
            "code=%s message=%s",
            close_status_code,
            close_msg,
        )

    @staticmethod
    def _parse_event(
        event: dict,
    ) -> MarketTick | None:
        """
        Convert a Binance market event into MarketTick.

        Currently handles aggTrade events.
        """

        event_type = event.get("e")

        if event_type != "aggTrade":
            return None

        timestamp_ms = event.get("E")

        if timestamp_ms is None:
            return None

        return MarketTick(
            symbol=event["s"],
            price=float(event["p"]),
            quantity=float(event["q"]),
            timestamp=datetime.fromtimestamp(
                timestamp_ms / 1000,
                tz=timezone.utc,
            ),
            event_type=event_type,
        )
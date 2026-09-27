"""
Webhook HTTP client.

Provides a generic outbound HTTP client for delivering trading
signals to user-configured webhook endpoints.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import requests


@dataclass(frozen=True, slots=True)
class WebhookConfig:
    """Configuration for a user webhook endpoint."""

    url: str
    secret: str | None = None
    timeout_seconds: float = 10.0
    headers: dict[str, str] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not self.url:
            raise ValueError(
                "Webhook URL cannot be empty."
            )

        if self.timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be greater than zero."
            )


@dataclass(frozen=True, slots=True)
class WebhookResponse:
    """Result returned by a webhook request."""

    success: bool
    status_code: int | None
    response_body: str | None
    error: str | None = None


class WebhookClient:
    """
    Generic HTTP webhook client.

    This class does not make trading decisions and does not
    communicate with exchange trading APIs directly.
    """

    def __init__(
        self,
        session: requests.Session | None = None,
    ) -> None:
        self._session = session or requests.Session()

    def send(
        self,
        config: WebhookConfig,
        payload: dict[str, Any],
    ) -> WebhookResponse:
        """Send a JSON payload to the configured webhook."""

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            **config.headers,
        }

        if config.secret:
            headers["X-Webhook-Secret"] = config.secret

        try:
            response = self._session.post(
                config.url,
                json=payload,
                headers=headers,
                timeout=config.timeout_seconds,
            )

            success = 200 <= response.status_code < 300

            return WebhookResponse(
                success=success,
                status_code=response.status_code,
                response_body=response.text[:2000],
                error=None if success else (
                    f"HTTP {response.status_code}"
                ),
            )

        except requests.RequestException as exc:
            return WebhookResponse(
                success=False,
                status_code=None,
                response_body=None,
                error=str(exc),
            )
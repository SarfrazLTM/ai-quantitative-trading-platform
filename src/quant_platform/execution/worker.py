"""
Webhook worker.

Consumes delivery jobs and sends them through the webhook client.
"""

from __future__ import annotations

import logging
import time

from .delivery import (
    DeliveryService,
    DeliveryStatus,
)
from .queue import DeliveryJob, InMemoryDeliveryQueue
from .retry import RetryPolicy
from .webhook import WebhookClient, WebhookConfig


logger = logging.getLogger(__name__)


class WebhookWorker:
    """
    Processes queued webhook delivery jobs.

    The worker does not contain trading logic. It only handles
    delivery, retry, and completion state.
    """

    def __init__(
        self,
        queue: InMemoryDeliveryQueue,
        delivery_service: DeliveryService,
        webhook_client: WebhookClient,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        self._queue = queue
        self._delivery_service = delivery_service
        self._webhook_client = webhook_client
        self._retry_policy = (
            retry_policy or RetryPolicy()
        )

        self._running = False

    def process_once(self) -> None:
        """Process one queued delivery job."""

        job = self._queue.dequeue(
            timeout=0.1,
        )

        if job is None:
            return

        try:
            self._process_job(job)
        finally:
            self._queue.task_done()

    def run(
        self,
        *,
        poll_interval_seconds: float = 0.5,
    ) -> None:
        """
        Continuously process webhook jobs.

        Intended as a simple reference worker loop.
        """

        self._running = True

        while self._running:
            self.process_once()

            time.sleep(
                poll_interval_seconds
            )

    def stop(self) -> None:
        """Stop the worker loop."""

        self._running = False

    def _process_job(
        self,
        job: DeliveryJob,
    ) -> None:
        """Process a single delivery job."""

        if self._delivery_service.is_delivered(
            job.signal_id
        ):
            logger.info(
                "Skipping already delivered signal: %s",
                job.signal_id,
            )
            return

        config = WebhookConfig(
            url=job.webhook_url,
        )

        response = self._webhook_client.send(
            config=config,
            payload=job.payload,
        )

        if response.success:
            self._delivery_service.mark_delivered(
                job
            )

            logger.info(
                "Webhook delivered: signal=%s attempt=%s",
                job.signal_id,
                job.attempt,
            )

            return

        logger.warning(
            "Webhook delivery failed: signal=%s "
            "attempt=%s error=%s",
            job.signal_id,
            job.attempt,
            response.error,
        )

        result = self._delivery_service.retry(
            job
        )

        if result.status == DeliveryStatus.RETRYING:
            delay = self._retry_policy.delay_seconds(
                result.attempt
            )

            logger.info(
                "Retrying webhook: signal=%s "
                "attempt=%s delay=%ss",
                job.signal_id,
                result.attempt,
                delay,
            )

            time.sleep(delay)

        else:
            logger.error(
                "Webhook delivery permanently failed: "
                "signal=%s attempts=%s",
                job.signal_id,
                result.attempt,
            )
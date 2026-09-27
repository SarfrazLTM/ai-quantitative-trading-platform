"""
Webhook delivery orchestration.

Coordinates queueing, idempotency, webhook delivery, and retry
decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any
from uuid import uuid4

from .idempotency import IdempotencyStore
from .queue import DeliveryJob, InMemoryDeliveryQueue
from .retry import RetryPolicy


class DeliveryStatus(StrEnum):
    """Possible webhook delivery states."""

    QUEUED = "queued"
    DELIVERED = "delivered"
    RETRYING = "retrying"
    FAILED = "failed"
    DUPLICATE = "duplicate"


@dataclass(frozen=True, slots=True)
class DeliveryRequest:
    """Request to deliver a trading signal."""

    signal_id: str
    webhook_url: str
    payload: dict[str, Any]
    idempotency_key: str | None = None


@dataclass(frozen=True, slots=True)
class DeliveryResult:
    """Result of a delivery operation."""

    job_id: str
    signal_id: str
    status: DeliveryStatus
    attempt: int
    error: str | None = None


class DeliveryService:
    """
    Coordinates creation and queueing of webhook delivery jobs.
    """

    def __init__(
        self,
        queue: InMemoryDeliveryQueue,
        idempotency_store: IdempotencyStore,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        self._queue = queue
        self._idempotency = idempotency_store
        self._retry_policy = (
            retry_policy or RetryPolicy()
        )

    def submit(
        self,
        request: DeliveryRequest,
    ) -> DeliveryResult:
        """
        Submit a signal for asynchronous delivery.
        """

        idempotency_key = (
            request.idempotency_key
            or request.signal_id
        )

        if self._idempotency.exists(
            idempotency_key
        ):
            return DeliveryResult(
                job_id="",
                signal_id=request.signal_id,
                status=DeliveryStatus.DUPLICATE,
                attempt=0,
            )

        job = DeliveryJob(
            job_id=str(uuid4()),
            signal_id=request.signal_id,
            webhook_url=request.webhook_url,
            payload=request.payload,
            attempt=0,
        )

        self._queue.enqueue(job)

        return DeliveryResult(
            job_id=job.job_id,
            signal_id=job.signal_id,
            status=DeliveryStatus.QUEUED,
            attempt=0,
        )

    def retry(
        self,
        job: DeliveryJob,
    ) -> DeliveryResult:
        """
        Requeue a failed delivery if retry policy allows it.
        """

        next_attempt = job.attempt + 1

        if not self._retry_policy.should_retry(
            next_attempt
        ):
            return DeliveryResult(
                job_id=job.job_id,
                signal_id=job.signal_id,
                status=DeliveryStatus.FAILED,
                attempt=next_attempt,
                error="Maximum retry attempts exceeded.",
            )

        retry_job = DeliveryJob(
            job_id=job.job_id,
            signal_id=job.signal_id,
            webhook_url=job.webhook_url,
            payload=job.payload,
            attempt=next_attempt,
        )

        self._queue.enqueue(retry_job)

        return DeliveryResult(
            job_id=job.job_id,
            signal_id=job.signal_id,
            status=DeliveryStatus.RETRYING,
            attempt=next_attempt,
        )

    def mark_delivered(
        self,
        job: DeliveryJob,
    ) -> None:
        """Mark a signal as successfully delivered."""

        self._idempotency.mark_completed(
            job.signal_id
        )
        
    def is_delivered(self, signal_id: str) -> bool:
    """Check whether a signal has already been delivered."""

        return self._idempotency.exists(signal_id)
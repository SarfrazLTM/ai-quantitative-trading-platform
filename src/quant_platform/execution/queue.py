"""
Webhook delivery queue.

The current implementation provides an in-memory queue for the
reference architecture. Production deployments can replace this
with Redis, Kafka, RabbitMQ, SQS, or another durable queue.
"""

from __future__ import annotations

from dataclasses import dataclass
from queue import Empty, Queue
from typing import Any


@dataclass(frozen=True, slots=True)
class DeliveryJob:
    """A unit of work for webhook delivery."""

    job_id: str
    signal_id: str
    webhook_url: str
    payload: dict[str, Any]
    attempt: int = 0


class InMemoryDeliveryQueue:
    """
    Thread-safe in-memory delivery queue.

    This implementation is intentionally simple and is suitable
    for tests and architectural demonstration.
    """

    def __init__(self) -> None:
        self._queue: Queue[DeliveryJob] = Queue()

    def enqueue(
        self,
        job: DeliveryJob,
    ) -> None:
        """Add a delivery job to the queue."""

        self._queue.put(job)

    def dequeue(
        self,
        timeout: float | None = None,
    ) -> DeliveryJob | None:
        """Retrieve the next job."""

        try:
            return self._queue.get(
                timeout=timeout,
            )
        except Empty:
            return None

    def task_done(self) -> None:
        """Mark the current queue task as completed."""

        self._queue.task_done()

    def size(self) -> int:
        """Return the number of queued jobs."""

        return self._queue.qsize()
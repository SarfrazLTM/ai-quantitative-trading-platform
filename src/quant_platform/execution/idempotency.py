"""
Idempotency support for webhook delivery.

Prevents the same delivery identifier from being processed
successfully more than once.
"""

from __future__ import annotations

from threading import Lock


class IdempotencyStore:
    """
    Thread-safe in-memory idempotency store.

    Production implementations can use Redis or another durable
    shared store.
    """

    def __init__(self) -> None:
        self._completed: set[str] = set()
        self._lock = Lock()

    def exists(
        self,
        key: str,
    ) -> bool:
        """Check whether a key has already completed."""

        with self._lock:
            return key in self._completed

    def mark_completed(
        self,
        key: str,
    ) -> None:
        """Mark a delivery key as successfully completed."""

        with self._lock:
            self._completed.add(key)

    def remove(
        self,
        key: str,
    ) -> None:
        """Remove a key from the completed set."""

        with self._lock:
            self._completed.discard(key)

    def clear(self) -> None:
        """Clear all stored idempotency keys."""

        with self._lock:
            self._completed.clear()

    def size(self) -> int:
        """Return the number of completed keys."""

        with self._lock:
            return len(self._completed)
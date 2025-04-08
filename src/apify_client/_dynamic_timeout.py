from __future__ import annotations

from collections.abc import AsyncIterable, Iterable
from typing import Protocol, Union

RequestContent = Union[str, bytes, Iterable[bytes], AsyncIterable[bytes]]


class DynamicTimeoutFunction(Protocol):
    """A function for dynamically creating suitable timeout for an http request."""

    def __call__(self, method: str, url: str, content: RequestContent) -> None | int:
        """Generate suitable timeout [s] for the request."""

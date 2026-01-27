"""Protocol definitions for type-safe resource clients.

These protocols define the minimal interface needed by resource clients,
allowing for structural typing without circular imports.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from apify_client._utils import JsonSerializable


@runtime_checkable
class HttpClientProtocol(Protocol):
    """HTTP client interface for resource clients (sync and async)."""

    def call(
        self,
        *,
        method: str,
        url: str,
        headers: dict[Any, Any] | None = None,
        params: dict[Any, Any] | None = None,
        data: Any = None,
        json: JsonSerializable | None = None,
        stream: bool | None = None,
        timeout_secs: int | None = None,
    ) -> Any:
        """Make an HTTP request to the Apify API."""
        ...


@runtime_checkable
class ApifyClientProtocol(Protocol):
    """Apify client interface for resource clients (sync and async)."""

    base_url: str
    public_base_url: str

    def actor(self, actor_id: str) -> Any:
        """Get client for a specific actor."""
        ...

    def run(self, run_id: str) -> Any:
        """Get client for a specific run."""
        ...

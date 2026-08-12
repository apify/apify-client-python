from __future__ import annotations

from typing import TYPE_CHECKING

import impit
from typing_extensions import override

from apify_client._consts import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_MIN_DELAY_BETWEEN_RETRIES,
    DEFAULT_TIMEOUT_LONG,
    DEFAULT_TIMEOUT_MAX,
    DEFAULT_TIMEOUT_MEDIUM,
    DEFAULT_TIMEOUT_SHORT,
)
from apify_client._docs import docs_group
from apify_client.http_clients._base import HttpClient, HttpClientAsync

if TYPE_CHECKING:
    from datetime import timedelta

    from apify_client._statistics import ClientStatistics
    from apify_client.http_compressors._base import HttpCompressor

_PERMANENT_ERRORS = (
    # A bad URL scheme or a request Impit itself rejects cannot succeed on a retry.
    impit.UnsupportedProtocol,
    impit.LocalProtocolError,
    # An over-long redirect chain is a routing loop, which repeating the request cannot break.
    impit.TooManyRedirects,
    # Status codes are retried by `_make_request` based on the status itself, never as a transport error.
    impit.HTTPStatusError,
)
"""Impit errors that a retry cannot fix. Everything else in the `impit.HTTPError` tree is treated as transient."""


@docs_group('HTTP clients')
class ImpitHttpClient(HttpClient):
    """Synchronous HTTP client for the Apify API built on top of [Impit](https://github.com/apify/impit).

    Impit is a high-performance HTTP client written in Rust that provides browser-like TLS fingerprints,
    automatic header ordering, and HTTP/2 support. This client wraps `impit.Client` and adds automatic retries
    with exponential backoff for rate-limited (HTTP 429) and server error (HTTP 5xx) responses.
    """

    @override
    def __init__(
        self,
        *,
        token: str | None = None,
        timeout_short: timedelta = DEFAULT_TIMEOUT_SHORT,
        timeout_medium: timedelta = DEFAULT_TIMEOUT_MEDIUM,
        timeout_long: timedelta = DEFAULT_TIMEOUT_LONG,
        timeout_max: timedelta = DEFAULT_TIMEOUT_MAX,
        max_retries: int = DEFAULT_MAX_RETRIES,
        min_delay_between_retries: timedelta = DEFAULT_MIN_DELAY_BETWEEN_RETRIES,
        statistics: ClientStatistics | None = None,
        headers: dict[str, str] | None = None,
        http_compressor: HttpCompressor | None = None,
    ) -> None:
        """Initialize the Impit-based synchronous HTTP client.

        Args:
            token: Apify API token for authentication.
            timeout_short: Default timeout for short-duration API operations (simple CRUD operations, ...).
            timeout_medium: Default timeout for medium-duration API operations (batch operations, listing, ...).
            timeout_long: Default timeout for long-duration API operations (long-polling, streaming, ...).
            timeout_max: Maximum timeout cap for any single request attempt, including tier and per-call timeouts.
            max_retries: Maximum number of retry attempts for failed requests.
            min_delay_between_retries: Minimum delay between retries (increases exponentially with each attempt).
            statistics: Statistics tracker for API calls. Created automatically if not provided.
            headers: Additional HTTP headers to include in all requests.
            http_compressor: Compressor used to compress request bodies. Defaults to `GzipHttpCompressor`.
        """
        super().__init__(
            token=token,
            timeout_short=timeout_short,
            timeout_medium=timeout_medium,
            timeout_long=timeout_long,
            timeout_max=timeout_max,
            max_retries=max_retries,
            min_delay_between_retries=min_delay_between_retries,
            statistics=statistics,
            headers=headers,
            http_compressor=http_compressor,
        )

        self._impit_client = impit.Client(follow_redirects=True)

    @override
    def is_timeout_error(self, exc: Exception) -> bool:
        return super().is_timeout_error(exc) or isinstance(exc, impit.TimeoutException)

    @override
    def close(self) -> None:
        """Release resources owned by this client.

        Impit doesn't expose a way to close its connection pool, and its `__exit__` keeps the client usable,
        so there is nothing to release yet. The method exists so the lifecycle interface is the same for every
        transport, and it will do real work once Impit supports it.
        """
        self._impit_client.__exit__(None, None, None)

    @override
    def send_request(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str],
        content: bytes | None,
        timeout: float | None,
        stream: bool,
    ) -> impit.Response:
        # Impit treats timeout=None as "use client default (30s)", not "no timeout".
        # Use a large value (24 hours) to effectively disable the timeout.
        # This can be removed once impit updates its behaviour: https://github.com/apify/impit/issues/401
        impit_timeout = 86_400 if timeout is None else timeout
        return self._impit_client.request(
            method=method,
            url=url,
            headers=headers,
            content=content,
            timeout=impit_timeout,
            stream=stream,
        )

    @override
    def is_retryable_transport_error(self, exc: Exception) -> bool:
        return self._is_transient_transport_error(
            exc,
            transport_errors=impit.HTTPError,
            permanent_errors=_PERMANENT_ERRORS,
        )


@docs_group('HTTP clients')
class ImpitHttpClientAsync(HttpClientAsync):
    """Asynchronous HTTP client for the Apify API built on top of [Impit](https://github.com/apify/impit).

    Impit is a high-performance HTTP client written in Rust that provides browser-like TLS fingerprints,
    automatic header ordering, and HTTP/2 support. This client wraps `impit.AsyncClient` and adds automatic retries
    with exponential backoff for rate-limited (HTTP 429) and server error (HTTP 5xx) responses.
    """

    @override
    def __init__(
        self,
        *,
        token: str | None = None,
        timeout_short: timedelta = DEFAULT_TIMEOUT_SHORT,
        timeout_medium: timedelta = DEFAULT_TIMEOUT_MEDIUM,
        timeout_long: timedelta = DEFAULT_TIMEOUT_LONG,
        timeout_max: timedelta = DEFAULT_TIMEOUT_MAX,
        max_retries: int = DEFAULT_MAX_RETRIES,
        min_delay_between_retries: timedelta = DEFAULT_MIN_DELAY_BETWEEN_RETRIES,
        statistics: ClientStatistics | None = None,
        headers: dict[str, str] | None = None,
        http_compressor: HttpCompressor | None = None,
    ) -> None:
        """Initialize the Impit-based asynchronous HTTP client.

        Args:
            token: Apify API token for authentication.
            timeout_short: Default timeout for short-duration API operations (simple CRUD operations, ...).
            timeout_medium: Default timeout for medium-duration API operations (batch operations, listing, ...).
            timeout_long: Default timeout for long-duration API operations (long-polling, streaming, ...).
            timeout_max: Maximum timeout cap for any single request attempt, including tier and per-call timeouts.
            max_retries: Maximum number of retry attempts for failed requests.
            min_delay_between_retries: Minimum delay between retries (increases exponentially with each attempt).
            statistics: Statistics tracker for API calls. Created automatically if not provided.
            headers: Additional HTTP headers to include in all requests.
            http_compressor: Compressor used to compress request bodies. Defaults to `GzipHttpCompressor`.
        """
        super().__init__(
            token=token,
            timeout_short=timeout_short,
            timeout_medium=timeout_medium,
            timeout_long=timeout_long,
            timeout_max=timeout_max,
            max_retries=max_retries,
            min_delay_between_retries=min_delay_between_retries,
            statistics=statistics,
            headers=headers,
            http_compressor=http_compressor,
        )

        self._impit_async_client = impit.AsyncClient(follow_redirects=True)

    @override
    def is_timeout_error(self, exc: Exception) -> bool:
        return super().is_timeout_error(exc) or isinstance(exc, impit.TimeoutException)

    @override
    async def aclose(self) -> None:
        """Release resources owned by this client.

        See `ImpitHttpClient.close` for why there is nothing to release yet.
        """
        await self._impit_async_client.__aexit__(None, None, None)

    @override
    async def send_request(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str],
        content: bytes | None,
        timeout: float | None,
        stream: bool,
    ) -> impit.Response:
        # See the synchronous implementation for why None maps to 24 hours.
        impit_timeout = 86_400 if timeout is None else timeout
        return await self._impit_async_client.request(
            method=method,
            url=url,
            headers=headers,
            content=content,
            timeout=impit_timeout,
            stream=stream,
        )

    @override
    def is_retryable_transport_error(self, exc: Exception) -> bool:
        return self._is_transient_transport_error(
            exc,
            transport_errors=impit.HTTPError,
            permanent_errors=_PERMANENT_ERRORS,
        )

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx2 as httpx
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
    # A request HTTPX rejects before sending it, e.g. one carrying an invalid header value.
    httpx.LocalProtocolError,
    # A URL scheme HTTPX refuses to speak, which repeating the request cannot change.
    httpx.UnsupportedProtocol,
    # An over-long redirect chain is a routing loop, which repeating the request cannot break.
    httpx.TooManyRedirects,
    # Only `Response.raise_for_status()` raises this, and the client never calls it - the shared pipeline decides on
    # status codes from the response itself.
    httpx.HTTPStatusError,
)
"""HTTPX errors that a retry cannot fix. Everything else in the `httpx.HTTPError` tree counts as transient."""


@docs_group('HTTP clients')
class HttpxHttpClient(HttpClient):
    """Synchronous HTTP client for the Apify API built on top of [HTTPX](https://github.com/pydantic/httpx2).

    This client wraps `httpx.Client` and adds automatic retries with exponential backoff for rate-limited
    (HTTP 429) and server error (HTTP 5xx) responses.

    HTTPX applies a request timeout to each socket operation rather than to the request as a whole, so a response
    whose body arrives slowly keeps resetting it and can outlast both the requested timeout and `timeout_max`. The
    default Impit client enforces the same value as a deadline for the whole request, body included.

    Requires the `httpx` extra: `pip install "apify-client[httpx]"`. That extra installs `httpx2`, Pydantic's
    maintained continuation of HTTPX, which this module imports under the `httpx` name.
    """

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
        """Initialize the HTTPX-based synchronous HTTP client.

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

        self._httpx_client = httpx.Client(
            follow_redirects=True,
            event_hooks={'response': [self._clear_response_cookies]},
        )

    @override
    def is_timeout_error(self, exc: Exception) -> bool:
        return super().is_timeout_error(exc) or isinstance(exc, httpx.TimeoutException)

    @override
    def is_retryable_transport_error(self, exc: Exception) -> bool:
        # Every error from HTTPX's own hierarchy counts as transient except the permanently-failing types listed in
        # `_PERMANENT_ERRORS`. Retrying is the default so a subclass HTTPX adds later is retried rather than
        # silently treated as fatal. HTTP status code errors are handled by the shared pipeline based on the
        # response status code, not here.
        return isinstance(exc, httpx.HTTPError) and not isinstance(exc, _PERMANENT_ERRORS)

    @override
    def close(self) -> None:
        """Close the underlying HTTPX connection pool."""
        self._httpx_client.close()

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
    ) -> httpx.Response:
        request = self._httpx_client.build_request(
            method=method,
            url=url,
            headers=headers,
            content=content,
            timeout=timeout,
        )
        _restore_explicit_cookie_header(request, headers)
        return self._httpx_client.send(request, stream=stream)

    def _clear_response_cookies(self, _response: httpx.Response) -> None:
        """Prevent HTTPX's shared cookie jar from leaking server cookies into later API requests."""
        self._httpx_client.cookies.clear()


@docs_group('HTTP clients')
class HttpxHttpClientAsync(HttpClientAsync):
    """Asynchronous HTTP client for the Apify API built on top of [HTTPX](https://github.com/pydantic/httpx2).

    This client wraps `httpx.AsyncClient` and adds automatic retries with exponential backoff for rate-limited
    (HTTP 429) and server error (HTTP 5xx) responses.

    HTTPX applies a request timeout to each socket operation rather than to the request as a whole, so a response
    whose body arrives slowly keeps resetting it and can outlast both the requested timeout and `timeout_max`. The
    default Impit client enforces the same value as a deadline for the whole request, body included.

    Requires the `httpx` extra: `pip install "apify-client[httpx]"`. That extra installs `httpx2`, Pydantic's
    maintained continuation of HTTPX, which this module imports under the `httpx` name.
    """

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
        """Initialize the HTTPX-based asynchronous HTTP client.

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

        self._httpx_async_client = httpx.AsyncClient(
            follow_redirects=True,
            event_hooks={'response': [self._clear_response_cookies]},
        )

    @override
    def is_timeout_error(self, exc: Exception) -> bool:
        return super().is_timeout_error(exc) or isinstance(exc, httpx.TimeoutException)

    @override
    def is_retryable_transport_error(self, exc: Exception) -> bool:
        # Every error from HTTPX's own hierarchy counts as transient except the permanently-failing types listed in
        # `_PERMANENT_ERRORS`. Retrying is the default so a subclass HTTPX adds later is retried rather than
        # silently treated as fatal. HTTP status code errors are handled by the shared pipeline based on the
        # response status code, not here.
        return isinstance(exc, httpx.HTTPError) and not isinstance(exc, _PERMANENT_ERRORS)

    @override
    async def aclose(self) -> None:
        """Close the underlying asynchronous HTTPX connection pool."""
        await self._httpx_async_client.aclose()

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
    ) -> httpx.Response:
        request = self._httpx_async_client.build_request(
            method=method,
            url=url,
            headers=headers,
            content=content,
            timeout=timeout,
        )
        _restore_explicit_cookie_header(request, headers)
        return await self._httpx_async_client.send(request, stream=stream)

    async def _clear_response_cookies(self, _response: httpx.Response) -> None:
        """Prevent HTTPX's shared cookie jar from leaking server cookies into later API requests."""
        self._httpx_async_client.cookies.clear()


def _restore_explicit_cookie_header(request: httpx.Request, headers: dict[str, str]) -> None:
    """Keep only cookies explicitly supplied for this request, never cookies from HTTPX's shared jar.

    HTTPX drops the `Cookie` header when it builds a redirect request and rebuilds it from the jar, so an explicit
    cookie only reaches the first hop of a redirected request.
    """
    explicit_cookie = next((value for key, value in headers.items() if key.lower() == 'cookie'), None)
    if explicit_cookie is None:
        request.headers.pop('cookie', None)
    else:
        request.headers['cookie'] = explicit_cookie

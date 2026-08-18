from __future__ import annotations

import asyncio
import json as jsonlib
import logging
import os
import random
import sys
import time
from contextlib import suppress
from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from importlib import metadata
from typing import TYPE_CHECKING, Any, TypeVar
from urllib.parse import urlencode

# `Protocol` comes from `typing_extensions`, not `typing`, because its runtime `isinstance` check looks attributes
# up statically. The `typing` implementation on Python 3.11 calls `hasattr`, which evaluates properties. On an
# unread streaming response, that either raises or silently buffers the whole body.
from typing_extensions import Protocol, runtime_checkable

from apify_client._consts import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_MIN_DELAY_BETWEEN_RETRIES,
    DEFAULT_TIMEOUT_LONG,
    DEFAULT_TIMEOUT_MAX,
    DEFAULT_TIMEOUT_MEDIUM,
    DEFAULT_TIMEOUT_SHORT,
    MIN_COMPRESSION_SIZE,
)
from apify_client._docs import docs_group
from apify_client._logging import LoggerOnce, log_context, logger_name
from apify_client._statistics import ClientStatistics
from apify_client._utils.http import is_compressible_content_type
from apify_client._utils.time import to_seconds
from apify_client.errors import ApifyApiError
from apify_client.http_compressors._gzip import GzipHttpCompressor

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Awaitable, Callable, Iterator, Mapping
    from types import TracebackType
    from typing import Self

    from apify_client.http_compressors._base import HttpCompressor
    from apify_client.types import JsonSerializable, Timeout

T = TypeVar('T')

logger = logging.getLogger(logger_name)
logger_once = LoggerOnce(logger)


@docs_group('HTTP clients')
@runtime_checkable
class HttpResponse(Protocol):
    """Protocol for HTTP response objects returned by HTTP clients.

    Any object that has the required attributes and methods can be used as an HTTP response
    (e.g., `impit.Response`). This enables custom HTTP client implementations to return
    their own response types.
    """

    @property
    def status_code(self) -> int:
        """HTTP status code of the response."""

    @property
    def text(self) -> str:
        """Response body decoded as text."""

    @property
    def content(self) -> bytes:
        """Raw response body as bytes."""

    @property
    def headers(self) -> Mapping[str, str]:
        """Response headers as a mapping."""

    def json(self) -> Any:
        """Parse response body as JSON."""

    def read(self) -> bytes:
        """Read the entire response body."""

    async def aread(self) -> bytes:
        """Read the entire response body asynchronously."""

    def close(self) -> None:
        """Close the response and release the connection."""

    async def aclose(self) -> None:
        """Close the response and release the connection asynchronously."""

    def iter_bytes(self) -> Iterator[bytes]:
        """Iterate over the response body in bytes chunks."""

    def aiter_bytes(self) -> AsyncIterator[bytes]:
        """Iterate over the response body in bytes chunks asynchronously."""


@docs_group('HTTP clients')
class HttpClientBase:
    """Shared configuration and utilities for HTTP clients.

    Provides common functionality for both sync and async HTTP clients including:
    header construction, parameter parsing, request body preparation, URL building,
    and timeout calculation.

    Subclasses should call `super().__init__()` to initialize shared configuration.
    The helper methods are then available for use in the `call()` implementation.
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
        """Initialize the HTTP client base.

        Args:
            token: Apify API token for authentication.
            timeout_short: Default timeout for short-duration API operations (simple CRUD operations, ...).
            timeout_medium: Default timeout for medium-duration API operations (batch operations, listing, ...).
            timeout_long: Default timeout for long-duration API operations (long-polling, streaming, ...).
            timeout_max: Maximum timeout cap for any single request attempt, including tier and per-call timeouts.
            max_retries: Maximum number of retries for failed requests.
            min_delay_between_retries: Minimum delay between retries.
            statistics: Statistics tracker for API calls. Created automatically if not provided.
            headers: Additional HTTP headers to include in all requests.
            http_compressor: Compressor used to compress request bodies. Defaults to `GzipHttpCompressor`.
        """
        self._http_compressor = http_compressor if http_compressor is not None else GzipHttpCompressor()
        self._timeout_short = timeout_short
        self._timeout_medium = timeout_medium
        self._timeout_long = timeout_long
        self._timeout_max = timeout_max
        self._max_retries = max_retries
        self._min_delay_between_retries = min_delay_between_retries
        self._statistics = statistics or ClientStatistics()

        # Build default headers.
        default_headers: dict[str, str] = {'Accept': 'application/json, */*'}

        workflow_key = os.getenv('APIFY_WORKFLOW_KEY')
        if workflow_key is not None:
            default_headers['X-Apify-Workflow-Key'] = workflow_key

        is_at_home = str('APIFY_IS_AT_HOME' in os.environ).lower()
        python_version = '.'.join([str(x) for x in sys.version_info[:3]])
        client_version = metadata.version('apify-client')

        user_agent = f'ApifyClient/{client_version} ({sys.platform}; Python/{python_version}); isAtHome/{is_at_home}'
        default_headers['User-Agent'] = user_agent

        if token is not None:
            default_headers['Authorization'] = f'Bearer {token}'

        self._headers = self._merge_headers(default_headers, headers)

    def set_default_authorization(self, token: str) -> None:
        """Set the `Authorization` header from the token, unless an authorization header is already configured.

        Args:
            token: The Apify API token to set as the `Bearer` authorization.
        """
        if self._get_header(self._headers, 'authorization') is None:
            self._headers['Authorization'] = f'Bearer {token}'

    def is_timeout_error(self, exc: Exception) -> bool:
        """Return whether an exception represents a transport timeout.

        Recognizes Python's own `TimeoutError`. Transport adapters extend it with the timeout types their HTTP
        library defines.
        """
        return isinstance(exc, TimeoutError)

    def is_retryable_transport_error(self, exc: Exception) -> bool:
        """Return whether an underlying HTTP-library exception is retryable.

        The default classifies nothing as retryable, so a transport that doesn't override it gives up on the first
        connection failure. Every transport adapter should map its own transient error types here.
        """
        _ = exc
        return False

    @staticmethod
    def _merge_headers(base: dict[str, str] | None, override: dict[str, str] | None) -> dict[str, str]:
        """Merge two header dicts, treating header names case-insensitively.

        A header from `override` replaces a same-named header in `base` regardless of the casing
        of either name, and keeps the casing it was passed with.
        """
        merged = dict(base) if base else {}
        for key, value in (override or {}).items():
            for existing_key in [k for k in merged if k.lower() == key.lower()]:
                del merged[existing_key]
            merged[key] = value
        return merged

    @staticmethod
    def _get_header(headers: dict[str, str], name: str) -> str | None:
        """Look up a header value by name, treated case-insensitively. Returns `None` if the header is not set."""
        return next((value for key, value in headers.items() if key.lower() == name.lower()), None)

    @staticmethod
    def _parse_params(params: dict[str, Any] | None) -> dict[str, Any] | None:
        """Convert request parameters to Apify API-compatible formats.

        Converts booleans to 'false'/'true', lists to comma-separated strings, datetimes to ISO 8601 Zulu format.
        """
        if params is None:
            return None

        parsed_params: dict[str, Any] = {}
        for key, value in params.items():
            if isinstance(value, bool):
                parsed_params[key] = (str(value)).lower()
            elif isinstance(value, list):
                parsed_params[key] = ','.join(value)
            elif isinstance(value, datetime):
                # Treat a naive datetime as UTC; `.astimezone()` would otherwise assume the host's local tz.
                aware = value.replace(tzinfo=UTC) if value.tzinfo is None else value
                utc_aware_dt = aware.astimezone(UTC)
                iso_str = utc_aware_dt.isoformat(timespec='milliseconds')
                parsed_params[key] = iso_str.replace('+00:00', 'Z')
            elif value is not None:
                parsed_params[key] = value

        return parsed_params

    def _compute_timeout(self, timeout: Timeout, *, attempt: int) -> int | float | None:
        """Resolve a timeout tier and compute the timeout for a request attempt with exponential increase.

        For `no_timeout`, returns `None` to indicate no timeout. For tier literals and explicit `timedelta` values,
        doubles the timeout with each attempt but caps at `timeout_max`. A base timeout above `timeout_max` is
        capped too, which warns once per timeout kind since the requested value does not take effect in full.

        Args:
            timeout: The timeout specification to resolve (tier literal or explicit `timedelta`).
            attempt: Current attempt number (1-indexed).

        Returns:
            Timeout in seconds, or `None` for no timeout.
        """
        if timeout == 'no_timeout':
            return None

        if timeout == 'short':
            resolved = self._timeout_short
        elif timeout == 'medium':
            resolved = self._timeout_medium
        elif timeout == 'long':
            resolved = self._timeout_long
        else:
            resolved = timeout

        if resolved > self._timeout_max:
            # Keyed per timeout kind, so retries and repeated calls do not spam the log with the same warning.
            logger_once.log(
                f'The requested timeout of {to_seconds(resolved)}s exceeds `timeout_max` '
                f'({to_seconds(self._timeout_max)}s) and is capped at it. Raise `timeout_max` on the client '
                'to allow longer request timeouts.',
                key=f'timeout-capped-{timeout if isinstance(timeout, str) else "explicit"}',
                level=logging.WARNING,
            )

        new_timeout = min(resolved * (2 ** (attempt - 1)), self._timeout_max)
        return to_seconds(new_timeout)

    @staticmethod
    def _is_body_worth_compressing(data: str | bytes | bytearray | None) -> bool:
        """Whether this body clears the size threshold `_prepare_request_call` compresses at, cheaply.

        Below the threshold nothing is ever compressed. At or above it the content type and a caller-supplied
        `Content-Encoding` still decide, but checking those here would buy nothing - a body that turns out to be
        already encoded only wastes the thread hop this answer guards.

        The threshold is measured on encoded bytes, so a character count alone cannot decide a `str`. It is a
        lower bound, so a `str` long enough in characters is long enough in bytes too. Below that the encoded
        length decides, and the body is then under 4 KiB, so encoding it here is cheap.
        """
        if isinstance(data, str):
            return len(data) >= MIN_COMPRESSION_SIZE or len(data.encode('utf-8')) >= MIN_COMPRESSION_SIZE
        if isinstance(data, (bytes, bytearray)):
            return len(data) >= MIN_COMPRESSION_SIZE
        return False

    def _prepare_request_call(
        self,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        data: str | bytes | bytearray | None = None,
        json: JsonSerializable | None = None,
    ) -> tuple[dict[str, str], dict[str, Any] | None, bytes | None]:
        """Prepare headers, params, and body for an HTTP request.

        Merges the client's default headers (including authorization) with per-request headers and serializes a
        JSON body. Header names are treated case-insensitively and per-request values win over the client
        defaults. For JSON bodies, a `Content-Type` header is set unless the caller supplied one.

        The body is compressed unless a `Content-Encoding` header is already set, the body is smaller than
        `MIN_COMPRESSION_SIZE`, or its content type says the payload is already compressed. A caller-supplied
        `Content-Encoding` is forwarded verbatim, which is how a pre-encoded body is uploaded - including one in
        an encoding the client ships no compressor for. `Content-Encoding: identity` therefore opts a single
        request out of compression.
        """
        if json is not None and data is not None:
            raise ValueError('Cannot pass both "json" and "data" parameters at the same time!')

        headers = self._merge_headers(self._headers, headers)

        # Dump JSON data to a string so it can be sent as a request body.
        if json is not None:
            data = jsonlib.dumps(json, ensure_ascii=False, allow_nan=False, default=str).encode('utf-8')
            if self._get_header(headers, 'content-type') is None:
                headers['Content-Type'] = 'application/json'

        if isinstance(data, (str, bytes, bytearray)):
            if isinstance(data, str):
                data = data.encode('utf-8')
            elif isinstance(data, bytearray):
                data = bytes(data)

            # A caller-supplied encoding says the body arrives already encoded, so compressing it here would
            # both mislabel it and waste the work.
            if (
                self._get_header(headers, 'content-encoding') is None
                and len(data) >= MIN_COMPRESSION_SIZE
                and is_compressible_content_type(self._get_header(headers, 'content-type'))
            ):
                data = self._http_compressor.compress(data)
                headers = self._merge_headers(headers, {'Content-Encoding': self._http_compressor.content_encoding})

        return (headers, self._parse_params(params), data)

    def _build_url_with_params(self, url: str, *, params: dict[str, Any] | None = None) -> str:
        """Build a URL with query parameters appended. List values are expanded into multiple key=value pairs."""
        if not params:
            return url

        param_pairs = list[tuple[str, str]]()
        for key, value in params.items():
            if isinstance(value, list):
                param_pairs.extend((key, str(v)) for v in value)
            else:
                param_pairs.append((key, str(value)))

        query_string = urlencode(param_pairs)

        return f'{url}?{query_string}'

    def _handle_request_exception(self, exc: Exception, *, stop_retrying: Callable[[], None]) -> None:
        """Stop retrying when an exception is not a retryable transport failure."""
        logger.debug('Request threw exception', exc_info=exc)
        if not self.is_retryable_transport_error(exc):
            logger.debug('Exception is not retryable', exc_info=exc)
            stop_retrying()

    @staticmethod
    def _is_transient_transport_error(
        exc: Exception,
        *,
        transport_errors: type[Exception] | tuple[type[Exception], ...],
        permanent_errors: tuple[type[Exception], ...],
    ) -> bool:
        """Apply the shared retry policy to an exception raised by an HTTP library.

        Every error from the library's own hierarchy counts as transient except the permanently-failing types the
        adapter lists. Retrying is the default because transports also report genuinely transient failures through
        their generic base class, e.g. Impit raises a bare `impit.HTTPError` for a body that ends mid-chunk. Sharing
        one policy across adapters keeps a change of transport from changing which failures are retried.
        """
        return isinstance(exc, transport_errors) and not isinstance(exc, permanent_errors)


@docs_group('HTTP clients')
class HttpClient(HttpClientBase):
    """Base class for synchronous HTTP clients used by `ApifyClient`.

    Concrete clients inherit its request preparation, retry, and error handling, and implement the transport,
    error-classification, and lifecycle hooks. Only `send_request` has to be implemented, the other hooks have
    defaults. Replacing `call` itself also remains supported, and then none of the hooks are used. Helper methods
    from `HttpClientBase` remain available for request preparation, URL building, and parameter parsing.

    The client's default headers from `self._headers` have to go out with every request, otherwise the
    `Authorization` header never reaches the API. The inherited `call` merges them into the per-request headers
    through `_prepare_request_call`, so only a client that replaces `call` has to do it itself.
    """

    def __enter__(self) -> Self:
        """Return this client and close it when the context exits."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close resources owned by the HTTP client."""
        self.close()

    def call(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        data: str | bytes | bytearray | None = None,
        json: JsonSerializable | None = None,
        stream: bool | None = None,
        timeout: Timeout = 'medium',
    ) -> HttpResponse:
        """Make an HTTP request with automatic retry and exponential backoff.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            url: Full URL to make the request to.
            headers: Additional headers to include.
            params: Query parameters to append to the URL.
            data: Raw request body data. Cannot be used together with json.
            json: JSON-serializable data for the request body. Cannot be used together with data.
            stream: Whether to stream the response body.
            timeout: Timeout for the API HTTP request. Use `short`, `medium`, or `long` tier literals for
                preconfigured timeouts. A `timedelta` overrides it for this call (capped at `timeout_max`), and
                `no_timeout` disables the timeout entirely.

        Returns:
            The HTTP response object.

        Raises:
            ApifyApiError: If the request fails after all retries or returns a non-retryable error status.
            ValueError: If both json and data are provided.
        """
        log_context.method.set(method)
        log_context.url.set(url)

        self._statistics.calls += 1

        prepared_headers, prepared_params, content = self._prepare_request_call(
            headers=headers,
            params=params,
            data=data,
            json=json,
        )

        return self._retry_with_exp_backoff(
            lambda stop_retrying, attempt: self._make_request(
                stop_retrying=stop_retrying,
                attempt=attempt,
                method=method,
                url=url,
                headers=prepared_headers,
                params=prepared_params,
                content=content,
                stream=stream,
                timeout=timeout,
            ),
            max_retries=self._max_retries,
            backoff_base=self._min_delay_between_retries,
        )

    def close(self) -> None:
        """Close resources owned by the HTTP client.

        Transports that own a connection pool or a session override it. The default does nothing.
        """

    def send_request(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str],
        content: bytes | None,
        timeout: float | None,
        stream: bool,
    ) -> HttpResponse:
        """Send one request through the underlying HTTP library.

        Required by the inherited `call`, so a transport adapter must implement it. Overriding `call` itself
        bypasses it entirely.
        """
        raise NotImplementedError

    @staticmethod
    def _retry_with_exp_backoff(
        func: Callable[[Callable[[], None], int], T],
        *,
        max_retries: int = 8,
        backoff_base: timedelta = timedelta(milliseconds=500),
        backoff_factor: float = 2,
        random_factor: float = 1,
    ) -> T:
        """Retry a function with exponential backoff and jitter."""
        if max_retries < 1:
            raise ValueError(f'max_retries must be at least 1, got {max_retries}')

        random_factor = min(max(0, random_factor), 1)
        backoff_factor = min(max(1, backoff_factor), 10)
        swallow = True

        def stop_retrying() -> None:
            nonlocal swallow
            swallow = False

        for attempt in range(1, max_retries + 1):
            try:
                return func(stop_retrying, attempt)
            except Exception:
                if not swallow:
                    raise

            random_sleep_factor = random.uniform(1, 1 + random_factor)
            backoff_base_secs = to_seconds(backoff_base)
            backoff_exp_factor = backoff_factor ** (attempt - 1)
            time.sleep(random_sleep_factor * backoff_base_secs * backoff_exp_factor)

        return func(stop_retrying, max_retries + 1)

    def _make_request(
        self,
        *,
        stop_retrying: Callable[[], None],
        attempt: int,
        method: str,
        url: str,
        headers: dict[str, str],
        params: dict[str, Any] | None,
        content: bytes | None,
        stream: bool | None,
        timeout: Timeout,
    ) -> HttpResponse:
        """Execute one request attempt through the transport adapter."""
        log_context.attempt.set(attempt)
        logger.debug('Sending request')

        self._statistics.requests += 1

        try:
            response = self.send_request(
                method=method,
                url=self._build_url_with_params(url, params=params),
                headers=headers,
                content=content,
                timeout=self._compute_timeout(timeout, attempt=attempt),
                stream=stream or False,
            )
        except Exception as exc:
            self._handle_request_exception(exc, stop_retrying=stop_retrying)
            raise

        if response.status_code < HTTPStatus.MULTIPLE_CHOICES:
            logger.debug('Request successful', extra={'status_code': response.status_code})
            return response

        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            self._statistics.add_rate_limit_error(attempt)

        logger.debug('Request unsuccessful', extra={'status_code': response.status_code})
        if (
            response.status_code < HTTPStatus.INTERNAL_SERVER_ERROR
            and response.status_code != HTTPStatus.TOO_MANY_REQUESTS
        ):
            logger.debug('Status code is not retryable', extra={'status_code': response.status_code})
            stop_retrying()

        try:
            response.read()
        except Exception as exc:
            with suppress(Exception):
                response.close()
            self._handle_request_exception(exc, stop_retrying=stop_retrying)
            raise

        raise ApifyApiError(response, attempt, method=method)


@docs_group('HTTP clients')
class HttpClientAsync(HttpClientBase):
    """Base class for asynchronous HTTP clients used by `ApifyClientAsync`.

    Extend this class to create a custom asynchronous HTTP client. See `HttpClient`
    for details on the expected behavior.
    """

    async def __aenter__(self) -> Self:
        """Return this client and close it when the async context exits."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close resources owned by the asynchronous HTTP client."""
        await self.aclose()

    async def call(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        data: str | bytes | bytearray | None = None,
        json: JsonSerializable | None = None,
        stream: bool | None = None,
        timeout: Timeout = 'medium',
    ) -> HttpResponse:
        """Make an HTTP request with automatic retry and exponential backoff.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            url: Full URL to make the request to.
            headers: Additional headers to include.
            params: Query parameters to append to the URL.
            data: Raw request body data. Cannot be used together with json.
            json: JSON-serializable data for the request body. Cannot be used together with data.
            stream: Whether to stream the response body.
            timeout: Timeout for the API HTTP request. Use `short`, `medium`, or `long` tier literals for
                preconfigured timeouts. A `timedelta` overrides it for this call (capped at `timeout_max`), and
                `no_timeout` disables the timeout entirely.

        Returns:
            The HTTP response object.

        Raises:
            ApifyApiError: If the request fails after all retries or returns a non-retryable error status.
            ValueError: If both json and data are provided.
        """
        log_context.method.set(method)
        log_context.url.set(url)

        self._statistics.calls += 1

        # Serializing and compressing a request body is CPU-bound and would block the event loop, so
        # offload preparation to a worker thread whenever there is something to compress. A body the
        # client sends as it is costs less to prepare inline than the hop itself. A `json` body always
        # hops, as its size is only known once serialized.
        if json is not None or self._is_body_worth_compressing(data):
            prepared_headers, prepared_params, content = await asyncio.to_thread(
                self._prepare_request_call,
                headers=headers,
                params=params,
                data=data,
                json=json,
            )
        else:
            prepared_headers, prepared_params, content = self._prepare_request_call(
                headers=headers,
                params=params,
                data=data,
                json=json,
            )

        return await self._retry_with_exp_backoff(
            lambda stop_retrying, attempt: self._make_request(
                stop_retrying=stop_retrying,
                attempt=attempt,
                method=method,
                url=url,
                headers=prepared_headers,
                params=prepared_params,
                content=content,
                stream=stream,
                timeout=timeout,
            ),
            max_retries=self._max_retries,
            backoff_base=self._min_delay_between_retries,
        )

    async def aclose(self) -> None:
        """Close resources owned by the asynchronous HTTP client.

        Transports that own a connection pool or a session override it. The default does nothing.
        """

    async def send_request(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str],
        content: bytes | None,
        timeout: float | None,
        stream: bool,
    ) -> HttpResponse:
        """Send one request through the underlying HTTP library.

        Required by the inherited `call`, so a transport adapter must implement it. Overriding `call` itself
        bypasses it entirely.
        """
        raise NotImplementedError

    @staticmethod
    async def _retry_with_exp_backoff(
        func: Callable[[Callable[[], None], int], Awaitable[T]],
        *,
        max_retries: int = 8,
        backoff_base: timedelta = timedelta(milliseconds=500),
        backoff_factor: float = 2,
        random_factor: float = 1,
    ) -> T:
        """Retry an async function with exponential backoff and jitter."""
        if max_retries < 1:
            raise ValueError(f'max_retries must be at least 1, got {max_retries}')

        random_factor = min(max(0, random_factor), 1)
        backoff_factor = min(max(1, backoff_factor), 10)
        swallow = True

        def stop_retrying() -> None:
            nonlocal swallow
            swallow = False

        for attempt in range(1, max_retries + 1):
            try:
                return await func(stop_retrying, attempt)
            except Exception:
                if not swallow:
                    raise

            random_sleep_factor = random.uniform(1, 1 + random_factor)
            backoff_base_secs = to_seconds(backoff_base)
            backoff_exp_factor = backoff_factor ** (attempt - 1)
            await asyncio.sleep(random_sleep_factor * backoff_base_secs * backoff_exp_factor)

        return await func(stop_retrying, max_retries + 1)

    async def _make_request(
        self,
        *,
        stop_retrying: Callable[[], None],
        attempt: int,
        method: str,
        url: str,
        headers: dict[str, str],
        params: dict[str, Any] | None,
        content: bytes | None,
        stream: bool | None,
        timeout: Timeout,
    ) -> HttpResponse:
        """Execute one request attempt through the transport adapter."""
        log_context.attempt.set(attempt)
        logger.debug('Sending request')

        self._statistics.requests += 1

        try:
            response = await self.send_request(
                method=method,
                url=self._build_url_with_params(url, params=params),
                headers=headers,
                content=content,
                timeout=self._compute_timeout(timeout, attempt=attempt),
                stream=stream or False,
            )
        except Exception as exc:
            self._handle_request_exception(exc, stop_retrying=stop_retrying)
            raise

        if response.status_code < HTTPStatus.MULTIPLE_CHOICES:
            logger.debug('Request successful', extra={'status_code': response.status_code})
            return response

        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            self._statistics.add_rate_limit_error(attempt)

        logger.debug('Request unsuccessful', extra={'status_code': response.status_code})
        if (
            response.status_code < HTTPStatus.INTERNAL_SERVER_ERROR
            and response.status_code != HTTPStatus.TOO_MANY_REQUESTS
        ):
            logger.debug('Status code is not retryable', extra={'status_code': response.status_code})
            stop_retrying()

        try:
            await response.aread()
        except Exception as exc:
            with suppress(Exception):
                await response.aclose()
            self._handle_request_exception(exc, stop_retrying=stop_retrying)
            raise

        raise ApifyApiError(response, attempt, method=method)

from __future__ import annotations

import asyncio
import logging
import random
import time
from datetime import timedelta
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, TypeVar

import impit

from apify_client._consts import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_MIN_DELAY_BETWEEN_RETRIES,
    DEFAULT_TIMEOUT_LONG,
    DEFAULT_TIMEOUT_MAX,
    DEFAULT_TIMEOUT_MEDIUM,
    DEFAULT_TIMEOUT_SHORT,
)
from apify_client._docs import docs_group
from apify_client._http_clients import HttpClient, HttpClientAsync
from apify_client._logging import log_context, logger_name
from apify_client._utils import to_seconds
from apify_client.errors import ApifyApiError, InvalidResponseBodyError

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from apify_client._http_clients import HttpResponse
    from apify_client._statistics import ClientStatistics
    from apify_client._types import JsonSerializable, Timeout

T = TypeVar('T')

logger = logging.getLogger(logger_name)


def _is_retryable_error(exc: Exception) -> bool:
    """Check if an exception represents a transient error that should be retried.

    All `impit.HTTPError` subclasses are considered retryable because they represent transport-level failures
    (network issues, timeouts, protocol errors, body decoding errors) that are typically transient. HTTP status
    code errors are handled separately in `_make_request` based on the response status code, not here.
    """
    return isinstance(
        exc,
        (
            InvalidResponseBodyError,
            impit.HTTPError,
        ),
    )


@docs_group('HTTP clients')
class ImpitHttpClient(HttpClient):
    """Synchronous HTTP client for the Apify API built on top of [Impit](https://github.com/apify/impit).

    Impit is a high-performance HTTP client written in Rust that provides browser-like TLS fingerprints,
    automatic header ordering, and HTTP/2 support. This client wraps `impit.Client` and adds automatic retries
    with exponential backoff for rate-limited (HTTP 429) and server error (HTTP 5xx) responses.
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
    ) -> None:
        """Initialize the Impit-based synchronous HTTP client.

        Args:
            token: Apify API token for authentication.
            timeout_short: Default timeout for short-duration API operations (simple CRUD operations, ...).
            timeout_medium: Default timeout for medium-duration API operations (batch operations, listing, ...).
            timeout_long: Default timeout for long-duration API operations (long-polling, streaming, ...).
            timeout_max: Maximum timeout cap for exponential timeout growth across retries.
            max_retries: Maximum number of retry attempts for failed requests.
            min_delay_between_retries: Minimum delay between retries (increases exponentially with each attempt).
            statistics: Statistics tracker for API calls. Created automatically if not provided.
            headers: Additional HTTP headers to include in all requests.
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
        )

        self._impit_client = impit.Client(
            headers=self._headers,
            follow_redirects=True,
        )

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
                preconfigured timeouts. A `timedelta` overrides it for this call, and `no_timeout` disables
                the timeout entirely.

        Returns:
            The HTTP response object.

        Raises:
            ApifyApiError: If the request fails after all retries or returns a non-retryable error status.
            ValueError: If both json and data are provided.
        """
        log_context.method.set(method)
        log_context.url.set(url)

        self._statistics.calls += 1

        prepared_headers, prepared_params, content = self._prepare_request_call(headers, params, data, json)

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
    ) -> impit.Response:
        """Execute a single HTTP request attempt.

        Args:
            stop_retrying: Callback to signal that retries should stop.
            attempt: Current attempt number (1-indexed).
            method: HTTP method.
            url: Request URL.
            headers: Request headers.
            params: Query parameters.
            content: Request body content.
            stream: Whether to stream the response.
            timeout: Timeout for this request.

        Returns:
            The HTTP response object.

        Raises:
            ApifyApiError: If the request fails with an error status.
        """
        log_context.attempt.set(attempt)
        logger.debug('Sending request')

        self._statistics.requests += 1

        try:
            url_with_params = self._build_url_with_params(url, params)

            response = self._impit_client.request(
                method=method,
                url=url_with_params,
                headers=headers,
                content=content,
                timeout=self._compute_timeout(timeout, attempt),
                stream=stream or False,
            )

            if response.status_code < HTTPStatus.MULTIPLE_CHOICES:
                logger.debug('Request successful', extra={'status_code': response.status_code})
                return response

            if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                self._statistics.add_rate_limit_error(attempt)

        except Exception as exc:
            logger.debug('Request threw exception', exc_info=exc)
            if not _is_retryable_error(exc):
                logger.debug('Exception is not retryable', exc_info=exc)
                stop_retrying()
            raise

        # Retry only server errors (5xx) and rate limits (429).
        logger.debug('Request unsuccessful', extra={'status_code': response.status_code})
        if (
            response.status_code < HTTPStatus.INTERNAL_SERVER_ERROR
            and response.status_code != HTTPStatus.TOO_MANY_REQUESTS
        ):
            logger.debug('Status code is not retryable', extra={'status_code': response.status_code})
            stop_retrying()

        # Read the response in case it is a stream, so we can raise the error properly.
        response.read()
        raise ApifyApiError(response, attempt, method=method)

    @staticmethod
    def _retry_with_exp_backoff(
        func: Callable[[Callable[[], None], int], T],
        *,
        max_retries: int = 8,
        backoff_base: timedelta = timedelta(milliseconds=500),
        backoff_factor: float = 2,
        random_factor: float = 1,
    ) -> T:
        """Retry a function with exponential backoff and jitter.

        Args:
            func: Function to retry. Receives (stop_retrying callback, attempt number).
            max_retries: Maximum retry attempts.
            backoff_base: Base delay.
            backoff_factor: Exponential multiplier (clamped to 1-10).
            random_factor: Jitter factor (clamped to 0-1).

        Returns:
            The function's return value on success.

        Raises:
            Exception: Re-raises the last exception if all retries fail or stop_retrying is called.
        """
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

            sleep_time_secs = random_sleep_factor * backoff_base_secs * backoff_exp_factor
            time.sleep(sleep_time_secs)

        return func(stop_retrying, max_retries + 1)


@docs_group('HTTP clients')
class ImpitHttpClientAsync(HttpClientAsync):
    """Asynchronous HTTP client for the Apify API built on top of [Impit](https://github.com/apify/impit).

    Impit is a high-performance HTTP client written in Rust that provides browser-like TLS fingerprints,
    automatic header ordering, and HTTP/2 support. This client wraps `impit.AsyncClient` and adds automatic retries
    with exponential backoff for rate-limited (HTTP 429) and server error (HTTP 5xx) responses.
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
    ) -> None:
        """Initialize the Impit-based asynchronous HTTP client.

        Args:
            token: Apify API token for authentication.
            timeout_short: Default timeout for short-duration API operations (simple CRUD operations, ...).
            timeout_medium: Default timeout for medium-duration API operations (batch operations, listing, ...).
            timeout_long: Default timeout for long-duration API operations (long-polling, streaming, ...).
            timeout_max: Maximum timeout cap for exponential timeout growth across retries.
            max_retries: Maximum number of retry attempts for failed requests.
            min_delay_between_retries: Minimum delay between retries (increases exponentially with each attempt).
            statistics: Statistics tracker for API calls. Created automatically if not provided.
            headers: Additional HTTP headers to include in all requests.
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
        )

        self._impit_async_client = impit.AsyncClient(
            headers=self._headers,
            follow_redirects=True,
        )

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
                preconfigured timeouts. A `timedelta` overrides it for this call, and `no_timeout` disables
                the timeout entirely.

        Returns:
            The HTTP response object.

        Raises:
            ApifyApiError: If the request fails after all retries or returns a non-retryable error status.
            ValueError: If both json and data are provided.
        """
        log_context.method.set(method)
        log_context.url.set(url)

        self._statistics.calls += 1

        prepared_headers, prepared_params, content = self._prepare_request_call(headers, params, data, json)

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
    ) -> impit.Response:
        """Execute a single HTTP request attempt.

        Args:
            stop_retrying: Callback to signal that retries should stop.
            attempt: Current attempt number (1-indexed).
            method: HTTP method.
            url: Request URL.
            headers: Request headers.
            params: Query parameters.
            content: Request body content.
            stream: Whether to stream the response.
            timeout: Timeout for this request.

        Returns:
            The HTTP response object.

        Raises:
            ApifyApiError: If the request fails with an error status.
        """
        log_context.attempt.set(attempt)
        logger.debug('Sending request')

        self._statistics.requests += 1

        try:
            url_with_params = self._build_url_with_params(url, params)

            response = await self._impit_async_client.request(
                method=method,
                url=url_with_params,
                headers=headers,
                content=content,
                timeout=self._compute_timeout(timeout, attempt),
                stream=stream or False,
            )

            if response.status_code < HTTPStatus.MULTIPLE_CHOICES:
                logger.debug('Request successful', extra={'status_code': response.status_code})
                return response

            if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                self._statistics.add_rate_limit_error(attempt)

        except Exception as exc:
            logger.debug('Request threw exception', exc_info=exc)
            if not _is_retryable_error(exc):
                logger.debug('Exception is not retryable', exc_info=exc)
                stop_retrying()
            raise

        # Retry only server errors (5xx) and rate limits (429).
        logger.debug('Request unsuccessful', extra={'status_code': response.status_code})
        if (
            response.status_code < HTTPStatus.INTERNAL_SERVER_ERROR
            and response.status_code != HTTPStatus.TOO_MANY_REQUESTS
        ):
            logger.debug('Status code is not retryable', extra={'status_code': response.status_code})
            stop_retrying()

        # Read the response in case it is a stream, so we can raise the error properly.
        await response.aread()
        raise ApifyApiError(response, attempt, method=method)

    @staticmethod
    async def _retry_with_exp_backoff(
        func: Callable[[Callable[[], None], int], Awaitable[T]],
        *,
        max_retries: int = 8,
        backoff_base: timedelta = timedelta(milliseconds=500),
        backoff_factor: float = 2,
        random_factor: float = 1,
    ) -> T:
        """Retry an async function with exponential backoff and jitter.

        Args:
            func: Async function to retry. Receives (stop_retrying callback, attempt number).
            max_retries: Maximum retry attempts.
            backoff_base: Base delay.
            backoff_factor: Exponential multiplier (clamped to 1-10).
            random_factor: Jitter factor (clamped to 0-1).

        Returns:
            The function's return value on success.

        Raises:
            Exception: Re-raises the last exception if all retries fail or stop_retrying is called.
        """
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

            sleep_time_secs = random_sleep_factor * backoff_base_secs * backoff_exp_factor
            await asyncio.sleep(sleep_time_secs)

        return await func(stop_retrying, max_retries + 1)

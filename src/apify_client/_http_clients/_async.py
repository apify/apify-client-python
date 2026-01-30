from __future__ import annotations

import asyncio
import logging
import random
from datetime import timedelta
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, TypeVar

import impit

from apify_client._consts import DEFAULT_MAX_RETRIES, DEFAULT_MIN_DELAY_BETWEEN_RETRIES, DEFAULT_TIMEOUT
from apify_client._http_clients._base import BaseHttpClient
from apify_client._logging import log_context, logger_name
from apify_client._utils import to_seconds
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from apify_client._consts import JsonSerializable
    from apify_client._statistics import ClientStatistics

T = TypeVar('T')

logger = logging.getLogger(logger_name)


class AsyncHttpClient(BaseHttpClient):
    """Asynchronous HTTP client for Apify API with automatic retries and exponential backoff."""

    def __init__(
        self,
        *,
        token: str | None = None,
        timeout: timedelta = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        min_delay_between_retries: timedelta = DEFAULT_MIN_DELAY_BETWEEN_RETRIES,
        statistics: ClientStatistics | None = None,
    ) -> None:
        """Initialize the asynchronous HTTP client.

        Args:
            token: Apify API token for authentication.
            timeout: Request timeout.
            max_retries: Maximum number of retries for failed requests.
            min_delay_between_retries: Minimum delay between retries.
            statistics: Statistics tracker for API calls. Created automatically if not provided.
        """
        super().__init__(
            token=token,
            timeout=timeout,
            max_retries=max_retries,
            min_delay_between_retries=min_delay_between_retries,
            statistics=statistics,
        )

        self._impit_async_client = impit.AsyncClient(
            headers=self._headers,
            follow_redirects=True,
            timeout=to_seconds(self._timeout),
        )

    async def call(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        data: Any = None,
        json: JsonSerializable | None = None,
        stream: bool | None = None,
        timeout: timedelta | None = None,
    ) -> impit.Response:
        """Make an HTTP request with automatic retry and exponential backoff.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            url: Full URL to make the request to.
            headers: Additional headers to include.
            params: Query parameters to append to the URL.
            data: Raw request body data. Cannot be used together with json.
            json: JSON-serializable data for the request body. Cannot be used together with data.
            stream: Whether to stream the response body.
            timeout: Timeout override for this request.

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
        content: Any,
        stream: bool | None,
        timeout: timedelta | None,
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
            timeout: Timeout override for this request.

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
                timeout=self._calculate_timeout(attempt, timeout),
                stream=stream or False,
            )

            if response.status_code < HTTPStatus.MULTIPLE_CHOICES:
                logger.debug('Request successful', extra={'status_code': response.status_code})
                return response

            if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                self._statistics.add_rate_limit_error(attempt)

        except Exception as exc:
            logger.debug('Request threw exception', exc_info=exc)
            if not self._is_retryable_error(exc):
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

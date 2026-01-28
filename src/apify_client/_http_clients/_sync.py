from __future__ import annotations

import logging
import random
import time
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, TypeVar

from apify_client._http_clients._base import BaseHttpClient
from apify_client._logging import log_context, logger_name
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from collections.abc import Callable

    import impit

    from apify_client._consts import JsonSerializable

T = TypeVar('T')

logger = logging.getLogger(logger_name)


class HttpClient(BaseHttpClient):
    def call(
        self,
        *,
        method: str,
        url: str,
        headers: dict | None = None,
        params: dict | None = None,
        data: Any = None,
        json: JsonSerializable | None = None,
        stream: bool | None = None,
        timeout_secs: int | None = None,
    ) -> impit.Response:
        log_context.method.set(method)
        log_context.url.set(url)

        self._statistics.calls += 1

        headers, params, content = self._prepare_request_call(headers, params, data, json)

        impit_client = self.impit_client

        def _make_request(stop_retrying: Callable, attempt: int) -> impit.Response:
            log_context.attempt.set(attempt)
            logger.debug('Sending request')

            self._statistics.requests += 1

            try:
                # Increase timeout with each attempt. Max timeout is bounded by the client timeout.
                timeout = min(
                    self._config.timeout_secs, (timeout_secs or self._config.timeout_secs) * 2 ** (attempt - 1)
                )

                url_with_params = self._build_url_with_params(url, params)

                response = impit_client.request(
                    method=method,
                    url=url_with_params,
                    headers=headers,
                    content=content,
                    timeout=timeout,
                    stream=stream or False,
                )

                # If response status is < 300, the request was successful, and we can return the result
                if response.status_code < 300:  # noqa: PLR2004
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

            # We want to retry only requests which are server errors (status >= 500) and could resolve on their own,
            # and also retry rate limited requests that throw 429 Too Many Requests errors
            logger.debug('Request unsuccessful', extra={'status_code': response.status_code})
            if response.status_code < 500 and response.status_code != HTTPStatus.TOO_MANY_REQUESTS:  # noqa: PLR2004
                logger.debug('Status code is not retryable', extra={'status_code': response.status_code})
                stop_retrying()

            # Read the response in case it is a stream, so we can raise the error properly
            response.read()
            raise ApifyApiError(response, attempt, method=method)

        return self._retry_with_exp_backoff(
            _make_request,
            max_retries=self._config.max_retries,
            backoff_base_millis=self._config.min_delay_between_retries_millis,
        )

    @staticmethod
    def _retry_with_exp_backoff(
        func: Callable[[Callable[[], None], int], T],
        *,
        max_retries: int = 8,
        backoff_base_millis: int = 500,
        backoff_factor: float = 2,
        random_factor: float = 1,
    ) -> T:
        """Retry a function with exponential backoff.

        Args:
            func: Function to retry. Receives a stop_retrying callback and attempt number.
            max_retries: Maximum number of retry attempts.
            backoff_base_millis: Base backoff delay in milliseconds.
            backoff_factor: Exponential backoff multiplier (1-10).
            random_factor: Random jitter factor (0-1).

        Returns:
            The return value of the function.
        """
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
            backoff_base_secs = backoff_base_millis / 1000
            backoff_exp_factor = backoff_factor ** (attempt - 1)

            sleep_time_secs = random_sleep_factor * backoff_base_secs * backoff_exp_factor
            time.sleep(sleep_time_secs)

        return func(stop_retrying, max_retries + 1)

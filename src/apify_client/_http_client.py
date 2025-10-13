from __future__ import annotations

import gzip
import json as jsonlib
import logging
import os
import sys
from datetime import datetime, timezone
from http import HTTPStatus
from importlib import metadata
from typing import TYPE_CHECKING, Any
from urllib.parse import urlencode

import impit

from apify_client._logging import log_context, logger_name
from apify_client._statistics import Statistics
from apify_client._utils import is_retryable_error, retry_with_exp_backoff, retry_with_exp_backoff_async
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from collections.abc import Callable

    from apify_client._types import JSONSerializable

DEFAULT_BACKOFF_EXPONENTIAL_FACTOR = 2
DEFAULT_BACKOFF_RANDOM_FACTOR = 1

logger = logging.getLogger(logger_name)


class _BaseHTTPClient:
    def __init__(
        self,
        *,
        token: str | None = None,
        max_retries: int = 8,
        min_delay_between_retries_millis: int = 500,
        timeout_secs: int = 360,
        stats: Statistics | None = None,
    ) -> None:
        self.max_retries = max_retries
        self.min_delay_between_retries_millis = min_delay_between_retries_millis
        self.timeout_secs = timeout_secs

        headers = {'Accept': 'application/json, */*'}

        workflow_key = os.getenv('APIFY_WORKFLOW_KEY')
        if workflow_key is not None:
            headers['X-Apify-Workflow-Key'] = workflow_key

        is_at_home = 'APIFY_IS_AT_HOME' in os.environ
        python_version = '.'.join([str(x) for x in sys.version_info[:3]])
        client_version = metadata.version('apify-client')

        user_agent = f'ApifyClient/{client_version} ({sys.platform}; Python/{python_version}); isAtHome/{is_at_home}'
        headers['User-Agent'] = user_agent

        if token is not None:
            headers['Authorization'] = f'Bearer {token}'

        self.impit_client = impit.Client(headers=headers, follow_redirects=True, timeout=timeout_secs)
        self.impit_async_client = impit.AsyncClient(headers=headers, follow_redirects=True, timeout=timeout_secs)

        self.stats = stats or Statistics()

    @staticmethod
    def _parse_params(params: dict | None) -> dict | None:
        if params is None:
            return None

        parsed_params: dict = {}
        for key, value in params.items():
            # Our API needs boolean parameters passed as 0 or 1
            if isinstance(value, bool):
                parsed_params[key] = int(value)
            # Our API needs lists passed as comma-separated strings
            elif isinstance(value, list):
                parsed_params[key] = ','.join(value)
            elif isinstance(value, datetime):
                utc_aware_dt = value.astimezone(timezone.utc)

                iso_str = utc_aware_dt.isoformat(timespec='milliseconds')

                # Convert to ISO 8601 string in Zulu format
                zulu_date_str = iso_str.replace('+00:00', 'Z')

                parsed_params[key] = zulu_date_str
            elif value is not None:
                parsed_params[key] = value

        return parsed_params

    def _prepare_request_call(
        self,
        headers: dict | None = None,
        params: dict | None = None,
        data: Any = None,
        json: JSONSerializable | None = None,
    ) -> tuple[dict, dict | None, Any]:
        if json and data:
            raise ValueError('Cannot pass both "json" and "data" parameters at the same time!')

        if not headers:
            headers = {}

        # dump JSON data to string, so they can be gzipped
        if json:
            data = jsonlib.dumps(json, ensure_ascii=False, allow_nan=False, default=str).encode('utf-8')
            headers['Content-Type'] = 'application/json'

        if isinstance(data, (str, bytes, bytearray)):
            if isinstance(data, str):
                data = data.encode('utf-8')
            data = gzip.compress(data)
            headers['Content-Encoding'] = 'gzip'

        return (
            headers,
            self._parse_params(params),
            data,
        )

    def _build_url_with_params(self, url: str, params: dict | None = None) -> str:
        if not params:
            return url

        param_pairs: list[tuple[str, str]] = []
        for key, value in params.items():
            if isinstance(value, list):
                param_pairs.extend((key, str(v)) for v in value)
            else:
                param_pairs.append((key, str(value)))

        query_string = urlencode(param_pairs)

        return f'{url}?{query_string}'


class HTTPClient(_BaseHTTPClient):
    def call(
        self,
        *,
        method: str,
        url: str,
        headers: dict | None = None,
        params: dict | None = None,
        data: Any = None,
        json: JSONSerializable | None = None,
        stream: bool | None = None,
        timeout_secs: int | None = None,
    ) -> impit.Response:
        log_context.method.set(method)
        log_context.url.set(url)

        self.stats.calls += 1

        headers, params, content = self._prepare_request_call(headers, params, data, json)

        impit_client = self.impit_client

        def _make_request(stop_retrying: Callable, attempt: int) -> impit.Response:
            log_context.attempt.set(attempt)
            logger.debug('Sending request')

            self.stats.requests += 1

            try:
                # Increase timeout with each attempt. Max timeout is bounded by the client timeout.
                timeout = min(self.timeout_secs, (timeout_secs or self.timeout_secs) * 2 ** (attempt - 1))

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
                    self.stats.add_rate_limit_error(attempt)

            except Exception as e:
                logger.debug('Request threw exception', exc_info=e)
                if not is_retryable_error(e):
                    logger.debug('Exception is not retryable', exc_info=e)
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

        return retry_with_exp_backoff(
            _make_request,
            max_retries=self.max_retries,
            backoff_base_millis=self.min_delay_between_retries_millis,
            backoff_factor=DEFAULT_BACKOFF_EXPONENTIAL_FACTOR,
            random_factor=DEFAULT_BACKOFF_RANDOM_FACTOR,
        )


class HTTPClientAsync(_BaseHTTPClient):
    async def call(
        self,
        *,
        method: str,
        url: str,
        headers: dict | None = None,
        params: dict | None = None,
        data: Any = None,
        json: JSONSerializable | None = None,
        stream: bool | None = None,
        timeout_secs: int | None = None,
    ) -> impit.Response:
        log_context.method.set(method)
        log_context.url.set(url)

        self.stats.calls += 1

        headers, params, content = self._prepare_request_call(headers, params, data, json)

        impit_async_client = self.impit_async_client

        async def _make_request(stop_retrying: Callable, attempt: int) -> impit.Response:
            log_context.attempt.set(attempt)
            logger.debug('Sending request')
            try:
                # Increase timeout with each attempt. Max timeout is bounded by the client timeout.
                timeout = min(self.timeout_secs, (timeout_secs or self.timeout_secs) * 2 ** (attempt - 1))

                url_with_params = self._build_url_with_params(url, params)

                response = await impit_async_client.request(
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
                    self.stats.add_rate_limit_error(attempt)

            except Exception as e:
                logger.debug('Request threw exception', exc_info=e)
                if not is_retryable_error(e):
                    logger.debug('Exception is not retryable', exc_info=e)
                    stop_retrying()
                raise

            # We want to retry only requests which are server errors (status >= 500) and could resolve on their own,
            # and also retry rate limited requests that throw 429 Too Many Requests errors
            logger.debug('Request unsuccessful', extra={'status_code': response.status_code})
            if response.status_code < 500 and response.status_code != HTTPStatus.TOO_MANY_REQUESTS:  # noqa: PLR2004
                logger.debug('Status code is not retryable', extra={'status_code': response.status_code})
                stop_retrying()

            # Read the response in case it is a stream, so we can raise the error properly
            await response.aread()
            raise ApifyApiError(response, attempt, method=method)

        return await retry_with_exp_backoff_async(
            _make_request,
            max_retries=self.max_retries,
            backoff_base_millis=self.min_delay_between_retries_millis,
            backoff_factor=DEFAULT_BACKOFF_EXPONENTIAL_FACTOR,
            random_factor=DEFAULT_BACKOFF_RANDOM_FACTOR,
        )

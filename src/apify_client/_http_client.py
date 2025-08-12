from __future__ import annotations

import gzip
import json as jsonlib
import logging
import os
import sys
from http import HTTPStatus
from importlib import metadata
from typing import TYPE_CHECKING, Any

import httpx
from apify_shared.utils import ignore_docs

from apify_client._errors import ApifyApiError, is_retryable_error
from apify_client._logging import log_context, logger_name
from apify_client._statistics import Statistics
from apify_client._utils import retry_with_exp_backoff, retry_with_exp_backoff_async

if TYPE_CHECKING:
    from collections.abc import Callable

    from apify_shared.types import JSONSerializable

DEFAULT_BACKOFF_EXPONENTIAL_FACTOR = 2
DEFAULT_BACKOFF_RANDOM_FACTOR = 1

logger = logging.getLogger(logger_name)


class _BaseHTTPClient:
    @ignore_docs
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

        self.httpx_client = httpx.Client(headers=headers, follow_redirects=True, timeout=timeout_secs)
        self.httpx_async_client = httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=timeout_secs)

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
    ) -> httpx.Response:
        log_context.method.set(method)
        log_context.url.set(url)

        self.stats.calls += 1

        headers, params, content = self._prepare_request_call(headers, params, data, json)

        httpx_client = self.httpx_client

        def _make_request(stop_retrying: Callable, attempt: int) -> httpx.Response:
            log_context.attempt.set(attempt)
            logger.debug('Sending request')

            self.stats.requests += 1

            try:
                request = httpx_client.build_request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    content=content,
                )

                # Increase timeout with each attempt. Max timeout is bounded by the client timeout.
                timeout = min(self.timeout_secs, (timeout_secs or self.timeout_secs) * 2 ** (attempt - 1))
                request.extensions['timeout'] = {
                    'connect': timeout,
                    'pool': timeout,
                    'read': timeout,
                    'write': timeout,
                }

                response = httpx_client.send(
                    request=request,
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
            raise ApifyApiError(response, attempt)

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
    ) -> httpx.Response:
        log_context.method.set(method)
        log_context.url.set(url)

        self.stats.calls += 1

        headers, params, content = self._prepare_request_call(headers, params, data, json)

        httpx_async_client = self.httpx_async_client

        async def _make_request(stop_retrying: Callable, attempt: int) -> httpx.Response:
            log_context.attempt.set(attempt)
            logger.debug('Sending request')
            try:
                request = httpx_async_client.build_request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    content=content,
                )

                # Increase timeout with each attempt. Max timeout is bounded by the client timeout.
                timeout = min(self.timeout_secs, (timeout_secs or self.timeout_secs) * 2 ** (attempt - 1))
                request.extensions['timeout'] = {
                    'connect': timeout,
                    'pool': timeout,
                    'read': timeout,
                    'write': timeout,
                }

                response = await httpx_async_client.send(
                    request=request,
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
            raise ApifyApiError(response, attempt)

        return await retry_with_exp_backoff_async(
            _make_request,
            max_retries=self.max_retries,
            backoff_base_millis=self.min_delay_between_retries_millis,
            backoff_factor=DEFAULT_BACKOFF_EXPONENTIAL_FACTOR,
            random_factor=DEFAULT_BACKOFF_RANDOM_FACTOR,
        )

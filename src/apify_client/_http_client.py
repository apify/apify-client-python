import gzip
import json as jsonlib
import logging
import os
import sys
from http import HTTPStatus
from importlib import metadata
from typing import Any, Callable, Dict, Optional, Tuple

import httpx

from ._errors import ApifyApiError, InvalidResponseBodyError, _is_retryable_error
from ._logging import logger_name
from ._types import JSONSerializable
from ._utils import (
    _is_content_type_json,
    _is_content_type_text,
    _is_content_type_xml,
    _retry_with_exp_backoff,
    _retry_with_exp_backoff_async,
    ignore_docs,
)

DEFAULT_BACKOFF_EXPONENTIAL_FACTOR = 2
DEFAULT_BACKOFF_RANDOM_FACTOR = 1

logger = logging.getLogger(logger_name)


class _BaseHTTPClient:
    @ignore_docs
    def __init__(
        self,
        *,
        token: Optional[str] = None,
        max_retries: int = 8,
        min_delay_between_retries_millis: int = 500,
        timeout_secs: int = 360,
    ) -> None:
        self.max_retries = max_retries
        self.min_delay_between_retries_millis = min_delay_between_retries_millis
        self.timeout_secs = timeout_secs

        headers = {'Accept': 'application/json, */*'}

        workflow_key = os.getenv('APIFY_WORKFLOW_KEY')
        if workflow_key is not None:
            headers['X-Apify-Workflow-Key'] = workflow_key

        is_at_home = ('APIFY_IS_AT_HOME' in os.environ)
        python_version = '.'.join([str(x) for x in sys.version_info[:3]])
        client_version = metadata.version('apify-client')

        user_agent = f'ApifyClient/{client_version} ({sys.platform}; Python/{python_version}); isAtHome/{is_at_home}'
        headers['User-Agent'] = user_agent

        if token is not None:
            headers['Authorization'] = f'Bearer {token}'

        self.httpx_client = httpx.Client(headers=headers, follow_redirects=True, timeout=timeout_secs)
        self.httpx_async_client = httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=timeout_secs)

    @staticmethod
    def _maybe_parse_response(response: httpx.Response) -> Any:
        if response.status_code == HTTPStatus.NO_CONTENT:
            return None

        content_type = ''
        if 'content-type' in response.headers:
            content_type = response.headers['content-type'].split(';')[0].strip()

        try:
            if _is_content_type_json(content_type):
                return response.json()
            elif _is_content_type_xml(content_type) or _is_content_type_text(content_type):
                return response.text
            else:
                return response.content
        except ValueError as err:
            raise InvalidResponseBodyError(response) from err

    @staticmethod
    def _parse_params(params: Optional[Dict]) -> Optional[Dict]:
        if params is None:
            return None

        parsed_params = {}
        for key, value in params.items():
            # Our API needs to have boolean parameters passed as 0 or 1, therefore we have to replace them
            if isinstance(value, bool):
                parsed_params[key] = int(value)
            elif value is not None:
                parsed_params[key] = value

        return parsed_params

    def _prepare_request_call(
        self,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        data: Optional[Any] = None,
        json: Optional[JSONSerializable] = None,
    ) -> Tuple[Dict, Optional[Dict], Any]:
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


class _HTTPClient(_BaseHTTPClient):
    def call(
        self,
        *,
        method: str,
        url: str,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        data: Optional[Any] = None,
        json: Optional[JSONSerializable] = None,
        stream: Optional[bool] = None,
        parse_response: Optional[bool] = True,
    ) -> httpx.Response:
        if stream and parse_response:
            raise ValueError('Cannot stream response and parse it at the same time!')

        headers, params, content = self._prepare_request_call(headers, params, data, json)

        httpx_client = self.httpx_client

        def _make_request(stop_retrying: Callable, attempt: int) -> httpx.Response:
            logger.debug(f'Sending request to {url}', extra={'attempt': attempt})
            try:
                request = httpx_client.build_request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    content=content,
                )
                response = httpx_client.send(
                    request=request,
                    stream=stream or False,
                )

                # If response status is < 300, the request was successful, and we can return the result
                if response.status_code < 300:
                    logger.debug(f'Request to {url} successful', extra={'attempt': attempt, 'status_code': response.status_code})
                    if not stream:
                        if parse_response:
                            _maybe_parsed_body = self._maybe_parse_response(response)
                        else:
                            _maybe_parsed_body = response.content
                        setattr(response, '_maybe_parsed_body', _maybe_parsed_body)  # noqa: B010

                    return response

            except Exception as e:
                logger.debug(f'Request to {url} threw exception', exc_info=e, extra={'attempt': attempt})
                if not _is_retryable_error(e):
                    logger.debug('Exception is not retryable', exc_info=e, extra={'attempt': attempt})
                    stop_retrying()
                raise e

            # We want to retry only requests which are server errors (status >= 500) and could resolve on their own,
            # and also retry rate limited requests that throw 429 Too Many Requests errors
            logger.debug(f'Request to {url} unsuccessful', extra={'attempt': attempt, 'status_code': response.status_code})
            if response.status_code < 500 and response.status_code != HTTPStatus.TOO_MANY_REQUESTS:
                logger.debug('Status code is not retryable', extra={'attempt': attempt, 'status_code': response.status_code})
                stop_retrying()
            raise ApifyApiError(response, attempt)

        return _retry_with_exp_backoff(
            _make_request,
            max_retries=self.max_retries,
            backoff_base_millis=self.min_delay_between_retries_millis,
            backoff_factor=DEFAULT_BACKOFF_EXPONENTIAL_FACTOR,
            random_factor=DEFAULT_BACKOFF_RANDOM_FACTOR,
        )


class _HTTPClientAsync(_BaseHTTPClient):
    async def call(
        self,
        *,
        method: str,
        url: str,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        data: Optional[Any] = None,
        json: Optional[JSONSerializable] = None,
        stream: Optional[bool] = None,
        parse_response: Optional[bool] = True,
    ) -> httpx.Response:
        if stream and parse_response:
            raise ValueError('Cannot stream response and parse it at the same time!')

        headers, params, content = self._prepare_request_call(headers, params, data, json)

        httpx_async_client = self.httpx_async_client

        async def _make_request(stop_retrying: Callable, attempt: int) -> httpx.Response:
            logger.debug('Sending request')
            try:
                request = httpx_async_client.build_request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    content=content,
                )
                response = await httpx_async_client.send(
                    request=request,
                    stream=stream or False,
                )

                # If response status is < 300, the request was successful, and we can return the result
                if response.status_code < 300:
                    logger.debug('Request successful', extra={'status_code': response.status_code})
                    if not stream:
                        if parse_response:
                            _maybe_parsed_body = self._maybe_parse_response(response)
                        else:
                            _maybe_parsed_body = response.content
                        setattr(response, '_maybe_parsed_body', _maybe_parsed_body)  # noqa: B010

                    return response

            except Exception as e:
                logger.debug('Request threw exception', exc_info=e)
                if not _is_retryable_error(e):
                    logger.debug('Exception is not retryable', exc_info=e)
                    stop_retrying()
                raise e

            # We want to retry only requests which are server errors (status >= 500) and could resolve on their own,
            # and also retry rate limited requests that throw 429 Too Many Requests errors
            logger.debug('Request unsuccessful', extra={'status_code': response.status_code})
            if response.status_code < 500 and response.status_code != HTTPStatus.TOO_MANY_REQUESTS:
                logger.debug('Status code is not retryable', extra={'status_code': response.status_code})
                stop_retrying()
            raise ApifyApiError(response, attempt)

        return await _retry_with_exp_backoff_async(
            _make_request,
            max_retries=self.max_retries,
            backoff_base_millis=self.min_delay_between_retries_millis,
            backoff_factor=DEFAULT_BACKOFF_EXPONENTIAL_FACTOR,
            random_factor=DEFAULT_BACKOFF_RANDOM_FACTOR,
        )

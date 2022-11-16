import gzip
import json as jsonlib
import os
import sys
from http import HTTPStatus
from typing import Any, Callable, Dict, Optional

import httpx

from ._errors import ApifyApiError, InvalidResponseBodyError, _is_retryable_error
from ._types import JSONSerializable
from ._utils import _is_content_type_json, _is_content_type_text, _is_content_type_xml, _retry_with_exp_backoff
from ._version import __version__

DEFAULT_BACKOFF_EXPONENTIAL_FACTOR = 2
DEFAULT_BACKOFF_RANDOM_FACTOR = 1


class _HTTPClient:
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

        is_at_home = ('APIFY_IS_AT_HOME' in os.environ)
        python_version = '.'.join([str(x) for x in sys.version_info[:3]])

        user_agent = f'ApifyClient/{__version__} ({sys.platform}; Python/{python_version}); isAtHome/{is_at_home}'
        headers['User-Agent'] = user_agent

        if token is not None:
            headers['Authorization'] = f'Bearer {token}'

        self.httpx_client = httpx.Client(headers=headers, follow_redirects=True, timeout=timeout_secs)

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

        if json and data:
            raise ValueError('Cannot pass both "json" and "data" parameters at the same time!')

        request_params = self._parse_params(params)
        httpx_client = self.httpx_client

        if not headers:
            headers = {}

        # dump JSON data to string, so they can be gzipped
        if json:
            data = jsonlib.dumps(json, ensure_ascii=False, default=str).encode('utf-8')
            headers['Content-Type'] = 'application/json'

        if isinstance(data, (str, bytes, bytearray)):
            if isinstance(data, str):
                data = data.encode('utf-8')
            data = gzip.compress(data)
            headers['Content-Encoding'] = 'gzip'

        # httpx uses `content` instead of `data` for binary content, let's rename it here to be clear about it
        content = data

        def _make_request(stop_retrying: Callable, attempt: int) -> httpx.Response:
            try:
                request = httpx_client.build_request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=request_params,
                    content=content,
                )
                response = httpx_client.send(
                    request=request,
                    stream=stream or False,
                )

                if response.status_code < 300:
                    if not stream:
                        if parse_response:
                            _maybe_parsed_body = self._maybe_parse_response(response)
                        else:
                            _maybe_parsed_body = response.content
                        setattr(response, '_maybe_parsed_body', _maybe_parsed_body)  # noqa: B010

                    return response

            except Exception as e:
                if not _is_retryable_error(e):
                    stop_retrying()
                raise e

            if response.status_code < 500 and response.status_code != HTTPStatus.TOO_MANY_REQUESTS:
                stop_retrying()
            raise ApifyApiError(response, attempt)

        return _retry_with_exp_backoff(
            _make_request,
            max_retries=self.max_retries,
            backoff_base_millis=self.min_delay_between_retries_millis,
            backoff_factor=DEFAULT_BACKOFF_EXPONENTIAL_FACTOR,
            random_factor=DEFAULT_BACKOFF_RANDOM_FACTOR,
        )

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

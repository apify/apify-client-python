import os
import sys
from http import HTTPStatus
from typing import Any, Callable, Dict, Optional

import requests
from requests.exceptions import ConnectionError, Timeout

from ._errors import ApifyApiError, InvalidResponseBodyError
from ._types import JSONSerializable
from ._utils import _is_content_type_json, _is_content_type_text, _is_content_type_xml, _retry_with_exp_backoff

DEFAULT_BACKOFF_EXPONENTIAL_FACTOR = 2
DEFAULT_BACKOFF_RANDOM_FACTOR = 1


class _HTTPClient:
    def __init__(self, max_retries: int = 8, min_delay_between_retries_millis: int = 500) -> None:
        self.max_retries = max_retries
        self.min_delay_between_retries_millis = min_delay_between_retries_millis
        self.requests_session = requests.Session()

        self.requests_session.headers.update({'Accept': 'application/json, */*'})

        # TODO add client version
        is_at_home = ('APIFY_IS_AT_HOME' in os.environ)
        python_version = '.'.join([str(x) for x in sys.version_info[:3]])

        user_agent = f'ApifyClient ({sys.platform}; Python/{python_version}); isAtHome/{is_at_home}'
        self.requests_session.headers.update({'User-Agent': user_agent})

    def call(
        self,
        *,
        method: str,
        url: str,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        data: Optional[str] = None,
        json: Optional[JSONSerializable] = None,
        stream: Optional[bool] = None,
        parse_response: Optional[bool] = True,
    ) -> requests.models.Response:
        request_params = self._parse_params(params)
        requests_session = self.requests_session

        def _make_request(bail: Callable, attempt: int) -> requests.models.Response:  # type: ignore[return]
            try:
                response = requests_session.request(
                    method,
                    url,
                    headers=headers,
                    params=request_params,
                    data=data,
                    json=json,
                    stream=stream,
                )
                if response.status_code < 300:
                    if parse_response:
                        _maybe_parsed_body = self._maybe_parse_response(response)
                    elif stream:
                        response.raw.decode_content = True
                        _maybe_parsed_body = response.raw
                    else:
                        _maybe_parsed_body = response.content
                    setattr(response, '_maybe_parsed_body', _maybe_parsed_body)
                    return response

            except (ConnectionError, Timeout, InvalidResponseBodyError) as e:
                raise e
            except Exception as e:
                bail(e)

            api_error = ApifyApiError(response, attempt)
            if response.status_code == HTTPStatus.TOO_MANY_REQUESTS or response.status_code >= 500:
                raise api_error
            else:
                bail(api_error)

        return _retry_with_exp_backoff(
            _make_request,
            max_retries=self.max_retries,
            backoff_base_millis=self.min_delay_between_retries_millis,
            backoff_factor=DEFAULT_BACKOFF_EXPONENTIAL_FACTOR,
            random_factor=DEFAULT_BACKOFF_RANDOM_FACTOR,
        )

    @staticmethod
    def _maybe_parse_response(response: requests.models.Response) -> Any:
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
            else:
                parsed_params[key] = value

        return parsed_params

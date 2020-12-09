import re
from typing import Any, Callable, Dict, List, Optional, Union

import requests
from requests.exceptions import ConnectionError, Timeout

from ._errors import ApifyApiError, InvalidResponseBodyError
from ._utils import _retry_with_exp_backoff

NO_CONTENT_STATUS_CODE = 204
RATE_LIMIT_EXCEEDED_STATUS_CODE = 429


class _HTTPClient:
    def __init__(self, max_retries: int = 8, min_delay_between_retries_millis: int = 500) -> None:
        self.max_retries = max_retries
        self.min_delay_between_retries_millis = min_delay_between_retries_millis
        self.requests_session = requests.Session()

    def call(
        self,
        *,
        method: str,
        url: str,
        headers: Dict = None,
        params: Dict = None,
        data: str = None,
        json: Union[str, Dict, List[str], List[Dict]] = None,
        stream: bool = None,
        parse_response: bool = True,
    ) -> requests.models.Response:
        request_params = self._parse_params(params)
        requests_session = self.requests_session

        def _make_request(bail: Callable, attempt: int) -> requests.models.Response:  # type: ignore[return]
            nonlocal requests_session, method, url, headers, request_params, data, json, stream, parse_response
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
            if response.status_code == RATE_LIMIT_EXCEEDED_STATUS_CODE or response.status_code >= 500:
                raise api_error
            else:
                bail(api_error)

        return _retry_with_exp_backoff(
            _make_request,
            max_retries=self.max_retries,
            backoff_base_millis=self.min_delay_between_retries_millis,
            backoff_factor=2,
            random_factor=1,
        )

    @staticmethod
    def _maybe_parse_response(response: requests.models.Response) -> Any:
        if response.status_code == NO_CONTENT_STATUS_CODE:
            return None

        content_type = ''
        if 'content-type' in response.headers:
            content_type = response.headers['content-type'].split(';')[0].strip()

        try:
            if re.search(r'^application/json', content_type, flags=re.IGNORECASE):
                return response.json()
            elif re.search(r'^application/.*xml$', content_type, flags=re.IGNORECASE) or re.search(r'^text/', content_type, flags=re.IGNORECASE):
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
            if isinstance(value, bool):
                parsed_params[key] = int(value)
            else:
                parsed_params[key] = value

        return parsed_params

from typing import Callable, Dict, List, Optional, Union

import requests
from requests.exceptions import ConnectionError, Timeout

from ._errors import ApifyApiError
from ._utils import _retry_with_exp_backoff

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
        json: Union[Dict, List[Union[str, Dict]]] = None,
        stream: bool = None,
    ) -> requests.models.Response:
        request_params = self._parse_params(params)
        requests_session = self.requests_session

        def _make_request(bail: Callable, attempt: int) -> requests.models.Response:  # type: ignore[return]
            nonlocal requests_session, method, url, headers, request_params, data, json, stream
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
                    return self._parse_response(response)
            except (ConnectionError, Timeout) as e:
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
    def _parse_response(response: requests.models.Response) -> requests.models.Response:
        # TODO parse based on response type
        return response

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

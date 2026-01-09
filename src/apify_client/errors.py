from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import impit


class ApifyClientError(Exception):
    """Base class for errors specific to the Apify API Client."""


class ApifyApiError(ApifyClientError):
    """Error from Apify API responses (rate limits, validation errors, internal errors).

    Thrown when HTTP request succeeds but API returns an error response. Rate limit and internal errors are
    retried automatically, while validation errors are thrown immediately for user correction.
    """

    def __init__(self, response: impit.Response, attempt: int, method: str = 'GET') -> None:
        """Initialize an API error from a failed response.

        Args:
            response: The failed API response.
            attempt: The attempt number when the request failed.
            method: The HTTP method used.
        """
        self.message: str | None = None
        self.type: str | None = None
        self.data = dict[str, str]()

        self.message = f'Unexpected error: {response.text}'
        try:
            response_data = response.json()
            if isinstance(response_data, dict) and 'error' in response_data:
                self.message = response_data['error']['message']
                self.type = response_data['error']['type']
                if 'data' in response_data['error']:
                    self.data = response_data['error']['data']
        except ValueError:
            pass

        super().__init__(self.message)

        self.name = 'ApifyApiError'
        self.status_code = response.status_code
        self.attempt = attempt
        self.http_method = method


class InvalidResponseBodyError(ApifyClientError):
    """Error when response body cannot be parsed (e.g., partial JSON).

    Commonly occurs when only partial JSON is received. Usually resolved by retrying the request.
    """

    def __init__(self, response: impit.Response) -> None:
        """Initialize a new instance.

        Args:
            response: The response that failed to parse.
        """
        super().__init__('Response body could not be parsed')

        self.name = 'InvalidResponseBodyError'
        self.code = 'invalid-response-body'
        self.response = response

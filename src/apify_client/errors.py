from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import impit


class ApifyClientError(Exception):
    """Base class for errors specific to the Apify API Client."""


class ApifyApiError(ApifyClientError):
    """Error specific to requests to the Apify API.

    An `ApifyApiError` is thrown for successful HTTP requests that reach the API, but the API responds with
    an error response. Typically, those are rate limit errors and internal errors, which are automatically retried,
    or validation errors, which are thrown immediately, because a correction by the user is needed.
    """

    def __init__(self, response: impit.Response, attempt: int, method: str = 'GET') -> None:
        """Initialize a new instance.

        Args:
            response: The response to the failed API call.
            attempt: Which attempt was the request that failed.
            method: The HTTP method used for the request.
        """
        self.message: str | None = None
        self.type: str | None = None
        self.data = dict[str, str]()

        self.message = f'Unexpected error: {response.text}'
        try:
            response_data = response.json()
            if 'error' in response_data:
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

        # TODO: self.client_method   # noqa: TD003
        # TODO: self.original_stack  # noqa: TD003
        # TODO: self.path  # noqa: TD003
        # TODO: self.stack  # noqa: TD003


class InvalidResponseBodyError(ApifyClientError):
    """Error caused by the response body failing to be parsed.

    This error exists for the quite common situation, where only a partial JSON response is received and an attempt
    to parse the JSON throws an error. In most cases this can be resolved by retrying the request. We do that by
    identifying this error in the HTTPClient.
    """

    def __init__(self, response: impit.Response) -> None:
        """Initialize a new instance.

        Args:
            response: The response which failed to be parsed.
        """
        super().__init__('Response body could not be parsed')

        self.name = 'InvalidResponseBodyError'
        self.code = 'invalid-response-body'
        self.response = response

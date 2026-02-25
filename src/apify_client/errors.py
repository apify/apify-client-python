from __future__ import annotations

from typing import TYPE_CHECKING

from apify_client._docs import docs_group

if TYPE_CHECKING:
    import impit


@docs_group('Errors')
class ApifyClientError(Exception):
    """Base class for all Apify API client errors.

    All custom exceptions defined by this package inherit from this class, making it convenient
    to catch any client-related error with a single except clause.
    """


@docs_group('Errors')
class ApifyApiError(ApifyClientError):
    """Error raised when the Apify API returns an error response.

    This error is raised when an HTTP request to the Apify API succeeds at the transport level
    but the server returns an error status code. Rate limit (HTTP 429) and server errors (HTTP 5xx)
    are retried automatically before this error is raised, while client errors (HTTP 4xx) are raised
    immediately.

    Attributes:
        message: The error message from the API response.
        type: The error type identifier from the API response (e.g. `record-not-found`).
        status_code: The HTTP status code of the error response.
        attempt: The attempt number when the error was raised.
        http_method: The HTTP method of the failed request.
        data: Additional error data from the API response.
    """

    def __init__(self, response: impit.Response, attempt: int, method: str = 'GET') -> None:
        """Initialize the API error from a failed response.

        Args:
            response: The failed HTTP response from the Apify API.
            attempt: The attempt number when the request failed (1-indexed).
            method: The HTTP method of the failed request.
        """
        self.message: str | None = None
        self.type: str | None = None
        self.data = dict[str, str]()
        self.message = f'Unexpected error: {response.text}'

        try:
            response_data = response.json()

            if (
                isinstance(response_data, dict)
                and 'error' in response_data
                and isinstance(response_data['error'], dict)
            ):
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


@docs_group('Errors')
class InvalidResponseBodyError(ApifyClientError):
    """Error raised when a response body cannot be parsed.

    This typically occurs when the API returns a partial or malformed JSON response, for example
    due to a network interruption. The client retries such requests automatically, so this error
    is only raised after all retry attempts have been exhausted.
    """

    def __init__(self, response: impit.Response) -> None:
        """Initialize the error from an unparsable response.

        Args:
            response: The HTTP response whose body could not be parsed.
        """
        super().__init__('Response body could not be parsed')

        self.name = 'InvalidResponseBodyError'
        self.code = 'invalid-response-body'
        self.response = response

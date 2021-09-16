from typing import Optional

import requests
from requests.exceptions import ChunkedEncodingError, ConnectionError, Timeout


class ApifyClientError(Exception):
    """Base class for errors specific to the Apify API Client."""

    pass


class ApifyApiError(ApifyClientError):
    """Error specific to requests to the Apify API.

    An `ApifyApiError` is thrown for successful HTTP requests that reach the API,
    but the API responds with an error response. Typically, those are rate limit
    errors and internal errors, which are automatically retried, or validation
    errors, which are thrown immediately, because a correction by the user is needed.
    """

    def __init__(self, response: requests.models.Response, attempt: int) -> None:
        """Create the ApifyApiError instance.

        Args:
            response: The response to the failed API call
            attempt: Which attempt was the request that failed
        """
        self.message: Optional[str] = None
        self.type: Optional[str] = None

        self.message = f'Unexpected error: {response.text}'
        try:
            response_data = response.json()
            if 'error' in response_data:
                self.message = response_data['error']['message']
                self.type = response_data['error']['type']
        except ValueError:
            pass

        super().__init__(self.message)

        self.name = 'ApifyApiError'
        self.status_code = response.status_code
        self.attempt = attempt
        self.http_method = response.request.method

        # TODO self.client_method
        # TODO self.original_stack
        # TODO self.path
        # TODO self.stack


class InvalidResponseBodyError(ApifyClientError):
    """Error caused by the response body failing to be parsed.

    This error exists for the quite common situation, where only a partial JSON response is received and
    an attempt to parse the JSON throws an error. In most cases this can be resolved by retrying the
    request. We do that by identifying this error in the _HTTPClient.
    """

    def __init__(self, response: requests.models.Response) -> None:
        """Create the InvalidResponseBodyError instance.

        Args:
            response: The response which failed to be parsed
        """
        super().__init__('Response body could not be parsed')

        self.name = 'InvalidResponseBodyError'
        self.code = 'invalid-response-body'
        self.response = response


def _is_retryable_error(e: Exception) -> bool:
    if isinstance(e, (InvalidResponseBodyError, ConnectionError, Timeout)):
        return True

    # This can happen if an API server pod restarts while handling a long-running request
    if isinstance(e, ChunkedEncodingError):
        if str(e).startswith('("Connection broken: InvalidChunkLength(got length b\'\', 0 bytes read)"'):
            return True

    return False

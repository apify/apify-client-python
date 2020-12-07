import requests


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
        """Creates the ApifyApiError instance.

        Args:
            response: The response to the failed API call
            attempt: Which retry was the request that failed
        """
        self.message = None
        self.type = None

        response_data = response.json()
        if 'error' in response_data:
            self.message = response_data['error']['message']
            self.type = response_data['error']['type']
        else:
            self.message = f'Unexpected error: {response.text}'

        super().__init__(self.message)

        self.name = 'ApifyApiError'
        self.status_code = response.status_code
        self.attempt = attempt
        self.http_method = response.request.method

        # TODO self.client_method
        # TODO self.original_stack
        # TODO self.path
        # TODO self.stack

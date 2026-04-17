from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group

if TYPE_CHECKING:
    from typing import Self

    from apify_client._http_clients import HttpResponse


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

    Instantiating `ApifyApiError` directly dispatches to a more specific subclass based on the
    `type` field of the API error response (e.g. a `record-not-found` response produces a
    `RecordNotFoundError`). Existing `except ApifyApiError` handlers continue to match because
    every generated subclass inherits from this class. If the response body cannot be parsed or
    the `type` is not recognized, an `ApifyApiError` is raised instead.

    Attributes:
        message: The error message from the API response.
        type: The error type identifier from the API response (e.g. `record-not-found`).
        status_code: The HTTP status code of the error response.
        attempt: The attempt number when the error was raised.
        http_method: The HTTP method of the failed request.
        data: Additional error data from the API response.
    """

    _apify_error_payload: dict[str, Any] | None

    def __new__(cls, response: HttpResponse, attempt: int, method: str = 'GET') -> Self:  # noqa: ARG004
        """Dispatch to the subclass matching the response's error `type`, if any."""
        payload = _extract_error_payload(response)
        target_cls: type[ApifyApiError] = cls
        if cls is ApifyApiError and payload is not None:
            error_type = payload.get('type')
            if isinstance(error_type, str):
                # avoid circular import with _generated_errors
                from apify_client._generated_errors import API_ERROR_CLASS_BY_TYPE  # noqa: PLC0415

                target_cls = API_ERROR_CLASS_BY_TYPE.get(error_type, cls)
        instance = super().__new__(target_cls)
        instance._apify_error_payload = payload
        return instance

    def __init__(self, response: HttpResponse, attempt: int, method: str = 'GET') -> None:
        """Initialize the API error from a failed response.

        Args:
            response: The failed HTTP response from the Apify API.
            attempt: The attempt number when the request failed (1-indexed).
            method: The HTTP method of the failed request.
        """
        # Prefer the payload stashed by __new__; fall back to re-parsing for direct subclass
        # instantiation (e.g. if a user constructs a subclass without going through the base class).
        payload = getattr(self, '_apify_error_payload', None)
        if payload is None:
            payload = _extract_error_payload(response)

        self.message: str | None = f'Unexpected error: {response.text}'
        self.type: str | None = None
        self.data = dict[str, str]()

        if payload is not None:
            self.message = payload['message']
            self.type = payload['type']
            if 'data' in payload:
                self.data = payload['data']

        super().__init__(self.message)

        self.name = 'ApifyApiError'
        self.status_code = response.status_code
        self.attempt = attempt
        self.http_method = method


def _extract_error_payload(response: HttpResponse) -> dict[str, Any] | None:
    """Return the `error` dict from the response body, or None if absent or unparsable."""
    try:
        data = response.json()
    except ValueError:
        return None
    if not isinstance(data, dict):
        return None
    error = data.get('error')
    return error if isinstance(error, dict) else None


@docs_group('Errors')
class InvalidResponseBodyError(ApifyClientError):
    """Error raised when a response body cannot be parsed.

    This typically occurs when the API returns a partial or malformed JSON response, for example
    due to a network interruption. The client retries such requests automatically, so this error
    is only raised after all retry attempts have been exhausted.
    """

    def __init__(self, response: HttpResponse) -> None:
        """Initialize the error from an unparsable response.

        Args:
            response: The HTTP response whose body could not be parsed.
        """
        super().__init__('Response body could not be parsed')

        self.name = 'InvalidResponseBodyError'
        self.code = 'invalid-response-body'
        self.response = response


from apify_client._generated_errors import *  # noqa: E402, F403

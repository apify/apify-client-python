from __future__ import annotations

from http import HTTPStatus
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
    HTTP status code of the response (e.g. a 404 response produces a `NotFoundError`). Existing
    `except ApifyApiError` handlers continue to match because every subclass inherits from this
    class. Statuses without a dedicated subclass fall back to `ApifyApiError` itself.

    The `type`, `message` and `data` fields from the API response body are exposed as attributes
    for inspection, but they are treated as non-authoritative metadata — dispatch is driven by the
    status code only, which is more stable than the per-endpoint `error.type` strings.

    Attributes:
        message: The error message from the API response.
        type: The error type identifier from the API response (e.g. `record-not-found`).
        status_code: The HTTP status code of the error response.
        attempt: The attempt number when the error was raised.
        http_method: The HTTP method of the failed request.
        data: Additional error data from the API response.
    """

    def __new__(cls, response: HttpResponse, attempt: int, method: str = 'GET') -> Self:  # noqa: ARG004
        """Dispatch to the subclass matching the response's HTTP status code, if any."""
        target_cls: type[ApifyApiError] = cls
        if cls is ApifyApiError:
            status = response.status_code
            mapped = _STATUS_TO_CLASS.get(status)
            if mapped is None and status >= HTTPStatus.INTERNAL_SERVER_ERROR:
                mapped = ServerError
            if mapped is not None:
                target_cls = mapped
        return super().__new__(target_cls)

    def __init__(self, response: HttpResponse, attempt: int, method: str = 'GET') -> None:
        """Initialize the API error from a failed response.

        Args:
            response: The failed HTTP response from the Apify API.
            attempt: The attempt number when the request failed (1-indexed).
            method: The HTTP method of the failed request.
        """
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
class InvalidRequestError(ApifyApiError):
    """Raised when the Apify API returns an HTTP 400 Bad Request response."""


@docs_group('Errors')
class UnauthorizedError(ApifyApiError):
    """Raised when the Apify API returns an HTTP 401 Unauthorized response."""


@docs_group('Errors')
class ForbiddenError(ApifyApiError):
    """Raised when the Apify API returns an HTTP 403 Forbidden response."""


@docs_group('Errors')
class NotFoundError(ApifyApiError):
    """Raised when the Apify API returns an HTTP 404 Not Found response."""


@docs_group('Errors')
class ConflictError(ApifyApiError):
    """Raised when the Apify API returns an HTTP 409 Conflict response."""


@docs_group('Errors')
class RateLimitError(ApifyApiError):
    """Raised when the Apify API returns an HTTP 429 Too Many Requests response.

    Rate-limited requests are retried automatically; this error is only raised after all
    retry attempts have been exhausted.
    """


@docs_group('Errors')
class ServerError(ApifyApiError):
    """Raised when the Apify API returns an HTTP 5xx response.

    Server errors are retried automatically; this error is only raised after all
    retry attempts have been exhausted.
    """


_STATUS_TO_CLASS: dict[int, type[ApifyApiError]] = {
    400: InvalidRequestError,
    401: UnauthorizedError,
    403: ForbiddenError,
    404: NotFoundError,
    409: ConflictError,
    429: RateLimitError,
}


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

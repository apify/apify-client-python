"""Utilities for error handling."""

from __future__ import annotations

from http import HTTPStatus

import impit

from apify_client.errors import ApifyApiError, InvalidResponseBodyError


def catch_not_found_or_throw(exc: ApifyApiError) -> None:
    """Suppress 404 Not Found errors, re-raise all other exceptions.

    Args:
        exc: The API error to check.

    Raises:
        ApifyApiError: If the error is not a 404 Not Found error.
    """
    is_not_found_status = exc.status_code == HTTPStatus.NOT_FOUND
    is_not_found_type = exc.type in ['record-not-found', 'record-or-token-not-found']
    if not (is_not_found_status and is_not_found_type):
        raise exc


def is_retryable_error(exc: Exception) -> bool:
    """Check if an exception should be retried.

    Args:
        exc: The exception to check.

    Returns:
        True if the exception is retryable (network errors, timeouts, etc.).
    """
    return isinstance(
        exc,
        (
            InvalidResponseBodyError,
            impit.NetworkError,
            impit.TimeoutException,
            impit.RemoteProtocolError,
        ),
    )

from __future__ import annotations

from typing import TYPE_CHECKING

import impit

from apify_client.errors import InvalidResponseBodyError, NotFoundError

if TYPE_CHECKING:
    from apify_client.errors import ApifyApiError


def catch_not_found_or_throw(exc: ApifyApiError) -> None:
    """Suppress 404 Not Found errors and re-raise all other API errors.

    Args:
        exc: The API error to check.

    Raises:
        ApifyApiError: If the error is not a 404 Not Found error.
    """
    if not isinstance(exc, NotFoundError):
        raise exc


def catch_not_found_for_resource_or_throw(exc: ApifyApiError, resource_id: str | None) -> None:
    """Like `catch_not_found_or_throw`, but only suppress 404s when the client targets a specific resource by ID.

    For chained clients without a `resource_id` (e.g. `run.dataset()`, `run.log()`), a 404 could mean either the
    parent or the default sub-resource is missing — the API body cannot disambiguate — so the error propagates
    rather than being swallowed.
    """
    if resource_id is None:
        raise exc
    catch_not_found_or_throw(exc)


def is_retryable_error(exc: Exception) -> bool:
    """Check if the given error is retryable.

    All `impit.HTTPError` subclasses are considered retryable because they represent transport-level failures
    (network issues, timeouts, protocol errors, body decoding errors) that are typically transient. HTTP status
    code errors are handled separately in `_make_request` based on the response status code, not here.
    """
    return isinstance(
        exc,
        (
            InvalidResponseBodyError,
            impit.HTTPError,
        ),
    )

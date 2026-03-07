from __future__ import annotations

import hashlib
import hmac
import io
import json
import string
import time
import warnings
from base64 import urlsafe_b64encode
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Literal, TypeVar, overload

import impit

from apify_client._consts import OVERRIDABLE_DEFAULT_HEADERS
from apify_client.errors import InvalidResponseBodyError

if TYPE_CHECKING:
    from datetime import timedelta

    from apify_client._http_clients import HttpResponse
    from apify_client.errors import ApifyApiError

T = TypeVar('T')

_BASE62_CHARSET = string.digits + string.ascii_letters
"""Module-level constant for base62 encoding."""


@overload
def to_seconds(td: None, *, as_int: bool = ...) -> None: ...
@overload
def to_seconds(td: timedelta) -> float: ...
@overload
def to_seconds(td: timedelta, *, as_int: Literal[True]) -> int: ...
@overload
def to_seconds(td: timedelta, *, as_int: Literal[False]) -> float: ...


def to_seconds(td: timedelta | None, *, as_int: bool = False) -> float | int | None:
    """Convert timedelta to seconds.

    Args:
        td: The timedelta to convert, or None.
        as_int: If True, round and return as int. Defaults to False.

    Returns:
        The total seconds as a float (or int if as_int=True), or None if input is None.
    """
    if td is None:
        return None
    seconds = td.total_seconds()
    return int(seconds) if as_int else seconds


def catch_not_found_or_throw(exc: ApifyApiError) -> None:
    """Suppress 404 Not Found errors and re-raise all other API errors.

    Args:
        exc: The API error to check.

    Raises:
        ApifyApiError: If the error is not a 404 Not Found error.
    """
    is_not_found_status = exc.status_code == HTTPStatus.NOT_FOUND
    is_not_found_type = exc.type in ['record-not-found', 'record-or-token-not-found']
    if not (is_not_found_status and is_not_found_type):
        raise exc


def encode_key_value_store_record_value(value: Any, content_type: str | None = None) -> tuple[Any, str]:
    """Encode a value for storage in a key-value store record.

    Args:
        value: The value to encode (can be dict, str, bytes, or file-like object).
        content_type: The content type; if None, it's inferred from the value type.

    Returns:
        A tuple of (encoded_value, content_type).
    """
    if not content_type:
        if isinstance(value, (bytes, bytearray, io.IOBase)):
            content_type = 'application/octet-stream'
        elif isinstance(value, str):
            content_type = 'text/plain; charset=utf-8'
        else:
            content_type = 'application/json; charset=utf-8'

    if (
        'application/json' in content_type
        and not isinstance(value, (bytes, bytearray, io.IOBase))
        and not isinstance(value, str)
    ):
        # Don't use indentation to reduce size.
        value = json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            default=str,
        ).encode('utf-8')

    return (value, content_type)


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


def to_safe_id(id: str) -> str:
    """Convert a resource ID to URL-safe format by replacing forward slashes with tildes.

    Args:
        id: The resource identifier in format `resource_id` or `username/resource_id`.

    Returns:
        The resource identifier with `/` characters replaced by `~`.
    """
    return id.replace('/', '~')


def response_to_dict(response: HttpResponse) -> dict:
    """Parse the API response as a dictionary and validate its type.

    Args:
        response: The HTTP response object from the API.

    Returns:
        The parsed response as a dictionary.

    Raises:
        ValueError: If the response is not a dictionary.
    """
    data = response.json()

    if isinstance(data, dict):
        return data

    raise ValueError(f'The response is not a dictionary. Got: {type(data).__name__}')


def response_to_list(response: HttpResponse) -> list:
    """Parse the API response as a list and validate its type.

    Args:
        response: The HTTP response object from the API.

    Returns:
        The parsed response as a list.

    Raises:
        ValueError: If the response is not a list.
    """
    data = response.json()

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        return [data]

    raise ValueError(f'The response is not a list. Got: {type(data).__name__}')


def encode_base62(num: int) -> str:
    """Encode an integer to a base62 string.

    Args:
        num: The number to encode.

    Returns:
        The base62-encoded string.
    """
    if num == 0:
        return _BASE62_CHARSET[0]

    # Use list to build result for O(n) complexity instead of O(n^2) string concatenation.
    parts = []
    while num > 0:
        num, remainder = divmod(num, 62)
        parts.append(_BASE62_CHARSET[remainder])

    # Reverse and join once at the end.
    return ''.join(reversed(parts))


def create_hmac_signature(secret_key: str, message: str) -> str:
    """Generate an HMAC-SHA256 signature and encode it using base62.

    The HMAC signature is truncated to 30 characters and then encoded in base62 to reduce the signature length.

    Args:
        secret_key: The secret key used for signing.
        message: The message to be signed.

    Returns:
        The base62-encoded signature.
    """
    signature = hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()[:30]

    decimal_signature = int(signature, 16)

    return encode_base62(decimal_signature)


def create_storage_content_signature(
    resource_id: str,
    url_signing_secret_key: str,
    expires_in: timedelta | None = None,
    version: int = 0,
) -> str:
    """Create a secure signature for a storage resource like a dataset or key-value store.

    This signature is used to generate a signed URL for authenticated access, which can be expiring or permanent.
    The signature is created using HMAC with the provided secret key and includes the resource ID, expiration time,
    and version.

    Args:
        resource_id: The unique identifier of the storage resource.
        url_signing_secret_key: The secret key for signing the URL.
        expires_in: Optional expiration duration; if None, the signature never expires.
        version: The signature version number (default: 0).

    Returns:
        The base64url-encoded signature string.
    """
    expires_at = int(time.time() * 1000) + int(to_seconds(expires_in) * 1000) if expires_in is not None else 0

    message_to_sign = f'{version}.{expires_at}.{resource_id}'
    hmac_sig = create_hmac_signature(url_signing_secret_key, message_to_sign)

    base64url_encoded_payload = urlsafe_b64encode(f'{version}.{expires_at}.{hmac_sig}'.encode())
    return base64url_encoded_payload.decode('utf-8')


def check_custom_headers(class_name: str, headers: dict[str, str]) -> None:
    """Warn if custom headers override important default headers."""
    overwrite_headers = [key for key in headers if key.title() in OVERRIDABLE_DEFAULT_HEADERS]

    if overwrite_headers:
        warnings.warn(
            f'{", ".join(overwrite_headers)} headers of {class_name} was overridden with an '
            'explicit value. A wrong header value can lead to API errors, it is recommended to use the default '
            f'value for following headers: {", ".join(OVERRIDABLE_DEFAULT_HEADERS)}.',
            category=UserWarning,
            stacklevel=3,
        )

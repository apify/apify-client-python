"""Utility functions and helpers for the Apify client."""

from __future__ import annotations

import base64
import hashlib
import hmac
import io
import json
import string
import time
from enum import Enum
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, TypeVar

from apify_client.errors import ApifyApiError  # noqa: TC001 - Used at runtime in catch_not_found_or_throw

if TYPE_CHECKING:
    from impit import Response

T = TypeVar('T')


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


def filter_none_values(
    data: dict,
    *,
    remove_empty_dicts: bool | None = None,
) -> dict:
    """Remove None values from a dictionary recursively.

    The Apify API ignores missing fields but may reject fields explicitly set to None. This function prepares request
    payloads by recursively removing None values from nested dictionaries.

    Args:
        data: The dictionary to clean.
        remove_empty_dicts: If True, also remove empty dictionaries after filtering None values.

    Returns:
        A new dictionary with None values removed at all nesting levels.
    """

    def _internal(dictionary: dict, *, remove_empty: bool | None = None) -> dict | None:
        result = {}
        for key, val in dictionary.items():
            if isinstance(val, dict):
                val = _internal(val, remove_empty=remove_empty)  # noqa: PLW2901
            if val is not None:
                result[key] = val
        if not result and remove_empty:
            return None
        return result

    result = _internal(data, remove_empty=remove_empty_dicts)
    return result if result is not None else {}


def encode_webhook_list_to_base64(webhooks: list[dict]) -> str:
    """Encode a list of webhook dictionaries to base64 for API transmission.

    Args:
        webhooks: A list of webhook dictionaries with keys like "event_types", "request_url", etc.

    Returns:
        A base64-encoded JSON string.
    """
    data = list[dict]()
    for webhook in webhooks:
        webhook_representation = {
            'eventTypes': [enum_to_value(event_type) for event_type in webhook['event_types']],
            'requestUrl': webhook['request_url'],
        }
        if 'payload_template' in webhook:
            webhook_representation['payloadTemplate'] = webhook['payload_template']
        if 'headers_template' in webhook:
            webhook_representation['headersTemplate'] = webhook['headers_template']
        data.append(webhook_representation)

    return base64.b64encode(json.dumps(data).encode('utf-8')).decode('ascii')


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
        value = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False, default=str).encode('utf-8')

    return (value, content_type)


def enum_to_value(value: Any) -> Any:
    """Convert an Enum member to its value, or return the value unchanged if not an Enum.

    Ensures Enum instances are converted to primitive values suitable for API transmission.

    Args:
        value: The value to potentially convert (Enum member or any other type).

    Returns:
        The Enum's value if the input is an Enum; otherwise returns the input unchanged.
    """
    if isinstance(value, Enum):
        return value.value
    return value


def to_safe_id(id: str) -> str:
    """Convert a resource ID to URL-safe format by replacing forward slashes with tildes.

    Args:
        id: The resource identifier in format `resource_id` or `username/resource_id`.

    Returns:
        The resource identifier with `/` characters replaced by `~`.
    """
    return id.replace('/', '~')


def response_to_dict(response: Response) -> dict:
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


def response_to_list(response: Response) -> list:
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

    raise ValueError(f'The response is not a list. Got: {type(data).__name__}')


def encode_base62(num: int) -> str:
    """Encode an integer to a base62 string.

    Args:
        num: The number to encode.

    Returns:
        The base62-encoded string.
    """
    charset = string.digits + string.ascii_letters

    if num == 0:
        return charset[0]

    res = ''
    while num > 0:
        num, remainder = divmod(num, 62)
        res = charset[remainder] + res
    return res


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
    expires_in_millis: int | None = None,
    version: int = 0,
) -> str:
    """Create a secure signature for a storage resource like a dataset or key-value store.

    This signature is used to generate a signed URL for authenticated access, which can be expiring or permanent.
    The signature is created using HMAC with the provided secret key and includes the resource ID, expiration time,
    and version.

    Args:
        resource_id: The unique identifier of the storage resource.
        url_signing_secret_key: The secret key for signing the URL.
        expires_in_millis: Optional expiration time in milliseconds from now; if None, the signature never expires.
        version: The signature version number (default: 0).

    Returns:
        The base64url-encoded signature string.
    """
    expires_at = int(time.time() * 1000) + expires_in_millis if expires_in_millis else 0

    message_to_sign = f'{version}.{expires_at}.{resource_id}'
    hmac_sig = create_hmac_signature(url_signing_secret_key, message_to_sign)

    base64url_encoded_payload = base64.urlsafe_b64encode(f'{version}.{expires_at}.{hmac_sig}'.encode())
    return base64url_encoded_payload.decode('utf-8')

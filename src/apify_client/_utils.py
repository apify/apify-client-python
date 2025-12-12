from __future__ import annotations

import asyncio
import base64
import io
import json
import random
import re
import time
from enum import Enum
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, TypeVar, cast

import impit

from apify_client.errors import InvalidResponseBodyError

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from impit import Response

    from apify_client.errors import ApifyApiError

T = TypeVar('T')


def filter_out_none_values_recursively(
    dictionary: dict,
    *,
    remove_empty_dicts: bool | None = None,
) -> dict:
    """Return a copy of the dictionary with all None values recursively removed.

    Args:
        dictionary: The dictionary to filter.
        remove_empty_dicts: If True, also remove empty dictionaries after filtering.

    Returns:
        A new dictionary without None values.
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

    return cast('dict', _internal(dictionary, remove_empty=remove_empty_dicts))


def maybe_extract_enum_member_value(maybe_enum_member: Any) -> Any:
    """Extract the value from an Enum member, or return the input unchanged if not an Enum."""
    if isinstance(maybe_enum_member, Enum):
        return maybe_enum_member.value
    return maybe_enum_member


def to_safe_id(id: str) -> str:
    """Convert a resource ID to URL-safe format by replacing `/` with `~`.

    Args:
        id: The resource identifier (format: `resource_id` or `username/resource_id`).

    Returns:
        The resource identifier with `/` replaced by `~`.
    """
    return id.replace('/', '~')


def response_to_dict(response: impit.Response) -> dict:
    """Ensure the API response is a dictionary.

    Args:
        response: The parsed API response (typically from `response.json()`).

    Returns:
        The response as a dictionary.

    Raises:
        ValueError: If the response is not a dictionary.
    """
    data = response.json()
    if isinstance(data, dict):
        return data

    raise ValueError('The response is not a dictionary.')


def response_to_list(response: impit.Response) -> list:
    """Ensure the API response is a list.

    Args:
        response: The parsed API response (typically from `response.json()`).

    Returns:
        The response as a list.

    Raises:
        ValueError: If the response is not a list.
    """
    data = response.json()
    if isinstance(data, list):
        return data

    raise ValueError('The response is not a list.')


def retry_with_exp_backoff(
    func: Callable[[Callable[[], None], int], T],
    *,
    max_retries: int = 8,
    backoff_base_millis: int = 500,
    backoff_factor: float = 2,
    random_factor: float = 1,
) -> T:
    """Retry a function with exponential backoff.

    Args:
        func: Function to retry. Receives a stop_retrying callback and attempt number.
        max_retries: Maximum number of retry attempts.
        backoff_base_millis: Base backoff delay in milliseconds.
        backoff_factor: Exponential backoff multiplier (1-10).
        random_factor: Random jitter factor (0-1).

    Returns:
        The return value of the function.
    """
    random_factor = min(max(0, random_factor), 1)
    backoff_factor = min(max(1, backoff_factor), 10)
    swallow = True

    def stop_retrying() -> None:
        nonlocal swallow
        swallow = False

    for attempt in range(1, max_retries + 1):
        try:
            return func(stop_retrying, attempt)
        except Exception:
            if not swallow:
                raise

        random_sleep_factor = random.uniform(1, 1 + random_factor)
        backoff_base_secs = backoff_base_millis / 1000
        backoff_exp_factor = backoff_factor ** (attempt - 1)

        sleep_time_secs = random_sleep_factor * backoff_base_secs * backoff_exp_factor
        time.sleep(sleep_time_secs)

    return func(stop_retrying, max_retries + 1)


async def retry_with_exp_backoff_async(
    async_func: Callable[[Callable[[], None], int], Awaitable[T]],
    *,
    max_retries: int = 8,
    backoff_base_millis: int = 500,
    backoff_factor: float = 2,
    random_factor: float = 1,
) -> T:
    """Retry an async function with exponential backoff.

    Args:
        async_func: Async function to retry. Receives a stop_retrying callback and attempt number.
        max_retries: Maximum number of retry attempts.
        backoff_base_millis: Base backoff delay in milliseconds.
        backoff_factor: Exponential backoff multiplier (1-10).
        random_factor: Random jitter factor (0-1).

    Returns:
        The return value of the async function.
    """
    random_factor = min(max(0, random_factor), 1)
    backoff_factor = min(max(1, backoff_factor), 10)
    swallow = True

    def stop_retrying() -> None:
        nonlocal swallow
        swallow = False

    for attempt in range(1, max_retries + 1):
        try:
            return await async_func(stop_retrying, attempt)
        except Exception:
            if not swallow:
                raise

        random_sleep_factor = random.uniform(1, 1 + random_factor)
        backoff_base_secs = backoff_base_millis / 1000
        backoff_exp_factor = backoff_factor ** (attempt - 1)

        sleep_time_secs = random_sleep_factor * backoff_base_secs * backoff_exp_factor
        await asyncio.sleep(sleep_time_secs)

    return await async_func(stop_retrying, max_retries + 1)


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


def encode_webhook_list_to_base64(webhooks: list[dict]) -> str:
    """Encode a list of webhook dictionaries to base64 for API transmission.

    Args:
        webhooks: List of webhook dictionaries with keys like "event_types", "request_url", etc.

    Returns:
        Base64-encoded JSON string.
    """
    data = list[dict]()
    for webhook in webhooks:
        webhook_representation = {
            'eventTypes': [maybe_extract_enum_member_value(event_type) for event_type in webhook['event_types']],
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
        content_type: The content type. If None, it's inferred from the value type.

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


def maybe_parse_response(response: Response) -> Any:
    """Parse an HTTP response based on its content type.

    Args:
        response: The HTTP response to parse.

    Returns:
        Parsed response data (JSON dict/list, text string, or raw bytes).

    Raises:
        InvalidResponseBodyError: If the response body cannot be parsed.
    """
    if response.status_code == HTTPStatus.NO_CONTENT:
        return None

    content_type = ''
    if 'content-type' in response.headers:
        content_type = response.headers['content-type'].split(';')[0].strip()

    try:
        if re.search(r'^application/json', content_type, flags=re.IGNORECASE):
            response_data = response.json()
        elif re.search(r'^application/.*xml$', content_type, flags=re.IGNORECASE) or re.search(
            r'^text/', content_type, flags=re.IGNORECASE
        ):
            response_data = response.text
        else:
            response_data = response.content
    except ValueError as err:
        raise InvalidResponseBodyError(response) from err
    else:
        return response_data


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

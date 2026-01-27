from __future__ import annotations

import asyncio
import base64
import io
import json
import math
import random
import re
import time
from datetime import datetime, timezone
from enum import Enum
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, TypeVar, cast

import impit

from apify_client._consts import ActorJobStatus
from apify_client.errors import ApifyApiError, ApifyClientError, InvalidResponseBodyError

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from impit import Response

    from apify_client._http_client import HttpClient, HttpClientAsync

T = TypeVar('T')

JsonSerializable = str | int | float | bool | None | dict[str, Any] | list[Any]
"""Type for representing json-serializable values. It's close enough to the real thing supported by json.parse.
It was suggested in a discussion with (and approved by) Guido van Rossum, so I'd consider it correct enough.
"""

# Constants for wait_for_finish functionality
DEFAULT_WAIT_FOR_FINISH_SEC = 999999
DEFAULT_WAIT_WHEN_JOB_NOT_EXIST_SEC = 3

# Standard timeout values for API operations
FAST_OPERATION_TIMEOUT_SECS = 5  # For fast, idempotent operations
STANDARD_OPERATION_TIMEOUT_SECS = 30  # For operations that may take longer


def wait_for_finish_sync(
    http_client: HttpClient,
    url: str,
    params: dict,
    wait_secs: int | None = None,
) -> dict | None:
    """Wait synchronously for an Actor job (run or build) to finish.

    Polls the job status until it reaches a terminal state or timeout.
    Handles 404 errors gracefully (job might not exist yet in replicas).

    Args:
        http_client: HTTP client instance for making requests
        url: Full URL to the job endpoint
        params: Base query parameters to include in each request
        wait_secs: Maximum seconds to wait (None = indefinite)

    Returns:
        Job data dict when finished, or None if job doesn't exist after
        DEFAULT_WAIT_WHEN_JOB_NOT_EXIST_SEC seconds

    Raises:
        ApifyApiError: If API returns errors other than 404
    """
    started_at = datetime.now(timezone.utc)
    should_repeat = True
    job: dict | None = None
    seconds_elapsed = 0

    while should_repeat:
        wait_for_finish = DEFAULT_WAIT_FOR_FINISH_SEC
        if wait_secs is not None:
            wait_for_finish = wait_secs - seconds_elapsed

        try:
            response = http_client.call(
                url=url,
                method='GET',
                params={**params, 'waitForFinish': wait_for_finish},
            )
            job_response = response_to_dict(response)
            job = job_response.get('data') if isinstance(job_response, dict) else job_response
            seconds_elapsed = math.floor((datetime.now(timezone.utc) - started_at).total_seconds())

            if not isinstance(job, dict):
                raise ApifyClientError(
                    f'Unexpected response format received from the API. '
                    f'Expected dict with "status" field, got: {type(job).__name__}'
                )

            is_terminal = ActorJobStatus(job['status']).is_terminal
            is_timed_out = wait_secs is not None and seconds_elapsed >= wait_secs
            if is_terminal or is_timed_out:
                should_repeat = False

            if not should_repeat:
                # Early return here so that we avoid the sleep below if not needed
                return job

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

            # If there are still not found errors after DEFAULT_WAIT_WHEN_JOB_NOT_EXIST_SEC, we give up
            # and return None. In such case, the requested record probably really doesn't exist.
            if seconds_elapsed > DEFAULT_WAIT_WHEN_JOB_NOT_EXIST_SEC:
                return None

        # It might take some time for database replicas to get up-to-date so sleep a bit before retrying
        time.sleep(0.25)

    return job


async def wait_for_finish_async(
    http_client: HttpClientAsync,
    url: str,
    params: dict,
    wait_secs: int | None = None,
) -> dict | None:
    """Wait asynchronously for an Actor job (run or build) to finish.

    Polls the job status until it reaches a terminal state or timeout.
    Handles 404 errors gracefully (job might not exist yet in replicas).

    Args:
        http_client: Async HTTP client instance for making requests
        url: Full URL to the job endpoint
        params: Base query parameters to include in each request
        wait_secs: Maximum seconds to wait (None = indefinite)

    Returns:
        Job data dict when finished, or None if job doesn't exist after
        DEFAULT_WAIT_WHEN_JOB_NOT_EXIST_SEC seconds

    Raises:
        ApifyApiError: If API returns errors other than 404
    """
    started_at = datetime.now(timezone.utc)
    should_repeat = True
    job: dict | None = None
    seconds_elapsed = 0

    while should_repeat:
        wait_for_finish = DEFAULT_WAIT_FOR_FINISH_SEC
        if wait_secs is not None:
            wait_for_finish = wait_secs - seconds_elapsed

        try:
            response = await http_client.call(
                url=url,
                method='GET',
                params={**params, 'waitForFinish': wait_for_finish},
            )
            job_response = response_to_dict(response)
            job = job_response.get('data') if isinstance(job_response, dict) else job_response

            if not isinstance(job, dict):
                raise ApifyClientError(
                    f'Unexpected response format received from the API. '
                    f'Expected dict with "status" field, got: {type(job).__name__}'
                )

            seconds_elapsed = math.floor((datetime.now(timezone.utc) - started_at).total_seconds())
            is_terminal = ActorJobStatus(job['status']).is_terminal
            is_timed_out = wait_secs is not None and seconds_elapsed >= wait_secs
            if is_terminal or is_timed_out:
                should_repeat = False

            if not should_repeat:
                # Early return here so that we avoid the sleep below if not needed
                return job

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

            # If there are still not found errors after DEFAULT_WAIT_WHEN_JOB_NOT_EXIST_SEC, we give up
            # and return None. In such case, the requested record probably really doesn't exist.
            if seconds_elapsed > DEFAULT_WAIT_WHEN_JOB_NOT_EXIST_SEC:
                return None

        # It might take some time for database replicas to get up-to-date so sleep a bit before retrying
        await asyncio.sleep(0.25)

    return job


def clean_request_dict(
    data: dict,
    *,
    remove_empty_dicts: bool | None = None,
) -> dict:
    """Remove None values from a dictionary recursively.

    The Apify API ignores missing fields but may reject fields explicitly
    set to None. This prepares request payloads by recursively removing
    None values.

    Args:
        data: Dictionary to clean
        remove_empty_dicts: Also remove empty dicts after filtering None values

    Returns:
        New dictionary with None values removed at all nesting levels

    Example:
        >>> clean_request_dict({'a': 1, 'b': None, 'c': {'d': None, 'e': 2}})
        {'a': 1, 'c': {'e': 2}}
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

    return cast('dict', _internal(data, remove_empty=remove_empty_dicts))


# Backwards compatibility alias
filter_out_none_values_recursively = clean_request_dict


def enum_to_value(value: Any) -> Any:
    """Convert Enum member to its value, or return unchanged if not an Enum.

    Ensures Enum instances are converted to primitive values suitable
    for API transmission.

    Args:
        value: Value to potentially convert (Enum member or any other type)

    Returns:
        If value is an Enum, returns value.value; otherwise returns value unchanged

    Example:
        >>> enum_to_value(ActorJobStatus.SUCCEEDED)
        'SUCCEEDED'
        >>> enum_to_value('already_a_string')
        'already_a_string'
        >>> enum_to_value(None)
        None
    """
    if isinstance(value, Enum):
        return value.value
    return value


# Backwards compatibility alias
maybe_extract_enum_member_value = enum_to_value


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

    raise ValueError(f'The response is not a dictionary. Got: {type(data).__name__}')


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

    raise ValueError(f'The response is not a list. Got: {type(data).__name__}')


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

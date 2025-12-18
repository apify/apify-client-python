from __future__ import annotations

import asyncio
import base64
import contextlib
import io
import json
import json as jsonlib
import random
import re
import time
from collections.abc import Callable
from datetime import datetime, timezone
from enum import Enum
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, TypeVar, cast, overload

import impit

from apify_client.errors import InvalidResponseBodyError

if TYPE_CHECKING:
    from collections.abc import Awaitable

    from impit import Response

    from apify_client.errors import ApifyApiError

PARSE_DATE_FIELDS_MAX_DEPTH = 3
PARSE_DATE_FIELDS_KEY_SUFFIX = 'At'
RECORD_NOT_FOUND_EXCEPTION_TYPES = ['record-not-found', 'record-or-token-not-found']

T = TypeVar('T')
StopRetryingType = Callable[[], None]


def filter_out_none_values_recursively(dictionary: dict) -> dict:
    """Return copy of the dictionary, recursively omitting all keys for which values are None."""
    return cast('dict', filter_out_none_values_recursively_internal(dictionary))


def filter_out_none_values_recursively_internal(
    dictionary: dict,
    *,
    remove_empty_dicts: bool | None = None,
) -> dict | None:
    """Recursively filters out None values from a dictionary.

    Unfortunately, it's necessary to have an internal function for the correct result typing,
    without having to create complicated overloads
    """
    result = {}
    for k, v in dictionary.items():
        if isinstance(v, dict):
            v = filter_out_none_values_recursively_internal(  # noqa: PLW2901
                v, remove_empty_dicts=remove_empty_dicts is True or remove_empty_dicts is None
            )
        if v is not None:
            result[k] = v
    if not result and remove_empty_dicts:
        return None
    return result


@overload
def parse_date_fields(data: list, max_depth: int = PARSE_DATE_FIELDS_MAX_DEPTH) -> list: ...


@overload
def parse_date_fields(data: dict, max_depth: int = PARSE_DATE_FIELDS_MAX_DEPTH) -> dict: ...


def parse_date_fields(data: list | dict, max_depth: int = PARSE_DATE_FIELDS_MAX_DEPTH) -> list | dict:
    """Recursively parse date fields in a list or dictionary up to the specified depth."""
    if max_depth < 0:
        return data

    if isinstance(data, list):
        return [parse_date_fields(item, max_depth - 1) for item in data]

    if isinstance(data, dict):

        def parse(key: str, value: object) -> object:
            parsed_value = value
            if key.endswith(PARSE_DATE_FIELDS_KEY_SUFFIX) and isinstance(value, str):
                with contextlib.suppress(ValueError):
                    parsed_value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
            elif isinstance(value, dict):
                parsed_value = parse_date_fields(value, max_depth - 1)
            elif isinstance(value, list):
                parsed_value = parse_date_fields(value, max_depth)
            return parsed_value

        return {key: parse(key, value) for (key, value) in data.items()}

    return data


def is_content_type_json(content_type: str) -> bool:
    """Check if the given content type is JSON."""
    return bool(re.search(r'^application/json', content_type, flags=re.IGNORECASE))


def is_content_type_xml(content_type: str) -> bool:
    """Check if the given content type is XML."""
    return bool(re.search(r'^application/.*xml$', content_type, flags=re.IGNORECASE))


def is_content_type_text(content_type: str) -> bool:
    """Check if the given content type is text."""
    return bool(re.search(r'^text/', content_type, flags=re.IGNORECASE))


def is_file_or_bytes(value: Any) -> bool:
    """Check if the input value is a file-like object or bytes.

    The check for IOBase is not ideal, it would be better to use duck typing,
    but then the check would be super complex, judging from how the 'requests' library does it.
    This way should be good enough for the vast majority of use cases, if it causes issues, we can improve it later.
    """
    return isinstance(value, (bytes, bytearray, io.IOBase))


def json_dumps(obj: Any) -> str:
    """Dump JSON to a string with the correct settings and serializer."""
    return json.dumps(obj, ensure_ascii=False, indent=2, default=str)


def maybe_extract_enum_member_value(maybe_enum_member: Any) -> Any:
    """Extract the value of an enumeration member if it is an Enum, otherwise return the original value."""
    if isinstance(maybe_enum_member, Enum):
        return maybe_enum_member.value
    return maybe_enum_member


def to_safe_id(id: str) -> str:
    # Identificators of resources in the API are either in the format `resource_id` or `username/resource_id`.
    # Since the `/` character has a special meaning in URL paths,
    # we replace it with `~` for proper route parsing on the API, where after parsing the URL it's replaced back to `/`.
    return id.replace('/', '~')


def pluck_data(parsed_response: Any) -> dict:
    if isinstance(parsed_response, dict) and 'data' in parsed_response:
        return cast('dict', parsed_response['data'])

    raise ValueError('The "data" property is missing in the response.')


def pluck_data_as_list(parsed_response: Any) -> list:
    if isinstance(parsed_response, dict) and 'data' in parsed_response:
        return cast('list', parsed_response['data'])

    raise ValueError('The "data" property is missing in the response.')


def retry_with_exp_backoff(
    func: Callable[[StopRetryingType, int], T],
    *,
    max_retries: int = 8,
    backoff_base_millis: int = 500,
    backoff_factor: float = 2,
    random_factor: float = 1,
) -> T:
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
    async_func: Callable[[StopRetryingType, int], Awaitable[T]],
    *,
    max_retries: int = 8,
    backoff_base_millis: int = 500,
    backoff_factor: float = 2,
    random_factor: float = 1,
) -> T:
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
    is_not_found_status = exc.status_code == HTTPStatus.NOT_FOUND
    is_not_found_type = exc.type in RECORD_NOT_FOUND_EXCEPTION_TYPES
    if not (is_not_found_status and is_not_found_type):
        raise exc


def encode_webhook_list_to_base64(webhooks: list[dict]) -> str:
    """Encode a list of dictionaries representing webhooks to their base64-encoded representation for the API."""
    data = []
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

    return base64.b64encode(jsonlib.dumps(data).encode('utf-8')).decode('ascii')


def encode_key_value_store_record_value(value: Any, content_type: str | None = None) -> tuple[Any, str]:
    if not content_type:
        if is_file_or_bytes(value):
            content_type = 'application/octet-stream'
        elif isinstance(value, str):
            content_type = 'text/plain; charset=utf-8'
        else:
            content_type = 'application/json; charset=utf-8'

    if 'application/json' in content_type and not is_file_or_bytes(value) and not isinstance(value, str):
        value = jsonlib.dumps(value, ensure_ascii=False, indent=2, allow_nan=False, default=str).encode('utf-8')

    return (value, content_type)


def maybe_parse_response(response: Response) -> Any:
    if response.status_code == HTTPStatus.NO_CONTENT:
        return None

    content_type = ''
    if 'content-type' in response.headers:
        content_type = response.headers['content-type'].split(';')[0].strip()

    try:
        if is_content_type_json(content_type):
            response_data = response.json()
        elif is_content_type_xml(content_type) or is_content_type_text(content_type):
            response_data = response.text
        else:
            response_data = response.content
    except ValueError as err:
        raise InvalidResponseBodyError(response) from err
    else:
        return response_data


def is_retryable_error(exc: Exception) -> bool:
    """Check if the given error is retryable."""
    return isinstance(
        exc,
        (
            InvalidResponseBodyError,
            impit.NetworkError,
            impit.TimeoutException,
            impit.RemoteProtocolError,
        ),
    )

from __future__ import annotations

import asyncio
import base64
import json
import random
import time
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, List, TypeVar, cast

from apify_shared.utils import is_file_or_bytes, maybe_extract_enum_member_value

if TYPE_CHECKING:
    from apify_client._errors import ApifyApiError

PARSE_DATE_FIELDS_MAX_DEPTH = 3
PARSE_DATE_FIELDS_KEY_SUFFIX = 'At'

RECORD_NOT_FOUND_EXCEPTION_TYPES = ['record-not-found', 'record-or-token-not-found']

T = TypeVar('T')
StopRetryingType = Callable[[], None]


def to_safe_id(id: str) -> str:
    # Identificators of resources in the API are either in the format `resource_id` or `username/resource_id`.
    # Since the `/` character has a special meaning in URL paths,
    # we replace it with `~` for proper route parsing on the API, where after parsing the URL it's replaced back to `/`.
    return id.replace('/', '~')


def pluck_data(parsed_response: Any) -> dict:
    if isinstance(parsed_response, dict) and 'data' in parsed_response:
        return cast(Dict, parsed_response['data'])

    raise ValueError('The "data" property is missing in the response.')


def pluck_data_as_list(parsed_response: Any) -> list:
    if isinstance(parsed_response, dict) and 'data' in parsed_response:
        return cast(List, parsed_response['data'])

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
        data.append(webhook_representation)

    return base64.b64encode(json.dumps(data).encode('utf-8')).decode('ascii')


def encode_key_value_store_record_value(value: Any, content_type: str | None = None) -> tuple[Any, str]:
    if not content_type:
        if is_file_or_bytes(value):
            content_type = 'application/octet-stream'
        elif isinstance(value, str):
            content_type = 'text/plain; charset=utf-8'
        else:
            content_type = 'application/json; charset=utf-8'

    if 'application/json' in content_type and not is_file_or_bytes(value) and not isinstance(value, str):
        value = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False, default=str).encode('utf-8')

    return (value, content_type)

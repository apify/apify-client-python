import io
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

import pytest

from apify_client._utils import (
    _encode_webhook_list_to_base64,
    _filter_out_none_values_recursively,
    _filter_out_none_values_recursively_internal,
    _is_content_type_json,
    _is_content_type_text,
    _is_content_type_xml,
    _is_file_or_bytes,
    _maybe_extract_enum_member_value,
    _parse_date_fields,
    _pluck_data,
    _retry_with_exp_backoff,
    _retry_with_exp_backoff_async,
    _to_safe_id,
    ignore_docs,
)
from apify_client.consts import WebhookEventType


def test__to_safe_id() -> None:
    assert _to_safe_id('abc') == 'abc'
    assert _to_safe_id('abc/def') == 'abc~def'
    assert _to_safe_id('abc~def') == 'abc~def'


def test__parse_date_fields() -> None:
    # works correctly on empty dicts
    assert _parse_date_fields({}) == {}

    # correctly parses dates on fields ending with -At
    expected_datetime = datetime(2016, 11, 14, 11, 10, 52, 425000, timezone.utc)
    assert _parse_date_fields({'createdAt': '2016-11-14T11:10:52.425Z'}) == {'createdAt': expected_datetime}

    # doesn't parse dates on fields not ending with -At
    assert _parse_date_fields({'saveUntil': '2016-11-14T11:10:52.425Z'}) == {'saveUntil': '2016-11-14T11:10:52.425Z'}

    # parses dates in dicts in lists
    expected_datetime = datetime(2016, 11, 14, 11, 10, 52, 425000, timezone.utc)
    assert _parse_date_fields([{'createdAt': '2016-11-14T11:10:52.425Z'}]) == [{'createdAt': expected_datetime}]

    # parses nested dates
    expected_datetime = datetime(2020, 2, 29, 10, 9, 8, 100000, timezone.utc)
    assert _parse_date_fields({'a': {'b': {'c': {'createdAt': '2020-02-29T10:09:08.100Z'}}}}) \
        == {'a': {'b': {'c': {'createdAt': expected_datetime}}}}

    # doesn't parse dates nested too deep
    expected_datetime = datetime(2020, 2, 29, 10, 9, 8, 100000, timezone.utc)
    assert _parse_date_fields({'a': {'b': {'c': {'d': {'createdAt': '2020-02-29T10:09:08.100Z'}}}}}) \
        == {'a': {'b': {'c': {'d': {'createdAt': '2020-02-29T10:09:08.100Z'}}}}}

    # doesn't die when the date can't be parsed
    assert _parse_date_fields({'createdAt': 'NOT_A_DATE'}) == {'createdAt': 'NOT_A_DATE'}


def test__pluck_data() -> None:
    # works correctly when data is present
    assert _pluck_data({'data': {}}) == {}
    assert _pluck_data({'a': 'b', 'data': {'b': 'c'}}) == {'b': 'c'}

    # throws the right error when it is not
    with pytest.raises(ValueError, match='The "data" property is missing in the response.'):
        _pluck_data({'a': 'b'})
    with pytest.raises(ValueError, match='The "data" property is missing in the response.'):
        _pluck_data(None)
    with pytest.raises(ValueError, match='The "data" property is missing in the response.'):
        _pluck_data('{"a": "b"}')


def test__is_content_type_json() -> None:
    # returns True for the right content types
    assert _is_content_type_json('application/json') is True
    assert _is_content_type_json('application/jsonc') is True
    # returns False for bad content types
    assert _is_content_type_json('application/xml') is False
    assert _is_content_type_json('application/ld+json') is False


def test__is_content_type_xml() -> None:
    # returns True for the right content types
    assert _is_content_type_xml('application/xml') is True
    assert _is_content_type_xml('application/xhtml+xml') is True
    # returns False for bad content types
    assert _is_content_type_xml('application/json') is False
    assert _is_content_type_xml('text/html') is False


def test__is_content_type_text() -> None:
    # returns True for the right content types
    assert _is_content_type_text('text/html') is True
    assert _is_content_type_text('text/plain') is True
    # returns False for bad content types
    assert _is_content_type_text('application/json') is False
    assert _is_content_type_text('application/text') is False


def test__is_file_or_bytes() -> None:
    # returns True for the right value types
    assert _is_file_or_bytes(b'abc') is True
    assert _is_file_or_bytes(bytearray.fromhex('F0F1F2')) is True
    assert _is_file_or_bytes(io.BytesIO(b'\x00\x01\x02')) is True

    # returns False for bad value types
    assert _is_file_or_bytes('abc') is False
    assert _is_file_or_bytes(['a', 'b', 'c']) is False
    assert _is_file_or_bytes({'a': 'b'}) is False
    assert _is_file_or_bytes(None) is False


def test__retry_with_exp_backoff() -> None:
    attempt_counter = 0

    class RetryableError(Exception):
        pass

    class NonRetryableError(Exception):
        pass

    def returns_on_fifth_attempt(_stop_retrying: Callable, attempt: int) -> Any:
        nonlocal attempt_counter
        attempt_counter += 1

        if attempt == 5:
            return 'SUCCESS'
        raise RetryableError()

    def bails_on_third_attempt(stop_retrying: Callable, attempt: int) -> Any:
        nonlocal attempt_counter
        attempt_counter += 1

        if attempt == 3:
            stop_retrying()
            raise NonRetryableError()
        else:
            raise RetryableError()

    # Returns the correct result after the correct time (should take 100 + 200 + 400 + 800 = 1500 ms)
    start = time.time()
    result = _retry_with_exp_backoff(returns_on_fifth_attempt, backoff_base_millis=100, backoff_factor=2, random_factor=0)
    elapsed_time_seconds = time.time() - start
    assert result == 'SUCCESS'
    assert attempt_counter == 5
    assert elapsed_time_seconds > 1.4
    assert elapsed_time_seconds < 2.0

    # Stops retrying when failed for max_retries times
    attempt_counter = 0
    with pytest.raises(RetryableError):
        _retry_with_exp_backoff(returns_on_fifth_attempt, max_retries=3, backoff_base_millis=1)
    assert attempt_counter == 4

    # Bails when the bail function is called
    attempt_counter = 0
    with pytest.raises(NonRetryableError):
        _retry_with_exp_backoff(bails_on_third_attempt, backoff_base_millis=1)
    assert attempt_counter == 3


async def test__retry_with_exp_backoff_async() -> None:
    attempt_counter = 0

    class RetryableError(Exception):
        pass

    class NonRetryableError(Exception):
        pass

    async def returns_on_fifth_attempt(_stop_retrying: Callable, attempt: int) -> Any:
        nonlocal attempt_counter
        attempt_counter += 1

        if attempt == 5:
            return 'SUCCESS'
        raise RetryableError()

    async def bails_on_third_attempt(stop_retrying: Callable, attempt: int) -> Any:
        nonlocal attempt_counter
        attempt_counter += 1

        if attempt == 3:
            stop_retrying()
            raise NonRetryableError()
        else:
            raise RetryableError()

    # Returns the correct result after the correct time (should take 100 + 200 + 400 + 800 = 1500 ms)
    start = time.time()
    result = await _retry_with_exp_backoff_async(returns_on_fifth_attempt, backoff_base_millis=100, backoff_factor=2, random_factor=0)
    elapsed_time_seconds = time.time() - start
    assert result == 'SUCCESS'
    assert attempt_counter == 5
    assert elapsed_time_seconds > 1.4
    assert elapsed_time_seconds < 2.0

    # Stops retrying when failed for max_retries times
    attempt_counter = 0
    with pytest.raises(RetryableError):
        await _retry_with_exp_backoff_async(returns_on_fifth_attempt, max_retries=3, backoff_base_millis=1)
    assert attempt_counter == 4

    # Bails when the bail function is called
    attempt_counter = 0
    with pytest.raises(NonRetryableError):
        await _retry_with_exp_backoff_async(bails_on_third_attempt, backoff_base_millis=1)
    assert attempt_counter == 3


def test__encode_webhook_list_to_base64() -> None:
    assert _encode_webhook_list_to_base64([]) == 'W10='
    assert _encode_webhook_list_to_base64([
        {
            'event_types': [WebhookEventType.ACTOR_RUN_CREATED],
            'request_url': 'https://example.com/run-created',
        },
        {
            'event_types': [WebhookEventType.ACTOR_RUN_SUCCEEDED],
            'request_url': 'https://example.com/run-succeeded',
            'payload_template': '{"hello": "world", "resource":{{resource}}}',
        },
    ]) == 'W3siZXZlbnRUeXBlcyI6IFsiQUNUT1IuUlVOLkNSRUFURUQiXSwgInJlcXVlc3RVcmwiOiAiaHR0cHM6Ly9leGFtcGxlLmNvbS9ydW4tY3JlYXRlZCJ9LCB7ImV2ZW50VHlwZXMiOiBbIkFDVE9SLlJVTi5TVUNDRUVERUQiXSwgInJlcXVlc3RVcmwiOiAiaHR0cHM6Ly9leGFtcGxlLmNvbS9ydW4tc3VjY2VlZGVkIiwgInBheWxvYWRUZW1wbGF0ZSI6ICJ7XCJoZWxsb1wiOiBcIndvcmxkXCIsIFwicmVzb3VyY2VcIjp7e3Jlc291cmNlfX19In1d'  # noqa: E501


def test__maybe_extract_enum_member_value() -> None:
    class TestEnum(Enum):
        A = 'A'
        B = 'B'

    assert _maybe_extract_enum_member_value(TestEnum.A) == 'A'
    assert _maybe_extract_enum_member_value(TestEnum.B) == 'B'
    assert _maybe_extract_enum_member_value('C') == 'C'
    assert _maybe_extract_enum_member_value(1) == 1
    assert _maybe_extract_enum_member_value(None) is None


def test__filter_out_none_values_recursively() -> None:
    assert _filter_out_none_values_recursively({'k1': 'v1'}) == {'k1': 'v1'}
    assert _filter_out_none_values_recursively({'k1': None}) == {}
    assert _filter_out_none_values_recursively({'k1': 'v1', 'k2': None, 'k3': {'k4': 'v4', 'k5': None}, 'k6': {'k7': None}}) \
        == {'k1': 'v1', 'k3': {'k4': 'v4'}}


def test__filter_out_none_values_recursively_internal() -> None:
    assert _filter_out_none_values_recursively_internal({}) == {}
    assert _filter_out_none_values_recursively_internal({'k1': {}}) == {}
    assert _filter_out_none_values_recursively_internal({}, False) == {}
    assert _filter_out_none_values_recursively_internal({'k1': {}}, False) == {'k1': {}}
    assert _filter_out_none_values_recursively_internal({}, True) is None
    assert _filter_out_none_values_recursively_internal({'k1': {}}, True) is None


def test_ignore_docs() -> None:
    def testing_function(_a: str, _b: str) -> str:
        """Dummy docstring"""
        return 'dummy'

    assert testing_function is ignore_docs(testing_function)

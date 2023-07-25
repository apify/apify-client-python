import time
from typing import Any, Callable

import pytest

from apify_client._utils import _encode_webhook_list_to_base64, _pluck_data, _retry_with_exp_backoff, _retry_with_exp_backoff_async, _to_safe_id
from apify_shared.consts import WebhookEventType


def test__to_safe_id() -> None:
    assert _to_safe_id('abc') == 'abc'
    assert _to_safe_id('abc/def') == 'abc~def'
    assert _to_safe_id('abc~def') == 'abc~def'


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

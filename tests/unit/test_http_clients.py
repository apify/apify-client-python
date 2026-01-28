import time
from collections.abc import Callable
from typing import Any

import pytest

from apify_client._http_clients import HttpClient, HttpClientAsync


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
        raise RetryableError

    def bails_on_third_attempt(stop_retrying: Callable, attempt: int) -> Any:
        nonlocal attempt_counter
        attempt_counter += 1

        if attempt == 3:
            stop_retrying()
            raise NonRetryableError
        else:  # noqa: RET506
            raise RetryableError

    # Returns the correct result after the correct time (should take 100 + 200 + 400 + 800 = 1500 ms)
    start = time.time()
    result = HttpClient._retry_with_exp_backoff(
        returns_on_fifth_attempt, backoff_base_millis=100, backoff_factor=2, random_factor=0
    )
    elapsed_time_seconds = time.time() - start
    assert result == 'SUCCESS'
    assert attempt_counter == 5
    assert elapsed_time_seconds > 1.4
    assert elapsed_time_seconds < 2.0

    # Stops retrying when failed for max_retries times
    attempt_counter = 0
    with pytest.raises(RetryableError):
        HttpClient._retry_with_exp_backoff(returns_on_fifth_attempt, max_retries=3, backoff_base_millis=1)
    assert attempt_counter == 4

    # Bails when the bail function is called
    attempt_counter = 0
    with pytest.raises(NonRetryableError):
        HttpClient._retry_with_exp_backoff(bails_on_third_attempt, backoff_base_millis=1)
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
        raise RetryableError

    async def bails_on_third_attempt(stop_retrying: Callable, attempt: int) -> Any:
        nonlocal attempt_counter
        attempt_counter += 1

        if attempt == 3:
            stop_retrying()
            raise NonRetryableError
        else:  # noqa: RET506
            raise RetryableError

    # Returns the correct result after the correct time (should take 100 + 200 + 400 + 800 = 1500 ms)
    start = time.time()
    result = await HttpClientAsync._retry_with_exp_backoff(
        returns_on_fifth_attempt, backoff_base_millis=100, backoff_factor=2, random_factor=0
    )
    elapsed_time_seconds = time.time() - start
    assert result == 'SUCCESS'
    assert attempt_counter == 5
    assert elapsed_time_seconds > 1.4
    assert elapsed_time_seconds < 2.0

    # Stops retrying when failed for max_retries times
    attempt_counter = 0
    with pytest.raises(RetryableError):
        await HttpClientAsync._retry_with_exp_backoff(returns_on_fifth_attempt, max_retries=3, backoff_base_millis=1)
    assert attempt_counter == 4

    # Bails when the bail function is called
    attempt_counter = 0
    with pytest.raises(NonRetryableError):
        await HttpClientAsync._retry_with_exp_backoff(bails_on_third_attempt, backoff_base_millis=1)
    assert attempt_counter == 3

import time
from datetime import datetime, timezone
from typing import Any, Callable

from apify_client._utils import _parse_date_fields, _pluck_data, _retry_with_exp_backoff, _to_safe_id

import pytest


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
    assert _parse_date_fields({'a': {'b': {'c': {'createdAt': '2020-02-29T10:09:08.100Z'}}}}) == {'a': {'b': {'c': {'createdAt': expected_datetime}}}}

    # doesn't parse dates nested too deep
    expected_datetime = datetime(2020, 2, 29, 10, 9, 8, 100000, timezone.utc)
    assert _parse_date_fields({'a': {'b': {'c': {'d': {'createdAt': '2020-02-29T10:09:08.100Z'}}}}}) \
        == {'a': {'b': {'c': {'d': {'createdAt': '2020-02-29T10:09:08.100Z'}}}}}

    # doesn't die when the date can't be parsed
    assert _parse_date_fields({'createdAt': 'NOT_A_DATE'}) == {'createdAt': 'NOT_A_DATE'}


def test__pluck_data() -> None:
    # TODO implement
    assert _pluck_data({'data': {}}) == {}


def test__retry_with_exp_backoff() -> None:
    attempt_counter = 0

    class RetryableException(Exception):
        pass

    class BailException(Exception):
        pass

    def returns_on_fifth_attempt(bail: Callable, attempt: int) -> Any:
        nonlocal attempt_counter
        attempt_counter += 1

        if attempt == 5:
            return 'SUCCESS'
        raise RetryableException()

    def bails_on_third_attempt(bail: Callable, attempt: int) -> Any:
        nonlocal attempt_counter
        attempt_counter += 1

        if attempt == 3:
            bail(BailException())
        raise RetryableException()

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
    with pytest.raises(RetryableException):
        _retry_with_exp_backoff(returns_on_fifth_attempt, max_retries=4, backoff_base_millis=1)
    assert attempt_counter == 4

    # Bails when the bail function is called
    attempt_counter = 0
    with pytest.raises(BailException):
        _retry_with_exp_backoff(bails_on_third_attempt, backoff_base_millis=1)
    assert attempt_counter == 3

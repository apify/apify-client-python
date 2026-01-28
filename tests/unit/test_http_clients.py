import time
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any
from unittest.mock import Mock

import impit
import pytest

from apify_client._config import ClientConfig
from apify_client._http_clients import HttpClient, HttpClientAsync
from apify_client._http_clients._base import BaseHttpClient
from apify_client._statistics import ClientStatistics
from apify_client.errors import InvalidResponseBodyError


def test_retry_with_exp_backoff() -> None:
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


async def test_retry_with_exp_backoff_async() -> None:
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


def test_base_http_client_initialization() -> None:
    """Test BaseHttpClient initialization with various configurations."""
    config = ClientConfig.from_user_params(
        token='test_token',
        api_url='https://api.test.com',
        timeout_secs=30,
        max_retries=5,
    )
    statistics = ClientStatistics()

    client = BaseHttpClient(config=config, statistics=statistics)

    assert client._config == config
    assert client._statistics == statistics
    assert isinstance(client.impit_client, impit.Client)
    assert isinstance(client.impit_async_client, impit.AsyncClient)

    # Test without statistics (should create default)
    client2 = BaseHttpClient(config=config)
    assert isinstance(client2._statistics, ClientStatistics)


def test_base_http_client_creates_impit_clients() -> None:
    """Test that BaseHttpClient creates impit clients correctly."""
    config = ClientConfig.from_user_params(token='test_token_123')
    client = BaseHttpClient(config=config)

    # Check that impit clients are created
    assert client.impit_client is not None
    assert client.impit_async_client is not None
    assert isinstance(client.impit_client, impit.Client)
    assert isinstance(client.impit_async_client, impit.AsyncClient)


def test_parse_params_none() -> None:
    """Test _parse_params with None input."""
    assert BaseHttpClient._parse_params(None) is None


def test_parse_params_boolean() -> None:
    """Test _parse_params converts booleans to integers."""
    result = BaseHttpClient._parse_params({'flag': True, 'disabled': False})
    assert result == {'flag': 1, 'disabled': 0}


def test_parse_params_list() -> None:
    """Test _parse_params converts lists to comma-separated strings."""
    result = BaseHttpClient._parse_params({'ids': ['id1', 'id2', 'id3']})
    assert result == {'ids': 'id1,id2,id3'}


def test_parse_params_datetime() -> None:
    """Test _parse_params converts datetime to Zulu format."""
    dt = datetime(2024, 1, 15, 10, 30, 45, 123000, tzinfo=timezone.utc)
    result = BaseHttpClient._parse_params({'created_at': dt})
    assert result == {'created_at': '2024-01-15T10:30:45.123Z'}


def test_parse_params_none_values_filtered() -> None:
    """Test _parse_params filters out None values."""
    result = BaseHttpClient._parse_params({'a': 1, 'b': None, 'c': 'value'})
    assert result == {'a': 1, 'c': 'value'}


def test_parse_params_mixed() -> None:
    """Test _parse_params with mixed types."""
    dt = datetime(2024, 1, 15, 10, 30, 45, 123000, tzinfo=timezone.utc)
    result = BaseHttpClient._parse_params(
        {
            'limit': 10,
            'offset': 0,
            'flag': True,
            'tags': ['tag1', 'tag2'],
            'created_at': dt,
            'name': 'test',
            'empty': None,
        }
    )
    assert result == {
        'limit': 10,
        'offset': 0,
        'flag': 1,
        'tags': 'tag1,tag2',
        'created_at': '2024-01-15T10:30:45.123Z',
        'name': 'test',
    }


def test_is_retryable_error() -> None:
    """Test _is_retryable_error correctly identifies retryable errors."""
    mock_response = Mock()
    assert BaseHttpClient._is_retryable_error(InvalidResponseBodyError(mock_response))
    assert BaseHttpClient._is_retryable_error(impit.NetworkError('test'))
    assert BaseHttpClient._is_retryable_error(impit.TimeoutException('test'))
    assert BaseHttpClient._is_retryable_error(impit.RemoteProtocolError('test'))

    # Non-retryable errors
    assert not BaseHttpClient._is_retryable_error(ValueError('test'))
    assert not BaseHttpClient._is_retryable_error(RuntimeError('test'))
    assert not BaseHttpClient._is_retryable_error(Exception('test'))


def test_prepare_request_call_basic() -> None:
    """Test _prepare_request_call with basic parameters."""
    config = ClientConfig.from_user_params()
    client = BaseHttpClient(config=config)

    headers, params, data = client._prepare_request_call()
    assert headers == {}
    assert params is None
    assert data is None


def test_prepare_request_call_with_json() -> None:
    """Test _prepare_request_call with JSON data."""
    config = ClientConfig.from_user_params()
    client = BaseHttpClient(config=config)

    json_data = {'key': 'value', 'number': 42}
    headers, _params, data = client._prepare_request_call(json=json_data)

    assert headers['Content-Type'] == 'application/json'
    assert headers['Content-Encoding'] == 'gzip'
    assert data is not None
    assert isinstance(data, bytes)


def test_prepare_request_call_with_string_data() -> None:
    """Test _prepare_request_call with string data."""
    config = ClientConfig.from_user_params()
    client = BaseHttpClient(config=config)

    headers, _params, data = client._prepare_request_call(data='test string')

    assert headers['Content-Encoding'] == 'gzip'
    assert isinstance(data, bytes)


def test_prepare_request_call_with_bytes_data() -> None:
    """Test _prepare_request_call with bytes data."""
    config = ClientConfig.from_user_params()
    client = BaseHttpClient(config=config)

    headers, _params, data = client._prepare_request_call(data=b'test bytes')

    assert headers['Content-Encoding'] == 'gzip'
    assert isinstance(data, bytes)


def test_prepare_request_call_json_and_data_error() -> None:
    """Test _prepare_request_call raises error when both json and data are provided."""
    config = ClientConfig.from_user_params()
    client = BaseHttpClient(config=config)

    with pytest.raises(ValueError, match='Cannot pass both "json" and "data" parameters'):
        client._prepare_request_call(json={'key': 'value'}, data='string')


def test_prepare_request_call_with_params() -> None:
    """Test _prepare_request_call parses params correctly."""
    config = ClientConfig.from_user_params()
    client = BaseHttpClient(config=config)

    _headers, params, _data = client._prepare_request_call(params={'limit': 10, 'flag': True})

    assert params == {'limit': 10, 'flag': 1}


def test_build_url_with_params_none() -> None:
    """Test _build_url_with_params with None params."""
    config = ClientConfig.from_user_params()
    client = BaseHttpClient(config=config)

    url = client._build_url_with_params('https://api.test.com/endpoint')
    assert url == 'https://api.test.com/endpoint'


def test_build_url_with_params_simple() -> None:
    """Test _build_url_with_params with simple params."""
    config = ClientConfig.from_user_params()
    client = BaseHttpClient(config=config)

    url = client._build_url_with_params('https://api.test.com/endpoint', {'key': 'value', 'limit': 10})
    assert 'key=value' in url
    assert 'limit=10' in url
    assert url.startswith('https://api.test.com/endpoint?')


def test_build_url_with_params_list() -> None:
    """Test _build_url_with_params with list values."""
    config = ClientConfig.from_user_params()
    client = BaseHttpClient(config=config)

    url = client._build_url_with_params('https://api.test.com/endpoint', {'tags': ['tag1', 'tag2', 'tag3']})
    assert 'tags=tag1' in url
    assert 'tags=tag2' in url
    assert 'tags=tag3' in url


def test_build_url_with_params_mixed() -> None:
    """Test _build_url_with_params with mixed param types."""
    config = ClientConfig.from_user_params()
    client = BaseHttpClient(config=config)

    url = client._build_url_with_params(
        'https://api.test.com/endpoint', {'limit': 10, 'tags': ['a', 'b'], 'name': 'test'}
    )
    assert 'limit=10' in url
    assert 'tags=a' in url
    assert 'tags=b' in url
    assert 'name=test' in url

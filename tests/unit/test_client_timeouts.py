from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any
from unittest.mock import Mock

import pytest
from impit import HTTPError, Response, TimeoutException

from apify_client._http_clients import ImpitHttpClient, ImpitHttpClientAsync

if TYPE_CHECKING:
    from collections.abc import Iterator


class EndOfTestError(Exception):
    """Custom exception that is raised after the relevant part of the code is executed to stop the test."""


@pytest.fixture
def patch_request(monkeypatch: pytest.MonkeyPatch) -> Iterator[list]:
    timeouts = []

    def mock_request(*_args: Any, **kwargs: Any) -> None:
        timeouts.append(kwargs.get('timeout'))
        raise EndOfTestError

    async def mock_request_async(*args: Any, **kwargs: Any) -> None:
        return mock_request(*args, **kwargs)

    monkeypatch.setattr('impit.Client.request', mock_request)
    monkeypatch.setattr('impit.AsyncClient.request', mock_request_async)
    yield timeouts
    monkeypatch.undo()


async def test_dynamic_timeout_async_client(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tests timeout values for request with retriable errors.

    Values should increase with each attempt, starting from initial call value and bounded by the client timeout value.
    """
    should_raise_error = iter((True, True, True, False))
    call_timeout = 1
    client_timeout = 5
    expected_timeouts = [call_timeout, 2, 4, client_timeout]
    retry_counter_mock = Mock()

    timeouts = []

    async def mock_request(*_args: Any, **kwargs: Any) -> Response:
        timeouts.append(kwargs.get('timeout'))
        retry_counter_mock()
        should_raise = next(should_raise_error)
        if should_raise:
            raise TimeoutException

        return Response(status_code=200)

    monkeypatch.setattr('impit.AsyncClient.request', mock_request)

    response = await ImpitHttpClientAsync(timeout=timedelta(seconds=client_timeout)).call(
        method='GET', url='http://placeholder.url/async_timeout', timeout=timedelta(seconds=call_timeout)
    )

    # Check that the retry counter was called the expected number of times
    # (4 times: 3 retries + 1 final successful call)
    assert retry_counter_mock.call_count == 4
    assert timeouts == expected_timeouts
    # Check that the response is successful
    assert response.status_code == 200


async def test_retry_on_http_error_async_client(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tests that bare impit.HTTPError (e.g. body decode errors) are retried.

    This reproduces the scenario where the HTTP response body is truncated mid-stream
    (e.g. "unexpected EOF during chunk size line"), which impit raises as a generic HTTPError.
    """
    should_raise_error = iter((True, True, False))
    retry_counter_mock = Mock()

    async def mock_request(*_args: Any, **_kwargs: Any) -> Response:
        retry_counter_mock()
        should_raise = next(should_raise_error)
        if should_raise:
            raise HTTPError('The internal HTTP library has thrown an error: unexpected EOF during chunk size line')

        return Response(status_code=200)

    monkeypatch.setattr('impit.AsyncClient.request', mock_request)

    response = await ImpitHttpClientAsync(timeout=timedelta(seconds=5)).call(
        method='GET', url='http://placeholder.url/http_error'
    )

    # 3 attempts: 2 failures + 1 success
    assert retry_counter_mock.call_count == 3
    assert response.status_code == 200


def test_dynamic_timeout_sync_client(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tests timeout values for request with retriable errors.

    Values should increase with each attempt, starting from initial call value and bounded by the client timeout value.
    """
    should_raise_error = iter((True, True, True, False))
    call_timeout = 1
    client_timeout = 5
    expected_timeouts = [call_timeout, 2, 4, client_timeout]
    retry_counter_mock = Mock()

    timeouts = []

    def mock_request(*_args: Any, **kwargs: Any) -> Response:
        timeouts.append(kwargs.get('timeout'))
        retry_counter_mock()
        should_raise = next(should_raise_error)
        if should_raise:
            raise TimeoutException

        return Response(status_code=200)

    monkeypatch.setattr('impit.Client.request', mock_request)

    response = ImpitHttpClient(timeout=timedelta(seconds=client_timeout)).call(
        method='GET', url='http://placeholder.url/sync_timeout', timeout=timedelta(seconds=call_timeout)
    )

    # Check that the retry counter was called the expected number of times
    # (4 times: 3 retries + 1 final successful call)
    assert retry_counter_mock.call_count == 4
    assert timeouts == expected_timeouts
    # Check that the response is successful
    assert response.status_code == 200

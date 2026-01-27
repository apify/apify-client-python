from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import Mock

import pytest
from impit import Response, TimeoutException

from apify_client._config import DEFAULT_TIMEOUT, ClientConfig
from apify_client._consts import FAST_OPERATION_TIMEOUT_SECS, STANDARD_OPERATION_TIMEOUT_SECS
from apify_client._http_client import HttpClient, HttpClientAsync
from apify_client._resource_clients import (
    DatasetClient,
    KeyValueStoreClient,
    RequestQueueClient,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

    from pytest_httpserver import HTTPServer


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

    config = ClientConfig.from_user_params(timeout_secs=client_timeout)
    response = await HttpClientAsync(config=config).call(
        method='GET', url='http://placeholder.url/async_timeout', timeout_secs=call_timeout
    )

    # Check that the retry counter was called the expected number of times
    # (4 times: 3 retries + 1 final successful call)
    assert retry_counter_mock.call_count == 4
    assert timeouts == expected_timeouts
    # Check that the response is successful
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

    config = ClientConfig.from_user_params(timeout_secs=client_timeout)
    response = HttpClient(config=config).call(
        method='GET', url='http://placeholder.url/sync_timeout', timeout_secs=call_timeout
    )

    # Check that the retry counter was called the expected number of times
    # (4 times: 3 retries + 1 final successful call)
    assert retry_counter_mock.call_count == 4
    assert timeouts == expected_timeouts
    # Check that the response is successful
    assert response.status_code == 200


_timeout_params = [
    (DatasetClient, 'get', FAST_OPERATION_TIMEOUT_SECS, {}),
    (DatasetClient, 'update', FAST_OPERATION_TIMEOUT_SECS, {}),
    (DatasetClient, 'delete', FAST_OPERATION_TIMEOUT_SECS, {}),
    (DatasetClient, 'list_items', DEFAULT_TIMEOUT, {}),
    (DatasetClient, 'get_items_as_bytes', DEFAULT_TIMEOUT, {}),
    (DatasetClient, 'push_items', STANDARD_OPERATION_TIMEOUT_SECS, {'items': {}}),
    (DatasetClient, 'get_statistics', FAST_OPERATION_TIMEOUT_SECS, {}),
    (KeyValueStoreClient, 'get', FAST_OPERATION_TIMEOUT_SECS, {}),
    (KeyValueStoreClient, 'update', DEFAULT_TIMEOUT, {}),
    (KeyValueStoreClient, 'delete', FAST_OPERATION_TIMEOUT_SECS, {}),
    (KeyValueStoreClient, 'list_keys', STANDARD_OPERATION_TIMEOUT_SECS, {}),
    (KeyValueStoreClient, 'get_record', DEFAULT_TIMEOUT, {'key': 'some_key'}),
    (KeyValueStoreClient, 'get_record_as_bytes', DEFAULT_TIMEOUT, {'key': 'some_key'}),
    (KeyValueStoreClient, 'set_record', DEFAULT_TIMEOUT, {'key': 'some_key', 'value': 'some_value'}),
    (KeyValueStoreClient, 'delete_record', FAST_OPERATION_TIMEOUT_SECS, {'key': 'some_key'}),
    (RequestQueueClient, 'get', FAST_OPERATION_TIMEOUT_SECS, {}),
    (RequestQueueClient, 'update', FAST_OPERATION_TIMEOUT_SECS, {}),
    (RequestQueueClient, 'delete', FAST_OPERATION_TIMEOUT_SECS, {}),
    (RequestQueueClient, 'list_head', FAST_OPERATION_TIMEOUT_SECS, {}),
    (RequestQueueClient, 'list_and_lock_head', STANDARD_OPERATION_TIMEOUT_SECS, {'lock_secs': 1}),
    (RequestQueueClient, 'add_request', FAST_OPERATION_TIMEOUT_SECS, {'request': {}}),
    (RequestQueueClient, 'get_request', FAST_OPERATION_TIMEOUT_SECS, {'request_id': 'some_id'}),
    (RequestQueueClient, 'update_request', STANDARD_OPERATION_TIMEOUT_SECS, {'request': {'id': 123}}),
    (RequestQueueClient, 'delete_request', FAST_OPERATION_TIMEOUT_SECS, {'request_id': 123}),
    (RequestQueueClient, 'prolong_request_lock', STANDARD_OPERATION_TIMEOUT_SECS, {'request_id': 123, 'lock_secs': 1}),
    (RequestQueueClient, 'delete_request_lock', FAST_OPERATION_TIMEOUT_SECS, {'request_id': 123}),
    (RequestQueueClient, 'batch_add_requests', STANDARD_OPERATION_TIMEOUT_SECS, {'requests': [{}]}),
    (RequestQueueClient, 'batch_delete_requests', FAST_OPERATION_TIMEOUT_SECS, {'requests': [{}]}),
    (RequestQueueClient, 'list_requests', STANDARD_OPERATION_TIMEOUT_SECS, {}),
]


# This test will probably need to be reworked or skipped when switching to `impit`.
# Without the mock library, it's difficult to reproduce, maybe with monkeypatch?
@pytest.mark.parametrize(
    ('client_type', 'method', 'expected_timeout', 'kwargs'),
    _timeout_params,
)
def test_specific_timeouts_for_specific_endpoints_sync(
    client_type: type[DatasetClient | KeyValueStoreClient | RequestQueueClient],
    method: str,
    kwargs: dict,
    expected_timeout: int,
    patch_request: list[float | None],
    httpserver: HTTPServer,
) -> None:
    httpserver.expect_request('/').respond_with_data(status=200)
    config = ClientConfig.from_user_params()
    http_client = HttpClient(config=config)
    base_url = httpserver.url_for('/')
    # Determine resource_path based on client type
    if client_type == DatasetClient:
        resource_path = 'datasets/test-id'
    elif client_type == KeyValueStoreClient:
        resource_path = 'key-value-stores/test-id'
    elif client_type == RequestQueueClient:
        resource_path = 'request-queues/test-id'
    else:
        resource_path = 'resource/test-id'

    client = client_type(
        base_url=base_url,
        public_base_url=base_url,
        http_client=http_client,
        resource_path=resource_path,
        resource_id='test-id',
    )
    with pytest.raises(EndOfTestError):
        getattr(client, method)(**kwargs)

    assert len(patch_request) == 1
    assert patch_request[0] == expected_timeout


# This test will probably need to be reworked or skipped when switching to `impit`.
# Without the mock library, it's difficult to reproduce, maybe with monkeypatch?
@pytest.mark.parametrize(
    ('client_type', 'method', 'expected_timeout', 'kwargs'),
    _timeout_params,
)
async def test_specific_timeouts_for_specific_endpoints_async(
    client_type: type[DatasetClient | KeyValueStoreClient | RequestQueueClient],
    method: str,
    kwargs: dict,
    expected_timeout: int,
    patch_request: list[float | None],
    httpserver: HTTPServer,
) -> None:
    httpserver.expect_request('/').respond_with_data(status=200)
    config = ClientConfig.from_user_params()
    http_client = HttpClient(config=config)
    base_url = httpserver.url_for('/')
    # Determine resource_path based on client type
    if client_type == DatasetClient:
        resource_path = 'datasets/test-id'
    elif client_type == KeyValueStoreClient:
        resource_path = 'key-value-stores/test-id'
    elif client_type == RequestQueueClient:
        resource_path = 'request-queues/test-id'
    else:
        resource_path = 'resource/test-id'

    client = client_type(
        base_url=base_url,
        public_base_url=base_url,
        http_client=http_client,
        resource_path=resource_path,
        resource_id='test-id',
    )
    with pytest.raises(EndOfTestError):
        await getattr(client, method)(**kwargs)

    assert len(patch_request) == 1
    assert patch_request[0] == expected_timeout

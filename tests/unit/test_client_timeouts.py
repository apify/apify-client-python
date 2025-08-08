from __future__ import annotations

import time
from functools import partial
from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest
import respx
from werkzeug import Response as WerkzeugResponse

from apify_client import ApifyClient
from apify_client._http_client import HTTPClient, HTTPClientAsync
from apify_client.client import DEFAULT_TIMEOUT
from apify_client.clients import DatasetClient, KeyValueStoreClient, RequestQueueClient
from apify_client.clients.resource_clients import dataset, request_queue
from apify_client.clients.resource_clients import key_value_store as kvs

if TYPE_CHECKING:
    from httpx import Request, Response
    from pytest_httpserver import HTTPServer
    from werkzeug import Request as WerkzeugRequest


class EndOfTestError(Exception):
    """Custom exception that is raised after the relevant part of the code is executed to stop the test."""


async def test_dynamic_timeout_async_client(httpserver: HTTPServer) -> None:
    """Tests timeout values for request with retriable errors.

    Values should increase with each attempt, starting from initial call value and bounded by the client timeout value.
    """
    should_raise_error = iter((True, True, True, False))
    call_timeout = 1
    client_timeout = 5
    expected_timeouts = iter((call_timeout, 2, 4, client_timeout))
    retry_counter_mock = Mock()

    def slow_handler(_request: WerkzeugRequest) -> WerkzeugResponse:
        timeout = next(expected_timeouts)
        should_raise = next(should_raise_error)
        # Counter for retries
        retry_counter_mock()

        if should_raise:
            # We expect longer than the client is willing to wait. This will cause a timeout on the client side.
            time.sleep(timeout + 0.02)

        return WerkzeugResponse('200 OK')

    httpserver.expect_request('/async_timeout', method='GET').respond_with_handler(slow_handler)

    server_url = str(httpserver.url_for('/async_timeout'))
    response = await HTTPClientAsync(timeout_secs=client_timeout).call(
        method='GET', url=server_url, timeout_secs=call_timeout
    )

    # Check that the retry counter was called the expected number of times
    # (4 times: 3 retries + 1 final successful call)
    assert retry_counter_mock.call_count == 4
    # Check that the response is successful
    assert response.status_code == 200


def test_dynamic_timeout_sync_client(httpserver: HTTPServer) -> None:
    """Tests timeout values for request with retriable errors.

    Values should increase with each attempt, starting from initial call value and bounded by the client timeout value.
    """
    should_raise_error = iter((True, True, True, False))
    call_timeout = 1
    client_timeout = 5
    expected_timeouts = iter((call_timeout, 2, 4, client_timeout))
    retry_counter_mock = Mock()

    def slow_handler(_request: WerkzeugRequest) -> WerkzeugResponse:
        timeout = next(expected_timeouts)
        should_raise = next(should_raise_error)
        # Counter for retries
        retry_counter_mock()

        if should_raise:
            # We expect longer than the client is willing to wait. This will cause a timeout on the client side.
            time.sleep(timeout + 0.02)

        return WerkzeugResponse('200 OK')

    httpserver.expect_request('/sync_timeout', method='GET').respond_with_handler(slow_handler)

    server_url = str(httpserver.url_for('/sync_timeout'))

    response = HTTPClient(timeout_secs=client_timeout).call(method='GET', url=server_url, timeout_secs=call_timeout)

    # Check that the retry counter was called the expected number of times
    # (4 times: 3 retries + 1 final successful call)
    assert retry_counter_mock.call_count == 4
    # Check that the response is successful
    assert response.status_code == 200


def assert_timeout(expected_timeout: int, request: Request) -> Response:
    """Assert that correct timeouts are set on the request and raise `EndOfTestError`.

    This is intended for tests that are only testing timeout value and further execution of the code is not desired.
    """
    assert request.extensions['timeout'] == {
        'connect': expected_timeout,
        'pool': expected_timeout,
        'read': expected_timeout,
        'write': expected_timeout,
    }
    raise EndOfTestError


_timeout_params = [
    (DatasetClient, 'get', dataset._SMALL_TIMEOUT, {}),
    (DatasetClient, 'update', dataset._SMALL_TIMEOUT, {}),
    (DatasetClient, 'delete', dataset._SMALL_TIMEOUT, {}),
    (DatasetClient, 'list_items', DEFAULT_TIMEOUT, {}),
    (DatasetClient, 'download_items', DEFAULT_TIMEOUT, {}),
    (DatasetClient, 'get_items_as_bytes', DEFAULT_TIMEOUT, {}),
    (DatasetClient, 'push_items', dataset._MEDIUM_TIMEOUT, {'items': {}}),
    (DatasetClient, 'get_statistics', dataset._SMALL_TIMEOUT, {}),
    (KeyValueStoreClient, 'get', kvs._SMALL_TIMEOUT, {}),
    (KeyValueStoreClient, 'update', DEFAULT_TIMEOUT, {}),
    (KeyValueStoreClient, 'delete', kvs._SMALL_TIMEOUT, {}),
    (KeyValueStoreClient, 'list_keys', kvs._MEDIUM_TIMEOUT, {}),
    (KeyValueStoreClient, 'get_record', DEFAULT_TIMEOUT, {'key': 'some_key'}),
    (KeyValueStoreClient, 'get_record_as_bytes', DEFAULT_TIMEOUT, {'key': 'some_key'}),
    (KeyValueStoreClient, 'set_record', DEFAULT_TIMEOUT, {'key': 'some_key', 'value': 'some_value'}),
    (KeyValueStoreClient, 'delete_record', kvs._SMALL_TIMEOUT, {'key': 'some_key'}),
    (RequestQueueClient, 'get', request_queue._SMALL_TIMEOUT, {}),
    (RequestQueueClient, 'update', request_queue._SMALL_TIMEOUT, {}),
    (RequestQueueClient, 'delete', request_queue._SMALL_TIMEOUT, {}),
    (RequestQueueClient, 'list_head', request_queue._SMALL_TIMEOUT, {}),
    (RequestQueueClient, 'list_and_lock_head', request_queue._MEDIUM_TIMEOUT, {'lock_secs': 1}),
    (RequestQueueClient, 'add_request', request_queue._SMALL_TIMEOUT, {'request': {}}),
    (RequestQueueClient, 'get_request', request_queue._SMALL_TIMEOUT, {'request_id': 'some_id'}),
    (RequestQueueClient, 'update_request', request_queue._MEDIUM_TIMEOUT, {'request': {'id': 123}}),
    (RequestQueueClient, 'delete_request', request_queue._SMALL_TIMEOUT, {'request_id': 123}),
    (RequestQueueClient, 'prolong_request_lock', request_queue._MEDIUM_TIMEOUT, {'request_id': 123, 'lock_secs': 1}),
    (RequestQueueClient, 'delete_request_lock', request_queue._SMALL_TIMEOUT, {'request_id': 123}),
    (RequestQueueClient, 'batch_add_requests', request_queue._MEDIUM_TIMEOUT, {'requests': [{}]}),
    (RequestQueueClient, 'batch_delete_requests', request_queue._SMALL_TIMEOUT, {'requests': [{}]}),
    (RequestQueueClient, 'list_requests', request_queue._MEDIUM_TIMEOUT, {}),
]


# This test will probably need to be reworked or skipped when switching to `impit`.
# Without the mock library, it's difficult to reproduce, maybe with monkeypatch?
@pytest.mark.parametrize(
    ('client_type', 'method', 'expected_timeout', 'kwargs'),
    _timeout_params,
)
@respx.mock
def test_specific_timeouts_for_specific_endpoints_sync(
    client_type: type[DatasetClient | KeyValueStoreClient | RequestQueueClient],
    method: str,
    kwargs: dict,
    expected_timeout: int,
) -> None:
    respx.route(host='example.com').mock(side_effect=partial(assert_timeout, expected_timeout))
    client = client_type(base_url='https://example.com', root_client=ApifyClient(), http_client=HTTPClient())
    with pytest.raises(EndOfTestError):
        getattr(client, method)(**kwargs)


# This test will probably need to be reworked or skipped when switching to `impit`.
# Without the mock library, it's difficult to reproduce, maybe with monkeypatch?
@pytest.mark.parametrize(
    ('client_type', 'method', 'expected_timeout', 'kwargs'),
    _timeout_params,
)
@respx.mock
async def test_specific_timeouts_for_specific_endpoints_async(
    client_type: type[DatasetClient | KeyValueStoreClient | RequestQueueClient],
    method: str,
    kwargs: dict,
    expected_timeout: int,
) -> None:
    respx.route(host='example.com').mock(side_effect=partial(assert_timeout, expected_timeout))
    client = client_type(base_url='https://example.com', root_client=ApifyClient(), http_client=HTTPClient())
    with pytest.raises(EndOfTestError):
        await getattr(client, method)(**kwargs)

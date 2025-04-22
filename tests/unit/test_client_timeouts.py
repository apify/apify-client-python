from __future__ import annotations

from functools import partial

import pytest
import respx
from httpx import Request, Response, TimeoutException

from apify_client import ApifyClient
from apify_client._http_client import HTTPClient, HTTPClientAsync
from apify_client.client import DEFAULT_TIMEOUT
from apify_client.clients import DatasetClient, KeyValueStoreClient, RequestQueueClient
from apify_client.clients.resource_clients import dataset, request_queue
from apify_client.clients.resource_clients import key_value_store as kvs


class EndOfTestError(Exception):
    """Custom exception that is raised after the relevant part of the code is executed to stop the test."""


@respx.mock
async def test_dynamic_timeout_async_client() -> None:
    """Tests timeout values for request with retriable errors.

    Values should increase with each attempt, starting from initial call value and bounded by the client timeout value.
    """
    should_raise_error = iter((True, True, True, False))
    call_timeout = 1
    client_timeout = 5
    expected_timeouts = iter((call_timeout, 2, 4, client_timeout))

    def check_timeout(request: Request) -> Response:
        expected_timeout = next(expected_timeouts)
        assert request.extensions['timeout'] == {
            'connect': expected_timeout,
            'pool': expected_timeout,
            'read': expected_timeout,
            'write': expected_timeout,
        }
        if next(should_raise_error):
            raise TimeoutException('This error can be retried')
        return Response(200)

    respx.get('https://example.com').mock(side_effect=check_timeout)
    await HTTPClientAsync(timeout_secs=client_timeout).call(
        method='GET', url='https://example.com', timeout_secs=call_timeout
    )


@respx.mock
def test_dynamic_timeout_sync_client() -> None:
    """Tests timeout values for request with retriable errors.

    Values should increase with each attempt, starting from initial call value and bounded by the client timeout value.
    """
    should_raise_error = iter((True, True, True, False))
    call_timeout = 1
    client_timeout = 5
    expected_timeouts = iter((call_timeout, 2, 4, client_timeout))

    def check_timeout(request: Request) -> Response:
        expected_timeout = next(expected_timeouts)
        assert request.extensions['timeout'] == {
            'connect': expected_timeout,
            'pool': expected_timeout,
            'read': expected_timeout,
            'write': expected_timeout,
        }
        if next(should_raise_error):
            raise TimeoutException('This error can be retired')
        return Response(200)

    respx.get('https://example.com').mock(side_effect=check_timeout)
    HTTPClient(timeout_secs=client_timeout).call(method='GET', url='https://example.com', timeout_secs=call_timeout)


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

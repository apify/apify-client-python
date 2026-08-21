from __future__ import annotations

import gzip
import json
import re
from typing import TYPE_CHECKING

import pytest
from werkzeug.wrappers import Response

from apify_client import ApifyClient, ApifyClientAsync
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from collections.abc import Callable

    from pytest_httpserver import HTTPServer
    from werkzeug.wrappers import Request

    from apify_client._typeddicts import RequestDict, RequestDraftDict

# The Apify API limit on the payload size of a batch-add request, which the client's batching must respect.
_API_MAX_PAYLOAD_SIZE_BYTES = 9 * 1024 * 1024

_EMPTY_BATCH_RESPONSE_CONTENT = '{"data": {"processedRequests": [], "unprocessedRequests": []}}'

_PARTIALLY_ADDED_BATCH_RESPONSE_CONTENT = """{
  "data": {
    "processedRequests": [
      {
        "requestId": "YiKoxjkaS9gjGTqhF",
        "uniqueKey": "http://example.com/1",
        "wasAlreadyPresent": true,
        "wasAlreadyHandled": false
      }
    ],
    "unprocessedRequests": [
      {
        "uniqueKey": "http://example.com/2",
        "url": "http://example.com/2",
        "method": "GET"
      }
    ]
  }
}"""


async def test_batch_not_processed_raises_exception_async(httpserver: HTTPServer) -> None:
    """Test that client exceptions are not silently ignored"""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync(
        token='placeholder_token',
        api_url=server_url,
        api_public_url=server_url,
    )
    httpserver.expect_oneshot_request(re.compile(r'.*'), method='POST').respond_with_data(status=401)
    requests: list[RequestDraftDict] = [
        {'unique_key': 'http://example.com/1', 'url': 'http://example.com/1', 'method': 'GET'},
        {'unique_key': 'http://example.com/2', 'url': 'http://example.com/2', 'method': 'GET'},
    ]
    rq_client = client.request_queue(request_queue_id='whatever')

    with pytest.raises(ApifyApiError):
        await rq_client.batch_add_requests(requests=requests)


async def test_batch_processed_partially_async(httpserver: HTTPServer) -> None:
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync(
        token='placeholder_token',
        api_url=server_url,
        api_public_url=server_url,
    )

    httpserver.expect_oneshot_request(re.compile(r'.*'), method='POST').respond_with_data(
        status=200, response_data=_PARTIALLY_ADDED_BATCH_RESPONSE_CONTENT
    )
    requests: list[RequestDraftDict] = [
        {'unique_key': 'http://example.com/1', 'url': 'http://example.com/1', 'method': 'GET'},
        {'unique_key': 'http://example.com/2', 'url': 'http://example.com/2', 'method': 'GET'},
    ]
    rq_client = client.request_queue(request_queue_id='whatever')

    batch_response = await rq_client.batch_add_requests(requests=requests)
    assert requests[0]['unique_key'] in {request.unique_key for request in batch_response.processed_requests}
    assert len(batch_response.unprocessed_requests) == 1
    assert batch_response.unprocessed_requests[0].unique_key == requests[1]['unique_key']


def test_batch_not_processed_raises_exception_sync(httpserver: HTTPServer) -> None:
    """Test that client exceptions are not silently ignored"""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(
        token='placeholder_token',
        api_url=server_url,
        api_public_url=server_url,
    )

    httpserver.expect_oneshot_request(re.compile(r'.*'), method='POST').respond_with_data(status=401)
    requests: list[RequestDraftDict] = [
        {'unique_key': 'http://example.com/1', 'url': 'http://example.com/1', 'method': 'GET'},
        {'unique_key': 'http://example.com/2', 'url': 'http://example.com/2', 'method': 'GET'},
    ]
    rq_client = client.request_queue(request_queue_id='whatever')

    with pytest.raises(ApifyApiError):
        rq_client.batch_add_requests(requests=requests)


def _make_large_requests() -> list[RequestDraftDict]:
    """Return 3 requests of ~4 MB each, so that all of them together exceed the 9 MB payload limit."""
    return [
        {
            'unique_key': f'http://example.com/{i}',
            'url': f'http://example.com/{i}?filler={"x" * (4 * 1024 * 1024)}',
            'method': 'GET',
        }
        for i in range(3)
    ]


def _payload_capturing_handler(
    payloads: list[bytes],
    response_content: str = _EMPTY_BATCH_RESPONSE_CONTENT,
) -> Callable[[Request], Response]:
    """Return a handler that records each request body and responds with `response_content`.

    Bodies below the client's compression threshold arrive uncompressed, so the recorded payload is
    decompressed only when the request says it was encoded.
    """

    def handler(request: Request) -> Response:
        body = request.get_data()
        payloads.append(gzip.decompress(body) if request.headers.get('Content-Encoding') == 'gzip' else body)
        return Response(response_content, status=200, content_type='application/json')

    return handler


async def test_batch_add_requests_splits_batches_by_payload_size_async(httpserver: HTTPServer) -> None:
    """Test that batches are split by serialized byte size so no POST payload exceeds the 9 MB API limit."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync(
        token='placeholder_token',
        api_url=server_url,
        api_public_url=server_url,
    )

    payloads = list[bytes]()
    httpserver.expect_request(re.compile(r'.*'), method='POST').respond_with_handler(
        _payload_capturing_handler(payloads)
    )
    rq_client = client.request_queue(request_queue_id='whatever')

    await rq_client.batch_add_requests(requests=_make_large_requests())

    assert len(payloads) > 1
    assert all(len(payload) <= _API_MAX_PAYLOAD_SIZE_BYTES for payload in payloads)
    assert sum(len(json.loads(payload)) for payload in payloads) == 3


def test_batch_add_requests_splits_batches_by_payload_size_sync(httpserver: HTTPServer) -> None:
    """Test that batches are split by serialized byte size so no POST payload exceeds the 9 MB API limit."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(
        token='placeholder_token',
        api_url=server_url,
        api_public_url=server_url,
    )

    payloads = list[bytes]()
    httpserver.expect_request(re.compile(r'.*'), method='POST').respond_with_handler(
        _payload_capturing_handler(payloads)
    )
    rq_client = client.request_queue(request_queue_id='whatever')

    rq_client.batch_add_requests(requests=_make_large_requests())

    assert len(payloads) > 1
    assert all(len(payload) <= _API_MAX_PAYLOAD_SIZE_BYTES for payload in payloads)
    assert sum(len(json.loads(payload)) for payload in payloads) == 3


def _make_oversized_and_small_requests() -> list[RequestDraftDict]:
    """Return a small request plus one whose serialized size alone exceeds the 9 MB payload limit."""
    return [
        {'unique_key': 'small', 'url': 'http://example.com/small', 'method': 'GET'},
        {
            'unique_key': 'oversized',
            'url': f'http://example.com/oversized?filler={"x" * (10 * 1024 * 1024)}',
            'method': 'GET',
        },
    ]


async def test_batch_add_requests_sends_oversized_request_alone_async(httpserver: HTTPServer) -> None:
    """Test that a request exceeding the payload limit is sent in its own batch for the API to judge, not rejected."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync(
        token='placeholder_token',
        api_url=server_url,
        api_public_url=server_url,
    )

    payloads = list[bytes]()
    httpserver.expect_request(re.compile(r'.*'), method='POST').respond_with_handler(
        _payload_capturing_handler(payloads)
    )
    rq_client = client.request_queue(request_queue_id='whatever')

    await rq_client.batch_add_requests(requests=_make_oversized_and_small_requests())

    assert sum(len(json.loads(payload)) for payload in payloads) == 2
    assert any(len(payload) > _API_MAX_PAYLOAD_SIZE_BYTES for payload in payloads)


def test_batch_add_requests_sends_oversized_request_alone_sync(httpserver: HTTPServer) -> None:
    """Test that a request exceeding the payload limit is sent in its own batch for the API to judge, not rejected."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(
        token='placeholder_token',
        api_url=server_url,
        api_public_url=server_url,
    )

    payloads = list[bytes]()
    httpserver.expect_request(re.compile(r'.*'), method='POST').respond_with_handler(
        _payload_capturing_handler(payloads)
    )
    rq_client = client.request_queue(request_queue_id='whatever')

    rq_client.batch_add_requests(requests=_make_oversized_and_small_requests())

    assert sum(len(json.loads(payload)) for payload in payloads) == 2
    assert any(len(payload) > _API_MAX_PAYLOAD_SIZE_BYTES for payload in payloads)


def test_batch_processed_partially_sync(httpserver: HTTPServer) -> None:
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(
        token='placeholder_token',
        api_url=server_url,
        api_public_url=server_url,
    )

    httpserver.expect_oneshot_request(re.compile(r'.*'), method='POST').respond_with_data(
        status=200, response_data=_PARTIALLY_ADDED_BATCH_RESPONSE_CONTENT
    )
    requests: list[RequestDraftDict] = [
        {'unique_key': 'http://example.com/1', 'url': 'http://example.com/1', 'method': 'GET'},
        {'unique_key': 'http://example.com/2', 'url': 'http://example.com/2', 'method': 'GET'},
    ]
    rq_client = client.request_queue(request_queue_id='whatever')

    batch_response = rq_client.batch_add_requests(requests=requests)
    assert requests[0]['unique_key'] in {request.unique_key for request in batch_response.processed_requests}
    assert len(batch_response.unprocessed_requests) == 1
    assert batch_response.unprocessed_requests[0].unique_key == requests[1]['unique_key']


_REQUEST_REGISTRATION_RESPONSE_CONTENT = (
    '{"data": {"requestId": "YiKoxjkaS9gjGTqhF", "wasAlreadyPresent": false, "wasAlreadyHandled": false}}'
)

_FULL_REQUEST_DICT: RequestDict = {
    'id': 'YiKoxjkaS9gjGTqhF',
    'unique_key': 'http://example.com/1',
    'url': 'http://example.com/1',
    'method': 'GET',
    'user_data': {'label': 'DETAIL'},
    'no_retry': True,
    'retry_count': 2,
    'loaded_url': 'http://example.com/1/final',
    'headers': {'X-Test': 'value'},
    'payload': 'body',
    'error_messages': ['boom'],
    'handled_at': '2019-06-16T10:23:31.607Z',
}


async def test_add_request_matches_update_request_casing_async(httpserver: HTTPServer) -> None:
    """The same snake_case request dict reaches the API camelCased on add_request just as on update_request."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync(token='placeholder_token', api_url=server_url, api_public_url=server_url)

    payloads = list[bytes]()
    httpserver.expect_request(re.compile(r'.*')).respond_with_handler(
        _payload_capturing_handler(payloads, _REQUEST_REGISTRATION_RESPONSE_CONTENT)
    )
    rq_client = client.request_queue(request_queue_id='whatever')

    await rq_client.add_request(_FULL_REQUEST_DICT)
    await rq_client.update_request(_FULL_REQUEST_DICT)

    added, updated = (json.loads(payload) for payload in payloads)
    assert added == updated
    assert added['userData'] == {'label': 'DETAIL'}
    assert [key for key in added if '_' in key] == []


def test_add_request_matches_update_request_casing_sync(httpserver: HTTPServer) -> None:
    """The same snake_case request dict reaches the API camelCased on add_request just as on update_request."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(token='placeholder_token', api_url=server_url, api_public_url=server_url)

    payloads = list[bytes]()
    httpserver.expect_request(re.compile(r'.*')).respond_with_handler(
        _payload_capturing_handler(payloads, _REQUEST_REGISTRATION_RESPONSE_CONTENT)
    )
    rq_client = client.request_queue(request_queue_id='whatever')

    rq_client.add_request(_FULL_REQUEST_DICT)
    rq_client.update_request(_FULL_REQUEST_DICT)

    added, updated = (json.loads(payload) for payload in payloads)
    assert added == updated
    assert added['userData'] == {'label': 'DETAIL'}
    assert [key for key in added if '_' in key] == []


async def test_batch_add_requests_camel_cases_every_field_async(httpserver: HTTPServer) -> None:
    """Every field of a snake_case request dict is camelCased in the batch-add payload."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync(token='placeholder_token', api_url=server_url, api_public_url=server_url)

    payloads = list[bytes]()
    httpserver.expect_request(re.compile(r'.*'), method='POST').respond_with_handler(
        _payload_capturing_handler(payloads)
    )
    rq_client = client.request_queue(request_queue_id='whatever')

    await rq_client.batch_add_requests(requests=[_FULL_REQUEST_DICT])

    (sent_request,) = json.loads(payloads[0])
    assert sent_request['userData'] == {'label': 'DETAIL'}
    assert [key for key in sent_request if '_' in key] == []


def test_batch_add_requests_camel_cases_every_field_sync(httpserver: HTTPServer) -> None:
    """Every field of a snake_case request dict is camelCased in the batch-add payload."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(token='placeholder_token', api_url=server_url, api_public_url=server_url)

    payloads = list[bytes]()
    httpserver.expect_request(re.compile(r'.*'), method='POST').respond_with_handler(
        _payload_capturing_handler(payloads)
    )
    rq_client = client.request_queue(request_queue_id='whatever')

    rq_client.batch_add_requests(requests=[_FULL_REQUEST_DICT])

    (sent_request,) = json.loads(payloads[0])
    assert sent_request['userData'] == {'label': 'DETAIL'}
    assert [key for key in sent_request if '_' in key] == []

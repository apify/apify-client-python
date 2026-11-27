from __future__ import annotations

import gzip
import json
import logging
import random
import re
from datetime import timedelta
from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest
from pydantic import ValidationError
from werkzeug.wrappers import Response

from apify_client import ApifyClient, ApifyClientAsync
from apify_client._models import RequestToDelete
from apify_client._resource_clients.request_queue import _compute_retry_delay_seconds
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from collections.abc import Callable

    from pytest_httpserver import HTTPServer
    from werkzeug.wrappers import Request

    from apify_client._typeddicts import RequestResourceDict, RequestWithoutIdDict

# The Apify API limit on the payload size of a batch-add request, which the client's batching must respect.
pytestmark = pytest.mark.usefixtures('http_client_classes')

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
    requests: list[RequestWithoutIdDict] = [
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

    unprocessed_body = (
        '{"data": {"processedRequests": [], "unprocessedRequests": '
        '[{"uniqueKey": "http://example.com/2", "url": "http://example.com/2", "method": "GET"}]}}'
    )
    handler = Mock(
        side_effect=[
            Response(_PARTIALLY_ADDED_BATCH_RESPONSE_CONTENT, status=200, content_type='application/json'),
            *(Response(unprocessed_body, status=200, content_type='application/json') for _ in range(3)),
        ]
    )

    httpserver.expect_request(re.compile(r'.*'), method='POST').respond_with_handler(handler)
    requests: list[RequestWithoutIdDict] = [
        {'unique_key': 'http://example.com/1', 'url': 'http://example.com/1', 'method': 'GET'},
        {'unique_key': 'http://example.com/2', 'url': 'http://example.com/2', 'method': 'GET'},
    ]
    rq_client = client.request_queue(request_queue_id='whatever')

    batch_response = await rq_client.batch_add_requests(
        requests=requests,
        min_delay_between_unprocessed_requests_retries=timedelta(milliseconds=1),
    )
    assert handler.call_count == 4
    assert [request.unique_key for request in batch_response.processed_requests] == [requests[0]['unique_key']]
    assert len(batch_response.unprocessed_requests) == 1
    assert batch_response.unprocessed_requests[0].unique_key == requests[1]['unique_key']
    assert client.stats.rate_limit_errors == {0: 1, 1: 1, 2: 1, 3: 1}


def test_batch_not_processed_raises_exception_sync(httpserver: HTTPServer) -> None:
    """Test that client exceptions are not silently ignored"""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(
        token='placeholder_token',
        api_url=server_url,
        api_public_url=server_url,
    )

    httpserver.expect_oneshot_request(re.compile(r'.*'), method='POST').respond_with_data(status=401)
    requests: list[RequestWithoutIdDict] = [
        {'unique_key': 'http://example.com/1', 'url': 'http://example.com/1', 'method': 'GET'},
        {'unique_key': 'http://example.com/2', 'url': 'http://example.com/2', 'method': 'GET'},
    ]
    rq_client = client.request_queue(request_queue_id='whatever')

    with pytest.raises(ApifyApiError):
        rq_client.batch_add_requests(requests=requests)


def _make_large_requests() -> list[RequestWithoutIdDict]:
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


def _make_oversized_and_small_requests() -> list[RequestWithoutIdDict]:
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

    unprocessed_body = (
        '{"data": {"processedRequests": [], "unprocessedRequests": '
        '[{"uniqueKey": "http://example.com/2", "url": "http://example.com/2", "method": "GET"}]}}'
    )
    handler = Mock(
        side_effect=[
            Response(_PARTIALLY_ADDED_BATCH_RESPONSE_CONTENT, status=200, content_type='application/json'),
            *(Response(unprocessed_body, status=200, content_type='application/json') for _ in range(3)),
        ]
    )

    httpserver.expect_request(re.compile(r'.*'), method='POST').respond_with_handler(handler)
    requests: list[RequestWithoutIdDict] = [
        {'unique_key': 'http://example.com/1', 'url': 'http://example.com/1', 'method': 'GET'},
        {'unique_key': 'http://example.com/2', 'url': 'http://example.com/2', 'method': 'GET'},
    ]
    rq_client = client.request_queue(request_queue_id='whatever')

    batch_response = rq_client.batch_add_requests(
        requests=requests,
        min_delay_between_unprocessed_requests_retries=timedelta(milliseconds=1),
    )
    assert handler.call_count == 4
    assert [request.unique_key for request in batch_response.processed_requests] == [requests[0]['unique_key']]
    assert len(batch_response.unprocessed_requests) == 1
    assert batch_response.unprocessed_requests[0].unique_key == requests[1]['unique_key']
    assert client.stats.rate_limit_errors == {0: 1, 1: 1, 2: 1, 3: 1}


def _progressive_retry_handler(sent_keys: list[list[str]]) -> Mock:
    """Return a mock handler that processes one request per round across 3 rounds."""
    handler = Mock()

    def respond(request: Request) -> Response:
        round_num = handler.call_count
        body = request.get_data()
        raw = gzip.decompress(body) if request.headers.get('Content-Encoding') == 'gzip' else body
        items = json.loads(raw)
        sent_keys.append([item['uniqueKey'] for item in items])

        processed = [
            {
                'requestId': f'id_{round_num}',
                'uniqueKey': f'http://example.com/{round_num}',
                'wasAlreadyPresent': False,
                'wasAlreadyHandled': False,
            }
        ]
        unprocessed = [
            {'uniqueKey': f'http://example.com/{k}', 'url': f'http://example.com/{k}', 'method': 'GET'}
            for k in range(round_num + 1, 4)
        ]
        return Response(
            json.dumps({'data': {'processedRequests': processed, 'unprocessedRequests': unprocessed}}),
            status=200,
            content_type='application/json',
        )

    handler.side_effect = respond
    return handler


async def test_batch_add_requests_retries_unprocessed_requests_async(httpserver: HTTPServer) -> None:
    """Unprocessed requests are retried by `unique_key` until processed and rate limits are tracked."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync(token='placeholder_token', api_url=server_url, api_public_url=server_url)

    sent_keys = list[list[str]]()
    httpserver.expect_request(re.compile(r'.*'), method='POST').respond_with_handler(
        _progressive_retry_handler(sent_keys)
    )
    requests: list[RequestWithoutIdDict] = [
        {'unique_key': f'http://example.com/{i}', 'url': f'http://example.com/{i}', 'method': 'GET'}
        for i in range(1, 4)
    ]
    rq_client = client.request_queue(request_queue_id='whatever')

    result = await rq_client.batch_add_requests(
        requests=requests,
        min_delay_between_unprocessed_requests_retries=timedelta(milliseconds=1),
    )

    assert sent_keys == [
        ['http://example.com/1', 'http://example.com/2', 'http://example.com/3'],
        ['http://example.com/2', 'http://example.com/3'],
        ['http://example.com/3'],
    ]
    assert [req.unique_key for req in result.processed_requests] == [
        'http://example.com/1',
        'http://example.com/2',
        'http://example.com/3',
    ]
    assert result.unprocessed_requests == []
    assert client.stats.rate_limit_errors == {0: 1, 1: 1}


def test_batch_add_requests_retries_unprocessed_requests_sync(httpserver: HTTPServer) -> None:
    """Unprocessed requests are retried by `unique_key` until processed and rate limits are tracked."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(token='placeholder_token', api_url=server_url, api_public_url=server_url)

    sent_keys = list[list[str]]()
    httpserver.expect_request(re.compile(r'.*'), method='POST').respond_with_handler(
        _progressive_retry_handler(sent_keys)
    )
    requests: list[RequestWithoutIdDict] = [
        {'unique_key': f'http://example.com/{i}', 'url': f'http://example.com/{i}', 'method': 'GET'}
        for i in range(1, 4)
    ]
    rq_client = client.request_queue(request_queue_id='whatever')

    result = rq_client.batch_add_requests(
        requests=requests,
        min_delay_between_unprocessed_requests_retries=timedelta(milliseconds=1),
    )

    assert sent_keys == [
        ['http://example.com/1', 'http://example.com/2', 'http://example.com/3'],
        ['http://example.com/2', 'http://example.com/3'],
        ['http://example.com/3'],
    ]
    assert [req.unique_key for req in result.processed_requests] == [
        'http://example.com/1',
        'http://example.com/2',
        'http://example.com/3',
    ]
    assert result.unprocessed_requests == []
    assert client.stats.rate_limit_errors == {0: 1, 1: 1}


async def test_batch_add_requests_zero_retries_async(httpserver: HTTPServer) -> None:
    """Setting `max_unprocessed_requests_retries=0` sends one call and returns unprocessed requests without retrying."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync(token='placeholder_token', api_url=server_url, api_public_url=server_url)

    handler = Mock(
        return_value=Response(_PARTIALLY_ADDED_BATCH_RESPONSE_CONTENT, status=200, content_type='application/json')
    )
    httpserver.expect_request(re.compile(r'.*'), method='POST').respond_with_handler(handler)
    requests: list[RequestWithoutIdDict] = [
        {'unique_key': 'http://example.com/1', 'url': 'http://example.com/1', 'method': 'GET'},
        {'unique_key': 'http://example.com/2', 'url': 'http://example.com/2', 'method': 'GET'},
    ]
    rq_client = client.request_queue(request_queue_id='whatever')

    result = await rq_client.batch_add_requests(requests=requests, max_unprocessed_requests_retries=0)

    assert handler.call_count == 1
    assert [req.unique_key for req in result.processed_requests] == ['http://example.com/1']
    assert [req.unique_key for req in result.unprocessed_requests] == ['http://example.com/2']
    assert client.stats.rate_limit_errors == {0: 1}


def test_batch_add_requests_zero_retries_sync(httpserver: HTTPServer) -> None:
    """Setting `max_unprocessed_requests_retries=0` sends one call and returns unprocessed requests without retrying."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(token='placeholder_token', api_url=server_url, api_public_url=server_url)

    handler = Mock(
        return_value=Response(_PARTIALLY_ADDED_BATCH_RESPONSE_CONTENT, status=200, content_type='application/json')
    )
    httpserver.expect_request(re.compile(r'.*'), method='POST').respond_with_handler(handler)
    requests: list[RequestWithoutIdDict] = [
        {'unique_key': 'http://example.com/1', 'url': 'http://example.com/1', 'method': 'GET'},
        {'unique_key': 'http://example.com/2', 'url': 'http://example.com/2', 'method': 'GET'},
    ]
    rq_client = client.request_queue(request_queue_id='whatever')

    result = rq_client.batch_add_requests(requests=requests, max_unprocessed_requests_retries=0)

    assert handler.call_count == 1
    assert [req.unique_key for req in result.processed_requests] == ['http://example.com/1']
    assert [req.unique_key for req in result.unprocessed_requests] == ['http://example.com/2']
    assert client.stats.rate_limit_errors == {0: 1}


@pytest.mark.parametrize(
    ('max_retries', 'min_delay'),
    [
        pytest.param(-1, timedelta(milliseconds=500), id='negative_retries'),
        pytest.param(3, timedelta(milliseconds=-1), id='negative_min_delay'),
    ],
)
async def test_batch_add_requests_invalid_retry_params_async(
    max_retries: int,
    min_delay: timedelta,
) -> None:
    """Negative retry count or minimum delay raises `ValueError` in the async client."""
    client = ApifyClientAsync(token='placeholder_token')
    rq_client = client.request_queue(request_queue_id='whatever')
    requests: list[RequestWithoutIdDict] = [
        {'unique_key': 'http://example.com/1', 'url': 'http://example.com/1', 'method': 'GET'},
    ]

    with pytest.raises(ValueError, match='must be non-negative'):
        await rq_client.batch_add_requests(
            requests=requests,
            max_unprocessed_requests_retries=max_retries,
            min_delay_between_unprocessed_requests_retries=min_delay,
        )


@pytest.mark.parametrize(
    ('max_retries', 'min_delay'),
    [
        pytest.param(-1, timedelta(milliseconds=500), id='negative_retries'),
        pytest.param(3, timedelta(milliseconds=-1), id='negative_min_delay'),
    ],
)
def test_batch_add_requests_invalid_retry_params_sync(
    max_retries: int,
    min_delay: timedelta,
) -> None:
    """Negative retry count or minimum delay raises `ValueError` in the sync client."""
    client = ApifyClient(token='placeholder_token')
    rq_client = client.request_queue(request_queue_id='whatever')
    requests: list[RequestWithoutIdDict] = [
        {'unique_key': 'http://example.com/1', 'url': 'http://example.com/1', 'method': 'GET'},
    ]

    with pytest.raises(ValueError, match='must be non-negative'):
        rq_client.batch_add_requests(
            requests=requests,
            max_unprocessed_requests_retries=max_retries,
            min_delay_between_unprocessed_requests_retries=min_delay,
        )


async def test_batch_add_requests_retry_round_error_returns_partial_result_async(
    httpserver: HTTPServer,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A failing retry round logs the error and returns requests added in earlier rounds plus remaining unprocessed."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync(
        token='placeholder_token',
        api_url=server_url,
        api_public_url=server_url,
        max_retries=1,
        min_delay_between_retries=timedelta(milliseconds=1),
    )

    handler = Mock(
        side_effect=[
            Response(_PARTIALLY_ADDED_BATCH_RESPONSE_CONTENT, status=200, content_type='application/json'),
            Response(
                '{"error": {"type": "internal-error", "message": "boom"}}', status=500, content_type='application/json'
            ),
            Response(
                '{"error": {"type": "internal-error", "message": "boom"}}', status=500, content_type='application/json'
            ),
        ]
    )
    httpserver.expect_request(re.compile(r'.*'), method='POST').respond_with_handler(handler)
    requests: list[RequestWithoutIdDict] = [
        {'unique_key': 'http://example.com/1', 'url': 'http://example.com/1', 'method': 'GET'},
        {'unique_key': 'http://example.com/2', 'url': 'http://example.com/2', 'method': 'GET'},
    ]
    rq_client = client.request_queue(request_queue_id='whatever')

    with caplog.at_level(logging.ERROR, logger='apify_client'):
        result = await rq_client.batch_add_requests(
            requests=requests,
            min_delay_between_unprocessed_requests_retries=timedelta(milliseconds=1),
        )

    assert [req.unique_key for req in result.processed_requests] == ['http://example.com/1']
    assert [req.unique_key for req in result.unprocessed_requests] == ['http://example.com/2']
    assert any('Failed to retry unprocessed requests' in record.message for record in caplog.records)


def test_batch_add_requests_retry_round_error_returns_partial_result_sync(
    httpserver: HTTPServer,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A failing retry round logs the error and returns requests added in earlier rounds plus remaining unprocessed."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(
        token='placeholder_token',
        api_url=server_url,
        api_public_url=server_url,
        max_retries=1,
        min_delay_between_retries=timedelta(milliseconds=1),
    )

    handler = Mock(
        side_effect=[
            Response(_PARTIALLY_ADDED_BATCH_RESPONSE_CONTENT, status=200, content_type='application/json'),
            Response(
                '{"error": {"type": "internal-error", "message": "boom"}}', status=500, content_type='application/json'
            ),
            Response(
                '{"error": {"type": "internal-error", "message": "boom"}}', status=500, content_type='application/json'
            ),
        ]
    )
    httpserver.expect_request(re.compile(r'.*'), method='POST').respond_with_handler(handler)
    requests: list[RequestWithoutIdDict] = [
        {'unique_key': 'http://example.com/1', 'url': 'http://example.com/1', 'method': 'GET'},
        {'unique_key': 'http://example.com/2', 'url': 'http://example.com/2', 'method': 'GET'},
    ]
    rq_client = client.request_queue(request_queue_id='whatever')

    with caplog.at_level(logging.ERROR, logger='apify_client'):
        result = rq_client.batch_add_requests(
            requests=requests,
            min_delay_between_unprocessed_requests_retries=timedelta(milliseconds=1),
        )

    assert [req.unique_key for req in result.processed_requests] == ['http://example.com/1']
    assert [req.unique_key for req in result.unprocessed_requests] == ['http://example.com/2']
    assert any('Failed to retry unprocessed requests' in record.message for record in caplog.records)


_INVALID_BATCH_RESPONSE_CONTENT = '{"data": {"processedRequests": "invalid", "unprocessedRequests": []}}'


async def test_batch_add_requests_retry_round_invalid_response_raises_async(httpserver: HTTPServer) -> None:
    """A retry round response that does not match the model raises `ValidationError` in the async client."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync(token='placeholder_token', api_url=server_url, api_public_url=server_url)

    handler = Mock(
        side_effect=[
            Response(_PARTIALLY_ADDED_BATCH_RESPONSE_CONTENT, status=200, content_type='application/json'),
            Response(_INVALID_BATCH_RESPONSE_CONTENT, status=200, content_type='application/json'),
        ]
    )
    httpserver.expect_request(re.compile(r'.*'), method='POST').respond_with_handler(handler)
    requests: list[RequestWithoutIdDict] = [
        {'unique_key': 'http://example.com/1', 'url': 'http://example.com/1', 'method': 'GET'},
        {'unique_key': 'http://example.com/2', 'url': 'http://example.com/2', 'method': 'GET'},
    ]
    rq_client = client.request_queue(request_queue_id='whatever')

    with pytest.raises(ValidationError):
        await rq_client.batch_add_requests(
            requests=requests,
            min_delay_between_unprocessed_requests_retries=timedelta(milliseconds=1),
        )

    assert handler.call_count == 2


def test_batch_add_requests_retry_round_invalid_response_raises_sync(httpserver: HTTPServer) -> None:
    """A retry round response that does not match the model raises `ValidationError` in the sync client."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(token='placeholder_token', api_url=server_url, api_public_url=server_url)

    handler = Mock(
        side_effect=[
            Response(_PARTIALLY_ADDED_BATCH_RESPONSE_CONTENT, status=200, content_type='application/json'),
            Response(_INVALID_BATCH_RESPONSE_CONTENT, status=200, content_type='application/json'),
        ]
    )
    httpserver.expect_request(re.compile(r'.*'), method='POST').respond_with_handler(handler)
    requests: list[RequestWithoutIdDict] = [
        {'unique_key': 'http://example.com/1', 'url': 'http://example.com/1', 'method': 'GET'},
        {'unique_key': 'http://example.com/2', 'url': 'http://example.com/2', 'method': 'GET'},
    ]
    rq_client = client.request_queue(request_queue_id='whatever')

    with pytest.raises(ValidationError):
        rq_client.batch_add_requests(
            requests=requests,
            min_delay_between_unprocessed_requests_retries=timedelta(milliseconds=1),
        )

    assert handler.call_count == 2


@pytest.mark.parametrize(
    ('attempt', 'expected_seconds'),
    [
        pytest.param(0, 0.75, id='first retry'),
        pytest.param(1, 1.5, id='second retry'),
        pytest.param(2, 3.0, id='third retry'),
    ],
)
def test_compute_retry_delay_seconds_doubles_per_attempt(
    monkeypatch: pytest.MonkeyPatch,
    attempt: int,
    expected_seconds: float,
) -> None:
    """The unprocessed-requests retry delay is the jittered minimum delay doubled for each attempt."""
    uniform = Mock(return_value=1.5)
    monkeypatch.setattr(random, 'uniform', uniform)

    delay = _compute_retry_delay_seconds(attempt, timedelta(milliseconds=500))

    assert delay == pytest.approx(expected_seconds)
    uniform.assert_called_once_with(1.0, 2.0)


_REQUEST_REGISTRATION_RESPONSE_CONTENT = (
    '{"data": {"requestId": "YiKoxjkaS9gjGTqhF", "wasAlreadyPresent": false, "wasAlreadyHandled": false}}'
)

_FULL_REQUEST_DICT: RequestResourceDict = {
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


class Unserializable:
    """A value no JSON serializer can encode without a stringification fallback."""

    def __str__(self) -> str:
        return 'unserializable'


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
    assert added['handledAt'] == '2019-06-16T10:23:31.607000Z'


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
    assert added['handledAt'] == '2019-06-16T10:23:31.607000Z'


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
    assert sent_request['handledAt'] == '2019-06-16T10:23:31.607000Z'


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
    assert sent_request['handledAt'] == '2019-06-16T10:23:31.607000Z'


async def test_add_request_stringifies_unserializable_user_data_async(httpserver: HTTPServer) -> None:
    """A `user_data` value JSON cannot represent is stringified instead of aborting the call."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync(token='placeholder_token', api_url=server_url, api_public_url=server_url)

    payloads = list[bytes]()
    httpserver.expect_request(re.compile(r'.*')).respond_with_handler(
        _payload_capturing_handler(payloads, _REQUEST_REGISTRATION_RESPONSE_CONTENT)
    )
    rq_client = client.request_queue(request_queue_id='whatever')

    await rq_client.add_request(
        {'unique_key': 'http://example.com/1', 'url': 'http://example.com/1', 'user_data': {'tag': Unserializable()}}
    )

    assert json.loads(payloads[0])['userData'] == {'tag': 'unserializable'}


def test_add_request_stringifies_unserializable_user_data_sync(httpserver: HTTPServer) -> None:
    """A `user_data` value JSON cannot represent is stringified instead of aborting the call."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(token='placeholder_token', api_url=server_url, api_public_url=server_url)

    payloads = list[bytes]()
    httpserver.expect_request(re.compile(r'.*')).respond_with_handler(
        _payload_capturing_handler(payloads, _REQUEST_REGISTRATION_RESPONSE_CONTENT)
    )
    rq_client = client.request_queue(request_queue_id='whatever')

    rq_client.add_request(
        {'unique_key': 'http://example.com/1', 'url': 'http://example.com/1', 'user_data': {'tag': Unserializable()}}
    )

    assert json.loads(payloads[0])['userData'] == {'tag': 'unserializable'}


async def test_batch_add_requests_stringifies_unserializable_user_data_async(httpserver: HTTPServer) -> None:
    """A `user_data` value JSON cannot represent is stringified instead of aborting the call."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync(token='placeholder_token', api_url=server_url, api_public_url=server_url)

    payloads = list[bytes]()
    httpserver.expect_request(re.compile(r'.*'), method='POST').respond_with_handler(
        _payload_capturing_handler(payloads)
    )
    rq_client = client.request_queue(request_queue_id='whatever')

    await rq_client.batch_add_requests(
        requests=[
            {
                'unique_key': 'http://example.com/1',
                'url': 'http://example.com/1',
                'user_data': {'tag': Unserializable()},
            }
        ]
    )

    (sent_request,) = json.loads(payloads[0])
    assert sent_request['userData'] == {'tag': 'unserializable'}


def test_batch_add_requests_stringifies_unserializable_user_data_sync(httpserver: HTTPServer) -> None:
    """A `user_data` value JSON cannot represent is stringified instead of aborting the call."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(token='placeholder_token', api_url=server_url, api_public_url=server_url)

    payloads = list[bytes]()
    httpserver.expect_request(re.compile(r'.*'), method='POST').respond_with_handler(
        _payload_capturing_handler(payloads)
    )
    rq_client = client.request_queue(request_queue_id='whatever')

    rq_client.batch_add_requests(
        requests=[
            {
                'unique_key': 'http://example.com/1',
                'url': 'http://example.com/1',
                'user_data': {'tag': Unserializable()},
            }
        ]
    )

    (sent_request,) = json.loads(payloads[0])
    assert sent_request['userData'] == {'tag': 'unserializable'}


async def test_batch_delete_requests_stringifies_unserializable_extra_async(httpserver: HTTPServer) -> None:
    """An extra field JSON cannot represent is stringified instead of aborting the call."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync(token='placeholder_token', api_url=server_url, api_public_url=server_url)

    payloads = list[bytes]()
    httpserver.expect_request(re.compile(r'.*'), method='DELETE').respond_with_handler(
        _payload_capturing_handler(payloads)
    )
    rq_client = client.request_queue(request_queue_id='whatever')

    request = RequestToDelete.model_validate({'id': 'YiKoxjkaS9gjGTqhF', 'weird': Unserializable()})
    await rq_client.batch_delete_requests(requests=[request])

    (sent_request,) = json.loads(payloads[0])
    assert sent_request == {'id': 'YiKoxjkaS9gjGTqhF', 'weird': 'unserializable'}


def test_batch_delete_requests_stringifies_unserializable_extra_sync(httpserver: HTTPServer) -> None:
    """An extra field JSON cannot represent is stringified instead of aborting the call."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(token='placeholder_token', api_url=server_url, api_public_url=server_url)

    payloads = list[bytes]()
    httpserver.expect_request(re.compile(r'.*'), method='DELETE').respond_with_handler(
        _payload_capturing_handler(payloads)
    )
    rq_client = client.request_queue(request_queue_id='whatever')

    request = RequestToDelete.model_validate({'id': 'YiKoxjkaS9gjGTqhF', 'weird': Unserializable()})
    rq_client.batch_delete_requests(requests=[request])

    (sent_request,) = json.loads(payloads[0])
    assert sent_request == {'id': 'YiKoxjkaS9gjGTqhF', 'weird': 'unserializable'}


async def test_add_request_requires_unique_key_and_url_async(httpserver: HTTPServer) -> None:
    """Pydantic still rejects a dict missing `unique_key`/`url`, even past a type-check bypass."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync(token='placeholder_token', api_url=server_url, api_public_url=server_url)
    rq_client = client.request_queue(request_queue_id='whatever')

    with pytest.raises(ValidationError) as exc_info:
        await rq_client.add_request({'method': 'GET'})  # ty: ignore[invalid-argument-type]

    assert {error['loc'][0] for error in exc_info.value.errors()} == {'uniqueKey', 'url'}
    assert httpserver.log == []


def test_add_request_requires_unique_key_and_url_sync(httpserver: HTTPServer) -> None:
    """Pydantic still rejects a dict missing `unique_key`/`url`, even past a type-check bypass."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(token='placeholder_token', api_url=server_url, api_public_url=server_url)
    rq_client = client.request_queue(request_queue_id='whatever')

    with pytest.raises(ValidationError) as exc_info:
        rq_client.add_request({'method': 'GET'})  # ty: ignore[invalid-argument-type]

    assert {error['loc'][0] for error in exc_info.value.errors()} == {'uniqueKey', 'url'}
    assert httpserver.log == []

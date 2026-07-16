from __future__ import annotations

import gzip
import json
import re
from typing import TYPE_CHECKING, Any

import brotli
import pytest
from werkzeug import Request, Response

from apify_client import ApifyClient, ApifyClientAsync
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from collections.abc import Callable

    from pytest_httpserver import HTTPServer

    from apify_client._typeddicts import RequestDraftDict

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


_ADD_REQUEST_RESPONSE_CONTENT = """{
  "data": {
    "requestId": "YiKoxjkaS9gjGTqhF",
    "wasAlreadyPresent": false,
    "wasAlreadyHandled": false
  }
}"""

_FULLY_ADDED_BATCH_RESPONSE_CONTENT = """{
  "data": {
    "processedRequests": [
      {
        "requestId": "YiKoxjkaS9gjGTqhF",
        "uniqueKey": "http://example.com/1",
        "wasAlreadyPresent": false,
        "wasAlreadyHandled": false
      }
    ],
    "unprocessedRequests": []
  }
}"""

_SNAKE_CASE_REQUEST: dict[str, Any] = {
    'unique_key': 'http://example.com/1',
    'url': 'http://example.com/1',
    'user_data': {'label': 'DETAIL'},
    'no_retry': True,
}

_EXPECTED_CAMEL_CASE_REQUEST = {
    'uniqueKey': 'http://example.com/1',
    'url': 'http://example.com/1',
    'userData': {'label': 'DETAIL'},
    'noRetry': True,
}


def _make_json_capture_handler(received_bodies: list[Any], response_content: str) -> Callable[[Request], Response]:
    def handler(request: Request) -> Response:
        body = request.get_data()
        encoding = request.headers.get('Content-Encoding')
        if encoding == 'br':
            body = brotli.decompress(body)
        elif encoding == 'gzip':
            body = gzip.decompress(body)
        received_bodies.append(json.loads(body))
        return Response(status=201, response=response_content, content_type='application/json')

    return handler


def test_add_request_camel_cases_fields_undeclared_on_model_sync(httpserver: HTTPServer) -> None:
    """Snake_case fields not declared on `RequestDraft` (e.g. `user_data`) are camelCased in the API payload."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(token='placeholder_token', api_url=server_url, api_public_url=server_url)

    received_bodies: list[Any] = []
    httpserver.expect_oneshot_request(re.compile(r'.*'), method='POST').respond_with_handler(
        _make_json_capture_handler(received_bodies, _ADD_REQUEST_RESPONSE_CONTENT)
    )

    client.request_queue(request_queue_id='whatever').add_request(_SNAKE_CASE_REQUEST)  # ty: ignore[invalid-argument-type]
    assert received_bodies == [_EXPECTED_CAMEL_CASE_REQUEST]


async def test_add_request_camel_cases_fields_undeclared_on_model_async(httpserver: HTTPServer) -> None:
    """Snake_case fields not declared on `RequestDraft` (e.g. `user_data`) are camelCased in the API payload."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync(token='placeholder_token', api_url=server_url, api_public_url=server_url)

    received_bodies: list[Any] = []
    httpserver.expect_oneshot_request(re.compile(r'.*'), method='POST').respond_with_handler(
        _make_json_capture_handler(received_bodies, _ADD_REQUEST_RESPONSE_CONTENT)
    )

    await client.request_queue(request_queue_id='whatever').add_request(_SNAKE_CASE_REQUEST)  # ty: ignore[invalid-argument-type]
    assert received_bodies == [_EXPECTED_CAMEL_CASE_REQUEST]


def test_batch_add_requests_camel_cases_fields_undeclared_on_model_sync(httpserver: HTTPServer) -> None:
    """Snake_case fields not declared on `RequestDraft` (e.g. `user_data`) are camelCased in the API payload."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(token='placeholder_token', api_url=server_url, api_public_url=server_url)

    received_bodies: list[Any] = []
    httpserver.expect_oneshot_request(re.compile(r'.*'), method='POST').respond_with_handler(
        _make_json_capture_handler(received_bodies, _FULLY_ADDED_BATCH_RESPONSE_CONTENT)
    )

    client.request_queue(request_queue_id='whatever').batch_add_requests(requests=[_SNAKE_CASE_REQUEST])  # ty: ignore[invalid-argument-type]
    assert received_bodies == [[_EXPECTED_CAMEL_CASE_REQUEST]]


async def test_batch_add_requests_camel_cases_fields_undeclared_on_model_async(httpserver: HTTPServer) -> None:
    """Snake_case fields not declared on `RequestDraft` (e.g. `user_data`) are camelCased in the API payload."""
    server_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync(token='placeholder_token', api_url=server_url, api_public_url=server_url)

    received_bodies: list[Any] = []
    httpserver.expect_oneshot_request(re.compile(r'.*'), method='POST').respond_with_handler(
        _make_json_capture_handler(received_bodies, _FULLY_ADDED_BATCH_RESPONSE_CONTENT)
    )

    await client.request_queue(request_queue_id='whatever').batch_add_requests(requests=[_SNAKE_CASE_REQUEST])  # ty: ignore[invalid-argument-type]
    assert received_bodies == [[_EXPECTED_CAMEL_CASE_REQUEST]]

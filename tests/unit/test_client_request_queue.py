from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest

from apify_client import ApifyClient, ApifyClientAsync
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from pytest_httpserver import HTTPServer

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


@pytest.mark.usefixtures('patch_basic_url')
async def test_batch_not_processed_raises_exception_async(httpserver: HTTPServer) -> None:
    """Test that client exceptions are not silently ignored"""
    client = ApifyClientAsync(token='placeholder_token')
    httpserver.expect_oneshot_request(re.compile(r'.*'), method='POST').respond_with_data(status=401)
    requests = [
        {'uniqueKey': 'http://example.com/1', 'url': 'http://example.com/1', 'method': 'GET'},
        {'uniqueKey': 'http://example.com/2', 'url': 'http://example.com/2', 'method': 'GET'},
    ]
    rq_client = client.request_queue(request_queue_id='whatever')

    with pytest.raises(ApifyApiError):
        await rq_client.batch_add_requests(requests=requests)


@pytest.mark.usefixtures('patch_basic_url')
async def test_batch_processed_partially_async(httpserver: HTTPServer) -> None:
    client = ApifyClientAsync(token='placeholder_token')

    httpserver.expect_oneshot_request(re.compile(r'.*'), method='POST').respond_with_data(
        status=200, response_data=_PARTIALLY_ADDED_BATCH_RESPONSE_CONTENT
    )
    requests = [
        {'uniqueKey': 'http://example.com/1', 'url': 'http://example.com/1', 'method': 'GET'},
        {'uniqueKey': 'http://example.com/2', 'url': 'http://example.com/2', 'method': 'GET'},
    ]
    rq_client = client.request_queue(request_queue_id='whatever')

    response = await rq_client.batch_add_requests(requests=requests)
    assert requests[0]['uniqueKey'] in {request['uniqueKey'] for request in response['processedRequests']}
    assert response['unprocessedRequests'] == [requests[1]]


@pytest.mark.usefixtures('patch_basic_url')
def test_batch_not_processed_raises_exception_sync(httpserver: HTTPServer) -> None:
    """Test that client exceptions are not silently ignored"""
    client = ApifyClient(token='placeholder_token')

    httpserver.expect_oneshot_request(re.compile(r'.*'), method='POST').respond_with_data(status=401)
    requests = [
        {'uniqueKey': 'http://example.com/1', 'url': 'http://example.com/1', 'method': 'GET'},
        {'uniqueKey': 'http://example.com/2', 'url': 'http://example.com/2', 'method': 'GET'},
    ]
    rq_client = client.request_queue(request_queue_id='whatever')

    with pytest.raises(ApifyApiError):
        rq_client.batch_add_requests(requests=requests)


@pytest.mark.usefixtures('patch_basic_url')
async def test_batch_processed_partially_sync(httpserver: HTTPServer) -> None:
    client = ApifyClient(token='placeholder_token')

    httpserver.expect_oneshot_request(re.compile(r'.*'), method='POST').respond_with_data(
        status=200, response_data=_PARTIALLY_ADDED_BATCH_RESPONSE_CONTENT
    )
    requests = [
        {'uniqueKey': 'http://example.com/1', 'url': 'http://example.com/1', 'method': 'GET'},
        {'uniqueKey': 'http://example.com/2', 'url': 'http://example.com/2', 'method': 'GET'},
    ]
    rq_client = client.request_queue(request_queue_id='whatever')

    response = rq_client.batch_add_requests(requests=requests)
    assert requests[0]['uniqueKey'] in {request['uniqueKey'] for request in response['processedRequests']}
    assert response['unprocessedRequests'] == [requests[1]]

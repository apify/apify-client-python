import pytest
import respx

import apify_client
from apify_client import ApifyClient, ApifyClientAsync

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


@respx.mock
async def test_batch_not_processed_raises_exception_async() -> None:
    """Test that client exceptions are not silently ignored"""
    client = ApifyClientAsync(token='')

    respx.route(method='POST', host='api.apify.com').mock(return_value=respx.MockResponse(401))
    requests = [
        {'uniqueKey': 'http://example.com/1', 'url': 'http://example.com/1', 'method': 'GET'},
        {'uniqueKey': 'http://example.com/2', 'url': 'http://example.com/2', 'method': 'GET'},
    ]
    rq_client = client.request_queue(request_queue_id='whatever')

    with pytest.raises(apify_client._errors.ApifyApiError):
        await rq_client.batch_add_requests(requests=requests)


@respx.mock
async def test_batch_processed_partially_async() -> None:
    client = ApifyClientAsync(token='')

    respx.route(method='POST', host='api.apify.com').mock(
        return_value=respx.MockResponse(200, content=_PARTIALLY_ADDED_BATCH_RESPONSE_CONTENT)
    )
    requests = [
        {'uniqueKey': 'http://example.com/1', 'url': 'http://example.com/1', 'method': 'GET'},
        {'uniqueKey': 'http://example.com/2', 'url': 'http://example.com/2', 'method': 'GET'},
    ]
    rq_client = client.request_queue(request_queue_id='whatever')

    response = await rq_client.batch_add_requests(requests=requests)
    assert requests[0]['uniqueKey'] in {request['uniqueKey'] for request in response['processedRequests']}
    assert response['unprocessedRequests'] == [requests[1]]


@respx.mock
def test_batch_not_processed_raises_exception_sync() -> None:
    """Test that client exceptions are not silently ignored"""
    client = ApifyClient(token='')

    respx.route(method='POST', host='api.apify.com').mock(return_value=respx.MockResponse(401))
    requests = [
        {'uniqueKey': 'http://example.com/1', 'url': 'http://example.com/1', 'method': 'GET'},
        {'uniqueKey': 'http://example.com/2', 'url': 'http://example.com/2', 'method': 'GET'},
    ]
    rq_client = client.request_queue(request_queue_id='whatever')

    with pytest.raises(apify_client._errors.ApifyApiError):
        rq_client.batch_add_requests(requests=requests)


@respx.mock
async def test_batch_processed_partially_sync() -> None:
    client = ApifyClient(token='')

    respx.route(method='POST', host='api.apify.com').mock(
        return_value=respx.MockResponse(200, content=_PARTIALLY_ADDED_BATCH_RESPONSE_CONTENT)
    )
    requests = [
        {'uniqueKey': 'http://example.com/1', 'url': 'http://example.com/1', 'method': 'GET'},
        {'uniqueKey': 'http://example.com/2', 'url': 'http://example.com/2', 'method': 'GET'},
    ]
    rq_client = client.request_queue(request_queue_id='whatever')

    response = rq_client.batch_add_requests(requests=requests)
    assert requests[0]['uniqueKey'] in {request['uniqueKey'] for request in response['processedRequests']}
    assert response['unprocessedRequests'] == [requests[1]]

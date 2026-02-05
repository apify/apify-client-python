from __future__ import annotations

import json
from datetime import timedelta
from typing import TYPE_CHECKING

import pytest
from werkzeug import Request, Response

from apify_client import ApifyClient, ApifyClientAsync
from apify_client._models import ActorJobStatus

if TYPE_CHECKING:
    from pytest_httpserver import HTTPServer

_MOCKED_ACTOR_ID = 'test_actor_id'
_MOCKED_RUN_ID = 'test_run_id'


def _create_minimal_run_response() -> dict:
    """Create minimal valid Run response for testing."""
    return {
        'data': {
            'id': _MOCKED_RUN_ID,
            'actId': _MOCKED_ACTOR_ID,
            'userId': 'test_user_id',
            'startedAt': '2019-11-30T07:34:24.202Z',
            'finishedAt': '2019-12-12T09:30:12.202Z',
            'status': ActorJobStatus.RUNNING.value,
            'statusMessage': 'Running',
            'isStatusMessageTerminal': False,
            'meta': {'origin': 'WEB'},
            'stats': {
                'restartCount': 0,
                'resurrectCount': 0,
                'computeUnits': 0.1,
            },
            'options': {
                'build': 'latest',
                'timeoutSecs': 300,
                'memoryMbytes': 1024,
                'diskMbytes': 2048,
            },
            'buildId': 'test_build_id',
            'generalAccess': 'RESTRICTED',
            'defaultKeyValueStoreId': 'test_kvs_id',
            'defaultDatasetId': 'test_dataset_id',
            'defaultRequestQueueId': 'test_rq_id',
            'buildNumber': '0.0.1',
            'containerUrl': 'https://test.runs.apify.net',
        }
    }


def test_actor_start_passes_timeout_param_sync(httpserver: HTTPServer) -> None:
    """Test that sync ActorClient.start() passes timeout as 'timeout' query parameter."""
    captured_requests: list[Request] = []

    def capture_request(request: Request) -> Response:
        captured_requests.append(request)
        return Response(
            response=json.dumps(_create_minimal_run_response()),
            status=200,
            mimetype='application/json',
        )

    httpserver.expect_request(
        f'/v2/acts/{_MOCKED_ACTOR_ID}/runs',
        method='POST',
    ).respond_with_handler(capture_request)

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(token='test_token', api_url=api_url)

    # Call start with timeout_secs
    client.actor(_MOCKED_ACTOR_ID).start(timeout=timedelta(seconds=300))

    # Verify the request was made with correct timeout parameter
    assert len(captured_requests) == 1
    request = captured_requests[0]

    # The timeout should be passed as 'timeout' query parameter, not 'timeout_secs'
    assert 'timeout' in request.args, "Expected 'timeout' query parameter to be present"
    assert request.args['timeout'] == '300', f'Expected timeout=300, got timeout={request.args.get("timeout")}'
    assert 'timeout_secs' not in request.args, "Unexpected 'timeout_secs' query parameter"


async def test_actor_start_passes_timeout_param_async(httpserver: HTTPServer) -> None:
    """Test that async ActorClientAsync.start() passes timeout as 'timeout' query parameter."""
    captured_requests: list[Request] = []

    def capture_request(request: Request) -> Response:
        captured_requests.append(request)
        return Response(
            response=json.dumps(_create_minimal_run_response()),
            status=200,
            mimetype='application/json',
        )

    httpserver.expect_request(
        f'/v2/acts/{_MOCKED_ACTOR_ID}/runs',
        method='POST',
    ).respond_with_handler(capture_request)

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync(token='test_token', api_url=api_url)

    # Call start with timeout_secs
    await client.actor(_MOCKED_ACTOR_ID).start(timeout=timedelta(seconds=300))

    # Verify the request was made with correct timeout parameter
    assert len(captured_requests) == 1
    request = captured_requests[0]

    # The timeout should be passed as 'timeout' query parameter, not 'timeout_secs'
    assert 'timeout' in request.args, "Expected 'timeout' query parameter to be present"
    assert request.args['timeout'] == '300', f'Expected timeout=300, got timeout={request.args.get("timeout")}'
    assert 'timeout_secs' not in request.args, "Unexpected 'timeout_secs' query parameter"


def test_actor_start_timeout_not_passed_when_none_sync(httpserver: HTTPServer) -> None:
    """Test that sync ActorClient.start() does not pass timeout when not specified."""
    captured_requests: list[Request] = []

    def capture_request(request: Request) -> Response:
        captured_requests.append(request)
        return Response(
            response=json.dumps(_create_minimal_run_response()),
            status=200,
            mimetype='application/json',
        )

    httpserver.expect_request(
        f'/v2/acts/{_MOCKED_ACTOR_ID}/runs',
        method='POST',
    ).respond_with_handler(capture_request)

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(token='test_token', api_url=api_url)

    # Call start without timeout_secs
    client.actor(_MOCKED_ACTOR_ID).start()

    # Verify timeout parameter is not present
    assert len(captured_requests) == 1
    request = captured_requests[0]
    assert 'timeout' not in request.args, "Unexpected 'timeout' query parameter when not specified"
    assert 'timeout_secs' not in request.args, "Unexpected 'timeout_secs' query parameter"


async def test_actor_start_timeout_not_passed_when_none_async(httpserver: HTTPServer) -> None:
    """Test that async ActorClientAsync.start() does not pass timeout when not specified."""
    captured_requests: list[Request] = []

    def capture_request(request: Request) -> Response:
        captured_requests.append(request)
        return Response(
            response=json.dumps(_create_minimal_run_response()),
            status=200,
            mimetype='application/json',
        )

    httpserver.expect_request(
        f'/v2/acts/{_MOCKED_ACTOR_ID}/runs',
        method='POST',
    ).respond_with_handler(capture_request)

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync(token='test_token', api_url=api_url)

    # Call start without timeout_secs
    await client.actor(_MOCKED_ACTOR_ID).start()

    # Verify timeout parameter is not present
    assert len(captured_requests) == 1
    request = captured_requests[0]
    assert 'timeout' not in request.args, "Unexpected 'timeout' query parameter when not specified"
    assert 'timeout_secs' not in request.args, "Unexpected 'timeout_secs' query parameter"


@pytest.mark.parametrize('timeout_value', [60, 300, 3600, 86400])
def test_actor_start_various_timeout_values_sync(httpserver: HTTPServer, timeout_value: int) -> None:
    """Test that various timeout values are correctly passed in sync start()."""
    captured_requests: list[Request] = []

    def capture_request(request: Request) -> Response:
        captured_requests.append(request)
        return Response(
            response=json.dumps(_create_minimal_run_response()),
            status=200,
            mimetype='application/json',
        )

    httpserver.expect_request(
        f'/v2/acts/{_MOCKED_ACTOR_ID}/runs',
        method='POST',
    ).respond_with_handler(capture_request)

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(token='test_token', api_url=api_url)

    client.actor(_MOCKED_ACTOR_ID).start(timeout=timedelta(seconds=timeout_value))

    assert len(captured_requests) == 1
    assert captured_requests[0].args['timeout'] == str(timeout_value)


@pytest.mark.parametrize('timeout_value', [60, 300, 3600, 86400])
async def test_actor_start_various_timeout_values_async(httpserver: HTTPServer, timeout_value: int) -> None:
    """Test that various timeout values are correctly passed in async start()."""
    captured_requests: list[Request] = []

    def capture_request(request: Request) -> Response:
        captured_requests.append(request)
        return Response(
            response=json.dumps(_create_minimal_run_response()),
            status=200,
            mimetype='application/json',
        )

    httpserver.expect_request(
        f'/v2/acts/{_MOCKED_ACTOR_ID}/runs',
        method='POST',
    ).respond_with_handler(capture_request)

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync(token='test_token', api_url=api_url)

    await client.actor(_MOCKED_ACTOR_ID).start(timeout=timedelta(seconds=timeout_value))

    assert len(captured_requests) == 1
    assert captured_requests[0].args['timeout'] == str(timeout_value)

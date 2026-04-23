from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pytest
from werkzeug import Response

from apify_client import ApifyClient, ApifyClientAsync
from apify_client._http_clients import ImpitHttpClient, ImpitHttpClientAsync
from apify_client.errors import (
    ApifyApiError,
    ConflictError,
    ForbiddenError,
    InvalidRequestError,
    NotFoundError,
    RateLimitError,
    ServerError,
    UnauthorizedError,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from pytest_httpserver import HTTPServer
    from werkzeug import Request

_TEST_PATH = '/errors'
_EXPECTED_MESSAGE = 'some_message'
_EXPECTED_TYPE = 'some_type'
_EXPECTED_DATA = {
    'invalidItems': {'0': ["should have required property 'name'"], '1': ["should have required property 'name'"]}
}

RAW_ERROR = (
    b'{\n'
    b'  "error": {\n'
    b'    "type": "insufficient-permissions",\n'
    b'    "message": "Insufficient permissions for the Actor run. Make sure you\''
    b're passing a correct API token and that it has the required permissions."\n'
    b'  }\n'
    b'}'
)

_DATASET_FIXTURE = {
    'id': 'ds-1',
    'userId': 'u-1',
    'createdAt': '2026-01-01T00:00:00.000Z',
    'modifiedAt': '2026-01-01T00:00:00.000Z',
    'accessedAt': '2026-01-01T00:00:00.000Z',
    'itemCount': 0,
    'cleanItemCount': 0,
    'consoleUrl': 'https://console.apify.com/storage/datasets/ds-1',
}

# Singleton sub-path endpoints — fetch a fixed path under an ID-identified parent (e.g. /schedules/{id}/log). A 404
# always means the parent is missing, so `NotFoundError` propagates instead of collapsing to `None`.
_SINGLETON_SUBPATH_404_CASES = [
    pytest.param('/v2/schedules/missing/log', 'GET', lambda c: c.schedule('missing').get_log(), id='schedule_get_log'),
    pytest.param('/v2/actor-tasks/missing/input', 'GET', lambda c: c.task('missing').get_input(), id='task_get_input'),
    pytest.param(
        '/v2/datasets/missing/statistics',
        'GET',
        lambda c: c.dataset('missing').get_statistics(),
        id='dataset_get_statistics',
    ),
    pytest.param('/v2/webhooks/missing/test', 'POST', lambda c: c.webhook('missing').test(), id='webhook_test'),
]


def _not_found_body() -> dict:
    return {'error': {'type': 'record-not-found', 'message': 'not found'}}


def streaming_handler(_request: Request) -> Response:
    """Handler for streaming log requests."""
    return Response(
        response=(RAW_ERROR[i : i + 1] for i in range(len(RAW_ERROR))),
        status=403,
        mimetype='application/octet-stream',
        headers={'Content-Length': str(len(RAW_ERROR))},
    )


@pytest.fixture
def sync_client(httpserver: HTTPServer) -> ApifyClient:
    return ApifyClient(token='test', api_url=httpserver.url_for('/').removesuffix('/'))


@pytest.fixture
def async_client(httpserver: HTTPServer) -> ApifyClientAsync:
    return ApifyClientAsync(token='test', api_url=httpserver.url_for('/').removesuffix('/'))


@pytest.fixture
def test_endpoint(httpserver: HTTPServer) -> str:
    httpserver.expect_request(_TEST_PATH).respond_with_json(
        {'error': {'message': _EXPECTED_MESSAGE, 'type': _EXPECTED_TYPE, 'data': _EXPECTED_DATA}}, status=400
    )
    return str(httpserver.url_for(_TEST_PATH))


def test_client_apify_api_error_with_data(test_endpoint: str) -> None:
    """Test that client correctly throws ApifyApiError with error data from response."""
    client = ImpitHttpClient()

    with pytest.raises(ApifyApiError) as exc:
        client.call(method='GET', url=test_endpoint)

    assert exc.value.message == _EXPECTED_MESSAGE
    assert exc.value.type == _EXPECTED_TYPE
    assert exc.value.data == _EXPECTED_DATA


async def test_async_client_apify_api_error_with_data(test_endpoint: str) -> None:
    """Test that async client correctly throws ApifyApiError with error data from response."""
    client = ImpitHttpClientAsync()

    with pytest.raises(ApifyApiError) as exc:
        await client.call(method='GET', url=test_endpoint)

    assert exc.value.message == _EXPECTED_MESSAGE
    assert exc.value.type == _EXPECTED_TYPE
    assert exc.value.data == _EXPECTED_DATA


def test_client_apify_api_error_streamed(httpserver: HTTPServer) -> None:
    """Test that client correctly throws ApifyApiError when the response has stream."""

    error = json.loads(RAW_ERROR.decode())

    client = ImpitHttpClient()

    httpserver.expect_request('/stream_error').respond_with_handler(streaming_handler)

    with pytest.raises(ApifyApiError) as exc:
        client.call(method='GET', url=httpserver.url_for('/stream_error'), stream=True)

    assert exc.value.message == error['error']['message']
    assert exc.value.type == error['error']['type']


async def test_async_client_apify_api_error_streamed(httpserver: HTTPServer) -> None:
    """Test that async client correctly throws ApifyApiError when the response has stream."""

    error = json.loads(RAW_ERROR.decode())

    client = ImpitHttpClientAsync()

    httpserver.expect_request('/stream_error').respond_with_handler(streaming_handler)

    with pytest.raises(ApifyApiError) as exc:
        await client.call(method='GET', url=httpserver.url_for('/stream_error'), stream=True)

    assert exc.value.message == error['error']['message']
    assert exc.value.type == error['error']['type']


def test_apify_api_error_dispatches_to_subclass_for_known_status(httpserver: HTTPServer) -> None:
    """Mapped HTTP status codes dispatch to their matching subclass."""
    httpserver.expect_request('/dispatch').respond_with_json(
        {'error': {'type': 'record-not-found', 'message': 'nope'}}, status=404
    )
    client = ImpitHttpClient()

    with pytest.raises(NotFoundError) as exc:
        client.call(method='GET', url=str(httpserver.url_for('/dispatch')))

    # Still an ApifyApiError, so legacy `except` handlers keep working.
    assert isinstance(exc.value, ApifyApiError)
    assert exc.value.status_code == 404
    assert exc.value.type == 'record-not-found'


def test_apify_api_error_dispatches_streamed_response(httpserver: HTTPServer) -> None:
    """Dispatch works even when the response body comes in as a stream (403 → ForbiddenError)."""
    httpserver.expect_request('/stream_dispatch').respond_with_handler(streaming_handler)
    client = ImpitHttpClient()

    with pytest.raises(ForbiddenError) as exc:
        client.call(method='GET', url=httpserver.url_for('/stream_dispatch'), stream=True)

    assert isinstance(exc.value, ApifyApiError)
    assert exc.value.status_code == 403
    assert exc.value.type == 'insufficient-permissions'


def test_apify_api_error_dispatches_5xx_to_server_error(httpserver: HTTPServer) -> None:
    """Any 5xx status falls under the ServerError subclass."""
    httpserver.expect_request('/server_error').respond_with_json(
        {'error': {'type': 'internal-error', 'message': 'boom'}}, status=503
    )
    client = ImpitHttpClient(max_retries=1)

    with pytest.raises(ServerError) as exc:
        client.call(method='GET', url=str(httpserver.url_for('/server_error')))

    assert isinstance(exc.value, ApifyApiError)
    assert exc.value.status_code == 503


def test_apify_api_error_falls_back_for_unmapped_status(httpserver: HTTPServer) -> None:
    """Statuses without a dedicated subclass fall back to the base ApifyApiError."""
    httpserver.expect_request('/unmapped').respond_with_json(
        {'error': {'type': 'whatever', 'message': 'nope'}}, status=418
    )
    client = ImpitHttpClient()

    with pytest.raises(ApifyApiError) as exc:
        client.call(method='GET', url=str(httpserver.url_for('/unmapped')))

    assert type(exc.value) is ApifyApiError
    assert exc.value.status_code == 418
    assert exc.value.type == 'whatever'


@pytest.mark.parametrize(
    ('status_code', 'expected_cls'),
    [
        pytest.param(400, InvalidRequestError, id='400 → InvalidRequestError'),
        pytest.param(401, UnauthorizedError, id='401 → UnauthorizedError'),
        pytest.param(403, ForbiddenError, id='403 → ForbiddenError'),
        pytest.param(404, NotFoundError, id='404 → NotFoundError'),
        pytest.param(409, ConflictError, id='409 → ConflictError'),
        pytest.param(429, RateLimitError, id='429 → RateLimitError'),
    ],
)
def test_apify_api_error_dispatches_all_mapped_statuses(
    httpserver: HTTPServer, status_code: int, expected_cls: type[ApifyApiError]
) -> None:
    """Every status in `_STATUS_TO_CLASS` dispatches to its matching subclass."""
    httpserver.expect_request('/dispatch_all').respond_with_json(
        {'error': {'type': 'some-type', 'message': 'msg'}}, status=status_code
    )
    # Use max_retries=1 so retryable statuses (429) don't loop during the test.
    client = ImpitHttpClient(max_retries=1)

    with pytest.raises(expected_cls) as exc:
        client.call(method='GET', url=str(httpserver.url_for('/dispatch_all')))

    assert type(exc.value) is expected_cls
    assert isinstance(exc.value, ApifyApiError)
    assert exc.value.status_code == status_code


def test_apify_api_error_falls_back_for_unparsable_body(httpserver: HTTPServer) -> None:
    """When the body can't be parsed, status-based dispatch still applies and `.type` is None."""
    httpserver.expect_request('/unparsable').respond_with_data('<not json>', status=418, content_type='text/html')
    client = ImpitHttpClient(max_retries=1)

    with pytest.raises(ApifyApiError) as exc:
        client.call(method='GET', url=str(httpserver.url_for('/unparsable')))

    assert type(exc.value) is ApifyApiError
    assert exc.value.type is None


def test_direct_get_returns_none_on_404(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    httpserver.expect_request('/v2/datasets/missing').respond_with_json(_not_found_body(), status=404)
    assert sync_client.dataset('missing').get() is None


async def test_direct_get_returns_none_on_404_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    httpserver.expect_request('/v2/datasets/missing').respond_with_json(_not_found_body(), status=404)
    assert await async_client.dataset('missing').get() is None


def test_chained_get_raises_on_404(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    httpserver.expect_request('/v2/actor-runs/missing-run/dataset').respond_with_json(_not_found_body(), status=404)
    with pytest.raises(NotFoundError):
        sync_client.run('missing-run').dataset().get()


async def test_chained_get_raises_on_404_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    httpserver.expect_request('/v2/actor-runs/missing-run/dataset').respond_with_json(_not_found_body(), status=404)
    with pytest.raises(NotFoundError):
        await async_client.run('missing-run').dataset().get()


def test_actor_last_run_dataset_get_raises_on_404(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """404 covers missing actor, missing last_run, or missing dataset — all three are indistinguishable from the single
    HTTP response (the client only hits the final URL), so `NotFoundError` propagates uniformly.
    """
    httpserver.expect_request('/v2/acts/actor-id/runs/last/dataset').respond_with_json(_not_found_body(), status=404)
    with pytest.raises(NotFoundError):
        sync_client.actor('actor-id').last_run().dataset().get()


async def test_actor_last_run_dataset_get_raises_on_404_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    httpserver.expect_request('/v2/acts/actor-id/runs/last/dataset').respond_with_json(_not_found_body(), status=404)
    with pytest.raises(NotFoundError):
        await async_client.actor('actor-id').last_run().dataset().get()


def test_actor_last_run_dataset_get_returns_dataset(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    httpserver.expect_request('/v2/acts/actor-id/runs/last/dataset').respond_with_json({'data': _DATASET_FIXTURE})
    dataset = sync_client.actor('actor-id').last_run().dataset().get()
    assert dataset is not None
    assert dataset.id == 'ds-1'


async def test_actor_last_run_dataset_get_returns_dataset_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    httpserver.expect_request('/v2/acts/actor-id/runs/last/dataset').respond_with_json({'data': _DATASET_FIXTURE})
    dataset = await async_client.actor('actor-id').last_run().dataset().get()
    assert dataset is not None
    assert dataset.id == 'ds-1'


def test_direct_delete_swallows_404(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    httpserver.expect_request('/v2/datasets/missing', method='DELETE').respond_with_json(_not_found_body(), status=404)
    sync_client.dataset('missing').delete()


async def test_direct_delete_swallows_404_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    httpserver.expect_request('/v2/datasets/missing', method='DELETE').respond_with_json(_not_found_body(), status=404)
    await async_client.dataset('missing').delete()


def test_chained_delete_raises_on_404(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    httpserver.expect_request('/v2/actor-runs/missing-run/dataset', method='DELETE').respond_with_json(
        _not_found_body(), status=404
    )
    with pytest.raises(NotFoundError):
        sync_client.run('missing-run').dataset().delete()


async def test_chained_delete_raises_on_404_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    httpserver.expect_request('/v2/actor-runs/missing-run/dataset', method='DELETE').respond_with_json(
        _not_found_body(), status=404
    )
    with pytest.raises(NotFoundError):
        await async_client.run('missing-run').dataset().delete()


def test_direct_log_get_returns_none_on_404(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    httpserver.expect_request('/v2/logs/missing').respond_with_json(_not_found_body(), status=404)
    assert sync_client.log('missing').get() is None


async def test_direct_log_get_returns_none_on_404_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    httpserver.expect_request('/v2/logs/missing').respond_with_json(_not_found_body(), status=404)
    assert await async_client.log('missing').get() is None


def test_chained_log_get_raises_on_404(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    httpserver.expect_request('/v2/actor-runs/missing-run/log').respond_with_json(_not_found_body(), status=404)
    with pytest.raises(NotFoundError):
        sync_client.run('missing-run').log().get()


async def test_chained_log_get_raises_on_404_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    httpserver.expect_request('/v2/actor-runs/missing-run/log').respond_with_json(_not_found_body(), status=404)
    with pytest.raises(NotFoundError):
        await async_client.run('missing-run').log().get()


@pytest.mark.parametrize(('path', 'method', 'call'), _SINGLETON_SUBPATH_404_CASES)
def test_singleton_subpath_raises_on_404(
    httpserver: HTTPServer,
    sync_client: ApifyClient,
    path: str,
    method: str,
    call: Callable[[ApifyClient], Any],
) -> None:
    httpserver.expect_request(path, method=method).respond_with_json(_not_found_body(), status=404)
    with pytest.raises(NotFoundError):
        call(sync_client)


@pytest.mark.parametrize(('path', 'method', 'call'), _SINGLETON_SUBPATH_404_CASES)
async def test_singleton_subpath_raises_on_404_async(
    httpserver: HTTPServer,
    async_client: ApifyClientAsync,
    path: str,
    method: str,
    call: Callable[[ApifyClientAsync], Awaitable[Any]],
) -> None:
    httpserver.expect_request(path, method=method).respond_with_json(_not_found_body(), status=404)
    with pytest.raises(NotFoundError):
        await call(async_client)

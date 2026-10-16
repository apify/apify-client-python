from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pytest
from werkzeug import Request, Response

if TYPE_CHECKING:
    from collections.abc import Callable

    from pytest_httpserver import HTTPServer

    from apify_client import ApifyClient, ApifyClientAsync

pytestmark = pytest.mark.usefixtures('http_client_classes')

_STORAGE_ID = 'test_storage_id'

_STORAGE_RESPONSE = {
    'data': {
        'id': _STORAGE_ID,
        'userId': 'test_user_id',
        'createdAt': '2026-08-01T10:00:00.000Z',
        'modifiedAt': '2026-08-01T10:00:00.000Z',
        'accessedAt': '2026-08-01T10:00:00.000Z',
        'itemCount': 0,
        'cleanItemCount': 0,
        'totalRequestCount': 0,
        'handledRequestCount': 0,
        'pendingRequestCount': 0,
        'hadMultipleClients': False,
        'consoleUrl': 'https://console.apify.com/storage/test_storage_id',
    }
}

_STORAGES = [
    pytest.param('datasets', 'dataset', id='dataset'),
    pytest.param('key-value-stores', 'key_value_store', id='key-value store'),
    pytest.param('request-queues', 'request_queue', id='request queue'),
]


def capture(captured: list[Request]) -> Callable[[Request], Response]:
    def handler(request: Request) -> Response:
        captured.append(request)
        return Response(json.dumps(_STORAGE_RESPONSE), status=200, mimetype='application/json')

    return handler


def body_of(request: Request) -> dict[str, Any]:
    return json.loads(request.get_data())


@pytest.mark.parametrize(('resource_path', 'client_method'), _STORAGES)
def test_update_sends_title(
    httpserver: HTTPServer, sync_client: ApifyClient, resource_path: str, client_method: str
) -> None:
    """`update` of each storage sends `title`."""
    captured: list[Request] = []
    httpserver.expect_request(f'/v2/{resource_path}/{_STORAGE_ID}', method='PUT').respond_with_handler(
        capture(captured)
    )

    getattr(sync_client, client_method)(_STORAGE_ID).update(title='My storage')

    assert len(captured) == 1
    assert body_of(captured[0]) == {'title': 'My storage'}


@pytest.mark.parametrize(('resource_path', 'client_method'), _STORAGES)
async def test_update_sends_title_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync, resource_path: str, client_method: str
) -> None:
    """Async `update` of each storage sends `title`."""
    captured: list[Request] = []
    httpserver.expect_request(f'/v2/{resource_path}/{_STORAGE_ID}', method='PUT').respond_with_handler(
        capture(captured)
    )

    await getattr(async_client, client_method)(_STORAGE_ID).update(title='My storage')

    assert len(captured) == 1
    assert body_of(captured[0]) == {'title': 'My storage'}

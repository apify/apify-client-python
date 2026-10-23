from __future__ import annotations

import gzip
import json
from typing import TYPE_CHECKING, Any

import pytest

from apify_client.errors import ApifyClientError, NotFoundError
from apify_client.http_compressors import GzipHttpCompressor

if TYPE_CHECKING:
    from pytest_httpserver import HTTPServer
    from werkzeug import Request

    from apify_client import ApifyClient, ApifyClientAsync
    from apify_client.http_compressors import HttpCompressor
    from apify_client.types import HttpCompressionAlgorithm

pytestmark = pytest.mark.usefixtures('http_client_classes')

_MOCKED_ACTOR_ID = 'test_actor_id'
_ACTOR_PATH = f'/v2/actors/{_MOCKED_ACTOR_ID}'
_SERVER_PREFIX = '/server'


def actor_response(server_url: str | None) -> dict[str, Any]:
    return {
        'data': {
            'id': _MOCKED_ACTOR_ID,
            'userId': 'test_user_id',
            'name': 'test-actor',
            'username': 'test-user',
            'isPublic': False,
            'createdAt': '2026-08-01T10:00:00.000Z',
            'modifiedAt': '2026-08-01T10:00:00.000Z',
            'stats': {},
            'versions': [],
            'defaultRunOptions': {},
            'standbyUrl': server_url,
        }
    }


def expect_server_actor(httpserver: HTTPServer) -> None:
    server_url = httpserver.url_for(_SERVER_PREFIX)
    httpserver.expect_request(_ACTOR_PATH, method='GET').respond_with_json(actor_response(server_url))


def server_requests(httpserver: HTTPServer) -> list[Request]:
    return [request for request, _ in httpserver.log if request.path.startswith(f'{_SERVER_PREFIX}/')]


def test_server_request_sends_request_to_server_url(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """The request goes to the server URL with the method, path, query, body, and the client's token."""
    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/search', method='POST').respond_with_json({'ok': True})

    response = sync_client.actor(_MOCKED_ACTOR_ID).server_request(
        '/search', method='POST', params={'q': 'apify'}, json={'limit': 5}
    )

    assert response.status_code == 200
    assert response.json() == {'ok': True}
    captured = server_requests(httpserver)
    assert len(captured) == 1
    assert captured[0].args.to_dict() == {'q': 'apify'}
    assert json.loads(captured[0].get_data()) == {'limit': 5}
    assert captured[0].headers['Authorization'] == 'Bearer test'


async def test_server_request_sends_request_to_server_url_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async variant of `test_server_request_sends_request_to_server_url`."""
    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/search', method='POST').respond_with_json({'ok': True})

    response = await async_client.actor(_MOCKED_ACTOR_ID).server_request(
        '/search', method='POST', params={'q': 'apify'}, json={'limit': 5}
    )

    assert response.status_code == 200
    assert response.json() == {'ok': True}
    captured = server_requests(httpserver)
    assert len(captured) == 1
    assert captured[0].args.to_dict() == {'q': 'apify'}
    assert json.loads(captured[0].get_data()) == {'limit': 5}
    assert captured[0].headers['Authorization'] == 'Bearer test'


def test_server_request_fetches_server_url_once(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """Later calls on the same client reuse the server URL fetched by the first one."""
    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/', method='GET').respond_with_json({'ok': True})
    actor_client = sync_client.actor(_MOCKED_ACTOR_ID)

    actor_client.server_request()
    actor_client.server_request()

    actor_gets = [request for request, _ in httpserver.log if request.path == _ACTOR_PATH]
    assert len(actor_gets) == 1


async def test_server_request_fetches_server_url_once_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async variant of `test_server_request_fetches_server_url_once`."""
    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/', method='GET').respond_with_json({'ok': True})
    actor_client = async_client.actor(_MOCKED_ACTOR_ID)

    await actor_client.server_request()
    await actor_client.server_request()

    actor_gets = [request for request, _ in httpserver.log if request.path == _ACTOR_PATH]
    assert len(actor_gets) == 1


@pytest.mark.parametrize(
    'path',
    [
        pytest.param('//evil.example/steal', id='protocol-relative'),
        pytest.param('@evil.example/steal', id='userinfo'),
        pytest.param('https://evil.example/steal', id='absolute url'),
    ],
)
def test_server_request_path_stays_on_server_host(httpserver: HTTPServer, sync_client: ApifyClient, path: str) -> None:
    """A path that looks like another host is still sent to the server, as a path on it."""
    expect_server_actor(httpserver)
    httpserver.no_handler_status_code = 200

    response = sync_client.actor(_MOCKED_ACTOR_ID).server_request(path)

    assert response.status_code == 200
    assert len(server_requests(httpserver)) == 1


def test_server_request_sends_body_uncompressed(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """A body large enough for the client to compress is sent as is, since servers may not decode it."""
    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/items', method='POST').respond_with_json({'ok': True})
    payload = {'items': ['x' * 100] * 100}

    sync_client.actor(_MOCKED_ACTOR_ID).server_request('/items', method='POST', json=payload)

    captured = server_requests(httpserver)
    assert len(captured) == 1
    assert 'Content-Encoding' not in captured[0].headers
    assert json.loads(captured[0].get_data()) == payload


async def test_server_request_sends_body_uncompressed_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async variant of `test_server_request_sends_body_uncompressed`."""
    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/items', method='POST').respond_with_json({'ok': True})
    payload = {'items': ['x' * 100] * 100}

    await async_client.actor(_MOCKED_ACTOR_ID).server_request('/items', method='POST', json=payload)

    captured = server_requests(httpserver)
    assert len(captured) == 1
    assert 'Content-Encoding' not in captured[0].headers
    assert json.loads(captured[0].get_data()) == payload


@pytest.mark.parametrize(
    'compression',
    [
        pytest.param('gzip', id='algorithm name'),
        pytest.param(GzipHttpCompressor(quality=1), id='compressor instance'),
    ],
)
def test_server_request_compresses_body_when_asked(
    httpserver: HTTPServer, sync_client: ApifyClient, compression: HttpCompressionAlgorithm | HttpCompressor
) -> None:
    """With `compression` set, a body large enough to compress is sent compressed and labeled with its encoding."""
    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/items', method='POST').respond_with_json({'ok': True})
    payload = {'items': ['x' * 100] * 100}

    sync_client.actor(_MOCKED_ACTOR_ID).server_request('/items', method='POST', json=payload, compression=compression)

    captured = server_requests(httpserver)
    assert len(captured) == 1
    assert captured[0].headers.get('Content-Encoding') == 'gzip'
    assert json.loads(gzip.decompress(captured[0].get_data())) == payload


async def test_server_request_compresses_body_when_asked_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async variant of `test_server_request_compresses_body_when_asked`."""
    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/items', method='POST').respond_with_json({'ok': True})
    payload = {'items': ['x' * 100] * 100}

    await async_client.actor(_MOCKED_ACTOR_ID).server_request('/items', method='POST', json=payload, compression='gzip')

    captured = server_requests(httpserver)
    assert len(captured) == 1
    assert captured[0].headers.get('Content-Encoding') == 'gzip'
    assert json.loads(gzip.decompress(captured[0].get_data())) == payload


def test_server_request_rejects_unknown_compression(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """An unsupported compression algorithm raises a `ValueError` without sending a request to the server."""
    expect_server_actor(httpserver)

    with pytest.raises(ValueError, match='Unsupported compression algorithm'):
        sync_client.actor(_MOCKED_ACTOR_ID).server_request('/items', method='POST', data='x', compression='zip')  # ty: ignore[invalid-argument-type]

    assert server_requests(httpserver) == []


def test_server_request_keeps_caller_content_encoding(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """A `Content-Encoding` header passed by the caller is sent as given, with the body untouched."""
    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/items', method='POST').respond_with_json({'ok': True})
    body = gzip.compress(b'x' * 2000)

    sync_client.actor(_MOCKED_ACTOR_ID).server_request(
        '/items', method='POST', headers={'content-encoding': 'gzip'}, data=body
    )

    captured = server_requests(httpserver)
    assert len(captured) == 1
    assert captured[0].headers.get('Content-Encoding') == 'gzip'
    assert captured[0].get_data() == body


def test_server_request_without_server_mode_raises(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """An Actor without Server mode enabled raises an error before any request to a server."""
    httpserver.expect_request(_ACTOR_PATH, method='GET').respond_with_json(actor_response(None))

    with pytest.raises(ApifyClientError, match='is not a Server Actor'):
        sync_client.actor(_MOCKED_ACTOR_ID).server_request()


async def test_server_request_without_server_mode_raises_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async variant of `test_server_request_without_server_mode_raises`."""
    httpserver.expect_request(_ACTOR_PATH, method='GET').respond_with_json(actor_response(None))

    with pytest.raises(ApifyClientError, match='is not a Server Actor'):
        await async_client.actor(_MOCKED_ACTOR_ID).server_request()


def test_server_request_missing_actor_raises_not_found(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """A missing Actor raises `NotFoundError`."""
    httpserver.expect_request(_ACTOR_PATH, method='GET').respond_with_json(
        {'error': {'type': 'record-not-found', 'message': 'Actor was not found'}}, status=404
    )

    with pytest.raises(NotFoundError):
        sync_client.actor(_MOCKED_ACTOR_ID).server_request()


def test_server_request_error_status_raises(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """An error status from the server raises the matching `ApifyApiError` subclass."""
    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/missing', method='GET').respond_with_data('Not here', status=404)

    with pytest.raises(NotFoundError, match='Not here'):
        sync_client.actor(_MOCKED_ACTOR_ID).server_request('/missing')

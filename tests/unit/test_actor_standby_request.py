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
_STANDBY_PREFIX = '/standby'


def actor_response(standby_url: str | None) -> dict[str, Any]:
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
            'standbyUrl': standby_url,
        }
    }


def expect_standby_actor(httpserver: HTTPServer) -> None:
    standby_url = httpserver.url_for(_STANDBY_PREFIX)
    httpserver.expect_request(_ACTOR_PATH, method='GET').respond_with_json(actor_response(standby_url))


def standby_requests(httpserver: HTTPServer) -> list[Request]:
    return [request for request, _ in httpserver.log if request.path.startswith(f'{_STANDBY_PREFIX}/')]


def test_standby_request_sends_request_to_standby_url(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """The request goes to the Standby URL with the method, path, query, body, and the client's token."""
    expect_standby_actor(httpserver)
    httpserver.expect_request(f'{_STANDBY_PREFIX}/search', method='POST').respond_with_json({'ok': True})

    response = sync_client.actor(_MOCKED_ACTOR_ID).standby_request(
        '/search', method='POST', params={'q': 'apify'}, json={'limit': 5}
    )

    assert response.status_code == 200
    assert response.json() == {'ok': True}
    captured = standby_requests(httpserver)
    assert len(captured) == 1
    assert captured[0].args.to_dict() == {'q': 'apify'}
    assert json.loads(captured[0].get_data()) == {'limit': 5}
    assert captured[0].headers['Authorization'] == 'Bearer test'


async def test_standby_request_sends_request_to_standby_url_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async variant of `test_standby_request_sends_request_to_standby_url`."""
    expect_standby_actor(httpserver)
    httpserver.expect_request(f'{_STANDBY_PREFIX}/search', method='POST').respond_with_json({'ok': True})

    response = await async_client.actor(_MOCKED_ACTOR_ID).standby_request(
        '/search', method='POST', params={'q': 'apify'}, json={'limit': 5}
    )

    assert response.status_code == 200
    assert response.json() == {'ok': True}
    captured = standby_requests(httpserver)
    assert len(captured) == 1
    assert captured[0].args.to_dict() == {'q': 'apify'}
    assert json.loads(captured[0].get_data()) == {'limit': 5}
    assert captured[0].headers['Authorization'] == 'Bearer test'


def test_standby_request_fetches_standby_url_once(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """Later calls on the same client reuse the Standby URL fetched by the first one."""
    expect_standby_actor(httpserver)
    httpserver.expect_request(f'{_STANDBY_PREFIX}/', method='GET').respond_with_json({'ok': True})
    actor_client = sync_client.actor(_MOCKED_ACTOR_ID)

    actor_client.standby_request()
    actor_client.standby_request()

    actor_gets = [request for request, _ in httpserver.log if request.path == _ACTOR_PATH]
    assert len(actor_gets) == 1


async def test_standby_request_fetches_standby_url_once_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async variant of `test_standby_request_fetches_standby_url_once`."""
    expect_standby_actor(httpserver)
    httpserver.expect_request(f'{_STANDBY_PREFIX}/', method='GET').respond_with_json({'ok': True})
    actor_client = async_client.actor(_MOCKED_ACTOR_ID)

    await actor_client.standby_request()
    await actor_client.standby_request()

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
def test_standby_request_path_stays_on_standby_host(
    httpserver: HTTPServer, sync_client: ApifyClient, path: str
) -> None:
    """A path that looks like another host is still sent to the Standby server, as a path on it."""
    expect_standby_actor(httpserver)
    httpserver.no_handler_status_code = 200

    response = sync_client.actor(_MOCKED_ACTOR_ID).standby_request(path)

    assert response.status_code == 200
    assert len(standby_requests(httpserver)) == 1


def test_standby_request_sends_body_uncompressed(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """A body large enough for the client to compress is sent as is, since Standby servers may not decode it."""
    expect_standby_actor(httpserver)
    httpserver.expect_request(f'{_STANDBY_PREFIX}/items', method='POST').respond_with_json({'ok': True})
    payload = {'items': ['x' * 100] * 100}

    sync_client.actor(_MOCKED_ACTOR_ID).standby_request('/items', method='POST', json=payload)

    captured = standby_requests(httpserver)
    assert len(captured) == 1
    assert 'Content-Encoding' not in captured[0].headers
    assert json.loads(captured[0].get_data()) == payload


async def test_standby_request_sends_body_uncompressed_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async variant of `test_standby_request_sends_body_uncompressed`."""
    expect_standby_actor(httpserver)
    httpserver.expect_request(f'{_STANDBY_PREFIX}/items', method='POST').respond_with_json({'ok': True})
    payload = {'items': ['x' * 100] * 100}

    await async_client.actor(_MOCKED_ACTOR_ID).standby_request('/items', method='POST', json=payload)

    captured = standby_requests(httpserver)
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
def test_standby_request_compresses_body_when_asked(
    httpserver: HTTPServer, sync_client: ApifyClient, compression: HttpCompressionAlgorithm | HttpCompressor
) -> None:
    """With `compression` set, a body large enough to compress is sent compressed and labeled with its encoding."""
    expect_standby_actor(httpserver)
    httpserver.expect_request(f'{_STANDBY_PREFIX}/items', method='POST').respond_with_json({'ok': True})
    payload = {'items': ['x' * 100] * 100}

    sync_client.actor(_MOCKED_ACTOR_ID).standby_request('/items', method='POST', json=payload, compression=compression)

    captured = standby_requests(httpserver)
    assert len(captured) == 1
    assert captured[0].headers.get('Content-Encoding') == 'gzip'
    assert json.loads(gzip.decompress(captured[0].get_data())) == payload


async def test_standby_request_compresses_body_when_asked_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async variant of `test_standby_request_compresses_body_when_asked`."""
    expect_standby_actor(httpserver)
    httpserver.expect_request(f'{_STANDBY_PREFIX}/items', method='POST').respond_with_json({'ok': True})
    payload = {'items': ['x' * 100] * 100}

    await async_client.actor(_MOCKED_ACTOR_ID).standby_request(
        '/items', method='POST', json=payload, compression='gzip'
    )

    captured = standby_requests(httpserver)
    assert len(captured) == 1
    assert captured[0].headers.get('Content-Encoding') == 'gzip'
    assert json.loads(gzip.decompress(captured[0].get_data())) == payload


def test_standby_request_rejects_unknown_compression(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """An unsupported compression algorithm raises a `ValueError` without sending a request to the Standby server."""
    expect_standby_actor(httpserver)

    with pytest.raises(ValueError, match='Unsupported compression algorithm'):
        sync_client.actor(_MOCKED_ACTOR_ID).standby_request('/items', method='POST', data='x', compression='zip')  # ty: ignore[invalid-argument-type]

    assert standby_requests(httpserver) == []


def test_standby_request_keeps_caller_content_encoding(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """A `Content-Encoding` header passed by the caller is sent as given, with the body untouched."""
    expect_standby_actor(httpserver)
    httpserver.expect_request(f'{_STANDBY_PREFIX}/items', method='POST').respond_with_json({'ok': True})
    body = gzip.compress(b'x' * 2000)

    sync_client.actor(_MOCKED_ACTOR_ID).standby_request(
        '/items', method='POST', headers={'content-encoding': 'gzip'}, data=body
    )

    captured = standby_requests(httpserver)
    assert len(captured) == 1
    assert captured[0].headers.get('Content-Encoding') == 'gzip'
    assert captured[0].get_data() == body


def test_standby_request_without_standby_mode_raises(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """An Actor without Standby mode enabled raises an error before any request to a Standby server."""
    httpserver.expect_request(_ACTOR_PATH, method='GET').respond_with_json(actor_response(None))

    with pytest.raises(ApifyClientError, match='does not have Standby mode enabled'):
        sync_client.actor(_MOCKED_ACTOR_ID).standby_request()


async def test_standby_request_without_standby_mode_raises_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async variant of `test_standby_request_without_standby_mode_raises`."""
    httpserver.expect_request(_ACTOR_PATH, method='GET').respond_with_json(actor_response(None))

    with pytest.raises(ApifyClientError, match='does not have Standby mode enabled'):
        await async_client.actor(_MOCKED_ACTOR_ID).standby_request()


def test_standby_request_missing_actor_raises_not_found(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """A missing Actor raises `NotFoundError`."""
    httpserver.expect_request(_ACTOR_PATH, method='GET').respond_with_json(
        {'error': {'type': 'record-not-found', 'message': 'Actor was not found'}}, status=404
    )

    with pytest.raises(NotFoundError):
        sync_client.actor(_MOCKED_ACTOR_ID).standby_request()


def test_standby_request_error_status_raises(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """An error status from the Standby server raises the matching `ApifyApiError` subclass."""
    expect_standby_actor(httpserver)
    httpserver.expect_request(f'{_STANDBY_PREFIX}/missing', method='GET').respond_with_data('Not here', status=404)

    with pytest.raises(NotFoundError, match='Not here'):
        sync_client.actor(_MOCKED_ACTOR_ID).standby_request('/missing')

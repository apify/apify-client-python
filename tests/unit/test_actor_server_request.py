from __future__ import annotations

import gzip
import json
from typing import TYPE_CHECKING, Any

import pytest
from werkzeug import Response

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


def actor_response(server_url: str | None, **extra_fields: Any) -> dict[str, Any]:
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
            **extra_fields,
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


def test_get_server_url_returns_standby_url(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`get_server_url` returns the Actor's `standby_url` and fetches it from the API only once."""
    expect_server_actor(httpserver)
    actor_client = sync_client.actor(_MOCKED_ACTOR_ID)

    assert actor_client.get_server_url() == httpserver.url_for(_SERVER_PREFIX)
    assert actor_client.get_server_url() == httpserver.url_for(_SERVER_PREFIX)

    actor_gets = [request for request, _ in httpserver.log if request.path == _ACTOR_PATH]
    assert len(actor_gets) == 1


async def test_get_server_url_returns_standby_url_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    """Async variant of `test_get_server_url_returns_standby_url`."""
    expect_server_actor(httpserver)
    actor_client = async_client.actor(_MOCKED_ACTOR_ID)

    assert await actor_client.get_server_url() == httpserver.url_for(_SERVER_PREFIX)
    assert await actor_client.get_server_url() == httpserver.url_for(_SERVER_PREFIX)

    actor_gets = [request for request, _ in httpserver.log if request.path == _ACTOR_PATH]
    assert len(actor_gets) == 1


def test_get_server_url_without_server_mode_raises(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`get_server_url` raises for an Actor without a server interface."""
    httpserver.expect_request(_ACTOR_PATH, method='GET').respond_with_json(actor_response(None))

    with pytest.raises(ApifyClientError, match='is not a Server Actor'):
        sync_client.actor(_MOCKED_ACTOR_ID).get_server_url()


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
    """An Actor without a server interface raises an error before any request to a server."""
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


_OPENAPI_SPEC = {'openapi': '3.0.0', 'info': {'title': 'Test server', 'version': '1.0.0'}, 'paths': {}}
_TAGGED_BUILDS = {
    'latest': {'buildId': 'latest_build_id', 'buildNumber': '0.0.2'},
    'beta': {'buildId': 'beta_build_id', 'buildNumber': '0.0.3'},
}


def build_response(build_id: str, actor_definition: dict[str, Any] | None) -> dict[str, Any]:
    return {
        'data': {
            'id': build_id,
            'actId': _MOCKED_ACTOR_ID,
            'userId': 'test_user_id',
            'startedAt': '2026-08-01T10:00:00.000Z',
            'status': 'SUCCEEDED',
            'meta': {'origin': 'API'},
            'buildNumber': '0.0.1',
            'actorDefinition': actor_definition,
        }
    }


def expect_builds_list(httpserver: HTTPServer, builds: dict[str, str]) -> None:
    """Serve the Actor's builds list as one page, so a request for a later offset gets no items."""
    items = [
        {
            'id': build_id,
            'status': 'SUCCEEDED',
            'startedAt': '2026-08-01T10:00:00.000Z',
            'usageTotalUsd': 0.01,
            'buildNumber': build_number,
        }
        for build_id, build_number in builds.items()
    ]

    def handler(request: Request) -> Response:
        offset = int(request.args.get('offset', 0))
        page = items[offset:]
        data = {'total': len(items), 'offset': offset, 'limit': 1000, 'desc': True, 'count': len(page), 'items': page}
        return Response(json.dumps({'data': data}), content_type='application/json')

    httpserver.expect_request(f'{_ACTOR_PATH}/builds', method='GET').respond_with_handler(handler)


def expect_server_actor_with_build(
    httpserver: HTTPServer, *, standby_build: str | None, build_id: str, actor_definition: dict[str, Any] | None
) -> None:
    actor_standby = {'isEnabled': True, 'build': standby_build}
    httpserver.expect_request(_ACTOR_PATH, method='GET').respond_with_json(
        actor_response(httpserver.url_for(_SERVER_PREFIX), taggedBuilds=_TAGGED_BUILDS, actorStandby=actor_standby)
    )
    httpserver.expect_request(f'/v2/actor-builds/{build_id}', method='GET').respond_with_json(
        build_response(build_id, actor_definition)
    )


@pytest.mark.parametrize(
    ('standby_build', 'build_id'),
    [
        pytest.param(None, 'latest_build_id', id='no build set uses latest'),
        pytest.param('beta', 'beta_build_id', id='build tag'),
    ],
)
def test_get_server_openapi_spec_from_tagged_build(
    httpserver: HTTPServer, sync_client: ApifyClient, standby_build: str | None, build_id: str
) -> None:
    """The specification comes from the web server schema of the tagged build that serves the server interface."""
    expect_server_actor_with_build(
        httpserver, standby_build=standby_build, build_id=build_id, actor_definition={'webServerSchema': _OPENAPI_SPEC}
    )

    assert sync_client.actor(_MOCKED_ACTOR_ID).get_server_openapi_spec() == _OPENAPI_SPEC


async def test_get_server_openapi_spec_from_tagged_build_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async variant of `test_get_server_openapi_spec_from_tagged_build`."""
    expect_server_actor_with_build(
        httpserver, standby_build='beta', build_id='beta_build_id', actor_definition={'webServerSchema': _OPENAPI_SPEC}
    )

    assert await async_client.actor(_MOCKED_ACTOR_ID).get_server_openapi_spec() == _OPENAPI_SPEC


def test_get_server_openapi_spec_from_build_number(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """A build number set for the server interface is looked up in the Actor's builds."""
    expect_server_actor_with_build(
        httpserver, standby_build='0.0.1', build_id='old_build_id', actor_definition={'webServerSchema': _OPENAPI_SPEC}
    )
    expect_builds_list(httpserver, {'latest_build_id': '0.0.2', 'old_build_id': '0.0.1'})

    assert sync_client.actor(_MOCKED_ACTOR_ID).get_server_openapi_spec() == _OPENAPI_SPEC


async def test_get_server_openapi_spec_from_build_number_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async variant of `test_get_server_openapi_spec_from_build_number`."""
    expect_server_actor_with_build(
        httpserver, standby_build='0.0.1', build_id='old_build_id', actor_definition={'webServerSchema': _OPENAPI_SPEC}
    )
    expect_builds_list(httpserver, {'latest_build_id': '0.0.2', 'old_build_id': '0.0.1'})

    assert await async_client.actor(_MOCKED_ACTOR_ID).get_server_openapi_spec() == _OPENAPI_SPEC


@pytest.mark.parametrize(
    'actor_definition',
    [
        pytest.param({'name': 'test-actor'}, id='no web server schema'),
        pytest.param(None, id='no actor definition'),
    ],
)
def test_get_server_openapi_spec_without_schema_returns_none(
    httpserver: HTTPServer, sync_client: ApifyClient, actor_definition: dict[str, Any] | None
) -> None:
    """A build without a web server schema has no specification to return."""
    expect_server_actor_with_build(
        httpserver, standby_build=None, build_id='latest_build_id', actor_definition=actor_definition
    )

    assert sync_client.actor(_MOCKED_ACTOR_ID).get_server_openapi_spec() is None


def test_get_server_openapi_spec_unknown_build_raises(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """A server interface build that is neither a tag nor a listed build number raises an error."""
    expect_server_actor_with_build(httpserver, standby_build='9.9.9', build_id='unused_build_id', actor_definition=None)
    expect_builds_list(httpserver, {'latest_build_id': '0.0.2'})

    with pytest.raises(ApifyClientError, match='does not exist'):
        sync_client.actor(_MOCKED_ACTOR_ID).get_server_openapi_spec()


def test_get_server_openapi_spec_without_server_mode_raises(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`get_server_openapi_spec` raises for an Actor without a server interface."""
    httpserver.expect_request(_ACTOR_PATH, method='GET').respond_with_json(actor_response(None))

    with pytest.raises(ApifyClientError, match='is not a Server Actor'):
        sync_client.actor(_MOCKED_ACTOR_ID).get_server_openapi_spec()


def test_standby_aliases_warn_and_delegate(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """The deprecated Standby-named methods emit a `DeprecationWarning` pointing at the caller and return the same."""
    expect_server_actor_with_build(
        httpserver, standby_build=None, build_id='latest_build_id', actor_definition={'webServerSchema': _OPENAPI_SPEC}
    )
    httpserver.expect_request(f'{_SERVER_PREFIX}/search', method='GET').respond_with_json({'ok': True})
    actor_client = sync_client.actor(_MOCKED_ACTOR_ID)

    with pytest.warns(DeprecationWarning, match='`get_standby_url` is deprecated') as record:
        assert actor_client.get_standby_url() == httpserver.url_for(_SERVER_PREFIX)
    assert record[0].filename == __file__

    with pytest.warns(DeprecationWarning, match='`get_standby_openapi_spec` is deprecated') as record:
        assert actor_client.get_standby_openapi_spec() == _OPENAPI_SPEC
    assert record[0].filename == __file__

    with pytest.warns(DeprecationWarning, match='`standby_request` is deprecated') as record:
        response = actor_client.standby_request('/search', params={'q': 'apify'})
    assert record[0].filename == __file__
    assert response.json() == {'ok': True}
    assert server_requests(httpserver)[0].args.to_dict() == {'q': 'apify'}


async def test_standby_aliases_warn_and_delegate_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    """Async variant of `test_standby_aliases_warn_and_delegate`."""
    expect_server_actor_with_build(
        httpserver, standby_build=None, build_id='latest_build_id', actor_definition={'webServerSchema': _OPENAPI_SPEC}
    )
    httpserver.expect_request(f'{_SERVER_PREFIX}/search', method='GET').respond_with_json({'ok': True})
    actor_client = async_client.actor(_MOCKED_ACTOR_ID)

    with pytest.warns(DeprecationWarning, match='`get_standby_url` is deprecated') as record:
        assert await actor_client.get_standby_url() == httpserver.url_for(_SERVER_PREFIX)
    assert record[0].filename == __file__

    with pytest.warns(DeprecationWarning, match='`get_standby_openapi_spec` is deprecated') as record:
        assert await actor_client.get_standby_openapi_spec() == _OPENAPI_SPEC
    assert record[0].filename == __file__

    with pytest.warns(DeprecationWarning, match='`standby_request` is deprecated') as record:
        response = await actor_client.standby_request('/search', params={'q': 'apify'})
    assert record[0].filename == __file__
    assert response.json() == {'ok': True}
    assert server_requests(httpserver)[0].args.to_dict() == {'q': 'apify'}

from __future__ import annotations

import gzip
import json
from datetime import timedelta
from typing import TYPE_CHECKING, Any
from unittest.mock import Mock

import pytest
from werkzeug import Request, Response

from apify_client import ApifyClient
from apify_client.errors import ApifyClientError, NotFoundError
from apify_client.http_compressors import GzipHttpCompressor

if TYPE_CHECKING:
    from pytest_httpserver import HTTPServer

    from apify_client import ApifyClientAsync
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


def test_request_sends_request_to_server_url(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """The request goes to the server URL with the method, path, query, body, and the client's token."""
    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/search', method='POST').respond_with_json({'ok': True})

    response = (
        sync_client.actor(_MOCKED_ACTOR_ID)
        .server()
        .request('/search', method='POST', params={'q': 'apify'}, json={'limit': 5})
    )

    assert response.status_code == 200
    assert response.json() == {'ok': True}
    captured = server_requests(httpserver)
    assert len(captured) == 1
    assert captured[0].args.to_dict() == {'q': 'apify'}
    assert json.loads(captured[0].get_data()) == {'limit': 5}
    assert captured[0].headers['X-Apify-Authorization'] == 'Bearer test'
    assert 'Authorization' not in captured[0].headers


async def test_request_sends_request_to_server_url_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async variant of `test_request_sends_request_to_server_url`."""
    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/search', method='POST').respond_with_json({'ok': True})

    response = (
        await async_client.actor(_MOCKED_ACTOR_ID)
        .server()
        .request('/search', method='POST', params={'q': 'apify'}, json={'limit': 5})
    )

    assert response.status_code == 200
    assert response.json() == {'ok': True}
    captured = server_requests(httpserver)
    assert len(captured) == 1
    assert captured[0].args.to_dict() == {'q': 'apify'}
    assert json.loads(captured[0].get_data()) == {'limit': 5}
    assert captured[0].headers['X-Apify-Authorization'] == 'Bearer test'
    assert 'Authorization' not in captured[0].headers


def test_request_sends_caller_authorization_header(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """An `Authorization` header passed by the caller reaches the server as it is, next to the client's token."""
    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/', method='GET').respond_with_json({'ok': True})

    sync_client.actor(_MOCKED_ACTOR_ID).server().request(headers={'Authorization': 'Bearer actor-token'})

    captured = server_requests(httpserver)
    assert captured[0].headers['Authorization'] == 'Bearer actor-token'
    assert captured[0].headers['X-Apify-Authorization'] == 'Bearer test'


def test_request_fetches_server_url_once(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """Later calls on the same client reuse the server URL fetched by the first one."""
    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/', method='GET').respond_with_json({'ok': True})
    actor_client = sync_client.actor(_MOCKED_ACTOR_ID)

    actor_client.server().request()
    actor_client.server().request()

    actor_gets = [request for request, _ in httpserver.log if request.path == _ACTOR_PATH]
    assert len(actor_gets) == 1


async def test_request_fetches_server_url_once_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    """Async variant of `test_request_fetches_server_url_once`."""
    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/', method='GET').respond_with_json({'ok': True})
    actor_client = async_client.actor(_MOCKED_ACTOR_ID)

    await actor_client.server().request()
    await actor_client.server().request()

    actor_gets = [request for request, _ in httpserver.log if request.path == _ACTOR_PATH]
    assert len(actor_gets) == 1


def test_get_url_returns_standby_url(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`get_url` returns the Actor's `standby_url` and fetches it from the API only once."""
    expect_server_actor(httpserver)
    actor_client = sync_client.actor(_MOCKED_ACTOR_ID)

    assert actor_client.server().get_url() == httpserver.url_for(_SERVER_PREFIX)
    assert actor_client.server().get_url() == httpserver.url_for(_SERVER_PREFIX)

    actor_gets = [request for request, _ in httpserver.log if request.path == _ACTOR_PATH]
    assert len(actor_gets) == 1


async def test_get_url_returns_standby_url_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    """Async variant of `test_get_url_returns_standby_url`."""
    expect_server_actor(httpserver)
    actor_client = async_client.actor(_MOCKED_ACTOR_ID)

    assert await actor_client.server().get_url() == httpserver.url_for(_SERVER_PREFIX)
    assert await actor_client.server().get_url() == httpserver.url_for(_SERVER_PREFIX)

    actor_gets = [request for request, _ in httpserver.log if request.path == _ACTOR_PATH]
    assert len(actor_gets) == 1


def test_get_url_without_server_mode_raises(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`get_url` raises for an Actor without a server interface."""
    httpserver.expect_request(_ACTOR_PATH, method='GET').respond_with_json(actor_response(None))

    with pytest.raises(ApifyClientError, match='is not a Server Actor'):
        sync_client.actor(_MOCKED_ACTOR_ID).server().get_url()


@pytest.mark.parametrize(
    'path',
    [
        pytest.param('//evil.example/steal', id='protocol-relative'),
        pytest.param('@evil.example/steal', id='userinfo'),
        pytest.param('https://evil.example/steal', id='absolute url'),
    ],
)
def test_request_path_stays_on_server_host(httpserver: HTTPServer, sync_client: ApifyClient, path: str) -> None:
    """A path that looks like another host is still sent to the server, as a path on it."""
    expect_server_actor(httpserver)
    httpserver.no_handler_status_code = 200

    response = sync_client.actor(_MOCKED_ACTOR_ID).server().request(path)

    assert response.status_code == 200
    assert len(server_requests(httpserver)) == 1


def test_request_sends_body_uncompressed(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """A body large enough for the client to compress is sent as is, since servers may not decode it."""
    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/items', method='POST').respond_with_json({'ok': True})
    payload = {'items': ['x' * 100] * 100}

    sync_client.actor(_MOCKED_ACTOR_ID).server().request('/items', method='POST', json=payload)

    captured = server_requests(httpserver)
    assert len(captured) == 1
    assert 'Content-Encoding' not in captured[0].headers
    assert json.loads(captured[0].get_data()) == payload


async def test_request_sends_body_uncompressed_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    """Async variant of `test_request_sends_body_uncompressed`."""
    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/items', method='POST').respond_with_json({'ok': True})
    payload = {'items': ['x' * 100] * 100}

    await async_client.actor(_MOCKED_ACTOR_ID).server().request('/items', method='POST', json=payload)

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
def test_request_compresses_body_when_asked(
    httpserver: HTTPServer, sync_client: ApifyClient, compression: HttpCompressionAlgorithm | HttpCompressor
) -> None:
    """With `compression` set, a body large enough to compress is sent compressed and labeled with its encoding."""
    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/items', method='POST').respond_with_json({'ok': True})
    payload = {'items': ['x' * 100] * 100}

    sync_client.actor(_MOCKED_ACTOR_ID).server().request('/items', method='POST', json=payload, compression=compression)

    captured = server_requests(httpserver)
    assert len(captured) == 1
    assert captured[0].headers.get('Content-Encoding') == 'gzip'
    assert json.loads(gzip.decompress(captured[0].get_data())) == payload


async def test_request_compresses_body_when_asked_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    """Async variant of `test_request_compresses_body_when_asked`."""
    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/items', method='POST').respond_with_json({'ok': True})
    payload = {'items': ['x' * 100] * 100}

    await (
        async_client.actor(_MOCKED_ACTOR_ID).server().request('/items', method='POST', json=payload, compression='gzip')
    )

    captured = server_requests(httpserver)
    assert len(captured) == 1
    assert captured[0].headers.get('Content-Encoding') == 'gzip'
    assert json.loads(gzip.decompress(captured[0].get_data())) == payload


def test_request_rejects_unknown_compression(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """An unsupported compression algorithm raises a `ValueError` without sending a request to the server."""
    expect_server_actor(httpserver)

    with pytest.raises(ValueError, match='Unsupported compression algorithm'):
        sync_client.actor(_MOCKED_ACTOR_ID).server().request('/items', method='POST', data='x', compression='zip')  # ty: ignore[invalid-argument-type]

    assert server_requests(httpserver) == []


def test_request_keeps_caller_content_encoding(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """A `Content-Encoding` header passed by the caller is sent as given, with the body untouched."""
    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/items', method='POST').respond_with_json({'ok': True})
    body = gzip.compress(b'x' * 2000)

    sync_client.actor(_MOCKED_ACTOR_ID).server().request(
        '/items', method='POST', headers={'content-encoding': 'gzip'}, data=body
    )

    captured = server_requests(httpserver)
    assert len(captured) == 1
    assert captured[0].headers.get('Content-Encoding') == 'gzip'
    assert captured[0].get_data() == body


def test_request_without_server_mode_raises(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """An Actor without a server interface raises an error before any request to a server."""
    httpserver.expect_request(_ACTOR_PATH, method='GET').respond_with_json(actor_response(None))

    with pytest.raises(ApifyClientError, match='is not a Server Actor'):
        sync_client.actor(_MOCKED_ACTOR_ID).server().request()


async def test_request_without_server_mode_raises_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    """Async variant of `test_request_without_server_mode_raises`."""
    httpserver.expect_request(_ACTOR_PATH, method='GET').respond_with_json(actor_response(None))

    with pytest.raises(ApifyClientError, match='is not a Server Actor'):
        await async_client.actor(_MOCKED_ACTOR_ID).server().request()


def test_request_missing_actor_raises_not_found(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """A missing Actor raises `NotFoundError`."""
    httpserver.expect_request(_ACTOR_PATH, method='GET').respond_with_json(
        {'error': {'type': 'record-not-found', 'message': 'Actor was not found'}}, status=404
    )

    with pytest.raises(NotFoundError):
        sync_client.actor(_MOCKED_ACTOR_ID).server().request()


def test_request_returns_error_response(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """An error response of the server comes back as it is."""
    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/missing', method='GET').respond_with_data('Not here', status=404)

    response = sync_client.actor(_MOCKED_ACTOR_ID).server().request('/missing')

    assert response.status_code == 404
    assert response.text == 'Not here'


async def test_request_returns_error_response_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    """Async variant of `test_request_returns_error_response`."""
    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/missing', method='GET').respond_with_data('Not here', status=404)

    response = await async_client.actor(_MOCKED_ACTOR_ID).server().request('/missing')

    assert response.status_code == 404
    assert response.text == 'Not here'


def test_request_returns_response_unread_with_stream(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """With `stream`, the body can be read in chunks."""
    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/', method='GET').respond_with_data(b'x' * 10_000)

    response = sync_client.actor(_MOCKED_ACTOR_ID).server().request(stream=True)
    try:
        assert b''.join(response.iter_bytes()) == b'x' * 10_000
    finally:
        response.close()


async def test_request_returns_response_unread_with_stream_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async variant of `test_request_returns_response_unread_with_stream`."""
    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/', method='GET').respond_with_data(b'x' * 10_000)

    response = await async_client.actor(_MOCKED_ACTOR_ID).server().request(stream=True)
    try:
        assert b''.join([chunk async for chunk in response.aiter_bytes()]) == b'x' * 10_000
    finally:
        await response.aclose()


def expect_flaky_server(httpserver: HTTPServer, statuses: list[int]) -> None:
    """Answer `/flaky` with each of `statuses` in turn, then with 200."""
    remaining = list(statuses)

    def handler(_request: Request) -> Response:
        status = remaining.pop(0) if remaining else 200
        return Response(json.dumps({'status': status}), status=status, content_type='application/json')

    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/flaky').respond_with_handler(handler)


def retrying_client(httpserver: HTTPServer, max_retries: int) -> ApifyClient:
    api_url = httpserver.url_for('/').removesuffix('/')
    return ApifyClient(token='test', api_url=api_url, max_retries=max_retries, min_delay_between_retries=timedelta(0))


@pytest.mark.parametrize('status', [pytest.param(429, id='rate limit'), pytest.param(503, id='service unavailable')])
def test_request_retries_platform_statuses(httpserver: HTTPServer, status: int) -> None:
    """A rate-limit or Service Unavailable response is retried."""
    expect_flaky_server(httpserver, [status, status])

    response = retrying_client(httpserver, max_retries=2).actor(_MOCKED_ACTOR_ID).server().request('/flaky')

    assert response.status_code == 200
    assert len(server_requests(httpserver)) == 3


def test_request_returns_last_retried_response(httpserver: HTTPServer) -> None:
    """Once the retries run out, the last retried response comes back."""
    expect_flaky_server(httpserver, [503, 503, 503])

    response = retrying_client(httpserver, max_retries=1).actor(_MOCKED_ACTOR_ID).server().request('/flaky')

    assert response.status_code == 503
    assert len(server_requests(httpserver)) == 2


def test_request_does_not_retry_other_server_errors(httpserver: HTTPServer) -> None:
    """A server error other than 503 comes back after a single attempt."""
    expect_flaky_server(httpserver, [500])

    client = retrying_client(httpserver, max_retries=2)
    response = client.actor(_MOCKED_ACTOR_ID).server().request('/flaky', method='POST', json={'a': 1})

    assert response.status_code == 500
    assert len(server_requests(httpserver)) == 1


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
def test_get_openapi_spec_from_tagged_build(
    httpserver: HTTPServer, sync_client: ApifyClient, standby_build: str | None, build_id: str
) -> None:
    """The specification comes from the web server schema of the tagged build that serves the server interface."""
    expect_server_actor_with_build(
        httpserver, standby_build=standby_build, build_id=build_id, actor_definition={'webServerSchema': _OPENAPI_SPEC}
    )

    assert sync_client.actor(_MOCKED_ACTOR_ID).server().get_openapi_spec() == _OPENAPI_SPEC


async def test_get_openapi_spec_from_tagged_build_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    """Async variant of `test_get_openapi_spec_from_tagged_build`."""
    expect_server_actor_with_build(
        httpserver, standby_build='beta', build_id='beta_build_id', actor_definition={'webServerSchema': _OPENAPI_SPEC}
    )

    assert await async_client.actor(_MOCKED_ACTOR_ID).server().get_openapi_spec() == _OPENAPI_SPEC


def test_get_openapi_spec_from_build_number(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """A build number set for the server interface is looked up in the Actor's builds."""
    expect_server_actor_with_build(
        httpserver, standby_build='0.0.1', build_id='old_build_id', actor_definition={'webServerSchema': _OPENAPI_SPEC}
    )
    expect_builds_list(httpserver, {'latest_build_id': '0.0.2', 'old_build_id': '0.0.1'})

    assert sync_client.actor(_MOCKED_ACTOR_ID).server().get_openapi_spec() == _OPENAPI_SPEC


def test_get_openapi_spec_passes_timeout_to_every_api_call(
    httpserver: HTTPServer, sync_client: ApifyClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The timeout of `get_openapi_spec` applies to fetching the Actor, listing its builds, and fetching the build."""
    expect_server_actor_with_build(
        httpserver, standby_build='0.0.1', build_id='old_build_id', actor_definition={'webServerSchema': _OPENAPI_SPEC}
    )
    expect_builds_list(httpserver, {'old_build_id': '0.0.1'})
    call = Mock(wraps=sync_client.http_client.call)
    monkeypatch.setattr(sync_client.http_client, 'call', call)

    sync_client.actor(_MOCKED_ACTOR_ID).server().get_openapi_spec(timeout='long')

    assert [call_args.kwargs['timeout'] for call_args in call.call_args_list] == ['long', 'long', 'long']


def test_get_url_passes_timeout(
    httpserver: HTTPServer, sync_client: ApifyClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The timeout of `get_url` applies to fetching the Actor."""
    expect_server_actor(httpserver)
    call = Mock(wraps=sync_client.http_client.call)
    monkeypatch.setattr(sync_client.http_client, 'call', call)

    sync_client.actor(_MOCKED_ACTOR_ID).server().get_url(timeout='medium')

    assert call.call_args.kwargs['timeout'] == 'medium'


async def test_get_openapi_spec_from_build_number_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    """Async variant of `test_get_openapi_spec_from_build_number`."""
    expect_server_actor_with_build(
        httpserver, standby_build='0.0.1', build_id='old_build_id', actor_definition={'webServerSchema': _OPENAPI_SPEC}
    )
    expect_builds_list(httpserver, {'latest_build_id': '0.0.2', 'old_build_id': '0.0.1'})

    assert await async_client.actor(_MOCKED_ACTOR_ID).server().get_openapi_spec() == _OPENAPI_SPEC


@pytest.mark.parametrize(
    'actor_definition',
    [
        pytest.param({'name': 'test-actor'}, id='no web server schema'),
        pytest.param(None, id='no actor definition'),
    ],
)
def test_get_openapi_spec_without_schema_returns_none(
    httpserver: HTTPServer, sync_client: ApifyClient, actor_definition: dict[str, Any] | None
) -> None:
    """A build without a web server schema has no specification to return."""
    expect_server_actor_with_build(
        httpserver, standby_build=None, build_id='latest_build_id', actor_definition=actor_definition
    )

    assert sync_client.actor(_MOCKED_ACTOR_ID).server().get_openapi_spec() is None


def test_get_openapi_spec_unknown_build_raises(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """A server interface build that is neither a tag nor a listed build number raises an error."""
    expect_server_actor_with_build(httpserver, standby_build='9.9.9', build_id='unused_build_id', actor_definition=None)
    expect_builds_list(httpserver, {'latest_build_id': '0.0.2'})

    with pytest.raises(ApifyClientError, match='does not exist'):
        sync_client.actor(_MOCKED_ACTOR_ID).server().get_openapi_spec()


def test_get_openapi_spec_without_server_mode_raises(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`get_openapi_spec` raises for an Actor without a server interface."""
    httpserver.expect_request(_ACTOR_PATH, method='GET').respond_with_json(actor_response(None))

    with pytest.raises(ApifyClientError, match='is not a Server Actor'):
        sync_client.actor(_MOCKED_ACTOR_ID).server().get_openapi_spec()


def test_standby_alias_warns_and_returns_server_client(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """The deprecated `standby` emits a `DeprecationWarning` pointing at the caller and returns the server client."""
    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/search', method='GET').respond_with_json({'ok': True})
    actor_client = sync_client.actor(_MOCKED_ACTOR_ID)

    with pytest.warns(DeprecationWarning, match='`standby` is deprecated') as record:
        standby_client = actor_client.standby()

    assert record[0].filename == __file__
    assert standby_client is actor_client.server()
    assert standby_client.request('/search').json() == {'ok': True}


async def test_standby_alias_warns_and_returns_server_client_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async variant of `test_standby_alias_warns_and_returns_server_client`."""
    expect_server_actor(httpserver)
    httpserver.expect_request(f'{_SERVER_PREFIX}/search', method='GET').respond_with_json({'ok': True})
    actor_client = async_client.actor(_MOCKED_ACTOR_ID)

    with pytest.warns(DeprecationWarning, match='`standby` is deprecated') as record:
        standby_client = actor_client.standby()

    assert record[0].filename == __file__
    assert standby_client is actor_client.server()
    response = await standby_client.request('/search')
    assert response.json() == {'ok': True}

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

_MOCKED_ACTOR_ID = 'test_actor_id'
_VERSION_NUMBER = '0.1'
_VERSIONS_PATH = f'/v2/actors/{_MOCKED_ACTOR_ID}/versions'
_VERSION_PATH = f'{_VERSIONS_PATH}/{_VERSION_NUMBER}'

_ACTOR_PATH = 'actors/my-actor'
_TARBALL_URL = 'https://example.com/monorepo.zip'

_VERSION_RESPONSE = {
    'data': {
        'versionNumber': _VERSION_NUMBER,
        'sourceType': 'TARBALL',
        'tarballUrl': _TARBALL_URL,
        'buildTag': 'latest',
        'envVars': [],
        'actorPath': _ACTOR_PATH,
    }
}


def capture(captured: list[Request]) -> Callable[[Request], Response]:
    def handler(request: Request) -> Response:
        captured.append(request)
        return Response(json.dumps(_VERSION_RESPONSE), status=200, mimetype='application/json')

    return handler


def request_body(request: Request) -> dict[str, Any]:
    return json.loads(request.get_data())


def test_create_sends_actor_path(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`create` sends `actor_path` as `actorPath` and reads it back from the response."""
    captured: list[Request] = []
    httpserver.expect_request(_VERSIONS_PATH, method='POST').respond_with_handler(capture(captured))

    versions_client = sync_client.actor(_MOCKED_ACTOR_ID).versions()
    version = versions_client.create(
        version_number=_VERSION_NUMBER,
        source_type='TARBALL',
        tarball_url=_TARBALL_URL,
        actor_path=_ACTOR_PATH,
    )

    assert len(captured) == 1
    assert request_body(captured[0]) == {
        'versionNumber': _VERSION_NUMBER,
        'sourceType': 'TARBALL',
        'tarballUrl': _TARBALL_URL,
        'actorPath': _ACTOR_PATH,
    }
    assert version.actor_path == _ACTOR_PATH


async def test_create_sends_actor_path_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    """Async `create` sends `actor_path` as `actorPath` and reads it back from the response."""
    captured: list[Request] = []
    httpserver.expect_request(_VERSIONS_PATH, method='POST').respond_with_handler(capture(captured))

    versions_client = async_client.actor(_MOCKED_ACTOR_ID).versions()
    version = await versions_client.create(
        version_number=_VERSION_NUMBER,
        source_type='TARBALL',
        tarball_url=_TARBALL_URL,
        actor_path=_ACTOR_PATH,
    )

    assert len(captured) == 1
    assert request_body(captured[0]) == {
        'versionNumber': _VERSION_NUMBER,
        'sourceType': 'TARBALL',
        'tarballUrl': _TARBALL_URL,
        'actorPath': _ACTOR_PATH,
    }
    assert version.actor_path == _ACTOR_PATH


def test_create_omits_actor_path_when_not_passed(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`create` leaves `actorPath` out of the request body when `actor_path` is not passed."""
    captured: list[Request] = []
    httpserver.expect_request(_VERSIONS_PATH, method='POST').respond_with_handler(capture(captured))

    versions_client = sync_client.actor(_MOCKED_ACTOR_ID).versions()
    versions_client.create(
        version_number=_VERSION_NUMBER,
        source_type='TARBALL',
        tarball_url=_TARBALL_URL,
    )

    assert len(captured) == 1
    assert 'actorPath' not in request_body(captured[0])


async def test_create_omits_actor_path_when_not_passed_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async `create` leaves `actorPath` out of the request body when `actor_path` is not passed."""
    captured: list[Request] = []
    httpserver.expect_request(_VERSIONS_PATH, method='POST').respond_with_handler(capture(captured))

    versions_client = async_client.actor(_MOCKED_ACTOR_ID).versions()
    await versions_client.create(
        version_number=_VERSION_NUMBER,
        source_type='TARBALL',
        tarball_url=_TARBALL_URL,
    )

    assert len(captured) == 1
    assert 'actorPath' not in request_body(captured[0])


def test_update_sends_actor_path(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`update` sends `actor_path` as `actorPath` and reads it back from the response."""
    captured: list[Request] = []
    httpserver.expect_request(_VERSION_PATH, method='PUT').respond_with_handler(capture(captured))

    version_client = sync_client.actor(_MOCKED_ACTOR_ID).version(_VERSION_NUMBER)
    version = version_client.update(
        tarball_url=_TARBALL_URL,
        actor_path=_ACTOR_PATH,
    )

    assert len(captured) == 1
    assert request_body(captured[0]) == {'tarballUrl': _TARBALL_URL, 'actorPath': _ACTOR_PATH}
    assert version.actor_path == _ACTOR_PATH


async def test_update_sends_actor_path_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    """Async `update` sends `actor_path` as `actorPath` and reads it back from the response."""
    captured: list[Request] = []
    httpserver.expect_request(_VERSION_PATH, method='PUT').respond_with_handler(capture(captured))

    version_client = async_client.actor(_MOCKED_ACTOR_ID).version(_VERSION_NUMBER)
    version = await version_client.update(
        tarball_url=_TARBALL_URL,
        actor_path=_ACTOR_PATH,
    )

    assert len(captured) == 1
    assert request_body(captured[0]) == {'tarballUrl': _TARBALL_URL, 'actorPath': _ACTOR_PATH}
    assert version.actor_path == _ACTOR_PATH


def test_update_omits_actor_path_when_not_passed(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`update` leaves `actorPath` out of the request body when `actor_path` is not passed."""
    captured: list[Request] = []
    httpserver.expect_request(_VERSION_PATH, method='PUT').respond_with_handler(capture(captured))

    version_client = sync_client.actor(_MOCKED_ACTOR_ID).version(_VERSION_NUMBER)
    version_client.update(tarball_url=_TARBALL_URL)

    assert len(captured) == 1
    assert request_body(captured[0]) == {'tarballUrl': _TARBALL_URL}


async def test_update_omits_actor_path_when_not_passed_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async `update` leaves `actorPath` out of the request body when `actor_path` is not passed."""
    captured: list[Request] = []
    httpserver.expect_request(_VERSION_PATH, method='PUT').respond_with_handler(capture(captured))

    version_client = async_client.actor(_MOCKED_ACTOR_ID).version(_VERSION_NUMBER)
    await version_client.update(tarball_url=_TARBALL_URL)

    assert len(captured) == 1
    assert request_body(captured[0]) == {'tarballUrl': _TARBALL_URL}

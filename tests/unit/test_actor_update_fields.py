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
_ACTOR_PATH = f'/v2/actors/{_MOCKED_ACTOR_ID}'
_ACTORS_PATH = '/v2/actors'

_ACTOR_RESPONSE = {
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
    }
}

_FIELDS: dict[str, Any] = {
    'actor_standby_disable_standby_fields_override': True,
    'actor_standby_should_pass_actor_input': False,
}

_EXPECTED_BODY = {
    'actorStandby': {'disableStandbyFieldsOverride': True, 'shouldPassActorInput': False},
}


def capture(captured: list[Request]) -> Callable[[Request], Response]:
    def handler(request: Request) -> Response:
        captured.append(request)
        return Response(json.dumps(_ACTOR_RESPONSE), status=200, mimetype='application/json')

    return handler


def body_subset(request: Request) -> dict[str, Any]:
    body = json.loads(request.get_data())
    return {key: body[key] for key in _EXPECTED_BODY}


def test_update_sends_standby_fields(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`update` nests the Standby flags into `actorStandby`."""
    captured: list[Request] = []
    httpserver.expect_request(_ACTOR_PATH, method='PUT').respond_with_handler(capture(captured))

    sync_client.actor(_MOCKED_ACTOR_ID).update(**_FIELDS)

    assert len(captured) == 1
    assert body_subset(captured[0]) == _EXPECTED_BODY


async def test_update_sends_standby_fields_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    """Async `update` nests the Standby flags into `actorStandby`."""
    captured: list[Request] = []
    httpserver.expect_request(_ACTOR_PATH, method='PUT').respond_with_handler(capture(captured))

    await async_client.actor(_MOCKED_ACTOR_ID).update(**_FIELDS)

    assert len(captured) == 1
    assert body_subset(captured[0]) == _EXPECTED_BODY


def test_create_sends_standby_fields(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`create` nests the Standby flags into `actorStandby`."""
    captured: list[Request] = []
    httpserver.expect_request(_ACTORS_PATH, method='POST').respond_with_handler(capture(captured))

    sync_client.actors().create(name='test-actor', **_FIELDS)

    assert len(captured) == 1
    assert body_subset(captured[0]) == _EXPECTED_BODY


async def test_create_sends_standby_fields_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    """Async `create` nests the Standby flags into `actorStandby`."""
    captured: list[Request] = []
    httpserver.expect_request(_ACTORS_PATH, method='POST').respond_with_handler(capture(captured))

    await async_client.actors().create(name='test-actor', **_FIELDS)

    assert len(captured) == 1
    assert body_subset(captured[0]) == _EXPECTED_BODY

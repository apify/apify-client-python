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
    'server_disable_fields_override': True,
    'server_should_pass_actor_input': False,
    'server_tenancy': 'SINGLE_TENANT',
}

_DEPRECATED_FIELDS: dict[str, Any] = {
    'actor_standby_disable_standby_fields_override': True,
    'actor_standby_should_pass_actor_input': False,
    'actor_standby_tenancy': 'SINGLE_TENANT',
}

_EXPECTED_BODY = {
    'actorStandby': {
        'disableStandbyFieldsOverride': True,
        'shouldPassActorInput': False,
        'tenancy': 'SINGLE_TENANT',
    },
}


def capture(captured: list[Request]) -> Callable[[Request], Response]:
    def handler(request: Request) -> Response:
        captured.append(request)
        return Response(json.dumps(_ACTOR_RESPONSE), status=200, mimetype='application/json')

    return handler


def body_subset(request: Request) -> dict[str, Any]:
    body = json.loads(request.get_data())
    return {key: body[key] for key in _EXPECTED_BODY}


def test_update_sends_server_fields(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`update` nests the `server_*` arguments into `actorStandby`."""
    captured: list[Request] = []
    httpserver.expect_request(_ACTOR_PATH, method='PUT').respond_with_handler(capture(captured))

    sync_client.actor(_MOCKED_ACTOR_ID).update(**_FIELDS)

    assert len(captured) == 1
    assert body_subset(captured[0]) == _EXPECTED_BODY


async def test_update_sends_server_fields_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    """Async `update` nests the `server_*` arguments into `actorStandby`."""
    captured: list[Request] = []
    httpserver.expect_request(_ACTOR_PATH, method='PUT').respond_with_handler(capture(captured))

    await async_client.actor(_MOCKED_ACTOR_ID).update(**_FIELDS)

    assert len(captured) == 1
    assert body_subset(captured[0]) == _EXPECTED_BODY


def test_create_sends_server_fields(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`create` nests the `server_*` arguments into `actorStandby`."""
    captured: list[Request] = []
    httpserver.expect_request(_ACTORS_PATH, method='POST').respond_with_handler(capture(captured))

    sync_client.actors().create(name='test-actor', **_FIELDS)

    assert len(captured) == 1
    assert body_subset(captured[0]) == _EXPECTED_BODY


async def test_create_sends_server_fields_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    """Async `create` nests the `server_*` arguments into `actorStandby`."""
    captured: list[Request] = []
    httpserver.expect_request(_ACTORS_PATH, method='POST').respond_with_handler(capture(captured))

    await async_client.actors().create(name='test-actor', **_FIELDS)

    assert len(captured) == 1
    assert body_subset(captured[0]) == _EXPECTED_BODY


def test_update_deprecated_standby_args_are_aliases(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """The deprecated `actor_standby_*` arguments of `update` warn at the caller and are sent as `server_*`."""
    captured: list[Request] = []
    httpserver.expect_request(_ACTOR_PATH, method='PUT').respond_with_handler(capture(captured))

    with pytest.warns(DeprecationWarning, match='argument is deprecated') as record:
        sync_client.actor(_MOCKED_ACTOR_ID).update(**_DEPRECATED_FIELDS)

    assert [warning.filename for warning in record] == [__file__, __file__, __file__]
    assert len(captured) == 1
    assert body_subset(captured[0]) == _EXPECTED_BODY


async def test_update_deprecated_standby_args_are_aliases_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """The deprecated `actor_standby_*` arguments of async `update` warn at the caller and are sent as `server_*`."""
    captured: list[Request] = []
    httpserver.expect_request(_ACTOR_PATH, method='PUT').respond_with_handler(capture(captured))

    with pytest.warns(DeprecationWarning, match='argument is deprecated') as record:
        await async_client.actor(_MOCKED_ACTOR_ID).update(**_DEPRECATED_FIELDS)

    assert [warning.filename for warning in record] == [__file__, __file__, __file__]
    assert len(captured) == 1
    assert body_subset(captured[0]) == _EXPECTED_BODY


def test_create_deprecated_standby_args_are_aliases(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """The deprecated `actor_standby_*` arguments of `create` warn at the caller and are sent as `server_*`."""
    captured: list[Request] = []
    httpserver.expect_request(_ACTORS_PATH, method='POST').respond_with_handler(capture(captured))

    with pytest.warns(DeprecationWarning, match='argument is deprecated') as record:
        sync_client.actors().create(name='test-actor', **_DEPRECATED_FIELDS)

    assert [warning.filename for warning in record] == [__file__, __file__, __file__]
    assert len(captured) == 1
    assert body_subset(captured[0]) == _EXPECTED_BODY


async def test_create_deprecated_standby_args_are_aliases_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """The deprecated `actor_standby_*` arguments of async `create` warn at the caller and are sent as `server_*`."""
    captured: list[Request] = []
    httpserver.expect_request(_ACTORS_PATH, method='POST').respond_with_handler(capture(captured))

    with pytest.warns(DeprecationWarning, match='argument is deprecated') as record:
        await async_client.actors().create(name='test-actor', **_DEPRECATED_FIELDS)

    assert [warning.filename for warning in record] == [__file__, __file__, __file__]
    assert len(captured) == 1
    assert body_subset(captured[0]) == _EXPECTED_BODY


def test_update_rejects_server_arg_and_its_deprecated_alias(sync_client: ApifyClient) -> None:
    """Passing both a `server_*` argument and its deprecated `actor_standby_*` alias raises a `ValueError`."""
    with (
        pytest.warns(DeprecationWarning, match='`actor_standby_build` argument is deprecated'),
        pytest.raises(ValueError, match='only one of `server_build` and `actor_standby_build`'),
    ):
        sync_client.actor(_MOCKED_ACTOR_ID).update(server_build='latest', actor_standby_build='beta')


def test_create_sends_actor_permission_level(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`create` sends `actor_permission_level` as `actorPermissionLevel`."""
    captured: list[Request] = []
    httpserver.expect_request(_ACTORS_PATH, method='POST').respond_with_handler(capture(captured))

    sync_client.actors().create(name='test-actor', actor_permission_level='LIMITED_PERMISSIONS')

    assert len(captured) == 1
    assert json.loads(captured[0].get_data()) == {'name': 'test-actor', 'actorPermissionLevel': 'LIMITED_PERMISSIONS'}


async def test_create_sends_actor_permission_level_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async `create` sends `actor_permission_level` as `actorPermissionLevel`."""
    captured: list[Request] = []
    httpserver.expect_request(_ACTORS_PATH, method='POST').respond_with_handler(capture(captured))

    await async_client.actors().create(name='test-actor', actor_permission_level='LIMITED_PERMISSIONS')

    assert len(captured) == 1
    assert json.loads(captured[0].get_data()) == {'name': 'test-actor', 'actorPermissionLevel': 'LIMITED_PERMISSIONS'}

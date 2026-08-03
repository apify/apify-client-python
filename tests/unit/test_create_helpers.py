"""Tests for the conflict-recovering create helpers in `tests/_utils.py`.

The recovery branches only run when a retried create request already committed server-side, which never happens in
a normal integration-test run. These tests drive them against a mocked API so a wrong error type or lookup route is
caught here instead of resurfacing as the flake the helpers exist to prevent.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

from .._utils import create_actor, create_actor_version, create_env_var, create_schedule, create_task
from apify_client import ApifyClient, ApifyClientAsync
from apify_client._models import Actor, EnvVar, Schedule, Task, Version
from apify_client.errors import ConflictError, ForbiddenError

if TYPE_CHECKING:
    from pytest_httpserver import HTTPServer

ACTOR_NAME = 'python-client-test-actor-AbCdEfGh'
TASK_NAME = 'python-client-test-task-AbCdEfGh'
SCHEDULE_NAME = 'python-client-test-schedule-AbCdEfGh'
USERNAME = 'test-user'

USER = {'username': USERNAME}

ACTOR = {
    'id': 'zdc3Pyhyz3m8vjDeM',
    'userId': 'wRsJZtadYvn4mBZmm',
    'name': ACTOR_NAME,
    'username': USERNAME,
    'isPublic': False,
    'createdAt': '2026-01-01T00:00:00.000Z',
    'modifiedAt': '2026-01-01T00:00:00.000Z',
    'stats': {},
    'versions': [],
    'defaultRunOptions': {},
}

TASK = {
    'id': 'asADASadYvn4mBZmm',
    'userId': 'wRsJZtadYvn4mBZmm',
    'actId': 'zdc3Pyhyz3m8vjDeM',
    'name': TASK_NAME,
    'createdAt': '2026-01-01T00:00:00.000Z',
    'modifiedAt': '2026-01-01T00:00:00.000Z',
}

SCHEDULE = {
    'id': 'asdLZtadYvn4mBZmm',
    'userId': 'wRsJZtadYvn4mBZmm',
    'name': SCHEDULE_NAME,
    'cronExpression': '0 0 * * *',
    'timezone': 'UTC',
    'isEnabled': False,
    'isExclusive': False,
    'createdAt': '2026-01-01T00:00:00.000Z',
    'modifiedAt': '2026-01-01T00:00:00.000Z',
    'actions': [],
}

VERSION = {'versionNumber': '1.0', 'sourceType': 'SOURCE_FILES'}

ENV_VAR = {'name': 'MY_VAR', 'value': 'my_value'}


def api_error(error_type: str) -> dict[str, Any]:
    """Build an API error response body carrying the given error type."""
    return {'error': {'type': error_type, 'message': f'Some other resource already has this name ({error_type}).'}}


def make_client(httpserver: HTTPServer, *, is_async: bool) -> ApifyClient | ApifyClientAsync:
    """Build a client pointed at the mock server."""
    api_url = httpserver.url_for('/').removesuffix('/')
    client_class = ApifyClientAsync if is_async else ApifyClient
    return client_class(token='placeholder_token', api_url=api_url, api_public_url=api_url)


@pytest.mark.parametrize('is_async', [pytest.param(False, id='sync'), pytest.param(True, id='async')])
async def test_create_actor_recovers_committed_actor(httpserver: HTTPServer, *, is_async: bool) -> None:
    """A create rejected as a name conflict is recovered through the owner-scoped Actor lookup."""
    httpserver.expect_oneshot_request('/v2/actors', method='POST').respond_with_json(
        api_error('actor-name-not-unique'), status=409
    )
    httpserver.expect_oneshot_request('/v2/users/me', method='GET').respond_with_json({'data': USER})
    httpserver.expect_oneshot_request(f'/v2/actors/{USERNAME}~{ACTOR_NAME}', method='GET').respond_with_json(
        {'data': ACTOR}
    )

    actor = await create_actor(make_client(httpserver, is_async=is_async), name=ACTOR_NAME, title='Test Actor')

    assert isinstance(actor, Actor)
    assert actor.name == ACTOR_NAME
    httpserver.check_assertions()


async def test_create_actor_propagates_unrelated_conflict(httpserver: HTTPServer) -> None:
    """A 409 that is not a name conflict is left alone - no recovery is attempted."""
    httpserver.expect_oneshot_request('/v2/actors', method='POST').respond_with_json(
        api_error('actor-monetization-not-enabled'), status=409
    )

    with pytest.raises(ConflictError):
        await create_actor(make_client(httpserver, is_async=True), name=ACTOR_NAME)

    httpserver.check_assertions()


async def test_create_actor_reraises_when_recovery_finds_nothing(httpserver: HTTPServer) -> None:
    """A name conflict whose Actor cannot be found afterwards fails with the original API error."""
    httpserver.expect_oneshot_request('/v2/actors', method='POST').respond_with_json(
        api_error('actor-name-not-unique'), status=409
    )
    httpserver.expect_oneshot_request('/v2/users/me', method='GET').respond_with_json({'data': USER})
    httpserver.expect_oneshot_request(f'/v2/actors/{USERNAME}~{ACTOR_NAME}', method='GET').respond_with_json(
        api_error('record-not-found'), status=404
    )

    with pytest.raises(ConflictError) as exc_info:
        await create_actor(make_client(httpserver, is_async=True), name=ACTOR_NAME)

    assert any('could not be retrieved' in note for note in exc_info.value.__notes__)
    httpserver.check_assertions()


async def test_create_task_recovers_committed_task(httpserver: HTTPServer) -> None:
    """A create rejected as a name conflict is recovered through the owner-scoped task lookup."""
    httpserver.expect_oneshot_request('/v2/actor-tasks', method='POST').respond_with_json(
        api_error('actor-task-name-not-unique'), status=409
    )
    httpserver.expect_oneshot_request('/v2/users/me', method='GET').respond_with_json({'data': USER})
    httpserver.expect_oneshot_request(f'/v2/actor-tasks/{USERNAME}~{TASK_NAME}', method='GET').respond_with_json(
        {'data': TASK}
    )

    task = await create_task(make_client(httpserver, is_async=True), actor_id=str(ACTOR['id']), name=TASK_NAME)

    assert isinstance(task, Task)
    assert task.name == TASK_NAME
    httpserver.check_assertions()


async def test_create_schedule_recovers_committed_schedule(httpserver: HTTPServer) -> None:
    """Schedules cannot be addressed by name, so recovery locates the committed one in the listing."""
    httpserver.expect_oneshot_request('/v2/schedules', method='POST').respond_with_json(
        api_error('schedule-name-not-unique'), status=409
    )
    listing = {'total': 1, 'offset': 0, 'limit': 1000, 'desc': True, 'count': 1, 'items': [SCHEDULE]}
    httpserver.expect_oneshot_request('/v2/schedules', method='GET').respond_with_json({'data': listing})
    httpserver.expect_oneshot_request(f'/v2/schedules/{SCHEDULE["id"]}', method='GET').respond_with_json(
        {'data': SCHEDULE}
    )

    schedule = await create_schedule(
        make_client(httpserver, is_async=True),
        cron_expression='0 0 * * *',
        is_enabled=False,
        is_exclusive=False,
        name=SCHEDULE_NAME,
    )

    assert isinstance(schedule, Schedule)
    assert schedule.name == SCHEDULE_NAME
    httpserver.check_assertions()


async def test_create_actor_version_recovers_committed_version(httpserver: HTTPServer) -> None:
    """A version conflict is reported as 403 rather than 409, and is recovered by version number."""
    versions_path = f'/v2/actors/{ACTOR["id"]}/versions'
    httpserver.expect_oneshot_request(versions_path, method='POST').respond_with_json(
        api_error('version-already-exists'), status=403
    )
    httpserver.expect_oneshot_request(f'{versions_path}/1.0', method='GET').respond_with_json({'data': VERSION})

    client = make_client(httpserver, is_async=True)
    version = await create_actor_version(
        client.actor(str(ACTOR['id'])),
        version_number='1.0',
        source_type='SOURCE_FILES',
    )

    assert isinstance(version, Version)
    assert version.version_number == '1.0'
    httpserver.check_assertions()


async def test_create_env_var_recovers_committed_env_var(httpserver: HTTPServer) -> None:
    """An env var conflict is reported as 403 rather than 409, and is recovered by name."""
    env_vars_path = f'/v2/actors/{ACTOR["id"]}/versions/1.0/env-vars'
    httpserver.expect_oneshot_request(env_vars_path, method='POST').respond_with_json(
        api_error('env-var-already-exists'), status=403
    )
    httpserver.expect_oneshot_request(f'{env_vars_path}/MY_VAR', method='GET').respond_with_json({'data': ENV_VAR})

    client = make_client(httpserver, is_async=True)
    env_var = await create_env_var(client.actor(str(ACTOR['id'])).version('1.0'), name='MY_VAR', value='my_value')

    assert isinstance(env_var, EnvVar)
    assert env_var.name == 'MY_VAR'
    httpserver.check_assertions()


async def test_create_env_var_propagates_unrelated_forbidden(httpserver: HTTPServer) -> None:
    """A 403 that is not an env var conflict is left alone - no recovery is attempted."""
    env_vars_path = f'/v2/actors/{ACTOR["id"]}/versions/1.0/env-vars'
    httpserver.expect_oneshot_request(env_vars_path, method='POST').respond_with_json(
        api_error('insufficient-permissions'), status=403
    )

    client = make_client(httpserver, is_async=True)
    with pytest.raises(ForbiddenError):
        await create_env_var(client.actor(str(ACTOR['id'])).version('1.0'), name='MY_VAR', value='my_value')

    httpserver.check_assertions()

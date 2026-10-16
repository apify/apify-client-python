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

_MOCKED_SCHEDULE_ID = 'test_schedule_id'
_SCHEDULE_PATH = f'/v2/schedules/{_MOCKED_SCHEDULE_ID}'
_SCHEDULES_PATH = '/v2/schedules'

_SCHEDULE_RESPONSE = {
    'data': {
        'id': _MOCKED_SCHEDULE_ID,
        'userId': 'test_user_id',
        'name': 'test-schedule',
        'cronExpression': '@daily',
        'timezone': 'UTC',
        'isEnabled': True,
        'isExclusive': False,
        'createdAt': '2026-08-01T10:00:00.000Z',
        'modifiedAt': '2026-08-01T10:00:00.000Z',
        'actions': [],
        'notifications': {'email': False},
    }
}


def capture(captured: list[Request]) -> Callable[[Request], Response]:
    def handler(request: Request) -> Response:
        captured.append(request)
        return Response(json.dumps(_SCHEDULE_RESPONSE), status=200, mimetype='application/json')

    return handler


def body_of(request: Request) -> dict[str, Any]:
    return json.loads(request.get_data())


@pytest.mark.parametrize(
    'notifications_email',
    [
        pytest.param(True, id='enabled'),
        pytest.param(False, id='disabled'),
    ],
)
def test_update_sends_notifications(
    httpserver: HTTPServer, sync_client: ApifyClient, *, notifications_email: bool
) -> None:
    """`update` sends `notifications_email` as `notifications.email`."""
    captured: list[Request] = []
    httpserver.expect_request(_SCHEDULE_PATH, method='PUT').respond_with_handler(capture(captured))

    sync_client.schedule(_MOCKED_SCHEDULE_ID).update(notifications_email=notifications_email)

    assert len(captured) == 1
    assert body_of(captured[0]) == {'notifications': {'email': notifications_email}}


@pytest.mark.parametrize(
    'notifications_email',
    [
        pytest.param(True, id='enabled'),
        pytest.param(False, id='disabled'),
    ],
)
async def test_update_sends_notifications_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync, *, notifications_email: bool
) -> None:
    """Async `update` sends `notifications_email` as `notifications.email`."""
    captured: list[Request] = []
    httpserver.expect_request(_SCHEDULE_PATH, method='PUT').respond_with_handler(capture(captured))

    await async_client.schedule(_MOCKED_SCHEDULE_ID).update(notifications_email=notifications_email)

    assert len(captured) == 1
    assert body_of(captured[0]) == {'notifications': {'email': notifications_email}}


def test_update_omits_notifications_by_default(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`update` sends no `notifications` key unless `notifications_email` is passed."""
    captured: list[Request] = []
    httpserver.expect_request(_SCHEDULE_PATH, method='PUT').respond_with_handler(capture(captured))

    sync_client.schedule(_MOCKED_SCHEDULE_ID).update(name='renamed')

    assert len(captured) == 1
    assert body_of(captured[0]) == {'name': 'renamed'}


def test_create_sends_notifications(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`create` sends `notifications_email` as `notifications.email`."""
    captured: list[Request] = []
    httpserver.expect_request(_SCHEDULES_PATH, method='POST').respond_with_handler(capture(captured))

    sync_client.schedules().create(
        cron_expression='@daily',
        is_enabled=True,
        is_exclusive=False,
        notifications_email=True,
    )

    assert len(captured) == 1
    assert body_of(captured[0])['notifications'] == {'email': True}


async def test_create_sends_notifications_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    """Async `create` sends `notifications_email` as `notifications.email`."""
    captured: list[Request] = []
    httpserver.expect_request(_SCHEDULES_PATH, method='POST').respond_with_handler(capture(captured))

    await async_client.schedules().create(
        cron_expression='@daily',
        is_enabled=True,
        is_exclusive=False,
        notifications_email=True,
    )

    assert len(captured) == 1
    assert body_of(captured[0])['notifications'] == {'email': True}

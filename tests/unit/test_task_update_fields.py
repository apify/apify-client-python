from __future__ import annotations

import json
from decimal import Decimal
from typing import TYPE_CHECKING, Any

import pytest
from werkzeug import Request, Response

if TYPE_CHECKING:
    from collections.abc import Callable

    from pytest_httpserver import HTTPServer

    from apify_client import ApifyClient, ApifyClientAsync

pytestmark = pytest.mark.usefixtures('http_client_classes')

_MOCKED_TASK_ID = 'test_task_id'
_TASK_PATH = f'/v2/actor-tasks/{_MOCKED_TASK_ID}'
_TASKS_PATH = '/v2/actor-tasks'

_TASK_RESPONSE = {
    'data': {
        'id': _MOCKED_TASK_ID,
        'userId': 'test_user_id',
        'actId': 'test_actor_id',
        'name': 'test-task',
        'createdAt': '2026-08-01T10:00:00.000Z',
        'modifiedAt': '2026-08-01T10:00:00.000Z',
    }
}

_FIELDS: dict[str, Any] = {
    'description': 'Scrapes the front page.',
    'max_total_charge_usd': Decimal('2.5'),
}

_EXPECTED_BODY = {
    'description': 'Scrapes the front page.',
    'options': {'maxTotalChargeUsd': 2.5},
}


def capture(captured: list[Request]) -> Callable[[Request], Response]:
    def handler(request: Request) -> Response:
        captured.append(request)
        return Response(json.dumps(_TASK_RESPONSE), status=200, mimetype='application/json')

    return handler


def body_subset(request: Request) -> dict[str, Any]:
    body = json.loads(request.get_data())
    return {key: body[key] for key in _EXPECTED_BODY}


def test_update_sends_description_and_max_total_charge(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`update` sends `description` and nests `max_total_charge_usd` into `options`."""
    captured: list[Request] = []
    httpserver.expect_request(_TASK_PATH, method='PUT').respond_with_handler(capture(captured))

    sync_client.task(_MOCKED_TASK_ID).update(**_FIELDS)

    assert len(captured) == 1
    assert body_subset(captured[0]) == _EXPECTED_BODY


async def test_update_sends_description_and_max_total_charge_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async `update` sends `description` and nests `max_total_charge_usd` into `options`."""
    captured: list[Request] = []
    httpserver.expect_request(_TASK_PATH, method='PUT').respond_with_handler(capture(captured))

    await async_client.task(_MOCKED_TASK_ID).update(**_FIELDS)

    assert len(captured) == 1
    assert body_subset(captured[0]) == _EXPECTED_BODY


def test_create_sends_description_and_max_total_charge(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`create` sends `description` and nests `max_total_charge_usd` into `options`."""
    captured: list[Request] = []
    httpserver.expect_request(_TASKS_PATH, method='POST').respond_with_handler(capture(captured))

    sync_client.tasks().create(actor_id='test_actor_id', name='test-task', **_FIELDS)

    assert len(captured) == 1
    assert body_subset(captured[0]) == _EXPECTED_BODY


async def test_create_sends_description_and_max_total_charge_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async `create` sends `description` and nests `max_total_charge_usd` into `options`."""
    captured: list[Request] = []
    httpserver.expect_request(_TASKS_PATH, method='POST').respond_with_handler(capture(captured))

    await async_client.tasks().create(actor_id='test_actor_id', name='test-task', **_FIELDS)

    assert len(captured) == 1
    assert body_subset(captured[0]) == _EXPECTED_BODY

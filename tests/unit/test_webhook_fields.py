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

_MOCKED_WEBHOOK_ID = 'test_webhook_id'
_WEBHOOK_PATH = f'/v2/webhooks/{_MOCKED_WEBHOOK_ID}'
_WEBHOOKS_PATH = '/v2/webhooks'

_WEBHOOK_RESPONSE = {
    'data': {
        'id': _MOCKED_WEBHOOK_ID,
        'userId': 'test_user_id',
        'createdAt': '2026-08-01T10:00:00.000Z',
        'modifiedAt': '2026-08-01T10:00:00.000Z',
        'eventTypes': ['ACTOR.RUN.SUCCEEDED'],
        'condition': {'actorId': 'test_actor_id'},
        'ignoreSslErrors': False,
    }
}

_FIELDS: dict[str, Any] = {
    'description': 'Notifies the CRM.',
    'should_interpolate_strings': True,
}

_EXPECTED_BODY = {
    'description': 'Notifies the CRM.',
    'shouldInterpolateStrings': True,
}


def capture(captured: list[Request]) -> Callable[[Request], Response]:
    def handler(request: Request) -> Response:
        captured.append(request)
        return Response(json.dumps(_WEBHOOK_RESPONSE), status=200, mimetype='application/json')

    return handler


def body_subset(request: Request) -> dict[str, Any]:
    body = json.loads(request.get_data())
    return {key: body[key] for key in _EXPECTED_BODY}


def test_update_sends_description_and_interpolation_flag(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`update` sends `description` and `shouldInterpolateStrings`."""
    captured: list[Request] = []
    httpserver.expect_request(_WEBHOOK_PATH, method='PUT').respond_with_handler(capture(captured))

    sync_client.webhook(_MOCKED_WEBHOOK_ID).update(**_FIELDS)

    assert len(captured) == 1
    assert body_subset(captured[0]) == _EXPECTED_BODY


async def test_update_sends_description_and_interpolation_flag_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async `update` sends `description` and `shouldInterpolateStrings`."""
    captured: list[Request] = []
    httpserver.expect_request(_WEBHOOK_PATH, method='PUT').respond_with_handler(capture(captured))

    await async_client.webhook(_MOCKED_WEBHOOK_ID).update(**_FIELDS)

    assert len(captured) == 1
    assert body_subset(captured[0]) == _EXPECTED_BODY


def test_create_sends_description_and_interpolation_flag(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`create` sends `description` and `shouldInterpolateStrings`."""
    captured: list[Request] = []
    httpserver.expect_request(_WEBHOOKS_PATH, method='POST').respond_with_handler(capture(captured))

    sync_client.webhooks().create(
        event_types=['ACTOR.RUN.SUCCEEDED'],
        request_url='https://example.com/hook',
        actor_id='test_actor_id',
        **_FIELDS,
    )

    assert len(captured) == 1
    assert body_subset(captured[0]) == _EXPECTED_BODY


async def test_create_sends_description_and_interpolation_flag_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async `create` sends `description` and `shouldInterpolateStrings`."""
    captured: list[Request] = []
    httpserver.expect_request(_WEBHOOKS_PATH, method='POST').respond_with_handler(capture(captured))

    await async_client.webhooks().create(
        event_types=['ACTOR.RUN.SUCCEEDED'],
        request_url='https://example.com/hook',
        actor_id='test_actor_id',
        **_FIELDS,
    )

    assert len(captured) == 1
    assert body_subset(captured[0]) == _EXPECTED_BODY

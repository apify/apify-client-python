from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from werkzeug import Request, Response

from apify_client import ApifyClient, ApifyClientAsync

if TYPE_CHECKING:
    from collections.abc import Callable

    from pytest_httpserver import HTTPServer

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


def _capture(captured: list[Request]) -> Callable[[Request], Response]:
    def handler(request: Request) -> Response:
        captured.append(request)
        return Response(json.dumps(_TASK_RESPONSE), status=200, mimetype='application/json')

    return handler


def _body_of(request: Request) -> dict[str, Any]:
    return json.loads(request.get_data())


def _client(httpserver: HTTPServer) -> ApifyClient:
    return ApifyClient(token='test_token', api_url=httpserver.url_for('/').removesuffix('/'))


def _async_client(httpserver: HTTPServer) -> ApifyClientAsync:
    return ApifyClientAsync(token='test_token', api_url=httpserver.url_for('/').removesuffix('/'))


def test_publish_sets_is_public_true(httpserver: HTTPServer) -> None:
    captured: list[Request] = []
    httpserver.expect_request(_TASK_PATH, method='PUT').respond_with_handler(_capture(captured))

    _client(httpserver).task(_MOCKED_TASK_ID).publish()

    assert len(captured) == 1
    assert _body_of(captured[0]) == {'isPublic': True}


def test_unpublish_sets_is_public_false(httpserver: HTTPServer) -> None:
    captured: list[Request] = []
    httpserver.expect_request(_TASK_PATH, method='PUT').respond_with_handler(_capture(captured))

    _client(httpserver).task(_MOCKED_TASK_ID).unpublish()

    assert len(captured) == 1
    # `False` must survive rather than being dropped as falsy - it is what unpublishes the task.
    assert _body_of(captured[0]) == {'isPublic': False}


def test_update_sends_only_the_requested_fields(httpserver: HTTPServer) -> None:
    """A plain update must send nothing but the field it was asked to change.

    Asserted as an exact body rather than as absences, because both extra keys would be damaging: a present
    `publicConfig` - even an empty object - is treated by the API as an edit of the public landing page and
    requires write access to the task's Actor, and a stray `isPublic: false` would silently unpublish the task.
    """
    captured: list[Request] = []
    httpserver.expect_request(_TASK_PATH, method='PUT').respond_with_handler(_capture(captured))

    _client(httpserver).task(_MOCKED_TASK_ID).update(name='renamed')

    assert len(captured) == 1
    assert _body_of(captured[0]) == {'name': 'renamed'}


def test_update_sends_public_config_fields(httpserver: HTTPServer) -> None:
    captured: list[Request] = []
    httpserver.expect_request(_TASK_PATH, method='PUT').respond_with_handler(_capture(captured))

    _client(httpserver).task(_MOCKED_TASK_ID).update(
        public_config_seo_title='Scrape a website',
        public_config_input_schema_fields=['query'],
        public_config_dataset_view='overview',
    )

    assert len(captured) == 1
    assert _body_of(captured[0])['publicConfig'] == {
        'seoTitle': 'Scrape a website',
        'inputSchemaFields': ['query'],
        'datasetView': 'overview',
    }


def test_update_can_configure_and_publish_at_once(httpserver: HTTPServer) -> None:
    captured: list[Request] = []
    httpserver.expect_request(_TASK_PATH, method='PUT').respond_with_handler(_capture(captured))

    _client(httpserver).task(_MOCKED_TASK_ID).update(
        is_public=True,
        public_config_dataset_view='overview',
    )

    assert len(captured) == 1
    body = _body_of(captured[0])
    assert body['isPublic'] is True
    assert body['publicConfig'] == {'datasetView': 'overview'}


def test_create_sends_public_config_without_publishing(httpserver: HTTPServer) -> None:
    captured: list[Request] = []
    httpserver.expect_request(_TASKS_PATH, method='POST').respond_with_handler(_capture(captured))

    _client(httpserver).tasks().create(
        actor_id='test_actor_id',
        name='test-task',
        public_config_seo_title='Scrape a website',
    )

    assert len(captured) == 1
    body = _body_of(captured[0])
    assert body['publicConfig'] == {'seoTitle': 'Scrape a website'}
    # Publication is never part of a create - it only happens through the update.
    assert 'isPublic' not in body


def test_create_sends_only_the_requested_fields(httpserver: HTTPServer) -> None:
    captured: list[Request] = []
    httpserver.expect_request(_TASKS_PATH, method='POST').respond_with_handler(_capture(captured))

    _client(httpserver).tasks().create(actor_id='test_actor_id', name='test-task')

    assert len(captured) == 1
    assert _body_of(captured[0]) == {'actId': 'test_actor_id', 'name': 'test-task'}


async def test_publish_sets_is_public_true_async(httpserver: HTTPServer) -> None:
    captured: list[Request] = []
    httpserver.expect_request(_TASK_PATH, method='PUT').respond_with_handler(_capture(captured))

    await _async_client(httpserver).task(_MOCKED_TASK_ID).publish()

    assert len(captured) == 1
    assert _body_of(captured[0]) == {'isPublic': True}


async def test_unpublish_sets_is_public_false_async(httpserver: HTTPServer) -> None:
    captured: list[Request] = []
    httpserver.expect_request(_TASK_PATH, method='PUT').respond_with_handler(_capture(captured))

    await _async_client(httpserver).task(_MOCKED_TASK_ID).unpublish()

    assert len(captured) == 1
    assert _body_of(captured[0]) == {'isPublic': False}


async def test_update_sends_only_the_requested_fields_async(httpserver: HTTPServer) -> None:
    captured: list[Request] = []
    httpserver.expect_request(_TASK_PATH, method='PUT').respond_with_handler(_capture(captured))

    await _async_client(httpserver).task(_MOCKED_TASK_ID).update(name='renamed')

    assert len(captured) == 1
    assert _body_of(captured[0]) == {'name': 'renamed'}


async def test_update_sends_public_config_fields_async(httpserver: HTTPServer) -> None:
    captured: list[Request] = []
    httpserver.expect_request(_TASK_PATH, method='PUT').respond_with_handler(_capture(captured))

    await (
        _async_client(httpserver)
        .task(_MOCKED_TASK_ID)
        .update(
            public_config_seo_title='Scrape a website',
            public_config_input_schema_fields=['query'],
            public_config_dataset_view='overview',
        )
    )

    assert len(captured) == 1
    assert _body_of(captured[0])['publicConfig'] == {
        'seoTitle': 'Scrape a website',
        'inputSchemaFields': ['query'],
        'datasetView': 'overview',
    }


async def test_create_sends_public_config_without_publishing_async(httpserver: HTTPServer) -> None:
    captured: list[Request] = []
    httpserver.expect_request(_TASKS_PATH, method='POST').respond_with_handler(_capture(captured))

    await (
        _async_client(httpserver)
        .tasks()
        .create(
            actor_id='test_actor_id',
            name='test-task',
            public_config_seo_title='Scrape a website',
        )
    )

    assert len(captured) == 1
    body = _body_of(captured[0])
    assert body['publicConfig'] == {'seoTitle': 'Scrape a website'}
    assert 'isPublic' not in body

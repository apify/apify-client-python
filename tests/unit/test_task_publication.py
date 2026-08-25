from __future__ import annotations

import json
from datetime import UTC, datetime
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

_PUBLISHED_AT = '2026-08-01T10:00:00.000Z'

_TASK_RESPONSE = {
    'data': {
        'id': _MOCKED_TASK_ID,
        'userId': 'test_user_id',
        'actId': 'test_actor_id',
        'name': 'test-task',
        'createdAt': '2026-08-01T10:00:00.000Z',
        'modifiedAt': '2026-08-01T10:00:00.000Z',
        # Publication state as the API returns it, so the deserialization half is exercised too.
        'isPublic': True,
        'publicConfig': {
            'publishedAt': _PUBLISHED_AT,
            'seoTitle': 'Scrape a website',
            'inputSchemaFields': ['query'],
            'datasetName': 'default',
            'datasetView': 'overview',
        },
    }
}


def _capture(captured: list[Request]) -> Callable[[Request], Response]:
    def handler(request: Request) -> Response:
        captured.append(request)
        return Response(json.dumps(_TASK_RESPONSE), status=200, mimetype='application/json')

    return handler


def _body_of(request: Request) -> dict[str, Any]:
    return json.loads(request.get_data())


def test_publish_sets_is_public_true(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`publish` sends `isPublic: true` and nothing else."""
    captured: list[Request] = []
    httpserver.expect_request(_TASK_PATH, method='PUT').respond_with_handler(_capture(captured))

    sync_client.task(_MOCKED_TASK_ID).publish()

    assert len(captured) == 1
    assert _body_of(captured[0]) == {'isPublic': True}


def test_publish_returns_the_published_task(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`publish` returns the parsed task, including its publication state and display configuration."""
    httpserver.expect_request(_TASK_PATH, method='PUT').respond_with_json(_TASK_RESPONSE)

    task = sync_client.task(_MOCKED_TASK_ID).publish()

    assert task.is_public is True
    assert task.public_config is not None
    assert task.public_config.published_at == datetime(2026, 8, 1, 10, 0, tzinfo=UTC)
    assert task.public_config.seo_title == 'Scrape a website'
    assert task.public_config.input_schema_fields == ['query']
    assert task.public_config.dataset_view == 'overview'


def test_unpublish_sets_is_public_false(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`unpublish` sends `isPublic: false` rather than omitting the field."""
    captured: list[Request] = []
    httpserver.expect_request(_TASK_PATH, method='PUT').respond_with_handler(_capture(captured))

    sync_client.task(_MOCKED_TASK_ID).unpublish()

    assert len(captured) == 1
    # `False` must survive `exclude_none` - it is what unpublishes the task.
    assert _body_of(captured[0]) == {'isPublic': False}


def test_update_sends_only_the_requested_fields(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """A plain update must send nothing but the field it was asked to change.

    Asserted as an exact body rather than as absences, because both extra keys would be damaging: a present
    `publicConfig` - even an empty object - is treated by the API as an edit of the public landing page and
    requires write access to the task's Actor, and a stray `isPublic: false` would silently unpublish the task.
    """
    captured: list[Request] = []
    httpserver.expect_request(_TASK_PATH, method='PUT').respond_with_handler(_capture(captured))

    sync_client.task(_MOCKED_TASK_ID).update(name='renamed')

    assert len(captured) == 1
    assert _body_of(captured[0]) == {'name': 'renamed'}


def test_update_sends_public_config_fields(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """The `public_config_*` arguments are nested under `publicConfig` with their API names."""
    captured: list[Request] = []
    httpserver.expect_request(_TASK_PATH, method='PUT').respond_with_handler(_capture(captured))

    sync_client.task(_MOCKED_TASK_ID).update(
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


def test_update_can_configure_and_publish_at_once(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """A single update can both fill in the display configuration and publish the task."""
    captured: list[Request] = []
    httpserver.expect_request(_TASK_PATH, method='PUT').respond_with_handler(_capture(captured))

    sync_client.task(_MOCKED_TASK_ID).update(is_public=True, public_config_dataset_view='overview')

    assert len(captured) == 1
    body = _body_of(captured[0])
    assert body['isPublic'] is True
    assert body['publicConfig'] == {'datasetView': 'overview'}


def test_create_sends_public_config_without_publishing(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """Create accepts the display configuration but never publishes the task."""
    captured: list[Request] = []
    httpserver.expect_request(_TASKS_PATH, method='POST').respond_with_handler(_capture(captured))

    sync_client.tasks().create(
        actor_id='test_actor_id',
        name='test-task',
        public_config_seo_title='Scrape a website',
    )

    assert len(captured) == 1
    body = _body_of(captured[0])
    assert body['publicConfig'] == {'seoTitle': 'Scrape a website'}
    assert 'isPublic' not in body


def test_create_sends_only_the_requested_fields(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """A plain create must not send an empty `publicConfig`, which would demand Actor write access."""
    captured: list[Request] = []
    httpserver.expect_request(_TASKS_PATH, method='POST').respond_with_handler(_capture(captured))

    sync_client.tasks().create(actor_id='test_actor_id', name='test-task')

    assert len(captured) == 1
    assert _body_of(captured[0]) == {'actId': 'test_actor_id', 'name': 'test-task'}


async def test_publish_sets_is_public_true_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    """`publish` sends `isPublic: true` and nothing else."""
    captured: list[Request] = []
    httpserver.expect_request(_TASK_PATH, method='PUT').respond_with_handler(_capture(captured))

    await async_client.task(_MOCKED_TASK_ID).publish()

    assert len(captured) == 1
    assert _body_of(captured[0]) == {'isPublic': True}


async def test_publish_returns_the_published_task_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    """`publish` returns the parsed task, including its publication state and display configuration."""
    httpserver.expect_request(_TASK_PATH, method='PUT').respond_with_json(_TASK_RESPONSE)

    task = await async_client.task(_MOCKED_TASK_ID).publish()

    assert task.is_public is True
    assert task.public_config is not None
    assert task.public_config.published_at == datetime(2026, 8, 1, 10, 0, tzinfo=UTC)
    assert task.public_config.dataset_view == 'overview'


async def test_unpublish_sets_is_public_false_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    """`unpublish` sends `isPublic: false` rather than omitting the field."""
    captured: list[Request] = []
    httpserver.expect_request(_TASK_PATH, method='PUT').respond_with_handler(_capture(captured))

    await async_client.task(_MOCKED_TASK_ID).unpublish()

    assert len(captured) == 1
    assert _body_of(captured[0]) == {'isPublic': False}


async def test_update_sends_only_the_requested_fields_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """A plain update must send nothing but the field it was asked to change."""
    captured: list[Request] = []
    httpserver.expect_request(_TASK_PATH, method='PUT').respond_with_handler(_capture(captured))

    await async_client.task(_MOCKED_TASK_ID).update(name='renamed')

    assert len(captured) == 1
    assert _body_of(captured[0]) == {'name': 'renamed'}


async def test_update_sends_public_config_fields_async(httpserver: HTTPServer, async_client: ApifyClientAsync) -> None:
    """The `public_config_*` arguments are nested under `publicConfig` with their API names."""
    captured: list[Request] = []
    httpserver.expect_request(_TASK_PATH, method='PUT').respond_with_handler(_capture(captured))

    await async_client.task(_MOCKED_TASK_ID).update(
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


async def test_update_can_configure_and_publish_at_once_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """A single update can both fill in the display configuration and publish the task."""
    captured: list[Request] = []
    httpserver.expect_request(_TASK_PATH, method='PUT').respond_with_handler(_capture(captured))

    await async_client.task(_MOCKED_TASK_ID).update(is_public=True, public_config_dataset_view='overview')

    assert len(captured) == 1
    body = _body_of(captured[0])
    assert body['isPublic'] is True
    assert body['publicConfig'] == {'datasetView': 'overview'}


async def test_create_sends_public_config_without_publishing_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Create accepts the display configuration but never publishes the task."""
    captured: list[Request] = []
    httpserver.expect_request(_TASKS_PATH, method='POST').respond_with_handler(_capture(captured))

    await async_client.tasks().create(
        actor_id='test_actor_id',
        name='test-task',
        public_config_seo_title='Scrape a website',
    )

    assert len(captured) == 1
    body = _body_of(captured[0])
    assert body['publicConfig'] == {'seoTitle': 'Scrape a website'}
    assert 'isPublic' not in body


async def test_create_sends_only_the_requested_fields_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """A plain create must not send an empty `publicConfig`, which would demand Actor write access."""
    captured: list[Request] = []
    httpserver.expect_request(_TASKS_PATH, method='POST').respond_with_handler(_capture(captured))

    await async_client.tasks().create(actor_id='test_actor_id', name='test-task')

    assert len(captured) == 1
    assert _body_of(captured[0]) == {'actId': 'test_actor_id', 'name': 'test-task'}

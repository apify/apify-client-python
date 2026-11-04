from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from apify_client import ApifyClient, ApifyClientAsync
from apify_client.errors import NotFoundError

if TYPE_CHECKING:
    from pytest_httpserver import HTTPServer

pytestmark = pytest.mark.usefixtures('http_client_classes')

_NOT_FOUND_BODY = {'error': {'type': 'record-not-found', 'message': 'not found'}}


@pytest.mark.parametrize(
    ('child_method', 'child_path'),
    [
        pytest.param('dataset', 'dataset', id='dataset'),
        pytest.param('key_value_store', 'key-value-store', id='key-value-store'),
        pytest.param('request_queue', 'request-queue', id='request-queue'),
        pytest.param('log', 'log', id='log'),
    ],
)
def test_last_run_filters_propagate_to_chained_clients(
    httpserver: HTTPServer,
    child_method: str,
    child_path: str,
) -> None:
    """`last_run(status=..., origin=...)` filters must be sent by the chained storage clients (regression vs 1.x)."""
    httpserver.expect_request(f'/v2/actors/actor-id/runs/last/{child_path}').respond_with_json(
        _NOT_FOUND_BODY, status=404
    )
    client = ApifyClient(token='test-token', api_url=httpserver.url_for('/').removesuffix('/'))

    last_run = client.actor('actor-id').last_run(status='SUCCEEDED', origin='WEB')
    with pytest.raises(NotFoundError):
        getattr(last_run, child_method)().get()

    request, _ = httpserver.log[-1]
    assert request.args.get('status') == 'SUCCEEDED'
    assert request.args.get('origin') == 'WEB'


@pytest.mark.parametrize(
    ('child_method', 'child_path'),
    [
        pytest.param('dataset', 'dataset', id='dataset'),
        pytest.param('key_value_store', 'key-value-store', id='key-value-store'),
        pytest.param('request_queue', 'request-queue', id='request-queue'),
        pytest.param('log', 'log', id='log'),
    ],
)
async def test_last_run_filters_propagate_to_chained_clients_async(
    httpserver: HTTPServer,
    child_method: str,
    child_path: str,
) -> None:
    """`last_run(status=..., origin=...)` filters must be sent by the chained storage clients (regression vs 1.x)."""
    httpserver.expect_request(f'/v2/actors/actor-id/runs/last/{child_path}').respond_with_json(
        _NOT_FOUND_BODY, status=404
    )
    client = ApifyClientAsync(token='test-token', api_url=httpserver.url_for('/').removesuffix('/'))

    last_run = client.actor('actor-id').last_run(status='SUCCEEDED', origin='WEB')
    with pytest.raises(NotFoundError):
        await getattr(last_run, child_method)().get()

    request, _ = httpserver.log[-1]
    assert request.args.get('status') == 'SUCCEEDED'
    assert request.args.get('origin') == 'WEB'


@pytest.mark.parametrize(
    ('resource', 'path_prefix'),
    [
        pytest.param('actor', 'actors', id='actor'),
        pytest.param('task', 'actor-tasks', id='task'),
    ],
)
@pytest.mark.parametrize(
    ('kwargs', 'expected_status'),
    [
        pytest.param({}, 'SUCCEEDED', id='default'),
        pytest.param({'status': 'FAILED'}, 'FAILED', id='explicit_status'),
        pytest.param({'status': None}, None, id='any_status'),
    ],
)
def test_last_run_defaults_to_succeeded(
    httpserver: HTTPServer,
    resource: str,
    path_prefix: str,
    kwargs: dict,
    expected_status: str | None,
) -> None:
    """`last_run()` asks for the last successful run unless the caller picks a different status or opts out."""
    httpserver.expect_request(f'/v2/{path_prefix}/resource-id/runs/last').respond_with_json(_NOT_FOUND_BODY, status=404)
    client = ApifyClient(token='test-token', api_url=httpserver.url_for('/').removesuffix('/'))

    assert getattr(client, resource)('resource-id').last_run(**kwargs).get() is None

    request, _ = httpserver.log[-1]
    assert request.args.get('status') == expected_status


@pytest.mark.parametrize(
    ('resource', 'path_prefix'),
    [
        pytest.param('actor', 'actors', id='actor'),
        pytest.param('task', 'actor-tasks', id='task'),
    ],
)
@pytest.mark.parametrize(
    ('kwargs', 'expected_status'),
    [
        pytest.param({}, 'SUCCEEDED', id='default'),
        pytest.param({'status': 'FAILED'}, 'FAILED', id='explicit_status'),
        pytest.param({'status': None}, None, id='any_status'),
    ],
)
async def test_last_run_defaults_to_succeeded_async(
    httpserver: HTTPServer,
    resource: str,
    path_prefix: str,
    kwargs: dict,
    expected_status: str | None,
) -> None:
    """Async variant of `test_last_run_defaults_to_succeeded`."""
    httpserver.expect_request(f'/v2/{path_prefix}/resource-id/runs/last').respond_with_json(_NOT_FOUND_BODY, status=404)
    client = ApifyClientAsync(token='test-token', api_url=httpserver.url_for('/').removesuffix('/'))

    assert await getattr(client, resource)('resource-id').last_run(**kwargs).get() is None

    request, _ = httpserver.log[-1]
    assert request.args.get('status') == expected_status

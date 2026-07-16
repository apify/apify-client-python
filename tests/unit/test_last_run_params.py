from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from apify_client import ApifyClient, ApifyClientAsync
from apify_client.errors import NotFoundError

if TYPE_CHECKING:
    from pytest_httpserver import HTTPServer

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

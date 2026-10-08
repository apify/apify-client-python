from __future__ import annotations

import inspect
from decimal import Decimal
from typing import TYPE_CHECKING, Any

import pytest

from apify_client import ApifyClient, ApifyClientAsync

if TYPE_CHECKING:
    from collections.abc import Callable

    from pytest_httpserver import HTTPServer

pytestmark = pytest.mark.usefixtures('http_client_classes')

RUN = {
    'id': 'run-id',
    'actId': 'actor-id',
    'userId': 'user-id',
    'startedAt': '2019-11-30T07:34:24.202Z',
    'status': 'SUCCEEDED',
    'meta': {'origin': 'API'},
    'stats': {'restartCount': 0, 'resurrectCount': 0, 'computeUnits': 0.1},
    'options': {'build': 'latest', 'timeoutSecs': 300, 'memoryMbytes': 1024, 'diskMbytes': 2048},
    'buildId': 'build-id',
    'generalAccess': 'RESTRICTED',
    'defaultKeyValueStoreId': 'kvs-id',
    'defaultDatasetId': 'dataset-id',
    'defaultRequestQueueId': 'rq-id',
    'buildNumber': '0.0.1',
    'containerUrl': 'https://test.runs.apify.net',
}

STARTERS = [
    pytest.param(lambda c, **kw: c.task('task-id').start(**kw), id='start'),
    pytest.param(lambda c, **kw: c.task('task-id').call(**kw), id='call'),
]


@pytest.fixture(params=[pytest.param(ApifyClient, id='sync'), pytest.param(ApifyClientAsync, id='async')])
def client(request: pytest.FixtureRequest, httpserver: HTTPServer) -> ApifyClient | ApifyClientAsync:
    return request.param(token='test', api_url=httpserver.url_for('/').removesuffix('/'))


async def run(starter: Callable[..., Any], client: ApifyClient | ApifyClientAsync, **kwargs: Any) -> Any:
    result = starter(client, **kwargs)
    return await result if inspect.isawaitable(result) else result


@pytest.mark.parametrize('starter', STARTERS)
@pytest.mark.parametrize(
    ('max_total_charge_usd', 'expected_query'),
    [
        pytest.param(Decimal('1.5'), {'maxTotalChargeUsd': '1.5'}, id='set'),
        pytest.param(None, {}, id='omitted'),
    ],
)
async def test_task_run_sends_max_total_charge_usd(
    httpserver: HTTPServer,
    client: ApifyClient | ApifyClientAsync,
    starter: Callable[..., Any],
    max_total_charge_usd: Decimal | None,
    expected_query: dict[str, str],
) -> None:
    """`max_total_charge_usd` reaches the task run API as the `maxTotalChargeUsd` query parameter."""
    httpserver.expect_request(
        '/v2/actor-tasks/task-id/runs', method='POST', query_string=expected_query
    ).respond_with_json({'data': RUN}, status=201)
    httpserver.expect_request('/v2/actor-runs/run-id').respond_with_json({'data': RUN})

    await run(starter, client, max_total_charge_usd=max_total_charge_usd)

    httpserver.check_assertions()

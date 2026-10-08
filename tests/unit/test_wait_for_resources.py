from __future__ import annotations

import inspect
import io
import json
import logging
from datetime import timedelta
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

import pytest
from werkzeug import Request, Response

from apify_client import ApifyClient, ApifyClientAsync
from apify_client._logging import logger
from apify_client._utils import wait_for_resources
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from collections.abc import Callable

    from pytest_httpserver import HTTPServer

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
    'containerUrl': 'https://run.apify.net',
}


ERROR_MESSAGES = {
    'actor-memory-limit-exceeded': (
        'By launching this job you will exceed the memory limit of 8192MB for all your Actor runs and builds '
        '(currently used: 4096MB, requested: 8192MB). Please consider upgrading or purchasing extra memory as an '
        'add-on at https://console.apify.com/billing/subscription to increase your Actor memory limit.'
    ),
    'concurrent-runs-limit-exceeded': (
        'By launching this job you will exceed your limit of 25 concurrent Actor runs. Please consider upgrading or '
        'purchasing an increase to concurrent Actor runs as an add-on at '
        'https://console.apify.com/billing/subscription to increase your limit.'
    ),
    'invalid-input': 'Input is not valid.',
}
"""Error messages the API rejects a run start with, by error type."""


def start_actor(client: ApifyClient | ApifyClientAsync, **kwargs: Any) -> Any:
    return client.actor('actor-id').start(**kwargs)


STARTERS = [
    pytest.param(start_actor, '/v2/actors/actor-id/runs', id='actor start'),
    pytest.param(
        lambda c, **kw: c.actor('actor-id').call(logger=None, **kw), '/v2/actors/actor-id/runs', id='actor call'
    ),
    pytest.param(lambda c, **kw: c.task('task-id').start(**kw), '/v2/actor-tasks/task-id/runs', id='task start'),
    pytest.param(lambda c, **kw: c.task('task-id').call(**kw), '/v2/actor-tasks/task-id/runs', id='task call'),
]


class StartServer:
    """Rejects the start requests with the queued error types, one per request, then starts the run."""

    def __init__(self, httpserver: HTTPServer, start_path: str) -> None:
        self.rejections: list[str] = []
        self.bodies: list[bytes] = []
        httpserver.expect_request(start_path, method='POST').respond_with_handler(self.handle_start)
        httpserver.expect_request('/v2/actor-runs/run-id').respond_with_json({'data': RUN})

    def handle_start(self, request: Request) -> Response:
        self.bodies.append(request.get_data())
        if self.rejections:
            error_type = self.rejections.pop(0)
            body = {'error': {'type': error_type, 'message': ERROR_MESSAGES[error_type]}}
            return Response(json.dumps(body), status=400 if error_type == 'invalid-input' else 402)
        return Response(json.dumps({'data': RUN}), status=201, mimetype='application/json')


@pytest.fixture
def sleeps(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Make the cooldown sleeps return at once and move a fake clock forward instead, recording each delay."""
    now = 0.0
    recorded: list[float] = []

    def sleep(seconds: float) -> None:
        nonlocal now
        recorded.append(seconds)
        now += seconds

    async def async_sleep(seconds: float) -> None:
        sleep(seconds)

    monkeypatch.setattr(wait_for_resources, 'time', SimpleNamespace(monotonic=lambda: now, sleep=sleep))
    monkeypatch.setattr(wait_for_resources, 'asyncio', SimpleNamespace(sleep=async_sleep))
    return recorded


@pytest.fixture(params=[pytest.param(ApifyClient, id='sync'), pytest.param(ApifyClientAsync, id='async')])
def client(request: pytest.FixtureRequest, httpserver: HTTPServer) -> ApifyClient | ApifyClientAsync:
    return request.param(token='test', api_url=httpserver.url_for('/').removesuffix('/'))


async def run(starter: Callable[..., Any], client: ApifyClient | ApifyClientAsync, **kwargs: Any) -> Any:
    result = starter(client, **kwargs)
    return await result if inspect.isawaitable(result) else result


@pytest.mark.parametrize(('starter', 'start_path'), STARTERS)
@pytest.mark.parametrize(
    'error_type',
    [
        pytest.param('actor-memory-limit-exceeded', id='memory limit'),
        pytest.param('concurrent-runs-limit-exceeded', id='concurrent runs limit'),
    ],
)
async def test_retries_start_every_10_seconds_until_it_succeeds(
    *,
    httpserver: HTTPServer,
    client: ApifyClient | ApifyClientAsync,
    sleeps: list[float],
    starter: Callable[..., Any],
    start_path: str,
    error_type: str,
) -> None:
    """A start rejected for lack of resources is retried every 10 seconds until the run starts."""
    server = StartServer(httpserver, start_path)
    server.rejections = [error_type, error_type]

    started_run = await run(starter, client, wait_for_resources=True)

    assert started_run is not None
    assert started_run.id == 'run-id'
    assert len(server.bodies) == 3
    assert sleeps == [10, 10]


@pytest.mark.parametrize(('starter', 'start_path'), STARTERS)
async def test_raises_first_rejection_without_the_option(
    httpserver: HTTPServer,
    client: ApifyClient | ApifyClientAsync,
    sleeps: list[float],
    starter: Callable[..., Any],
    start_path: str,
) -> None:
    """Without `wait_for_resources`, a start rejected for lack of resources raises right away."""
    server = StartServer(httpserver, start_path)
    server.rejections = ['actor-memory-limit-exceeded']

    with pytest.raises(ApifyApiError) as exc_info:
        await run(starter, client)

    assert exc_info.value.type == 'actor-memory-limit-exceeded'
    assert len(server.bodies) == 1
    assert sleeps == []


async def test_raises_any_other_error_right_away(
    httpserver: HTTPServer, client: ApifyClient | ApifyClientAsync, sleeps: list[float]
) -> None:
    """An error other than a lack of resources raises without a retry."""
    server = StartServer(httpserver, '/v2/actors/actor-id/runs')
    server.rejections = ['invalid-input']

    with pytest.raises(ApifyApiError) as exc_info:
        await run(start_actor, client, wait_for_resources=True)

    assert exc_info.value.type == 'invalid-input'
    assert len(server.bodies) == 1
    assert sleeps == []


async def test_timedelta_bounds_the_retrying(
    *,
    httpserver: HTTPServer,
    client: ApifyClient | ApifyClientAsync,
    sleeps: list[float],
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A `timedelta` bounds the retrying, after which the last rejection is raised."""
    server = StartServer(httpserver, '/v2/actors/actor-id/runs')
    server.rejections = ['actor-memory-limit-exceeded'] * 10
    monkeypatch.setattr(logger, 'propagate', True)

    with caplog.at_level(logging.INFO, logger=logger.name), pytest.raises(ApifyApiError) as exc_info:
        await run(start_actor, client, wait_for_resources=timedelta(seconds=25))

    assert exc_info.value.type == 'actor-memory-limit-exceeded'
    # Attempts at 0, 10, 20 and 25 seconds, the last cooldown cut short by the bound.
    assert len(server.bodies) == 4
    assert sleeps == [10, 10, 5]
    assert [record.getMessage() for record in caplog.records] == [
        f'Not enough resources to start the run, retrying in 10s: {ERROR_MESSAGES["actor-memory-limit-exceeded"]}',
        f'Not enough resources to start the run, retrying in 10s: {ERROR_MESSAGES["actor-memory-limit-exceeded"]}',
        f'Not enough resources to start the run, retrying in 5s: {ERROR_MESSAGES["actor-memory-limit-exceeded"]}',
    ]


async def test_zero_timedelta_makes_a_single_attempt(
    httpserver: HTTPServer, client: ApifyClient | ApifyClientAsync, sleeps: list[float]
) -> None:
    """A zero `timedelta` raises the first rejection without a retry."""
    server = StartServer(httpserver, '/v2/actors/actor-id/runs')
    server.rejections = ['actor-memory-limit-exceeded']

    with pytest.raises(ApifyApiError):
        await run(start_actor, client, wait_for_resources=timedelta(0))

    assert len(server.bodies) == 1
    assert sleeps == []


async def test_retry_resends_a_file_like_input(
    httpserver: HTTPServer, client: ApifyClient | ApifyClientAsync, sleeps: list[float]
) -> None:
    """A file-like run input is sent whole again on every retry of the start."""
    server = StartServer(httpserver, '/v2/actors/actor-id/runs')
    server.rejections = ['actor-memory-limit-exceeded']

    await run(
        start_actor,
        client,
        run_input=io.BytesIO(b'{"a": 1}'),
        content_type='application/json',
        wait_for_resources=True,
    )

    assert server.bodies == [b'{"a": 1}', b'{"a": 1}']
    assert sleeps == [10]


async def test_unrewindable_streamed_input_is_not_retried(
    httpserver: HTTPServer, client: ApifyClient | ApifyClientAsync, sleeps: list[float]
) -> None:
    """A streamed run input that cannot be rewound is sent once, and its rejection is raised without a retry."""
    server = StartServer(httpserver, '/v2/actors/actor-id/runs')
    server.rejections = ['actor-memory-limit-exceeded']

    with pytest.raises(ApifyApiError):
        await run(
            start_actor,
            client,
            run_input=iter([b'{"a": ', b'1}']),
            content_type='application/json',
            wait_for_resources=True,
        )

    assert server.bodies == [b'{"a": 1}']
    assert sleeps == []

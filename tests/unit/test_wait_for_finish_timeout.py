from __future__ import annotations

import inspect
import json
from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING, Any
from unittest.mock import Mock

import pytest
from werkzeug import Request, Response

from apify_client import ApifyClient, ApifyClientAsync

if TYPE_CHECKING:
    from collections.abc import Callable

    from pytest_httpserver import HTTPServer

    from apify_client.types import Timeout

pytestmark = pytest.mark.usefixtures('http_client_classes')

ACTOR_ID = 'test_actor_id'
TASK_ID = 'test_task_id'
RUN_ID = 'test_run_id'
BUILD_ID = 'test_build_id'

RUN_RESPONSE = {
    'data': {
        'id': 'test_run_id',
        'actId': ACTOR_ID,
        'userId': 'test_user_id',
        'startedAt': '2026-08-01T10:00:00.000Z',
        'status': 'RUNNING',
        'meta': {'origin': 'API'},
        'stats': {'restartCount': 0, 'resurrectCount': 0, 'computeUnits': 0.1},
        'options': {'build': 'latest', 'timeoutSecs': 300, 'memoryMbytes': 1024, 'diskMbytes': 2048},
        'buildId': 'test_build_id',
        'generalAccess': 'RESTRICTED',
        'defaultKeyValueStoreId': 'test_kvs_id',
        'defaultDatasetId': 'test_dataset_id',
        'defaultRequestQueueId': 'test_rq_id',
        'buildNumber': '0.0.1',
        'containerUrl': 'https://test.runs.apify.net',
    }
}

BUILD_RESPONSE = {
    'data': {
        'id': 'test_build_id',
        'actId': ACTOR_ID,
        'userId': 'test_user_id',
        'startedAt': '2026-08-01T10:00:00.000Z',
        'status': 'RUNNING',
        'meta': {'origin': 'API'},
        'buildNumber': '0.0.1',
    }
}


def _as_wait_for_finish_timedelta(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Convert the `wait_for_finish` seconds used by the other call sites to the `timedelta` `get` expects."""
    wait_for_finish = kwargs.get('wait_for_finish')
    if wait_for_finish is None:
        return kwargs
    return {**kwargs, 'wait_for_finish': timedelta(seconds=wait_for_finish)}


@dataclass(frozen=True)
class CallSite:
    """A client method that sends `waitForFinish`, with the endpoint it calls and its default timeout tier."""

    invoke: Callable[..., Any]
    method: str
    path: str
    response_body: dict
    tier_secs: int


CALL_SITES = [
    pytest.param(
        CallSite(
            invoke=lambda client, **kwargs: client.actor(ACTOR_ID).start(**kwargs),
            method='POST',
            path=f'/v2/actors/{ACTOR_ID}/runs',
            response_body=RUN_RESPONSE,
            tier_secs=30,
        ),
        id='actor start',
    ),
    pytest.param(
        CallSite(
            invoke=lambda client, **kwargs: client.actor(ACTOR_ID).build(version_number='0.0', **kwargs),
            method='POST',
            path=f'/v2/actors/{ACTOR_ID}/builds',
            response_body=BUILD_RESPONSE,
            tier_secs=30,
        ),
        id='actor build',
    ),
    pytest.param(
        CallSite(
            invoke=lambda client, **kwargs: client.actor(ACTOR_ID).default_build(**kwargs),
            method='GET',
            path=f'/v2/actors/{ACTOR_ID}/builds/default',
            response_body=BUILD_RESPONSE,
            tier_secs=5,
        ),
        id='actor default build',
    ),
    pytest.param(
        CallSite(
            invoke=lambda client, **kwargs: client.task(TASK_ID).start(**kwargs),
            method='POST',
            path=f'/v2/actor-tasks/{TASK_ID}/runs',
            response_body=RUN_RESPONSE,
            tier_secs=30,
        ),
        id='task start',
    ),
    pytest.param(
        CallSite(
            invoke=lambda client, **kwargs: client.run(RUN_ID).get(**_as_wait_for_finish_timedelta(kwargs)),
            method='GET',
            path=f'/v2/actor-runs/{RUN_ID}',
            response_body=RUN_RESPONSE,
            tier_secs=5,
        ),
        id='run get',
    ),
    pytest.param(
        CallSite(
            invoke=lambda client, **kwargs: client.build(BUILD_ID).get(**_as_wait_for_finish_timedelta(kwargs)),
            method='GET',
            path=f'/v2/actor-builds/{BUILD_ID}',
            response_body=BUILD_RESPONSE,
            tier_secs=5,
        ),
        id='build get',
    ),
]

GET_CALL_SITES = [
    pytest.param(
        lambda client, **kwargs: client.run(RUN_ID).get(**kwargs),
        f'/v2/actor-runs/{RUN_ID}',
        RUN_RESPONSE,
        id='run get',
    ),
    pytest.param(
        lambda client, **kwargs: client.build(BUILD_ID).get(**kwargs),
        f'/v2/actor-builds/{BUILD_ID}',
        BUILD_RESPONSE,
        id='build get',
    ),
]


@pytest.fixture(params=[pytest.param(ApifyClient, id='sync'), pytest.param(ApifyClientAsync, id='async')])
def client(request: pytest.FixtureRequest, httpserver: HTTPServer) -> ApifyClient | ApifyClientAsync:
    return request.param(
        token='test',
        api_url=httpserver.url_for('/').removesuffix('/'),
        timeout_short=timedelta(seconds=5),
        timeout_medium=timedelta(seconds=30),
    )


async def call_and_capture_timeout(
    client: ApifyClient | ApifyClientAsync,
    monkeypatch: pytest.MonkeyPatch,
    httpserver: HTTPServer,
    call_site: CallSite,
    **kwargs: Any,
) -> float | None:
    """Invoke the call site against a mocked endpoint and return the timeout of the first request attempt."""
    response = Response(json.dumps(call_site.response_body), status=200, mimetype='application/json')
    httpserver.expect_request(call_site.path, method=call_site.method).respond_with_response(response)
    http_client = client.http_client
    send_request = Mock(wraps=http_client.send_request)
    monkeypatch.setattr(http_client, 'send_request', send_request)

    result = call_site.invoke(client, **kwargs)
    if inspect.isawaitable(result):
        await result

    return send_request.call_args_list[0].kwargs['timeout']


@pytest.mark.parametrize('call_site', CALL_SITES)
async def test_default_timeout_covers_wait_for_finish(
    client: ApifyClient | ApifyClientAsync,
    monkeypatch: pytest.MonkeyPatch,
    httpserver: HTTPServer,
    call_site: CallSite,
) -> None:
    """The default timeout tier is extended by `wait_for_finish`, so the request outlasts the API's hold."""
    timeout = await call_and_capture_timeout(client, monkeypatch, httpserver, call_site, wait_for_finish=60)

    assert timeout == call_site.tier_secs + 60


@pytest.mark.parametrize('call_site', CALL_SITES)
async def test_explicit_timeout_ignores_wait_for_finish(
    client: ApifyClient | ApifyClientAsync,
    monkeypatch: pytest.MonkeyPatch,
    httpserver: HTTPServer,
    call_site: CallSite,
) -> None:
    """An explicit `timedelta` timeout is used as given, whatever `wait_for_finish` is."""
    timeout = await call_and_capture_timeout(
        client, monkeypatch, httpserver, call_site, wait_for_finish=60, timeout=timedelta(seconds=7)
    )

    assert timeout == 7


@pytest.mark.parametrize(
    ('timeout', 'wait_for_finish', 'expected'),
    [
        pytest.param('medium', None, 'medium', id='no wait'),
        pytest.param('medium', 0, 'medium', id='zero wait'),
        pytest.param('medium', -5, 'medium', id='negative wait'),
        pytest.param('medium', 20, timedelta(seconds=50), id='medium tier'),
        pytest.param('short', 20, timedelta(seconds=25), id='short tier'),
        pytest.param('medium', 600, timedelta(seconds=90), id='wait above API maximum'),
        pytest.param('no_timeout', 60, 'no_timeout', id='no timeout'),
        pytest.param(timedelta(seconds=7), 60, timedelta(seconds=7), id='explicit timedelta'),
    ],
)
def test_timeout_for_wait_for_finish(
    client: ApifyClient | ApifyClientAsync,
    timeout: Timeout,
    wait_for_finish: int | None,
    expected: Timeout,
) -> None:
    """A timeout tier is extended by `wait_for_finish`, capped at the API's 60 s hold; other timeouts stay as given."""
    actor_client = client.actor(ACTOR_ID)

    assert actor_client._timeout_for_wait_for_finish(timeout, wait_for_finish) == expected


@pytest.mark.parametrize(('invoke', 'path', 'response_body'), GET_CALL_SITES)
async def test_get_sends_wait_for_finish_as_whole_seconds(
    client: ApifyClient | ApifyClientAsync,
    httpserver: HTTPServer,
    invoke: Callable[..., Any],
    path: str,
    response_body: dict,
) -> None:
    """`get` sends `wait_for_finish` as the `waitForFinish` query parameter, rounded down to whole seconds."""
    captured: list[Request] = []

    def handler(request: Request) -> Response:
        captured.append(request)
        return Response(json.dumps(response_body), status=200, mimetype='application/json')

    httpserver.expect_request(path, method='GET').respond_with_handler(handler)

    result = invoke(client, wait_for_finish=timedelta(seconds=45, milliseconds=500))
    if inspect.isawaitable(result):
        await result

    assert captured[0].args.get('waitForFinish') == '45'


@pytest.mark.parametrize(('invoke', 'path', 'response_body'), GET_CALL_SITES)
async def test_get_omits_wait_for_finish_by_default(
    client: ApifyClient | ApifyClientAsync,
    httpserver: HTTPServer,
    invoke: Callable[..., Any],
    path: str,
    response_body: dict,
) -> None:
    """`get` omits the `waitForFinish` query parameter when `wait_for_finish` is not given."""
    captured: list[Request] = []

    def handler(request: Request) -> Response:
        captured.append(request)
        return Response(json.dumps(response_body), status=200, mimetype='application/json')

    httpserver.expect_request(path, method='GET').respond_with_handler(handler)

    result = invoke(client)
    if inspect.isawaitable(result):
        await result

    assert 'waitForFinish' not in captured[0].args

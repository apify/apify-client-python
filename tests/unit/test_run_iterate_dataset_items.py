from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, Mock, call

import pytest
from werkzeug import Response

from apify_client import ApifyClient, ApifyClientAsync

if TYPE_CHECKING:
    from pytest_httpserver import HTTPServer
    from werkzeug import Request

    from apify_client._literals import ActorJobStatus

pytestmark = pytest.mark.usefixtures('http_client_classes')

RUN_ID = 'test-run-id'
RUN_PATH = f'/v2/actor-runs/{RUN_ID}'
UNWIND_PARTS = 3
NO_WAIT = timedelta(0)


@dataclass
class Step:
    """State of the run that the fake API switches to on one run status read."""

    pushed_rows: int
    """Total number of rows in the dataset, readable right away."""

    item_count: int
    """The dataset's `itemCount`, which lags behind the pushed rows."""

    status: ActorJobStatus


@dataclass
class FakeRunApi:
    """Fake run, run dataset and dataset items endpoints, advanced by one `Step` per run status read."""

    steps: list[Step]
    step_index: int = -1

    @property
    def step(self) -> Step:
        return self.steps[max(self.step_index, 0)]

    def register(self, httpserver: HTTPServer) -> None:
        httpserver.expect_request(RUN_PATH, method='GET').respond_with_handler(self.handle_run)
        httpserver.expect_request(f'{RUN_PATH}/dataset', method='GET').respond_with_handler(self.handle_dataset)
        httpserver.expect_request(f'{RUN_PATH}/dataset/items', method='GET').respond_with_handler(self.handle_items)

    def handle_run(self, _request: Request) -> Response:
        self.step_index = min(self.step_index + 1, len(self.steps) - 1)
        run = {
            'id': RUN_ID,
            'actId': 'test-actor-id',
            'userId': 'test-user-id',
            'startedAt': '2019-11-30T07:34:24.202Z',
            'status': self.step.status,
            'meta': {'origin': 'WEB'},
            'stats': {'restartCount': 0, 'resurrectCount': 0, 'computeUnits': 0.1},
            'options': {'build': 'latest', 'timeoutSecs': 300, 'memoryMbytes': 1024, 'diskMbytes': 2048},
            'buildId': 'test-build-id',
            'defaultKeyValueStoreId': 'test-kvs-id',
            'defaultDatasetId': 'test-dataset-id',
            'defaultRequestQueueId': 'test-rq-id',
            'containerUrl': 'https://test.runs.apify.net',
        }
        return Response(json.dumps({'data': run}), status=200, mimetype='application/json')

    def handle_dataset(self, _request: Request) -> Response:
        dataset = {
            'id': 'test-dataset-id',
            'userId': 'test-user-id',
            'createdAt': '2019-12-12T07:34:14.202Z',
            'modifiedAt': '2019-12-13T08:36:13.202Z',
            'accessedAt': '2019-12-14T08:36:13.202Z',
            'itemCount': self.step.item_count,
            'cleanItemCount': self.step.item_count,
            'consoleUrl': 'https://console.apify.com/storage/datasets/test-dataset-id',
        }
        return Response(json.dumps({'data': dataset}), status=200, mimetype='application/json')

    def handle_items(self, request: Request) -> Response:
        """Scan exactly `limit` rows from `offset`, like the real endpoint, and derive the count from `itemCount`."""
        offset = int(request.args.get('offset', 0))
        limit = int(request.args.get('limit', 0)) or 999_999_999_999
        rows = range(offset, min(offset + limit, self.step.pushed_rows))
        items = shape_items(rows, clean=request.args.get('clean') == 'true', unwind=bool(request.args.get('unwind')))
        headers = {
            'x-apify-pagination-total': str(self.step.item_count),
            'x-apify-pagination-offset': str(offset),
            'x-apify-pagination-count': str(max(min(self.step.item_count - offset, limit), 0)),
            'x-apify-pagination-limit': str(limit),
            'x-apify-pagination-desc': 'false',
        }
        return Response(json.dumps(items), status=200, headers=headers, mimetype='application/json')


def shape_items(rows: range, *, clean: bool = False, unwind: bool = False) -> list[dict[str, Any]]:
    """Turn dataset rows into items: `clean` drops every odd row, `unwind` splits a row into `UNWIND_PARTS` items."""
    kept_rows = [row for row in rows if not (clean and row % 2)]
    if unwind:
        return [{'row': row, 'part': part} for row in kept_rows for part in range(UNWIND_PARTS)]
    return [{'row': row} for row in kept_rows]


LAGGING_RUN_STEPS = [
    Step(pushed_rows=3, item_count=0, status='READY'),
    Step(pushed_rows=40, item_count=3, status='RUNNING'),
    Step(pushed_rows=52, item_count=25, status='RUNNING'),
    # The run has finished, but `itemCount` still lags more than one page behind the readable rows.
    Step(pushed_rows=75, item_count=52, status='SUCCEEDED'),
]

# The same run with `itemCount` caught up by the time it finished.
CAUGHT_UP_RUN_STEPS = [*LAGGING_RUN_STEPS[:-1], Step(pushed_rows=52, item_count=52, status='SUCCEEDED')]


def test_iterate_dataset_items_yields_every_row_once_sync(httpserver: HTTPServer) -> None:
    """Rows pushed across polls and past a lagging item count after the run finished are all yielded, in order."""
    api = FakeRunApi(LAGGING_RUN_STEPS)
    api.register(httpserver)
    client = ApifyClient(token='test-token', api_url=httpserver.url_for('/').removesuffix('/'))

    items = list(client.run(RUN_ID).iterate_dataset_items(chunk_size=10, poll_interval=NO_WAIT))

    assert items == shape_items(range(75))


async def test_iterate_dataset_items_yields_every_row_once_async(httpserver: HTTPServer) -> None:
    """Rows pushed across polls and past a lagging item count after the run finished are all yielded, in order."""
    api = FakeRunApi(LAGGING_RUN_STEPS)
    api.register(httpserver)
    client = ApifyClientAsync(token='test-token', api_url=httpserver.url_for('/').removesuffix('/'))

    items = [item async for item in client.run(RUN_ID).iterate_dataset_items(chunk_size=10, poll_interval=NO_WAIT)]

    assert items == shape_items(range(75))


@pytest.mark.parametrize(
    'shaping',
    [
        pytest.param({'clean': True}, id='clean drops items'),
        pytest.param({'unwind': True}, id='unwind multiplies items'),
    ],
)
def test_iterate_dataset_items_with_shaped_items_sync(httpserver: HTTPServer, shaping: dict[str, bool]) -> None:
    """Filters and `unwind` change the item count per page without duplicating or skipping rows while the run runs."""
    api = FakeRunApi(CAUGHT_UP_RUN_STEPS)
    api.register(httpserver)
    client = ApifyClient(token='test-token', api_url=httpserver.url_for('/').removesuffix('/'))

    items = list(
        client.run(RUN_ID).iterate_dataset_items(
            clean=shaping.get('clean'),
            unwind=['parts'] if shaping.get('unwind') else None,
            chunk_size=10,
            poll_interval=NO_WAIT,
        )
    )

    assert items == shape_items(range(52), **shaping)


@pytest.mark.parametrize(
    'shaping',
    [
        pytest.param({'clean': True}, id='clean drops items'),
        pytest.param({'unwind': True}, id='unwind multiplies items'),
    ],
)
async def test_iterate_dataset_items_with_shaped_items_async(httpserver: HTTPServer, shaping: dict[str, bool]) -> None:
    """Filters and `unwind` change the item count per page without duplicating or skipping rows while the run runs."""
    api = FakeRunApi(CAUGHT_UP_RUN_STEPS)
    api.register(httpserver)
    client = ApifyClientAsync(token='test-token', api_url=httpserver.url_for('/').removesuffix('/'))

    items = [
        item
        async for item in client.run(RUN_ID).iterate_dataset_items(
            clean=shaping.get('clean'),
            unwind=['parts'] if shaping.get('unwind') else None,
            chunk_size=10,
            poll_interval=NO_WAIT,
        )
    ]

    assert items == shape_items(range(52), **shaping)


@pytest.mark.parametrize(
    'status',
    [
        pytest.param('ABORTING', id='aborting'),
        pytest.param('TIMING-OUT', id='timing out'),
    ],
)
def test_iterate_dataset_items_keeps_polling_until_terminal_sync(
    httpserver: HTTPServer, status: ActorJobStatus
) -> None:
    """A run that is aborting or timing out can still push items, so polling goes on until a terminal status."""
    api = FakeRunApi(
        [
            Step(pushed_rows=5, item_count=5, status=status),
            Step(pushed_rows=8, item_count=8, status='ABORTED'),
        ]
    )
    api.register(httpserver)
    client = ApifyClient(token='test-token', api_url=httpserver.url_for('/').removesuffix('/'))

    items = list(client.run(RUN_ID).iterate_dataset_items(poll_interval=NO_WAIT))

    assert items == shape_items(range(8))


@pytest.mark.parametrize(
    'status',
    [
        pytest.param('ABORTING', id='aborting'),
        pytest.param('TIMING-OUT', id='timing out'),
    ],
)
async def test_iterate_dataset_items_keeps_polling_until_terminal_async(
    httpserver: HTTPServer, status: ActorJobStatus
) -> None:
    """A run that is aborting or timing out can still push items, so polling goes on until a terminal status."""
    api = FakeRunApi(
        [
            Step(pushed_rows=5, item_count=5, status=status),
            Step(pushed_rows=8, item_count=8, status='ABORTED'),
        ]
    )
    api.register(httpserver)
    client = ApifyClientAsync(token='test-token', api_url=httpserver.url_for('/').removesuffix('/'))

    items = [item async for item in client.run(RUN_ID).iterate_dataset_items(poll_interval=NO_WAIT)]

    assert items == shape_items(range(8))


def test_iterate_dataset_items_respects_offset_and_limit_sync(httpserver: HTTPServer) -> None:
    """Iteration starts at `offset` and stops once `limit` rows are scanned, without waiting for the run to finish."""
    api = FakeRunApi(
        [Step(pushed_rows=4, item_count=4, status='RUNNING'), Step(pushed_rows=20, item_count=20, status='RUNNING')]
    )
    api.register(httpserver)
    client = ApifyClient(token='test-token', api_url=httpserver.url_for('/').removesuffix('/'))

    items = list(client.run(RUN_ID).iterate_dataset_items(offset=2, limit=7, chunk_size=3, poll_interval=NO_WAIT))

    assert items == shape_items(range(2, 9))
    assert api.step.status == 'RUNNING'


async def test_iterate_dataset_items_respects_offset_and_limit_async(httpserver: HTTPServer) -> None:
    """Iteration starts at `offset` and stops once `limit` rows are scanned, without waiting for the run to finish."""
    api = FakeRunApi(
        [Step(pushed_rows=4, item_count=4, status='RUNNING'), Step(pushed_rows=20, item_count=20, status='RUNNING')]
    )
    api.register(httpserver)
    client = ApifyClientAsync(token='test-token', api_url=httpserver.url_for('/').removesuffix('/'))

    items = [
        item
        async for item in client.run(RUN_ID).iterate_dataset_items(
            offset=2, limit=7, chunk_size=3, poll_interval=NO_WAIT
        )
    ]

    assert items == shape_items(range(2, 9))
    assert api.step.status == 'RUNNING'


def test_iterate_dataset_items_sleeps_between_polls_sync(
    httpserver: HTTPServer, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The iterator waits `poll_interval` after each poll of an unfinished run and not after the final one."""
    api = FakeRunApi(LAGGING_RUN_STEPS)
    api.register(httpserver)
    client = ApifyClient(token='test-token', api_url=httpserver.url_for('/').removesuffix('/'))
    sleep = Mock()
    monkeypatch.setattr('apify_client._resource_clients.run.time.sleep', sleep)

    list(client.run(RUN_ID).iterate_dataset_items(poll_interval=timedelta(seconds=2)))

    assert sleep.call_args_list == [call(2.0)] * 3


async def test_iterate_dataset_items_sleeps_between_polls_async(
    httpserver: HTTPServer, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The iterator waits `poll_interval` after each poll of an unfinished run and not after the final one."""
    api = FakeRunApi(LAGGING_RUN_STEPS)
    api.register(httpserver)
    client = ApifyClientAsync(token='test-token', api_url=httpserver.url_for('/').removesuffix('/'))
    sleep = AsyncMock()
    monkeypatch.setattr('apify_client._resource_clients.run.asyncio.sleep', sleep)

    [item async for item in client.run(RUN_ID).iterate_dataset_items(poll_interval=timedelta(seconds=2))]

    assert sleep.call_args_list == [call(2.0)] * 3

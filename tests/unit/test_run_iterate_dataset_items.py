from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import timedelta
from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, Mock, call

import pytest
from werkzeug import Response

if TYPE_CHECKING:
    from pytest_httpserver import HTTPServer
    from werkzeug import Request

    from apify_client import ApifyClient, ApifyClientAsync
    from apify_client._literals import ActorJobStatus
    from apify_client._models import Run

pytestmark = pytest.mark.usefixtures('http_client_classes')

RUN_ID = 'test-run-id'
RUN_PATH = f'/v2/actor-runs/{RUN_ID}'
ACTOR_ID = 'test-actor-id'
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
    run_requests: list[dict[str, str]] = field(default_factory=list)
    last_run_requests: int = 0
    items_requests: list[dict[str, str]] = field(default_factory=list)

    @property
    def step(self) -> Step:
        return self.steps[max(self.step_index, 0)]

    def register(self, httpserver: HTTPServer) -> None:
        httpserver.expect_request(RUN_PATH, method='GET').respond_with_handler(self.handle_run)
        httpserver.expect_request(f'{RUN_PATH}/dataset', method='GET').respond_with_handler(self.handle_dataset)
        httpserver.expect_request(f'{RUN_PATH}/dataset/items', method='GET').respond_with_handler(self.handle_items)
        httpserver.expect_request(f'/v2/actors/{ACTOR_ID}/runs/last', method='GET').respond_with_handler(
            self.handle_last_run
        )

    def handle_run(self, request: Request) -> Response:
        self.run_requests.append(dict(request.args))
        self.step_index = min(self.step_index + 1, len(self.steps) - 1)
        run = {
            'id': RUN_ID,
            'actId': ACTOR_ID,
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

    def handle_last_run(self, request: Request) -> Response:
        self.last_run_requests += 1
        return self.handle_run(request)

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
        self.items_requests.append(dict(request.args))
        rows = range(offset, min(offset + limit, self.step.pushed_rows))
        items = shape_items(
            rows,
            clean=request.args.get('clean') == 'true',
            skip_empty=request.args.get('skipEmpty') == 'true',
            unwind=bool(request.args.get('unwind')),
        )
        headers = {
            'x-apify-pagination-total': str(self.step.item_count),
            'x-apify-pagination-offset': str(offset),
            'x-apify-pagination-count': str(max(min(self.step.item_count - offset, limit), 0)),
            'x-apify-pagination-limit': str(limit),
            'x-apify-pagination-desc': 'false',
        }
        return Response(json.dumps(items), status=200, headers=headers, mimetype='application/json')


def shape_items(
    rows: range, *, clean: bool = False, skip_empty: bool = False, unwind: bool = False
) -> list[dict[str, Any]]:
    """Turn dataset rows into items: `clean` and `skip_empty` drop every odd row, `unwind` splits a row into items.

    Under `unwind`, every third row holds an empty array and so unwinds into no items at all.
    """
    kept_rows = [row for row in rows if not ((clean or skip_empty) and row % 2)]
    if unwind:
        return [{'row': row, 'part': part} for row in kept_rows if row % 3 != 2 for part in range(UNWIND_PARTS)]
    return [{'row': row} for row in kept_rows]


LAGGING_RUN_STEPS = [
    Step(pushed_rows=3, item_count=0, status='READY'),
    Step(pushed_rows=40, item_count=3, status='RUNNING'),
    Step(pushed_rows=52, item_count=25, status='RUNNING'),
    # The run has finished, but `itemCount` still lags more than one page behind the readable rows.
    Step(pushed_rows=75, item_count=52, status='SUCCEEDED'),
]


def test_iterate_dataset_items_yields_every_row_once_sync(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """Rows pushed across polls and past a lagging item count after the run finished are all yielded, in order."""
    api = FakeRunApi(LAGGING_RUN_STEPS)
    api.register(httpserver)

    items = list(sync_client.run(RUN_ID).iterate_dataset_items(chunk_size=10, poll_interval=NO_WAIT))

    assert items == shape_items(range(75))


async def test_iterate_dataset_items_yields_every_row_once_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Rows pushed across polls and past a lagging item count after the run finished are all yielded, in order."""
    api = FakeRunApi(LAGGING_RUN_STEPS)
    api.register(httpserver)

    items = [
        item async for item in async_client.run(RUN_ID).iterate_dataset_items(chunk_size=10, poll_interval=NO_WAIT)
    ]

    assert items == shape_items(range(75))


CHUNK_SIZES = [
    pytest.param(10, id='partly filtered pages'),
    pytest.param(1, id='fully filtered pages'),
]


@pytest.mark.parametrize('chunk_size', CHUNK_SIZES)
@pytest.mark.parametrize(
    'shaping',
    [
        pytest.param({'clean': True}, id='clean drops items'),
        pytest.param({'skip_empty': True}, id='skip_empty drops items'),
        pytest.param({'unwind': True}, id='unwind multiplies or drops items'),
    ],
)
def test_iterate_dataset_items_with_shaped_items_sync(
    httpserver: HTTPServer, sync_client: ApifyClient, shaping: dict[str, bool], chunk_size: int
) -> None:
    """Filters and `unwind` reshape or empty pages without duplicating or skipping rows, also past a lagging count."""
    api = FakeRunApi(LAGGING_RUN_STEPS)
    api.register(httpserver)

    items = list(
        sync_client.run(RUN_ID).iterate_dataset_items(
            clean=shaping.get('clean'),
            skip_empty=shaping.get('skip_empty'),
            unwind=['parts'] if shaping.get('unwind') else None,
            chunk_size=chunk_size,
            poll_interval=NO_WAIT,
        )
    )

    assert items == shape_items(range(75), **shaping)


@pytest.mark.parametrize('chunk_size', CHUNK_SIZES)
@pytest.mark.parametrize(
    'shaping',
    [
        pytest.param({'clean': True}, id='clean drops items'),
        pytest.param({'skip_empty': True}, id='skip_empty drops items'),
        pytest.param({'unwind': True}, id='unwind multiplies or drops items'),
    ],
)
async def test_iterate_dataset_items_with_shaped_items_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync, shaping: dict[str, bool], chunk_size: int
) -> None:
    """Filters and `unwind` reshape or empty pages without duplicating or skipping rows, also past a lagging count."""
    api = FakeRunApi(LAGGING_RUN_STEPS)
    api.register(httpserver)

    items = [
        item
        async for item in async_client.run(RUN_ID).iterate_dataset_items(
            clean=shaping.get('clean'),
            skip_empty=shaping.get('skip_empty'),
            unwind=['parts'] if shaping.get('unwind') else None,
            chunk_size=chunk_size,
            poll_interval=NO_WAIT,
        )
    ]

    assert items == shape_items(range(75), **shaping)


@pytest.mark.parametrize(
    'status',
    [
        pytest.param('ABORTING', id='aborting'),
        pytest.param('TIMING-OUT', id='timing out'),
    ],
)
def test_iterate_dataset_items_keeps_polling_until_terminal_sync(
    httpserver: HTTPServer, sync_client: ApifyClient, status: ActorJobStatus
) -> None:
    """A run that is aborting or timing out can still push items, so polling goes on until a terminal status."""
    api = FakeRunApi(
        [
            Step(pushed_rows=5, item_count=5, status=status),
            Step(pushed_rows=8, item_count=8, status='ABORTED'),
        ]
    )
    api.register(httpserver)

    items = list(sync_client.run(RUN_ID).iterate_dataset_items(poll_interval=NO_WAIT))

    assert items == shape_items(range(8))


@pytest.mark.parametrize(
    'status',
    [
        pytest.param('ABORTING', id='aborting'),
        pytest.param('TIMING-OUT', id='timing out'),
    ],
)
async def test_iterate_dataset_items_keeps_polling_until_terminal_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync, status: ActorJobStatus
) -> None:
    """A run that is aborting or timing out can still push items, so polling goes on until a terminal status."""
    api = FakeRunApi(
        [
            Step(pushed_rows=5, item_count=5, status=status),
            Step(pushed_rows=8, item_count=8, status='ABORTED'),
        ]
    )
    api.register(httpserver)

    items = [item async for item in async_client.run(RUN_ID).iterate_dataset_items(poll_interval=NO_WAIT)]

    assert items == shape_items(range(8))


def test_iterate_dataset_items_respects_offset_and_limit_sync(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """Iteration starts at `offset` and stops once `limit` rows are scanned, without waiting for the run to finish."""
    api = FakeRunApi(
        [Step(pushed_rows=4, item_count=4, status='RUNNING'), Step(pushed_rows=20, item_count=20, status='RUNNING')]
    )
    api.register(httpserver)

    items = list(sync_client.run(RUN_ID).iterate_dataset_items(offset=2, limit=7, chunk_size=3, poll_interval=NO_WAIT))

    assert items == shape_items(range(2, 9))
    assert api.step.status == 'RUNNING'


async def test_iterate_dataset_items_respects_offset_and_limit_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Iteration starts at `offset` and stops once `limit` rows are scanned, without waiting for the run to finish."""
    api = FakeRunApi(
        [Step(pushed_rows=4, item_count=4, status='RUNNING'), Step(pushed_rows=20, item_count=20, status='RUNNING')]
    )
    api.register(httpserver)

    items = [
        item
        async for item in async_client.run(RUN_ID).iterate_dataset_items(
            offset=2, limit=7, chunk_size=3, poll_interval=NO_WAIT
        )
    ]

    assert items == shape_items(range(2, 9))
    assert api.step.status == 'RUNNING'


def test_iterate_dataset_items_limit_ends_reading_past_item_count_sync(
    httpserver: HTTPServer, sync_client: ApifyClient
) -> None:
    """A `limit` beyond the lagging item count of a finished run stops the reads past it at the limit."""
    api = FakeRunApi(LAGGING_RUN_STEPS)
    api.register(httpserver)

    items = list(sync_client.run(RUN_ID).iterate_dataset_items(limit=60, chunk_size=10, poll_interval=NO_WAIT))

    assert items == shape_items(range(60))


async def test_iterate_dataset_items_limit_ends_reading_past_item_count_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """A `limit` beyond the lagging item count of a finished run stops the reads past it at the limit."""
    api = FakeRunApi(LAGGING_RUN_STEPS)
    api.register(httpserver)

    items = [
        item
        async for item in async_client.run(RUN_ID).iterate_dataset_items(limit=60, chunk_size=10, poll_interval=NO_WAIT)
    ]

    assert items == shape_items(range(60))


def test_iterate_dataset_items_forwards_options_without_extra_read_sync(
    httpserver: HTTPServer, sync_client: ApifyClient
) -> None:
    """Item options reach every page request, and without a dropping filter an empty page ends with no plain read."""
    api = FakeRunApi([Step(pushed_rows=5, item_count=3, status='SUCCEEDED')])
    api.register(httpserver)

    items = list(sync_client.run(RUN_ID).iterate_dataset_items(fields=['row'], chunk_size=10, poll_interval=NO_WAIT))

    assert items == shape_items(range(5))
    assert [request.get('fields') for request in api.items_requests] == ['row', 'row', 'row']


async def test_iterate_dataset_items_forwards_options_without_extra_read_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Item options reach every page request, and without a dropping filter an empty page ends with no plain read."""
    api = FakeRunApi([Step(pushed_rows=5, item_count=3, status='SUCCEEDED')])
    api.register(httpserver)

    items = [
        item
        async for item in async_client.run(RUN_ID).iterate_dataset_items(
            fields=['row'], chunk_size=10, poll_interval=NO_WAIT
        )
    ]

    assert items == shape_items(range(5))
    assert [request.get('fields') for request in api.items_requests] == ['row', 'row', 'row']


def test_iterate_dataset_items_waits_for_finish_between_polls_sync(
    httpserver: HTTPServer, sync_client: ApifyClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Each poll of an unfinished run waits up to `poll_interval` for the run to finish, and the final one does not."""
    api = FakeRunApi(LAGGING_RUN_STEPS)
    api.register(httpserver)
    run_client = sync_client.run(RUN_ID)
    wait_with_holding = run_client.wait_for_finish

    # The fake API answers at once, so a real wait would re-read the run until the deadline and skip steps.
    def wait_without_holding(**kwargs: Any) -> Run | None:
        return wait_with_holding(**{**kwargs, 'wait_duration': NO_WAIT})

    wait_for_finish = Mock(side_effect=wait_without_holding)
    monkeypatch.setattr(run_client, 'wait_for_finish', wait_for_finish)

    items = list(run_client.iterate_dataset_items(poll_interval=timedelta(seconds=2)))

    assert items == shape_items(range(75))
    assert wait_for_finish.call_args_list == [call(wait_duration=timedelta(seconds=2), timeout='long')] * 3
    assert api.run_requests == [{}] + [{'waitForFinish': '0'}] * 3


async def test_iterate_dataset_items_waits_for_finish_between_polls_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Each poll of an unfinished run waits up to `poll_interval` for the run to finish, and the final one does not."""
    api = FakeRunApi(LAGGING_RUN_STEPS)
    api.register(httpserver)
    run_client = async_client.run(RUN_ID)
    wait_with_holding = run_client.wait_for_finish

    # The fake API answers at once, so a real wait would re-read the run until the deadline and skip steps.
    async def wait_without_holding(**kwargs: Any) -> Run | None:
        return await wait_with_holding(**{**kwargs, 'wait_duration': NO_WAIT})

    wait_for_finish = AsyncMock(side_effect=wait_without_holding)
    monkeypatch.setattr(run_client, 'wait_for_finish', wait_for_finish)

    items = [item async for item in run_client.iterate_dataset_items(poll_interval=timedelta(seconds=2))]

    assert items == shape_items(range(75))
    assert wait_for_finish.call_args_list == [call(wait_duration=timedelta(seconds=2), timeout='long')] * 3
    assert api.run_requests == [{}] + [{'waitForFinish': '0'}] * 3


def test_iterate_dataset_items_pins_the_last_run_sync(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """A `last_run()` client resolves `runs/last` once and reads that run's dataset to the end."""
    api = FakeRunApi(LAGGING_RUN_STEPS)
    api.register(httpserver)

    run_client = sync_client.actor(ACTOR_ID).last_run()
    items = list(run_client.iterate_dataset_items(chunk_size=10, poll_interval=NO_WAIT))

    assert items == shape_items(range(75))
    assert api.last_run_requests == 1


async def test_iterate_dataset_items_pins_the_last_run_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """A `last_run()` client resolves `runs/last` once and reads that run's dataset to the end."""
    api = FakeRunApi(LAGGING_RUN_STEPS)
    api.register(httpserver)

    run_client = async_client.actor(ACTOR_ID).last_run()
    items = [item async for item in run_client.iterate_dataset_items(chunk_size=10, poll_interval=NO_WAIT)]

    assert items == shape_items(range(75))
    assert api.last_run_requests == 1

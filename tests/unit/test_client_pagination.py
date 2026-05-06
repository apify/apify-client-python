from __future__ import annotations

import dataclasses
import json
import re
from typing import TYPE_CHECKING, Any, Literal, TypeAlias

import pytest
from pydantic.fields import FieldInfo
from werkzeug import Response

from apify_client import ApifyClient, ApifyClientAsync
from apify_client import _models as _models_module
from apify_client._resource_clients import (
    ActorCollectionClient,
    ActorCollectionClientAsync,
    ActorEnvVarCollectionClient,
    ActorEnvVarCollectionClientAsync,
    ActorVersionCollectionClient,
    ActorVersionCollectionClientAsync,
    BuildCollectionClient,
    BuildCollectionClientAsync,
    DatasetClient,
    DatasetClientAsync,
    DatasetCollectionClient,
    DatasetCollectionClientAsync,
    KeyValueStoreClient,
    KeyValueStoreClientAsync,
    KeyValueStoreCollectionClient,
    KeyValueStoreCollectionClientAsync,
    RequestQueueClient,
    RequestQueueClientAsync,
    RequestQueueCollectionClient,
    RequestQueueCollectionClientAsync,
    RunCollectionClient,
    RunCollectionClientAsync,
    ScheduleCollectionClient,
    ScheduleCollectionClientAsync,
    StoreCollectionClient,
    StoreCollectionClientAsync,
    TaskCollectionClient,
    TaskCollectionClientAsync,
    WebhookCollectionClient,
    WebhookCollectionClientAsync,
    WebhookDispatchCollectionClient,
    WebhookDispatchCollectionClientAsync,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from _pytest.mark import ParameterSet
    from pydantic import BaseModel
    from pytest_httpserver import HTTPServer
    from werkzeug import Request


CollectionClient: TypeAlias = (
    ActorCollectionClient
    | BuildCollectionClient
    | RunCollectionClient
    | ScheduleCollectionClient
    | TaskCollectionClient
    | WebhookCollectionClient
    | WebhookDispatchCollectionClient
    | DatasetCollectionClient
    | KeyValueStoreCollectionClient
    | RequestQueueCollectionClient
    | StoreCollectionClient
    | ActorEnvVarCollectionClient
    | ActorVersionCollectionClient
)

CollectionClientAsync: TypeAlias = (
    ActorCollectionClientAsync
    | BuildCollectionClientAsync
    | RunCollectionClientAsync
    | ScheduleCollectionClientAsync
    | TaskCollectionClientAsync
    | WebhookCollectionClientAsync
    | WebhookDispatchCollectionClientAsync
    | DatasetCollectionClientAsync
    | KeyValueStoreCollectionClientAsync
    | RequestQueueCollectionClientAsync
    | StoreCollectionClientAsync
    | ActorEnvVarCollectionClientAsync
    | ActorVersionCollectionClientAsync
)

ID_PLACEHOLDER = 'some-id'
NORMAL_ITEMS = 2500
EXTRA_ITEMS_UNNAMED = 100
MAX_ITEMS_PER_PAGE = 1000

# Inner list models whose `items: list[<specific schema>]` is relaxed to `list[dict]`. Point of these tests is
# pagination mechanism, not internal object validation.
_RELAXED_LIST_MODELS = (
    'ListOfActors',
    'ListOfBuilds',
    'ListOfDatasets',
    'ListOfEnvVars',
    'ListOfKeys',
    'ListOfKeyValueStores',
    'ListOfRequestQueues',
    'ListOfRequests',
    'ListOfRuns',
    'ListOfSchedules',
    'ListOfStoreActors',
    'ListOfTasks',
    'ListOfVersions',
    'ListOfWebhookDispatches',
    'ListOfWebhooks',
)

# Outer wrappers that embed a relaxed list model via `.data`. Their compiled schema pins the inner's schema at
# construction time, so they need a forced rebuild to pick up the relaxation. The wrappers themselves are not mutated —
# their own field annotations stay as-is.
_REBUILT_RESPONSE_WRAPPERS = (
    'ListOfActorsInStoreResponse',
    'ListOfActorsResponse',
    'ListOfBuildsResponse',
    'ListOfDatasetsResponse',
    'ListOfEnvVarsResponse',
    'ListOfKeyValueStoresResponse',
    'ListOfKeysResponse',
    'ListOfRequestQueuesResponse',
    'ListOfRequestsResponse',
    'ListOfRunsResponse',
    'ListOfSchedulesResponse',
    'ListOfTasksResponse',
    'ListOfVersionsResponse',
    'ListOfWebhooksResponse',
)


@pytest.fixture(autouse=True)
def _relax_item_validation() -> Any:
    """Relax only the element type of `items` on paginated list models for the test run.

    Pagination tests feed synthetic `{'id': N}` items that don't satisfy the real API schemas (`ActorShort`,
    `BuildShort`, `Request`, `EnvVar`, …). Instead of bypassing validation wholesale, each inner `ListOf*` model has its
    `items` field swapped to `list[dict]` and rebuilt. Outer `.data` wrapping and every pagination-metadata field remain
    validated.
    """
    relaxed_field = FieldInfo.from_annotation(list[dict])
    originals: dict[type[BaseModel], FieldInfo] = {}
    wrappers = [getattr(_models_module, name) for name in _REBUILT_RESPONSE_WRAPPERS]

    for name in _RELAXED_LIST_MODELS:
        cls = getattr(_models_module, name)
        originals[cls] = cls.model_fields['items']
        cls.model_fields['items'] = relaxed_field
        cls.model_rebuild(force=True)
    for wrapper in wrappers:
        wrapper.model_rebuild(force=True)
    try:
        yield
    finally:
        for cls, field in originals.items():
            cls.model_fields['items'] = field
            cls.model_rebuild(force=True)
        for wrapper in wrappers:
            wrapper.model_rebuild(force=True)


def create_items(start: int, end: int, step: int | None = None) -> list[dict[str, int]]:
    """Create a list of test items for the given index range."""
    if not step:
        step = -1 if end < start else 1
    return [{'id': i} for i in range(start, end, step)]


def _is_true(value: str | None) -> bool:
    """Match the `'true'` wire form produced by the client's bool→string serialization."""
    return value == 'true'


def _parse_int_param(value: str | None) -> int:
    return int(value) if value not in (None, '') else 0


def _handle_offset_pagination(request: Request) -> Response:
    """Serve an offset-paginated Apify API response.

    The simulated platform holds 2500 items normally and an additional 100 when `unnamed=true` is requested. Pages are
    capped at 1000 items regardless of the requested limit, mirroring the real API. The dataset items endpoint returns
    items as a raw list; all other endpoints wrap them in `{'data': {...}}`.
    """
    params = request.args

    total_items = (NORMAL_ITEMS + EXTRA_ITEMS_UNNAMED) if _is_true(params.get('unnamed')) else NORMAL_ITEMS
    offset = _parse_int_param(params.get('offset'))
    limit = _parse_int_param(params.get('limit'))
    assert offset >= 0, 'Invalid offset sent to API'
    assert limit >= 0, 'Invalid limit sent to API'

    desc = _is_true(params.get('desc'))
    items = create_items(total_items, 0) if desc else create_items(0, total_items)

    lower_index = min(offset, total_items)
    upper_index = min(offset + (limit or total_items), total_items)
    count = min(max(upper_index - lower_index, 0), MAX_ITEMS_PER_PAGE)
    selected_items = items[lower_index : min(upper_index, lower_index + MAX_ITEMS_PER_PAGE)]

    # Every second item is filtered out when `skipEmpty=true`, `skipHidden=true`, or `clean=true`.
    if _is_true(params.get('skipEmpty')) or _is_true(params.get('skipHidden')) or _is_true(params.get('clean')):
        selected_items = selected_items[::2]

    headers = {
        'x-apify-pagination-count': str(count),
        'x-apify-pagination-total': str(total_items),
        'x-apify-pagination-offset': str(offset),
        'x-apify-pagination-limit': str(limit or count or 1),
        'x-apify-pagination-desc': str(desc).lower(),
        'content-type': 'application/json',
    }

    if request.path.endswith(f'/datasets/{ID_PLACEHOLDER}/items'):
        body: Any = selected_items
    else:
        body = {
            'data': {
                'total': total_items,
                'count': count,
                'offset': offset,
                'limit': limit or (count or 1),
                'desc': desc,
                'items': selected_items,
            }
        }
    return Response(status=200, headers=headers, response=json.dumps(body))


def _handle_cursor_pagination(request: Request) -> Response:
    """Serve a cursor-paginated Apify API response for KVS keys and RQ requests.

    Holds 2500 synthetic items whose integer `id` equals their position. Each page is capped at 1000 items. KVS uses
    `exclusiveStartKey`; RQ accepts either the deprecated `exclusiveStartId` on the initial call or the opaque `cursor`
    on subsequent calls. All three values encode the last-seen item id as a string — the next page starts at id + 1.
    """
    params = request.args
    limit = _parse_int_param(params.get('limit'))
    assert limit >= 0, 'Invalid limit sent to API'

    cursor_raw = params.get('exclusiveStartKey') or params.get('exclusiveStartId') or params.get('cursor')

    total_items = NORMAL_ITEMS
    start = int(cursor_raw) + 1 if cursor_raw not in (None, '') else 0
    end = total_items if not limit else min(start + limit, total_items)
    page_end = min(end, start + MAX_ITEMS_PER_PAGE)
    selected_items = [{'id': i} for i in range(start, page_end)]

    if request.path.endswith('/keys'):
        is_truncated = page_end < total_items and bool(selected_items)
        next_exclusive_start_key = str(selected_items[-1]['id']) if selected_items and is_truncated else None
        body: dict[str, Any] = {
            'data': {
                'items': selected_items,
                'count': len(selected_items),
                'limit': limit or (len(selected_items) or 1),
                'is_truncated': is_truncated,
                'next_exclusive_start_key': next_exclusive_start_key,
            }
        }
    else:  # `/requests`
        has_more = page_end < total_items and bool(selected_items)
        next_cursor = str(selected_items[-1]['id']) if has_more else None
        body = {
            'data': {
                'items': selected_items,
                'count': len(selected_items),
                'limit': limit or (len(selected_items) or 1),
                'next_cursor': next_cursor,
            }
        }
    return Response(status=200, headers={'content-type': 'application/json'}, response=json.dumps(body))


def _pagination_handler(request: Request) -> Response:
    """Dispatch between cursor-based (KVS keys, RQ requests) and offset-based endpoints."""
    if request.path.endswith(('/keys', '/requests')):
        return _handle_cursor_pagination(request)
    return _handle_offset_pagination(request)


@pytest.fixture
def pagination_server(httpserver: HTTPServer) -> HTTPServer:
    """Register a catch-all handler that mirrors the Apify paginated endpoints."""
    httpserver.expect_request(re.compile(r'.*')).respond_with_handler(_pagination_handler)
    return httpserver


def _make_sync_client(httpserver: HTTPServer) -> ApifyClient:
    return ApifyClient(token='test', api_url=httpserver.url_for('/'))


def _make_async_client(httpserver: HTTPServer) -> ApifyClientAsync:
    return ApifyClientAsync(token='test', api_url=httpserver.url_for('/'))


# Map resource-client class name to a factory that, given an `ApifyClient`/`ApifyClientAsync`, returns the sub-client
# under test. Usable for both sync and async since every accessor is available symmetrically on both root clients.
_CLIENT_FACTORIES: dict[str, Callable[[Any], Any]] = {
    'ActorCollectionClient': lambda c: c.actors(),
    'ScheduleCollectionClient': lambda c: c.schedules(),
    'TaskCollectionClient': lambda c: c.tasks(),
    'WebhookCollectionClient': lambda c: c.webhooks(),
    'WebhookDispatchCollectionClient': lambda c: c.webhook_dispatches(),
    'StoreCollectionClient': lambda c: c.store(),
    'DatasetCollectionClient': lambda c: c.datasets(),
    'KeyValueStoreCollectionClient': lambda c: c.key_value_stores(),
    'RequestQueueCollectionClient': lambda c: c.request_queues(),
    'BuildCollectionClient': lambda c: c.actor(ID_PLACEHOLDER).builds(),
    'RunCollectionClient': lambda c: c.actor(ID_PLACEHOLDER).runs(),
    'ActorVersionCollectionClient': lambda c: c.actor(ID_PLACEHOLDER).versions(),
    'ActorEnvVarCollectionClient': lambda c: c.actor(ID_PLACEHOLDER).version('some-version').env_vars(),
    'DatasetClient': lambda c: c.dataset(ID_PLACEHOLDER),
    'KeyValueStoreClient': lambda c: c.key_value_store(ID_PLACEHOLDER),
    'RequestQueueClient': lambda c: c.request_queue(ID_PLACEHOLDER),
}


_CLIENT_SET_NAMES: dict[Literal['collection', 'dataset', 'kvs', 'rq'], tuple[str, ...]] = {
    # Tuple rather than set: pytest-xdist requires a stable iteration order across workers.
    # https://pytest-xdist.readthedocs.io/en/stable/known-limitations.html#order-and-amount-of-test-must-be-consistent
    'collection': (
        'ActorCollectionClient',
        'ScheduleCollectionClient',
        'TaskCollectionClient',
        'WebhookCollectionClient',
        'WebhookDispatchCollectionClient',
        'StoreCollectionClient',
        'DatasetCollectionClient',
        'KeyValueStoreCollectionClient',
        'RequestQueueCollectionClient',
        'BuildCollectionClient',
        'RunCollectionClient',
        'ActorVersionCollectionClient',
        'ActorEnvVarCollectionClient',
    ),
    'dataset': ('DatasetClient',),
    'kvs': ('KeyValueStoreClient',),
    'rq': ('RequestQueueClient',),
}


@dataclasses.dataclass
class _PaginationCase:
    """A single parametrized pagination test case."""

    id: str
    inputs: dict
    expected_items: list[dict[str, int]]
    supported_clients: set[str]

    def __hash__(self) -> int:
        return hash(self.id)


COLLECTION_CLIENTS = {
    'ActorCollectionClient',
    'BuildCollectionClient',
    'RunCollectionClient',
    'ScheduleCollectionClient',
    'TaskCollectionClient',
    'WebhookCollectionClient',
    'WebhookDispatchCollectionClient',
    'DatasetCollectionClient',
    'KeyValueStoreCollectionClient',
    'RequestQueueCollectionClient',
    'StoreCollectionClient',
}

NO_OPTIONS_CLIENTS = {
    'ActorEnvVarCollectionClient',
    'ActorVersionCollectionClient',
}

DATASET_CLIENTS = {'DatasetClient'}
RQ_CLIENTS = {'RequestQueueClient'}
KVS_CLIENTS = {'KeyValueStoreClient'}
STORAGE_CLIENTS = DATASET_CLIENTS | RQ_CLIENTS | KVS_CLIENTS
OPTIONS_CLIENTS = COLLECTION_CLIENTS | STORAGE_CLIENTS

TEST_CASES = (
    _PaginationCase('No options normal', {}, create_items(0, 2500), OPTIONS_CLIENTS),
    # These clients can't iterate over all items if there is more of them than the API limit as they offer no pagination
    # parameters.
    _PaginationCase('No options limited', {}, create_items(0, 1000), NO_OPTIONS_CLIENTS),
    _PaginationCase('Limit', {'limit': 1100}, create_items(0, 1100), OPTIONS_CLIENTS),
    _PaginationCase('Out of range limit', {'limit': 3000}, create_items(0, 2500), OPTIONS_CLIENTS),
    _PaginationCase(
        'Offset',
        {'offset': 1000},
        create_items(1000, 2500),
        OPTIONS_CLIENTS - KVS_CLIENTS - RQ_CLIENTS,
    ),
    _PaginationCase(
        'Offset and limit',
        {'offset': 1000, 'limit': 1100},
        create_items(1000, 2100),
        OPTIONS_CLIENTS - KVS_CLIENTS - RQ_CLIENTS,
    ),
    _PaginationCase('Out of range offset', {'offset': 3000}, [], OPTIONS_CLIENTS - KVS_CLIENTS - RQ_CLIENTS),
    _PaginationCase(
        'Offset, limit, descending',
        {'offset': 1000, 'limit': 1100, 'desc': True},
        create_items(1500, 400),
        OPTIONS_CLIENTS - {'StoreCollectionClient'} - KVS_CLIENTS - RQ_CLIENTS,
    ),
    _PaginationCase(
        'Offset, limit, descending, unnamed',
        {'offset': 50, 'limit': 1100, 'desc': True, 'unnamed': True},
        create_items(2550, 1450),
        {'DatasetCollectionClient', 'KeyValueStoreCollectionClient', 'RequestQueueCollectionClient'},
    ),
    _PaginationCase(
        'chunk_size',
        {'chunk_size': 100, 'limit': 250},
        create_items(0, 250),
        STORAGE_CLIENTS,
    ),
    _PaginationCase(
        'Offset, limit, descending, chunk_size',
        {'offset': 50, 'limit': 1100, 'desc': True, 'chunk_size': 100},
        create_items(2450, 1350),
        DATASET_CLIENTS,
    ),
    _PaginationCase(
        'Offset, limit, descending, chunk_size, clean',
        {'limit': 1500, 'chunk_size': 100, 'clean': True},
        # API behavior with `clean=True` is to apply the cleaning after pagination, so we end up with missing items
        # being counted towards the limit and thus fewer total items returned.
        create_items(0, 1500, 2),
        DATASET_CLIENTS,
    ),
    _PaginationCase(
        'Exclusive start key',
        {'exclusive_start_key': '1000'},
        create_items(1001, 2500),
        KVS_CLIENTS,
    ),
    _PaginationCase(
        'Exclusive start key and limit',
        {'exclusive_start_key': '1000', 'limit': 500},
        create_items(1001, 1501),
        KVS_CLIENTS,
    ),
    _PaginationCase(
        'Cursor',
        {'cursor': '1000'},
        create_items(1001, 2500),
        RQ_CLIENTS,
    ),
    _PaginationCase(
        'Cursor and limit',
        {'cursor': '1000', 'limit': 500},
        create_items(1001, 1501),
        RQ_CLIENTS,
    ),
)


def _generate_test_params(client_set: Literal['collection', 'dataset', 'kvs', 'rq']) -> list[ParameterSet]:
    """Build the pytest parameter set for the given client category.

    Each parameter carries the resource-client class name; the test body instantiates the real client against the
    `httpserver` URL and looks up the factory in `_CLIENT_FACTORIES`.
    """
    client_names = _CLIENT_SET_NAMES[client_set]
    return [
        pytest.param(test_case.inputs, test_case.expected_items, client_name, id=f'{client_name}:{test_case.id}')
        for test_case in TEST_CASES
        for client_name in client_names
        if client_name in test_case.supported_clients
    ]


@pytest.mark.parametrize(
    ('inputs', 'expected_items', 'client_name'),
    _generate_test_params(client_set='collection'),
)
def test_client_list_iterable(
    pagination_server: HTTPServer,
    client_name: str,
    inputs: dict,
    expected_items: list[dict[str, int]],
) -> None:
    """Every sync collection client's `list()` return value should iterate across pages."""
    client: CollectionClient = _CLIENT_FACTORIES[client_name](_make_sync_client(pagination_server))
    returned_items = list(client.iterate(**inputs))
    assert len(returned_items) == len(expected_items)
    assert returned_items == expected_items


@pytest.mark.parametrize(
    ('inputs', 'expected_items', 'client_name'),
    _generate_test_params(client_set='collection'),
)
async def test_client_list_iterable_async(
    pagination_server: HTTPServer,
    client_name: str,
    inputs: dict,
    expected_items: list[dict[str, int]],
) -> None:
    """Every async collection client's `list()` return value should iterate across pages."""
    client: CollectionClientAsync = _CLIENT_FACTORIES[client_name](_make_async_client(pagination_server))
    returned_items = [item async for item in client.iterate(**inputs)]
    assert len(returned_items) == len(expected_items)
    assert returned_items == expected_items


@pytest.mark.parametrize(
    ('inputs', 'expected_items', 'client_name'),
    _generate_test_params(client_set='dataset'),
)
def test_dataset_items_list_iterable(
    pagination_server: HTTPServer,
    client_name: str,
    inputs: dict,
    expected_items: list[dict[str, int]],
) -> None:
    """The sync dataset client's `iterate_items()` should iterate across pages."""
    client: DatasetClient = _CLIENT_FACTORIES[client_name](_make_sync_client(pagination_server))
    returned_items = list(client.iterate_items(**inputs))

    if inputs == {}:
        list_response = client.list_items(**inputs)
        assert len(returned_items) == list_response.total

    assert len(returned_items) == len(expected_items)
    assert returned_items == expected_items


@pytest.mark.parametrize(
    ('inputs', 'expected_items', 'client_name'),
    _generate_test_params(client_set='dataset'),
)
async def test_dataset_items_list_iterable_async(
    pagination_server: HTTPServer,
    client_name: str,
    inputs: dict,
    expected_items: list[dict[str, int]],
) -> None:
    """The async dataset client's `iterate_items()` should iterate across pages."""
    client: DatasetClientAsync = _CLIENT_FACTORIES[client_name](_make_async_client(pagination_server))
    returned_items = [item async for item in client.iterate_items(**inputs)]

    if inputs == {}:
        list_response = await client.list_items(**inputs)
        assert len(returned_items) == list_response.total

    assert returned_items == expected_items


@pytest.mark.parametrize(
    ('inputs', 'expected_items', 'client_name'),
    _generate_test_params(client_set='kvs'),
)
def test_kvs_list_keys_iterable(
    pagination_server: HTTPServer,
    client_name: str,
    inputs: dict,
    expected_items: list[dict[str, int]],
) -> None:
    """The sync KVS client's `iterate_keys()` should iterate across cursor-paginated pages."""
    client: KeyValueStoreClient = _CLIENT_FACTORIES[client_name](_make_sync_client(pagination_server))
    returned_items = [dict(item) for item in client.iterate_keys(**inputs)]

    assert returned_items == expected_items


@pytest.mark.parametrize(
    ('inputs', 'expected_items', 'client_name'),
    _generate_test_params(client_set='kvs'),
)
async def test_kvs_list_keys_iterable_async(
    pagination_server: HTTPServer,
    client_name: str,
    inputs: dict,
    expected_items: list[dict[str, int]],
) -> None:
    """The async KVS client's `iterate_keys()` should iterate across cursor-paginated pages."""
    client: KeyValueStoreClientAsync = _CLIENT_FACTORIES[client_name](_make_async_client(pagination_server))
    returned_items = [dict(item) async for item in client.iterate_keys(**inputs)]

    assert returned_items == expected_items


@pytest.mark.parametrize(
    ('inputs', 'expected_items', 'client_name'),
    _generate_test_params(client_set='rq'),
)
def test_rq_list_requests_iterable(
    pagination_server: HTTPServer,
    client_name: str,
    inputs: dict,
    expected_items: list[dict[str, int]],
) -> None:
    """The sync RQ client's `iterate_requests()` should iterate across cursor-paginated pages."""
    client: RequestQueueClient = _CLIENT_FACTORIES[client_name](_make_sync_client(pagination_server))
    returned_items = [dict(item) for item in client.iterate_requests(**inputs)]
    assert returned_items == expected_items


@pytest.mark.parametrize(
    ('inputs', 'expected_items', 'client_name'),
    _generate_test_params(client_set='rq'),
)
async def test_rq_list_requests_iterable_async(
    pagination_server: HTTPServer,
    client_name: str,
    inputs: dict,
    expected_items: list[dict[str, int]],
) -> None:
    """The async RQ client's `iterate_requests()` should iterate across cursor-paginated pages."""
    client: RequestQueueClientAsync = _CLIENT_FACTORIES[client_name](_make_async_client(pagination_server))
    returned_items = [dict(item) async for item in client.iterate_requests(**inputs)]
    assert returned_items == expected_items


def test_rq_list_requests_rejects_cursor_and_exclusive_start_id() -> None:
    """Passing both `cursor` and `exclusive_start_id` is mutually exclusive and must error."""
    client = ApifyClient(token='').request_queue(ID_PLACEHOLDER)
    with pytest.raises(ValueError, match='Cannot use both'):
        client.list_requests(cursor='a', exclusive_start_id='b')


async def test_rq_list_requests_rejects_cursor_and_exclusive_start_id_async() -> None:
    """Async variant of the mutual-exclusion check."""
    client = ApifyClientAsync(token='').request_queue(ID_PLACEHOLDER)
    with pytest.raises(ValueError, match='Cannot use both'):
        await client.list_requests(cursor='a', exclusive_start_id='b')

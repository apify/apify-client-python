from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Any, Literal, TypeAlias
from unittest import mock
from unittest.mock import Mock

import pytest

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
    KeyValueStoreCollectionClient,
    KeyValueStoreCollectionClientAsync,
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
    from _pytest.mark import ParameterSet

    from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync


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

# Response wrappers whose `model_validate` should be bypassed during pagination tests so
# synthetic `{'id': N, 'key': N}` test items are accepted without matching the real API schemas.
_BYPASSED_RESPONSE_CLASSES = (
    'ListOfActorsResponse',
    'ListOfBuildsResponse',
    'ListOfRunsResponse',
    'ListOfSchedulesResponse',
    'ListOfTasksResponse',
    'ListOfWebhooksResponse',
    'WebhookDispatchList',
    'ListOfDatasetsResponse',
    'ListOfKeyValueStoresResponse',
    'ListOfRequestQueuesResponse',
    'ListOfActorsInStoreResponse',
    'ListOfEnvVarsResponse',
    'ListOfVersionsResponse',
)


@dataclasses.dataclass
class _FakeListModel:
    """Stand-in for a paginated list model that mimics the fields the iteration logic accesses."""

    items: list[dict[str, int]]
    total: int = 0
    count: int = 0
    offset: int = 0
    limit: int = 0
    desc: bool = False


@dataclasses.dataclass
class _FakeResponseWrapper:
    """Stand-in for a `*Response` Pydantic model that wraps a paginated list under `.data`."""

    data: _FakeListModel


@pytest.fixture(autouse=True)
def _bypass_response_validation() -> Any:
    """Replace the Pydantic `model_validate` of response wrappers with a lightweight builder.

    Pagination tests use synthetic items that don't satisfy the real API schemas. Bypassing
    validation lets the iteration logic run while still building a model-like object that exposes
    the fields the client code consumes (`.data`, `.items`, `.total`, etc.).
    """

    def _build(_cls: type, obj: dict) -> _FakeResponseWrapper:
        data_dict = obj.get('data') or {}
        items = data_dict.get('items', [])
        return _FakeResponseWrapper(
            data=_FakeListModel(
                items=items,
                total=data_dict.get('total', len(items)),
                count=data_dict.get('count', len(items)),
                offset=data_dict.get('offset', 0),
                limit=data_dict.get('limit', 0),
                desc=data_dict.get('desc', False),
            )
        )

    patchers = []
    for class_name in _BYPASSED_RESPONSE_CLASSES:
        cls = getattr(_models_module, class_name)
        patchers.append(mock.patch.object(cls, 'model_validate', classmethod(_build)))

    for p in patchers:
        p.start()
    try:
        yield
    finally:
        for p in patchers:
            p.stop()


def create_items(start: int, end: int) -> list[dict[str, int]]:
    """Create a list of test items for the given index range."""
    step = -1 if end < start else 1
    return [{'id': i, 'key': i} for i in range(start, end, step)]


def _mocked_api_pagination_logic(*, url: str, params: dict[str, Any] | None = None, **_: Any) -> Mock:
    """Simulate a paginated Apify API response.

    The mocked platform holds 2500 items normally and an additional 100 when ``unnamed=True`` is
    requested. Items are simple objects with an incrementing ``id`` and ``key`` that make it easy
    to verify iteration order.

    Pages are capped at 1000 items regardless of the requested limit, mirroring the real API.
    """
    params = params or {}

    normal_items = 2500
    extra_items = 100  # for example unnamed resources
    max_items_per_page = 1000

    total_items = (normal_items + extra_items) if params.get('unnamed') else normal_items

    offset_raw = params.get('offset')
    offset = int(offset_raw) if offset_raw not in (None, '') else 0
    limit_raw = params.get('limit')
    limit = int(limit_raw) if limit_raw not in (None, '') else 0
    assert offset >= 0, 'Invalid offset sent to API'
    assert limit >= 0, 'Invalid limit sent to API'

    desc = params.get('desc') in (True, 'true', 'True', 1, '1')
    items = create_items(total_items, 0) if desc else create_items(0, total_items)

    lower_index = min(offset, total_items)
    upper_index = min(offset + (limit or total_items), total_items)
    count = min(max(upper_index - lower_index, 0), max_items_per_page)

    selected_items = items[lower_index : min(upper_index, lower_index + max_items_per_page)]

    response = Mock()

    # The dataset items endpoint returns items as a raw list
    if url.endswith(f'/datasets/{ID_PLACEHOLDER}/items'):
        response.content = b''
        response.json = lambda: selected_items
    else:
        response.content = b''
        response.json = lambda: {
            'data': {
                'total': total_items,
                'count': count,
                'offset': offset,
                'limit': limit or (count or 1),
                'desc': desc,
                'items': selected_items,
            }
        }

    response.headers = {
        'x-apify-pagination-total': str(total_items),
        'x-apify-pagination-offset': str(offset),
        'x-apify-pagination-limit': str(limit or count or 1),
        'x-apify-pagination-desc': str(desc).lower(),
    }
    return response


@dataclasses.dataclass
class _PaginationCase:
    """A single parametrized pagination test case."""

    id: str
    inputs: dict
    expected_items: list[dict[str, int]]
    supported_clients: set[str]

    def __hash__(self) -> int:
        return hash(self.id)

    def supports(self, client: ResourceClient | ResourceClientAsync) -> bool:
        """Check whether the given client implements functionality tested by this test case."""
        return client.__class__.__name__.removesuffix('Async') in self.supported_clients


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

ALL_CLIENTS = COLLECTION_CLIENTS | NO_OPTIONS_CLIENTS | DATASET_CLIENTS

TEST_CASES = (
    _PaginationCase('No options', {}, create_items(0, 2500), ALL_CLIENTS),
    _PaginationCase('Limit', {'limit': 1100}, create_items(0, 1100), ALL_CLIENTS - NO_OPTIONS_CLIENTS),
    _PaginationCase('Out of range limit', {'limit': 3000}, create_items(0, 2500), ALL_CLIENTS - NO_OPTIONS_CLIENTS),
    _PaginationCase('Offset', {'offset': 1000}, create_items(1000, 2500), ALL_CLIENTS - NO_OPTIONS_CLIENTS),
    _PaginationCase(
        'Offset and limit',
        {'offset': 1000, 'limit': 1100},
        create_items(1000, 2100),
        ALL_CLIENTS - NO_OPTIONS_CLIENTS,
    ),
    _PaginationCase('Out of range offset', {'offset': 3000}, [], ALL_CLIENTS - NO_OPTIONS_CLIENTS),
    _PaginationCase(
        'Offset, limit, descending',
        {'offset': 1000, 'limit': 1100, 'desc': True},
        create_items(1500, 400),
        ALL_CLIENTS - NO_OPTIONS_CLIENTS - {'StoreCollectionClient'},
    ),
    _PaginationCase(
        'Offset, limit, descending, unnamed',
        {'offset': 50, 'limit': 1100, 'desc': True, 'unnamed': True},
        create_items(2550, 1450),
        {'DatasetCollectionClient', 'KeyValueStoreCollectionClient', 'RequestQueueCollectionClient'},
    ),
    _PaginationCase(
        'Offset, limit, descending, chunk_size',
        {'offset': 50, 'limit': 1100, 'desc': True, 'chunk_size': 100},
        create_items(2450, 1350),
        DATASET_CLIENTS,
    ),
)


def _generate_test_params(client_set: Literal['collection', 'dataset'], *, async_clients: bool) -> list[ParameterSet]:
    """Build the pytest parameter set for the given client category."""
    client = ApifyClientAsync(token='') if async_clients else ApifyClient(token='')

    # Tuple rather than set because pytest-xdist requires a stable iteration order.
    # https://pytest-xdist.readthedocs.io/en/stable/known-limitations.html#order-and-amount-of-test-must-be-consistent
    clients: tuple[ResourceClient | ResourceClientAsync, ...]

    match client_set:
        case 'collection':
            clients = (
                client.actors(),
                client.schedules(),
                client.tasks(),
                client.webhooks(),
                client.webhook_dispatches(),
                client.store(),
                client.datasets(),
                client.key_value_stores(),
                client.request_queues(),
                client.actor(ID_PLACEHOLDER).builds(),
                client.actor(ID_PLACEHOLDER).runs(),
                client.actor(ID_PLACEHOLDER).versions(),
                client.actor(ID_PLACEHOLDER).version('some-version').env_vars(),
            )
        case 'dataset':
            clients = (client.dataset(ID_PLACEHOLDER),)
        case _:
            raise ValueError(f'Unknown client set: {client_set}')

    return [
        pytest.param(
            test_case.inputs, test_case.expected_items, sub_client, id=f'{sub_client.__class__.__name__}:{test_case.id}'
        )
        for test_case in TEST_CASES
        for sub_client in clients
        if test_case.supports(sub_client)
    ]


@pytest.mark.parametrize(
    ('inputs', 'expected_items', 'client'),
    _generate_test_params(client_set='collection', async_clients=False),
)
def test_client_list_iterable(
    client: CollectionClient,
    inputs: dict,
    expected_items: list[dict[str, int]],
) -> None:
    """Every sync collection client's `list()` return value should iterate across pages."""
    with mock.patch.object(client._http_client, 'call', side_effect=_mocked_api_pagination_logic):
        returned_items = list(client.list(**inputs))

        if inputs == {}:
            list_response = client.list(**inputs)
            assert len(returned_items) == list_response.total

        assert returned_items == expected_items


@pytest.mark.parametrize(
    ('inputs', 'expected_items', 'client'),
    _generate_test_params(client_set='collection', async_clients=True),
)
async def test_client_list_iterable_async(
    client: CollectionClientAsync,
    inputs: dict,
    expected_items: list[dict[str, int]],
) -> None:
    """Every async collection client's `list()` return value should iterate across pages."""

    async def async_side_effect(**kwargs: Any) -> Mock:
        return _mocked_api_pagination_logic(**kwargs)

    with mock.patch.object(client._http_client, 'call', side_effect=async_side_effect):
        returned_items = [item async for item in client.list(**inputs)]

        if inputs == {}:
            list_response = await client.list(**inputs)
            assert len(returned_items) == list_response.total

        assert returned_items == expected_items


@pytest.mark.parametrize(
    ('inputs', 'expected_items', 'client'),
    _generate_test_params(client_set='dataset', async_clients=False),
)
def test_dataset_items_list_iterable(
    client: DatasetClient,
    inputs: dict,
    expected_items: list[dict[str, int]],
) -> None:
    """The sync dataset client's `list_items()` return value should iterate across pages."""
    with mock.patch.object(client._http_client, 'call', side_effect=_mocked_api_pagination_logic):
        returned_items = list(client.list_items(**inputs))

        if inputs == {}:
            list_response = client.list_items(**inputs)
            assert len(returned_items) == list_response.total

        assert returned_items == expected_items

        # Until the deprecated `iterate_items` method is removed, it should behave the same
        inputs_without_chunk_size = {k: v for k, v in inputs.items() if k != 'chunk_size'}
        with pytest.warns(DeprecationWarning, match='iterate_items.*is deprecated'):
            assert returned_items == list(client.iterate_items(**inputs_without_chunk_size))


@pytest.mark.parametrize(
    ('inputs', 'expected_items', 'client'),
    _generate_test_params(client_set='dataset', async_clients=True),
)
async def test_dataset_items_list_iterable_async(
    client: DatasetClientAsync,
    inputs: dict,
    expected_items: list[dict[str, int]],
) -> None:
    """The async dataset client's `list_items()` return value should iterate across pages."""

    async def async_side_effect(**kwargs: Any) -> Mock:
        return _mocked_api_pagination_logic(**kwargs)

    with mock.patch.object(client._http_client, 'call', side_effect=async_side_effect):
        returned_items = [item async for item in client.list_items(**inputs)]

        if inputs == {}:
            list_response = await client.list_items(**inputs)
            assert len(returned_items) == list_response.total

        assert returned_items == expected_items

        # Until the deprecated `iterate_items` method is removed, it should behave the same
        inputs_without_chunk_size = {k: v for k, v in inputs.items() if k != 'chunk_size'}
        with pytest.warns(DeprecationWarning, match='iterate_items.*is deprecated'):
            assert returned_items == [item async for item in client.iterate_items(**inputs_without_chunk_size)]

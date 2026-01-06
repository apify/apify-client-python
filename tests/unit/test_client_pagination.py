import dataclasses
from typing import Any, Literal, TypeAlias
from unittest import mock
from unittest.mock import Mock

import pytest
from _pytest.mark import ParameterSet

from apify_client import ApifyClient, ApifyClientAsync
from apify_client.clients import (
    ActorCollectionClient,
    ActorCollectionClientAsync,
    BaseClient,
    BaseClientAsync,
    BuildCollectionClient,
    BuildCollectionClientAsync,
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
from apify_client.clients.resource_clients import DatasetClientAsync

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
)

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
)


def create_items(start: int, end: int) -> list[dict[str, int]]:
    """Create list of test items of specified range."""
    step = -1 if end < start else 1
    return [{'id': i, 'key': i} for i in range(start, end, step)]


def mocked_api_pagination_logic(*_: Any, **kwargs: Any) -> dict:
    """This function is a placeholder representing the mocked API pagination logic.

    It simulates paginated responses from an API only to a limited extend to test iteration logic in client.
    Returned items are only placeholders that enable keeping track of their index on platform.

    There are 2500 normal items in the collection and additional 100 extra items.
    Items are simple objects with incrementing attributes for easy verification.
    """
    params = kwargs.get('params', {})
    normal_items = 2500
    extra_items = 100  # additional items, for example unnamed
    max_items_per_page = 1000

    total_items = (normal_items + extra_items) if params.get('unnamed') else normal_items
    offset = params.get('offset') or 0
    limit = params.get('limit') or 0
    assert offset >= 0, 'Invalid offset send to API'
    assert limit >= 0, 'Invalid limit send to API'

    # Ordered all items in the mocked platform.
    items = create_items(total_items, 0) if params.get('desc', False) else create_items(0, total_items)
    lower_index = min(offset, total_items)
    upper_index = min(offset + (limit or total_items), total_items)
    count = min(upper_index - lower_index, max_items_per_page)

    response = Mock()
    response.json = lambda: {
        'data': {
            'total': total_items,
            'count': count,
            'offset': offset,
            'limit': limit or count,
            'desc': params.get('desc', False),
            'items': items[lower_index : min(upper_index, lower_index + max_items_per_page)],
        }
    }
    response.headers = {
        'x-apify-pagination-total': str(total_items),
        'x-apify-pagination-offset': str(offset),
        'x-apify-pagination-limit': str(limit or count),
        'x-apify-pagination-desc': str(params.get('desc', False)).lower(),
    }
    return response


@dataclasses.dataclass
class TestCase:
    """Class representing a single test case for pagination tests."""

    id: str
    inputs: dict
    expected_items: list[dict[str, int]]
    supported_clients: set[str]

    def __hash__(self) -> int:
        return hash(self.id)

    def supports(self, client: BaseClient | BaseClientAsync) -> bool:
        """Check whether the given client implements functionality tested by this test."""
        return client.__class__.__name__.replace('Async', '') in self.supported_clients


# Prepare supported testcases for different clients
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

STORAGE_CLIENTS = {
    'DatasetClient',
    'KeyValueStoreClient',
    'RequestQueueClient',
}

ALL_CLIENTS = COLLECTION_CLIENTS | NO_OPTIONS_CLIENTS | STORAGE_CLIENTS

TEST_CASES = (
    TestCase('No options', {}, create_items(0, 2500), ALL_CLIENTS),
    TestCase('Limit', {'limit': 1100}, create_items(0, 1100), ALL_CLIENTS - NO_OPTIONS_CLIENTS),
    TestCase('Out of range limit', {'limit': 3000}, create_items(0, 2500), ALL_CLIENTS - NO_OPTIONS_CLIENTS),
    TestCase('Offset', {'offset': 1000}, create_items(1000, 2500), ALL_CLIENTS - NO_OPTIONS_CLIENTS),
    TestCase(
        'Offset and limit', {'offset': 1000, 'limit': 1100}, create_items(1000, 2100), ALL_CLIENTS - NO_OPTIONS_CLIENTS
    ),
    TestCase('Out of range offset', {'offset': 3000}, [], ALL_CLIENTS - NO_OPTIONS_CLIENTS),
    TestCase(
        'Offset, limit, descending',
        {'offset': 1000, 'limit': 1100, 'desc': True},
        create_items(1500, 400),
        ALL_CLIENTS - NO_OPTIONS_CLIENTS - {'StoreCollectionClient'},
    ),
    TestCase(
        'Offset, limit, descending, unnamed',
        {'offset': 50, 'limit': 1100, 'desc': True, 'unnamed': True},
        create_items(2550, 1450),
        {'DatasetCollectionClient', 'KeyValueStoreCollectionClient', 'RequestQueueCollectionClient'},
    ),
    TestCase(
        'Offset, limit, descending, chunkSize',
        {'offset': 50, 'limit': 1100, 'desc': True, 'chunk_size': 100},
        create_items(1500, 400),
        {'DatasetClient'},
    ),
    TestCase('Exclusive start key', {'exclusive_start_key': 1000}, create_items(1001, 2500), {'KeyValueStoreClient'}),
    TestCase('Exclusive start id', {'exclusive_start_id': 1000}, create_items(1001, 2500), {'RequestQueueClient'}),
)


def generate_test_params(
    client_set: Literal['collection', 'kvs', 'rq', 'dataset'], *, async_clients: bool = False
) -> list[ParameterSet]:
    """Generate list of ParameterSets for parametrized tests.

    Different clients support different options and thus different scenarios.
    """

    client = ApifyClientAsync(token='') if async_clients else ApifyClient(token='')

    # This is tuple instead of set because pytest-xdist
    # https://pytest-xdist.readthedocs.io/en/stable/known-limitations.html#order-and-amount-of-test-must-be-consistent
    clients: tuple[BaseClient | BaseClientAsync, ...]

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
                client.actor('some-id').builds(),
                client.actor('some-id').runs(),
                client.actor('some-id').versions(),
                client.actor('some-id').version('some-version').env_vars(),
            )
        case 'kvs':
            clients = (client.key_value_store('some-id'),)
        case 'rq':
            clients = (client.request_queue('some-id'),)
        case 'dataset':
            clients = (client.dataset('some-id'),)
        case _:
            raise ValueError(f'Unknown client set: {client_set}')

    return [
        pytest.param(
            test_case.inputs, test_case.expected_items, client, id=f'{client.__class__.__name__}:{test_case.id}'
        )
        for test_case in TEST_CASES
        for client in clients
        if test_case.supports(client)
    ]


@pytest.mark.parametrize(
    ('inputs', 'expected_items', 'client'), generate_test_params(client_set='collection', async_clients=True)
)
async def test_client_list_iterable_async(
    client: CollectionClientAsync, inputs: dict, expected_items: list[dict[str, int]]
) -> None:
    with mock.patch.object(client.http_client, 'call', side_effect=mocked_api_pagination_logic):
        returned_items = [item async for item in client.list(**inputs)]

        if inputs == {}:
            list_response = await client.list(**inputs)
            assert len(returned_items) == list_response.total

        assert returned_items == expected_items


@pytest.mark.parametrize(
    ('inputs', 'expected_items', 'client'), generate_test_params(client_set='collection', async_clients=False)
)
def test_client_list_iterable(client: CollectionClient, inputs: dict, expected_items: list[dict[str, int]]) -> None:
    with mock.patch.object(client.http_client, 'call', side_effect=mocked_api_pagination_logic):
        returned_items = [item for item in client.list(**inputs)]  # noqa: C416 list needed for assertion

        if inputs == {}:
            list_response = client.list(**inputs)
            assert len(returned_items) == list_response.total

        assert returned_items == expected_items


@pytest.mark.parametrize(
    ('inputs', 'expected_items', 'client'), generate_test_params(client_set='dataset', async_clients=True)
)
async def test_dataset_items_list_iterable_async(
    client: DatasetClientAsync, inputs: dict, expected_items: list[dict[str, int]]
) -> None:
    with mock.patch.object(client.http_client, 'call', side_effect=mocked_api_pagination_logic):
        returned_items = [item async for item in client.list_items(**inputs)]

        if inputs == {}:
            list_response = await client.list_items(**inputs)
            print(1)
            assert len(returned_items) == list_response.total

        assert returned_items == expected_items

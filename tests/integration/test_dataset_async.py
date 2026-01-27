from __future__ import annotations

import asyncio
import json
from unittest import mock
from unittest.mock import Mock

import impit
import pytest

from .utils import DatasetFixture, get_random_resource_name, parametrized_api_urls
from apify_client import ApifyClientAsync
from apify_client._client_config import DEFAULT_API_URL
from apify_client.errors import ApifyApiError

##################################################
# OLD TESTS - Tests with mocks and signed URLs
##################################################

MOCKED_API_DATASET_RESPONSE = """{
  "data": {
    "id": "someID",
    "name": "name",
    "userId": "userId",
    "createdAt": "2025-09-11T08:48:51.806Z",
    "modifiedAt": "2025-09-11T08:48:51.806Z",
    "accessedAt": "2025-09-11T08:48:51.806Z",
    "itemCount": 0,
    "cleanItemCount": 0,
    "actId": null,
    "actRunId": null,
    "schema": null,
    "stats": {
      "readCount": 0,
      "writeCount": 0,
      "deleteCount": 0,
      "listCount": 0,
      "storageBytes": 0
    },
    "fields": [],
    "consoleUrl": "https://console.apify.com/storage/datasets/someID",
    "itemsPublicUrl": "https://api.apify.com/v2/datasets/someID/items",
    "generalAccess": "FOLLOW_USER_SETTING",
    "urlSigningSecretKey": "urlSigningSecretKey"
  }
}"""


async def test_dataset_should_create_public_items_expiring_url_with_params(
    apify_client_async: ApifyClientAsync,
) -> None:
    created_dataset = await apify_client_async.datasets().get_or_create(name=get_random_resource_name('dataset'))

    dataset = apify_client_async.dataset(created_dataset.id)
    items_public_url = await dataset.create_items_public_url(
        expires_in_secs=2000,
        limit=10,
        offset=0,
    )

    assert 'signature=' in items_public_url
    assert 'limit=10' in items_public_url
    assert 'offset=0' in items_public_url

    impit_async_client = impit.AsyncClient()
    response = await impit_async_client.get(items_public_url, timeout=5)
    assert response.status_code == 200

    await dataset.delete()
    assert await apify_client_async.dataset(created_dataset.id).get() is None


async def test_dataset_should_create_public_items_non_expiring_url(apify_client_async: ApifyClientAsync) -> None:
    created_dataset = await apify_client_async.datasets().get_or_create(name=get_random_resource_name('dataset'))

    dataset = apify_client_async.dataset(created_dataset.id)
    items_public_url = await dataset.create_items_public_url()

    assert 'signature=' in items_public_url

    impit_async_client = impit.AsyncClient()
    response = await impit_async_client.get(items_public_url, timeout=5)
    assert response.status_code == 200

    await dataset.delete()
    assert await apify_client_async.dataset(created_dataset.id).get() is None


@parametrized_api_urls
async def test_public_url(api_token: str, api_url: str, api_public_url: str) -> None:
    apify_client = ApifyClientAsync(token=api_token, api_url=api_url, api_public_url=api_public_url)
    dataset = apify_client.dataset('someID')

    # Mock the API call to return predefined response
    mock_response = Mock()
    mock_response.json.return_value = json.loads(MOCKED_API_DATASET_RESPONSE)
    with mock.patch.object(apify_client.http_client, 'call', return_value=mock_response):
        public_url = await dataset.create_items_public_url()
        assert public_url == (
            f'{(api_public_url or DEFAULT_API_URL).strip("/")}/v2/datasets/'
            f'someID/items?signature={public_url.split("signature=")[1]}'
        )


async def test_list_items_signature(
    apify_client_async: ApifyClientAsync, test_dataset_of_another_user: DatasetFixture
) -> None:
    dataset = apify_client_async.dataset(dataset_id=test_dataset_of_another_user.id)

    # Permission error without valid signature
    with pytest.raises(
        ApifyApiError,
        match=r"Insufficient permissions for the dataset. Make sure you're passing a "
        r'correct API token and that it has the required permissions.',
    ):
        await dataset.list_items()

    # Dataset content retrieved with correct signature
    assert (
        test_dataset_of_another_user.expected_content
        == (await dataset.list_items(signature=test_dataset_of_another_user.signature)).items
    )


async def test_iterate_items_signature(
    apify_client_async: ApifyClientAsync, test_dataset_of_another_user: DatasetFixture
) -> None:
    dataset = apify_client_async.dataset(dataset_id=test_dataset_of_another_user.id)

    # Permission error without valid signature
    with pytest.raises(
        ApifyApiError,
        match=r"Insufficient permissions for the dataset. Make sure you're passing a "
        r'correct API token and that it has the required permissions.',
    ):
        [item async for item in dataset.iterate_items()]

    # Dataset content retrieved with correct signature
    assert test_dataset_of_another_user.expected_content == [
        item async for item in dataset.iterate_items(signature=test_dataset_of_another_user.signature)
    ]


async def test_get_items_as_bytes_signature(
    apify_client_async: ApifyClientAsync, test_dataset_of_another_user: DatasetFixture
) -> None:
    dataset = apify_client_async.dataset(dataset_id=test_dataset_of_another_user.id)

    # Permission error without valid signature
    with pytest.raises(
        ApifyApiError,
        match=r"Insufficient permissions for the dataset. Make sure you're passing a "
        r'correct API token and that it has the required permissions.',
    ):
        await dataset.get_items_as_bytes()

    # Dataset content retrieved with correct signature
    raw_data = await dataset.get_items_as_bytes(signature=test_dataset_of_another_user.signature)
    assert test_dataset_of_another_user.expected_content == json.loads(raw_data.decode('utf-8'))


#############
# NEW TESTS #
#############


async def test_dataset_get_or_create_and_get(apify_client_async: ApifyClientAsync) -> None:
    """Test creating a dataset and retrieving it."""
    dataset_name = get_random_resource_name('dataset')

    # Create dataset
    created_dataset = await apify_client_async.datasets().get_or_create(name=dataset_name)
    assert created_dataset is not None
    assert created_dataset.id is not None
    assert created_dataset.name == dataset_name

    # Get the same dataset
    dataset_client = apify_client_async.dataset(created_dataset.id)
    retrieved_dataset = await dataset_client.get()
    assert retrieved_dataset is not None
    assert retrieved_dataset.id == created_dataset.id
    assert retrieved_dataset.name == dataset_name

    # Cleanup
    await dataset_client.delete()


async def test_dataset_update(apify_client_async: ApifyClientAsync) -> None:
    """Test updating dataset properties."""
    dataset_name = get_random_resource_name('dataset')
    new_name = get_random_resource_name('dataset-updated')

    created_dataset = await apify_client_async.datasets().get_or_create(name=dataset_name)
    dataset_client = apify_client_async.dataset(created_dataset.id)

    # Update the name
    updated_dataset = await dataset_client.update(name=new_name)
    assert updated_dataset is not None
    assert updated_dataset.name == new_name
    assert updated_dataset.id == created_dataset.id

    # Verify the update persisted
    retrieved_dataset = await dataset_client.get()
    assert retrieved_dataset is not None
    assert retrieved_dataset.name == new_name

    # Cleanup
    await dataset_client.delete()


async def test_dataset_push_and_list_items(apify_client_async: ApifyClientAsync) -> None:
    """Test pushing items to dataset and listing them."""
    dataset_name = get_random_resource_name('dataset')

    created_dataset = await apify_client_async.datasets().get_or_create(name=dataset_name)
    dataset_client = apify_client_async.dataset(created_dataset.id)

    # Push some items
    items_to_push = [
        {'id': 1, 'name': 'Item 1', 'value': 100},
        {'id': 2, 'name': 'Item 2', 'value': 200},
        {'id': 3, 'name': 'Item 3', 'value': 300},
    ]
    await dataset_client.push_items(items_to_push)

    # Wait briefly for eventual consistency
    await asyncio.sleep(1)

    # List items
    items_page = await dataset_client.list_items()
    assert items_page is not None
    assert len(items_page.items) == 3
    assert items_page.count == 3
    # Note: items_page.total may be 0 immediately after push due to eventual consistency

    # Verify items content
    for i, item in enumerate(items_page.items):
        assert item['id'] == items_to_push[i]['id']
        assert item['name'] == items_to_push[i]['name']
        assert item['value'] == items_to_push[i]['value']

    # Cleanup
    await dataset_client.delete()


async def test_dataset_list_items_with_pagination(apify_client_async: ApifyClientAsync) -> None:
    """Test listing items with pagination parameters."""
    dataset_name = get_random_resource_name('dataset')

    created_dataset = await apify_client_async.datasets().get_or_create(name=dataset_name)
    dataset_client = apify_client_async.dataset(created_dataset.id)

    # Push more items
    items_to_push = [{'index': i, 'value': i * 10} for i in range(10)]
    await dataset_client.push_items(items_to_push)

    # Wait briefly for eventual consistency
    await asyncio.sleep(1)

    # List with limit
    items_page = await dataset_client.list_items(limit=5)
    assert len(items_page.items) == 5
    assert items_page.count == 5
    # Note: items_page.total may be 0 immediately after push due to eventual consistency
    assert items_page.limit == 5

    # List with offset
    items_page_offset = await dataset_client.list_items(offset=5, limit=5)
    assert len(items_page_offset.items) == 5
    assert items_page_offset.offset == 5
    # Note: items_page.total may be 0 immediately after push due to eventual consistency

    # Verify different items
    assert items_page.items[0]['index'] != items_page_offset.items[0]['index']

    # Cleanup
    await dataset_client.delete()


async def test_dataset_list_items_with_fields(apify_client_async: ApifyClientAsync) -> None:
    """Test listing items with field filtering."""
    dataset_name = get_random_resource_name('dataset')

    created_dataset = await apify_client_async.datasets().get_or_create(name=dataset_name)
    dataset_client = apify_client_async.dataset(created_dataset.id)

    # Push items with multiple fields
    items_to_push = [
        {'id': 1, 'name': 'Item 1', 'value': 100, 'extra': 'data1'},
        {'id': 2, 'name': 'Item 2', 'value': 200, 'extra': 'data2'},
    ]
    await dataset_client.push_items(items_to_push)

    # Wait briefly for eventual consistency
    await asyncio.sleep(1)

    # List with fields filter
    items_page = await dataset_client.list_items(fields=['id', 'name'])
    assert len(items_page.items) == 2

    # Verify only specified fields are returned
    for item in items_page.items:
        assert 'id' in item
        assert 'name' in item
        assert 'value' not in item
        assert 'extra' not in item

    # Cleanup
    await dataset_client.delete()


async def test_dataset_iterate_items(apify_client_async: ApifyClientAsync) -> None:
    """Test iterating over dataset items."""
    dataset_name = get_random_resource_name('dataset')

    created_dataset = await apify_client_async.datasets().get_or_create(name=dataset_name)
    dataset_client = apify_client_async.dataset(created_dataset.id)

    # Push items
    items_to_push = [{'index': i} for i in range(5)]
    await dataset_client.push_items(items_to_push)

    # Wait briefly for eventual consistency
    await asyncio.sleep(1)

    # Iterate over items
    collected_items = [item async for item in dataset_client.iterate_items()]

    assert len(collected_items) == 5
    for i, item in enumerate(collected_items):
        assert item['index'] == i

    # Cleanup
    await dataset_client.delete()


async def test_dataset_delete_nonexistent(apify_client_async: ApifyClientAsync) -> None:
    """Test that getting a deleted dataset returns None."""
    dataset_name = get_random_resource_name('dataset')

    created_dataset = await apify_client_async.datasets().get_or_create(name=dataset_name)
    dataset_client = apify_client_async.dataset(created_dataset.id)

    # Delete dataset
    await dataset_client.delete()

    # Verify it's gone
    retrieved_dataset = await dataset_client.get()
    assert retrieved_dataset is None


async def test_dataset_get_statistics(apify_client_async: ApifyClientAsync) -> None:
    """Test getting dataset statistics."""
    dataset_name = get_random_resource_name('dataset')

    created_dataset = await apify_client_async.datasets().get_or_create(name=dataset_name)
    dataset_client = apify_client_async.dataset(created_dataset.id)

    try:
        # Push some items first
        items_to_push = [
            {'id': 1, 'name': 'Item 1'},
            {'id': 2, 'name': 'Item 2'},
        ]
        await dataset_client.push_items(items_to_push)

        # Wait briefly for eventual consistency
        await asyncio.sleep(1)

        # Get statistics
        statistics = await dataset_client.get_statistics()

        # Verify statistics is returned and properly parsed
        assert statistics is not None

    finally:
        # Cleanup
        await dataset_client.delete()


async def test_dataset_stream_items(apify_client_async: ApifyClientAsync) -> None:
    """Test streaming dataset items."""
    dataset_name = get_random_resource_name('dataset')

    created_dataset = await apify_client_async.datasets().get_or_create(name=dataset_name)
    dataset_client = apify_client_async.dataset(created_dataset.id)

    try:
        # Push some items
        items_to_push = [
            {'id': 1, 'name': 'Item 1', 'value': 100},
            {'id': 2, 'name': 'Item 2', 'value': 200},
            {'id': 3, 'name': 'Item 3', 'value': 300},
        ]
        await dataset_client.push_items(items_to_push)

        # Wait briefly for eventual consistency
        await asyncio.sleep(1)

        # Stream items using async context manager
        async with dataset_client.stream_items(item_format='json') as response:
            assert response is not None
            assert response.status_code == 200
            content = await response.aread()
            items = json.loads(content)
            assert len(items) == 3
            assert items[0]['id'] == 1

    finally:
        # Cleanup
        await dataset_client.delete()

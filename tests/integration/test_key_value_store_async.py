from __future__ import annotations

import asyncio
import json
from unittest import mock
from unittest.mock import Mock

import impit
import pytest

from .utils import KvsFixture, get_random_resource_name, parametrized_api_urls
from apify_client import ApifyClientAsync
from apify_client._config import DEFAULT_API_URL
from apify_client._utils import create_hmac_signature, create_storage_content_signature
from apify_client.errors import ApifyApiError

##################################################
# OLD TESTS - Tests with mocks and signed URLs
##################################################

MOCKED_ID = 'someID'


def _get_mocked_api_kvs_response(signing_key: str | None = None) -> Mock:
    response_data = {
        'data': {
            'id': MOCKED_ID,
            'name': 'name',
            'userId': 'userId',
            'createdAt': '2025-09-11T08:48:51.806Z',
            'modifiedAt': '2025-09-11T08:48:51.806Z',
            'accessedAt': '2025-09-11T08:48:51.806Z',
            'actId': None,
            'actRunId': None,
            'schema': None,
            'stats': {'readCount': 0, 'writeCount': 0, 'deleteCount': 0, 'listCount': 0, 'storageBytes': 0},
            'consoleUrl': 'https://console.apify.com/storage/key-value-stores/someID',
            'keysPublicUrl': 'https://api.apify.com/v2/key-value-stores/someID/keys',
            'generalAccess': 'FOLLOW_USER_SETTING',
        }
    }
    if signing_key:
        response_data['data']['urlSigningSecretKey'] = signing_key

    mock_response = Mock()
    mock_response.json.return_value = response_data
    return mock_response


async def test_key_value_store_should_create_expiring_keys_public_url_with_params(
    apify_client_async: ApifyClientAsync,
) -> None:
    created_store = await apify_client_async.key_value_stores().get_or_create(
        name=get_random_resource_name('key-value-store')
    )

    store = apify_client_async.key_value_store(created_store.id)
    keys_public_url = await store.create_keys_public_url(
        expires_in_secs=2000,
        limit=10,
    )

    assert 'signature=' in keys_public_url
    assert 'limit=10' in keys_public_url

    impit_async_client = impit.AsyncClient()
    response = await impit_async_client.get(keys_public_url, timeout=5)
    assert response.status_code == 200

    await store.delete()
    assert await apify_client_async.key_value_store(created_store.id).get() is None


async def test_key_value_store_should_create_public_keys_non_expiring_url(
    apify_client_async: ApifyClientAsync,
) -> None:
    created_store = await apify_client_async.key_value_stores().get_or_create(
        name=get_random_resource_name('key-value-store')
    )

    store = apify_client_async.key_value_store(created_store.id)
    keys_public_url = await store.create_keys_public_url()

    assert 'signature=' in keys_public_url

    impit_async_client = impit.AsyncClient()
    response = await impit_async_client.get(keys_public_url, timeout=5)
    assert response.status_code == 200

    await store.delete()
    assert await apify_client_async.key_value_store(created_store.id).get() is None


@pytest.mark.parametrize('signing_key', [None, 'custom-signing-key'])
@parametrized_api_urls
async def test_public_url(api_token: str, api_url: str, api_public_url: str, signing_key: str) -> None:
    apify_client = ApifyClientAsync(token=api_token, api_url=api_url, api_public_url=api_public_url)
    kvs = apify_client.key_value_store(MOCKED_ID)

    # Mock the API call to return predefined response
    with mock.patch.object(
        apify_client.http_client,
        'call',
        return_value=_get_mocked_api_kvs_response(signing_key=signing_key),
    ):
        public_url = await kvs.create_keys_public_url()
        if signing_key:
            signature_value = create_storage_content_signature(
                resource_id=MOCKED_ID, url_signing_secret_key=signing_key
            )
            expected_signature = f'?signature={signature_value}'
        else:
            expected_signature = ''
        assert public_url == (
            f'{(api_public_url or DEFAULT_API_URL).strip("/")}/v2/key-value-stores/someID/keys{expected_signature}'
        )


@pytest.mark.parametrize('signing_key', [None, 'custom-signing-key'])
@parametrized_api_urls
async def test_record_public_url(api_token: str, api_url: str, api_public_url: str, signing_key: str) -> None:
    apify_client = ApifyClientAsync(token=api_token, api_url=api_url, api_public_url=api_public_url)
    key = 'some_key'
    kvs = apify_client.key_value_store(MOCKED_ID)

    # Mock the API call to return predefined response
    with mock.patch.object(
        apify_client.http_client,
        'call',
        return_value=_get_mocked_api_kvs_response(signing_key=signing_key),
    ):
        public_url = await kvs.get_record_public_url(key=key)
        expected_signature = f'?signature={create_hmac_signature(signing_key, key)}' if signing_key else ''
        assert public_url == (
            f'{(api_public_url or DEFAULT_API_URL).strip("/")}/v2/key-value-stores/someID/'
            f'records/{key}{expected_signature}'
        )


async def test_list_keys_signature(apify_client_async: ApifyClientAsync, test_kvs_of_another_user: KvsFixture) -> None:
    kvs = apify_client_async.key_value_store(key_value_store_id=test_kvs_of_another_user.id)

    # Permission error without valid signature
    with pytest.raises(
        ApifyApiError,
        match=r"Insufficient permissions for the key-value store. Make sure you're passing a correct"
        r' API token and that it has the required permissions.',
    ):
        await kvs.list_keys()

    # Kvs content retrieved with correct signature
    response = await kvs.list_keys(signature=test_kvs_of_another_user.signature)
    raw_items = response.items

    assert set(test_kvs_of_another_user.expected_content) == {item.key for item in raw_items}


async def test_get_record_signature(apify_client_async: ApifyClientAsync, test_kvs_of_another_user: KvsFixture) -> None:
    key = 'key1'
    kvs = apify_client_async.key_value_store(key_value_store_id=test_kvs_of_another_user.id)

    # Permission error without valid signature
    with pytest.raises(
        ApifyApiError,
        match=r"Insufficient permissions for the key-value store. Make sure you're passing a correct"
        r' API token and that it has the required permissions.',
    ):
        await kvs.get_record(key=key)

    # Kvs content retrieved with correct signature
    record = await kvs.get_record(key=key, signature=test_kvs_of_another_user.keys_signature[key])
    assert record
    assert test_kvs_of_another_user.expected_content[key] == record['value']


async def test_get_record_as_bytes_signature(
    apify_client_async: ApifyClientAsync, test_kvs_of_another_user: KvsFixture
) -> None:
    key = 'key1'
    kvs = apify_client_async.key_value_store(key_value_store_id=test_kvs_of_another_user.id)

    # Permission error without valid signature
    with pytest.raises(
        ApifyApiError,
        match=r"Insufficient permissions for the key-value store. Make sure you're passing a correct"
        r' API token and that it has the required permissions.',
    ):
        await kvs.get_record_as_bytes(key=key)

    # Kvs content retrieved with correct signature
    item = await kvs.get_record_as_bytes(key=key, signature=test_kvs_of_another_user.keys_signature[key])
    assert item
    assert test_kvs_of_another_user.expected_content[key] == json.loads(item['value'].decode('utf-8'))


async def test_stream_record_signature(
    apify_client_async: ApifyClientAsync,
    test_kvs_of_another_user: KvsFixture,
) -> None:
    key = 'key1'
    kvs = apify_client_async.key_value_store(key_value_store_id=test_kvs_of_another_user.id)

    # Permission error without valid signature
    with pytest.raises(
        ApifyApiError,
        match=r"Insufficient permissions for the key-value store. Make sure you're passing a correct"
        r' API token and that it has the required permissions.',
    ):
        async with kvs.stream_record(key=key):
            pass

    # Kvs content retrieved with correct signature
    async with kvs.stream_record(key=key, signature=test_kvs_of_another_user.keys_signature[key]) as stream:
        assert stream
        value = json.loads(stream['value'].content.decode('utf-8'))
    assert test_kvs_of_another_user.expected_content[key] == value


#############
# NEW TESTS #
#############


async def test_key_value_store_get_or_create_and_get(apify_client_async: ApifyClientAsync) -> None:
    """Test creating a key-value store and retrieving it."""
    store_name = get_random_resource_name('kvs')

    # Create store
    created_store = await apify_client_async.key_value_stores().get_or_create(name=store_name)
    assert created_store is not None
    assert created_store.id is not None
    assert created_store.name == store_name

    # Get the same store
    store_client = apify_client_async.key_value_store(created_store.id)
    retrieved_store = await store_client.get()
    assert retrieved_store is not None
    assert retrieved_store.id == created_store.id
    assert retrieved_store.name == store_name

    # Cleanup
    await store_client.delete()


async def test_key_value_store_update(apify_client_async: ApifyClientAsync) -> None:
    """Test updating key-value store properties."""
    store_name = get_random_resource_name('kvs')
    new_name = get_random_resource_name('kvs-updated')

    created_store = await apify_client_async.key_value_stores().get_or_create(name=store_name)
    store_client = apify_client_async.key_value_store(created_store.id)

    # Update the name
    updated_store = await store_client.update(name=new_name)
    assert updated_store is not None
    assert updated_store.name == new_name
    assert updated_store.id == created_store.id

    # Verify the update persisted
    retrieved_store = await store_client.get()
    assert retrieved_store is not None
    assert retrieved_store.name == new_name

    # Cleanup
    await store_client.delete()


async def test_key_value_store_set_and_get_record(apify_client_async: ApifyClientAsync) -> None:
    """Test setting and getting records from key-value store."""
    store_name = get_random_resource_name('kvs')

    created_store = await apify_client_async.key_value_stores().get_or_create(name=store_name)
    store_client = apify_client_async.key_value_store(created_store.id)

    # Set a JSON record
    test_value = {'name': 'Test Item', 'value': 123, 'nested': {'data': 'value'}}
    await store_client.set_record('test-key', test_value)

    # Wait briefly for eventual consistency
    await asyncio.sleep(1)

    # Get the record
    record = await store_client.get_record('test-key')
    assert record is not None
    assert record['key'] == 'test-key'
    assert record['value'] == test_value
    assert 'application/json' in record['content_type']

    # Cleanup
    await store_client.delete()


async def test_key_value_store_set_and_get_text_record(apify_client_async: ApifyClientAsync) -> None:
    """Test setting and getting text records."""
    store_name = get_random_resource_name('kvs')

    created_store = await apify_client_async.key_value_stores().get_or_create(name=store_name)
    store_client = apify_client_async.key_value_store(created_store.id)

    # Set a text record
    test_text = 'Hello, this is a test text!'
    await store_client.set_record('text-key', test_text, content_type='text/plain')

    # Wait briefly for eventual consistency
    await asyncio.sleep(1)

    # Get the record
    record = await store_client.get_record('text-key')
    assert record is not None
    assert record['key'] == 'text-key'
    assert record['value'] == test_text
    assert 'text/plain' in record['content_type']

    # Cleanup
    await store_client.delete()


async def test_key_value_store_list_keys(apify_client_async: ApifyClientAsync) -> None:
    """Test listing keys in the key-value store."""
    store_name = get_random_resource_name('kvs')

    created_store = await apify_client_async.key_value_stores().get_or_create(name=store_name)
    store_client = apify_client_async.key_value_store(created_store.id)

    # Set multiple records
    for i in range(5):
        await store_client.set_record(f'key-{i}', {'index': i})

    # Wait briefly for eventual consistency
    await asyncio.sleep(1)

    # List keys
    keys_response = await store_client.list_keys()
    assert keys_response is not None
    assert len(keys_response.items) == 5

    # Verify key names
    key_names = [item.key for item in keys_response.items]
    for i in range(5):
        assert f'key-{i}' in key_names

    # Cleanup
    await store_client.delete()


async def test_key_value_store_list_keys_with_limit(apify_client_async: ApifyClientAsync) -> None:
    """Test listing keys with limit parameter."""
    store_name = get_random_resource_name('kvs')

    created_store = await apify_client_async.key_value_stores().get_or_create(name=store_name)
    store_client = apify_client_async.key_value_store(created_store.id)

    # Set multiple records
    for i in range(10):
        await store_client.set_record(f'item-{i:02d}', {'index': i})

    # Wait briefly for eventual consistency
    await asyncio.sleep(1)

    # List with limit
    keys_response = await store_client.list_keys(limit=5)
    assert keys_response is not None
    assert len(keys_response.items) == 5

    # Cleanup
    await store_client.delete()


async def test_key_value_store_record_exists(apify_client_async: ApifyClientAsync) -> None:
    """Test checking if a record exists."""
    store_name = get_random_resource_name('kvs')

    created_store = await apify_client_async.key_value_stores().get_or_create(name=store_name)
    store_client = apify_client_async.key_value_store(created_store.id)

    # Set a record
    await store_client.set_record('exists-key', {'data': 'value'})

    # Wait briefly for eventual consistency
    await asyncio.sleep(1)

    # Check existence
    assert await store_client.record_exists('exists-key') is True
    assert await store_client.record_exists('non-existent-key') is False

    # Cleanup
    await store_client.delete()


async def test_key_value_store_delete_record(apify_client_async: ApifyClientAsync) -> None:
    """Test deleting a record from the store."""
    store_name = get_random_resource_name('kvs')

    created_store = await apify_client_async.key_value_stores().get_or_create(name=store_name)
    store_client = apify_client_async.key_value_store(created_store.id)

    # Set a record
    await store_client.set_record('delete-me', {'data': 'value'})

    # Wait briefly for eventual consistency
    await asyncio.sleep(1)

    # Verify it exists
    assert await store_client.get_record('delete-me') is not None

    # Delete the record
    await store_client.delete_record('delete-me')

    # Wait briefly
    await asyncio.sleep(1)

    # Verify it's gone
    assert await store_client.get_record('delete-me') is None

    # Cleanup
    await store_client.delete()


async def test_key_value_store_delete_nonexistent(apify_client_async: ApifyClientAsync) -> None:
    """Test that getting a deleted store returns None."""
    store_name = get_random_resource_name('kvs')

    created_store = await apify_client_async.key_value_stores().get_or_create(name=store_name)
    store_client = apify_client_async.key_value_store(created_store.id)

    # Delete store
    await store_client.delete()

    # Verify it's gone
    retrieved_store = await store_client.get()
    assert retrieved_store is None

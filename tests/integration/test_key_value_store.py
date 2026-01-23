from __future__ import annotations

import json
import time
from unittest import mock
from unittest.mock import Mock

import impit
import pytest
from apify_shared.utils import create_hmac_signature, create_storage_content_signature

from .utils import KvsFixture, get_random_resource_name, parametrized_api_urls
from apify_client import ApifyClient
from apify_client._client import DEFAULT_API_URL
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


def test_key_value_store_should_create_expiring_keys_public_url_with_params(
    apify_client: ApifyClient,
) -> None:
    created_store = apify_client.key_value_stores().get_or_create(name=get_random_resource_name('key-value-store'))

    store = apify_client.key_value_store(created_store.id)
    keys_public_url = store.create_keys_public_url(
        expires_in_secs=2000,
        limit=10,
    )

    assert 'signature=' in keys_public_url
    assert 'limit=10' in keys_public_url

    impit_client = impit.Client()
    response = impit_client.get(keys_public_url, timeout=5)
    assert response.status_code == 200

    store.delete()
    assert apify_client.key_value_store(created_store.id).get() is None


def test_key_value_store_should_create_public_keys_non_expiring_url(apify_client: ApifyClient) -> None:
    created_store = apify_client.key_value_stores().get_or_create(name=get_random_resource_name('key-value-store'))

    store = apify_client.key_value_store(created_store.id)
    keys_public_url = store.create_keys_public_url()

    assert 'signature=' in keys_public_url

    impit_client = impit.Client()
    response = impit_client.get(keys_public_url, timeout=5)
    assert response.status_code == 200

    store.delete()
    assert apify_client.key_value_store(created_store.id).get() is None


@pytest.mark.parametrize('signing_key', [None, 'custom-signing-key'])
@parametrized_api_urls
def test_public_url(api_token: str, api_url: str, api_public_url: str, signing_key: str) -> None:
    apify_client = ApifyClient(token=api_token, api_url=api_url, api_public_url=api_public_url)
    kvs = apify_client.key_value_store(MOCKED_ID)

    # Mock the API call to return predefined response
    with mock.patch.object(
        apify_client.http_client,
        'call',
        return_value=_get_mocked_api_kvs_response(signing_key=signing_key),
    ):
        public_url = kvs.create_keys_public_url()
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
def test_record_public_url(api_token: str, api_url: str, api_public_url: str, signing_key: str) -> None:
    apify_client = ApifyClient(token=api_token, api_url=api_url, api_public_url=api_public_url)
    key = 'some_key'
    kvs = apify_client.key_value_store(MOCKED_ID)

    # Mock the API call to return predefined response
    with mock.patch.object(
        apify_client.http_client,
        'call',
        return_value=_get_mocked_api_kvs_response(signing_key=signing_key),
    ):
        public_url = kvs.get_record_public_url(key=key)
        expected_signature = f'?signature={create_hmac_signature(signing_key, key)}' if signing_key else ''
        assert public_url == (
            f'{(api_public_url or DEFAULT_API_URL).strip("/")}/v2/key-value-stores/someID/'
            f'records/{key}{expected_signature}'
        )


def test_list_keys_signature(apify_client: ApifyClient, test_kvs_of_another_user: KvsFixture) -> None:
    kvs = apify_client.key_value_store(key_value_store_id=test_kvs_of_another_user.id)

    # Permission error without valid signature
    with pytest.raises(
        ApifyApiError,
        match=r"Insufficient permissions for the key-value store. Make sure you're passing a correct"
        r' API token and that it has the required permissions.',
    ):
        kvs.list_keys()

    # Kvs content retrieved with correct signature
    response = kvs.list_keys(signature=test_kvs_of_another_user.signature)
    raw_items = response.items

    assert set(test_kvs_of_another_user.expected_content) == {item.key for item in raw_items}


def test_get_record_signature(apify_client: ApifyClient, test_kvs_of_another_user: KvsFixture) -> None:
    key = 'key1'
    kvs = apify_client.key_value_store(key_value_store_id=test_kvs_of_another_user.id)

    # Permission error without valid signature
    with pytest.raises(
        ApifyApiError,
        match=r"Insufficient permissions for the key-value store. Make sure you're passing a correct"
        r' API token and that it has the required permissions.',
    ):
        kvs.get_record(key=key)

    # Kvs content retrieved with correct signature
    record = kvs.get_record(key=key, signature=test_kvs_of_another_user.keys_signature[key])
    assert record
    assert test_kvs_of_another_user.expected_content[key] == record['value']


def test_get_record_as_bytes_signature(apify_client: ApifyClient, test_kvs_of_another_user: KvsFixture) -> None:
    key = 'key1'
    kvs = apify_client.key_value_store(key_value_store_id=test_kvs_of_another_user.id)

    # Permission error without valid signature
    with pytest.raises(
        ApifyApiError,
        match=r"Insufficient permissions for the key-value store. Make sure you're passing a correct"
        r' API token and that it has the required permissions.',
    ):
        kvs.get_record_as_bytes(key=key)

    # Kvs content retrieved with correct signature
    item = kvs.get_record_as_bytes(key=key, signature=test_kvs_of_another_user.keys_signature[key])
    assert item
    assert test_kvs_of_another_user.expected_content[key] == json.loads(item['value'].decode('utf-8'))


def test_stream_record_signature(apify_client: ApifyClient, test_kvs_of_another_user: KvsFixture) -> None:
    key = 'key1'
    kvs = apify_client.key_value_store(key_value_store_id=test_kvs_of_another_user.id)

    # Permission error without valid signature
    with (
        pytest.raises(
            ApifyApiError,
            match=r"Insufficient permissions for the key-value store. Make sure you're passing a correct"
            r' API token and that it has the required permissions.',
        ),
        kvs.stream_record(key=key),
    ):
        pass

    # Kvs content retrieved with correct signature
    with kvs.stream_record(key=key, signature=test_kvs_of_another_user.keys_signature[key]) as stream:
        assert stream
        value = json.loads(stream['value'].content.decode('utf-8'))
    assert test_kvs_of_another_user.expected_content[key] == value


#############
# NEW TESTS #
#############


def test_key_value_store_get_or_create_and_get(apify_client: ApifyClient) -> None:
    """Test creating a key-value store and retrieving it."""
    store_name = get_random_resource_name('kvs')

    # Create store
    created_store = apify_client.key_value_stores().get_or_create(name=store_name)
    assert created_store is not None
    assert created_store.id is not None
    assert created_store.name == store_name

    # Get the same store
    store_client = apify_client.key_value_store(created_store.id)
    retrieved_store = store_client.get()
    assert retrieved_store is not None
    assert retrieved_store.id == created_store.id
    assert retrieved_store.name == store_name

    # Cleanup
    store_client.delete()


def test_key_value_store_update(apify_client: ApifyClient) -> None:
    """Test updating key-value store properties."""
    store_name = get_random_resource_name('kvs')
    new_name = get_random_resource_name('kvs-updated')

    created_store = apify_client.key_value_stores().get_or_create(name=store_name)
    store_client = apify_client.key_value_store(created_store.id)

    # Update the name
    updated_store = store_client.update(name=new_name)
    assert updated_store is not None
    assert updated_store.name == new_name
    assert updated_store.id == created_store.id

    # Verify the update persisted
    retrieved_store = store_client.get()
    assert retrieved_store is not None
    assert retrieved_store.name == new_name

    # Cleanup
    store_client.delete()


def test_key_value_store_set_and_get_record(apify_client: ApifyClient) -> None:
    """Test setting and getting records from key-value store."""
    store_name = get_random_resource_name('kvs')

    created_store = apify_client.key_value_stores().get_or_create(name=store_name)
    store_client = apify_client.key_value_store(created_store.id)

    # Set a JSON record
    test_value = {'name': 'Test Item', 'value': 123, 'nested': {'data': 'value'}}
    store_client.set_record('test-key', test_value)

    # Wait briefly for eventual consistency
    time.sleep(1)

    # Get the record
    record = store_client.get_record('test-key')
    assert record is not None
    assert record['key'] == 'test-key'
    assert record['value'] == test_value
    assert 'application/json' in record['content_type']

    # Cleanup
    store_client.delete()


def test_key_value_store_set_and_get_text_record(apify_client: ApifyClient) -> None:
    """Test setting and getting text records."""
    store_name = get_random_resource_name('kvs')

    created_store = apify_client.key_value_stores().get_or_create(name=store_name)
    store_client = apify_client.key_value_store(created_store.id)

    # Set a text record
    test_text = 'Hello, this is a test text!'
    store_client.set_record('text-key', test_text, content_type='text/plain')

    # Wait briefly for eventual consistency
    time.sleep(1)

    # Get the record
    record = store_client.get_record('text-key')
    assert record is not None
    assert record['key'] == 'text-key'
    assert record['value'] == test_text
    assert 'text/plain' in record['content_type']

    # Cleanup
    store_client.delete()


def test_key_value_store_list_keys(apify_client: ApifyClient) -> None:
    """Test listing keys in the key-value store."""
    store_name = get_random_resource_name('kvs')

    created_store = apify_client.key_value_stores().get_or_create(name=store_name)
    store_client = apify_client.key_value_store(created_store.id)

    # Set multiple records
    for i in range(5):
        store_client.set_record(f'key-{i}', {'index': i})

    # Wait briefly for eventual consistency
    time.sleep(1)

    # List keys
    keys_response = store_client.list_keys()
    assert keys_response is not None
    assert len(keys_response.items) == 5

    # Verify key names
    key_names = [item.key for item in keys_response.items]
    for i in range(5):
        assert f'key-{i}' in key_names

    # Cleanup
    store_client.delete()


def test_key_value_store_list_keys_with_limit(apify_client: ApifyClient) -> None:
    """Test listing keys with limit parameter."""
    store_name = get_random_resource_name('kvs')

    created_store = apify_client.key_value_stores().get_or_create(name=store_name)
    store_client = apify_client.key_value_store(created_store.id)

    # Set multiple records
    for i in range(10):
        store_client.set_record(f'item-{i:02d}', {'index': i})

    # Wait briefly for eventual consistency
    time.sleep(1)

    # List with limit
    keys_response = store_client.list_keys(limit=5)
    assert keys_response is not None
    assert len(keys_response.items) == 5

    # Cleanup
    store_client.delete()


def test_key_value_store_record_exists(apify_client: ApifyClient) -> None:
    """Test checking if a record exists."""
    store_name = get_random_resource_name('kvs')

    created_store = apify_client.key_value_stores().get_or_create(name=store_name)
    store_client = apify_client.key_value_store(created_store.id)

    # Set a record
    store_client.set_record('exists-key', {'data': 'value'})

    # Wait briefly for eventual consistency
    time.sleep(1)

    # Check existence
    assert store_client.record_exists('exists-key') is True
    assert store_client.record_exists('non-existent-key') is False

    # Cleanup
    store_client.delete()


def test_key_value_store_delete_record(apify_client: ApifyClient) -> None:
    """Test deleting a record from the store."""
    store_name = get_random_resource_name('kvs')

    created_store = apify_client.key_value_stores().get_or_create(name=store_name)
    store_client = apify_client.key_value_store(created_store.id)

    # Set a record
    store_client.set_record('delete-me', {'data': 'value'})

    # Wait briefly for eventual consistency
    time.sleep(1)

    # Verify it exists
    assert store_client.get_record('delete-me') is not None

    # Delete the record
    store_client.delete_record('delete-me')

    # Wait briefly
    time.sleep(1)

    # Verify it's gone
    assert store_client.get_record('delete-me') is None

    # Cleanup
    store_client.delete()


def test_key_value_store_delete_nonexistent(apify_client: ApifyClient) -> None:
    """Test that getting a deleted store returns None."""
    store_name = get_random_resource_name('kvs')

    created_store = apify_client.key_value_stores().get_or_create(name=store_name)
    store_client = apify_client.key_value_store(created_store.id)

    # Delete store
    store_client.delete()

    # Verify it's gone
    retrieved_store = store_client.get()
    assert retrieved_store is None

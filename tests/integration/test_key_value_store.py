from __future__ import annotations

import json
from unittest import mock
from unittest.mock import Mock

import impit
import pytest
from apify_shared.utils import create_hmac_signature, create_storage_content_signature

from .integration_test_utils import TestKvs, parametrized_api_urls, random_resource_name
from apify_client import ApifyClient, ApifyClientAsync
from apify_client.client import DEFAULT_API_URL
from apify_client.errors import ApifyApiError

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


class TestKeyValueStoreSync:
    def test_key_value_store_should_create_expiring_keys_public_url_with_params(
        self, apify_client: ApifyClient
    ) -> None:
        created_store = apify_client.key_value_stores().get_or_create(name=random_resource_name('key-value-store'))

        store = apify_client.key_value_store(created_store['id'])
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
        assert apify_client.key_value_store(created_store['id']).get() is None

    def test_key_value_store_should_create_public_keys_non_expiring_url(self, apify_client: ApifyClient) -> None:
        created_store = apify_client.key_value_stores().get_or_create(name=random_resource_name('key-value-store'))

        store = apify_client.key_value_store(created_store['id'])
        keys_public_url = store.create_keys_public_url()

        assert 'signature=' in keys_public_url

        impit_client = impit.Client()
        response = impit_client.get(keys_public_url, timeout=5)
        assert response.status_code == 200

        store.delete()
        assert apify_client.key_value_store(created_store['id']).get() is None

    @pytest.mark.parametrize('signing_key', [None, 'custom-signing-key'])
    @parametrized_api_urls
    def test_public_url(self, api_token: str, api_url: str, api_public_url: str, signing_key: str) -> None:
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
    def test_record_public_url(self, api_token: str, api_url: str, api_public_url: str, signing_key: str) -> None:
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

    def test_list_keys_signature(self, apify_client: ApifyClient, test_kvs_of_another_user: TestKvs) -> None:
        kvs = apify_client.key_value_store(key_value_store_id=test_kvs_of_another_user.id)

        # Permission error without valid signature
        with pytest.raises(
            ApifyApiError,
            match=r"Insufficient permissions for the key-value store. Make sure you're passing a correct"
            r' API token and that it has the required permissions.',
        ):
            kvs.list_keys()

        # Kvs content retrieved with correct signature
        raw_items = kvs.list_keys(signature=test_kvs_of_another_user.signature)['items']

        assert set(test_kvs_of_another_user.expected_content) == {item['key'] for item in raw_items}

    def test_get_record_signature(self, apify_client: ApifyClient, test_kvs_of_another_user: TestKvs) -> None:
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

    def test_get_record_as_bytes_signature(self, apify_client: ApifyClient, test_kvs_of_another_user: TestKvs) -> None:
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

    def test_stream_record_signature(self, apify_client: ApifyClient, test_kvs_of_another_user: TestKvs) -> None:
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


class TestKeyValueStoreAsync:
    async def test_key_value_store_should_create_expiring_keys_public_url_with_params(
        self, apify_client_async: ApifyClientAsync
    ) -> None:
        created_store = await apify_client_async.key_value_stores().get_or_create(
            name=random_resource_name('key-value-store')
        )

        store = apify_client_async.key_value_store(created_store['id'])
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
        assert await apify_client_async.key_value_store(created_store['id']).get() is None

    async def test_key_value_store_should_create_public_keys_non_expiring_url(
        self, apify_client_async: ApifyClientAsync
    ) -> None:
        created_store = await apify_client_async.key_value_stores().get_or_create(
            name=random_resource_name('key-value-store')
        )

        store = apify_client_async.key_value_store(created_store['id'])
        keys_public_url = await store.create_keys_public_url()

        assert 'signature=' in keys_public_url

        impit_async_client = impit.AsyncClient()
        response = await impit_async_client.get(keys_public_url, timeout=5)
        assert response.status_code == 200

        await store.delete()
        assert await apify_client_async.key_value_store(created_store['id']).get() is None

    @pytest.mark.parametrize('signing_key', [None, 'custom-signing-key'])
    @parametrized_api_urls
    async def test_public_url(self, api_token: str, api_url: str, api_public_url: str, signing_key: str) -> None:
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
    async def test_record_public_url(self, api_token: str, api_url: str, api_public_url: str, signing_key: str) -> None:
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

    async def test_list_keys_signature(
        self, apify_client_async: ApifyClientAsync, test_kvs_of_another_user: TestKvs
    ) -> None:
        kvs = apify_client_async.key_value_store(key_value_store_id=test_kvs_of_another_user.id)

        # Permission error without valid signature
        with pytest.raises(
            ApifyApiError,
            match=r"Insufficient permissions for the key-value store. Make sure you're passing a correct"
            r' API token and that it has the required permissions.',
        ):
            await kvs.list_keys()

        # Kvs content retrieved with correct signature
        raw_items = (await kvs.list_keys(signature=test_kvs_of_another_user.signature))['items']

        assert set(test_kvs_of_another_user.expected_content) == {item['key'] for item in raw_items}

    async def test_get_record_signature(
        self, apify_client_async: ApifyClientAsync, test_kvs_of_another_user: TestKvs
    ) -> None:
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
        self, apify_client_async: ApifyClientAsync, test_kvs_of_another_user: TestKvs
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
        self, apify_client_async: ApifyClientAsync, test_kvs_of_another_user: TestKvs
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

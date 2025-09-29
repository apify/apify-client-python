from __future__ import annotations

import json
from unittest import mock
from unittest.mock import Mock

import impit
import pytest

from integration.integration_test_utils import parametrized_api_urls, random_resource_name

from apify_client import ApifyClient, ApifyClientAsync
from apify_client.client import DEFAULT_API_URL


def _get_mocked_api_kvs_response(signing_key: str | None = None) -> str:
    response_data = {
        'data': {
            'id': 'someID',
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

    return json.dumps(response_data)


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

    @pytest.mark.parametrize('signature', [None, 'custom-signature'])
    @parametrized_api_urls
    def test_public_url(self, api_token: str, api_url: str, api_public_url: str, signature: str) -> None:
        apify_client = ApifyClient(token=api_token, api_url=api_url, api_public_url=api_public_url)
        kvs = apify_client.key_value_store('someID')

        # Mock the API call to return predefined response
        with mock.patch.object(
            apify_client.http_client,
            'call',
            return_value=Mock(text=_get_mocked_api_kvs_response(signing_key=signature)),
        ):
            public_url = kvs.create_keys_public_url()
            expected_signature = f'?signature={public_url.split("signature=")[1]}' if signature else ''
            assert public_url == (
                f'{(api_public_url or DEFAULT_API_URL).strip("/")}/v2/key-value-stores/someID/keys{expected_signature}'
            )

    @pytest.mark.parametrize('signature', [None, 'custom-signature'])
    def test_record_public_url(self, api_token: str, signature: str) -> None:
        apify_client = ApifyClient(token=api_token)
        kvs = apify_client.key_value_store('someID')

        # Mock the API call to return predefined response
        with mock.patch.object(
            apify_client.http_client,
            'call',
            return_value=Mock(text=_get_mocked_api_kvs_response(signing_key=signature)),
        ):
            public_url = kvs.get_record_public_url(key='key')
            expected_signature = f'?signature={public_url.split("signature=")[1]}' if signature else ''
            assert public_url == (f'{DEFAULT_API_URL}/v2/key-value-stores/someID/records/key{expected_signature}')


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

    @pytest.mark.parametrize('signature', [None, 'custom-signature'])
    @parametrized_api_urls
    async def test_record_public_url(self, api_token: str, api_url: str, api_public_url: str, signature: str) -> None:
        apify_client = ApifyClientAsync(token=api_token, api_url=api_url, api_public_url=api_public_url)
        kvs = apify_client.key_value_store('someID')

        # Mock the API call to return predefined response
        with mock.patch.object(
            apify_client.http_client,
            'call',
            return_value=Mock(text=_get_mocked_api_kvs_response(signing_key=signature)),
        ):
            public_url = await kvs.create_keys_public_url()
            expected_signature = f'?signature={public_url.split("signature=")[1]}' if signature else ''
            assert public_url == (
                f'{(api_public_url or DEFAULT_API_URL).strip("/")}/v2/key-value-stores/someID/keys{expected_signature}'
            )

    @pytest.mark.parametrize('signature', [None, 'custom-signature'])
    async def test_public_url(self, api_token: str, signature: str) -> None:
        apify_client = ApifyClientAsync(token=api_token)
        kvs = apify_client.key_value_store('someID')

        # Mock the API call to return predefined response
        with mock.patch.object(
            apify_client.http_client,
            'call',
            return_value=Mock(text=_get_mocked_api_kvs_response(signing_key=signature)),
        ):
            public_url = await kvs.get_record_public_url(key='key')
            expected_signature = f'?signature={public_url.split("signature=")[1]}' if signature else ''
            assert public_url == (f'{DEFAULT_API_URL}/v2/key-value-stores/someID/records/key{expected_signature}')

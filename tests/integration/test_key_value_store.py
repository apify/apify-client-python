from __future__ import annotations

from typing import TYPE_CHECKING

import impit

from integration.integration_test_utils import random_resource_name

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync


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

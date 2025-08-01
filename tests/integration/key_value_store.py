from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING

import httpx
from integration_test_utils import random_resource_name

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync


class TestKeyValueStoreSync:
    def test_key_value_store_should_create_public_keys_expiring_url_with_params(
        self, apify_client: ApifyClient
    ) -> None:
        created_store = apify_client.key_value_stores().get_or_create(name=random_resource_name('key-value-store'))

        store = apify_client.key_value_store(created_store['id'])
        keys_public_url = store.create_keys_public_url(
            expires_in_millis=2000,
            limit=10,
        )

        assert 'signature=' in keys_public_url
        assert 'limit=10' in keys_public_url

        httpx_client = httpx.Client()
        response = httpx_client.get(keys_public_url, timeout=5)
        assert response.status_code == 200

        time.sleep(3)

        # Assert that the request is now forbidden (expired signature)
        httpx_client = httpx.Client()
        response_after_expiry = httpx_client.get(keys_public_url, timeout=5)
        assert response_after_expiry.status_code == 403

        store.delete()
        assert apify_client.key_value_store(created_store['id']).get() is None

    def test_key_value_store_should_create_public_keys_non_expiring_url(self, apify_client: ApifyClient) -> None:
        created_store = apify_client.key_value_stores().get_or_create(name=random_resource_name('key-value-store'))

        store = apify_client.key_value_store(created_store['id'])
        keys_public_url = store.create_keys_public_url()

        assert 'signature=' in keys_public_url

        httpx_client = httpx.Client()
        response = httpx_client.get(keys_public_url, timeout=5)
        assert response.status_code == 200

        store.delete()
        assert apify_client.key_value_store(created_store['id']).get() is None


class TestKeyValueStoreAsync:
    async def test_key_value_store_should_create_public_keys_expiring_url_with_params(
        self, apify_client_async: ApifyClientAsync
    ) -> None:
        created_store = await apify_client_async.key_value_stores().get_or_create(
            name=random_resource_name('key-value-store')
        )

        store = apify_client_async.key_value_store(created_store['id'])
        keys_public_url = await store.create_keys_public_url(
            expires_in_millis=2000,
            limit=10,
        )

        assert 'signature=' in keys_public_url
        assert 'limit=10' in keys_public_url

        httpx_async_client = httpx.AsyncClient()
        response = await httpx_async_client.get(keys_public_url, timeout=5)
        assert response.status_code == 200

        await asyncio.sleep(3)

        # Assert that the request is now forbidden (expired signature)
        response_after_expiry = await httpx_async_client.get(keys_public_url, timeout=5)
        assert response_after_expiry.status_code == 403

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

        httpx_async_client = httpx.AsyncClient()
        response = await httpx_async_client.get(keys_public_url, timeout=5)
        assert response.status_code == 200

        await store.delete()
        assert await apify_client_async.key_value_store(created_store['id']).get() is None

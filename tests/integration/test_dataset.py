from __future__ import annotations

import impit

from integration.conftest import parametrized_api_urls
from integration.integration_test_utils import random_resource_name

from apify_client import ApifyClient, ApifyClientAsync
from apify_client.client import DEFAULT_API_URL


class TestDatasetSync:
    def test_dataset_should_create_public_items_expiring_url_with_params(self, apify_client: ApifyClient) -> None:
        created_dataset = apify_client.datasets().get_or_create(name=random_resource_name('dataset'))

        dataset = apify_client.dataset(created_dataset['id'])
        items_public_url = dataset.create_items_public_url(
            expires_in_secs=2000,
            limit=10,
            offset=0,
        )

        assert 'signature=' in items_public_url
        assert 'limit=10' in items_public_url
        assert 'offset=0' in items_public_url

        impit_client = impit.Client()
        response = impit_client.get(items_public_url, timeout=5)
        assert response.status_code == 200

        dataset.delete()
        assert apify_client.dataset(created_dataset['id']).get() is None

    def test_dataset_should_create_public_items_non_expiring_url(self, apify_client: ApifyClient) -> None:
        created_dataset = apify_client.datasets().get_or_create(name=random_resource_name('dataset'))

        dataset = apify_client.dataset(created_dataset['id'])
        items_public_url = dataset.create_items_public_url()

        assert 'signature=' in items_public_url

        impit_client = impit.Client()
        response = impit_client.get(items_public_url, timeout=5)
        assert response.status_code == 200

        dataset.delete()
        assert apify_client.dataset(created_dataset['id']).get() is None

    @parametrized_api_urls
    def test_public_url(self, api_token: str, api_url: str, api_public_url: str) -> None:
        apify_client = ApifyClient(token=api_token, api_url=api_url, api_public_url=api_public_url)
        created_store = apify_client.datasets().get_or_create(name=random_resource_name('key-value-store'))
        dataset = apify_client.dataset(created_store['id'])
        try:
            public_url = dataset.create_items_public_url()
            assert public_url == (
                f'{(api_public_url or DEFAULT_API_URL).strip("/")}/v2/datasets/'
                f'{created_store["id"]}/items?signature={public_url.split("signature=")[1]}'
            )
        finally:
            dataset.delete()

    def test_public_url_nonexistent_host(self, api_token: str) -> None:
        dataset_name = 'whatever'
        non_existent_url = 'http://10.0.88.214:8010'
        apify_client = ApifyClient(token=api_token, api_url=non_existent_url)
        kvs_client = apify_client.dataset(dataset_id=dataset_name)
        assert kvs_client._url() == f'{non_existent_url}/v2/datasets/{dataset_name}'
        assert kvs_client._url(public=True) == f'{DEFAULT_API_URL}/v2/datasets/{dataset_name}'


class TestDatasetAsync:
    async def test_dataset_should_create_public_items_expiring_url_with_params(
        self, apify_client_async: ApifyClientAsync
    ) -> None:
        created_dataset = await apify_client_async.datasets().get_or_create(name=random_resource_name('dataset'))

        dataset = apify_client_async.dataset(created_dataset['id'])
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
        assert await apify_client_async.dataset(created_dataset['id']).get() is None

    async def test_dataset_should_create_public_items_non_expiring_url(
        self, apify_client_async: ApifyClientAsync
    ) -> None:
        created_dataset = await apify_client_async.datasets().get_or_create(name=random_resource_name('dataset'))

        dataset = apify_client_async.dataset(created_dataset['id'])
        items_public_url = await dataset.create_items_public_url()

        assert 'signature=' in items_public_url

        impit_async_client = impit.AsyncClient()
        response = await impit_async_client.get(items_public_url, timeout=5)
        assert response.status_code == 200

        await dataset.delete()
        assert await apify_client_async.dataset(created_dataset['id']).get() is None

    @parametrized_api_urls
    async def test_public_url(self, api_token: str, api_url: str, api_public_url: str) -> None:
        apify_client = ApifyClientAsync(token=api_token, api_url=api_url, api_public_url=api_public_url)
        created_store = await apify_client.datasets().get_or_create(name=random_resource_name('key-value-store'))
        dataset = apify_client.dataset(created_store['id'])
        try:
            public_url = await dataset.create_items_public_url()
            assert public_url == (
                f'{(api_public_url or DEFAULT_API_URL).strip("/")}/v2/datasets/'
                f'{created_store["id"]}/items?signature={public_url.split("signature=")[1]}'
            )
        finally:
            await dataset.delete()

    def test_public_url_nonexistent_host(self, api_token: str) -> None:
        dataset_name = 'whatever'
        non_existent_url = 'http://10.0.88.214:8010'
        apify_client = ApifyClientAsync(token=api_token, api_url=non_existent_url)
        kvs_client = apify_client.dataset(dataset_id=dataset_name)
        assert kvs_client._url() == f'{non_existent_url}/v2/datasets/{dataset_name}'
        assert kvs_client._url(public=True) == f'{DEFAULT_API_URL}/v2/datasets/{dataset_name}'

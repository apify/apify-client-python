from __future__ import annotations

from typing import TYPE_CHECKING

import impit

from integration.integration_test_utils import random_resource_name

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync


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

from __future__ import annotations

import json
from unittest import mock
from unittest.mock import Mock

import impit
import pytest

from integration.integration_test_utils import TestDataset, parametrized_api_urls, random_resource_name

from apify_client import ApifyClient, ApifyClientAsync
from apify_client.client import DEFAULT_API_URL
from apify_client.errors import ApifyApiError

MOCKED_API_DATASET_RESPONSE = """{
  "data": {
    "id": "someID",
    "name": "name",
    "userId": "userId",
    "createdAt": "2025-09-11T08:48:51.806Z",
    "modifiedAt": "2025-09-11T08:48:51.806Z",
    "accessedAt": "2025-09-11T08:48:51.806Z",
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
        dataset = apify_client.dataset('someID')

        # Mock the API call to return predefined response
        mock_response = Mock()
        mock_response.json.return_value = json.loads(MOCKED_API_DATASET_RESPONSE)
        with mock.patch.object(apify_client.http_client, 'call', return_value=mock_response):
            public_url = dataset.create_items_public_url()
            assert public_url == (
                f'{(api_public_url or DEFAULT_API_URL).strip("/")}/v2/datasets/'
                f'someID/items?signature={public_url.split("signature=")[1]}'
            )

    def test_list_items_signature(self, apify_client: ApifyClient, test_dataset_of_another_user: TestDataset) -> None:
        dataset = apify_client.dataset(dataset_id=test_dataset_of_another_user.id)

        # Permission error without valid signature
        with pytest.raises(
            ApifyApiError,
            match=r"Insufficient permissions for the dataset. Make sure you're passing a "
            r'correct API token and that it has the required permissions.',
        ):
            dataset.list_items()

        # Dataset content retrieved with correct signature
        assert (
            test_dataset_of_another_user.expected_content
            == dataset.list_items(signature=test_dataset_of_another_user.signature).items
        )

    def test_iterate_items_signature(
        self, apify_client: ApifyClient, test_dataset_of_another_user: TestDataset
    ) -> None:
        dataset = apify_client.dataset(dataset_id=test_dataset_of_another_user.id)

        # Permission error without valid signature
        with pytest.raises(
            ApifyApiError,
            match=r"Insufficient permissions for the dataset. Make sure you're passing a "
            r'correct API token and that it has the required permissions.',
        ):
            list(dataset.iterate_items())

        # Dataset content retrieved with correct signature
        assert test_dataset_of_another_user.expected_content == list(
            dataset.iterate_items(signature=test_dataset_of_another_user.signature)
        )

    def test_get_items_as_bytes_signature(
        self, apify_client: ApifyClient, test_dataset_of_another_user: TestDataset
    ) -> None:
        dataset = apify_client.dataset(dataset_id=test_dataset_of_another_user.id)

        # Permission error without valid signature
        with pytest.raises(
            ApifyApiError,
            match=r"Insufficient permissions for the dataset. Make sure you're passing a "
            r'correct API token and that it has the required permissions.',
        ):
            dataset.get_items_as_bytes()

        # Dataset content retrieved with correct signature
        raw_data = dataset.get_items_as_bytes(signature=test_dataset_of_another_user.signature)
        assert test_dataset_of_another_user.expected_content == json.loads(raw_data.decode('utf-8'))


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
        self, apify_client_async: ApifyClientAsync, test_dataset_of_another_user: TestDataset
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
        self, apify_client_async: ApifyClientAsync, test_dataset_of_another_user: TestDataset
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
        self, apify_client_async: ApifyClientAsync, test_dataset_of_another_user: TestDataset
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

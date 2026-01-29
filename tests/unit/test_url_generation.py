"""Unit tests for URL generation logic.

Tests public URL generation for datasets and key-value stores using mocks.
These tests verify URL construction with various API URL configurations.
"""

from __future__ import annotations

import json
from unittest import mock
from unittest.mock import Mock

import pytest

from apify_client import ApifyClient, ApifyClientAsync
from apify_client._consts import DEFAULT_API_URL
from apify_client._utils import create_hmac_signature, create_storage_content_signature

# ============================================================================
# Test data and helpers
# ============================================================================

MOCKED_DATASET_RESPONSE = """{
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

MOCKED_KVS_ID = 'someID'


def _get_mocked_kvs_response(signing_key: str | None = None) -> Mock:
    """Create a mock API response for key-value store."""
    response_data = {
        'data': {
            'id': MOCKED_KVS_ID,
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


# Parametrize decorator for testing various API URL and public URL combinations
parametrized_api_urls = pytest.mark.parametrize(
    ('api_url', 'api_public_url'),
    [
        ('https://api.apify.com', 'https://api.apify.com'),
        ('https://api.apify.com', None),
        ('https://api.apify.com', 'https://custom-public-url.com'),
        ('https://api.apify.com', 'https://custom-public-url.com/with/custom/path'),
        ('https://api.apify.com', 'https://custom-public-url.com/with/custom/path/'),
        ('http://10.0.88.214:8010', 'https://api.apify.com'),
        ('http://10.0.88.214:8010', None),
    ],
)


# ============================================================================
# Dataset URL generation tests
# ============================================================================


@parametrized_api_urls
def test_dataset_public_url_sync(api_url: str, api_public_url: str | None) -> None:
    """Test public URL generation for datasets with sync client."""
    client = ApifyClient(token='dummy-token', api_url=api_url, api_public_url=api_public_url)
    dataset = client.dataset('someID')

    mock_response = Mock()
    mock_response.json.return_value = json.loads(MOCKED_DATASET_RESPONSE)

    with mock.patch.object(client._http_client, 'call', return_value=mock_response):
        public_url = dataset.create_items_public_url()

        assert public_url == (
            f'{(api_public_url or DEFAULT_API_URL).strip("/")}/v2/datasets/'
            f'someID/items?signature={public_url.split("signature=")[1]}'
        )


@parametrized_api_urls
async def test_dataset_public_url_async(api_url: str, api_public_url: str | None) -> None:
    """Test public URL generation for datasets with async client."""
    client = ApifyClientAsync(token='dummy-token', api_url=api_url, api_public_url=api_public_url)
    dataset = client.dataset('someID')

    mock_response = Mock()
    mock_response.json.return_value = json.loads(MOCKED_DATASET_RESPONSE)

    with mock.patch.object(client._http_client, 'call', return_value=mock_response):
        public_url = await dataset.create_items_public_url()

        assert public_url == (
            f'{(api_public_url or DEFAULT_API_URL).strip("/")}/v2/datasets/'
            f'someID/items?signature={public_url.split("signature=")[1]}'
        )


# ============================================================================
# Key-value store URL generation tests
# ============================================================================


@pytest.mark.parametrize('signing_key', [None, 'custom-signing-key'])
@parametrized_api_urls
def test_kvs_public_url_sync(api_url: str, api_public_url: str | None, signing_key: str | None) -> None:
    """Test public URL generation for key-value stores with sync client."""
    client = ApifyClient(token='dummy-token', api_url=api_url, api_public_url=api_public_url)
    kvs = client.key_value_store(MOCKED_KVS_ID)

    with mock.patch.object(client._http_client, 'call', return_value=_get_mocked_kvs_response(signing_key=signing_key)):
        public_url = kvs.create_keys_public_url()

        if signing_key:
            signature_value = create_storage_content_signature(
                resource_id=MOCKED_KVS_ID, url_signing_secret_key=signing_key
            )
            expected_signature = f'?signature={signature_value}'
        else:
            expected_signature = ''

        assert public_url == (
            f'{(api_public_url or DEFAULT_API_URL).strip("/")}/v2/key-value-stores/'
            f'{MOCKED_KVS_ID}/keys{expected_signature}'
        )


@pytest.mark.parametrize('signing_key', [None, 'custom-signing-key'])
@parametrized_api_urls
async def test_kvs_public_url_async(api_url: str, api_public_url: str | None, signing_key: str | None) -> None:
    """Test public URL generation for key-value stores with async client."""
    client = ApifyClientAsync(token='dummy-token', api_url=api_url, api_public_url=api_public_url)
    kvs = client.key_value_store(MOCKED_KVS_ID)

    with mock.patch.object(client._http_client, 'call', return_value=_get_mocked_kvs_response(signing_key=signing_key)):
        public_url = await kvs.create_keys_public_url()

        if signing_key:
            signature_value = create_storage_content_signature(
                resource_id=MOCKED_KVS_ID, url_signing_secret_key=signing_key
            )
            expected_signature = f'?signature={signature_value}'
        else:
            expected_signature = ''

        assert public_url == (
            f'{(api_public_url or DEFAULT_API_URL).strip("/")}/v2/key-value-stores/'
            f'{MOCKED_KVS_ID}/keys{expected_signature}'
        )


@pytest.mark.parametrize('signing_key', [None, 'custom-signing-key'])
@parametrized_api_urls
def test_kvs_record_public_url_sync(api_url: str, api_public_url: str | None, signing_key: str | None) -> None:
    """Test record public URL generation for key-value stores with sync client."""
    client = ApifyClient(token='dummy-token', api_url=api_url, api_public_url=api_public_url)
    key = 'some_key'
    kvs = client.key_value_store(MOCKED_KVS_ID)

    with mock.patch.object(client._http_client, 'call', return_value=_get_mocked_kvs_response(signing_key=signing_key)):
        public_url = kvs.get_record_public_url(key=key)

        expected_signature = f'?signature={create_hmac_signature(signing_key, key)}' if signing_key else ''
        assert public_url == (
            f'{(api_public_url or DEFAULT_API_URL).strip("/")}/v2/key-value-stores/{MOCKED_KVS_ID}/'
            f'records/{key}{expected_signature}'
        )


@pytest.mark.parametrize('signing_key', [None, 'custom-signing-key'])
@parametrized_api_urls
async def test_kvs_record_public_url_async(api_url: str, api_public_url: str | None, signing_key: str | None) -> None:
    """Test record public URL generation for key-value stores with async client."""
    client = ApifyClientAsync(token='dummy-token', api_url=api_url, api_public_url=api_public_url)
    key = 'some_key'
    kvs = client.key_value_store(MOCKED_KVS_ID)

    with mock.patch.object(client._http_client, 'call', return_value=_get_mocked_kvs_response(signing_key=signing_key)):
        public_url = await kvs.get_record_public_url(key=key)

        expected_signature = f'?signature={create_hmac_signature(signing_key, key)}' if signing_key else ''
        assert public_url == (
            f'{(api_public_url or DEFAULT_API_URL).strip("/")}/v2/key-value-stores/{MOCKED_KVS_ID}/'
            f'records/{key}{expected_signature}'
        )

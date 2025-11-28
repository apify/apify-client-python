import json
import os
import secrets
from collections.abc import Generator

import pytest
from apify_shared.utils import create_hmac_signature, create_storage_content_signature

from .integration_test_utils import TestDataset, TestKvs
from apify_client import ApifyClient, ApifyClientAsync

TOKEN_ENV_VAR = 'APIFY_TEST_USER_API_TOKEN'
TOKEN_ENV_VAR_2 = 'APIFY_TEST_USER_2_API_TOKEN'
API_URL_ENV_VAR = 'APIFY_INTEGRATION_TESTS_API_URL'


def crypto_random_object_id(length: int = 17) -> str:
    """Generate a random object ID."""
    chars = 'abcdefghijklmnopqrstuvwxyzABCEDFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(secrets.choice(chars) for _ in range(length))


@pytest.fixture(scope='session')
def api_token() -> str:
    token = os.getenv(TOKEN_ENV_VAR)
    if not token:
        raise RuntimeError(f'{TOKEN_ENV_VAR} environment variable is missing, cannot run tests!')
    return token


@pytest.fixture(scope='session')
def api_token_2() -> str:
    """API token for the second test user for storage permission tests."""
    token = os.getenv(TOKEN_ENV_VAR_2)
    if not token:
        raise RuntimeError(f'{TOKEN_ENV_VAR_2} environment variable is missing, cannot run permission tests!')
    return token


@pytest.fixture
def apify_client(api_token: str) -> ApifyClient:
    return ApifyClient(api_token, api_url=os.getenv(API_URL_ENV_VAR))


# This fixture can't be session-scoped,
# because then you start getting `RuntimeError: Event loop is closed` errors,
# because `impit.AsyncClient` in `ApifyClientAsync` tries to reuse the same event loop across requests,
# but `pytest-asyncio` closes the event loop after each test,
# and uses a new one for the next test.
@pytest.fixture
def apify_client_async(api_token: str) -> ApifyClientAsync:
    return ApifyClientAsync(api_token, api_url=os.getenv(API_URL_ENV_VAR))


@pytest.fixture(scope='session')
def test_dataset_of_another_user(api_token_2: str) -> Generator[TestDataset]:
    """Pre-existing named dataset of another test user with restricted access."""
    client = ApifyClient(api_token_2, api_url=os.getenv(API_URL_ENV_VAR))

    dataset_name = f'API-test-permissions-{crypto_random_object_id()}'
    dataset = client.datasets().get_or_create(name=dataset_name)
    dataset_client = client.dataset(dataset_id=dataset['id'])
    expected_content = [{'item1': 1, 'item2': 2, 'item3': 3}, {'item1': 4, 'item2': 5, 'item3': 6}]

    # Push data to dataset
    dataset_client.push_items(json.dumps(expected_content))

    # Generate signature for the test
    signature = create_storage_content_signature(
        resource_id=dataset['id'], url_signing_secret_key=dataset['urlSigningSecretKey']
    )

    yield TestDataset(
        id=dataset['id'],
        signature=signature,
        expected_content=[{'item1': 1, 'item2': 2, 'item3': 3}, {'item1': 4, 'item2': 5, 'item3': 6}],
    )

    dataset_client.delete()


@pytest.fixture(scope='session')
def test_kvs_of_another_user(api_token_2: str) -> Generator[TestKvs]:
    """Pre-existing named key value store of another test user with restricted access."""
    client = ApifyClient(api_token_2, api_url=os.getenv(API_URL_ENV_VAR))

    kvs_name = f'API-test-permissions-{crypto_random_object_id()}'
    kvs = client.key_value_stores().get_or_create(name=kvs_name)
    kvs_client = client.key_value_store(key_value_store_id=kvs['id'])
    expected_content = {'key1': 1, 'key2': 2, 'key3': 3}

    # Push data to kvs
    for key, value in expected_content.items():
        kvs_client.set_record(key, value)

    # Generate signature for the test
    signature = create_storage_content_signature(
        resource_id=kvs['id'], url_signing_secret_key=kvs['urlSigningSecretKey']
    )

    yield TestKvs(
        id=kvs['id'],
        signature=signature,
        expected_content=expected_content,
        keys_signature={key: create_hmac_signature(kvs['urlSigningSecretKey'], key) for key in expected_content},
    )

    kvs_client.delete()

"""Pytest configuration and fixtures for integration tests.

Provides sync/async client parametrization and shared test fixtures.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from typing import TYPE_CHECKING, Any, TypeVar, overload

import pytest

from .utils import DatasetFixture, KvsFixture, get_crypto_random_object_id
from apify_client import ApifyClient, ApifyClientAsync
from apify_client._utils import create_hmac_signature, create_storage_content_signature

if TYPE_CHECKING:
    from collections.abc import Coroutine, Generator

# Environment variable names for test configuration
TOKEN_ENV_VAR = 'APIFY_TEST_USER_API_TOKEN'
TOKEN_ENV_VAR_2 = 'APIFY_TEST_USER_2_API_TOKEN'
API_URL_ENV_VAR = 'APIFY_INTEGRATION_TESTS_API_URL'

T = TypeVar('T')


# ============================================================================
# Helper functions for sync/async test compatibility
# ============================================================================


@overload
async def maybe_await(value: Coroutine[Any, Any, T]) -> T: ...


@overload
async def maybe_await(value: T) -> T: ...


async def maybe_await(value: T | Coroutine[Any, Any, T]) -> T:
    """Await coroutines, pass through other values.

    Enables unified test code for both sync and async clients:
        result = await maybe_await(client.datasets().list())
    """
    if hasattr(value, '__await__'):
        return await value  # type: ignore[misc,return-value]
    return value


async def maybe_sleep(seconds: float, *, is_async: bool) -> None:
    """Sleep using asyncio or time.sleep based on client type."""
    if is_async:
        await asyncio.sleep(seconds)
    else:
        time.sleep(seconds)  # noqa: ASYNC251


# ============================================================================
# Session-scoped fixtures (created once per test session)
# ============================================================================


@pytest.fixture(scope='session')
def api_token() -> str:
    """Primary test user API token."""
    token = os.getenv(TOKEN_ENV_VAR)
    if not token:
        raise RuntimeError(f'{TOKEN_ENV_VAR} environment variable is missing, cannot run tests!')
    return token


@pytest.fixture(scope='session')
def api_token_2() -> str:
    """Secondary test user API token for permission tests."""
    token = os.getenv(TOKEN_ENV_VAR_2)
    if not token:
        raise RuntimeError(f'{TOKEN_ENV_VAR_2} environment variable is missing, cannot run permission tests!')
    return token


@pytest.fixture(scope='session')
def test_dataset_of_another_user(api_token_2: str) -> Generator[DatasetFixture]:
    """Dataset owned by secondary user for testing cross-user access restrictions."""
    client = ApifyClient(api_token_2, api_url=os.getenv(API_URL_ENV_VAR))

    # Create dataset with test data
    dataset_name = f'API-test-permissions-{get_crypto_random_object_id()}'
    dataset = client.datasets().get_or_create(name=dataset_name)
    dataset_client = client.dataset(dataset_id=dataset.id)
    expected_content = [{'item1': 1, 'item2': 2, 'item3': 3}, {'item1': 4, 'item2': 5, 'item3': 6}]
    dataset_client.push_items(json.dumps(expected_content))

    # Generate signature for authenticated access
    assert dataset.url_signing_secret_key is not None
    signature = create_storage_content_signature(
        resource_id=dataset.id,
        url_signing_secret_key=dataset.url_signing_secret_key,
    )

    yield DatasetFixture(
        id=dataset.id,
        signature=signature,
        expected_content=expected_content,
    )

    dataset_client.delete()


@pytest.fixture(scope='session')
def test_kvs_of_another_user(api_token_2: str) -> Generator[KvsFixture]:
    """Key-value store owned by secondary user for testing cross-user access restrictions."""
    client = ApifyClient(api_token_2, api_url=os.getenv(API_URL_ENV_VAR))

    # Create key-value store with test data
    kvs_name = f'API-test-permissions-{get_crypto_random_object_id()}'
    kvs = client.key_value_stores().get_or_create(name=kvs_name)
    kvs_client = client.key_value_store(key_value_store_id=kvs.id)
    expected_content = {'key1': 1, 'key2': 2, 'key3': 3}
    for key, value in expected_content.items():
        kvs_client.set_record(key, value)

    # Generate signatures for authenticated access
    signature = create_storage_content_signature(
        resource_id=kvs.id,
        url_signing_secret_key=kvs.url_signing_secret_key or '',
    )

    yield KvsFixture(
        id=kvs.id,
        signature=signature,
        expected_content=expected_content,
        keys_signature={key: create_hmac_signature(kvs.url_signing_secret_key or '', key) for key in expected_content},
    )

    kvs_client.delete()


# ============================================================================
# Function-scoped fixtures (created for each test)
# ============================================================================


@pytest.fixture
def apify_client(api_token: str) -> ApifyClient:
    """Sync Apify client instance."""
    return ApifyClient(api_token, api_url=os.getenv(API_URL_ENV_VAR))


@pytest.fixture
def apify_client_async(api_token: str) -> ApifyClientAsync:
    """Async Apify client instance."""
    return ApifyClientAsync(api_token, api_url=os.getenv(API_URL_ENV_VAR))


@pytest.fixture(params=['sync', 'async'])
def client_type(request: pytest.FixtureRequest) -> str:
    """Parametrize tests to run with both sync and async clients."""
    return request.param


@pytest.fixture
def client(
    client_type: str,
    apify_client: ApifyClient,
    apify_client_async: ApifyClientAsync,
) -> ApifyClient | ApifyClientAsync:
    """Return sync or async client based on parametrization."""
    return apify_client if client_type == 'sync' else apify_client_async


@pytest.fixture
def is_async(client_type: str) -> bool:
    """True if current test is using async client."""
    return client_type == 'async'

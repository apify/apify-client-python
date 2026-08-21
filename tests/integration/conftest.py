from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from .._utils import (
    API_URL_ENV_VAR,
    TOKEN_ENV_VAR,
    TOKEN_ENV_VAR_2,
    DatasetFixture,
    KvsFixture,
    get_crypto_random_object_id,
)
from apify_client import ApifyClient, ApifyClientAsync
from apify_client._consts import DEFAULT_API_URL
from apify_client._utils.crypto import create_hmac_signature, create_storage_content_signature
from apify_client.http_clients import (
    HttpClient,
    HttpClientAsync,
    Httpx2HttpClient,
    Httpx2HttpClientAsync,
    ImpitHttpClient,
    ImpitHttpClientAsync,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator


@dataclass(frozen=True)
class HttpClientClasses:
    """Synchronous and asynchronous variants of a built-in HTTP client."""

    sync: type[HttpClient]
    async_: type[HttpClientAsync]


DEFAULT_HTTP_CLIENT_CLASSES = HttpClientClasses(sync=ImpitHttpClient, async_=ImpitHttpClientAsync)
"""HTTP clients the live-API suite runs with unless a test asks for another transport."""

ALL_HTTP_CLIENT_CLASSES = [
    pytest.param(DEFAULT_HTTP_CLIENT_CLASSES, id='impit'),
    pytest.param(HttpClientClasses(sync=Httpx2HttpClient, async_=Httpx2HttpClientAsync), id='httpx2'),
]
"""Every built-in HTTP client, for tests that exercise transport behavior rather than an API resource."""


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
    api_url = os.getenv(API_URL_ENV_VAR) or DEFAULT_API_URL
    client = ApifyClient(api_token_2, api_url=api_url)

    # Create dataset with test data
    dataset_name = f'API-test-permissions-{get_crypto_random_object_id()}'
    dataset = client.datasets().get_or_create(name=dataset_name)
    dataset_client = client.dataset(dataset_id=dataset.id)
    expected_content = [{'item1': 1, 'item2': 2, 'item3': 3}, {'item1': 4, 'item2': 5, 'item3': 6}]
    dataset_client.push_items(json.dumps(expected_content))

    # Generate signature for authenticated access
    assert dataset.url_signing_secret_key is not None
    signature = create_storage_content_signature(
        dataset.id,
        dataset.url_signing_secret_key,
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
    api_url = os.getenv(API_URL_ENV_VAR) or DEFAULT_API_URL
    client = ApifyClient(api_token_2, api_url=api_url)

    # Create key-value store with test data
    kvs_name = f'API-test-permissions-{get_crypto_random_object_id()}'
    kvs = client.key_value_stores().get_or_create(name=kvs_name)
    kvs_client = client.key_value_store(key_value_store_id=kvs.id)
    expected_content = {'key1': 1, 'key2': 2, 'key3': 3}
    for key, value in expected_content.items():
        kvs_client.set_record(key, value)

    # Generate signatures for authenticated access
    signature = create_storage_content_signature(
        kvs.id,
        kvs.url_signing_secret_key or '',
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
def http_client_classes(request: pytest.FixtureRequest) -> HttpClientClasses:
    """Return the sync and async classes of the HTTP client the test runs with.

    Defaults to Impit so the live-API suite isn't multiplied by every transport. A transport-level test opts into
    the full matrix with `@pytest.mark.parametrize('http_client_classes', ALL_HTTP_CLIENT_CLASSES, indirect=True)`.
    """
    if not hasattr(request, 'param'):
        return DEFAULT_HTTP_CLIENT_CLASSES

    assert isinstance(request.param, HttpClientClasses)
    return request.param


@pytest.fixture(params=['sync', 'async'])
def client_type(request: pytest.FixtureRequest) -> str:
    """Parametrize tests to run with both sync and async clients."""
    return request.param


@pytest.fixture
async def client(
    client_type: str,
    api_token: str,
    http_client_classes: HttpClientClasses,
) -> AsyncGenerator[ApifyClient | ApifyClientAsync]:
    """Return each sync/async and HTTP client implementation combination."""
    api_url = os.getenv(API_URL_ENV_VAR) or DEFAULT_API_URL
    if client_type == 'sync':
        http_client = http_client_classes.sync()
        yield ApifyClient.with_custom_http_client(
            api_token,
            api_url=api_url,
            http_client=http_client,
        )
        http_client.close()
        return

    http_client_async = http_client_classes.async_()
    yield ApifyClientAsync.with_custom_http_client(
        api_token,
        api_url=api_url,
        http_client=http_client_async,
    )
    await http_client_async.aclose()


@pytest.fixture
def is_async(client_type: str) -> bool:
    """True if current test is using async client."""
    return client_type == 'async'

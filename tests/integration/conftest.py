from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING

import pytest

from .._utils import (
    TOKEN_ENV_VAR,
    TOKEN_ENV_VAR_2,
    ClientType,
    DatasetFixture,
    HttpClientClasses,
    KvsFixture,
    get_api_url,
    get_crypto_random_object_id,
    open_apify_client,
)
from apify_client import ApifyClient, ApifyClientAsync
from apify_client._utils.crypto import create_hmac_signature, create_storage_content_signature
from apify_client.http_clients import (
    Httpx2HttpClient,
    Httpx2HttpClientAsync,
    ImpitHttpClient,
    ImpitHttpClientAsync,
)
from apify_client.http_compressors import (
    BrotliHttpCompressor,
    GzipHttpCompressor,
    HttpCompressor,
    ZstdHttpCompressor,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator


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
    api_url = get_api_url()
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
    api_url = get_api_url()
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


@pytest.fixture(
    params=[
        pytest.param(HttpClientClasses(sync=ImpitHttpClient, async_=ImpitHttpClientAsync), id='impit'),
        pytest.param(HttpClientClasses(sync=Httpx2HttpClient, async_=Httpx2HttpClientAsync), id='httpx2'),
    ]
)
def http_client_classes(request: pytest.FixtureRequest) -> HttpClientClasses:
    """Return the sync and async classes of the HTTP client the test runs with, once per built-in transport."""
    classes = request.param
    assert isinstance(classes, HttpClientClasses)
    return classes


@pytest.fixture(params=['sync', 'async'])
def client_type(request: pytest.FixtureRequest) -> ClientType:
    """Parametrize tests to run with both sync and async clients."""
    return request.param


@pytest.fixture
async def client(
    client_type: ClientType,
    api_token: str,
    http_client_classes: HttpClientClasses,
) -> AsyncGenerator[ApifyClient | ApifyClientAsync]:
    """Return each sync/async and HTTP client implementation combination."""
    async with open_apify_client(api_token, client_type, http_client_classes) as client:
        yield client


@pytest.fixture(
    params=[
        pytest.param(GzipHttpCompressor, id='gzip'),
        pytest.param(BrotliHttpCompressor, id='brotli'),
        pytest.param(ZstdHttpCompressor, id='zstd'),
    ]
)
def http_compressor_class(request: pytest.FixtureRequest) -> type[HttpCompressor]:
    """Return the class of the request-body compressor the test runs with, once per built-in compressor."""
    return request.param


@pytest.fixture
async def compressing_client(
    client_type: ClientType,
    api_token: str,
    http_client_classes: HttpClientClasses,
    http_compressor_class: type[HttpCompressor],
) -> AsyncGenerator[ApifyClient | ApifyClientAsync]:
    """Return each sync/async, HTTP client, and compressor combination, compressing request bodies explicitly."""
    async with open_apify_client(api_token, client_type, http_client_classes, http_compressor_class()) as client:
        yield client


@pytest.fixture
def is_async(client_type: ClientType) -> bool:
    """True if current test is using async client."""
    return client_type == 'async'

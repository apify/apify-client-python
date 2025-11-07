import os

import pytest

from .integration_test_utils import TestDataset, TestKvs
from apify_client import ApifyClient, ApifyClientAsync

TOKEN_ENV_VAR = 'APIFY_TEST_USER_API_TOKEN'
API_URL_ENV_VAR = 'APIFY_INTEGRATION_TESTS_API_URL'


@pytest.fixture
def api_token() -> str:
    token = os.getenv(TOKEN_ENV_VAR)
    if not token:
        raise RuntimeError(f'{TOKEN_ENV_VAR} environment variable is missing, cannot run tests!')
    return token


@pytest.fixture
def apify_client(api_token: str) -> ApifyClient:
    api_url = os.getenv(API_URL_ENV_VAR)
    return ApifyClient(api_token, api_url=api_url)


# This fixture can't be session-scoped,
# because then you start getting `RuntimeError: Event loop is closed` errors,
# because `impit.AsyncClient` in `ApifyClientAsync` tries to reuse the same event loop across requests,
# but `pytest-asyncio` closes the event loop after each test,
# and uses a new one for the next test.
@pytest.fixture
def apify_client_async(api_token: str) -> ApifyClientAsync:
    api_url = os.getenv(API_URL_ENV_VAR)
    return ApifyClientAsync(api_token, api_url=api_url)


@pytest.fixture
def test_dataset_of_another_user() -> TestDataset:
    """Pre-existing dataset of another test user with restricted access."""
    return TestDataset(
        id='InrsNvJNGwJMFAR2l',
        signature='MC4wLjFGbVN3UjB5T0xvMU1hU0lFQjZCMQ',
        expected_content=[{'item1': 1, 'item2': 2, 'item3': 3}, {'item1': 4, 'item2': 5, 'item3': 6}],
    )


@pytest.fixture
def test_kvs_of_another_user() -> TestKvs:
    """Pre-existing key value store of another test user with restricted access."""
    return TestKvs(
        id='0SWREKM4yzKnpQRGA',
        signature='MC4wLjVKVmlMSVpDNEhaazg1Z1VXTnBP',
        expected_content={'key1': 1, 'key2': 2, 'key3': 3},
        keys_signature={
            'key1': 'qrQL9pHpiok99v9kWhKx',
            'key2': '1BhGTfsLvpsF8aPiIgoBt',
            'key3': 'rPPqxmTNcxvvpvO0Bx5s',
        },
    )

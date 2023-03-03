import os

import pytest

from apify_client import ApifyClient, ApifyClientAsync

TOKEN_ENV_VAR = 'APIFY_TEST_USER_API_TOKEN'
API_URL_ENV_VAR = 'APIFY_INTEGRATION_TESTS_API_URL'


@pytest.fixture
def apify_client() -> ApifyClient:
    api_token = os.getenv(TOKEN_ENV_VAR)
    api_url = os.getenv(API_URL_ENV_VAR)

    if not api_token:
        raise RuntimeError(f'{TOKEN_ENV_VAR} environment variable is missing, cannot run tests!')

    return ApifyClient(api_token, api_url=api_url)


# This fixture can't be session-scoped,
# because then you start getting `RuntimeError: Event loop is closed` errors,
# because `httpx.AsyncClient` in `ApifyClientAsync` tries to reuse the same event loop across requests,
# but `pytest-asyncio` closes the event loop after each test,
# and uses a new one for the next test.
@pytest.fixture
def apify_client_async() -> ApifyClientAsync:
    api_token = os.getenv(TOKEN_ENV_VAR)
    api_url = os.getenv(API_URL_ENV_VAR)

    if not api_token:
        raise RuntimeError(f'{TOKEN_ENV_VAR} environment variable is missing, cannot run tests!')

    return ApifyClientAsync(api_token, api_url=api_url)

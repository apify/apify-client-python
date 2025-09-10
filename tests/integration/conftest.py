import os

import pytest

from apify_client import ApifyClient, ApifyClientAsync

TOKEN_ENV_VAR = 'APIFY_TEST_USER_API_TOKEN'
API_URL_ENV_VAR = 'APIFY_INTEGRATION_TESTS_API_URL'

parametrized_api_urls = pytest.mark.parametrize(
    ('api_url', 'api_public_url'),
    [
        ('https://api.apify.com', 'https://api.apify.com'),
        ('https://api.apify.com', None),
        ('https://api.apify.com', 'https://custom-public-url.com'),
        ('https://api.apify.com', 'https://custom-public-url.com/with/custom/path'),
        ('https://api.apify.com', 'https://custom-public-url.com/with/custom/path/'),
    ],
)


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

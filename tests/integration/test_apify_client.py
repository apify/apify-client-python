"""Unified tests for apify client (sync + async)."""

from __future__ import annotations

import os

from .._utils import API_URL_ENV_VAR, maybe_await
from apify_client import ApifyClient, ApifyClientAsync
from apify_client._consts import DEFAULT_API_URL
from apify_client._models import UserPrivateInfo, UserPublicInfo
from apify_client.http_clients import ImpitHttpClient, ImpitHttpClientAsync


async def test_apify_client(client: ApifyClient | ApifyClientAsync) -> None:
    """Test basic apify client functionality."""
    user_client = client.user('me')
    me = await maybe_await(user_client.get())
    assert isinstance(me, UserPrivateInfo | UserPublicInfo)
    assert me.username is not None


async def test_plain_constructor_reaches_the_api(client_type: str, api_token: str) -> None:
    """The plain constructor - the form users write - reaches the API with the HTTP client it builds itself.

    The rest of the suite injects a transport through `with_custom_http_client` to run against every built-in
    implementation, which leaves the default construction path untested against the live API.
    """
    api_url = os.getenv(API_URL_ENV_VAR) or DEFAULT_API_URL

    if client_type == 'sync':
        sync_client = ApifyClient(api_token, api_url=api_url)
        assert isinstance(sync_client.http_client, ImpitHttpClient)
        assert sync_client.user('me').get() is not None
        sync_client.http_client.close()
        return

    async_client = ApifyClientAsync(api_token, api_url=api_url)
    assert isinstance(async_client.http_client, ImpitHttpClientAsync)
    assert await async_client.user('me').get() is not None
    await async_client.http_client.aclose()

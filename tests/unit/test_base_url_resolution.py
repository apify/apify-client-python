from __future__ import annotations

from typing import TYPE_CHECKING

from apify_client import ApifyClient, ApifyClientAsync
from apify_client._consts import DEFAULT_API_PUBLIC_URL, DEFAULT_API_URL
from apify_client.http_clients import ImpitHttpClient, ImpitHttpClientAsync

if TYPE_CHECKING:
    import pytest

# ============================================================================
# API base URL (`APIFY_API_BASE_URL`) — criteria 1-4
# ============================================================================


def test_api_url_defaults_to_production_when_unset_sync(monkeypatch: pytest.MonkeyPatch) -> None:
    """No env var and no argument: resolves to the production default."""
    monkeypatch.delenv('APIFY_API_BASE_URL', raising=False)
    client = ApifyClient(token='dummy-token')
    assert client._base_url == f'{DEFAULT_API_URL}/v2'


async def test_api_url_defaults_to_production_when_unset_async(monkeypatch: pytest.MonkeyPatch) -> None:
    """No env var and no argument: resolves to the production default (async)."""
    monkeypatch.delenv('APIFY_API_BASE_URL', raising=False)
    client = ApifyClientAsync(token='dummy-token')
    assert client._base_url == f'{DEFAULT_API_URL}/v2'


def test_api_url_env_var_used_when_no_argument_sync(monkeypatch: pytest.MonkeyPatch) -> None:
    """`APIFY_API_BASE_URL` is used when no explicit `api_url` argument is given."""
    monkeypatch.setenv('APIFY_API_BASE_URL', 'http://localhost:8080')
    client = ApifyClient(token='dummy-token')
    assert client._base_url == 'http://localhost:8080/v2'


async def test_api_url_env_var_used_when_no_argument_async(monkeypatch: pytest.MonkeyPatch) -> None:
    """`APIFY_API_BASE_URL` is used when no explicit `api_url` argument is given (async)."""
    monkeypatch.setenv('APIFY_API_BASE_URL', 'http://localhost:8080')
    client = ApifyClientAsync(token='dummy-token')
    assert client._base_url == 'http://localhost:8080/v2'


def test_explicit_api_url_wins_over_env_var_sync(monkeypatch: pytest.MonkeyPatch) -> None:
    """An explicit `api_url` argument wins over `APIFY_API_BASE_URL`."""
    monkeypatch.setenv('APIFY_API_BASE_URL', 'http://localhost:8080')
    client = ApifyClient(token='dummy-token', api_url='http://example.test')
    assert client._base_url == 'http://example.test/v2'


async def test_explicit_api_url_wins_over_env_var_async(monkeypatch: pytest.MonkeyPatch) -> None:
    """An explicit `api_url` argument wins over `APIFY_API_BASE_URL` (async)."""
    monkeypatch.setenv('APIFY_API_BASE_URL', 'http://localhost:8080')
    client = ApifyClientAsync(token='dummy-token', api_url='http://example.test')
    assert client._base_url == 'http://example.test/v2'


def test_api_url_custom_port_from_env_needs_no_special_handling(monkeypatch: pytest.MonkeyPatch) -> None:
    """A custom port supplied via the env var works with no special handling."""
    monkeypatch.setenv('APIFY_API_BASE_URL', 'http://localhost:9999')
    client = ApifyClient(token='dummy-token')
    assert client._base_url == 'http://localhost:9999/v2'


# ============================================================================
# Public API base URL (`APIFY_API_PUBLIC_BASE_URL`) — criteria 5-8
# ============================================================================


def test_api_public_url_defaults_to_production_when_unset_sync(monkeypatch: pytest.MonkeyPatch) -> None:
    """No env var and no argument: the public base URL resolves to the production default."""
    monkeypatch.delenv('APIFY_API_PUBLIC_BASE_URL', raising=False)
    client = ApifyClient(token='dummy-token')
    assert client._public_base_url == f'{DEFAULT_API_PUBLIC_URL}/v2'


async def test_api_public_url_defaults_to_production_when_unset_async(monkeypatch: pytest.MonkeyPatch) -> None:
    """No env var and no argument: the public base URL resolves to the production default (async)."""
    monkeypatch.delenv('APIFY_API_PUBLIC_BASE_URL', raising=False)
    client = ApifyClientAsync(token='dummy-token')
    assert client._public_base_url == f'{DEFAULT_API_PUBLIC_URL}/v2'


def test_api_public_url_env_var_used_when_no_argument(monkeypatch: pytest.MonkeyPatch) -> None:
    """`APIFY_API_PUBLIC_BASE_URL` is used when no explicit `api_public_url` argument is given."""
    monkeypatch.setenv('APIFY_API_PUBLIC_BASE_URL', 'http://localhost:8080')
    client = ApifyClient(token='dummy-token')
    assert client._public_base_url == 'http://localhost:8080/v2'


def test_explicit_api_public_url_wins_over_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    """An explicit `api_public_url` argument wins over `APIFY_API_PUBLIC_BASE_URL`."""
    monkeypatch.setenv('APIFY_API_PUBLIC_BASE_URL', 'http://localhost:8080')
    client = ApifyClient(token='dummy-token', api_public_url='http://example.test')
    assert client._public_base_url == 'http://example.test/v2'


def test_api_base_and_public_base_env_vars_are_independent(monkeypatch: pytest.MonkeyPatch) -> None:
    """Setting only `APIFY_API_BASE_URL` leaves the public base URL at its default."""
    monkeypatch.delenv('APIFY_API_PUBLIC_BASE_URL', raising=False)
    monkeypatch.setenv('APIFY_API_BASE_URL', 'http://localhost:8080')
    client = ApifyClient(token='dummy-token')
    assert client._base_url == 'http://localhost:8080/v2'
    assert client._public_base_url == f'{DEFAULT_API_PUBLIC_URL}/v2'


def test_api_base_and_public_base_env_vars_are_independent_other_direction(monkeypatch: pytest.MonkeyPatch) -> None:
    """Setting only `APIFY_API_PUBLIC_BASE_URL` leaves the API base URL at its default."""
    monkeypatch.delenv('APIFY_API_BASE_URL', raising=False)
    monkeypatch.setenv('APIFY_API_PUBLIC_BASE_URL', 'http://localhost:8080')
    client = ApifyClient(token='dummy-token')
    assert client._public_base_url == 'http://localhost:8080/v2'
    assert client._base_url == f'{DEFAULT_API_URL}/v2'


# ============================================================================
# `with_custom_http_client` resolves URLs by the same precedence — criterion 9
# ============================================================================


def test_with_custom_http_client_resolves_env_var_sync(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('APIFY_API_BASE_URL', 'http://localhost:8080')
    client = ApifyClient.with_custom_http_client(token='dummy-token', http_client=ImpitHttpClient())
    assert client._base_url == 'http://localhost:8080/v2'


async def test_with_custom_http_client_resolves_env_var_async(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('APIFY_API_BASE_URL', 'http://localhost:8080')
    client = ApifyClientAsync.with_custom_http_client(token='dummy-token', http_client=ImpitHttpClientAsync())
    assert client._base_url == 'http://localhost:8080/v2'


def test_with_custom_http_client_explicit_arg_wins_sync(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('APIFY_API_BASE_URL', 'http://localhost:8080')
    client = ApifyClient.with_custom_http_client(
        token='dummy-token',
        api_url='http://example.test',
        http_client=ImpitHttpClient(),
    )
    assert client._base_url == 'http://example.test/v2'


def test_with_custom_http_client_public_url_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('APIFY_API_PUBLIC_BASE_URL', 'http://localhost:8080')
    client = ApifyClient.with_custom_http_client(token='dummy-token', http_client=ImpitHttpClient())
    assert client._public_base_url == 'http://localhost:8080/v2'


async def test_with_custom_http_client_public_url_env_var_async(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('APIFY_API_PUBLIC_BASE_URL', 'http://localhost:8080')
    client = ApifyClientAsync.with_custom_http_client(token='dummy-token', http_client=ImpitHttpClientAsync())
    assert client._public_base_url == 'http://localhost:8080/v2'


# ============================================================================
# The `/v2` suffix invariant — criterion 19
# ============================================================================


def test_v2_suffix_applied_to_env_supplied_api_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('APIFY_API_BASE_URL', 'http://localhost:8080')
    client = ApifyClient(token='dummy-token')
    assert client._base_url.endswith('/v2')
    assert client._base_url == 'http://localhost:8080/v2'


def test_v2_suffix_applied_to_env_supplied_public_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('APIFY_API_PUBLIC_BASE_URL', 'http://localhost:8080')
    client = ApifyClient(token='dummy-token')
    assert client._public_base_url.endswith('/v2')
    assert client._public_base_url == 'http://localhost:8080/v2'

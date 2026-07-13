from __future__ import annotations

import pytest

from apify_client import ApifyClient, ApifyClientAsync
from apify_client._consts import DEFAULT_API_PUBLIC_URL, DEFAULT_API_URL
from apify_client.http_clients import ImpitHttpClient, ImpitHttpClientAsync

# Both clients resolve base URLs identically; construction is synchronous for both.
CLIENT_CLASSES = [
    pytest.param(ApifyClient, id='sync'),
    pytest.param(ApifyClientAsync, id='async'),
]

# Scenarios for the `with_custom_http_client` tests: (env_var, api_url, api_public_url, attr, expected).
WITH_CUSTOM_HTTP_CLIENT_SCENARIOS = [
    pytest.param(
        'APIFY_API_BASE_URL',
        None,
        None,
        '_base_url',
        'http://localhost:8080/v2',
        id='api-base-env-var-resolved',
    ),
    pytest.param(
        'APIFY_API_BASE_URL',
        'http://example.test',
        None,
        '_base_url',
        'http://example.test/v2',
        id='explicit-api-url-wins',
    ),
    pytest.param(
        'APIFY_API_PUBLIC_BASE_URL',
        None,
        None,
        '_public_base_url',
        'http://localhost:8080/v2',
        id='public-base-env-var-resolved',
    ),
]


# ============================================================================
# API base URL (`APIFY_API_BASE_URL`) — criteria 1-4
# ============================================================================


@pytest.mark.parametrize('client_class', CLIENT_CLASSES)
@pytest.mark.parametrize(
    ('env_value', 'explicit_arg', 'expected'),
    [
        pytest.param(None, None, f'{DEFAULT_API_URL}/v2', id='defaults-to-production-when-unset'),
        pytest.param('http://localhost:8080', None, 'http://localhost:8080/v2', id='env-var-used-when-no-argument'),
        pytest.param(
            'http://localhost:8080',
            'http://example.test',
            'http://example.test/v2',
            id='explicit-arg-wins-over-env-var',
        ),
        pytest.param(
            'http://localhost:9999',
            None,
            'http://localhost:9999/v2',
            id='custom-port-needs-no-special-handling',
        ),
    ],
)
def test_api_url_resolution(
    client_class: type[ApifyClient | ApifyClientAsync],
    env_value: str | None,
    explicit_arg: str | None,
    expected: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """API base URL resolves as explicit arg > `APIFY_API_BASE_URL` > default, for both clients."""
    if env_value is None:
        monkeypatch.delenv('APIFY_API_BASE_URL', raising=False)
    else:
        monkeypatch.setenv('APIFY_API_BASE_URL', env_value)
    client = client_class(token='dummy-token', api_url=explicit_arg)
    assert client._base_url == expected


# ============================================================================
# Public API base URL (`APIFY_API_PUBLIC_BASE_URL`) — criteria 5-8
# ============================================================================


@pytest.mark.parametrize('client_class', CLIENT_CLASSES)
@pytest.mark.parametrize(
    ('env_value', 'explicit_arg', 'expected'),
    [
        pytest.param(None, None, f'{DEFAULT_API_PUBLIC_URL}/v2', id='defaults-to-production-when-unset'),
        pytest.param('http://localhost:8080', None, 'http://localhost:8080/v2', id='env-var-used-when-no-argument'),
        pytest.param(
            'http://localhost:8080',
            'http://example.test',
            'http://example.test/v2',
            id='explicit-arg-wins-over-env-var',
        ),
    ],
)
def test_api_public_url_resolution(
    client_class: type[ApifyClient | ApifyClientAsync],
    env_value: str | None,
    explicit_arg: str | None,
    expected: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Public API base URL resolves as explicit arg > `APIFY_API_PUBLIC_BASE_URL` > default, for both clients."""
    if env_value is None:
        monkeypatch.delenv('APIFY_API_PUBLIC_BASE_URL', raising=False)
    else:
        monkeypatch.setenv('APIFY_API_PUBLIC_BASE_URL', env_value)
    client = client_class(token='dummy-token', api_public_url=explicit_arg)
    assert client._public_base_url == expected


@pytest.mark.parametrize(
    ('env_var', 'expected_base', 'expected_public'),
    [
        pytest.param(
            'APIFY_API_BASE_URL',
            'http://localhost:8080/v2',
            f'{DEFAULT_API_PUBLIC_URL}/v2',
            id='only-api-base-set-leaves-public-at-default',
        ),
        pytest.param(
            'APIFY_API_PUBLIC_BASE_URL',
            f'{DEFAULT_API_URL}/v2',
            'http://localhost:8080/v2',
            id='only-public-set-leaves-api-base-at-default',
        ),
    ],
)
def test_api_base_and_public_base_env_vars_are_independent(
    env_var: str,
    expected_base: str,
    expected_public: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Setting only one of the two env vars leaves the other at its default."""
    monkeypatch.delenv('APIFY_API_BASE_URL', raising=False)
    monkeypatch.delenv('APIFY_API_PUBLIC_BASE_URL', raising=False)
    monkeypatch.setenv(env_var, 'http://localhost:8080')
    client = ApifyClient(token='dummy-token')
    assert client._base_url == expected_base
    assert client._public_base_url == expected_public


# ============================================================================
# `with_custom_http_client` resolves URLs by the same precedence — criterion 9
# ============================================================================


@pytest.mark.parametrize(
    ('env_var', 'api_url', 'api_public_url', 'attr', 'expected'), WITH_CUSTOM_HTTP_CLIENT_SCENARIOS
)
def test_with_custom_http_client_resolution_sync(
    env_var: str,
    api_url: str | None,
    api_public_url: str | None,
    attr: str,
    expected: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`with_custom_http_client` resolves URLs by the same precedence as the constructor (sync)."""
    monkeypatch.setenv(env_var, 'http://localhost:8080')
    client = ApifyClient.with_custom_http_client(
        token='dummy-token',
        http_client=ImpitHttpClient(),
        api_url=api_url,
        api_public_url=api_public_url,
    )
    assert getattr(client, attr) == expected


@pytest.mark.parametrize(
    ('env_var', 'api_url', 'api_public_url', 'attr', 'expected'), WITH_CUSTOM_HTTP_CLIENT_SCENARIOS
)
async def test_with_custom_http_client_resolution_async(
    env_var: str,
    api_url: str | None,
    api_public_url: str | None,
    attr: str,
    expected: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`with_custom_http_client` resolves URLs by the same precedence as the constructor (async)."""
    monkeypatch.setenv(env_var, 'http://localhost:8080')
    client = ApifyClientAsync.with_custom_http_client(
        token='dummy-token',
        http_client=ImpitHttpClientAsync(),
        api_url=api_url,
        api_public_url=api_public_url,
    )
    assert getattr(client, attr) == expected


# ============================================================================
# The `/v2` suffix invariant — criterion 19
# ============================================================================


@pytest.mark.parametrize(
    ('env_var', 'attr'),
    [
        pytest.param('APIFY_API_BASE_URL', '_base_url', id='api-base'),
        pytest.param('APIFY_API_PUBLIC_BASE_URL', '_public_base_url', id='public-base'),
    ],
)
def test_v2_suffix_applied_to_env_supplied_url(
    env_var: str,
    attr: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The `/v2` version suffix is appended to an env-supplied base URL that lacks it."""
    monkeypatch.setenv(env_var, 'http://localhost:8080')
    client = ApifyClient(token='dummy-token')
    value = getattr(client, attr)
    assert value.endswith('/v2')
    assert value == 'http://localhost:8080/v2'

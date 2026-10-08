from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from apify_client import ApifyClient, ApifyClientAsync

if TYPE_CHECKING:
    from pytest_httpserver import HTTPServer

pytestmark = pytest.mark.usefixtures('http_client_classes')

ACTOR_ID = 'test_actor_id'


def expect_validate_input(httpserver: HTTPServer, build: str) -> str:
    httpserver.expect_request(
        f'/v2/actors/{ACTOR_ID}/validate-input',
        method='POST',
        query_string={'build': build},
    ).respond_with_json({'valid': True})
    return httpserver.url_for('/').removesuffix('/')


def test_validate_input_passes_build_sync(httpserver: HTTPServer) -> None:
    """`build` is sent as the `build` query parameter."""
    client = ApifyClient(token='test_token', api_url=expect_validate_input(httpserver, '1.2.3'))

    assert client.actor(ACTOR_ID).validate_input({}, build='1.2.3') is True
    httpserver.check_assertions()


async def test_validate_input_passes_build_async(httpserver: HTTPServer) -> None:
    """`build` is sent as the `build` query parameter."""
    client = ApifyClientAsync(token='test_token', api_url=expect_validate_input(httpserver, '1.2.3'))

    assert await client.actor(ACTOR_ID).validate_input({}, build='1.2.3') is True
    httpserver.check_assertions()


def test_validate_input_build_tag_is_deprecated_alias_sync(httpserver: HTTPServer) -> None:
    """The deprecated `build_tag` emits a `DeprecationWarning` pointing at the caller and is sent as `build`."""
    client = ApifyClient(token='test_token', api_url=expect_validate_input(httpserver, 'beta'))

    with pytest.warns(DeprecationWarning, match='`build_tag` argument is deprecated') as record:
        assert client.actor(ACTOR_ID).validate_input({}, build_tag='beta') is True
    assert record[0].filename == __file__
    httpserver.check_assertions()


async def test_validate_input_build_tag_is_deprecated_alias_async(httpserver: HTTPServer) -> None:
    """The deprecated `build_tag` emits a `DeprecationWarning` pointing at the caller and is sent as `build`."""
    client = ApifyClientAsync(token='test_token', api_url=expect_validate_input(httpserver, 'beta'))

    with pytest.warns(DeprecationWarning, match='`build_tag` argument is deprecated') as record:
        assert await client.actor(ACTOR_ID).validate_input({}, build_tag='beta') is True
    assert record[0].filename == __file__
    httpserver.check_assertions()


def test_validate_input_rejects_build_and_build_tag_sync() -> None:
    """Passing both `build` and `build_tag` raises a `ValueError`."""
    client = ApifyClient(token='test_token')

    with (
        pytest.warns(DeprecationWarning, match='`build_tag` argument is deprecated'),
        pytest.raises(ValueError, match='only one of'),
    ):
        client.actor(ACTOR_ID).validate_input({}, build='latest', build_tag='beta')


async def test_validate_input_rejects_build_and_build_tag_async() -> None:
    """Passing both `build` and `build_tag` raises a `ValueError`."""
    client = ApifyClientAsync(token='test_token')

    with (
        pytest.warns(DeprecationWarning, match='`build_tag` argument is deprecated'),
        pytest.raises(ValueError, match='only one of'),
    ):
        await client.actor(ACTOR_ID).validate_input({}, build='latest', build_tag='beta')

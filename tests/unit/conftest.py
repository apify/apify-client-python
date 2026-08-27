from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

import pytest
from pytest_httpserver import HTTPServer

from .._utils import HttpClientClasses
from apify_client import ApifyClient, ApifyClientAsync
from apify_client.http_clients import (
    HttpClient,
    HttpClientAsync,
    HttpxHttpClient,
    HttpxHttpClientAsync,
    ImpitHttpClient,
    ImpitHttpClientAsync,
)

if TYPE_CHECKING:
    from collections.abc import Iterable


@pytest.fixture(scope='session')
def make_httpserver() -> Iterable[HTTPServer]:
    werkzeug_logger = getLogger('werkzeug')
    werkzeug_logger.disabled = True

    server = HTTPServer(threaded=True, host='127.0.0.1')
    server.start()
    yield server
    server.clear()
    if server.is_running():
        server.stop()


@pytest.fixture
def httpserver(make_httpserver: HTTPServer) -> Iterable[HTTPServer]:
    server = make_httpserver
    yield server
    server.clear()


@pytest.fixture
def sync_client(httpserver: HTTPServer) -> ApifyClient:
    return ApifyClient(token='test', api_url=httpserver.url_for('/').removesuffix('/'))


@pytest.fixture
def async_client(httpserver: HTTPServer) -> ApifyClientAsync:
    return ApifyClientAsync(token='test', api_url=httpserver.url_for('/').removesuffix('/'))


@pytest.fixture(
    params=[
        pytest.param(HttpClientClasses(sync=ImpitHttpClient, async_=ImpitHttpClientAsync), id='impit'),
        pytest.param(HttpClientClasses(sync=HttpxHttpClient, async_=HttpxHttpClientAsync), id='httpx'),
    ]
)
def http_client_classes(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> HttpClientClasses:
    """Run the test once per built-in HTTP transport, making each the default the Apify clients construct.

    A module opts every test it holds into the transport matrix with
    `pytestmark = pytest.mark.usefixtures('http_client_classes')`. Tests constructing transports directly get the
    same single parametrization axis through the derived `http_client_class` / `http_client_async_class` fixtures.
    """
    classes = request.param
    assert isinstance(classes, HttpClientClasses)
    monkeypatch.setattr('apify_client._apify_client.ImpitHttpClient', classes.sync)
    monkeypatch.setattr('apify_client._apify_client.ImpitHttpClientAsync', classes.async_)
    return classes


@pytest.fixture
def http_client_class(http_client_classes: HttpClientClasses) -> type[HttpClient]:
    """Return each built-in synchronous HTTP client class."""
    return http_client_classes.sync


@pytest.fixture
def http_client_async_class(http_client_classes: HttpClientClasses) -> type[HttpClientAsync]:
    """Return each built-in asynchronous HTTP client class."""
    return http_client_classes.async_

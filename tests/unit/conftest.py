from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

import pytest
from pytest_httpserver import HTTPServer

from apify_client.http_clients import HttpClient, HttpClientAsync, ImpitHttpClient, ImpitHttpClientAsync

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


@pytest.fixture(params=[pytest.param(ImpitHttpClient, id='impit')])
def http_client_class(request: pytest.FixtureRequest) -> type[HttpClient]:
    """Return each built-in synchronous HTTP client class."""
    return request.param


@pytest.fixture(params=[pytest.param(ImpitHttpClientAsync, id='impit')])
def http_client_async_class(request: pytest.FixtureRequest) -> type[HttpClientAsync]:
    """Return each built-in asynchronous HTTP client class."""
    return request.param

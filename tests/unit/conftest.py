from collections.abc import Iterable, Iterator
from logging import getLogger

import pytest
from pytest_httpserver import HTTPServer


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
def patch_basic_url(httpserver: HTTPServer, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    server_url = httpserver.url_for('/').removesuffix('/')
    monkeypatch.setattr('apify_client.client.DEFAULT_API_URL', server_url)
    yield
    monkeypatch.undo()

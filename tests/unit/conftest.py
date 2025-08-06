from collections.abc import Iterable, Iterator
from logging import getLogger

import pytest
from pytest_httpserver import HTTPServer


@pytest.fixture(scope='session')
def make_httpserver() -> Iterable[HTTPServer]:
    werkzeug_logger = getLogger('werkzeug')
    werkzeug_logger.disabled = True

    server = HTTPServer(threaded=True)
    server.start()
    yield server
    server.clear()  # type: ignore[no-untyped-call]
    if server.is_running():
        server.stop()  # type: ignore[no-untyped-call]


@pytest.fixture(scope='session')
def httpserver(make_httpserver: HTTPServer) -> HTTPServer:
    return make_httpserver


@pytest.fixture
def patch_basic_url(httpserver: HTTPServer, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    server_url = httpserver.url_for('/').removesuffix('/')
    monkeypatch.setattr('apify_client.client.DEFAULT_API_URL', server_url)
    yield
    monkeypatch.undo()

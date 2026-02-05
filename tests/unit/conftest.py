from collections.abc import Iterable
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

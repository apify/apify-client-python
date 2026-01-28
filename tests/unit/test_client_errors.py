from __future__ import annotations

import json
import time
from typing import TYPE_CHECKING

import pytest
from werkzeug import Response

from apify_client._config import ClientConfig
from apify_client._http_clients import HttpClient, HttpClientAsync
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from collections.abc import Iterator

    from pytest_httpserver import HTTPServer
    from werkzeug import Request

_TEST_PATH = '/errors'
_EXPECTED_MESSAGE = 'some_message'
_EXPECTED_TYPE = 'some_type'
_EXPECTED_DATA = {
    'invalidItems': {'0': ["should have required property 'name'"], '1': ["should have required property 'name'"]}
}

RAW_ERROR = (
    b'{\n'
    b'  "error": {\n'
    b'    "type": "insufficient-permissions",\n'
    b'    "message": "Insufficient permissions for the Actor run. Make sure you\''
    b're passing a correct API token and that it has the required permissions."\n'
    b'  }\n'
    b'}'
)


@pytest.fixture
def test_config() -> ClientConfig:
    return ClientConfig.from_user_params()


@pytest.fixture
def test_endpoint(httpserver: HTTPServer) -> str:
    httpserver.expect_request(_TEST_PATH).respond_with_json(
        {'error': {'message': _EXPECTED_MESSAGE, 'type': _EXPECTED_TYPE, 'data': _EXPECTED_DATA}}, status=400
    )
    return str(httpserver.url_for(_TEST_PATH))


def streaming_handler(_request: Request) -> Response:
    """Handler for streaming log requests."""

    def generate_response() -> Iterator[bytes]:
        for i in range(len(RAW_ERROR)):
            yield RAW_ERROR[i : i + 1]
            time.sleep(0.01)

    return Response(
        response=(RAW_ERROR[i : i + 1] for i in range(len(RAW_ERROR))),
        status=403,
        mimetype='application/octet-stream',
        headers={'Content-Length': str(len(RAW_ERROR))},
    )


def test_client_apify_api_error_with_data(test_endpoint: str, test_config: ClientConfig) -> None:
    """Test that client correctly throws ApifyApiError with error data from response."""
    client = HttpClient(config=test_config)

    with pytest.raises(ApifyApiError) as exc:
        client.call(method='GET', url=test_endpoint)

    assert exc.value.message == _EXPECTED_MESSAGE
    assert exc.value.type == _EXPECTED_TYPE
    assert exc.value.data == _EXPECTED_DATA


async def test_async_client_apify_api_error_with_data(test_endpoint: str, test_config: ClientConfig) -> None:
    """Test that async client correctly throws ApifyApiError with error data from response."""
    client = HttpClientAsync(config=test_config)

    with pytest.raises(ApifyApiError) as exc:
        await client.call(method='GET', url=test_endpoint)

    assert exc.value.message == _EXPECTED_MESSAGE
    assert exc.value.type == _EXPECTED_TYPE
    assert exc.value.data == _EXPECTED_DATA


def test_client_apify_api_error_streamed(httpserver: HTTPServer, test_config: ClientConfig) -> None:
    """Test that client correctly throws ApifyApiError when the response has stream."""

    error = json.loads(RAW_ERROR.decode())

    client = HttpClient(config=test_config)

    httpserver.expect_request('/stream_error').respond_with_handler(streaming_handler)

    with pytest.raises(ApifyApiError) as exc:
        client.call(method='GET', url=httpserver.url_for('/stream_error'), stream=True)

    assert exc.value.message == error['error']['message']
    assert exc.value.type == error['error']['type']


async def test_async_client_apify_api_error_streamed(httpserver: HTTPServer, test_config: ClientConfig) -> None:
    """Test that async client correctly throws ApifyApiError when the response has stream."""

    error = json.loads(RAW_ERROR.decode())

    client = HttpClientAsync(config=test_config)

    httpserver.expect_request('/stream_error').respond_with_handler(streaming_handler)

    with pytest.raises(ApifyApiError) as exc:
        await client.call(method='GET', url=httpserver.url_for('/stream_error'), stream=True)

    assert exc.value.message == error['error']['message']
    assert exc.value.type == error['error']['type']

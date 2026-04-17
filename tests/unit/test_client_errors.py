from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
from werkzeug import Response

from apify_client._http_clients import ImpitHttpClient, ImpitHttpClientAsync
from apify_client.errors import ApifyApiError, InsufficientPermissionsError, RecordNotFoundError

if TYPE_CHECKING:
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
def test_endpoint(httpserver: HTTPServer) -> str:
    httpserver.expect_request(_TEST_PATH).respond_with_json(
        {'error': {'message': _EXPECTED_MESSAGE, 'type': _EXPECTED_TYPE, 'data': _EXPECTED_DATA}}, status=400
    )
    return str(httpserver.url_for(_TEST_PATH))


def streaming_handler(_request: Request) -> Response:
    """Handler for streaming log requests."""
    return Response(
        response=(RAW_ERROR[i : i + 1] for i in range(len(RAW_ERROR))),
        status=403,
        mimetype='application/octet-stream',
        headers={'Content-Length': str(len(RAW_ERROR))},
    )


def test_client_apify_api_error_with_data(test_endpoint: str) -> None:
    """Test that client correctly throws ApifyApiError with error data from response."""
    client = ImpitHttpClient()

    with pytest.raises(ApifyApiError) as exc:
        client.call(method='GET', url=test_endpoint)

    assert exc.value.message == _EXPECTED_MESSAGE
    assert exc.value.type == _EXPECTED_TYPE
    assert exc.value.data == _EXPECTED_DATA


async def test_async_client_apify_api_error_with_data(test_endpoint: str) -> None:
    """Test that async client correctly throws ApifyApiError with error data from response."""
    client = ImpitHttpClientAsync()

    with pytest.raises(ApifyApiError) as exc:
        await client.call(method='GET', url=test_endpoint)

    assert exc.value.message == _EXPECTED_MESSAGE
    assert exc.value.type == _EXPECTED_TYPE
    assert exc.value.data == _EXPECTED_DATA


def test_client_apify_api_error_streamed(httpserver: HTTPServer) -> None:
    """Test that client correctly throws ApifyApiError when the response has stream."""

    error = json.loads(RAW_ERROR.decode())

    client = ImpitHttpClient()

    httpserver.expect_request('/stream_error').respond_with_handler(streaming_handler)

    with pytest.raises(ApifyApiError) as exc:
        client.call(method='GET', url=httpserver.url_for('/stream_error'), stream=True)

    assert exc.value.message == error['error']['message']
    assert exc.value.type == error['error']['type']


async def test_async_client_apify_api_error_streamed(httpserver: HTTPServer) -> None:
    """Test that async client correctly throws ApifyApiError when the response has stream."""

    error = json.loads(RAW_ERROR.decode())

    client = ImpitHttpClientAsync()

    httpserver.expect_request('/stream_error').respond_with_handler(streaming_handler)

    with pytest.raises(ApifyApiError) as exc:
        await client.call(method='GET', url=httpserver.url_for('/stream_error'), stream=True)

    assert exc.value.message == error['error']['message']
    assert exc.value.type == error['error']['type']


def test_apify_api_error_dispatches_to_subclass_for_known_type(httpserver: HTTPServer) -> None:
    """Known error types (from the OpenAPI spec) dispatch to their matching subclass."""
    httpserver.expect_request('/dispatch').respond_with_json(
        {'error': {'type': 'record-not-found', 'message': 'nope'}}, status=404
    )
    client = ImpitHttpClient()

    with pytest.raises(RecordNotFoundError) as exc:
        client.call(method='GET', url=str(httpserver.url_for('/dispatch')))

    # Still an ApifyApiError, so legacy `except` handlers keep working.
    assert isinstance(exc.value, ApifyApiError)
    assert exc.value.type == 'record-not-found'


def test_apify_api_error_dispatches_streamed_response(httpserver: HTTPServer) -> None:
    """Dispatch works even when the response body comes in as a stream (insufficient-permissions)."""
    httpserver.expect_request('/stream_dispatch').respond_with_handler(streaming_handler)
    client = ImpitHttpClient()

    with pytest.raises(InsufficientPermissionsError) as exc:
        client.call(method='GET', url=httpserver.url_for('/stream_dispatch'), stream=True)

    assert isinstance(exc.value, ApifyApiError)
    assert exc.value.type == 'insufficient-permissions'


def test_apify_api_error_falls_back_for_unknown_type(httpserver: HTTPServer) -> None:
    """Unknown error types fall back to the base ApifyApiError class."""
    httpserver.expect_request('/unknown').respond_with_json(
        {'error': {'type': 'totally-made-up', 'message': 'nope'}}, status=400
    )
    client = ImpitHttpClient()

    with pytest.raises(ApifyApiError) as exc:
        client.call(method='GET', url=str(httpserver.url_for('/unknown')))

    assert type(exc.value) is ApifyApiError
    assert exc.value.type == 'totally-made-up'


def test_apify_api_error_falls_back_for_unparsable_body(httpserver: HTTPServer) -> None:
    """When the body can't be parsed, dispatch falls back to ApifyApiError without raising."""
    httpserver.expect_request('/unparsable').respond_with_data('<not json>', status=500, content_type='text/html')
    client = ImpitHttpClient(max_retries=1)

    with pytest.raises(ApifyApiError) as exc:
        client.call(method='GET', url=str(httpserver.url_for('/unparsable')))

    assert type(exc.value) is ApifyApiError
    assert exc.value.type is None

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from apify_client._errors import ApifyApiError
from apify_client._http_client import HTTPClient, HTTPClientAsync

if TYPE_CHECKING:
    from pytest_httpserver import HTTPServer

_TEST_PATH = '/errors'
_EXPECTED_MESSAGE = 'some_message'
_EXPECTED_TYPE = 'some_type'
_EXPECTED_DATA = {
    'invalidItems': {'0': ["should have required property 'name'"], '1': ["should have required property 'name'"]}
}


@pytest.fixture
def test_endpoint(httpserver: HTTPServer) -> str:
    httpserver.expect_request(_TEST_PATH).respond_with_json(
        {'error': {'message': _EXPECTED_MESSAGE, 'type': _EXPECTED_TYPE, 'data': _EXPECTED_DATA}}, status=400
    )
    return str(httpserver.url_for(_TEST_PATH))


def test_client_apify_api_error_with_data(test_endpoint: str) -> None:
    """Test that client correctly throws ApifyApiError with error data from response."""
    client = HTTPClient()

    with pytest.raises(ApifyApiError) as e:
        client.call(method='GET', url=test_endpoint)

    assert e.value.message == _EXPECTED_MESSAGE
    assert e.value.type == _EXPECTED_TYPE
    assert e.value.data == _EXPECTED_DATA


async def test_async_client_apify_api_error_with_data(test_endpoint: str) -> None:
    """Test that async client correctly throws ApifyApiError with error data from response."""
    client = HTTPClientAsync()

    with pytest.raises(ApifyApiError) as e:
        await client.call(method='GET', url=test_endpoint)

    assert e.value.message == _EXPECTED_MESSAGE
    assert e.value.type == _EXPECTED_TYPE
    assert e.value.data == _EXPECTED_DATA

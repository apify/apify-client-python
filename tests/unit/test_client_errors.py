import json
from collections.abc import Generator

import httpx
import pytest
import respx

from apify_client._errors import ApifyApiError
from apify_client._http_client import HTTPClient, HTTPClientAsync

_TEST_URL = 'http://example.com'
_EXPECTED_MESSAGE = 'some_message'
_EXPECTED_TYPE = 'some_type'
_EXPECTED_DATA = {
    'invalidItems': {'0': ["should have required property 'name'"], '1': ["should have required property 'name'"]}
}


@pytest.fixture(autouse=True)
def mocked_response() -> Generator[respx.MockRouter]:
    response_content = json.dumps(
        {'error': {'message': _EXPECTED_MESSAGE, 'type': _EXPECTED_TYPE, 'data': _EXPECTED_DATA}}
    )
    with respx.mock() as respx_mock:
        respx_mock.get(_TEST_URL).mock(return_value=httpx.Response(400, content=response_content))
        yield respx_mock


def test_client_apify_api_error_with_data() -> None:
    """Test that client correctly throws ApifyApiError with error data from response."""
    client = HTTPClient()

    with pytest.raises(ApifyApiError) as e:
        client.call(method='GET', url=_TEST_URL)

    assert e.value.message == _EXPECTED_MESSAGE
    assert e.value.type == _EXPECTED_TYPE
    assert e.value.data == _EXPECTED_DATA


async def test_async_client_apify_api_error_with_data() -> None:
    """Test that async client correctly throws ApifyApiError with error data from response."""
    client = HTTPClientAsync()

    with pytest.raises(ApifyApiError) as e:
        await client.call(method='GET', url=_TEST_URL)

    assert e.value.message == _EXPECTED_MESSAGE
    assert e.value.type == _EXPECTED_TYPE
    assert e.value.data == _EXPECTED_DATA

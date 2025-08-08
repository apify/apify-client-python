import json
from collections.abc import AsyncIterator, Generator, Iterator

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
def mocked_response() -> Generator[respx.MockRouter]:
    response_content = json.dumps(
        {'error': {'message': _EXPECTED_MESSAGE, 'type': _EXPECTED_TYPE, 'data': _EXPECTED_DATA}}
    )
    with respx.mock() as respx_mock:
        respx_mock.get(_TEST_URL).mock(return_value=httpx.Response(400, content=response_content))
        yield respx_mock


@pytest.mark.usefixtures('mocked_response')
def test_client_apify_api_error_with_data() -> None:
    """Test that client correctly throws ApifyApiError with error data from response."""
    client = HTTPClient()

    with pytest.raises(ApifyApiError) as e:
        client.call(method='GET', url=_TEST_URL)

    assert e.value.message == _EXPECTED_MESSAGE
    assert e.value.type == _EXPECTED_TYPE
    assert e.value.data == _EXPECTED_DATA


@pytest.mark.usefixtures('mocked_response')
async def test_async_client_apify_api_error_with_data() -> None:
    """Test that async client correctly throws ApifyApiError with error data from response."""
    client = HTTPClientAsync()

    with pytest.raises(ApifyApiError) as e:
        await client.call(method='GET', url=_TEST_URL)

    assert e.value.message == _EXPECTED_MESSAGE
    assert e.value.type == _EXPECTED_TYPE
    assert e.value.data == _EXPECTED_DATA


def test_client_apify_api_error_streamed() -> None:
    """Test that client correctly throws ApifyApiError when the response has stream."""

    error = json.loads(RAW_ERROR.decode())

    class ByteStream(httpx._types.SyncByteStream):
        def __iter__(self) -> Iterator[bytes]:
            yield RAW_ERROR

        def close(self) -> None:
            pass

    stream_url = 'http://some-stream-url.com'

    client = HTTPClient()

    with respx.mock() as respx_mock:
        respx_mock.get(url=stream_url).mock(return_value=httpx.Response(stream=ByteStream(), status_code=403))
        with pytest.raises(ApifyApiError) as e:
            client.call(method='GET', url=stream_url, stream=True, parse_response=False)

    assert e.value.message == error['error']['message']
    assert e.value.type == error['error']['type']


async def test_async_client_apify_api_error_streamed() -> None:
    """Test that async client correctly throws ApifyApiError when the response has stream."""

    error = json.loads(RAW_ERROR.decode())

    class AsyncByteStream(httpx._types.AsyncByteStream):
        async def __aiter__(self) -> AsyncIterator[bytes]:
            yield RAW_ERROR

        async def aclose(self) -> None:
            pass

    stream_url = 'http://some-stream-url.com'

    client = HTTPClientAsync()

    with respx.mock() as respx_mock:
        respx_mock.get(url=stream_url).mock(return_value=httpx.Response(stream=AsyncByteStream(), status_code=403))
        with pytest.raises(ApifyApiError) as e:
            await client.call(method='GET', url=stream_url, stream=True, parse_response=False)

    assert e.value.message == error['error']['message']
    assert e.value.type == error['error']['type']

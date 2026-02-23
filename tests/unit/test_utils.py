import io
from datetime import timedelta
from enum import Enum
from http import HTTPStatus
from unittest.mock import Mock

import impit
import pytest

from apify_client._models import WebhookEventType
from apify_client._utils import (
    catch_not_found_or_throw,
    create_hmac_signature,
    create_storage_content_signature,
    encode_base62,
    encode_key_value_store_record_value,
    encode_webhook_list_to_base64,
    enum_to_value,
    filter_none_values,
    is_retryable_error,
    response_to_dict,
    response_to_list,
    to_safe_id,
)
from apify_client.errors import ApifyApiError, InvalidResponseBodyError


def test_to_safe_id() -> None:
    assert to_safe_id('abc') == 'abc'
    assert to_safe_id('abc/def') == 'abc~def'
    assert to_safe_id('abc~def') == 'abc~def'
    assert to_safe_id('user/resource/extra') == 'user~resource~extra'


def test_encode_webhook_list_to_base64() -> None:
    assert encode_webhook_list_to_base64([]) == 'W10='
    assert (
        encode_webhook_list_to_base64(
            [
                {
                    'event_types': [WebhookEventType.ACTOR_RUN_CREATED],
                    'request_url': 'https://example.com/run-created',
                },
                {
                    'event_types': [WebhookEventType.ACTOR_RUN_SUCCEEDED],
                    'request_url': 'https://example.com/run-succeeded',
                    'payload_template': '{"hello": "world", "resource":{{resource}}}',
                },
            ]
        )
        == 'W3siZXZlbnRUeXBlcyI6IFsiQUNUT1IuUlVOLkNSRUFURUQiXSwgInJlcXVlc3RVcmwiOiAiaHR0cHM6Ly9leGFtcGxlLmNvbS9ydW4tY3JlYXRlZCJ9LCB7ImV2ZW50VHlwZXMiOiBbIkFDVE9SLlJVTi5TVUNDRUVERUQiXSwgInJlcXVlc3RVcmwiOiAiaHR0cHM6Ly9leGFtcGxlLmNvbS9ydW4tc3VjY2VlZGVkIiwgInBheWxvYWRUZW1wbGF0ZSI6ICJ7XCJoZWxsb1wiOiBcIndvcmxkXCIsIFwicmVzb3VyY2VcIjp7e3Jlc291cmNlfX19In1d'  # noqa: E501
    )


@pytest.mark.parametrize(
    'exc',
    [
        InvalidResponseBodyError(impit.Response(status_code=200)),
        impit.HTTPError('generic http error'),
        impit.NetworkError('network error'),
        impit.TimeoutException('timeout'),
        impit.RemoteProtocolError('remote protocol error'),
        impit.ReadError('read error'),
        impit.ConnectError('connect error'),
        impit.WriteError('write error'),
        impit.DecodingError('decoding error'),
    ],
)
def test__is_retryable_error(exc: Exception) -> None:
    assert is_retryable_error(exc) is True


@pytest.mark.parametrize(
    'exc',
    [
        Exception('generic exception'),
        ValueError('value error'),
        RuntimeError('runtime error'),
    ],
)
def test__is_not_retryable_error(exc: Exception) -> None:
    assert is_retryable_error(exc) is False


@pytest.mark.parametrize(
    ('status_code', 'error_type', 'should_suppress'),
    [
        pytest.param(HTTPStatus.NOT_FOUND, 'record-not-found', True, id='404 record-not-found'),
        pytest.param(HTTPStatus.NOT_FOUND, 'record-or-token-not-found', True, id='404 token-not-found'),
        pytest.param(HTTPStatus.NOT_FOUND, 'some-other-error', False, id='404 other error type'),
        pytest.param(HTTPStatus.INTERNAL_SERVER_ERROR, 'record-not-found', False, id='500 record-not-found'),
    ],
)
def test_catch_not_found_or_throw(status_code: HTTPStatus, error_type: str, *, should_suppress: bool) -> None:
    """Test that catch_not_found_or_throw suppresses 404 errors correctly."""
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.text = f'{{"error":{{"type":"{error_type}"}}}}'

    error = ApifyApiError(mock_response, 1)
    error.type = error_type

    if should_suppress:
        catch_not_found_or_throw(error)
    else:
        with pytest.raises(ApifyApiError):
            catch_not_found_or_throw(error)


@pytest.mark.parametrize(
    ('input_dict', 'remove_empty_dicts', 'expected'),
    [
        pytest.param({'a': 1, 'b': None, 'c': 3}, False, {'a': 1, 'c': 3}, id='Simple case'),
        pytest.param({'a': {'b': None, 'c': 2}, 'd': None}, False, {'a': {'c': 2}}, id='Nested dictionaries'),
        pytest.param({'a': {'b': {'c': None, 'd': 4}}}, False, {'a': {'b': {'d': 4}}}, id='Deep nesting'),
        pytest.param({'a': None, 'b': None}, False, {}, id='Empty dict after filtering'),
        pytest.param({'a': {'b': None}, 'c': 3}, True, {'c': 3}, id='Remove empty dicts'),
        pytest.param({'a': {'b': None}, 'c': 3}, False, {'a': {}, 'c': 3}, id='Keep empty dicts by default'),
        pytest.param(
            {'a': 0, 'b': '', 'c': False}, False, {'a': 0, 'b': '', 'c': False}, id='Keep falsy non-None values'
        ),
    ],
)
def test_filter_none_values(input_dict: dict, *, remove_empty_dicts: bool, expected: dict) -> None:
    """Test filtering None values from dictionaries."""
    assert filter_none_values(input_dict, remove_empty_dicts=remove_empty_dicts) == expected


def test_encode_key_value_store_record_value_dict() -> None:
    """Test that dictionaries are encoded as JSON."""
    value, content_type = encode_key_value_store_record_value({'key': 'value'})
    assert b'"key"' in value
    assert b'"value"' in value
    assert content_type == 'application/json; charset=utf-8'


@pytest.mark.parametrize(
    ('input_value', 'input_content_type', 'expected_value', 'expected_content_type'),
    [
        pytest.param('hello', None, 'hello', 'text/plain; charset=utf-8', id='String is text/plain'),
        pytest.param(b'binary data', None, b'binary data', 'application/octet-stream', id='Bytes is octet-stream'),
        pytest.param('hello', 'text/html', 'hello', 'text/html', id='Custom content type is preserved'),
    ],
)
def test_encode_key_value_store_record_value(
    input_value: str | bytes, input_content_type: str | None, expected_value: str | bytes, expected_content_type: str
) -> None:
    """Test encoding of key-value store record values."""
    if input_content_type is not None:
        value, content_type = encode_key_value_store_record_value(input_value, input_content_type)
    else:
        value, content_type = encode_key_value_store_record_value(input_value)
    assert value == expected_value
    assert content_type == expected_content_type


def test_encode_key_value_store_record_value_bytesio() -> None:
    """Test that BytesIO is encoded as octet-stream."""
    buffer = io.BytesIO(b'buffer data')
    value, content_type = encode_key_value_store_record_value(buffer)
    assert value == buffer
    assert content_type == 'application/octet-stream'


class _TestEnum(Enum):
    VALUE1 = 'val1'
    VALUE2 = 42


@pytest.mark.parametrize(
    ('input_value', 'expected'),
    [
        pytest.param(_TestEnum.VALUE1, 'val1', id='Enum string value'),
        pytest.param(_TestEnum.VALUE2, 42, id='Enum int value'),
        pytest.param('not_an_enum', 'not_an_enum', id='Plain string passthrough'),
        pytest.param(123, 123, id='Plain int passthrough'),
        pytest.param(None, None, id='None passthrough'),
    ],
)
def test_enum_to_value(input_value: _TestEnum | str | int | None, expected: str | int | None) -> None:
    """Test enum to value conversion."""
    assert enum_to_value(input_value) == expected


def test_response_to_dict() -> None:
    """Test parsing response as dictionary."""
    mock_response = Mock()
    mock_response.json.return_value = {'key': 'value'}
    assert response_to_dict(mock_response) == {'key': 'value'}


@pytest.mark.parametrize(
    'json_return_value',
    [
        pytest.param(['list', 'response'], id='List response'),
        pytest.param('string', id='String response'),
    ],
)
def test_response_to_dict_raises_for_non_dict(json_return_value: object) -> None:
    """Test that response_to_dict raises for non-dict responses."""
    mock_response = Mock()
    mock_response.json.return_value = json_return_value
    with pytest.raises(ValueError, match='The response is not a dictionary'):
        response_to_dict(mock_response)


def test_response_to_list() -> None:
    """Test parsing response as list."""
    mock_response = Mock()
    mock_response.json.return_value = ['item1', 'item2']
    assert response_to_list(mock_response) == ['item1', 'item2']


def test_response_to_list_wraps_dict_in_list() -> None:
    """Test that response_to_list wraps a dict response in a list."""
    mock_response = Mock()
    mock_response.json.return_value = {'dict': 'response'}
    assert response_to_list(mock_response) == [{'dict': 'response'}]


def test_response_to_list_raises_for_non_list() -> None:
    """Test that response_to_list raises for non-list, non-dict responses."""
    mock_response = Mock()
    mock_response.json.return_value = 'string'
    with pytest.raises(ValueError, match='The response is not a list'):
        response_to_list(mock_response)


@pytest.mark.parametrize(
    ('input_value', 'expected'),
    [
        pytest.param(0, '0', id='Zero'),
        pytest.param(1, '1', id='One'),
        pytest.param(9, '9', id='Last digit'),
        pytest.param(10, 'a', id='First lowercase letter'),
        pytest.param(35, 'z', id='Last lowercase letter'),
        pytest.param(36, 'A', id='First uppercase letter'),
        pytest.param(61, 'Z', id='Last uppercase letter'),
        pytest.param(62, '10', id='First two-char encoding'),
        pytest.param(100, '1C', id='100'),
        pytest.param(123456, 'w7e', id='Large number'),
    ],
)
def test_encode_base62(input_value: int, expected: str) -> None:
    """Test base62 encoding."""
    assert encode_base62(input_value) == expected


def test_create_hmac_signature() -> None:
    """Test HMAC signature creation."""
    # Test with known values
    signature = create_hmac_signature('secret_key', 'test_message')
    assert isinstance(signature, str)
    assert len(signature) > 0

    # Same inputs should produce same output
    signature2 = create_hmac_signature('secret_key', 'test_message')
    assert signature == signature2

    # Different inputs should produce different output
    signature3 = create_hmac_signature('different_key', 'test_message')
    assert signature != signature3

    signature4 = create_hmac_signature('secret_key', 'different_message')
    assert signature != signature4


def test_create_storage_signature() -> None:
    """Test storage signature creation."""
    # Non-expiring signature
    signature = create_storage_content_signature('resource_123', 'secret_key')
    assert isinstance(signature, str)
    assert len(signature) > 0

    # Expiring signature
    signature_expiring = create_storage_content_signature(
        'resource_123',
        'secret_key',
        expires_in=timedelta(seconds=60),
    )

    assert isinstance(signature_expiring, str)
    assert len(signature_expiring) > 0
    assert signature != signature_expiring  # Different because of expiration

    # Different resource IDs produce different signatures
    signature2 = create_storage_content_signature('resource_456', 'secret_key')
    assert signature != signature2

    # Same inputs should produce same output (for non-expiring)
    signature3 = create_storage_content_signature('resource_123', 'secret_key')
    assert signature == signature3

    # Test with version parameter
    signature_v1 = create_storage_content_signature('resource_123', 'secret_key', version=1)
    assert signature != signature_v1

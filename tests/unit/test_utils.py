import io
from enum import Enum
from http import HTTPStatus
from unittest.mock import Mock

import pytest

from apify_client._consts import WebhookEventType
from apify_client._utils import (
    catch_not_found_or_throw,
    create_hmac_signature,
    create_storage_content_signature,
    encode_base62,
    encode_key_value_store_record_value,
    encode_webhook_list_to_base64,
    enum_to_value,
    filter_none_values,
    response_to_dict,
    response_to_list,
    to_safe_id,
)
from apify_client.errors import ApifyApiError


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


def test_catch_not_found_or_throw() -> None:
    """Test that catch_not_found_or_throw suppresses 404 errors correctly."""
    # Mock response for 404 Not Found
    mock_response = Mock()
    mock_response.status_code = HTTPStatus.NOT_FOUND
    mock_response.text = '{"error":{"type":"record-not-found"}}'

    # Should not raise for record-not-found
    error_404_record = ApifyApiError(mock_response, 1)
    error_404_record.type = 'record-not-found'
    catch_not_found_or_throw(error_404_record)

    # Should not raise for record-or-token-not-found
    error_404_token = ApifyApiError(mock_response, 1)
    error_404_token.type = 'record-or-token-not-found'
    catch_not_found_or_throw(error_404_token)

    # Should raise for other error types with 404
    error_404_other = ApifyApiError(mock_response, 1)
    error_404_other.type = 'some-other-error'
    with pytest.raises(ApifyApiError):
        catch_not_found_or_throw(error_404_other)

    # Should raise for non-404 status codes
    mock_response_500 = Mock()
    mock_response_500.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    mock_response_500.text = '{"error":{"type":"record-not-found"}}'
    error_500 = ApifyApiError(mock_response_500, 1)
    error_500.type = 'record-not-found'
    with pytest.raises(ApifyApiError):
        catch_not_found_or_throw(error_500)


def test_filter_none_values() -> None:
    """Test filtering None values from dictionaries."""
    # Simple case
    assert filter_none_values({'a': 1, 'b': None, 'c': 3}) == {'a': 1, 'c': 3}

    # Nested dictionaries
    assert filter_none_values({'a': {'b': None, 'c': 2}, 'd': None}) == {'a': {'c': 2}}

    # Deep nesting
    assert filter_none_values({'a': {'b': {'c': None, 'd': 4}}}) == {'a': {'b': {'d': 4}}}

    # Empty dict after filtering
    assert filter_none_values({'a': None, 'b': None}) == {}

    # Remove empty dicts
    assert filter_none_values({'a': {'b': None}, 'c': 3}, remove_empty_dicts=True) == {'c': 3}

    # Don't remove empty dicts by default
    assert filter_none_values({'a': {'b': None}, 'c': 3}) == {'a': {}, 'c': 3}

    # Keep zero values
    assert filter_none_values({'a': 0, 'b': '', 'c': False}) == {'a': 0, 'b': '', 'c': False}


def test_encode_key_value_store_record_value() -> None:
    """Test encoding of key-value store record values."""
    # Dictionary should be encoded as JSON
    value, content_type = encode_key_value_store_record_value({'key': 'value'})
    assert b'"key"' in value
    assert b'"value"' in value
    assert content_type == 'application/json; charset=utf-8'

    # String should be text/plain
    value, content_type = encode_key_value_store_record_value('hello')
    assert value == 'hello'
    assert content_type == 'text/plain; charset=utf-8'

    # Bytes should be octet-stream
    value, content_type = encode_key_value_store_record_value(b'binary data')
    assert value == b'binary data'
    assert content_type == 'application/octet-stream'

    # Custom content type should be preserved
    value, content_type = encode_key_value_store_record_value('hello', 'text/html')
    assert value == 'hello'
    assert content_type == 'text/html'

    # BytesIO should be octet-stream
    buffer = io.BytesIO(b'buffer data')
    value, content_type = encode_key_value_store_record_value(buffer)
    assert value == buffer
    assert content_type == 'application/octet-stream'


def test_enum_to_value() -> None:
    """Test enum to value conversion."""

    class TestEnum(Enum):
        VALUE1 = 'val1'
        VALUE2 = 42

    assert enum_to_value(TestEnum.VALUE1) == 'val1'
    assert enum_to_value(TestEnum.VALUE2) == 42
    assert enum_to_value('not_an_enum') == 'not_an_enum'
    assert enum_to_value(123) == 123
    assert enum_to_value(None) is None


def test_response_to_dict() -> None:
    """Test parsing response as dictionary."""
    mock_response = Mock()
    mock_response.json.return_value = {'key': 'value'}

    result = response_to_dict(mock_response)
    assert result == {'key': 'value'}

    # Should raise for non-dict responses
    mock_response.json.return_value = ['list', 'response']
    with pytest.raises(ValueError, match='The response is not a dictionary'):
        response_to_dict(mock_response)

    mock_response.json.return_value = 'string'
    with pytest.raises(ValueError, match='The response is not a dictionary'):
        response_to_dict(mock_response)


def test_response_to_list() -> None:
    """Test parsing response as list."""
    mock_response = Mock()
    mock_response.json.return_value = ['item1', 'item2']

    result = response_to_list(mock_response)
    assert result == ['item1', 'item2']

    # Should raise for non-list responses
    mock_response.json.return_value = {'dict': 'response'}
    with pytest.raises(ValueError, match='The response is not a list'):
        response_to_list(mock_response)

    mock_response.json.return_value = 'string'
    with pytest.raises(ValueError, match='The response is not a list'):
        response_to_list(mock_response)


def test_encode_base62() -> None:
    """Test base62 encoding.

    charset = string.digits + string.ascii_letters
    So: 0-9 (0-9), a-z (10-35), A-Z (36-61)
    """
    assert encode_base62(0) == '0'
    assert encode_base62(1) == '1'
    assert encode_base62(9) == '9'
    assert encode_base62(10) == 'a'
    assert encode_base62(35) == 'z'
    assert encode_base62(36) == 'A'
    assert encode_base62(61) == 'Z'
    assert encode_base62(62) == '10'
    assert encode_base62(100) == '1C'
    assert encode_base62(123456) == 'w7e'


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


def test_create_storage_content_signature() -> None:
    """Test storage content signature creation."""
    # Non-expiring signature
    signature = create_storage_content_signature('resource_123', 'secret_key')
    assert isinstance(signature, str)
    assert len(signature) > 0

    # Expiring signature
    signature_expiring = create_storage_content_signature('resource_123', 'secret_key', expires_in_millis=60000)
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

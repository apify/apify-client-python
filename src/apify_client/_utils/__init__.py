"""Utility functions and helpers for the Apify client."""

from __future__ import annotations

from apify_client._utils.data import filter_none_values
from apify_client._utils.encoding import encode_key_value_store_record_value, encode_webhook_list_to_base64
from apify_client._utils.enums import enum_to_value
from apify_client._utils.errors import catch_not_found_or_throw, is_retryable_error
from apify_client._utils.identifiers import to_safe_id
from apify_client._utils.response import maybe_parse_response, response_to_dict, response_to_list
from apify_client._utils.retry import retry_with_exp_backoff, retry_with_exp_backoff_async
from apify_client._utils.signing import (
    create_hmac_signature,
    create_storage_content_signature,
    encode_base62,
)
from apify_client._utils.waiting import wait_for_finish_async, wait_for_finish_sync

__all__ = [
    # Errors
    'catch_not_found_or_throw',
    # Data manipulation
    'clean_request_dict',
    # Signing
    'create_hmac_signature',
    'create_storage_content_signature',
    'encode_base62',
    # Encoding
    'encode_key_value_store_record_value',
    'encode_webhook_list_to_base64',
    # Enums
    'enum_to_value',
    'is_retryable_error',
    # Response parsing
    'maybe_parse_response',
    'response_to_dict',
    'response_to_list',
    # Retry logic
    'retry_with_exp_backoff',
    'retry_with_exp_backoff_async',
    # Identifiers
    'to_safe_id',
    # Waiting
    'wait_for_finish_async',
    'wait_for_finish_sync',
]

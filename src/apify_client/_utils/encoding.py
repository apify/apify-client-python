"""Utilities for encoding data for API transmission."""

from __future__ import annotations

import base64
import io
import json
from typing import Any

from apify_client._utils.enums import enum_to_value


def encode_webhook_list_to_base64(webhooks: list[dict]) -> str:
    """Encode a list of webhook dictionaries to base64 for API transmission.

    Args:
        webhooks: List of webhook dictionaries with keys like "event_types", "request_url", etc.

    Returns:
        Base64-encoded JSON string.
    """
    data = list[dict]()
    for webhook in webhooks:
        webhook_representation = {
            'eventTypes': [enum_to_value(event_type) for event_type in webhook['event_types']],
            'requestUrl': webhook['request_url'],
        }
        if 'payload_template' in webhook:
            webhook_representation['payloadTemplate'] = webhook['payload_template']
        if 'headers_template' in webhook:
            webhook_representation['headersTemplate'] = webhook['headers_template']
        data.append(webhook_representation)

    return base64.b64encode(json.dumps(data).encode('utf-8')).decode('ascii')


def encode_key_value_store_record_value(value: Any, content_type: str | None = None) -> tuple[Any, str]:
    """Encode a value for storage in a key-value store record.

    Args:
        value: The value to encode (can be dict, str, bytes, or file-like object).
        content_type: The content type. If None, it's inferred from the value type.

    Returns:
        A tuple of (encoded_value, content_type).
    """
    if not content_type:
        if isinstance(value, (bytes, bytearray, io.IOBase)):
            content_type = 'application/octet-stream'
        elif isinstance(value, str):
            content_type = 'text/plain; charset=utf-8'
        else:
            content_type = 'application/json; charset=utf-8'

    if (
        'application/json' in content_type
        and not isinstance(value, (bytes, bytearray, io.IOBase))
        and not isinstance(value, str)
    ):
        value = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False, default=str).encode('utf-8')

    return (value, content_type)

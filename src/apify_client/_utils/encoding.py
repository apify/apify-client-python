from __future__ import annotations

import json
from base64 import b64encode
from functools import cache
from typing import TYPE_CHECKING, Any

from apify_client._models import WebhookCreate, WebhookRepresentation

if TYPE_CHECKING:
    from apify_client.types import WebhooksList


def encode_key_value_store_record_value(value: Any, *, content_type: str | None = None) -> tuple[Any, str]:
    """Encode a value for storage in a key-value store record.

    Args:
        value: The value to encode (can be dict, str, bytes, or file-like object).
        content_type: The content type; if None, it's inferred from the value type.

    Returns:
        A tuple of (encoded_value, content_type).
    """
    # Read file-like values into memory; the transport only accepts bytes-like bodies. Detect them by a
    # callable `read` (not `io.IOBase`) so duck-typed file-likes are read, not JSON-serialized.
    read = getattr(value, 'read', None)
    if callable(read):
        value = read()

    if not content_type:
        if isinstance(value, (bytes, bytearray)):
            content_type = 'application/octet-stream'
        elif isinstance(value, str):
            content_type = 'text/plain; charset=utf-8'
        else:
            content_type = 'application/json; charset=utf-8'

    if 'application/json' in content_type and not isinstance(value, (bytes, bytearray, str)):
        # Don't use indentation to reduce size.
        value = json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            default=str,
        ).encode('utf-8')

    return (value, content_type)


@cache
def _webhook_representation_keys() -> frozenset[str]:
    """Return all field names and aliases declared on `WebhookRepresentation`."""
    keys = set[str]()
    for name, info in WebhookRepresentation.model_fields.items():
        keys.add(name)
        if info.alias is not None:
            keys.add(info.alias)
    return frozenset(keys)


def encode_webhooks_to_base64(webhooks: WebhooksList | None) -> str | None:
    """Encode a list of ad-hoc webhooks to a base64 string for the `webhooks` query parameter.

    Returns `None` for `None` or an empty list, so the query parameter is omitted.

    See `WebhooksList` for the accepted shapes. `WebhookRepresentation` instances are used as-is. `WebhookCreate`
    instances and dict shapes are projected onto the fields `WebhookRepresentation` declares, dropping anything else
    (e.g. persistent-only fields like `condition`). Filtering by the declared field names and aliases means new
    ad-hoc fields added to `WebhookRepresentation` flow through automatically, without touching this function.
    """
    if not webhooks:
        return None

    representations = list[WebhookRepresentation]()
    allowed = _webhook_representation_keys()

    for webhook in webhooks:
        if isinstance(webhook, WebhookRepresentation):
            representations.append(webhook)
            continue

        data = webhook.model_dump(by_alias=True) if isinstance(webhook, WebhookCreate) else dict(webhook)
        filtered = {key: value for key, value in data.items() if key in allowed}
        representations.append(WebhookRepresentation.model_validate(filtered))

    data = [r.model_dump(by_alias=True, exclude_none=True) for r in representations]
    json_string = json.dumps(data).encode(encoding='utf-8')
    return b64encode(json_string).decode(encoding='ascii')

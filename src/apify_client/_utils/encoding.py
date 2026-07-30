from __future__ import annotations

import json
from base64 import b64encode
from functools import cache
from inspect import isawaitable, iscoroutine
from typing import TYPE_CHECKING, Any

from apify_client._models import WebhookCreate, WebhookRepresentation

if TYPE_CHECKING:
    from apify_client.types import WebhooksList


def encode_key_value_store_record_value(
    value: Any, *, content_type: str | None = None
) -> tuple[bytes | bytearray | str, str]:
    """Encode a value for storage in a key-value store record.

    Args:
        value: The value to encode. Anything exposing a callable `read` is treated as a file-like object: `read`
            is called with no arguments, so the value is consumed from its current position and buffered in
            memory whole - the object is neither rewound nor closed, and async file-like objects are rejected.
            Any other value is JSON-serialized unless it is already bytes or a string.
        content_type: The content type; if None, it's inferred from the value type.

    Returns:
        A tuple of (encoded_value, content_type).

    Raises:
        TypeError: If the value cannot be encoded into a body the transport accepts.
    """
    # Read file-like values into memory; the transport only accepts bytes-like bodies. Detect them by a
    # callable `read` (not `io.IOBase`) so duck-typed file-likes are read, not JSON-serialized. Impit exposes
    # no streaming `content=` API, so the value has to be buffered whole.
    read = getattr(value, 'read', None)
    if callable(read):
        value = read()

        if isawaitable(value):
            if iscoroutine(value):
                value.close()  # Prevent a "coroutine was never awaited" warning.
            raise TypeError(
                'Async file-like objects are not supported. Await the read yourself and pass the resulting '
                'bytes or string.'
            )

        if not isinstance(value, (bytes, bytearray, str)):
            raise TypeError(f'Reading the file-like value returned {type(value).__name__}, expected bytes or str.')

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

    # A non-JSON content type skips the serialization above, so anything that is not bytes-like would reach the
    # transport unencoded and fail there with an opaque error.
    if not isinstance(value, (bytes, bytearray, str)):
        raise TypeError(
            f'Cannot encode a {type(value).__name__} value as {content_type!r}. Pass bytes, a string, or a '
            'file-like object, or use a JSON content type.'
        )

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

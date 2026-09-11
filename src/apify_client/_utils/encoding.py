from __future__ import annotations

import io
import json
from base64 import b64encode
from functools import cache
from typing import TYPE_CHECKING, Any

from apify_client._models import WebhookCreate, WebhookRepresentation
from apify_client.http_clients._streamed_body import StreamedRequestBody

if TYPE_CHECKING:
    from apify_client.types import StreamedBodySource, WebhooksList


def encode_key_value_store_record_value(
    value: Any, *, content_type: str | None = None, content_encoding: str | None = None
) -> tuple[bytes | bytearray | str | StreamedBodySource, str]:
    """Encode a value for storage in a key-value store record.

    Args:
        value: The value to encode. A file-like object (anything with a callable `read`), an iterator of byte chunks,
            or a streamed `HttpResponse` is returned as it is, to be streamed to the API in chunks from its current
            position - the object is neither rewound nor closed. Any other value is JSON-serialized unless it is
            already bytes or a string.
        content_type: The content type; if None, it's inferred from the value type. A file opened in text mode is
            `text/plain; charset=utf-8`, any other streamed value is `application/octet-stream`.
        content_encoding: The encoding the caller declares the value already carries, if any. Anything other than
            `identity` means the value is compressed, which only a bytes-like payload can be, so a string, a
            JSON-serialized object, or a text-mode file is rejected. Any other streamed value is taken at its word,
            since its bytes are only seen as they are sent.

    Returns:
        A tuple of (encoded_value, content_type).

    Raises:
        TypeError: If the value cannot be encoded into a body the transport accepts, or if it cannot be carrying
            the declared `content_encoding`.
    """
    declared_encoding = (content_encoding or '').strip().lower()
    declares_compression = declared_encoding not in ('', 'identity')

    if StreamedRequestBody.is_source(value):
        is_text = isinstance(value, io.TextIOBase)
        if declares_compression and is_text:
            raise TypeError(
                f'Cannot upload a file-like value opened in text mode with `Content-Encoding: {content_encoding}`. '
                'An encoding other than `identity` declares the value is already compressed, so pass the compressed '
                'bytes, or a binary file-like object that reads them.'
            )
        return (value, content_type or ('text/plain; charset=utf-8' if is_text else 'application/octet-stream'))

    # A declared compression describes bytes the caller compressed. A string or a JSON-serializable object cannot
    # be carrying one, and would otherwise be stored under a header that misdescribes it - the client forwards the
    # header untouched and never inspects the body.
    if declares_compression and not isinstance(value, (bytes, bytearray)):
        raise TypeError(
            f'Cannot upload a {type(value).__name__} value with `Content-Encoding: {content_encoding}`. An encoding '
            'other than `identity` declares the value is already compressed, so pass the compressed bytes, or a '
            'file-like object that reads them.'
        )

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

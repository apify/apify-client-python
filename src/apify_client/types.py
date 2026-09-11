from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from datetime import timedelta
from typing import TYPE_CHECKING, Literal, Protocol

from apify_client._models import WebhookCreate, WebhookRepresentation
from apify_client._typeddicts import (
    WebhookCreateCamelDict,
    WebhookCreateDict,
    WebhookRepresentationCamelDict,
    WebhookRepresentationDict,
)
from apify_client.http_clients import HttpResponse, StreamedRequestBody

if TYPE_CHECKING:
    from collections.abc import Awaitable

HttpCompressionAlgorithm = Literal['brotli', 'gzip']
"""Accepted string literals for the `compression` parameter on `ApifyClient` and `ApifyClientAsync`."""

Timeout = timedelta | Literal['no_timeout', 'short', 'medium', 'long']
"""Type for the `timeout` parameter on resource client methods.

`'short'`, `'medium'`, and `'long'` are tier literals resolved by the HTTP client to configured values.
A `timedelta` overrides the timeout for this call, and `'no_timeout'` disables the timeout entirely.
"""

WebhooksList = (
    list[WebhookCreate]
    | list[WebhookCreateDict]
    | list[WebhookCreateCamelDict]
    | list[WebhookRepresentation]
    | list[WebhookRepresentationDict]
    | list[WebhookRepresentationCamelDict]
)
"""Type for the `webhooks` parameter on resource-client `start`/`call` methods and `from_webhooks`.

`WebhookRepresentation` / `WebhookRepresentationDict` / `WebhookRepresentationCamelDict` are the minimal ad-hoc
webhook shape (only `event_types` and `request_url` required). `WebhookCreate` / `WebhookCreateDict` /
`WebhookCreateCamelDict` are accepted so a persistent-webhook definition can be reused; their fields not relevant
to ad-hoc webhooks (e.g. `condition`) are ignored at runtime. The `*CamelDict` variants accept camelCase keys
matching the Apify API spelling.
"""


class SupportsRead(Protocol):
    """A file-like object a request body can be streamed from, for example an open file or an `io.BytesIO`.

    `read` is called with the chunk size until it returns an empty value. A file opened in text mode returns `str`
    chunks, which are UTF-8 encoded. An `async def read`, as `aiofiles` provides, is accepted by `ApifyClientAsync`.
    """

    def read(self, size: int, /) -> bytes | str | Awaitable[bytes | str]:
        """Read up to `size` bytes or characters, returning an empty value at the end."""


StreamedBodySource = (
    SupportsRead | Iterator[bytes | str] | AsyncIterator[bytes | str] | HttpResponse | StreamedRequestBody
)
"""Type for a request body the client streams to the API in chunks instead of holding it in memory whole.

A file-like object is read in chunks, an iterator or async iterator yields the chunks itself, and a streamed
`HttpResponse` forwards its body, which chains one API call's output into another's input. Accepted as the `data` of
`HttpClient.call`, as the `value` of `KeyValueStoreClient.set_record`, and as the `run_input` of Actor runs. See
`StreamedRequestBody` for the retry and compression rules that apply.

Pass a `StreamedRequestBody` built by hand to choose the chunk size a file-like source is read in, which no resource
client exposes on its own.
"""

JsonSerializable = dict[str, 'JsonSerializable'] | list['JsonSerializable'] | str | int | float | bool | None
"""Recursive type for JSON-serializable values - primitives plus objects and arrays with JSON-serializable contents.

Based on the definition discussed in https://github.com/python/typing/issues/182.
"""

__all__ = [
    'HttpCompressionAlgorithm',
    'JsonSerializable',
    'StreamedBodySource',
    'SupportsRead',
    'Timeout',
    'WebhooksList',
]

from __future__ import annotations

from collections.abc import AsyncIterable, Iterable
from datetime import timedelta
from typing import IO, TYPE_CHECKING, Literal, Protocol

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
    """A file-like object that is not an `io.IOBase` stream, read whole with a single `read()` call.

    Its result is sent as one chunk, so the source is held in memory whole and gets a single attempt. An `io.IOBase`
    stream, such as an open file or an `io.BytesIO`, is read in chunks instead. An `async def read`, as `aiofiles`
    provides, is accepted by `ApifyClientAsync`.
    """

    def read(self) -> bytes | str | Awaitable[bytes | str]:
        """Read the whole source."""


StreamedBodySource = (
    IO[bytes]
    | IO[str]
    | SupportsRead
    | Iterable[bytes | str]
    | AsyncIterable[bytes | str]
    | HttpResponse
    | StreamedRequestBody
)
"""Type for a request body the client streams to the API in chunks.

An `io.IOBase` stream is read in chunks, any other file-like object is read whole with one `read()` call, an iterable
or async iterable yields the chunks itself, and a streamed `HttpResponse` forwards its body, which chains one API
call's output into another's input. The iterable is any iterator, such as a generator, or an object that only
implements `__iter__` or `__aiter__`. A `Collection` - a `str`, `bytes`, `list`, `dict`, or any other sized container -
and a pydantic model are excluded at runtime as the values the client uploads whole or serializes as JSON, which the
static type cannot express. Accepted as the `data` of `HttpClient.call`, as the `value` of
`KeyValueStoreClient.set_record`, and as the `run_input` of Actor runs. See `StreamedRequestBody` for the retry and
compression rules that apply.

Pass a `StreamedRequestBody` built by hand to choose the chunk size an `io.IOBase` source is read in, which no
resource client exposes on its own.
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

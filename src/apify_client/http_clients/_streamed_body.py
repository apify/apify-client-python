from __future__ import annotations

import asyncio
import inspect
from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING, Any

from apify_client._consts import STREAMED_BODY_CHUNK_SIZE
from apify_client._docs import docs_group

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from typing import TypeGuard

    from apify_client.types import StreamedBodySource

_DONE = object()
"""Sentinel a worker thread returns once a synchronous iterator is exhausted."""


@docs_group('HTTP clients')
class StreamedRequestBody:
    """A request body sent from its source in chunks, so the body is never held in memory whole.

    `HttpClient.call` and `HttpClientAsync.call` wrap a `data` argument that is a file-like object, an iterator of
    byte chunks, or a streamed `HttpResponse` in this class. The transport pulls the chunks from `iter_bytes` or
    `aiter_bytes` and sends each one as it arrives, and the body is never compressed.

    The shared retry loop can send a body again only when its source is a seekable file-like object, in which case
    `rewind` seeks back to where the source was when the body was created. Any other source is consumed by the attempt
    that sends it, so the request gets a single attempt.

    A file opened in text mode, or an iterator yielding strings, is UTF-8 encoded chunk by chunk. A file-like object
    whose `read` is a coroutine function, as `aiofiles` provides, and an async iterator can only be sent by the
    asynchronous client.
    """

    def __init__(self, source: StreamedBodySource, *, chunk_size: int = STREAMED_BODY_CHUNK_SIZE) -> None:
        """Initialize the streamed request body.

        Args:
            source: The object the chunks come from. See `is_source` for the accepted kinds.
            chunk_size: Size, in bytes, of the chunks a file-like source is read in. An iterator or a response
                decides its own chunk sizes.

        Raises:
            TypeError: If `source` is not an object the body can be streamed from.
        """
        self._chunk_size = chunk_size
        self._error: Exception | None = None
        self._is_async = False

        # Exactly one of these produces the chunks: a file-like `read`, a factory of a synchronous iterable, or a
        # factory of an asynchronous one. A response provides both factories.
        self._read: Callable[[int], Any] | None = None
        self._sync_chunks: Callable[[], Iterable[Any]] | None = None
        self._async_chunks: Callable[[], AsyncIterator[Any]] | None = None

        # Set for a seekable file-like source, the only kind that can be sent more than once.
        self._seek: Callable[[int], Any] | None = None
        self._start: int | None = None

        read = getattr(source, 'read', None)
        if _is_response(source):
            self._sync_chunks = source.iter_bytes
            self._async_chunks = getattr(source, 'aiter_bytes', None)
        elif callable(read):
            self._read = read
            self._is_async = inspect.iscoroutinefunction(read)
            # The `seekable` check guards the `tell` call, which a pipe or a socket rejects. An async file-like
            # object also seeks asynchronously, so it is treated as a source that cannot be rewound.
            seekable = getattr(source, 'seekable', None)
            tell = getattr(source, 'tell', None)
            seek = getattr(source, 'seek', None)
            if not self._is_async and callable(seekable) and callable(tell) and callable(seek) and seekable():
                self._start = tell()
                self._seek = seek
        elif isinstance(source, Iterator):
            self._sync_chunks = lambda: source
        elif isinstance(source, AsyncIterator):
            self._async_chunks = lambda: source
            self._is_async = True
        else:
            raise TypeError(
                f'Cannot stream a request body from a {type(source).__name__}. Pass a file-like object, an iterator '
                'of byte chunks, or a streamed response.'
            )

    @staticmethod
    def is_source(value: object) -> TypeGuard[StreamedBodySource]:
        """Return whether a value is an object a request body can be streamed from.

        These are a streamed `HttpResponse` (anything with a callable `iter_bytes`), a file-like object (anything
        with a callable `read`), and an iterator or async iterator of byte chunks. A `str`, `bytes`, `bytearray`, or
        a container such as a `list` or `dict` is not a source, even though some of them can be iterated.
        """
        return (
            _is_response(value)
            or callable(getattr(value, 'read', None))
            or isinstance(value, (Iterator, AsyncIterator))
        )

    @property
    def is_async(self) -> bool:
        """Whether the chunks can only be produced asynchronously, so only `HttpClientAsync` can send the body."""
        return self._is_async

    @property
    def rewindable(self) -> bool:
        """Whether the body can be sent again after `rewind`, which only a seekable file-like source allows."""
        return self._seek is not None

    @property
    def error(self) -> Exception | None:
        """The exception the source raised while the chunks were pulled, if any.

        A transport reports such a failure as its own error, which may wrap the cause beyond recognition. The retry
        loop raises this exception instead, since sending the body again cannot fix its source.
        """
        return self._error

    def rewind(self) -> None:
        """Seek the source back to where it was when the body was created, so the body can be sent again.

        Raises:
            RuntimeError: If the source cannot be rewound. Check `rewindable` first.
        """
        if self._seek is None or self._start is None:
            raise RuntimeError('The source of the streamed request body cannot be rewound.')
        self._error = None
        self._seek(self._start)

    def iter_bytes(self) -> Iterator[bytes]:
        """Yield the body in chunks, reading a file-like source in `chunk_size` pieces.

        Raises:
            TypeError: If the source can only produce its chunks asynchronously, see `is_async`.
        """
        if self._is_async:
            raise TypeError(
                'The request body is streamed from an asynchronous source, which only the asynchronous client can '
                'send. Use `ApifyClientAsync`, or pass a synchronous file-like object or iterator.'
            )
        return self._iter_chunks()

    def aiter_bytes(self) -> AsyncIterator[bytes]:
        """Yield the body in chunks asynchronously, pulling a synchronous source in a worker thread.

        A blocking `read` or `__next__` would stall the event loop, so a synchronous file-like object or iterator is
        pulled through `asyncio.to_thread`, one chunk at a time.
        """
        return self._aiter_chunks()

    def _iter_chunks(self) -> Iterator[bytes]:
        try:
            if self._read is not None:
                # A file-like source signals its end with an empty read.
                while data := _to_bytes(self._read(self._chunk_size)):
                    yield data
            elif self._sync_chunks is not None:
                for chunk in self._sync_chunks():
                    # In chunked transfer encoding an empty chunk terminates the body, so none is passed on.
                    if data := _to_bytes(chunk):
                        yield data
        except Exception as exc:
            self._error = exc
            raise

    async def _aiter_chunks(self) -> AsyncIterator[bytes]:
        try:
            if self._read is not None:
                while True:
                    chunk = (
                        await self._read(self._chunk_size)
                        if self._is_async
                        else await asyncio.to_thread(self._read, self._chunk_size)
                    )
                    data = _to_bytes(chunk)
                    if not data:
                        return
                    yield data
            elif self._async_chunks is not None:
                async for chunk in self._async_chunks():
                    if data := _to_bytes(chunk):
                        yield data
            elif self._sync_chunks is not None:
                iterator = iter(self._sync_chunks())
                while (chunk := await asyncio.to_thread(_next_or_done, iterator)) is not _DONE:
                    if data := _to_bytes(chunk):
                        yield data
        except Exception as exc:
            self._error = exc
            raise


def _next_or_done(iterator: Iterator[Any]) -> Any:
    """Return the next item of a synchronous iterator, or `_DONE` once it is exhausted."""
    return next(iterator, _DONE)


def _is_response(value: object) -> TypeGuard[Any]:
    """Return whether a value is a streamed response, recognized by a callable `iter_bytes`."""
    return callable(getattr(value, 'iter_bytes', None))


def _to_bytes(chunk: object) -> bytes:
    """Convert one chunk to bytes, UTF-8 encoding a string.

    Raises:
        TypeError: If the chunk is neither bytes-like nor a string, for example `None` from a non-blocking stream
            with no data available, or a coroutine from an async `read` called synchronously.
    """
    if isinstance(chunk, bytes):
        return chunk
    if isinstance(chunk, (bytearray, memoryview)):
        return bytes(chunk)
    if isinstance(chunk, str):
        return chunk.encode('utf-8')
    raise TypeError(f'The streamed request body produced a {type(chunk).__name__} chunk, expected bytes or str.')

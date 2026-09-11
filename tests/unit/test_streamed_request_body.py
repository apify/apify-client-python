from __future__ import annotations

import io
from typing import TYPE_CHECKING, Any, cast

import pytest

from apify_client._consts import STREAMED_BODY_CHUNK_SIZE
from apify_client.http_clients import StreamedRequestBody

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator


class Reader:
    """A duck-typed file-like object: a callable `read`, no `io.IOBase` ancestry, no seeking."""

    def __init__(self, data: bytes) -> None:
        self._buffer = io.BytesIO(data)

    def read(self, size: int = -1) -> bytes:
        return self._buffer.read(size)


class AsyncReader:
    """A file-like object with a coroutine `read`, as `aiofiles` provides."""

    def __init__(self, data: bytes) -> None:
        self._buffer = io.BytesIO(data)

    async def read(self, size: int = -1) -> bytes:
        return self._buffer.read(size)


class FakeStreamedResponse:
    """The streaming half of the `HttpResponse` protocol, with both a sync and an async chunk iterator."""

    def __init__(self, chunks: list[bytes]) -> None:
        self.chunks = chunks

    def read(self) -> bytes:
        return b''.join(self.chunks)

    def iter_bytes(self) -> Iterator[bytes]:
        yield from self.chunks

    async def aiter_bytes(self) -> AsyncIterator[bytes]:
        for chunk in self.chunks:
            yield chunk


class SyncOnlyStreamedResponse:
    """A response-like object with only a synchronous chunk iterator."""

    def __init__(self, chunks: list[bytes]) -> None:
        self.chunks = chunks

    def iter_bytes(self) -> Iterator[bytes]:
        yield from self.chunks


def bytes_chunks() -> Iterator[bytes]:
    yield b'abc'
    yield b''
    yield b'def'


async def async_bytes_chunks() -> AsyncIterator[bytes]:
    yield b'abc'
    yield b''
    yield b'def'


@pytest.mark.parametrize(
    'value',
    [
        pytest.param(io.BytesIO(b'data'), id='binary file-like'),
        pytest.param(io.StringIO('data'), id='text-mode file-like'),
        pytest.param(Reader(b'data'), id='duck-typed reader'),
        pytest.param(AsyncReader(b'data'), id='async reader'),
        pytest.param(iter([b'data']), id='iterator'),
        pytest.param(bytes_chunks(), id='generator'),
        pytest.param(async_bytes_chunks(), id='async generator'),
        pytest.param(FakeStreamedResponse([b'data']), id='streamed response'),
    ],
)
def test_is_source(value: Any) -> None:
    """A file-like object, an iterator, an async iterator, and a streamed response can all feed a body."""
    assert StreamedRequestBody.is_source(value)


@pytest.mark.parametrize(
    'value',
    [
        pytest.param(b'data', id='bytes'),
        pytest.param(bytearray(b'data'), id='bytearray'),
        pytest.param('data', id='str'),
        pytest.param([b'data'], id='list of chunks'),
        pytest.param({'key': 'value'}, id='dict'),
        pytest.param(None, id='none'),
        pytest.param(42, id='int'),
    ],
)
def test_is_not_source(value: Any) -> None:
    """Buffered bodies and plain containers are not sources, even the iterable ones."""
    assert not StreamedRequestBody.is_source(value)


def test_rejects_non_source() -> None:
    """Building a body from a value that is not a source fails with a clear error."""
    with pytest.raises(TypeError, match='Cannot stream a request body from a list'):
        StreamedRequestBody(cast('Any', [b'data']))


def test_rejects_a_body_that_is_already_streamed() -> None:
    """Wrapping a body again would read it as a response and drop its rewind position, so it is refused."""
    body = StreamedRequestBody(io.BytesIO(b'data'))

    with pytest.raises(TypeError, match='already a streamed request body'):
        StreamedRequestBody(body)


def test_file_like_is_read_in_chunks_of_chunk_size() -> None:
    """A file-like source is pulled through `read(chunk_size)` until it runs dry."""
    body = StreamedRequestBody(io.BytesIO(b'x' * 10), chunk_size=4)

    assert list(body.iter_bytes()) == [b'xxxx', b'xxxx', b'xx']


def test_default_chunk_size_is_the_constant() -> None:
    """Without an explicit chunk size, a file-like source is read in `STREAMED_BODY_CHUNK_SIZE` pieces."""
    body = StreamedRequestBody(io.BytesIO(b'x' * (STREAMED_BODY_CHUNK_SIZE + 1)))

    assert [len(chunk) for chunk in body.iter_bytes()] == [STREAMED_BODY_CHUNK_SIZE, 1]


@pytest.mark.parametrize(
    ('source', 'expected'),
    [
        pytest.param(io.StringIO('héllo'), b'h\xc3\xa9llo', id='text-mode file-like'),
        pytest.param(iter(['hé', 'llo']), b'h\xc3\xa9llo', id='str iterator'),
        pytest.param(iter([bytearray(b'he'), memoryview(b'llo')]), b'hello', id='bytes-like chunks'),
    ],
)
def test_chunks_are_normalized_to_bytes(source: Any, expected: bytes) -> None:
    """String chunks are UTF-8 encoded and other bytes-like chunks are converted, whichever the source yields."""
    body = StreamedRequestBody(source)

    assert b''.join(body.iter_bytes()) == expected


def test_empty_iterator_chunks_are_skipped() -> None:
    """An empty chunk would terminate a chunked transfer, so it never reaches the transport."""
    body = StreamedRequestBody(bytes_chunks())

    assert list(body.iter_bytes()) == [b'abc', b'def']


def test_streamed_response_is_forwarded() -> None:
    """A streamed response feeds the body through its own chunk iterator."""
    body = StreamedRequestBody(cast('Any', FakeStreamedResponse([b'abc', b'def'])))

    assert list(body.iter_bytes()) == [b'abc', b'def']
    assert not body.is_async
    assert not body.rewindable


def test_seekable_file_like_is_rewindable_to_its_starting_position() -> None:
    """A seekable source can be sent again from where it was when the body was created, not from offset zero."""
    buffer = io.BytesIO(b'skip-rest')
    buffer.read(5)
    body = StreamedRequestBody(buffer)

    assert body.rewindable
    assert b''.join(body.iter_bytes()) == b'rest'
    assert b''.join(body.iter_bytes()) == b''

    body.rewind()

    assert b''.join(body.iter_bytes()) == b'rest'


def test_text_mode_file_like_is_rewindable() -> None:
    """A text file's opaque `tell` cookie works as the rewind position."""
    buffer = io.StringIO('skip-rest')
    buffer.read(5)
    body = StreamedRequestBody(buffer)
    list(body.iter_bytes())

    body.rewind()

    assert b''.join(body.iter_bytes()) == b'rest'


class NonSeekableBytesIO(io.BytesIO):
    """A binary stream that reports itself as non-seekable, like a pipe."""

    def seekable(self) -> bool:
        return False


@pytest.mark.parametrize(
    'source',
    [
        pytest.param(NonSeekableBytesIO(b'data'), id='non-seekable file-like'),
        pytest.param(Reader(b'data'), id='reader without seek support'),
        pytest.param(AsyncReader(b'data'), id='async reader'),
        pytest.param(iter([b'data']), id='iterator'),
        pytest.param(async_bytes_chunks(), id='async iterator'),
        pytest.param(FakeStreamedResponse([b'data']), id='streamed response'),
    ],
)
def test_is_not_rewindable(source: Any) -> None:
    """Everything but a seekable file-like source is consumed once, and says so."""
    body = StreamedRequestBody(source)

    assert not body.rewindable
    with pytest.raises(RuntimeError, match='cannot be rewound'):
        body.rewind()


@pytest.mark.parametrize(
    'source',
    [
        pytest.param(AsyncReader(b'data'), id='async reader'),
        pytest.param(async_bytes_chunks(), id='async iterator'),
    ],
)
def test_async_source_cannot_be_iterated_synchronously(source: Any) -> None:
    """An asynchronous source is rejected up front, before the transport pulls a single chunk."""
    body = StreamedRequestBody(source)

    assert body.is_async
    with pytest.raises(TypeError, match='Use `ApifyClientAsync`'):
        body.iter_bytes()


@pytest.mark.parametrize(
    'source',
    [
        pytest.param(io.BytesIO(b'data'), id='binary file-like'),
        pytest.param(Reader(b'data'), id='duck-typed reader'),
        pytest.param(iter([b'data']), id='iterator'),
        pytest.param(FakeStreamedResponse([b'data']), id='streamed response'),
    ],
)
def test_sync_source_is_not_async(source: Any) -> None:
    """A synchronous source works with both clients."""
    assert not StreamedRequestBody(source).is_async


@pytest.mark.parametrize(
    ('source', 'expected'),
    [
        pytest.param(io.BytesIO(b'x' * 10), [b'xxxx', b'xxxx', b'xx'], id='binary file-like'),
        pytest.param(io.StringIO('héllo'), [b'h\xc3\xa9ll', b'o'], id='text-mode file-like'),
        pytest.param(Reader(b'x' * 10), [b'xxxx', b'xxxx', b'xx'], id='duck-typed reader'),
        pytest.param(AsyncReader(b'x' * 10), [b'xxxx', b'xxxx', b'xx'], id='async reader'),
        pytest.param(bytes_chunks(), [b'abc', b'def'], id='generator'),
        pytest.param(async_bytes_chunks(), [b'abc', b'def'], id='async generator'),
        pytest.param(FakeStreamedResponse([b'abc', b'def']), [b'abc', b'def'], id='streamed response'),
        pytest.param(SyncOnlyStreamedResponse([b'abc', b'def']), [b'abc', b'def'], id='sync-only response'),
    ],
)
async def test_aiter_bytes_handles_every_source_kind(source: Any, expected: list[bytes]) -> None:
    """The asynchronous iteration reads file-likes in chunks and forwards iterators, sync or async."""
    body = StreamedRequestBody(source, chunk_size=4)

    assert [chunk async for chunk in body.aiter_bytes()] == expected


class NoneReader:
    """Mimics a non-blocking raw stream with no data available: `read` returns `None`."""

    def read(self, size: int = -1) -> None:
        _ = size


def test_bad_chunk_raises_and_is_recorded_as_the_error() -> None:
    """A chunk that is neither bytes-like nor text fails the body, and the failure is kept for the retry loop."""
    body = StreamedRequestBody(cast('Any', NoneReader()))

    with pytest.raises(TypeError, match='produced a NoneType chunk') as exc_info:
        list(body.iter_bytes())

    assert body.error is exc_info.value


class FailingReader:
    """A file-like object whose second read fails, like a disk error halfway through a file."""

    def __init__(self) -> None:
        self._reads = 0

    def read(self, size: int = -1) -> bytes:
        _ = size
        self._reads += 1
        if self._reads > 1:
            raise OSError('disk on fire')
        return b'first chunk'


def test_source_failure_is_recorded_as_the_error() -> None:
    """An exception from the source propagates and is kept, so the retry loop can raise it instead of a wrapper."""
    body = StreamedRequestBody(FailingReader())
    chunks = body.iter_bytes()

    assert next(chunks) == b'first chunk'
    with pytest.raises(OSError, match='disk on fire') as exc_info:
        next(chunks)
    assert body.error is exc_info.value


async def test_source_failure_is_recorded_as_the_error_async() -> None:
    """The asynchronous iteration keeps a source failure the same way."""
    body = StreamedRequestBody(FailingReader())

    with pytest.raises(OSError, match='disk on fire') as exc_info:
        _ = [chunk async for chunk in body.aiter_bytes()]
    assert body.error is exc_info.value


def test_rewind_clears_the_error() -> None:
    """A rewound body starts the next attempt with a clean slate."""

    class FailOnceBuffer(io.BytesIO):
        def __init__(self) -> None:
            super().__init__(b'data')
            self.fail = True

        def read(self, size: int | None = -1) -> bytes:
            if self.fail:
                self.fail = False
                raise OSError('transient')
            return super().read(size)

    body = StreamedRequestBody(FailOnceBuffer())
    with pytest.raises(OSError, match='transient'):
        list(body.iter_bytes())
    assert body.error is not None

    body.rewind()

    assert body.error is None
    assert b''.join(body.iter_bytes()) == b'data'

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, Mock

import pytest

from apify_client._streamed_log import StreamedLogAsync, StreamedLogBase

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


@pytest.mark.parametrize(
    ('chunks', 'expected_calls'),
    [
        pytest.param(
            [b'2025-05-13T07:24:12.588Z first\n2025-05-13T07:24:13', b'.588Z second\n'],
            [(logging.INFO, '2025-05-13T07:24:12.588Z first'), (logging.INFO, '2025-05-13T07:24:13.588Z second')],
            id='marker-split-across-chunks',
        ),
        pytest.param(
            [b'2025-05-13T07:24:12.588Z unterminated'],
            [],
            id='unterminated-line-waits-for-newline',
        ),
        pytest.param(
            [b'preamble without marker\n', b'2025-05-13T07:24:12.588Z first\n'],
            [(logging.INFO, '2025-05-13T07:24:12.588Z first')],
            id='text-before-first-message-is-skipped',
        ),
    ],
)
def test_streamed_log_redirects_each_complete_line(chunks: list[bytes], expected_calls: list[tuple[int, str]]) -> None:
    """Each chunk redirects the messages its newlines complete and keeps only the unterminated rest."""
    to_logger = Mock(spec=logging.Logger)
    streamed_log = StreamedLogBase(to_logger)

    for chunk in chunks:
        streamed_log._process_new_data(chunk)

    calls = [(call.kwargs['level'], call.kwargs['msg']) for call in to_logger.log.call_args_list]
    assert calls == expected_calls


@pytest.mark.parametrize(
    ('content', 'level'),
    [
        pytest.param('INFO  Saved ERROR_PAGE screenshot', logging.INFO, id='info-with-error-text'),
        pytest.param('DEBUG WARNING in payload', logging.DEBUG, id='debug-with-warning-text'),
        pytest.param('ERROR failed\nCRITICAL detail', logging.ERROR, id='multiline'),
        pytest.param('[apify] DEBUG ERROR in payload', logging.DEBUG, id='logger-prefix'),
        pytest.param('WARNING warning', logging.WARNING, id='warning'),
        pytest.param('FATAL failed', logging.FATAL, id='fatal'),
        pytest.param('ERROR_PAGE saved', logging.INFO, id='unknown-token'),
        pytest.param('Saved ERROR screenshot', logging.INFO, id='no-level'),
        pytest.param('', logging.INFO, id='empty'),
    ],
)
def test_streamed_log_level_uses_token(content: str, level: int) -> None:
    """Only the level token immediately after the timestamp determines severity."""
    logger = Mock(spec=logging.Logger)
    stream = StreamedLogBase(logger)
    stream._process_whole_log(f'2026-11-15T13:00:00.000Z {content}'.encode())
    assert logger.log.call_args.kwargs['level'] == level


async def test_async_stop_drains_in_flight_chunk() -> None:
    """Stopping lets the last in-flight chunk reach the logger before the stream ends."""
    delivered = asyncio.Event()
    release = asyncio.Event()

    async def chunks() -> AsyncIterator[bytes]:
        yield b'2026-11-15T13:00:00.000Z INFO first\n'
        delivered.set()
        await release.wait()
        yield b'2026-11-15T13:00:01.000Z INFO last\n'

    response = Mock()
    response.aiter_bytes.side_effect = chunks
    context = AsyncMock()
    context.__aenter__.return_value = response
    client = Mock()
    client.stream.return_value = context
    logger = Mock(spec=logging.Logger)
    stream = StreamedLogAsync(client, to_logger=logger)
    task = stream.start()
    await delivered.wait()
    asyncio.get_running_loop().call_soon(release.set)
    await stream.stop()
    assert not task.cancelled()
    assert len(logger.log.call_args_list) == 2
    assert logger.log.call_args.kwargs['msg'].endswith('INFO last')


async def test_async_stop_cancels_silent_stream(monkeypatch: pytest.MonkeyPatch) -> None:
    """A stream that stays silent is cancelled after the grace period."""
    logger = Mock(spec=logging.Logger)
    stream = StreamedLogAsync(Mock(), to_logger=logger)
    monkeypatch.setattr(StreamedLogAsync, '_stop_timeout_s', 0.01, raising=False)
    stream._received_data = True
    task = asyncio.create_task(asyncio.Event().wait())
    stream._streaming_task = task
    await stream.stop()
    assert task.cancelled()
    assert stream._streaming_task is None


async def test_async_stop_cancels_stream_when_caller_is_cancelled() -> None:
    """Cancelling stop during the grace period must not leave it waiting for the stream."""
    stream = StreamedLogAsync(Mock(), to_logger=Mock(spec=logging.Logger))
    stream._received_data = True
    task = asyncio.create_task(asyncio.Event().wait())
    stream._streaming_task = task
    stopper = asyncio.create_task(stream.stop())
    await asyncio.sleep(0)
    stopper.cancel()
    try:
        done, _ = await asyncio.wait({stopper}, timeout=0.1)
        assert stopper in done
        assert task.cancelled()
        assert stream._streaming_task is None
    finally:
        task.cancel()
        await asyncio.gather(task, stopper, return_exceptions=True)

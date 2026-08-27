from __future__ import annotations

import asyncio
import logging
import re
import threading
from asyncio import Task
from datetime import UTC, datetime
from threading import Thread
from typing import TYPE_CHECKING, ClassVar, Self, cast

from apify_client._docs import docs_group

if TYPE_CHECKING:
    from types import TracebackType

    from apify_client._resource_clients import LogClient, LogClientAsync
    from apify_client.http_clients import HttpResponse
    from apify_client.types import Timeout


class StreamedLogBase:
    """Base class for streaming and buffering chunked Actor run logs."""

    _force_propagate = False
    """Test related flag to enable propagation of logs to the `caplog` fixture during tests."""

    _stream_timeout: ClassVar[Timeout] = 'no_timeout'
    """Timeout for the log-stream long-poll request, which stays open for the whole Actor run.

    A bounded transport timeout can truncate a longer run mid-stream. `no_timeout` keeps the connection open for the
    duration of the run (Impit currently maps it to an effective 24-hour cap) and mirrors the JS client.
    """

    def __init__(self, to_logger: logging.Logger, *, from_start: bool = True) -> None:
        if self._force_propagate:
            to_logger.propagate = True
        self._to_logger = to_logger
        self._stream_buffer = list[bytes]()
        self._split_marker = re.compile(rb'(?:\n|^)(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)')
        self._relevancy_time_limit: datetime | None = None if from_start else datetime.now(tz=UTC)

    def _process_new_data(self, data: bytes) -> None:
        new_chunk = data
        self._stream_buffer.append(new_chunk)
        if re.findall(self._split_marker, new_chunk):
            # If complete split marker was found in new chunk, then log the buffer.
            self._log_buffer_content(include_last_part=False)

    def _log_buffer_content(self, *, include_last_part: bool = False) -> None:
        """Merge the whole buffer and split it into parts based on the marker.

        Log the messages created from the split parts and remove them from buffer.
        The last part could be incomplete, and so it can be left unprocessed in the buffer until later.
        """
        all_parts = re.split(self._split_marker, b''.join(self._stream_buffer))[1:]  # The First split is empty
        if include_last_part:
            message_markers = all_parts[0::2]
            message_contents = all_parts[1::2]
            self._stream_buffer = []
        else:
            message_markers = all_parts[0:-2:2]
            message_contents = all_parts[1:-2:2]
            # The last two parts (marker and message) are possibly not complete and will be left in the buffer
            self._stream_buffer = all_parts[-2:]

        for marker, content in zip(message_markers, message_contents, strict=False):
            decoded_marker = marker.decode('utf-8')
            decoded_content = content.decode('utf-8')
            if self._relevancy_time_limit:
                log_time = datetime.fromisoformat(decoded_marker)
                if log_time < self._relevancy_time_limit:
                    # Skip irrelevant logs
                    continue
            message = decoded_marker + decoded_content
            self._to_logger.log(level=self._guess_log_level_from_message(message), msg=message.strip())

    @staticmethod
    def _guess_log_level_from_message(message: str) -> int:
        """Guess the log level from the message."""
        # Using only levels explicitly mentioned in the logging module
        known_levels = ('CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET')
        for level in known_levels:
            if level in message:
                # `getLevelName` returns an `int` when string is passed as input.
                return cast('int', logging.getLevelName(level))
        # Unknown log level. Fall back to the default.
        return logging.INFO


@docs_group('Other')
class StreamedLog(StreamedLogBase):
    """Streams Actor run log output to a Python logger in a background thread.

    The log stream is consumed in a background thread and each log message is forwarded to the provided logger with
    an appropriate log level inferred from the message content.

    Can be used as a context manager, which automatically starts and stops the streaming thread. Alternatively,
    call `start` and `stop` manually. Obtain an instance via `RunClient.get_streamed_log`.
    """

    _stop_timeout_s: ClassVar[float] = 5
    """Upper bound on how long `stop` waits for the streaming thread to finish.

    Closing the response only ends the read on a transport that honours it, which neither Impit nor HTTPX does, so
    without a bound `stop` would wait for the next chunk, which on a quiet run may be hours away.
    """

    def __init__(self, log_client: LogClient, *, to_logger: logging.Logger, from_start: bool = True) -> None:
        """Initialize `StreamedLog`.

        Args:
            log_client: The log client used to stream raw log data from the Actor run.
            to_logger: The logger to which the log messages will be forwarded.
            from_start: If `True`, all logs from the start of the Actor run will be streamed. If `False`, only newly
                arrived logs will be streamed. This can be useful for long-running Actors in stand-by mode where only
                recent logs are relevant.
        """
        super().__init__(to_logger=to_logger, from_start=from_start)
        self._log_client = log_client
        self._streaming_thread: Thread | None = None
        self._log_stream: HttpResponse | None = None
        self._stop_logging = False

    def start(self) -> Thread:
        """Start the streaming thread.

        The caller is responsible for cleanup by calling the `stop` method when done.
        """
        if self._streaming_thread and self._streaming_thread.is_alive():
            raise RuntimeError('Streaming thread already active')
        self._stop_logging = False
        # A daemon thread so a stream still blocked on a read can never hold up interpreter shutdown.
        self._streaming_thread = threading.Thread(target=self._stream_log, daemon=True)
        self._streaming_thread.start()
        return self._streaming_thread

    def stop(self) -> None:
        """Signal the streaming thread to stop logging and wait up to `_stop_timeout_s` for it to finish.

        A thread that outlives the wait is a daemon with `_stop_logging` set, so it exits after at most one more chunk,
        and only then does its buffered tail reach the logger. Its handle is kept while it is alive, so `start` cannot
        revive it beside a second thread on the same buffer.
        """
        if not self._streaming_thread:
            raise RuntimeError('Streaming thread is not active')
        self._stop_logging = True
        # Read once; the streaming thread clears the attribute as soon as the stream ends.
        log_stream = self._log_stream
        if log_stream is not None:
            try:
                log_stream.close()
            except Exception:
                # A failing `close` in a custom transport must not fail the caller.
                self._to_logger.exception('Closing the log stream failed:')
        self._streaming_thread.join(timeout=self._stop_timeout_s)
        if self._streaming_thread.is_alive():
            # Otherwise log messages arriving after `stop` returned have no explanation.
            self._to_logger.debug('Log streaming thread outlived the stop timeout; it ends after the next chunk.')
        else:
            self._streaming_thread = None

    def __enter__(self) -> Self:
        """Start the streaming thread within the context. Exiting the context will finish the streaming thread."""
        self.start()
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        """Stop the streaming thread."""
        self.stop()

    def _stream_log(self) -> None:
        try:
            with self._log_client.stream(raw=True, timeout=self._stream_timeout) as log_stream:
                if not log_stream:
                    return
                # Published so `stop` can close the response.
                self._log_stream = log_stream
                try:
                    # `stop` may have run before the response existed for it to close.
                    if self._stop_logging:
                        return
                    for data in log_stream.iter_bytes():
                        self._process_new_data(data)
                        if self._stop_logging:
                            break
                finally:
                    self._log_stream = None
                    # Flush the last buffered part even if the read timed out or was stopped.
                    self._log_buffer_content(include_last_part=True)
        except Exception as exc:
            if self._stop_logging:
                # Expected during a stop, but this also catches a failed flush of the buffered tail, so report it.
                self._to_logger.debug('Log streaming stopped while `stop` was in progress: %r', exc)
                return
            if self._log_client._http_client.is_timeout_error(exc):  # noqa: SLF001
                # The stream cannot continue, so warn and let the thread end instead of leaking a traceback.
                self._to_logger.warning('Log streaming stopped: the log stream request timed out.')
            else:
                # Any other failure in log redirection must not escape the background thread; log it instead.
                self._to_logger.exception('Log redirection stopped due to unexpected error:')


@docs_group('Other')
class StreamedLogAsync(StreamedLogBase):
    """Streams Actor run log output to a Python logger in an asyncio task.

    The log stream is consumed in a background asyncio task and each log message is forwarded to the provided logger
    with an appropriate log level inferred from the message content.

    Can be used as an async context manager, which automatically starts and cancels the streaming task. Alternatively,
    call `start` and `stop` manually. Obtain an instance via `RunClientAsync.get_streamed_log`.
    """

    def __init__(self, log_client: LogClientAsync, *, to_logger: logging.Logger, from_start: bool = True) -> None:
        """Initialize `StreamedLogAsync`.

        Args:
            log_client: The async log client used to stream raw log data from the Actor run.
            to_logger: The logger to which the log messages will be forwarded.
            from_start: If `True`, all logs from the start of the Actor run will be streamed. If `False`, only newly
                arrived logs will be streamed. This can be useful for long-running Actors in stand-by mode where only
                recent logs are relevant.
        """
        super().__init__(to_logger=to_logger, from_start=from_start)
        self._log_client = log_client
        self._streaming_task: Task | None = None

    def start(self) -> Task:
        """Start the streaming task.

        The caller is responsible for cleanup by calling the `stop` method when done.
        """
        if self._streaming_task and not self._streaming_task.done():
            raise RuntimeError('Streaming task already active')
        self._streaming_task = asyncio.create_task(self._stream_log())
        return self._streaming_task

    async def stop(self) -> None:
        """Stop the streaming task."""
        if not self._streaming_task:
            raise RuntimeError('Streaming task is not active')

        self._streaming_task.cancel()
        try:
            await self._streaming_task
        except asyncio.CancelledError:
            pass
        finally:
            self._streaming_task = None

    async def __aenter__(self) -> Self:
        """Start the streaming task within the context. Exiting the context will cancel the streaming task."""
        self.start()
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        """Cancel the streaming task."""
        await self.stop()

    async def _stream_log(self) -> None:
        try:
            async with self._log_client.stream(raw=True, timeout=self._stream_timeout) as log_stream:
                if not log_stream:
                    return
                try:
                    async for data in log_stream.aiter_bytes():
                        self._process_new_data(data)
                finally:
                    # Flush the last buffered part even if the task is cancelled by `stop()`.
                    self._log_buffer_content(include_last_part=True)
        except Exception as exc:
            if self._log_client._http_client.is_timeout_error(exc):  # noqa: SLF001
                # A timeout on the long-lived stream is an expected terminal condition, not an error.
                self._to_logger.warning('Log streaming stopped: the log stream request timed out.')
            else:
                # Exception in log redirection should not propagate further.
                self._to_logger.exception('Log redirection stopped due to unexpected error:')

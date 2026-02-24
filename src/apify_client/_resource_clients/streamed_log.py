from __future__ import annotations

import asyncio
import logging
import re
import threading
from asyncio import Task
from datetime import UTC, datetime
from threading import Thread
from typing import TYPE_CHECKING, Self, cast

if TYPE_CHECKING:
    from types import TracebackType

    from apify_client._resource_clients import LogClient, LogClientAsync


class StreamedLog:
    """Utility class for streaming logs from another Actor.

    It uses buffer to deal with possibly chunked logs. Chunked logs are stored in buffer. Chunks are expected to contain
    specific markers that indicate the start of the log message. Each time a new chunk with complete split marker
    arrives, the buffer is processed, logged and emptied.

    This works only if the logs have datetime marker in ISO format. For example, `2025-05-12T15:35:59.429Z` This is the
    default log standard for the Actors.
    """

    # Test related flag to enable propagation of logs to the `caplog` fixture during tests.
    _force_propagate = False

    def __init__(self, to_logger: logging.Logger, *, from_start: bool = True) -> None:
        """Initialize `StreamedLog`.

        Args:
            to_logger: The logger to which the logs will be redirected.
            from_start: If `True`, all logs from the start of the Actor run will be redirected. If `False`, only newly
                arrived logs will be redirected. This can be useful for redirecting only a small portion of relevant
                logs for long-running Actors in stand-by.

        """
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


class StreamedLogSync(StreamedLog):
    """Sync variant of `StreamedLog` that is logging in threads."""

    def __init__(self, log_client: LogClient, *, to_logger: logging.Logger, from_start: bool = True) -> None:
        super().__init__(to_logger=to_logger, from_start=from_start)
        self._log_client = log_client
        self._streaming_thread: Thread | None = None
        self._stop_logging = False

    def start(self) -> Thread:
        """Start the streaming thread. The caller has to handle any cleanup by manually calling the `stop` method."""
        if self._streaming_thread:
            raise RuntimeError('Streaming thread already active')
        self._stop_logging = False
        self._streaming_thread = threading.Thread(target=self._stream_log)
        self._streaming_thread.start()
        return self._streaming_thread

    def stop(self) -> None:
        """Signal the streaming thread to stop logging and wait for it to finish."""
        if not self._streaming_thread:
            raise RuntimeError('Streaming thread is not active')
        self._stop_logging = True
        self._streaming_thread.join()
        self._streaming_thread = None
        self._stop_logging = False

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
        with self._log_client.stream(raw=True) as log_stream:
            if not log_stream:
                return
            for data in log_stream.iter_bytes():
                self._process_new_data(data)
                if self._stop_logging:
                    break

            # If the stream is finished, then the last part will be also processed.
            self._log_buffer_content(include_last_part=True)
        return


class StreamedLogAsync(StreamedLog):
    """Async variant of `StreamedLog` that is logging in tasks."""

    def __init__(self, log_client: LogClientAsync, *, to_logger: logging.Logger, from_start: bool = True) -> None:
        super().__init__(to_logger=to_logger, from_start=from_start)
        self._log_client = log_client
        self._streaming_task: Task | None = None

    def start(self) -> Task:
        """Start the streaming task. The caller has to handle any cleanup by manually calling the `stop` method."""
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
        async with self._log_client.stream(raw=True) as log_stream:
            if not log_stream:
                return
            async for data in log_stream.aiter_bytes():
                self._process_new_data(data)

            # If the stream is finished, then the last part will be also processed.
            self._log_buffer_content(include_last_part=True)

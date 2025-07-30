from __future__ import annotations

import asyncio
import logging
import re
import threading
import time
from asyncio import Task
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timedelta, timezone
from threading import Thread
from typing import TYPE_CHECKING, Any, cast

from apify_shared.utils import ignore_docs

from apify_client._errors import ApifyApiError
from apify_client._utils import catch_not_found_or_throw
from apify_client.clients.base import ResourceClient, ResourceClientAsync

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator
    from types import TracebackType

    import httpx
    from typing_extensions import Self

    from apify_client.clients import RunClient, RunClientAsync


class LogClient(ResourceClient):
    """Sub-client for manipulating logs."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'logs')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self, *, raw: bool = False) -> str | None:
        """Retrieve the log as text.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Args:
            raw: If true, the log will include formating. For example, coloring character sequences.

        Returns:
            The retrieved log, or None, if it does not exist.
        """
        try:
            response = self.http_client.call(
                url=self.url,
                method='GET',
                params=self._params(raw=raw),
            )

            return response.text  # noqa: TRY300

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    def get_as_bytes(self, *, raw: bool = False) -> bytes | None:
        """Retrieve the log as raw bytes.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Args:
            raw: If true, the log will include formating. For example, coloring character sequences.

        Returns:
            The retrieved log as raw bytes, or None, if it does not exist.
        """
        try:
            response = self.http_client.call(
                url=self.url,
                method='GET',
                params=self._params(raw=raw),
                parse_response=False,
            )

            return response.content  # noqa: TRY300

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    @contextmanager
    def stream(self, *, raw: bool = False) -> Iterator[httpx.Response | None]:
        """Retrieve the log as a stream.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Args:
            raw: If true, the log will include formating. For example, coloring character sequences.

        Returns:
            The retrieved log as a context-managed streaming `Response`, or None, if it does not exist.
        """
        response = None
        try:
            response = self.http_client.call(
                url=self.url,
                method='GET',
                params=self._params(stream=True, raw=raw),
                stream=True,
                parse_response=False,
            )

            yield response
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            yield None
        finally:
            if response:
                response.close()


class LogClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating logs."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'logs')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self, *, raw: bool = False) -> str | None:
        """Retrieve the log as text.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Args:
            raw: If true, the log will include formating. For example, coloring character sequences.

        Returns:
            The retrieved log, or None, if it does not exist.
        """
        try:
            response = await self.http_client.call(
                url=self.url,
                method='GET',
                params=self._params(raw=raw),
            )

            return response.text  # noqa: TRY300

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    async def get_as_bytes(self, *, raw: bool = False) -> bytes | None:
        """Retrieve the log as raw bytes.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Args:
            raw: If true, the log will include formating. For example, coloring character sequences.

        Returns:
            The retrieved log as raw bytes, or None, if it does not exist.
        """
        try:
            response = await self.http_client.call(
                url=self.url,
                method='GET',
                params=self._params(raw=raw),
                parse_response=False,
            )

            return response.content  # noqa: TRY300

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    @asynccontextmanager
    async def stream(self, *, raw: bool = False) -> AsyncIterator[httpx.Response | None]:
        """Retrieve the log as a stream.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Args:
            raw: If true, the log will include formating. For example, coloring character sequences.

        Returns:
            The retrieved log as a context-managed streaming `Response`, or None, if it does not exist.
        """
        response = None
        try:
            response = await self.http_client.call(
                url=self.url,
                method='GET',
                params=self._params(stream=True, raw=raw),
                stream=True,
                parse_response=False,
            )

            yield response
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            yield None
        finally:
            if response:
                await response.aclose()


class StreamedLog:
    """Utility class for streaming logs from another Actor.

    It uses buffer to deal with possibly chunked logs. Chunked logs are stored in buffer. Chunks are expected to contain
    specific markers that indicate the start of the log message. Each time a new chunk with complete split marker
    arrives, the buffer is processed, logged and emptied.

    This works only if the logs have datetime marker in ISO format. For example, `2025-05-12T15:35:59.429Z` This is the
    default log standard for the actors.
    """

    # Test related flag to enable propagation of logs to the `caplog` fixture during tests.
    _force_propagate = False

    def __init__(self, to_logger: logging.Logger, *, from_start: bool = True) -> None:
        """Initialize `StreamedLog`.

        Args:
            to_logger: The logger to which the logs will be redirected.
            from_start: If `True`, all logs from the start of the actor run will be redirected. If `False`, only newly
                arrived logs will be redirected. This can be useful for redirecting only a small portion of relevant
                logs for long-running actors in stand-by.

        """
        if self._force_propagate:
            to_logger.propagate = True
        self._to_logger = to_logger
        self._stream_buffer = list[bytes]()
        self._split_marker = re.compile(rb'(?:\n|^)(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)')
        self._relevancy_time_limit: datetime | None = None if from_start else datetime.now(tz=timezone.utc)

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

        for marker, content in zip(message_markers, message_contents):
            decoded_marker = marker.decode('utf-8')
            decoded_content = content.decode('utf-8')
            if self._relevancy_time_limit:
                log_time = datetime.fromisoformat(decoded_marker.replace('Z', '+00:00'))
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
        if self._streaming_task:
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


class StatusMessageWatcher:
    """Utility class for logging status messages from another Actor run.

    Status message is logged at fixed time intervals, and there is no guarantee that all messages will be logged,
    especially in cases of frequent status message changes.
    """

    _force_propagate = False
    # This is final sleep time to try to get the last status and status message of finished Actor run.
    # The status and status message can get set on the Actor run with a delay. Sleep time does not guarantee that the
    # final message will be captured, but increases the chances of that.
    _final_sleep_time_s = 6

    def __init__(self, *, to_logger: logging.Logger, check_period: timedelta = timedelta(seconds=5)) -> None:
        """Initialize `StatusMessageWatcher`.

        Args:
            to_logger: The logger to which the status message will be redirected.
            check_period: The period with which the status message will be polled.
        """
        if self._force_propagate:
            to_logger.propagate = True
        self._to_logger = to_logger
        self._check_period = check_period.total_seconds()
        self._last_status_message = ''

    def _log_run_data(self, run_data: dict[str, Any] | None) -> bool:
        """Get relevant run data, log them if changed and return `True` if more data is expected.

        Args:
            run_data: The dictionary that contains the run data.

        Returns:
              `True` if more data is expected, `False` otherwise.
        """
        if run_data is not None:
            status = run_data.get('status', 'Unknown status')
            status_message = run_data.get('statusMessage', '')
            new_status_message = f'Status: {status}, Message: {status_message}'

            if new_status_message != self._last_status_message:
                self._last_status_message = new_status_message
                self._to_logger.info(new_status_message)

            return not (run_data.get('isStatusMessageTerminal', False))
        return True


class StatusMessageWatcherAsync(StatusMessageWatcher):
    """Async variant of `StatusMessageWatcher` that is logging in task."""

    def __init__(
        self, *, run_client: RunClientAsync, to_logger: logging.Logger, check_period: timedelta = timedelta(seconds=1)
    ) -> None:
        """Initialize `StatusMessageWatcherAsync`.

        Args:
            run_client: The client for run that will be used to get a status and message.
            to_logger: The logger to which the status message will be redirected.
            check_period: The period with which the status message will be polled.
        """
        super().__init__(to_logger=to_logger, check_period=check_period)
        self._run_client = run_client
        self._logging_task: Task | None = None

    def start(self) -> Task:
        """Start the logging task. The caller has to handle any cleanup by manually calling the `stop` method."""
        if self._logging_task:
            raise RuntimeError('Logging task already active')
        self._logging_task = asyncio.create_task(self._log_changed_status_message())
        return self._logging_task

    async def stop(self) -> None:
        """Stop the logging task."""
        if not self._logging_task:
            raise RuntimeError('Logging task is not active')

        self._logging_task.cancel()
        try:
            await self._logging_task
        except asyncio.CancelledError:
            self._logging_task = None

    async def __aenter__(self) -> Self:
        """Start the logging task within the context. Exiting the context will cancel the logging task."""
        self.start()
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        """Cancel the logging task."""
        await asyncio.sleep(self._final_sleep_time_s)
        await self.stop()

    async def _log_changed_status_message(self) -> None:
        while True:
            run_data = await self._run_client.get()
            if not self._log_run_data(run_data):
                break
            await asyncio.sleep(self._check_period)


class StatusMessageWatcherSync(StatusMessageWatcher):
    """Sync variant of `StatusMessageWatcher` that is logging in thread."""

    def __init__(
        self, *, run_client: RunClient, to_logger: logging.Logger, check_period: timedelta = timedelta(seconds=1)
    ) -> None:
        """Initialize `StatusMessageWatcherSync`.

        Args:
            run_client: The client for run that will be used to get a status and message.
            to_logger: The logger to which the status message will be redirected.
            check_period: The period with which the status message will be polled.
        """
        super().__init__(to_logger=to_logger, check_period=check_period)
        self._run_client = run_client
        self._logging_thread: Thread | None = None
        self._stop_logging = False

    def start(self) -> Thread:
        """Start the logging thread. The caller has to handle any cleanup by manually calling the `stop` method."""
        if self._logging_thread:
            raise RuntimeError('Logging thread already active')
        self._stop_logging = False
        self._logging_thread = threading.Thread(target=self._log_changed_status_message)
        self._logging_thread.start()
        return self._logging_thread

    def stop(self) -> None:
        """Signal the _logging_thread thread to stop logging and wait for it to finish."""
        if not self._logging_thread:
            raise RuntimeError('Logging thread is not active')
        time.sleep(self._final_sleep_time_s)
        self._stop_logging = True
        self._logging_thread.join()
        self._logging_thread = None
        self._stop_logging = False

    def __enter__(self) -> Self:
        """Start the logging task within the context. Exiting the context will cancel the logging task."""
        self.start()
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        """Cancel the logging task."""
        self.stop()

    def _log_changed_status_message(self) -> None:
        while True:
            if not self._log_run_data(self._run_client.get()):
                break
            if self._stop_logging:
                break
            time.sleep(self._check_period)

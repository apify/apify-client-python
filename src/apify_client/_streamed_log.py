from __future__ import annotations

import asyncio
import logging
import re
import threading
import warnings
from asyncio import Task
from datetime import UTC, datetime
from threading import Thread
from typing import TYPE_CHECKING, ClassVar, Self

from apify_client._docs import docs_group

if TYPE_CHECKING:
    from types import TracebackType

    from apify_client._resource_clients import LogClient, LogClientAsync
    from apify_client.http_clients import HttpResponse
    from apify_client.types import Timeout


_ANSI_CODE = re.compile(r'\x1b\[[0-9;]*m')
_LEVEL_PATTERN = re.compile(r'\b(CRITICAL|FATAL|ERROR|WARNING|WARN|INFO|DEBUG)\b')


def _as_utc(value: datetime | None) -> datetime | None:
    """Return `value` as an aware datetime, treating a naive one as UTC like the rest of the client does."""
    if value is None or value.tzinfo is not None:
        return value
    return value.replace(tzinfo=UTC)


def resolve_since(*, since: datetime | None, from_start: bool | None) -> datetime | None:
    """Return the time to redirect the log from, given `since` and the deprecated `from_start` argument.

    A set `from_start` emits a `DeprecationWarning`. `from_start=True` means the whole log, `from_start=False` the log
    from now on.

    Raises:
        ValueError: If both `since` and `from_start` are set.
    """
    if from_start is None:
        return since
    warnings.warn(
        'The `from_start` argument is deprecated and will be removed in v4. Use `since` instead.',
        DeprecationWarning,
        stacklevel=2,
    )
    if since is not None:
        raise ValueError('Pass only one of `since` and `from_start`.')
    return None if from_start else datetime.now(tz=UTC)


class StreamedLogBase:
    """Base class for streaming and buffering chunked Actor run logs."""

    _force_propagate = False
    """Test related flag to enable propagation of logs to the `caplog` fixture during tests."""

    _stream_timeout: ClassVar[Timeout] = 'no_timeout'
    """Timeout for the log-stream long-poll request, which stays open for the whole Actor run.

    A bounded transport timeout can truncate a longer run mid-stream. `no_timeout` keeps the connection open for the
    duration of the run (Impit currently maps it to an effective 24-hour cap) and mirrors the JS client.
    """

    _empty_stream_retry_s: ClassVar[float] = 0.5
    """Pause before the first reopen of a log stream that ended before the run logged anything.

    The API serves the log of a run that has not logged anything yet as an empty stream that ends at once. Each further
    reopen doubles the pause up to `_empty_stream_max_retry_s`, which bounds the request rate while a run waits long to
    start, for example for free memory.
    """

    _empty_stream_max_retry_s: ClassVar[float] = 5
    """Upper bound on the pause between reopens of an empty log stream."""

    _reopen_pause_s: ClassVar[float] = 1
    """Pause before reopening a log stream that broke off before its end.

    The platform cuts off a log stream that has carried no data for several minutes, even though the run goes on. The
    cut-off stream fails with a transport error, while the stream of a finished log ends without one.
    """

    def __init__(self, to_logger: logging.Logger, *, since: datetime | None = None) -> None:
        if self._force_propagate:
            to_logger.propagate = True
        self._to_logger = to_logger
        self._stream_buffer = list[bytes]()
        self._split_marker = re.compile(rb'(?:\n|^)(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)')
        self._since = _as_utc(since)
        self._received_data = False
        self._last_redirected_at: datetime | None = None
        self._replayed_until: datetime | None = None

    def _process_new_data(self, data: bytes) -> None:
        if data:
            self._received_data = True
        self._stream_buffer.append(data)
        if b'\n' in data:
            self._log_buffer_content(include_last_part=False)

    def _log_buffer_content(self, *, include_last_part: bool = False) -> None:
        """Redirect every complete line in the buffer and keep only the unterminated last line.

        A line is complete once its newline arrives. With `include_last_part`, the unterminated last line is redirected
        too.
        """
        buffer = b''.join(self._stream_buffer)
        last_newline = buffer.rfind(b'\n')
        if include_last_part:
            complete, rest = buffer, b''
        elif last_newline == -1:
            complete, rest = b'', buffer
        else:
            complete, rest = buffer[:last_newline], buffer[last_newline + 1 :]
        self._stream_buffer = [rest] if rest else []

        all_parts = re.split(self._split_marker, complete)[1:]  # Every platform log line starts with a marker
        message_markers = all_parts[0::2]
        message_contents = all_parts[1::2]
        for marker, content in zip(message_markers, message_contents, strict=True):
            decoded_marker = marker.decode('utf-8')
            decoded_content = content.decode('utf-8')
            log_time = datetime.fromisoformat(decoded_marker)
            if self._since is not None and log_time < self._since:
                continue
            if self._replayed_until is not None and log_time <= self._replayed_until:
                continue
            message = decoded_marker + decoded_content
            self._to_logger.log(level=self._guess_log_level_from_message(message), msg=message.strip())
            self._last_redirected_at = log_time

    def _prepare_reopen(self) -> None:
        """Make the reopened stream redirect only the messages after the last redirected one.

        The API cannot continue a log stream from a given point, so the reopened stream replays the log from its start.
        The unterminated last line of the stream that broke off is dropped, since the reopened stream delivers it in
        full.
        """
        self._stream_buffer = []
        self._replayed_until = self._last_redirected_at

    def _process_whole_log(self, log: bytes | None) -> None:
        """Redirect a whole log read in one request, including its last part."""
        if log:
            self._process_new_data(log)
            self._log_buffer_content(include_last_part=True)

    @staticmethod
    def _guess_log_level_from_message(message: str) -> int:
        """Return the first whole-word level name found in the message, ignoring ANSI colors. Default to INFO."""
        match = _LEVEL_PATTERN.search(_ANSI_CODE.sub('', message))
        return logging.getLevelNamesMapping()[match[1]] if match else logging.INFO


@docs_group('Other')
class StreamedLog(StreamedLogBase):
    """Streams Actor run log output to a Python logger in a background thread.

    The log stream is consumed in a background thread and each log message is forwarded to the provided logger with
    the first level name found in the message, defaulting to INFO when there is none.

    Can be used as a context manager, which automatically starts and stops the streaming thread. Alternatively,
    call `start` and `stop` manually. Obtain an instance via `RunClient.get_streamed_log`.
    """

    _stop_timeout_s: ClassVar[float] = 5
    """Upper bound on how long `stop` waits for the streaming thread to finish.

    Closing the response only ends the read on a transport that honours it, which neither Impit nor HTTPX does, so
    without a bound `stop` would wait for the next chunk, which on a quiet run may be hours away.
    """

    def __init__(
        self,
        log_client: LogClient,
        *,
        to_logger: logging.Logger,
        since: datetime | None = None,
        from_start: bool | None = None,
    ) -> None:
        """Initialize `StreamedLog`.

        Args:
            log_client: The log client used to stream raw log data from the Actor run.
            to_logger: The logger to which the log messages will be forwarded.
            since: Redirect only the log messages logged at this time or later. A naive datetime is treated as UTC.
                If `None`, the whole log is redirected.
            from_start: Deprecated, use `since` instead. `True` is the same as `since=None`, and `False` the same as
                `since=datetime.now(tz=UTC)`. Will be removed in v4.
        """
        since = resolve_since(since=since, from_start=from_start)
        super().__init__(to_logger=to_logger, since=since)
        self._log_client = log_client
        self._streaming_thread: Thread | None = None
        self._log_stream: HttpResponse | None = None
        self._stop_event = threading.Event()

    @property
    def last_redirected_at(self) -> datetime | None:
        """The timestamp of the last redirected log message, or `None` if nothing has been redirected yet.

        To continue the redirection later, for example after the Actor that redirects the log reboots, save it and
        pass it plus one millisecond as `since` to `RunClient.get_streamed_log`.
        """
        return self._last_redirected_at

    def start(self) -> Thread:
        """Start the streaming thread.

        The caller is responsible for cleanup by calling the `stop` method when done.
        """
        if self._streaming_thread and self._streaming_thread.is_alive():
            raise RuntimeError('Streaming thread already active')
        self._stop_event.clear()
        self._received_data = False
        # A daemon thread so a stream still blocked on a read can never hold up interpreter shutdown.
        self._streaming_thread = threading.Thread(target=self._stream_log, daemon=True)
        self._streaming_thread.start()
        return self._streaming_thread

    def stop(self) -> None:
        """Signal the streaming thread to stop logging and wait up to `_stop_timeout_s` for it to finish.

        A thread that outlives the wait is a daemon with `_stop_event` set, so it exits after at most one more chunk,
        and only then does its buffered tail reach the logger. Its handle is kept while it is alive, so `start` cannot
        revive it beside a second thread on the same buffer. If no stream has delivered anything yet, the thread reads
        the whole log in one request before it ends.
        """
        if not self._streaming_thread:
            raise RuntimeError('Streaming thread is not active')
        self._stop_event.set()
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
            retry_s = self._empty_stream_retry_s
            while not self._stop_event.is_set():
                if not self._stream_log_once():
                    return
                if self._received_data:
                    self._stop_event.wait(self._reopen_pause_s)
                    continue
                # An empty stream means the run has not logged anything yet, so reopen it until the first bytes arrive.
                self._stop_event.wait(retry_s)
                retry_s = min(retry_s * 2, self._empty_stream_max_retry_s)
        except Exception as exc:
            if self._stop_event.is_set():
                # `stop` closed the stream out from under the read, so the failure is expected.
                self._to_logger.debug('Log streaming stopped while `stop` was in progress: %r', exc)
            elif self._log_client._http_client.is_timeout_error(exc):  # noqa: SLF001
                # The stream cannot continue, so warn and let the thread end instead of leaking a traceback.
                self._to_logger.warning('Log streaming stopped: the log stream request timed out.')
                return

            else:
                # Any other failure in log redirection must not escape the background thread; log it instead.
                self._to_logger.exception('Log redirection stopped due to unexpected error:')
                return

        if self._received_data:
            return

        # Stopped before any stream delivered a byte, which a run that finishes quickly can cause.
        try:
            self._process_whole_log(self._log_client.get_as_bytes(raw=True))
        except Exception:
            self._to_logger.exception('Log redirection stopped due to unexpected error:')

    def _stream_log_once(self) -> bool:
        """Redirect one log stream until it ends or `stop` is called. Return whether the stream has to be opened again.

        A stream is opened again when it was empty, or when it broke off after it had delivered data. A stream that
        ends without an error after delivering data carried the whole log of a finished run.
        """
        with self._log_client.stream(raw=True, timeout=self._stream_timeout) as log_stream:
            if not log_stream:
                return False
            # Published so `stop` can close the response.
            self._log_stream = log_stream
            broke_off = False
            try:
                # `stop` may have run before the response existed for it to close. No earlier stream delivered
                # anything, and one opened this late would end after its first chunk, so read the whole log in one
                # request.
                if self._stop_event.is_set():
                    return True
                chunks = iter(log_stream.iter_bytes())
                while not self._stop_event.is_set():
                    # Only a failed read means the stream broke off. A failure to process the data would repeat on
                    # every replay, so it ends the redirection.
                    try:
                        data = next(chunks)
                    except StopIteration:
                        break
                    except Exception as exc:
                        is_timeout = self._log_client._http_client.is_timeout_error(exc)  # noqa: SLF001
                        if not self._received_data or is_timeout or self._stop_event.is_set():
                            raise
                        self._to_logger.debug('Log stream broke off, reopening it: %r', exc)
                        self._prepare_reopen()
                        broke_off = True
                        break
                    self._process_new_data(data)
            finally:
                self._log_stream = None
                try:
                    # Flush the last buffered part even if the read timed out or was stopped.
                    self._log_buffer_content(include_last_part=True)
                except Exception:
                    # A truncated stream leaves an undecodable tail, which is worth a traceback even while a stop is
                    # in progress.
                    self._to_logger.exception('Log redirection stopped due to unexpected error:')
        return broke_off or not self._received_data


@docs_group('Other')
class StreamedLogAsync(StreamedLogBase):
    """Streams Actor run log output to a Python logger in an asyncio task.

    The log stream is consumed in a background asyncio task and each log message is forwarded to the provided logger
    with the first level name found in the message, defaulting to INFO when there is none.

    Can be used as an async context manager, which automatically starts and cancels the streaming task. Alternatively,
    call `start` and `stop` manually. Obtain an instance via `RunClientAsync.get_streamed_log`.
    """

    _stop_timeout_s: ClassVar[float] = 1
    """Grace period for in-flight log data before the streaming task is cancelled."""

    def __init__(
        self,
        log_client: LogClientAsync,
        *,
        to_logger: logging.Logger,
        since: datetime | None = None,
        from_start: bool | None = None,
    ) -> None:
        """Initialize `StreamedLogAsync`.

        Args:
            log_client: The async log client used to stream raw log data from the Actor run.
            to_logger: The logger to which the log messages will be forwarded.
            since: Redirect only the log messages logged at this time or later. A naive datetime is treated as UTC.
                If `None`, the whole log is redirected.
            from_start: Deprecated, use `since` instead. `True` is the same as `since=None`, and `False` the same as
                `since=datetime.now(tz=UTC)`. Will be removed in v4.
        """
        since = resolve_since(since=since, from_start=from_start)
        super().__init__(to_logger=to_logger, since=since)
        self._log_client = log_client
        self._streaming_task: Task | None = None

    @property
    def last_redirected_at(self) -> datetime | None:
        """The timestamp of the last redirected log message, or `None` if nothing has been redirected yet.

        To continue the redirection later, for example after the Actor that redirects the log reboots, save it and
        pass it plus one millisecond as `since` to `RunClient.get_streamed_log`.
        """
        return self._last_redirected_at

    def start(self) -> Task:
        """Start the streaming task.

        The caller is responsible for cleanup by calling the `stop` method when done.
        """
        if self._streaming_task and not self._streaming_task.done():
            raise RuntimeError('Streaming task already active')
        self._received_data = False
        self._streaming_task = asyncio.create_task(self._stream_log())
        return self._streaming_task

    async def stop(self) -> None:
        """Wait up to one second for the stream to end, then cancel the streaming task.

        Caller cancellation cancels the streaming task and propagates without reading the whole log.
        If no stream has delivered anything yet, read the whole log in one request instead.
        """
        if not self._streaming_task:
            raise RuntimeError('Streaming task is not active')

        was_streaming = not self._streaming_task.done()
        try:
            await asyncio.wait_for(self._streaming_task, timeout=self._stop_timeout_s)
        except TimeoutError:
            pass
        except asyncio.CancelledError:
            # Swallow the task's own cancellation, but let a cancellation of the caller propagate.
            current = asyncio.current_task()
            if current is not None and current.cancelling():
                raise
        finally:
            self._streaming_task = None
        if not was_streaming or self._received_data:
            return
        # Stopped before any stream delivered a byte, which a run that finishes quickly can cause.
        try:
            self._process_whole_log(await self._log_client.get_as_bytes(raw=True))
        except Exception:
            self._to_logger.exception('Log redirection stopped due to unexpected error:')

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
            retry_s = self._empty_stream_retry_s
            while await self._stream_log_once():
                if self._received_data:
                    await asyncio.sleep(self._reopen_pause_s)
                    continue
                # An empty stream means the run has not logged anything yet, so reopen it until the first bytes arrive.
                await asyncio.sleep(retry_s)
                retry_s = min(retry_s * 2, self._empty_stream_max_retry_s)
        except Exception as exc:
            if self._log_client._http_client.is_timeout_error(exc):  # noqa: SLF001
                # A timeout on the long-lived stream is an expected terminal condition, not an error.
                self._to_logger.warning('Log streaming stopped: the log stream request timed out.')
            else:
                # Exception in log redirection should not propagate further.
                self._to_logger.exception('Log redirection stopped due to unexpected error:')

    async def _stream_log_once(self) -> bool:
        """Redirect one log stream until it ends. Return whether the stream has to be opened again.

        A stream is opened again when it was empty, or when it broke off after it had delivered data. A stream that
        ends without an error after delivering data carried the whole log of a finished run.
        """
        async with self._log_client.stream(raw=True, timeout=self._stream_timeout) as log_stream:
            if not log_stream:
                return False
            broke_off = False
            try:
                chunks = aiter(log_stream.aiter_bytes())
                while True:
                    # Only a failed read means the stream broke off. A failure to process the data would repeat on
                    # every replay, so it ends the redirection.
                    try:
                        data = await anext(chunks)
                    except StopAsyncIteration:
                        break
                    except Exception as exc:
                        is_timeout = self._log_client._http_client.is_timeout_error(exc)  # noqa: SLF001
                        if not self._received_data or is_timeout:
                            raise
                        self._to_logger.debug('Log stream broke off, reopening it: %r', exc)
                        self._prepare_reopen()
                        broke_off = True
                        break
                    self._process_new_data(data)
            finally:
                try:
                    # Flush the last buffered part even if the task is cancelled by `stop()`.
                    self._log_buffer_content(include_last_part=True)
                except Exception:
                    # A truncated stream leaves an undecodable tail. Keeping the failure here also keeps the
                    # cancellation `stop` raised propagating, so the task ends up cancelled as asyncio expects.
                    self._to_logger.exception('Log redirection stopped due to unexpected error:')
        return broke_off or not self._received_data

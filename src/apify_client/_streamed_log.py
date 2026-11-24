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
from apify_client._resource_clients._resource_client import _TERMINAL_STATUSES

if TYPE_CHECKING:
    from types import TracebackType

    from apify_client._resource_clients import LogClient, LogClientAsync, RunClient, RunClientAsync
    from apify_client.http_clients import HttpResponse
    from apify_client.types import Timeout


_ANSI_CODE = re.compile(r'\x1b\[[0-9;]*m')
_LEVEL_PATTERN = re.compile(r'\b(CRITICAL|FATAL|ERROR|WARNING|WARN|INFO|DEBUG)\b')


def _as_utc(value: datetime | None) -> datetime | None:
    """Return `value` as an aware datetime, treating a naive one as UTC like the rest of the client does."""
    if value is None or value.tzinfo is not None:
        return value
    return value.replace(tzinfo=UTC)


def resolve_since(*, since: datetime | None, from_start: bool | None, stacklevel: int) -> datetime | None:
    """Return the time to redirect the log from, given `since` and the deprecated `from_start` argument.

    A set `from_start` emits a `DeprecationWarning` pointing `stacklevel` frames above the caller of this function.
    `from_start=True` means the whole log, `from_start=False` the log from now on.

    Raises:
        ValueError: If both `since` and `from_start` are set.
    """
    if from_start is None:
        return since
    warnings.warn(
        'The `from_start` argument is deprecated and will be removed in v4. Use `since` instead.',
        DeprecationWarning,
        stacklevel=stacklevel + 1,
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

    _reconnect_retry_s: ClassVar[float] = 1
    """Pause before reopening a log stream that ended while the run was still going.

    The platform closes a log stream that has carried no data for several minutes, even though the run goes on. Each
    reopen that fails before delivering anything doubles the pause up to `_reconnect_max_retry_s`.
    """

    _reconnect_max_retry_s: ClassVar[float] = 30
    """Upper bound on the pause between reopens of a log stream that ended while the run was still going."""

    def __init__(self, to_logger: logging.Logger, *, since: datetime | None = None) -> None:
        if self._force_propagate:
            to_logger.propagate = True
        self._to_logger = to_logger
        self._stream_buffer = list[bytes]()
        self._split_marker = re.compile(rb'(?:\n|^)(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)')
        self._since = _as_utc(since)
        self._received_data = False
        self._stream_delivered_data = False
        # The timestamp of the last redirected message and how many redirected messages carry it. A reopened stream
        # replays the log from its start, and these tell where the redirection left off.
        self._last_redirected_at: datetime | None = None
        self._redirected_at_last_timestamp = 0
        # Where a reopened stream catches up with the redirection: messages before `_resume_after`, and the first
        # `_resume_skip_count` messages at it, were already redirected.
        self._resume_after: datetime | None = None
        self._resume_skip_count = 0

    def _process_new_data(self, data: bytes) -> None:
        if data:
            self._received_data = True
            self._stream_delivered_data = True
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
            if self._is_already_redirected(log_time):
                continue
            if self._since is not None and log_time < self._since:
                continue
            message = decoded_marker + decoded_content
            self._to_logger.log(level=self._guess_log_level_from_message(message), msg=message.strip())
            self._remember_redirected(log_time)

    def _is_already_redirected(self, log_time: datetime) -> bool:
        """Return whether a message of a reopened stream was redirected before the stream was reopened.

        The position in the log decides, not the timestamp alone: once the reopened stream gets past the last
        redirected message, every later message is new, even one with an older timestamp, which a run that migrated
        to a host with a clock running behind can log.
        """
        if self._resume_after is None:
            return False
        if log_time < self._resume_after:
            return True
        if log_time == self._resume_after and self._resume_skip_count > 0:
            self._resume_skip_count -= 1
            return True
        self._resume_after = None
        return False

    def _remember_redirected(self, log_time: datetime) -> None:
        if log_time == self._last_redirected_at:
            self._redirected_at_last_timestamp += 1
        else:
            self._last_redirected_at = log_time
            self._redirected_at_last_timestamp = 1

    def _prepare_reopen(self) -> None:
        """Set up skipping the messages a reopened stream replays, and drop the unterminated line of the ended one.

        The reopened stream delivers that line again in full, so redirecting the cut-off part would log it twice.
        """
        self._stream_buffer = []
        self._resume_after = self._last_redirected_at
        self._resume_skip_count = self._redirected_at_last_timestamp

    def _flush_tail(self) -> None:
        """Redirect the unterminated last line, logging a failure instead of raising it."""
        try:
            self._log_buffer_content(include_last_part=True)
        except Exception:
            # A truncated stream leaves an undecodable tail.
            self._to_logger.exception('Log redirection stopped due to unexpected error:')

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
        run_client: RunClient | None = None,
    ) -> None:
        """Initialize `StreamedLog`.

        Args:
            log_client: The log client used to stream raw log data from the Actor run.
            to_logger: The logger to which the log messages will be forwarded.
            since: Redirect only the log messages logged at this time or later. A naive datetime is treated as UTC.
                If `None`, the whole log is redirected.
            from_start: Deprecated, use `since` instead. `True` is the same as `since=None`, and `False` the same as
                `since=datetime.now(tz=UTC)`. Will be removed in v4.
            run_client: The client of the run whose log is streamed. With it, a log stream that ends while the run is
                still going is reopened, and the redirection resumes after the last redirected message.
        """
        # Skips `resolve_since` and this method, so the warning points at the caller.
        since = resolve_since(since=since, from_start=from_start, stacklevel=2)
        super().__init__(to_logger=to_logger, since=since)
        self._log_client = log_client
        self._run_client = run_client
        self._streaming_thread: Thread | None = None
        self._log_stream: HttpResponse | None = None
        self._stop_event = threading.Event()

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
            # An empty stream means the run has not logged anything yet, so reopen it until the first bytes arrive.
            retry_s = self._empty_stream_retry_s
            reconnect_s = self._reconnect_retry_s
            reopened_after_finish = False
            while not self._stop_event.is_set():
                self._stream_delivered_data = False
                broke_off = False
                try:
                    if not self._stream_log_once():
                        return
                except Exception as exc:
                    if not self._may_reopen():
                        raise
                    broke_off = True
                    self._to_logger.debug('Log stream broke off, reopening it: %r', exc)
                if not self._received_data:
                    self._stop_event.wait(retry_s)
                    retry_s = min(retry_s * 2, self._empty_stream_max_retry_s)
                    continue
                if not self._may_reopen():
                    # `stop` may have landed after the ended stream kept its unterminated last line.
                    self._flush_tail()
                    return
                try:
                    run_finished = self._is_run_finished()
                except Exception:
                    self._flush_tail()
                    raise
                # A stream that broke off can miss the last messages of a run that finished meanwhile, so it is
                # reopened once more to catch up. A stream that ended on its own carried the whole log.
                if run_finished and (not broke_off or reopened_after_finish):
                    self._flush_tail()
                    return
                reopened_after_finish = run_finished
                self._prepare_reopen()
                if self._stream_delivered_data:
                    reconnect_s = self._reconnect_retry_s
                self._stop_event.wait(reconnect_s)
                reconnect_s = min(reconnect_s * 2, self._reconnect_max_retry_s)
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
        """Redirect one log stream until it ends or `stop` is called. Return `False` when the log does not exist."""
        with self._log_client.stream(raw=True, timeout=self._stream_timeout) as log_stream:
            if not log_stream:
                return False
            # Published so `stop` can close the response.
            self._log_stream = log_stream
            try:
                # `stop` may have run before the response existed for it to close. A stream opened this late would
                # end after its first chunk, so leave the log to the one-shot read of a session that has not received
                # anything yet, or to the streams before this one.
                if self._stop_event.is_set():
                    return True
                for data in log_stream.iter_bytes():
                    self._process_new_data(data)
                    if self._stop_event.is_set():
                        break
            finally:
                self._log_stream = None
                try:
                    # Flush the last buffered part even if the read timed out or was stopped. A stream that may be
                    # reopened keeps it until that is decided, since the reopened stream delivers it in full.
                    self._log_buffer_content(include_last_part=not self._may_reopen())
                except Exception:
                    # A truncated stream leaves an undecodable tail, which is worth a traceback even while a stop is
                    # in progress.
                    self._to_logger.exception('Log redirection stopped due to unexpected error:')
        return True

    def _may_reopen(self) -> bool:
        """Return whether an ended stream may be reopened to resume the redirection."""
        return self._run_client is not None and self._received_data and not self._stop_event.is_set()

    def _is_run_finished(self) -> bool:
        if self._run_client is None:
            return True
        run = self._run_client.get()
        return run is None or run.status in _TERMINAL_STATUSES


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
        run_client: RunClientAsync | None = None,
    ) -> None:
        """Initialize `StreamedLogAsync`.

        Args:
            log_client: The async log client used to stream raw log data from the Actor run.
            to_logger: The logger to which the log messages will be forwarded.
            since: Redirect only the log messages logged at this time or later. A naive datetime is treated as UTC.
                If `None`, the whole log is redirected.
            from_start: Deprecated, use `since` instead. `True` is the same as `since=None`, and `False` the same as
                `since=datetime.now(tz=UTC)`. Will be removed in v4.
            run_client: The client of the run whose log is streamed. With it, a log stream that ends while the run is
                still going is reopened, and the redirection resumes after the last redirected message.
        """
        # Skips `resolve_since` and this method, so the warning points at the caller.
        since = resolve_since(since=since, from_start=from_start, stacklevel=2)
        super().__init__(to_logger=to_logger, since=since)
        self._log_client = log_client
        self._run_client = run_client
        self._streaming_task: Task | None = None

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
            # An empty stream means the run has not logged anything yet, so reopen it until the first bytes arrive.
            retry_s = self._empty_stream_retry_s
            reconnect_s = self._reconnect_retry_s
            reopened_after_finish = False
            while True:
                self._stream_delivered_data = False
                broke_off = False
                try:
                    if not await self._stream_log_once():
                        return
                except Exception as exc:
                    if not self._may_reopen():
                        raise
                    broke_off = True
                    self._to_logger.debug('Log stream broke off, reopening it: %r', exc)
                if not self._received_data:
                    await asyncio.sleep(retry_s)
                    retry_s = min(retry_s * 2, self._empty_stream_max_retry_s)
                    continue
                if not self._may_reopen():
                    return
                try:
                    run_finished = await self._is_run_finished()
                except Exception:
                    self._flush_tail()
                    raise
                # A stream that broke off can miss the last messages of a run that finished meanwhile, so it is
                # reopened once more to catch up. A stream that ended on its own carried the whole log.
                if run_finished and (not broke_off or reopened_after_finish):
                    self._flush_tail()
                    return
                reopened_after_finish = run_finished
                self._prepare_reopen()
                if self._stream_delivered_data:
                    reconnect_s = self._reconnect_retry_s
                await asyncio.sleep(reconnect_s)
                reconnect_s = min(reconnect_s * 2, self._reconnect_max_retry_s)
        except asyncio.CancelledError:
            # `stop` cancelled the task, possibly while an ended stream kept its unterminated last line.
            self._flush_tail()
            raise
        except Exception as exc:
            if self._log_client._http_client.is_timeout_error(exc):  # noqa: SLF001
                # A timeout on the long-lived stream is an expected terminal condition, not an error.
                self._to_logger.warning('Log streaming stopped: the log stream request timed out.')
            else:
                # Exception in log redirection should not propagate further.
                self._to_logger.exception('Log redirection stopped due to unexpected error:')

    async def _stream_log_once(self) -> bool:
        """Redirect one log stream until it ends. Return `False` when the log does not exist."""
        async with self._log_client.stream(raw=True, timeout=self._stream_timeout) as log_stream:
            if not log_stream:
                return False
            try:
                async for data in log_stream.aiter_bytes():
                    self._process_new_data(data)
            finally:
                try:
                    # Flush the last buffered part even if the task is cancelled by `stop()`. A stream that may be
                    # reopened keeps it until that is decided, since the reopened stream delivers it in full.
                    self._log_buffer_content(include_last_part=not self._may_reopen())
                except Exception:
                    # A truncated stream leaves an undecodable tail. Keeping the failure here also keeps the
                    # cancellation `stop` raised propagating, so the task ends up cancelled as asyncio expects.
                    self._to_logger.exception('Log redirection stopped due to unexpected error:')
        return True

    def _may_reopen(self) -> bool:
        """Return whether an ended stream may be reopened to resume the redirection."""
        return self._run_client is not None and self._received_data

    async def _is_run_finished(self) -> bool:
        if self._run_client is None:
            return True
        run = await self._run_client.get()
        return run is None or run.status in _TERMINAL_STATUSES

from __future__ import annotations

import asyncio
import threading
import time
from asyncio import Task
from datetime import timedelta
from threading import Thread
from typing import TYPE_CHECKING, Self

from apify_client._docs import docs_group
from apify_client._utils import to_seconds

if TYPE_CHECKING:
    import logging
    from types import TracebackType

    from apify_client._models import Run
    from apify_client._resource_clients import RunClient, RunClientAsync


class StatusMessageWatcherBase:
    """Base class for polling and logging Actor run status messages."""

    _force_propagate = False
    # This is final sleep time to try to get the last status and status message of finished Actor run.
    # The status and status message can get set on the Actor run with a delay. Sleep time does not guarantee that the
    # final message will be captured, but increases the chances of that.
    _final_sleep_time_s = 6

    def __init__(self, *, to_logger: logging.Logger, check_period: timedelta = timedelta(seconds=5)) -> None:
        if self._force_propagate:
            to_logger.propagate = True
        self._to_logger = to_logger
        self._check_period = to_seconds(check_period)
        self._last_status_message = ''

    def _log_run_data(self, run_data: Run | None) -> bool:
        """Get relevant run data, log them if changed and return `True` if more data is expected.

        Args:
            run_data: The Run model that contains the run data.

        Returns:
              `True` if more data is expected, `False` otherwise.
        """
        if run_data is not None:
            status = run_data.status.value if run_data.status else 'Unknown status'
            status_message = run_data.status_message or ''
            new_status_message = f'Status: {status}, Message: {status_message}'

            if new_status_message != self._last_status_message:
                self._last_status_message = new_status_message
                self._to_logger.info(new_status_message)

            return not (run_data.is_status_message_terminal or False)
        return True


@docs_group('Other')
class StatusMessageWatcherAsync(StatusMessageWatcherBase):
    """Polls and logs Actor run status messages in an asyncio task.

    The status message and status of the Actor run are polled at a fixed interval and forwarded to the provided logger
    whenever they change. There is no guarantee that every intermediate status message will be captured, especially
    when messages change rapidly.

    Can be used as an async context manager, which automatically starts and cancels the polling task. Alternatively,
    call `start` and `stop` manually. Obtain an instance via `RunClientAsync.get_status_message_watcher`.
    """

    def __init__(
        self, *, run_client: RunClientAsync, to_logger: logging.Logger, check_period: timedelta = timedelta(seconds=1)
    ) -> None:
        """Initialize `StatusMessageWatcherAsync`.

        Args:
            run_client: The run client used to poll the Actor run status and status message.
            to_logger: The logger to which the status messages will be forwarded.
            check_period: How often to poll the status message.
        """
        super().__init__(to_logger=to_logger, check_period=check_period)
        self._run_client = run_client
        self._logging_task: Task | None = None

    def start(self) -> Task:
        """Start the polling task.

        The caller is responsible for cleanup by calling the `stop` method when done.
        """
        if self._logging_task and not self._logging_task.done():
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
            pass
        finally:
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


@docs_group('Other')
class StatusMessageWatcher(StatusMessageWatcherBase):
    """Polls and logs Actor run status messages in a background thread.

    The status message and status of the Actor run are polled at a fixed interval and forwarded to the provided logger
    whenever they change. There is no guarantee that every intermediate status message will be captured, especially
    when messages change rapidly.

    Can be used as a context manager, which automatically starts and stops the polling thread. Alternatively,
    call `start` and `stop` manually. Obtain an instance via `RunClient.get_status_message_watcher`.
    """

    def __init__(
        self, *, run_client: RunClient, to_logger: logging.Logger, check_period: timedelta = timedelta(seconds=1)
    ) -> None:
        """Initialize `StatusMessageWatcher`.

        Args:
            run_client: The run client used to poll the Actor run status and status message.
            to_logger: The logger to which the status messages will be forwarded.
            check_period: How often to poll the status message.
        """
        super().__init__(to_logger=to_logger, check_period=check_period)
        self._run_client = run_client
        self._logging_thread: Thread | None = None
        self._stop_logging = False

    def start(self) -> Thread:
        """Start the polling thread.

        The caller is responsible for cleanup by calling the `stop` method when done.
        """
        if self._logging_thread:
            raise RuntimeError('Logging thread already active')
        self._stop_logging = False
        self._logging_thread = threading.Thread(target=self._log_changed_status_message)
        self._logging_thread.start()
        return self._logging_thread

    def stop(self) -> None:
        """Signal the logging thread to stop logging and wait for it to finish."""
        if not self._logging_thread:
            raise RuntimeError('Logging thread is not active')
        time.sleep(self._final_sleep_time_s)
        self._stop_logging = True
        self._logging_thread.join()
        self._logging_thread = None
        self._stop_logging = False

    def __enter__(self) -> Self:
        """Start the logging thread within the context. Exiting the context will stop the logging thread."""
        self.start()
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        """Stop the logging thread."""
        self.stop()

    def _log_changed_status_message(self) -> None:
        while True:
            if not self._log_run_data(self._run_client.get()):
                break
            if self._stop_logging:
                break
            time.sleep(self._check_period)

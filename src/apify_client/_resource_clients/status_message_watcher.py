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


@docs_group('Resource clients')
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


@docs_group('Resource clients')
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


@docs_group('Resource clients')
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

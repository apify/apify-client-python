from __future__ import annotations

import asyncio
import logging
from asyncio import Task
from contextlib import asynccontextmanager, contextmanager
from typing import TYPE_CHECKING, Any

from apify_shared.utils import ignore_docs

from apify_client._errors import ApifyApiError
from apify_client._utils import catch_not_found_or_throw
from apify_client.clients.base import ResourceClient, ResourceClientAsync

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator
    from types import TracebackType

    import httpx
    from mypy.types import Self


class LogClient(ResourceClient):
    """Sub-client for manipulating logs."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'logs')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> str | None:
        """Retrieve the log as text.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Returns:
            The retrieved log, or None, if it does not exist.
        """
        try:
            response = self.http_client.call(
                url=self.url,
                method='GET',
                params=self._params(),
            )

            return response.text  # noqa: TRY300

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    def get_as_bytes(self) -> bytes | None:
        """Retrieve the log as raw bytes.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Returns:
            The retrieved log as raw bytes, or None, if it does not exist.
        """
        try:
            response = self.http_client.call(
                url=self.url,
                method='GET',
                params=self._params(),
                parse_response=False,
            )

            return response.content  # noqa: TRY300

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    @contextmanager
    def stream(self) -> Iterator[httpx.Response | None]:
        """Retrieve the log as a stream.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Returns:
            The retrieved log as a context-managed streaming `Response`, or None, if it does not exist.
        """
        response = None
        try:
            response = self.http_client.call(
                url=self.url,
                method='GET',
                params=self._params(stream=True),
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

    async def get(self) -> str | None:
        """Retrieve the log as text.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Returns:
            The retrieved log, or None, if it does not exist.
        """
        try:
            response = await self.http_client.call(
                url=self.url,
                method='GET',
                params=self._params(),
            )

            return response.text  # noqa: TRY300

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    async def get_as_bytes(self) -> bytes | None:
        """Retrieve the log as raw bytes.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Returns:
            The retrieved log as raw bytes, or None, if it does not exist.
        """
        try:
            response = await self.http_client.call(
                url=self.url,
                method='GET',
                params=self._params(),
                parse_response=False,
            )

            return response.content  # noqa: TRY300

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    @asynccontextmanager
    async def stream(self) -> AsyncIterator[httpx.Response | None]:
        """Retrieve the log as a stream.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Returns:
            The retrieved log as a context-managed streaming `Response`, or None, if it does not exist.
        """
        response = None
        try:
            response = await self.http_client.call(
                url=self.url,
                method='GET',
                params=self._params(stream=True),
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


class StreamedLogSync:
    """Utility class for streaming logs from another actor."""


class StreamedLogAsync:
    """Utility class for streaming logs from another actor."""

    def __init__(self, log_client: LogClientAsync, to_logger: logging.Logger) -> None:
        self._log_client = log_client
        self._to_logger = to_logger
        self._streaming_task: Task | None = None

    def __call__(self) -> Task:
        """Start the streaming task. The called has to handle any cleanup."""
        return asyncio.create_task(self._stream_log(self._to_logger))

    async def __aenter__(self) -> Self:
        """Start the streaming task within the context. Exiting the context will cancel the streaming task."""
        if self._streaming_task:
            raise RuntimeError('Streaming task already active')
        self._streaming_task = self()

        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        """Cancel the streaming task."""
        if not self._streaming_task:
            raise RuntimeError('Streaming task is not active')

        self._streaming_task.cancel()

        self._streaming_task = None

    async def _stream_log(self, to_logger: logging.Logger) -> None:
        async with self._log_client.stream() as log_stream:
            if not log_stream:
                return
            async for data in log_stream.aiter_bytes():
                log_level = logging.INFO  # The Original log level is not known unless the message is inspected.
                # Adjust the log level in custom logger filter if needed.

                # Split by lines for each line that does start with standard format, try to guess the log level
                # example split marker: \n2025-05-12T15:35:59.429Z

                to_logger.log(level=log_level, msg=data.decode('utf-8'))
                #logging.getLogger("apify_client").info(data)
        # Cleanup in the end
        #log_stream.close()

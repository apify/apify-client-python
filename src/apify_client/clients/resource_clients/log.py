from __future__ import annotations

import asyncio
import logging
import re
from asyncio import Task
from contextlib import asynccontextmanager, contextmanager
from typing import TYPE_CHECKING, Any, cast

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


class StreamedLogSync:
    """Utility class for streaming logs from another actor."""


class StreamedLogAsync:
    """Utility class for streaming logs from another actor."""

    # Test related flag to enable propagation of logs to the `caplog` fixture during tests.
    _force_propagate = False

    def __init__(self, log_client: LogClientAsync, to_logger: logging.Logger) -> None:
        self._log_client = log_client
        self._to_logger = to_logger
        self._streaming_task: Task | None = None
        if self._force_propagate:
            to_logger.propagate = True
        self._stream_buffer = list[str]()
        # Redirected logs are forwarded to logger as soon as there are at least two split markers present in the buffer.
        # For example, 2025-05-12T15:35:59.429Z
        self._split_marker = re.compile(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)')

    def __call__(self) -> Task:
        """Start the streaming task. The caller has to handle any cleanup."""
        return asyncio.create_task(self._stream_log())

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

    async def _stream_log(self) -> None:
        async with self._log_client.stream(raw=True) as log_stream:
            if not log_stream:
                return
            async for data in log_stream.aiter_bytes():
                new_chunk = data.decode('utf-8')
                self._stream_buffer.append(new_chunk)
                if re.findall(self._split_marker, new_chunk):
                    # If complete split marker was found in new chunk, then process the buffer.
                    self._log_buffer_content(include_last_part=False)

            # If the stream is finished, then the last part will be also processed.
            self._log_buffer_content(include_last_part=True)

    def _log_buffer_content(self, *, include_last_part: bool = False) -> None:
        """Merge the whole buffer and plit it into parts based on the marker.

        The last part could be incomplete, and so it can be left unprocessed and in the buffer.
        """
        all_parts = re.split(self._split_marker, ''.join(self._stream_buffer))
        # First split is empty string
        if include_last_part:
            message_markers = all_parts[1::2]
            message_contents = all_parts[2::2]
            self._stream_buffer = []
        else:
            message_markers = all_parts[1:-2:2]
            message_contents = all_parts[2:-2:2]
            # The last two parts (marker and message) are possibly not complete and will be left in the buffer
            self._stream_buffer = all_parts[-2:]

        for marker, content in zip(message_markers, message_contents):
            message = marker + content
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

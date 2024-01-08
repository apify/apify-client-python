from __future__ import annotations

from contextlib import asynccontextmanager, contextmanager
from typing import TYPE_CHECKING, Any, AsyncIterator, Iterator

from apify_shared.utils import ignore_docs

from apify_client._errors import ApifyApiError
from apify_client._utils import catch_not_found_or_throw
from apify_client.clients.base import ResourceClient, ResourceClientAsync

if TYPE_CHECKING:
    import httpx


class LogClient(ResourceClient):
    """Sub-client for manipulating logs."""

    @ignore_docs
    def __init__(self: LogClient, *args: Any, **kwargs: Any) -> None:
        """Initialize the LogClient."""
        resource_path = kwargs.pop('resource_path', 'logs')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self: LogClient) -> str | None:
        """Retrieve the log as text.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Returns:
            str, optional: The retrieved log, or None, if it does not exist.
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

    def get_as_bytes(self: LogClient) -> bytes | None:
        """Retrieve the log as raw bytes.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Returns:
            bytes, optional: The retrieved log as raw bytes, or None, if it does not exist.
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
    def stream(self: LogClient) -> Iterator[httpx.Response | None]:
        """Retrieve the log as a stream.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Returns:
            httpx.Response, optional: The retrieved log as a context-managed streaming Response, or None, if it does not exist.
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
    def __init__(self: LogClientAsync, *args: Any, **kwargs: Any) -> None:
        """Initialize the LogClientAsync."""
        resource_path = kwargs.pop('resource_path', 'logs')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self: LogClientAsync) -> str | None:
        """Retrieve the log as text.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Returns:
            str, optional: The retrieved log, or None, if it does not exist.
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

    async def get_as_bytes(self: LogClientAsync) -> bytes | None:
        """Retrieve the log as raw bytes.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Returns:
            bytes, optional: The retrieved log as raw bytes, or None, if it does not exist.
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
    async def stream(self: LogClientAsync) -> AsyncIterator[httpx.Response | None]:
        """Retrieve the log as a stream.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Returns:
            httpx.Response, optional: The retrieved log as a context-managed streaming Response, or None, if it does not exist.
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

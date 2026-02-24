from __future__ import annotations

from contextlib import asynccontextmanager, contextmanager
from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import catch_not_found_or_throw
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    import impit


@docs_group('Resource clients')
class LogClient(ResourceClient):
    """Sub-client for managing a specific log.

    Provides methods to get and stream logs. Obtain an instance via `ApifyClient.log`.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'logs')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self, *, raw: bool = False) -> str | None:
        """Retrieve the log as text.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Args:
            raw: If true, the log will include formatting. For example, coloring character sequences.

        Returns:
            The retrieved log, or None, if it does not exist.
        """
        try:
            response = self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(raw=raw),
            )

            return response.text  # noqa: TRY300

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    def get_as_bytes(self, *, raw: bool = False) -> bytes | None:
        """Retrieve the log as raw bytes.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Args:
            raw: If true, the log will include formatting. For example, coloring character sequences.

        Returns:
            The retrieved log as raw bytes, or None, if it does not exist.
        """
        try:
            response = self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(raw=raw),
            )

            return response.content  # noqa: TRY300

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    @contextmanager
    def stream(self, *, raw: bool = False) -> Iterator[impit.Response | None]:
        """Retrieve the log as a stream.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Args:
            raw: If true, the log will include formatting. For example, coloring character sequences.

        Returns:
            The retrieved log as a context-managed streaming `Response`, or None, if it does not exist.
        """
        response = None
        try:
            response = self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(stream=True, raw=raw),
                stream=True,
            )

            yield response
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            yield None
        finally:
            if response:
                response.close()


@docs_group('Resource clients')
class LogClientAsync(ResourceClientAsync):
    """Sub-client for managing a specific log.

    Provides methods to get and stream logs. Obtain an instance via `ApifyClientAsync.log`.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'logs')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self, *, raw: bool = False) -> str | None:
        """Retrieve the log as text.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Args:
            raw: If true, the log will include formatting. For example, coloring character sequences.

        Returns:
            The retrieved log, or None, if it does not exist.
        """
        try:
            response = await self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(raw=raw),
            )

            return response.text  # noqa: TRY300

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    async def get_as_bytes(self, *, raw: bool = False) -> bytes | None:
        """Retrieve the log as raw bytes.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Args:
            raw: If true, the log will include formatting. For example, coloring character sequences.

        Returns:
            The retrieved log as raw bytes, or None, if it does not exist.
        """
        try:
            response = await self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(raw=raw),
            )

            return response.content  # noqa: TRY300

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    @asynccontextmanager
    async def stream(self, *, raw: bool = False) -> AsyncIterator[impit.Response | None]:
        """Retrieve the log as a stream.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Args:
            raw: If true, the log will include formatting. For example, coloring character sequences.

        Returns:
            The retrieved log as a context-managed streaming `Response`, or None, if it does not exist.
        """
        response = None
        try:
            response = await self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(stream=True, raw=raw),
                stream=True,
            )

            yield response
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            yield None
        finally:
            if response:
                await response.aclose()

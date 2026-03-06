from __future__ import annotations

from contextlib import asynccontextmanager, contextmanager
from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import catch_not_found_or_throw
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from apify_client._http_clients import HttpResponse
    from apify_client._types import Timeout


@docs_group('Resource clients')
class LogClient(ResourceClient):
    """Sub-client for managing a specific log.

    Provides methods to manage logs, e.g. get or stream them. Obtain an instance via an appropriate method on the
    `ApifyClient` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'logs',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_path=resource_path,
            **kwargs,
        )

    def get(self, *, raw: bool = False, timeout: Timeout = 'long') -> str | None:
        """Retrieve the log as text.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Args:
            raw: If true, the log will include formatting. For example, coloring character sequences.
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved log, or None, if it does not exist.
        """
        try:
            response = self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(raw=raw),
                timeout=timeout,
            )

            return response.text  # noqa: TRY300

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    def get_as_bytes(self, *, raw: bool = False, timeout: Timeout = 'long') -> bytes | None:
        """Retrieve the log as raw bytes.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Args:
            raw: If true, the log will include formatting. For example, coloring character sequences.
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved log as raw bytes, or None, if it does not exist.
        """
        try:
            response = self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(raw=raw),
                timeout=timeout,
            )

            return response.content  # noqa: TRY300

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    @contextmanager
    def stream(self, *, raw: bool = False, timeout: Timeout = 'long') -> Iterator[HttpResponse | None]:
        """Retrieve the log as a stream.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Args:
            raw: If true, the log will include formatting. For example, coloring character sequences.
            timeout: Timeout for the API HTTP request.

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
                timeout=timeout,
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

    Provides methods to manage logs, e.g. get or stream them. Obtain an instance via an appropriate method on the
    `ApifyClientAsync` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'logs',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_path=resource_path,
            **kwargs,
        )

    async def get(self, *, raw: bool = False, timeout: Timeout = 'long') -> str | None:
        """Retrieve the log as text.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Args:
            raw: If true, the log will include formatting. For example, coloring character sequences.
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved log, or None, if it does not exist.
        """
        try:
            response = await self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(raw=raw),
                timeout=timeout,
            )

            return response.text  # noqa: TRY300

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    async def get_as_bytes(self, *, raw: bool = False, timeout: Timeout = 'long') -> bytes | None:
        """Retrieve the log as raw bytes.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Args:
            raw: If true, the log will include formatting. For example, coloring character sequences.
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved log as raw bytes, or None, if it does not exist.
        """
        try:
            response = await self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(raw=raw),
                timeout=timeout,
            )

            return response.content  # noqa: TRY300

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    @asynccontextmanager
    async def stream(self, *, raw: bool = False, timeout: Timeout = 'long') -> AsyncIterator[HttpResponse | None]:
        """Retrieve the log as a stream.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Args:
            raw: If true, the log will include formatting. For example, coloring character sequences.
            timeout: Timeout for the API HTTP request.

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
                timeout=timeout,
            )

            yield response
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            yield None
        finally:
            if response:
                await response.aclose()

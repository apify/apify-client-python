from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._models import Build, BuildResponse
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import response_to_dict

if TYPE_CHECKING:
    from datetime import timedelta

    from apify_client._resource_clients import LogClient, LogClientAsync
    from apify_client._types import Timeout


@docs_group('Resource clients')
class BuildClient(ResourceClient):
    """Sub-client for managing a specific Actor build.

    Provides methods to manage a specific Actor build, e.g. get it, abort it, or wait for it to finish. Obtain an
    instance via an appropriate method on the `ApifyClient` class.
    """

    def __init__(
        self,
        *,
        resource_id: str,
        resource_path: str = 'actor-builds',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_id=resource_id,
            resource_path=resource_path,
            **kwargs,
        )

    def get(self, *, timeout: Timeout = 'short') -> Build | None:
        """Return information about the Actor build.

        https://docs.apify.com/api/v2#/reference/actor-builds/build-object/get-build

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved Actor build data.
        """
        result = self._get(timeout=timeout)
        if result is None:
            return None
        return BuildResponse.model_validate(result).data

    def delete(self, *, timeout: Timeout = 'short') -> None:
        """Delete the build.

        https://docs.apify.com/api/v2#/reference/actor-builds/delete-build/delete-build

        Args:
            timeout: Timeout for the API HTTP request.
        """
        self._delete(timeout=timeout)

    def abort(self, *, timeout: Timeout = 'short') -> Build:
        """Abort the Actor build which is starting or currently running and return its details.

        https://docs.apify.com/api/v2#/reference/actor-builds/abort-build/abort-build

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The data of the aborted Actor build.
        """
        response = self._http_client.call(
            url=self._build_url('abort'),
            method='POST',
            params=self._build_params(),
            timeout=timeout,
        )
        result = response_to_dict(response)
        return BuildResponse.model_validate(result).data

    def get_open_api_definition(self, *, timeout: Timeout = 'medium') -> dict:
        """Return OpenAPI definition of the Actor's build.

        https://docs.apify.com/api/v2/actor-build-openapi-json-get

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            OpenAPI definition of the Actor's build.
        """
        response = self._http_client.call(
            url=self._build_url('openapi.json'),
            method='GET',
            timeout=timeout,
        )
        return response_to_dict(response)

    def wait_for_finish(
        self, *, wait_duration: timedelta | None = None, timeout: Timeout = 'no_timeout'
    ) -> Build | None:
        """Wait synchronously until the build finishes or the server times out.

        Args:
            wait_duration: How long does the client wait for build to finish. None for indefinite.
            timeout: Timeout for the API HTTP request.

        Returns:
            The Actor build data. If the status on the object is not one of the terminal statuses (SUCCEEDED, FAILED,
                TIMED_OUT, ABORTED), then the build has not yet finished.
        """
        result = self._wait_for_finish(
            url=self._build_url(),
            params=self._build_params(),
            wait_duration=wait_duration,
            timeout=timeout,
        )
        return Build.model_validate(result) if result is not None else None

    def log(self) -> LogClient:
        """Get the client for the log of the Actor build.

        https://docs.apify.com/api/v2/#/reference/actor-builds/build-log/get-log

        Returns:
            A client allowing access to the log of this Actor build.
        """
        return self._client_registry.log_client(
            resource_path='log',
            **self._base_client_kwargs,
        )


@docs_group('Resource clients')
class BuildClientAsync(ResourceClientAsync):
    """Sub-client for managing a specific Actor build.

    Provides methods to manage a specific Actor build, e.g. get it, abort it, or wait for it to finish. Obtain an
    instance via an appropriate method on the `ApifyClientAsync` class.
    """

    def __init__(
        self,
        *,
        resource_id: str,
        resource_path: str = 'actor-builds',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_id=resource_id,
            resource_path=resource_path,
            **kwargs,
        )

    async def get(self, *, timeout: Timeout = 'short') -> Build | None:
        """Return information about the Actor build.

        https://docs.apify.com/api/v2#/reference/actor-builds/build-object/get-build

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved Actor build data.
        """
        result = await self._get(timeout=timeout)
        if result is None:
            return None
        return BuildResponse.model_validate(result).data

    async def abort(self, *, timeout: Timeout = 'short') -> Build:
        """Abort the Actor build which is starting or currently running and return its details.

        https://docs.apify.com/api/v2#/reference/actor-builds/abort-build/abort-build

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The data of the aborted Actor build.
        """
        response = await self._http_client.call(
            url=self._build_url('abort'),
            method='POST',
            params=self._build_params(),
            timeout=timeout,
        )
        result = response_to_dict(response)
        return BuildResponse.model_validate(result).data

    async def delete(self, *, timeout: Timeout = 'short') -> None:
        """Delete the build.

        https://docs.apify.com/api/v2#/reference/actor-builds/delete-build/delete-build

        Args:
            timeout: Timeout for the API HTTP request.
        """
        await self._delete(timeout=timeout)

    async def get_open_api_definition(self, *, timeout: Timeout = 'medium') -> dict:
        """Return OpenAPI definition of the Actor's build.

        https://docs.apify.com/api/v2/actor-build-openapi-json-get

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            OpenAPI definition of the Actor's build.
        """
        response = await self._http_client.call(
            url=self._build_url('openapi.json'),
            method='GET',
            timeout=timeout,
        )
        return response_to_dict(response)

    async def wait_for_finish(
        self, *, wait_duration: timedelta | None = None, timeout: Timeout = 'no_timeout'
    ) -> Build | None:
        """Wait asynchronously until the build finishes or the server times out.

        Args:
            wait_duration: How long does the client wait for build to finish. None for indefinite.
            timeout: Timeout for the API HTTP request.

        Returns:
            The Actor build data. If the status on the object is not one of the terminal statuses (SUCCEEDED, FAILED,
                TIMED_OUT, ABORTED), then the build has not yet finished.
        """
        result = await self._wait_for_finish(
            url=self._build_url(),
            params=self._build_params(),
            wait_duration=wait_duration,
            timeout=timeout,
        )
        return Build.model_validate(result) if result is not None else None

    def log(self) -> LogClientAsync:
        """Get the client for the log of the Actor build.

        https://docs.apify.com/api/v2/#/reference/actor-builds/build-log/get-log

        Returns:
            A client allowing access to the log of this Actor build.
        """
        return self._client_registry.log_client(
            resource_path='log',
            **self._base_client_kwargs,
        )

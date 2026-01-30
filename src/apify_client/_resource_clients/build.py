from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._models import Build, BuildResponse
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import catch_not_found_or_throw, response_to_dict
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from datetime import timedelta

    from apify_client._resource_clients import LogClient, LogClientAsync


class BuildClient(ResourceClient):
    """Sub-client for manipulating a single Actor build."""

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

    def get(self) -> Build | None:
        """Return information about the Actor build.

        https://docs.apify.com/api/v2#/reference/actor-builds/build-object/get-build

        Returns:
            The retrieved Actor build data.
        """
        try:
            response = self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(),
            )
            result = response_to_dict(response)
            return BuildResponse.model_validate(result).data
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            return None

    def delete(self) -> None:
        """Delete the build.

        https://docs.apify.com/api/v2#/reference/actor-builds/delete-build/delete-build
        """
        try:
            self._http_client.call(
                url=self._build_url(),
                method='DELETE',
                params=self._build_params(),
            )
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

    def abort(self) -> Build:
        """Abort the Actor build which is starting or currently running and return its details.

        https://docs.apify.com/api/v2#/reference/actor-builds/abort-build/abort-build

        Returns:
            The data of the aborted Actor build.
        """
        response = self._http_client.call(
            url=self._build_url('abort'),
            method='POST',
            params=self._build_params(),
        )
        result = response_to_dict(response)
        return BuildResponse.model_validate(result).data

    def get_open_api_definition(self) -> dict | None:
        """Return OpenAPI definition of the Actor's build.

        https://docs.apify.com/api/v2/actor-build-openapi-json-get

        Returns:
            OpenAPI definition of the Actor's build.
        """
        response = self._http_client.call(
            url=self._build_url('openapi.json'),
            method='GET',
        )

        response_as_dict: dict = response.json()

        return response_as_dict

    def wait_for_finish(self, *, wait_duration: timedelta | None = None) -> Build | None:
        """Wait synchronously until the build finishes or the server times out.

        Args:
            wait_duration: How long does the client wait for build to finish. None for indefinite.

        Returns:
            The Actor build data. If the status on the object is not one of the terminal statuses (SUCCEEDED, FAILED,
                TIMED_OUT, ABORTED), then the build has not yet finished.
        """
        result = self._wait_for_finish(
            url=self._build_url(),
            params=self._build_params(),
            wait_duration=wait_duration,
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


class BuildClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single Actor build."""

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

    async def get(self) -> Build | None:
        """Return information about the Actor build.

        https://docs.apify.com/api/v2#/reference/actor-builds/build-object/get-build

        Returns:
            The retrieved Actor build data.
        """
        try:
            response = await self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(),
            )
            result = response_to_dict(response)
            return BuildResponse.model_validate(result).data
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            return None

    async def abort(self) -> Build:
        """Abort the Actor build which is starting or currently running and return its details.

        https://docs.apify.com/api/v2#/reference/actor-builds/abort-build/abort-build

        Returns:
            The data of the aborted Actor build.
        """
        response = await self._http_client.call(
            url=self._build_url('abort'),
            method='POST',
            params=self._build_params(),
        )
        result = response_to_dict(response)
        return BuildResponse.model_validate(result).data

    async def delete(self) -> None:
        """Delete the build.

        https://docs.apify.com/api/v2#/reference/actor-builds/delete-build/delete-build
        """
        try:
            await self._http_client.call(
                url=self._build_url(),
                method='DELETE',
                params=self._build_params(),
            )
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

    async def get_open_api_definition(self) -> dict | None:
        """Return OpenAPI definition of the Actor's build.

        https://docs.apify.com/api/v2/actor-build-openapi-json-get

        Returns:
            OpenAPI definition of the Actor's build.
        """
        response = await self._http_client.call(
            url=self._build_url('openapi.json'),
            method='GET',
        )

        response_as_dict: dict = response.json()

        return response_as_dict

    async def wait_for_finish(self, *, wait_duration: timedelta | None = None) -> Build | None:
        """Wait asynchronously until the build finishes or the server times out.

        Args:
            wait_duration: How long does the client wait for build to finish. None for indefinite.

        Returns:
            The Actor build data. If the status on the object is not one of the terminal statuses (SUCCEEDED, FAILED,
                TIMED_OUT, ABORTED), then the build has not yet finished.
        """
        result = await self._wait_for_finish(
            url=self._build_url(),
            params=self._build_params(),
            wait_duration=wait_duration,
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

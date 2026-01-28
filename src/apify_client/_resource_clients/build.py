from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._models import Build, GetBuildResponse, PostAbortBuildResponse
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import catch_not_found_or_throw, response_to_dict, wait_for_finish_async, wait_for_finish_sync
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from apify_client._resource_clients.log import LogClient, LogClientAsync


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
            return GetBuildResponse.model_validate(result).data
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
        return PostAbortBuildResponse.model_validate(result).data

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

    def wait_for_finish(self, *, wait_secs: int | None = None) -> Build | None:
        """Wait synchronously until the build finishes or the server times out.

        Args:
            wait_secs: How long does the client wait for build to finish. None for indefinite.

        Returns:
            The Actor build data. If the status on the object is not one of the terminal statuses (SUCCEEDED, FAILED,
                TIMED_OUT, ABORTED), then the build has not yet finished.
        """
        result = wait_for_finish_sync(
            http_client=self._http_client,
            url=self._build_url(),
            params=self._build_params(),
            wait_secs=wait_secs,
        )
        return Build.model_validate(result) if result is not None else None

    def log(self) -> LogClient:
        """Get the client for the log of the Actor build.

        https://docs.apify.com/api/v2/#/reference/actor-builds/build-log/get-log

        Returns:
            A client allowing access to the log of this Actor build.
        """
        return self._client_classes.log_client(
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
            return GetBuildResponse.model_validate(result).data
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
        return PostAbortBuildResponse.model_validate(result).data

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

    async def wait_for_finish(self, *, wait_secs: int | None = None) -> Build | None:
        """Wait synchronously until the build finishes or the server times out.

        Args:
            wait_secs: How long does the client wait for build to finish. None for indefinite.

        Returns:
            The Actor build data. If the status on the object is not one of the terminal statuses (SUCCEEDED, FAILED,
                TIMED_OUT, ABORTED), then the build has not yet finished.
        """
        result = await wait_for_finish_async(
            http_client=self._http_client,
            url=self._build_url(),
            params=self._build_params(),
            wait_secs=wait_secs,
        )
        return Build.model_validate(result) if result is not None else None

    def log(self) -> LogClientAsync:
        """Get the client for the log of the Actor build.

        https://docs.apify.com/api/v2/#/reference/actor-builds/build-log/get-log

        Returns:
            A client allowing access to the log of this Actor build.
        """
        return self._client_classes.log_client(
            resource_path='log',
            **self._base_client_kwargs,
        )

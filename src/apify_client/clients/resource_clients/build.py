from __future__ import annotations

from typing import Any

from apify_shared.utils import ignore_docs

from apify_client.clients.base import ActorJobBaseClient, ActorJobBaseClientAsync
from apify_client.clients.resource_clients.log import LogClient, LogClientAsync


class BuildClient(ActorJobBaseClient):
    """Sub-client for manipulating a single Actor build."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'actor-builds')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> dict | None:
        """Return information about the Actor build.

        https://docs.apify.com/api/v2#/reference/actor-builds/build-object/get-build

        Returns:
            The retrieved Actor build data.
        """
        return self._get()

    def delete(self) -> None:
        """Delete the build.

        https://docs.apify.com/api/v2#/reference/actor-builds/delete-build/delete-build
        """
        return self._delete()

    def abort(self) -> dict:
        """Abort the Actor build which is starting or currently running and return its details.

        https://docs.apify.com/api/v2#/reference/actor-builds/abort-build/abort-build

        Returns:
            The data of the aborted Actor build.
        """
        return self._abort()

    def get_open_api_definition(self) -> dict | None:
        """Return OpenAPI definition of the Actor's build.

        https://docs.apify.com/api/v2/actor-build-openapi-json-get

        Returns:
            OpenAPI definition of the Actor's build.
        """
        response = self.http_client.call(
            url=self._url('openapi.json'),
            method='GET',
        )

        response_data: dict = response.json()

        return response_data

    def wait_for_finish(self, *, wait_secs: int | None = None) -> dict | None:
        """Wait synchronously until the build finishes or the server times out.

        Args:
            wait_secs: How long does the client wait for build to finish. None for indefinite.

        Returns:
            The Actor build data. If the status on the object is not one of the terminal statuses (SUCEEDED, FAILED,
                TIMED_OUT, ABORTED), then the build has not yet finished.
        """
        return self._wait_for_finish(wait_secs=wait_secs)

    def log(self) -> LogClient:
        """Get the client for the log of the Actor build.

        https://docs.apify.com/api/v2/#/reference/actor-builds/build-log/get-log

        Returns:
            A client allowing access to the log of this Actor build.
        """
        return LogClient(
            **self._sub_resource_init_options(resource_path='log'),
        )


class BuildClientAsync(ActorJobBaseClientAsync):
    """Async sub-client for manipulating a single Actor build."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'actor-builds')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self) -> dict | None:
        """Return information about the Actor build.

        https://docs.apify.com/api/v2#/reference/actor-builds/build-object/get-build

        Returns:
            The retrieved Actor build data.
        """
        return await self._get()

    async def abort(self) -> dict:
        """Abort the Actor build which is starting or currently running and return its details.

        https://docs.apify.com/api/v2#/reference/actor-builds/abort-build/abort-build

        Returns:
            The data of the aborted Actor build.
        """
        return await self._abort()

    async def delete(self) -> None:
        """Delete the build.

        https://docs.apify.com/api/v2#/reference/actor-builds/delete-build/delete-build
        """
        return await self._delete()

    async def get_open_api_definition(self) -> dict | None:
        """Return OpenAPI definition of the Actor's build.

        https://docs.apify.com/api/v2/actor-build-openapi-json-get

        Returns:
            OpenAPI definition of the Actor's build.
        """
        response = await self.http_client.call(
            url=self._url('openapi.json'),
            method='GET',
        )

        response_data: dict = response.json()

        return response_data

    async def wait_for_finish(self, *, wait_secs: int | None = None) -> dict | None:
        """Wait synchronously until the build finishes or the server times out.

        Args:
            wait_secs: How long does the client wait for build to finish. None for indefinite.

        Returns:
            The Actor build data. If the status on the object is not one of the terminal statuses (SUCEEDED, FAILED,
                TIMED_OUT, ABORTED), then the build has not yet finished.
        """
        return await self._wait_for_finish(wait_secs=wait_secs)

    def log(self) -> LogClientAsync:
        """Get the client for the log of the Actor build.

        https://docs.apify.com/api/v2/#/reference/actor-builds/build-log/get-log

        Returns:
            A client allowing access to the log of this Actor build.
        """
        return LogClientAsync(
            **self._sub_resource_init_options(resource_path='log'),
        )

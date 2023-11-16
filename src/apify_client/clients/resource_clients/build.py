from __future__ import annotations

from typing import Any

from apify_shared.utils import ignore_docs

from ..base import ActorJobBaseClient, ActorJobBaseClientAsync


class BuildClient(ActorJobBaseClient):
    """Sub-client for manipulating a single actor build."""

    @ignore_docs
    def __init__(self: BuildClient, *args: Any, **kwargs: Any) -> None:
        """Initialize the BuildClient."""
        resource_path = kwargs.pop('resource_path', 'actor-builds')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self: BuildClient) -> dict | None:
        """Return information about the actor build.

        https://docs.apify.com/api/v2#/reference/actor-builds/build-object/get-build

        Returns:
            dict, optional: The retrieved actor build data
        """
        return self._get()

    def delete(self: BuildClient) -> None:
        """Delete the build.

        https://docs.apify.com/api/v2#/reference/actor-builds/delete-build/delete-build
        """
        return self._delete()

    def abort(self: BuildClient) -> dict:
        """Abort the actor build which is starting or currently running and return its details.

        https://docs.apify.com/api/v2#/reference/actor-builds/abort-build/abort-build

        Returns:
            dict: The data of the aborted actor build
        """
        return self._abort()

    def wait_for_finish(self: BuildClient, *, wait_secs: int | None = None) -> dict | None:
        """Wait synchronously until the build finishes or the server times out.

        Args:
            wait_secs (int, optional): how long does the client wait for build to finish. None for indefinite.

        Returns:
            dict, optional: The actor build data. If the status on the object is not one of the terminal statuses
                (SUCEEDED, FAILED, TIMED_OUT, ABORTED), then the build has not yet finished.
        """
        return self._wait_for_finish(wait_secs=wait_secs)


class BuildClientAsync(ActorJobBaseClientAsync):
    """Async sub-client for manipulating a single actor build."""

    @ignore_docs
    def __init__(self: BuildClientAsync, *args: Any, **kwargs: Any) -> None:
        """Initialize the BuildClientAsync."""
        resource_path = kwargs.pop('resource_path', 'actor-builds')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self: BuildClientAsync) -> dict | None:
        """Return information about the actor build.

        https://docs.apify.com/api/v2#/reference/actor-builds/build-object/get-build

        Returns:
            dict, optional: The retrieved actor build data
        """
        return await self._get()

    async def abort(self: BuildClientAsync) -> dict:
        """Abort the actor build which is starting or currently running and return its details.

        https://docs.apify.com/api/v2#/reference/actor-builds/abort-build/abort-build

        Returns:
            dict: The data of the aborted actor build
        """
        return await self._abort()

    async def delete(self: BuildClientAsync) -> None:
        """Delete the build.

        https://docs.apify.com/api/v2#/reference/actor-builds/delete-build/delete-build
        """
        return await self._delete()

    async def wait_for_finish(self: BuildClientAsync, *, wait_secs: int | None = None) -> dict | None:
        """Wait synchronously until the build finishes or the server times out.

        Args:
            wait_secs (int, optional): how long does the client wait for build to finish. None for indefinite.

        Returns:
            dict, optional: The actor build data. If the status on the object is not one of the terminal statuses
                (SUCEEDED, FAILED, TIMED_OUT, ABORTED), then the build has not yet finished.
        """
        return await self._wait_for_finish(wait_secs=wait_secs)

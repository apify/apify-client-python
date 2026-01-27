from __future__ import annotations

from typing import Any

from apify_client._models import GetListOfBuildsResponse, ListOfBuilds
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import response_to_dict


class BuildCollectionClient(ResourceClient):
    """Sub-client for listing Actor builds."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'actor-builds')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListOfBuilds:
        """List all Actor builds.

        List all Actor builds, either of a single Actor, or all user's Actors, depending on where this client
        was initialized from.

        https://docs.apify.com/api/v2#/reference/actors/build-collection/get-list-of-builds
        https://docs.apify.com/api/v2#/reference/actor-builds/build-collection/get-user-builds-list

        Args:
            limit: How many builds to retrieve.
            offset: What build to include as first when retrieving the list.
            desc: Whether to sort the builds in descending order based on their start date.

        Returns:
            The retrieved Actor builds.
        """
        response = self.http_client.call(
            url=self._url(),
            method='GET',
            params=self._params(limit=limit, offset=offset, desc=desc),
        )
        response_as_dict = response_to_dict(response)
        return GetListOfBuildsResponse.model_validate(response_as_dict).data


class BuildCollectionClientAsync(ResourceClientAsync):
    """Async sub-client for listing Actor builds."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'actor-builds')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListOfBuilds:
        """List all Actor builds.

        List all Actor builds, either of a single Actor, or all user's Actors, depending on where this client
        was initialized from.

        https://docs.apify.com/api/v2#/reference/actors/build-collection/get-list-of-builds
        https://docs.apify.com/api/v2#/reference/actor-builds/build-collection/get-user-builds-list

        Args:
            limit: How many builds to retrieve.
            offset: What build to include as first when retrieving the list.
            desc: Whether to sort the builds in descending order based on their start date.

        Returns:
            The retrieved Actor builds.
        """
        response = await self.http_client.call(
            url=self._url(),
            method='GET',
            params=self._params(limit=limit, offset=offset, desc=desc),
        )
        response_as_dict = response_to_dict(response)
        return GetListOfBuildsResponse.model_validate(response_as_dict).data

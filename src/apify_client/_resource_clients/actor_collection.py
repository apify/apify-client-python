from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from apify_client._models import Actor, ActorShort, CreateActorResponse, GetListOfActorsResponse, ListOfActors
from apify_client._representations import get_actor_representation
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import filter_none_values, response_to_dict

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator
    from datetime import timedelta


class ActorCollectionClient(ResourceClient):
    """Sub-client for manipulating Actors."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'acts')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self,
        *,
        my: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        sort_by: Literal['createdAt', 'stats.lastRunStartedAt'] | None = 'createdAt',
    ) -> ListOfActors:
        """List the Actors the user has created or used.

        https://docs.apify.com/api/v2#/reference/actors/actor-collection/get-list-of-actors

        Args:
            my: If True, will return only Actors which the user has created themselves.
            limit: How many Actors to list.
            offset: What Actor to include as first when retrieving the list.
            desc: Whether to sort the Actors in descending order based on their creation date.
            sort_by: Field to sort the results by.

        Returns:
            The list of available Actors matching the specified filters.
        """
        response = self._http_client.call(
            url=self._build_url(),
            method='GET',
            params=self._build_params(my=my, limit=limit, offset=offset, desc=desc, sortBy=sort_by),
        )
        response_as_dict = response_to_dict(response)
        return GetListOfActorsResponse.model_validate(response_as_dict).data

    def iterate(
        self,
        *,
        my: bool | None = None,
        limit: int | None = None,
        desc: bool | None = None,
    ) -> Iterator[ActorShort]:
        """Iterate over the Actors the user has created or used.

        https://docs.apify.com/api/v2#/reference/actors/actor-collection/get-list-of-actors

        Args:
            my: If True, will return only Actors which the user has created themselves.
            limit: Maximum number of Actors to return. By default there is no limit.
            desc: Whether to sort the Actors in descending order based on their creation date.

        Yields:
            An Actor from the collection.
        """
        cache_size = 1000
        read_items = 0
        offset = 0

        while True:
            effective_limit = cache_size
            if limit is not None:
                if read_items == limit:
                    break
                effective_limit = min(cache_size, limit - read_items)

            current_page = self.list(
                my=my,
                limit=effective_limit,
                offset=offset,
                desc=desc,
            )

            yield from current_page.items

            current_page_item_count = len(current_page.items)
            read_items += current_page_item_count
            offset += current_page_item_count

            if current_page_item_count < cache_size:
                break

    def create(
        self,
        *,
        name: str,
        title: str | None = None,
        description: str | None = None,
        seo_title: str | None = None,
        seo_description: str | None = None,
        versions: list[dict] | None = None,  # ty: ignore[invalid-type-form]
        restart_on_error: bool | None = None,
        is_public: bool | None = None,
        is_deprecated: bool | None = None,
        is_anonymously_runnable: bool | None = None,
        categories: list[str] | None = None,  # ty: ignore[invalid-type-form]
        default_run_build: str | None = None,
        default_run_max_items: int | None = None,
        default_run_memory_mbytes: int | None = None,
        default_run_timeout: timedelta | None = None,
        example_run_input_body: Any = None,
        example_run_input_content_type: str | None = None,
        actor_standby_is_enabled: bool | None = None,
        actor_standby_desired_requests_per_actor_run: int | None = None,
        actor_standby_max_requests_per_actor_run: int | None = None,
        actor_standby_idle_timeout: timedelta | None = None,
        actor_standby_build: str | None = None,
        actor_standby_memory_mbytes: int | None = None,
    ) -> Actor:
        """Create a new Actor.

        https://docs.apify.com/api/v2#/reference/actors/actor-collection/create-actor

        Args:
            name: The name of the Actor.
            title: The title of the Actor (human-readable).
            description: The description for the Actor.
            seo_title: The title of the Actor optimized for search engines.
            seo_description: The description of the Actor optimized for search engines.
            versions: The list of Actor versions.
            restart_on_error: If true, the Actor run process will be restarted whenever it exits with
                a non-zero status code.
            is_public: Whether the Actor is public.
            is_deprecated: Whether the Actor is deprecated.
            is_anonymously_runnable: Whether the Actor is anonymously runnable.
            categories: The categories to which the Actor belongs to.
            default_run_build: Tag or number of the build that you want to run by default.
            default_run_max_items: Default limit of the number of results that will be returned by runs
                of this Actor, if the Actor is charged per result.
            default_run_memory_mbytes: Default amount of memory allocated for the runs of this Actor, in megabytes.
            default_run_timeout: Default timeout for the runs of this Actor.
            example_run_input_body: Input to be prefilled as default input to new users of this Actor.
            example_run_input_content_type: The content type of the example run input.
            actor_standby_is_enabled: Whether the Actor Standby is enabled.
            actor_standby_desired_requests_per_actor_run: The desired number of concurrent HTTP requests for
                a single Actor Standby run.
            actor_standby_max_requests_per_actor_run: The maximum number of concurrent HTTP requests for
                a single Actor Standby run.
            actor_standby_idle_timeout: If the Actor run does not receive any requests for this time,
                it will be shut down.
            actor_standby_build: The build tag or number to run when the Actor is in Standby mode.
            actor_standby_memory_mbytes: The memory in megabytes to use when the Actor is in Standby mode.

        Returns:
            The created Actor.
        """
        actor_representation = get_actor_representation(
            name=name,
            title=title,
            description=description,
            seo_title=seo_title,
            seo_description=seo_description,
            versions=versions,
            restart_on_error=restart_on_error,
            is_public=is_public,
            is_deprecated=is_deprecated,
            is_anonymously_runnable=is_anonymously_runnable,
            categories=categories,
            default_run_build=default_run_build,
            default_run_max_items=default_run_max_items,
            default_run_memory_mbytes=default_run_memory_mbytes,
            default_run_timeout=default_run_timeout,
            example_run_input_body=example_run_input_body,
            example_run_input_content_type=example_run_input_content_type,
            actor_standby_is_enabled=actor_standby_is_enabled,
            actor_standby_desired_requests_per_actor_run=actor_standby_desired_requests_per_actor_run,
            actor_standby_max_requests_per_actor_run=actor_standby_max_requests_per_actor_run,
            actor_standby_idle_timeout=actor_standby_idle_timeout,
            actor_standby_build=actor_standby_build,
            actor_standby_memory_mbytes=actor_standby_memory_mbytes,
        )

        response = self._http_client.call(
            url=self._build_url(),
            method='POST',
            params=self._build_params(),
            json=filter_none_values(actor_representation, remove_empty_dicts=True),
        )

        result = response_to_dict(response)
        return CreateActorResponse.model_validate(result).data


class ActorCollectionClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating Actors."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'acts')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(
        self,
        *,
        my: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        sort_by: Literal['createdAt', 'stats.lastRunStartedAt'] | None = 'createdAt',
    ) -> ListOfActors:
        """List the Actors the user has created or used.

        https://docs.apify.com/api/v2#/reference/actors/actor-collection/get-list-of-actors

        Args:
            my: If True, will return only Actors which the user has created themselves.
            limit: How many Actors to list.
            offset: What Actor to include as first when retrieving the list.
            desc: Whether to sort the Actors in descending order based on their creation date.
            sort_by: Field to sort the results by.

        Returns:
            The list of available Actors matching the specified filters.
        """
        response = await self._http_client.call(
            url=self._build_url(),
            method='GET',
            params=self._build_params(my=my, limit=limit, offset=offset, desc=desc, sortBy=sort_by),
        )
        response_as_dict = response_to_dict(response)
        return GetListOfActorsResponse.model_validate(response_as_dict).data

    async def iterate(
        self,
        *,
        my: bool | None = None,
        limit: int | None = None,
        desc: bool | None = None,
    ) -> AsyncIterator[ActorShort]:
        """Iterate over the Actors the user has created or used.

        https://docs.apify.com/api/v2#/reference/actors/actor-collection/get-list-of-actors

        Args:
            my: If True, will return only Actors which the user has created themselves.
            limit: Maximum number of Actors to return. By default there is no limit.
            desc: Whether to sort the Actors in descending order based on their creation date.

        Yields:
            An Actor from the collection.
        """
        cache_size = 1000
        read_items = 0
        offset = 0

        while True:
            effective_limit = cache_size
            if limit is not None:
                if read_items == limit:
                    break
                effective_limit = min(cache_size, limit - read_items)

            current_page = await self.list(
                my=my,
                limit=effective_limit,
                offset=offset,
                desc=desc,
            )

            for item in current_page.items:
                yield item

            current_page_item_count = len(current_page.items)
            read_items += current_page_item_count
            offset += current_page_item_count

            if current_page_item_count < cache_size:
                break

    async def create(
        self,
        *,
        name: str,
        title: str | None = None,
        description: str | None = None,
        seo_title: str | None = None,
        seo_description: str | None = None,
        versions: list[dict] | None = None,  # ty: ignore[invalid-type-form]
        restart_on_error: bool | None = None,
        is_public: bool | None = None,
        is_deprecated: bool | None = None,
        is_anonymously_runnable: bool | None = None,
        categories: list[str] | None = None,  # ty: ignore[invalid-type-form]
        default_run_build: str | None = None,
        default_run_max_items: int | None = None,
        default_run_memory_mbytes: int | None = None,
        default_run_timeout: timedelta | None = None,
        example_run_input_body: Any = None,
        example_run_input_content_type: str | None = None,
        actor_standby_is_enabled: bool | None = None,
        actor_standby_desired_requests_per_actor_run: int | None = None,
        actor_standby_max_requests_per_actor_run: int | None = None,
        actor_standby_idle_timeout: timedelta | None = None,
        actor_standby_build: str | None = None,
        actor_standby_memory_mbytes: int | None = None,
    ) -> Actor:
        """Create a new Actor.

        https://docs.apify.com/api/v2#/reference/actors/actor-collection/create-actor

        Args:
            name: The name of the Actor.
            title: The title of the Actor (human-readable).
            description: The description for the Actor.
            seo_title: The title of the Actor optimized for search engines.
            seo_description: The description of the Actor optimized for search engines.
            versions: The list of Actor versions.
            restart_on_error: If true, the Actor run process will be restarted whenever it exits with
                a non-zero status code.
            is_public: Whether the Actor is public.
            is_deprecated: Whether the Actor is deprecated.
            is_anonymously_runnable: Whether the Actor is anonymously runnable.
            categories: The categories to which the Actor belongs to.
            default_run_build: Tag or number of the build that you want to run by default.
            default_run_max_items: Default limit of the number of results that will be returned by runs
                of this Actor, if the Actor is charged per result.
            default_run_memory_mbytes: Default amount of memory allocated for the runs of this Actor, in megabytes.
            default_run_timeout: Default timeout for the runs of this Actor.
            example_run_input_body: Input to be prefilled as default input to new users of this Actor.
            example_run_input_content_type: The content type of the example run input.
            actor_standby_is_enabled: Whether the Actor Standby is enabled.
            actor_standby_desired_requests_per_actor_run: The desired number of concurrent HTTP requests for
                a single Actor Standby run.
            actor_standby_max_requests_per_actor_run: The maximum number of concurrent HTTP requests for
                a single Actor Standby run.
            actor_standby_idle_timeout: If the Actor run does not receive any requests for this time,
                it will be shut down.
            actor_standby_build: The build tag or number to run when the Actor is in Standby mode.
            actor_standby_memory_mbytes: The memory in megabytes to use when the Actor is in Standby mode.

        Returns:
            The created Actor.
        """
        actor_representation = get_actor_representation(
            name=name,
            title=title,
            description=description,
            seo_title=seo_title,
            seo_description=seo_description,
            versions=versions,
            restart_on_error=restart_on_error,
            is_public=is_public,
            is_deprecated=is_deprecated,
            is_anonymously_runnable=is_anonymously_runnable,
            categories=categories,
            default_run_build=default_run_build,
            default_run_max_items=default_run_max_items,
            default_run_memory_mbytes=default_run_memory_mbytes,
            default_run_timeout=default_run_timeout,
            example_run_input_body=example_run_input_body,
            example_run_input_content_type=example_run_input_content_type,
            actor_standby_is_enabled=actor_standby_is_enabled,
            actor_standby_desired_requests_per_actor_run=actor_standby_desired_requests_per_actor_run,
            actor_standby_max_requests_per_actor_run=actor_standby_max_requests_per_actor_run,
            actor_standby_idle_timeout=actor_standby_idle_timeout,
            actor_standby_build=actor_standby_build,
            actor_standby_memory_mbytes=actor_standby_memory_mbytes,
        )

        response = await self._http_client.call(
            url=self._build_url(),
            method='POST',
            params=self._build_params(),
            json=filter_none_values(actor_representation, remove_empty_dicts=True),
        )

        result = response_to_dict(response)
        return CreateActorResponse.model_validate(result).data

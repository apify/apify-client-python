from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from apify_client._docs import docs_group
from apify_client._models import (
    Actor,
    ActorResponse,
    ActorStandby,
    CreateActorRequest,
    DefaultRunOptions,
    ExampleRunInput,
    ListOfActors,
    ListOfActorsResponse,
)
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import to_seconds

if TYPE_CHECKING:
    from datetime import timedelta

    from apify_client._types import Timeout


@docs_group('Resource clients')
class ActorCollectionClient(ResourceClient):
    """Sub-client for the Actor collection.

    Provides methods to manage the Actor collection, e.g. list or create Actors. Obtain an instance via an appropriate
    method on the `ApifyClient` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'acts',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_path=resource_path,
            **kwargs,
        )

    def list(
        self,
        *,
        my: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        sort_by: Literal['createdAt', 'stats.lastRunStartedAt'] | None = 'createdAt',
        timeout: Timeout = 'medium',
    ) -> ListOfActors:
        """List the Actors the user has created or used.

        https://docs.apify.com/api/v2#/reference/actors/actor-collection/get-list-of-actors

        Args:
            my: If True, will return only Actors which the user has created themselves.
            limit: How many Actors to list.
            offset: What Actor to include as first when retrieving the list.
            desc: Whether to sort the Actors in descending order based on their creation date.
            sort_by: Field to sort the results by.
            timeout: Timeout for the API HTTP request.

        Returns:
            The list of available Actors matching the specified filters.
        """
        result = self._list(timeout=timeout, my=my, limit=limit, offset=offset, desc=desc, sortBy=sort_by)
        return ListOfActorsResponse.model_validate(result).data

    def create(
        self,
        *,
        name: str,
        title: str | None = None,
        description: str | None = None,
        seo_title: str | None = None,
        seo_description: str | None = None,
        versions: list[dict[str, Any]] | None = None,  # ty: ignore[invalid-type-form]
        restart_on_error: bool | None = None,
        is_public: bool | None = None,
        is_deprecated: bool | None = None,
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
        timeout: Timeout = 'medium',
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
            timeout: Timeout for the API HTTP request.

        Returns:
            The created Actor.
        """
        actor_fields = CreateActorRequest(
            name=name,
            title=title,
            description=description,
            seo_title=seo_title,
            seo_description=seo_description,
            versions=versions,
            is_public=is_public,
            is_deprecated=is_deprecated,
            categories=categories,
            default_run_options=DefaultRunOptions(
                build=default_run_build,
                max_items=default_run_max_items,
                memory_mbytes=default_run_memory_mbytes,
                timeout_secs=to_seconds(default_run_timeout, as_int=True),
                restart_on_error=restart_on_error,
            ),
            actor_standby=ActorStandby(
                is_enabled=actor_standby_is_enabled,
                desired_requests_per_actor_run=actor_standby_desired_requests_per_actor_run,
                max_requests_per_actor_run=actor_standby_max_requests_per_actor_run,
                idle_timeout_secs=to_seconds(actor_standby_idle_timeout, as_int=True),
                build=actor_standby_build,
                memory_mbytes=actor_standby_memory_mbytes,
            ),
            example_run_input=ExampleRunInput(
                body=example_run_input_body,
                content_type=example_run_input_content_type,
            ),
        )
        result = self._create(timeout=timeout, **actor_fields.model_dump(by_alias=True, exclude_none=True))
        return ActorResponse.model_validate(result).data


@docs_group('Resource clients')
class ActorCollectionClientAsync(ResourceClientAsync):
    """Sub-client for the Actor collection.

    Provides methods to manage the Actor collection, e.g. list or create Actors. Obtain an instance via an appropriate
    method on the `ApifyClientAsync` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'acts',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_path=resource_path,
            **kwargs,
        )

    async def list(
        self,
        *,
        my: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        sort_by: Literal['createdAt', 'stats.lastRunStartedAt'] | None = 'createdAt',
        timeout: Timeout = 'medium',
    ) -> ListOfActors:
        """List the Actors the user has created or used.

        https://docs.apify.com/api/v2#/reference/actors/actor-collection/get-list-of-actors

        Args:
            my: If True, will return only Actors which the user has created themselves.
            limit: How many Actors to list.
            offset: What Actor to include as first when retrieving the list.
            desc: Whether to sort the Actors in descending order based on their creation date.
            sort_by: Field to sort the results by.
            timeout: Timeout for the API HTTP request.

        Returns:
            The list of available Actors matching the specified filters.
        """
        result = await self._list(timeout=timeout, my=my, limit=limit, offset=offset, desc=desc, sortBy=sort_by)
        return ListOfActorsResponse.model_validate(result).data

    async def create(
        self,
        *,
        name: str,
        title: str | None = None,
        description: str | None = None,
        seo_title: str | None = None,
        seo_description: str | None = None,
        versions: list[dict[str, Any]] | None = None,  # ty: ignore[invalid-type-form]
        restart_on_error: bool | None = None,
        is_public: bool | None = None,
        is_deprecated: bool | None = None,
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
        timeout: Timeout = 'medium',
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
            timeout: Timeout for the API HTTP request.

        Returns:
            The created Actor.
        """
        actor_fields = CreateActorRequest(
            name=name,
            title=title,
            description=description,
            seo_title=seo_title,
            seo_description=seo_description,
            versions=versions,
            is_public=is_public,
            is_deprecated=is_deprecated,
            categories=categories,
            default_run_options=DefaultRunOptions(
                build=default_run_build,
                max_items=default_run_max_items,
                memory_mbytes=default_run_memory_mbytes,
                timeout_secs=to_seconds(default_run_timeout, as_int=True),
                restart_on_error=restart_on_error,
            ),
            actor_standby=ActorStandby(
                is_enabled=actor_standby_is_enabled,
                desired_requests_per_actor_run=actor_standby_desired_requests_per_actor_run,
                max_requests_per_actor_run=actor_standby_max_requests_per_actor_run,
                idle_timeout_secs=to_seconds(actor_standby_idle_timeout, as_int=True),
                build=actor_standby_build,
                memory_mbytes=actor_standby_memory_mbytes,
            ),
            example_run_input=ExampleRunInput(
                body=example_run_input_body,
                content_type=example_run_input_content_type,
            ),
        )
        result = await self._create(timeout=timeout, **actor_fields.model_dump(by_alias=True, exclude_none=True))
        return ActorResponse.model_validate(result).data

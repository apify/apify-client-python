from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from apify_client._docs import docs_group
from apify_client._models import (
    ActorResource,
    ActorResponse,
    CreateActorRequest,
    DefaultRunOptions,
    ExampleRunInput,
    ListOfActors,
    ListOfActorsResponse,
)
from apify_client._pagination import get_items_iterator, get_items_iterator_async
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils.server_args import build_actor_standby
from apify_client._utils.time import to_seconds

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator
    from datetime import timedelta

    from apify_client._literals import ActorPermissionLevel, Tenancy
    from apify_client._models import ActorListItem
    from apify_client.types import Timeout


@docs_group('Resource clients')
class ActorCollectionClient(ResourceClient):
    """Sub-client for the Actor collection.

    Provides methods to manage the Actor collection, e.g. list or create Actors. Obtain an instance via an appropriate
    method on the `ApifyClient` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'actors',
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

    def iterate(
        self,
        *,
        my: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        sort_by: Literal['createdAt', 'stats.lastRunStartedAt'] | None = 'createdAt',
        chunk_size: int | None = None,
        timeout: Timeout = 'medium',
    ) -> Iterator[ActorListItem]:
        """Iterate over the Actors the user has created or used.

        Simple `list` does only one API call, possibly not listing all items matching the criteria. This method
        returns an iterator that is capable of making multiple API calls to retrieve all items matching the criteria.

        https://docs.apify.com/api/v2#/reference/actors/actor-collection/get-list-of-actors

        Args:
            my: If True, will return only Actors which the user has created themselves.
            limit: How many Actors to list.
            offset: What Actor to include as first when retrieving the list.
            desc: Whether to sort the Actors in descending order based on their creation date.
            sort_by: Field to sort the results by.
            chunk_size: Maximum number of Actors requested per API call when iterating across pages.
            timeout: Timeout for the API HTTP request.

        Yields:
            The Actors available to the user matching the specified filters.
        """

        def _callback(*, limit: int | None = None, offset: int | None = None) -> ListOfActors:
            return self.list(my=my, limit=limit, offset=offset, desc=desc, sort_by=sort_by, timeout=timeout)

        return get_items_iterator(_callback, limit=limit, offset=offset, chunk_size=chunk_size)

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
        default_run_force_permission_level: ActorPermissionLevel | None = None,
        example_run_input_body: str | None = None,
        example_run_input_content_type: str | None = None,
        server_is_enabled: bool | None = None,
        server_desired_requests_per_actor_run: int | None = None,
        server_max_requests_per_actor_run: int | None = None,
        server_idle_timeout: timedelta | None = None,
        server_build: str | None = None,
        server_memory_mbytes: int | None = None,
        server_disable_fields_override: bool | None = None,
        server_should_pass_actor_input: bool | None = None,
        server_tenancy: Tenancy | None = None,
        actor_permission_level: ActorPermissionLevel | None = None,
        timeout: Timeout = 'medium',
        actor_standby_is_enabled: bool | None = None,
        actor_standby_desired_requests_per_actor_run: int | None = None,
        actor_standby_max_requests_per_actor_run: int | None = None,
        actor_standby_idle_timeout: timedelta | None = None,
        actor_standby_build: str | None = None,
        actor_standby_memory_mbytes: int | None = None,
        actor_standby_disable_standby_fields_override: bool | None = None,
        actor_standby_should_pass_actor_input: bool | None = None,
        actor_standby_tenancy: Tenancy | None = None,
    ) -> ActorResource:
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
            default_run_force_permission_level: Permission level to force on the runs of this Actor, overriding the
                permission level of the Actor.
            example_run_input_body: Input to be prefilled as default input to new users of this Actor, serialized
                as a string (e.g. `json.dumps(input)` for a JSON input).
            example_run_input_content_type: The content type of the example run input.
            server_is_enabled: Whether the Actor is a Server Actor, which runs a web server called over HTTP.
            server_desired_requests_per_actor_run: The desired number of concurrent HTTP requests for a single run of
                the Server Actor.
            server_max_requests_per_actor_run: The maximum number of concurrent HTTP requests for a single run of the
                Server Actor.
            server_idle_timeout: If a run of the Server Actor does not receive any requests for this time, it is shut
                down.
            server_build: The build tag or number that the Server Actor runs.
            server_memory_mbytes: The memory in megabytes for the runs of the Server Actor.
            server_disable_fields_override: If true, prevents the Server Actor configuration from being overridden
                elsewhere.
            server_should_pass_actor_input: Whether to pass the Actor input to the runs of the Server Actor. If false,
                they start with no input.
            server_tenancy: Whether each user gets their own runs of the Server Actor (`SINGLE_TENANT`) or the runs are
                shared across users (`MULTI_TENANT`). `MULTI_TENANT` requires pay-per-event pricing.
            actor_permission_level: The permission level of the Actor on Apify platform.
            timeout: Timeout for the API HTTP request.
            actor_standby_is_enabled: Deprecated alias of `server_is_enabled`. Will be removed in v4.
            actor_standby_desired_requests_per_actor_run: Deprecated alias of `server_desired_requests_per_actor_run`.
                Will be removed in v4.
            actor_standby_max_requests_per_actor_run: Deprecated alias of `server_max_requests_per_actor_run`. Will be
                removed in v4.
            actor_standby_idle_timeout: Deprecated alias of `server_idle_timeout`. Will be removed in v4.
            actor_standby_build: Deprecated alias of `server_build`. Will be removed in v4.
            actor_standby_memory_mbytes: Deprecated alias of `server_memory_mbytes`. Will be removed in v4.
            actor_standby_disable_standby_fields_override: Deprecated alias of `server_disable_fields_override`. Will be
                removed in v4.
            actor_standby_should_pass_actor_input: Deprecated alias of `server_should_pass_actor_input`. Will be removed
                in v4.
            actor_standby_tenancy: Deprecated alias of `server_tenancy`. Will be removed in v4.

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
            actor_permission_level=actor_permission_level,
            is_deprecated=is_deprecated,
            categories=categories,
            default_run_options=DefaultRunOptions(
                build=default_run_build,
                max_items=default_run_max_items,
                memory_mbytes=default_run_memory_mbytes,
                timeout_secs=to_seconds(default_run_timeout, as_int=True),
                force_permission_level=default_run_force_permission_level,
                restart_on_error=restart_on_error,
            ),
            actor_standby=build_actor_standby(
                {
                    'server_is_enabled': server_is_enabled,
                    'server_desired_requests_per_actor_run': server_desired_requests_per_actor_run,
                    'server_max_requests_per_actor_run': server_max_requests_per_actor_run,
                    'server_idle_timeout': server_idle_timeout,
                    'server_build': server_build,
                    'server_memory_mbytes': server_memory_mbytes,
                    'server_disable_fields_override': server_disable_fields_override,
                    'server_should_pass_actor_input': server_should_pass_actor_input,
                    'server_tenancy': server_tenancy,
                },
                {
                    'actor_standby_is_enabled': actor_standby_is_enabled,
                    'actor_standby_desired_requests_per_actor_run': actor_standby_desired_requests_per_actor_run,
                    'actor_standby_max_requests_per_actor_run': actor_standby_max_requests_per_actor_run,
                    'actor_standby_idle_timeout': actor_standby_idle_timeout,
                    'actor_standby_build': actor_standby_build,
                    'actor_standby_memory_mbytes': actor_standby_memory_mbytes,
                    'actor_standby_disable_standby_fields_override': actor_standby_disable_standby_fields_override,
                    'actor_standby_should_pass_actor_input': actor_standby_should_pass_actor_input,
                    'actor_standby_tenancy': actor_standby_tenancy,
                },
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
        resource_path: str = 'actors',
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

    def iterate(
        self,
        *,
        my: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        sort_by: Literal['createdAt', 'stats.lastRunStartedAt'] | None = 'createdAt',
        chunk_size: int | None = None,
        timeout: Timeout = 'medium',
    ) -> AsyncIterator[ActorListItem]:
        """Iterate over the Actors the user has created or used.

        Simple `list` does only one API call, possibly not listing all items matching the criteria. This method
        returns an iterator that is capable of making multiple API calls to retrieve all items matching the criteria.

        https://docs.apify.com/api/v2#/reference/actors/actor-collection/get-list-of-actors

        Args:
            my: If True, will return only Actors which the user has created themselves.
            limit: How many Actors to list.
            offset: What Actor to include as first when retrieving the list.
            desc: Whether to sort the Actors in descending order based on their creation date.
            sort_by: Field to sort the results by.
            chunk_size: Maximum number of Actors requested per API call when iterating across pages.
            timeout: Timeout for the API HTTP request.

        Yields:
            The Actors available to the user matching the specified filters.
        """

        async def _callback(*, limit: int | None = None, offset: int | None = None) -> ListOfActors:
            return await self.list(my=my, limit=limit, offset=offset, desc=desc, sort_by=sort_by, timeout=timeout)

        return get_items_iterator_async(_callback, limit=limit, offset=offset, chunk_size=chunk_size)

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
        default_run_force_permission_level: ActorPermissionLevel | None = None,
        example_run_input_body: str | None = None,
        example_run_input_content_type: str | None = None,
        server_is_enabled: bool | None = None,
        server_desired_requests_per_actor_run: int | None = None,
        server_max_requests_per_actor_run: int | None = None,
        server_idle_timeout: timedelta | None = None,
        server_build: str | None = None,
        server_memory_mbytes: int | None = None,
        server_disable_fields_override: bool | None = None,
        server_should_pass_actor_input: bool | None = None,
        server_tenancy: Tenancy | None = None,
        actor_permission_level: ActorPermissionLevel | None = None,
        timeout: Timeout = 'medium',
        actor_standby_is_enabled: bool | None = None,
        actor_standby_desired_requests_per_actor_run: int | None = None,
        actor_standby_max_requests_per_actor_run: int | None = None,
        actor_standby_idle_timeout: timedelta | None = None,
        actor_standby_build: str | None = None,
        actor_standby_memory_mbytes: int | None = None,
        actor_standby_disable_standby_fields_override: bool | None = None,
        actor_standby_should_pass_actor_input: bool | None = None,
        actor_standby_tenancy: Tenancy | None = None,
    ) -> ActorResource:
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
            default_run_force_permission_level: Permission level to force on the runs of this Actor, overriding the
                permission level of the Actor.
            example_run_input_body: Input to be prefilled as default input to new users of this Actor, serialized
                as a string (e.g. `json.dumps(input)` for a JSON input).
            example_run_input_content_type: The content type of the example run input.
            server_is_enabled: Whether the Actor is a Server Actor, which runs a web server called over HTTP.
            server_desired_requests_per_actor_run: The desired number of concurrent HTTP requests for a single run of
                the Server Actor.
            server_max_requests_per_actor_run: The maximum number of concurrent HTTP requests for a single run of the
                Server Actor.
            server_idle_timeout: If a run of the Server Actor does not receive any requests for this time, it is shut
                down.
            server_build: The build tag or number that the Server Actor runs.
            server_memory_mbytes: The memory in megabytes for the runs of the Server Actor.
            server_disable_fields_override: If true, prevents the Server Actor configuration from being overridden
                elsewhere.
            server_should_pass_actor_input: Whether to pass the Actor input to the runs of the Server Actor. If false,
                they start with no input.
            server_tenancy: Whether each user gets their own runs of the Server Actor (`SINGLE_TENANT`) or the runs are
                shared across users (`MULTI_TENANT`). `MULTI_TENANT` requires pay-per-event pricing.
            actor_permission_level: The permission level of the Actor on Apify platform.
            timeout: Timeout for the API HTTP request.
            actor_standby_is_enabled: Deprecated alias of `server_is_enabled`. Will be removed in v4.
            actor_standby_desired_requests_per_actor_run: Deprecated alias of `server_desired_requests_per_actor_run`.
                Will be removed in v4.
            actor_standby_max_requests_per_actor_run: Deprecated alias of `server_max_requests_per_actor_run`. Will be
                removed in v4.
            actor_standby_idle_timeout: Deprecated alias of `server_idle_timeout`. Will be removed in v4.
            actor_standby_build: Deprecated alias of `server_build`. Will be removed in v4.
            actor_standby_memory_mbytes: Deprecated alias of `server_memory_mbytes`. Will be removed in v4.
            actor_standby_disable_standby_fields_override: Deprecated alias of `server_disable_fields_override`. Will be
                removed in v4.
            actor_standby_should_pass_actor_input: Deprecated alias of `server_should_pass_actor_input`. Will be removed
                in v4.
            actor_standby_tenancy: Deprecated alias of `server_tenancy`. Will be removed in v4.

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
            actor_permission_level=actor_permission_level,
            is_deprecated=is_deprecated,
            categories=categories,
            default_run_options=DefaultRunOptions(
                build=default_run_build,
                max_items=default_run_max_items,
                memory_mbytes=default_run_memory_mbytes,
                timeout_secs=to_seconds(default_run_timeout, as_int=True),
                force_permission_level=default_run_force_permission_level,
                restart_on_error=restart_on_error,
            ),
            actor_standby=build_actor_standby(
                {
                    'server_is_enabled': server_is_enabled,
                    'server_desired_requests_per_actor_run': server_desired_requests_per_actor_run,
                    'server_max_requests_per_actor_run': server_max_requests_per_actor_run,
                    'server_idle_timeout': server_idle_timeout,
                    'server_build': server_build,
                    'server_memory_mbytes': server_memory_mbytes,
                    'server_disable_fields_override': server_disable_fields_override,
                    'server_should_pass_actor_input': server_should_pass_actor_input,
                    'server_tenancy': server_tenancy,
                },
                {
                    'actor_standby_is_enabled': actor_standby_is_enabled,
                    'actor_standby_desired_requests_per_actor_run': actor_standby_desired_requests_per_actor_run,
                    'actor_standby_max_requests_per_actor_run': actor_standby_max_requests_per_actor_run,
                    'actor_standby_idle_timeout': actor_standby_idle_timeout,
                    'actor_standby_build': actor_standby_build,
                    'actor_standby_memory_mbytes': actor_standby_memory_mbytes,
                    'actor_standby_disable_standby_fields_override': actor_standby_disable_standby_fields_override,
                    'actor_standby_should_pass_actor_input': actor_standby_should_pass_actor_input,
                    'actor_standby_tenancy': actor_standby_tenancy,
                },
            ),
            example_run_input=ExampleRunInput(
                body=example_run_input_body,
                content_type=example_run_input_content_type,
            ),
        )
        result = await self._create(timeout=timeout, **actor_fields.model_dump(by_alias=True, exclude_none=True))
        return ActorResponse.model_validate(result).data

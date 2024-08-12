from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_shared.utils import filter_out_none_values_recursively, ignore_docs

from apify_client.clients.base import ResourceCollectionClient, ResourceCollectionClientAsync
from apify_client.clients.resource_clients.actor import get_actor_representation

if TYPE_CHECKING:
    from apify_shared.models import ListPage


class ActorCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating Actors."""

    @ignore_docs
    def __init__(self: ActorCollectionClient, *args: Any, **kwargs: Any) -> None:
        """Initialize the ActorCollectionClient."""
        resource_path = kwargs.pop('resource_path', 'acts')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self: ActorCollectionClient,
        *,
        my: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListPage[dict]:
        """List the Actors the user has created or used.

        https://docs.apify.com/api/v2#/reference/actors/actor-collection/get-list-of-actors

        Args:
            my (bool, optional): If True, will return only Actors which the user has created themselves.
            limit (int, optional): How many Actors to list
            offset (int, optional): What Actor to include as first when retrieving the list
            desc (bool, optional): Whether to sort the Actors in descending order based on their creation date

        Returns:
            ListPage: The list of available Actors matching the specified filters.
        """
        return self._list(my=my, limit=limit, offset=offset, desc=desc)

    def create(
        self: ActorCollectionClient,
        *,
        name: str,
        title: str | None = None,
        description: str | None = None,
        seo_title: str | None = None,
        seo_description: str | None = None,
        versions: list[dict] | None = None,  # type: ignore
        restart_on_error: bool | None = None,
        is_public: bool | None = None,
        is_deprecated: bool | None = None,
        is_anonymously_runnable: bool | None = None,
        categories: list[str] | None = None,  # type: ignore
        default_run_build: str | None = None,
        default_run_max_items: int | None = None,
        default_run_memory_mbytes: int | None = None,
        default_run_timeout_secs: int | None = None,
        example_run_input_body: Any = None,
        example_run_input_content_type: str | None = None,
        actor_standby_is_enabled: bool | None = None,
        actor_standby_desired_requests_per_actor_run: int | None = None,
        actor_standby_max_requests_per_actor_run: int | None = None,
        actor_standby_idle_timeout_secs: int | None = None,
        actor_standby_build: str | None = None,
        actor_standby_memory_mbytes: int | None = None,
    ) -> dict:
        """Create a new Actor.

        https://docs.apify.com/api/v2#/reference/actors/actor-collection/create-actor

        Args:
            name (str): The name of the Actor
            title (str, optional): The title of the Actor (human-readable)
            description (str, optional): The description for the Actor
            seo_title (str, optional): The title of the Actor optimized for search engines
            seo_description (str, optional): The description of the Actor optimized for search engines
            versions (list of dict, optional): The list of Actor versions
            restart_on_error (bool, optional): If true, the main Actor run process will be restarted whenever it exits with a non-zero status code.
            is_public (bool, optional): Whether the Actor is public.
            is_deprecated (bool, optional): Whether the Actor is deprecated.
            is_anonymously_runnable (bool, optional): Whether the Actor is anonymously runnable.
            categories (list of str, optional): The categories to which the Actor belongs to.
            default_run_build (str, optional): Tag or number of the build that you want to run by default.
            default_run_max_items (int, optional): Default limit of the number of results that will be returned by runs of this Actor,
                                                   if the Actor is charged per result.
            default_run_memory_mbytes (int, optional): Default amount of memory allocated for the runs of this Actor, in megabytes.
            default_run_timeout_secs (int, optional): Default timeout for the runs of this Actor in seconds.
            example_run_input_body (Any, optional): Input to be prefilled as default input to new users of this Actor.
            example_run_input_content_type (str, optional): The content type of the example run input.
            actor_standby_is_enabled (bool, optional): Whether the Actor Standby is enabled.
            actor_standby_desired_requests_per_actor_run (int, optional): The desired number of concurrent HTTP requests for
                a single Actor Standby run.
            actor_standby_max_requests_per_actor_run (int, optional): The maximum number of concurrent HTTP requests for a single Actor Standby run.
            actor_standby_idle_timeout_secs (int, optional): If the Actor run does not receive any requests for this time, it will be shut down.
            actor_standby_build (str, optional): The build tag or number to run when the Actor is in Standby mode.
            actor_standby_memory_mbytes (int, optional): The memory in megabytes to use when the Actor is in Standby mode.

        Returns:
            dict: The created Actor.
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
            default_run_timeout_secs=default_run_timeout_secs,
            example_run_input_body=example_run_input_body,
            example_run_input_content_type=example_run_input_content_type,
            actor_standby_is_enabled=actor_standby_is_enabled,
            actor_standby_desired_requests_per_actor_run=actor_standby_desired_requests_per_actor_run,
            actor_standby_max_requests_per_actor_run=actor_standby_max_requests_per_actor_run,
            actor_standby_idle_timeout_secs=actor_standby_idle_timeout_secs,
            actor_standby_build=actor_standby_build,
            actor_standby_memory_mbytes=actor_standby_memory_mbytes,
        )

        return self._create(filter_out_none_values_recursively(actor_representation))


class ActorCollectionClientAsync(ResourceCollectionClientAsync):
    """Async sub-client for manipulating Actors."""

    @ignore_docs
    def __init__(self: ActorCollectionClientAsync, *args: Any, **kwargs: Any) -> None:
        """Initialize the ActorCollectionClientAsync."""
        resource_path = kwargs.pop('resource_path', 'acts')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(
        self: ActorCollectionClientAsync,
        *,
        my: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListPage[dict]:
        """List the Actors the user has created or used.

        https://docs.apify.com/api/v2#/reference/actors/actor-collection/get-list-of-actors

        Args:
            my (bool, optional): If True, will return only Actors which the user has created themselves.
            limit (int, optional): How many Actors to list
            offset (int, optional): What Actor to include as first when retrieving the list
            desc (bool, optional): Whether to sort the Actors in descending order based on their creation date

        Returns:
            ListPage: The list of available Actors matching the specified filters.
        """
        return await self._list(my=my, limit=limit, offset=offset, desc=desc)

    async def create(
        self: ActorCollectionClientAsync,
        *,
        name: str,
        title: str | None = None,
        description: str | None = None,
        seo_title: str | None = None,
        seo_description: str | None = None,
        versions: list[dict] | None = None,  # type: ignore
        restart_on_error: bool | None = None,
        is_public: bool | None = None,
        is_deprecated: bool | None = None,
        is_anonymously_runnable: bool | None = None,
        categories: list[str] | None = None,  # type: ignore
        default_run_build: str | None = None,
        default_run_max_items: int | None = None,
        default_run_memory_mbytes: int | None = None,
        default_run_timeout_secs: int | None = None,
        example_run_input_body: Any = None,
        example_run_input_content_type: str | None = None,
        actor_standby_is_enabled: bool | None = None,
        actor_standby_desired_requests_per_actor_run: int | None = None,
        actor_standby_max_requests_per_actor_run: int | None = None,
        actor_standby_idle_timeout_secs: int | None = None,
        actor_standby_build: str | None = None,
        actor_standby_memory_mbytes: int | None = None,
    ) -> dict:
        """Create a new Actor.

        https://docs.apify.com/api/v2#/reference/actors/actor-collection/create-actor

        Args:
            name (str): The name of the Actor
            title (str, optional): The title of the Actor (human-readable)
            description (str, optional): The description for the Actor
            seo_title (str, optional): The title of the Actor optimized for search engines
            seo_description (str, optional): The description of the Actor optimized for search engines
            versions (list of dict, optional): The list of Actor versions
            restart_on_error (bool, optional): If true, the main Actor run process will be restarted whenever it exits with a non-zero status code.
            is_public (bool, optional): Whether the Actor is public.
            is_deprecated (bool, optional): Whether the Actor is deprecated.
            is_anonymously_runnable (bool, optional): Whether the Actor is anonymously runnable.
            categories (list of str, optional): The categories to which the Actor belongs to.
            default_run_build (str, optional): Tag or number of the build that you want to run by default.
            default_run_max_items (int, optional): Default limit of the number of results that will be returned by runs of this Actor,
                                                   if the Actor is charged per result.
            default_run_memory_mbytes (int, optional): Default amount of memory allocated for the runs of this Actor, in megabytes.
            default_run_timeout_secs (int, optional): Default timeout for the runs of this Actor in seconds.
            example_run_input_body (Any, optional): Input to be prefilled as default input to new users of this Actor.
            example_run_input_content_type (str, optional): The content type of the example run input.
            actor_standby_is_enabled (bool, optional): Whether the Actor Standby is enabled.
            actor_standby_desired_requests_per_actor_run (int, optional): The desired number of concurrent HTTP requests for
                a single Actor Standby run.
            actor_standby_max_requests_per_actor_run (int, optional): The maximum number of concurrent HTTP requests for a single Actor Standby run.
            actor_standby_idle_timeout_secs (int, optional): If the Actor run does not receive any requests for this time, it will be shut down.
            actor_standby_build (str, optional): The build tag or number to run when the Actor is in Standby mode.
            actor_standby_memory_mbytes (int, optional): The memory in megabytes to use when the Actor is in Standby mode.

        Returns:
            dict: The created Actor.
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
            default_run_timeout_secs=default_run_timeout_secs,
            example_run_input_body=example_run_input_body,
            example_run_input_content_type=example_run_input_content_type,
            actor_standby_is_enabled=actor_standby_is_enabled,
            actor_standby_desired_requests_per_actor_run=actor_standby_desired_requests_per_actor_run,
            actor_standby_max_requests_per_actor_run=actor_standby_max_requests_per_actor_run,
            actor_standby_idle_timeout_secs=actor_standby_idle_timeout_secs,
            actor_standby_build=actor_standby_build,
            actor_standby_memory_mbytes=actor_standby_memory_mbytes,
        )

        return await self._create(filter_out_none_values_recursively(actor_representation))

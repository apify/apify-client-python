from typing import Any, Dict, List, Optional

from ..._utils import ListPage, _filter_out_none_values_recursively
from ..base import ResourceCollectionClient
from .actor import _get_actor_representation


class ActorCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating actors."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the ActorCollectionClient."""
        resource_path = kwargs.pop('resource_path', 'acts')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self,
        *,
        my: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        desc: Optional[bool] = None,
    ) -> ListPage:
        """List the actors the user has created or used.

        https://docs.apify.com/api/v2#/reference/actors/actor-collection/get-list-of-actors

        Args:
            my (bool, optional): If True, will return only actors which the user has created themselves.
            limit (int, optional): How many actors to list
            offset (int, optional): What actor to include as first when retrieving the list
            desc (bool, optional): Whether to sort the actors in descending order based on their creation date

        Returns:
            ListPage: The list of available actors matching the specified filters.
        """
        return self._list(my=my, limit=limit, offset=offset, desc=desc)

    def create(
        self,
        *,
        name: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        seo_title: Optional[str] = None,
        seo_description: Optional[str] = None,
        versions: Optional[List[Dict]] = None,
        restart_on_error: Optional[bool] = None,
        is_public: Optional[bool] = None,
        is_deprecated: Optional[bool] = None,
        is_anonymously_runnable: Optional[bool] = None,
        categories: Optional[List[str]] = None,
        default_run_build: Optional[str] = None,
        default_run_memory_mbytes: Optional[int] = None,
        default_run_timeout_secs: Optional[int] = None,
        example_run_input_body: Optional[Any] = None,
        example_run_input_content_type: Optional[str] = None,
    ) -> Dict:
        """Create a new actor.

        https://docs.apify.com/api/v2#/reference/actors/actor-collection/create-actor

        Args:
            name (str): The name of the actor
            title (str, optional): The title of the actor (human-readable)
            description (str, optional): The description for the actor
            seo_title (str, optional): The title of the actor optimized for search engines
            seo_description (str, optional): The description of the actor optimized for search engines
            versions (list of dict, optional): The list of actor versions
            restart_on_error (bool, optional): If true, the main actor run process will be restarted whenever it exits with a non-zero status code.
            is_public (bool, optional): Whether the actor is public.
            is_deprecated (bool, optional): Whether the actor is deprecated.
            is_anonymously_runnable (bool, optional): Whether the actor is anonymously runnable.
            categories (list of str, optional): The categories to which the actor belongs to.
            default_run_build (str, optional): Tag or number of the build that you want to run by default.
            default_run_memory_mbytes (int, optional): Default amount of memory allocated for the runs of this actor, in megabytes.
            default_run_timeout_secs (int, optional): Default timeout for the runs of this actor in seconds.
            example_run_input_body (Any, optional): Input to be prefilled as default input to new users of this actor.
            example_run_input_content_type (str, optional): The content type of the example run input.

        Returns:
            dict: The created actor.
        """
        actor_representation = _get_actor_representation(
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
            default_run_memory_mbytes=default_run_memory_mbytes,
            default_run_timeout_secs=default_run_timeout_secs,
            example_run_input_body=example_run_input_body,
            example_run_input_content_type=example_run_input_content_type,
        )

        return self._create(_filter_out_none_values_recursively(actor_representation))

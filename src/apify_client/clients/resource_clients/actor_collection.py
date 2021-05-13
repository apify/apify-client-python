from typing import Any, Dict, List, Optional

from ..._utils import ListPage
from ..base import ResourceCollectionClient


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
        actor_fields: Dict[str, Any] = {}
        if name is not None:
            actor_fields['name'] = name
        if title is not None:
            actor_fields['title'] = title
        if description is not None:
            actor_fields['description'] = description
        if seo_title is not None:
            actor_fields['seoTitle'] = seo_title
        if seo_description is not None:
            actor_fields['seoDescription'] = seo_description
        if versions is not None:
            actor_fields['versions'] = versions
        if restart_on_error is not None:
            actor_fields['restartOnError'] = restart_on_error
        if is_public is not None:
            actor_fields['isPublic'] = is_public
        if is_deprecated is not None:
            actor_fields['isDeprecated'] = is_deprecated
        if is_anonymously_runnable is not None:
            actor_fields['isAnonymouslyRunnable'] = is_anonymously_runnable
        if categories is not None:
            actor_fields['categories'] = categories

        default_run_options: Dict[str, Any] = {}
        if default_run_build is not None:
            default_run_options['build'] = default_run_build
        if default_run_memory_mbytes is not None:
            default_run_options['memoryMbytes'] = default_run_memory_mbytes
        if default_run_timeout_secs is not None:
            default_run_options['timeoutSecs'] = default_run_timeout_secs
        if default_run_options:
            actor_fields['defaultRunOptions'] = default_run_options

        example_run_input: Dict[str, Any] = {}
        if example_run_input_body is not None:
            example_run_input['body'] = example_run_input_body
        if example_run_input_content_type is not None:
            example_run_input['contentType'] = example_run_input_content_type
        if example_run_input:
            actor_fields['exampleRunInput'] = example_run_input

        return self._create(actor_fields)

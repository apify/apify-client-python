from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_shared.utils import filter_out_none_values_recursively, ignore_docs

from apify_client.clients.base import ResourceCollectionClient, ResourceCollectionClientAsync
from apify_client.clients.resource_clients.task import get_task_representation

if TYPE_CHECKING:
    from apify_shared.models import ListPage


class TaskCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating tasks."""

    @ignore_docs
    def __init__(self: TaskCollectionClient, *args: Any, **kwargs: Any) -> None:
        """Initialize the TaskCollectionClient."""
        resource_path = kwargs.pop('resource_path', 'actor-tasks')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self: TaskCollectionClient,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListPage[dict]:
        """List the available tasks.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-collection/get-list-of-tasks

        Args:
            limit (int, optional): How many tasks to list
            offset (int, optional): What task to include as first when retrieving the list
            desc (bool, optional): Whether to sort the tasks in descending order based on their creation date

        Returns:
            ListPage: The list of available tasks matching the specified filters.
        """
        return self._list(limit=limit, offset=offset, desc=desc)

    def create(
        self: TaskCollectionClient,
        *,
        actor_id: str,
        name: str,
        build: str | None = None,
        timeout_secs: int | None = None,
        memory_mbytes: int | None = None,
        max_items: int | None = None,
        task_input: dict | None = None,
        title: str | None = None,
        actor_standby_desired_requests_per_actor_run: int | None = None,
        actor_standby_max_requests_per_actor_run: int | None = None,
        actor_standby_idle_timeout_secs: int | None = None,
        actor_standby_build: str | None = None,
        actor_standby_memory_mbytes: int | None = None,
    ) -> dict:
        """Create a new task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-collection/create-task

        Args:
            actor_id (str): Id of the Actor that should be run
            name (str): Name of the task
            build (str, optional): Actor build to run. It can be either a build tag or build number.
                                   By default, the run uses the build specified in the task settings (typically latest).
            memory_mbytes (int, optional): Memory limit for the run, in megabytes.
                                           By default, the run uses a memory limit specified in the task settings.
            max_items (int, optional): Maximum number of results that will be returned by runs of this task.
                                       If the Actor of this task is charged per result, you will not be charged for more results than the given limit.
            timeout_secs (int, optional): Optional timeout for the run, in seconds. By default, the run uses timeout specified in the task settings.
            task_input (dict, optional): Task input object.
            title (str, optional): A human-friendly equivalent of the name
            actor_standby_desired_requests_per_actor_run (int, optional): The desired number of concurrent HTTP requests for
                a single Actor Standby run.
            actor_standby_max_requests_per_actor_run (int, optional): The maximum number of concurrent HTTP requests for a single Actor Standby run.
            actor_standby_idle_timeout_secs (int, optional): If the Actor run does not receive any requests for this time, it will be shut down.
            actor_standby_build (str, optional): The build tag or number to run when the Actor is in Standby mode.
            actor_standby_memory_mbytes (int, optional): The memory in megabytes to use when the Actor is in Standby mode.

        Returns:
            dict: The created task.
        """
        task_representation = get_task_representation(
            actor_id=actor_id,
            name=name,
            task_input=task_input,
            build=build,
            max_items=max_items,
            memory_mbytes=memory_mbytes,
            timeout_secs=timeout_secs,
            title=title,
            actor_standby_desired_requests_per_actor_run=actor_standby_desired_requests_per_actor_run,
            actor_standby_max_requests_per_actor_run=actor_standby_max_requests_per_actor_run,
            actor_standby_idle_timeout_secs=actor_standby_idle_timeout_secs,
            actor_standby_build=actor_standby_build,
            actor_standby_memory_mbytes=actor_standby_memory_mbytes,
        )

        return self._create(filter_out_none_values_recursively(task_representation))


class TaskCollectionClientAsync(ResourceCollectionClientAsync):
    """Async sub-client for manipulating tasks."""

    @ignore_docs
    def __init__(self: TaskCollectionClientAsync, *args: Any, **kwargs: Any) -> None:
        """Initialize the TaskCollectionClientAsync."""
        resource_path = kwargs.pop('resource_path', 'actor-tasks')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(
        self: TaskCollectionClientAsync,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListPage[dict]:
        """List the available tasks.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-collection/get-list-of-tasks

        Args:
            limit (int, optional): How many tasks to list
            offset (int, optional): What task to include as first when retrieving the list
            desc (bool, optional): Whether to sort the tasks in descending order based on their creation date

        Returns:
            ListPage: The list of available tasks matching the specified filters.
        """
        return await self._list(limit=limit, offset=offset, desc=desc)

    async def create(
        self: TaskCollectionClientAsync,
        *,
        actor_id: str,
        name: str,
        build: str | None = None,
        timeout_secs: int | None = None,
        memory_mbytes: int | None = None,
        max_items: int | None = None,
        task_input: dict | None = None,
        title: str | None = None,
        actor_standby_desired_requests_per_actor_run: int | None = None,
        actor_standby_max_requests_per_actor_run: int | None = None,
        actor_standby_idle_timeout_secs: int | None = None,
        actor_standby_build: str | None = None,
        actor_standby_memory_mbytes: int | None = None,
    ) -> dict:
        """Create a new task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-collection/create-task

        Args:
            actor_id (str): Id of the Actor that should be run
            name (str): Name of the task
            build (str, optional): Actor build to run. It can be either a build tag or build number.
                                   By default, the run uses the build specified in the task settings (typically latest).
            memory_mbytes (int, optional): Memory limit for the run, in megabytes.
                                           By default, the run uses a memory limit specified in the task settings.
            max_items (int, optional): Maximum number of results that will be returned by runs of this task.
                                       If the Actor of this task is charged per result, you will not be charged for more results than the given limit.
            timeout_secs (int, optional): Optional timeout for the run, in seconds. By default, the run uses timeout specified in the task settings.
            task_input (dict, optional): Task input object.
            title (str, optional): A human-friendly equivalent of the name
            actor_standby_desired_requests_per_actor_run (int, optional): The desired number of concurrent HTTP requests for
                a single Actor Standby run.
            actor_standby_max_requests_per_actor_run (int, optional): The maximum number of concurrent HTTP requests for a single Actor Standby run.
            actor_standby_idle_timeout_secs (int, optional): If the Actor run does not receive any requests for this time, it will be shut down.
            actor_standby_build (str, optional): The build tag or number to run when the Actor is in Standby mode.
            actor_standby_memory_mbytes (int, optional): The memory in megabytes to use when the Actor is in Standby mode.

        Returns:
            dict: The created task.
        """
        task_representation = get_task_representation(
            actor_id=actor_id,
            name=name,
            task_input=task_input,
            build=build,
            max_items=max_items,
            memory_mbytes=memory_mbytes,
            timeout_secs=timeout_secs,
            title=title,
            actor_standby_desired_requests_per_actor_run=actor_standby_desired_requests_per_actor_run,
            actor_standby_max_requests_per_actor_run=actor_standby_max_requests_per_actor_run,
            actor_standby_idle_timeout_secs=actor_standby_idle_timeout_secs,
            actor_standby_build=actor_standby_build,
            actor_standby_memory_mbytes=actor_standby_memory_mbytes,
        )

        return await self._create(filter_out_none_values_recursively(task_representation))

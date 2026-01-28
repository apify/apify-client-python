from __future__ import annotations

from typing import Any

from apify_client._models import CreateTaskResponse, GetListOfTasksResponse, ListOfTasks, Task
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._resource_clients.task import get_task_representation
from apify_client._utils import filter_none_values, response_to_dict


class TaskCollectionClient(ResourceClient):
    """Sub-client for manipulating tasks."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'actor-tasks')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListOfTasks:
        """List the available tasks.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-collection/get-list-of-tasks

        Args:
            limit: How many tasks to list.
            offset: What task to include as first when retrieving the list.
            desc: Whether to sort the tasks in descending order based on their creation date.

        Returns:
            The list of available tasks matching the specified filters.
        """
        response = self._http_client.call(
            url=self._build_url(),
            method='GET',
            params=self._build_params(limit=limit, offset=offset, desc=desc),
        )
        response_as_dict = response_to_dict(response)
        return GetListOfTasksResponse.model_validate(response_as_dict).data

    def create(
        self,
        *,
        actor_id: str,
        name: str,
        build: str | None = None,
        timeout_secs: int | None = None,
        memory_mbytes: int | None = None,
        max_items: int | None = None,
        restart_on_error: bool | None = None,
        task_input: dict | None = None,
        title: str | None = None,
        actor_standby_desired_requests_per_actor_run: int | None = None,
        actor_standby_max_requests_per_actor_run: int | None = None,
        actor_standby_idle_timeout_secs: int | None = None,
        actor_standby_build: str | None = None,
        actor_standby_memory_mbytes: int | None = None,
    ) -> Task:
        """Create a new task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-collection/create-task

        Args:
            actor_id: Id of the Actor that should be run.
            name: Name of the task.
            build: Actor build to run. It can be either a build tag or build number. By default, the run uses
                the build specified in the task settings (typically latest).
            memory_mbytes: Memory limit for the run, in megabytes. By default, the run uses a memory limit specified
                in the task settings.
            max_items: Maximum number of results that will be returned by runs of this task. If the Actor of this task
                is charged per result, you will not be charged for more results than the given limit.
            timeout_secs: Optional timeout for the run, in seconds. By default, the run uses timeout specified
                in the task settings.
            restart_on_error: If true, the Task run process will be restarted whenever it exits with
                a non-zero status code.
            task_input: Task input object.
            title: A human-friendly equivalent of the name.
            actor_standby_desired_requests_per_actor_run: The desired number of concurrent HTTP requests for
                a single Actor Standby run.
            actor_standby_max_requests_per_actor_run: The maximum number of concurrent HTTP requests for
                a single Actor Standby run.
            actor_standby_idle_timeout_secs: If the Actor run does not receive any requests for this time,
                it will be shut down.
            actor_standby_build: The build tag or number to run when the Actor is in Standby mode.
            actor_standby_memory_mbytes: The memory in megabytes to use when the Actor is in Standby mode.

        Returns:
            The created task.
        """
        task_representation = get_task_representation(
            actor_id=actor_id,
            name=name,
            task_input=task_input,
            build=build,
            max_items=max_items,
            memory_mbytes=memory_mbytes,
            timeout_secs=timeout_secs,
            restart_on_error=restart_on_error,
            title=title,
            actor_standby_desired_requests_per_actor_run=actor_standby_desired_requests_per_actor_run,
            actor_standby_max_requests_per_actor_run=actor_standby_max_requests_per_actor_run,
            actor_standby_idle_timeout_secs=actor_standby_idle_timeout_secs,
            actor_standby_build=actor_standby_build,
            actor_standby_memory_mbytes=actor_standby_memory_mbytes,
        )

        response = self._http_client.call(
            url=self._build_url(),
            method='POST',
            params=self._build_params(),
            json=filter_none_values(task_representation),
        )

        result = response_to_dict(response)
        return CreateTaskResponse.model_validate(result).data


class TaskCollectionClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating tasks."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'actor-tasks')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListOfTasks:
        """List the available tasks.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-collection/get-list-of-tasks

        Args:
            limit: How many tasks to list.
            offset: What task to include as first when retrieving the list.
            desc: Whether to sort the tasks in descending order based on their creation date.

        Returns:
            The list of available tasks matching the specified filters.
        """
        response = await self._http_client.call(
            url=self._build_url(),
            method='GET',
            params=self._build_params(limit=limit, offset=offset, desc=desc),
        )
        response_as_dict = response_to_dict(response)
        return GetListOfTasksResponse.model_validate(response_as_dict).data

    async def create(
        self,
        *,
        actor_id: str,
        name: str,
        build: str | None = None,
        timeout_secs: int | None = None,
        memory_mbytes: int | None = None,
        max_items: int | None = None,
        restart_on_error: bool | None = None,
        task_input: dict | None = None,
        title: str | None = None,
        actor_standby_desired_requests_per_actor_run: int | None = None,
        actor_standby_max_requests_per_actor_run: int | None = None,
        actor_standby_idle_timeout_secs: int | None = None,
        actor_standby_build: str | None = None,
        actor_standby_memory_mbytes: int | None = None,
    ) -> Task:
        """Create a new task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-collection/create-task

        Args:
            actor_id: Id of the Actor that should be run.
            name: Name of the task.
            build: Actor build to run. It can be either a build tag or build number. By default, the run uses
                the build specified in the task settings (typically latest).
            memory_mbytes: Memory limit for the run, in megabytes. By default, the run uses a memory limit specified
                in the task settings.
            max_items: Maximum number of results that will be returned by runs of this task. If the Actor of this task
                is charged per result, you will not be charged for more results than the given limit.
            timeout_secs: Optional timeout for the run, in seconds. By default, the run uses timeout specified
                in the task settings.
            restart_on_error: If true, the Task run process will be restarted whenever it exits with
                a non-zero status code.
            task_input: Task input object.
            title: A human-friendly equivalent of the name.
            actor_standby_desired_requests_per_actor_run: The desired number of concurrent HTTP requests for
                a single Actor Standby run.
            actor_standby_max_requests_per_actor_run: The maximum number of concurrent HTTP requests for
                a single Actor Standby run.
            actor_standby_idle_timeout_secs: If the Actor run does not receive any requests for this time,
                it will be shut down.
            actor_standby_build: The build tag or number to run when the Actor is in Standby mode.
            actor_standby_memory_mbytes: The memory in megabytes to use when the Actor is in Standby mode.

        Returns:
            The created task.
        """
        task_representation = get_task_representation(
            actor_id=actor_id,
            name=name,
            task_input=task_input,
            build=build,
            max_items=max_items,
            memory_mbytes=memory_mbytes,
            timeout_secs=timeout_secs,
            restart_on_error=restart_on_error,
            title=title,
            actor_standby_desired_requests_per_actor_run=actor_standby_desired_requests_per_actor_run,
            actor_standby_max_requests_per_actor_run=actor_standby_max_requests_per_actor_run,
            actor_standby_idle_timeout_secs=actor_standby_idle_timeout_secs,
            actor_standby_build=actor_standby_build,
            actor_standby_memory_mbytes=actor_standby_memory_mbytes,
        )

        response = await self._http_client.call(
            url=self._build_url(),
            method='POST',
            params=self._build_params(),
            json=filter_none_values(task_representation),
        )

        result = response_to_dict(response)
        return CreateTaskResponse.model_validate(result).data

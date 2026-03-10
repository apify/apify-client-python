from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._models import (
    ActorStandby,
    CreateTaskRequest,
    ListOfTasks,
    ListOfTasksResponse,
    Task,
    TaskInput,
    TaskOptions,
    TaskResponse,
)
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import to_seconds

if TYPE_CHECKING:
    from datetime import timedelta

    from apify_client._types import Timeout


@docs_group('Resource clients')
class TaskCollectionClient(ResourceClient):
    """Sub-client for the task collection.

    Provides methods to manage the task collection, e.g. list or create tasks. Obtain an instance via an appropriate
    method on the `ApifyClient` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'actor-tasks',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_path=resource_path,
            **kwargs,
        )

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        timeout: Timeout = 'medium',
    ) -> ListOfTasks:
        """List the available tasks.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-collection/get-list-of-tasks

        Args:
            limit: How many tasks to list.
            offset: What task to include as first when retrieving the list.
            desc: Whether to sort the tasks in descending order based on their creation date.
            timeout: Timeout for the API HTTP request.

        Returns:
            The list of available tasks matching the specified filters.
        """
        result = self._list(timeout=timeout, limit=limit, offset=offset, desc=desc)
        return ListOfTasksResponse.model_validate(result).data

    def create(
        self,
        *,
        actor_id: str,
        name: str,
        build: str | None = None,
        run_timeout: timedelta | None = None,
        memory_mbytes: int | None = None,
        max_items: int | None = None,
        restart_on_error: bool | None = None,
        task_input: dict | None = None,
        title: str | None = None,
        actor_standby_desired_requests_per_actor_run: int | None = None,
        actor_standby_max_requests_per_actor_run: int | None = None,
        actor_standby_idle_timeout: timedelta | None = None,
        actor_standby_build: str | None = None,
        actor_standby_memory_mbytes: int | None = None,
        timeout: Timeout = 'medium',
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
            run_timeout: Optional timeout for the run. By default, the run uses timeout specified
                in the task settings.
            restart_on_error: If true, the Task run process will be restarted whenever it exits with
                a non-zero status code.
            task_input: Task input object.
            title: A human-friendly equivalent of the name.
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
            The created task.
        """
        task_fields = CreateTaskRequest(
            act_id=actor_id,
            name=name,
            title=title,
            input=TaskInput.model_validate(task_input) if task_input else None,
            options=TaskOptions(
                build=build,
                max_items=max_items,
                memory_mbytes=memory_mbytes,
                timeout_secs=to_seconds(run_timeout, as_int=True),
                restart_on_error=restart_on_error,
            ),
            actor_standby=ActorStandby(
                desired_requests_per_actor_run=actor_standby_desired_requests_per_actor_run,
                max_requests_per_actor_run=actor_standby_max_requests_per_actor_run,
                idle_timeout_secs=to_seconds(actor_standby_idle_timeout, as_int=True),
                build=actor_standby_build,
                memory_mbytes=actor_standby_memory_mbytes,
            ),
        )
        result = self._create(timeout=timeout, **task_fields.model_dump(by_alias=True, exclude_none=True))
        return TaskResponse.model_validate(result).data


@docs_group('Resource clients')
class TaskCollectionClientAsync(ResourceClientAsync):
    """Sub-client for the task collection.

    Provides methods to manage the task collection, e.g. list or create tasks. Obtain an instance via an appropriate
    method on the `ApifyClientAsync` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'actor-tasks',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_path=resource_path,
            **kwargs,
        )

    async def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        timeout: Timeout = 'medium',
    ) -> ListOfTasks:
        """List the available tasks.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-collection/get-list-of-tasks

        Args:
            limit: How many tasks to list.
            offset: What task to include as first when retrieving the list.
            desc: Whether to sort the tasks in descending order based on their creation date.
            timeout: Timeout for the API HTTP request.

        Returns:
            The list of available tasks matching the specified filters.
        """
        result = await self._list(timeout=timeout, limit=limit, offset=offset, desc=desc)
        return ListOfTasksResponse.model_validate(result).data

    async def create(
        self,
        *,
        actor_id: str,
        name: str,
        build: str | None = None,
        run_timeout: timedelta | None = None,
        memory_mbytes: int | None = None,
        max_items: int | None = None,
        restart_on_error: bool | None = None,
        task_input: dict | None = None,
        title: str | None = None,
        actor_standby_desired_requests_per_actor_run: int | None = None,
        actor_standby_max_requests_per_actor_run: int | None = None,
        actor_standby_idle_timeout: timedelta | None = None,
        actor_standby_build: str | None = None,
        actor_standby_memory_mbytes: int | None = None,
        timeout: Timeout = 'medium',
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
            run_timeout: Optional timeout for the run. By default, the run uses timeout specified
                in the task settings.
            restart_on_error: If true, the Task run process will be restarted whenever it exits with
                a non-zero status code.
            task_input: Task input object.
            title: A human-friendly equivalent of the name.
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
            The created task.
        """
        task_fields = CreateTaskRequest(
            act_id=actor_id,
            name=name,
            title=title,
            input=TaskInput.model_validate(task_input) if task_input else None,
            options=TaskOptions(
                build=build,
                max_items=max_items,
                memory_mbytes=memory_mbytes,
                timeout_secs=to_seconds(run_timeout, as_int=True),
                restart_on_error=restart_on_error,
            ),
            actor_standby=ActorStandby(
                desired_requests_per_actor_run=actor_standby_desired_requests_per_actor_run,
                max_requests_per_actor_run=actor_standby_max_requests_per_actor_run,
                idle_timeout_secs=to_seconds(actor_standby_idle_timeout, as_int=True),
                build=actor_standby_build,
                memory_mbytes=actor_standby_memory_mbytes,
            ),
        )
        result = await self._create(timeout=timeout, **task_fields.model_dump(by_alias=True, exclude_none=True))
        return TaskResponse.model_validate(result).data

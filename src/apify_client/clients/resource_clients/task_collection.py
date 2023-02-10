from typing import Any, Dict, Optional

from ..._utils import ListPage, _filter_out_none_values_recursively, ignore_docs
from ..base import ResourceCollectionClient, ResourceCollectionClientAsync
from .task import _get_task_representation


class TaskCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating tasks."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the TaskCollectionClient."""
        resource_path = kwargs.pop('resource_path', 'actor-tasks')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        desc: Optional[bool] = None,
    ) -> ListPage[Dict]:
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
        self,
        *,
        actor_id: str,
        name: str,
        build: Optional[str] = None,
        timeout_secs: Optional[int] = None,
        memory_mbytes: Optional[int] = None,
        task_input: Optional[Dict] = None,
        title: Optional[str] = None,
    ) -> Dict:
        """Create a new task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-collection/create-task

        Args:
            actor_id (str): Id of the actor that should be run
            name (str): Name of the task
            build (str, optional): Actor build to run. It can be either a build tag or build number.
                                   By default, the run uses the build specified in the task settings (typically latest).
            memory_mbytes (int, optional): Memory limit for the run, in megabytes.
                                           By default, the run uses a memory limit specified in the task settings.
            timeout_secs (int, optional): Optional timeout for the run, in seconds. By default, the run uses timeout specified in the task settings.
            task_input (dict, optional): Task input object.
            title (str, optional): A human-friendly equivalent of the name

        Returns:
            dict: The created task.
        """
        task_representation = _get_task_representation(
            actor_id=actor_id,
            name=name,
            task_input=task_input,
            build=build,
            memory_mbytes=memory_mbytes,
            timeout_secs=timeout_secs,
            title=title,
        )

        return self._create(_filter_out_none_values_recursively(task_representation))


class TaskCollectionClientAsync(ResourceCollectionClientAsync):
    """Async sub-client for manipulating tasks."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the TaskCollectionClientAsync."""
        resource_path = kwargs.pop('resource_path', 'actor-tasks')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        desc: Optional[bool] = None,
    ) -> ListPage[Dict]:
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
        self,
        *,
        actor_id: str,
        name: str,
        build: Optional[str] = None,
        timeout_secs: Optional[int] = None,
        memory_mbytes: Optional[int] = None,
        task_input: Optional[Dict] = None,
        title: Optional[str] = None,
    ) -> Dict:
        """Create a new task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-collection/create-task

        Args:
            actor_id (str): Id of the actor that should be run
            name (str): Name of the task
            build (str, optional): Actor build to run. It can be either a build tag or build number.
                                   By default, the run uses the build specified in the task settings (typically latest).
            memory_mbytes (int, optional): Memory limit for the run, in megabytes.
                                           By default, the run uses a memory limit specified in the task settings.
            timeout_secs (int, optional): Optional timeout for the run, in seconds. By default, the run uses timeout specified in the task settings.
            task_input (dict, optional): Task input object.
            title (str, optional): A human-friendly equivalent of the name

        Returns:
            dict: The created task.
        """
        task_representation = _get_task_representation(
            actor_id=actor_id,
            name=name,
            task_input=task_input,
            build=build,
            memory_mbytes=memory_mbytes,
            timeout_secs=timeout_secs,
            title=title,
        )

        return await self._create(_filter_out_none_values_recursively(task_representation))

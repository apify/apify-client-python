from typing import Any, Dict, Optional

from ..base.resource_collection_client import ResourceCollectionClient


class TaskCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating tasks."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the TaskCollectionClient with the passed arguments."""
        super().__init__(*args, resource_path='actor-tasks', **kwargs)

    def list(self, *, limit: Optional[int] = None, offset: Optional[int] = None, desc: Optional[bool] = None) -> Dict:
        """List the available tasks.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-collection/get-list-of-tasks

        Args:
            limit: How many tasks to retrieve
            offset: What tasks to include as first when retrieving the list
            desc: Whether to sort the tasks in descending order based on their modification date

        Returns:
            The list of available tasks matching the specified filters.
        """
        return self._list(limit=limit, offset=offset, desc=desc)

    def create(
        self,
        *,
        actor_id: str,
        name: str,
        task_options: Optional[Dict] = {},
        task_input: Optional[Dict] = {},
    ) -> Dict:
        """Create a new task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-collection/create-task

        Args:
            actor_id (string): Id of the actor that should be run
            name (string): Name of the task
            task_options (dict, optional): Task options, can contain the following keys: build, timeoutSecs and memoryMbytes keys
            task_input (dict, optional): Task input object.

        Returns:
            The created task.
        """
        return self._create({
            "actId": actor_id,
            "name": name,
            "options": task_options,
            "input": task_input,
        })

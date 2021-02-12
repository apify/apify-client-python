import io
from typing import Any, Dict, Generator, List, Optional, cast


from ..._types import JSONSerializable
from ..._utils import _catch_not_found_or_throw, _pluck_data_as_list, _snake_case_to_camel_case
from ..base.resource_client import ResourceClient


class TaskClient(ResourceClient):
    """Sub-client for manipulating a single task."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the TaskClient."""
        super().__init__(*args, resource_path='actor-tasks', **kwargs)

    def get(self) -> Optional[Dict]:
        """Retrieve the task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/get-task

        Returns:
            The retrieved task
        """
        return self._get()

    def update(
        self,
        *,
        name: Optional[str] = None,
        task_options: Optional[Dict] = None,
        task_input: Optional[Dict] = None,
    ) -> Dict:
        """Update the task with specified fields.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/update-task

        Args:
            name (string): Name of the task
            task_options (dict, optional): Task options, can contain the following keys: build, timeoutSecs and memoryMbytes keys
            task_input (dict, optional): Task input object.

        Returns:
            The updated task
        """
        updated_kwargs = {
            _snake_case_to_camel_case(key): value
            for key, value in locals().items() if key != 'self' and value is not None
        }
        return self._update(updated_kwargs)

    def delete(self) -> None:
        """Delete the task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/delete-task
        """
        return self._delete()

    def start(
        self,
        *,
        task_input: Optional[Dict] = None,
        build: Optional[str] = None,
        memory: Optional[int] = None,
        timeout: Optional[int] = None,
        wait_for_finish: Optional[bool] = None,
        webhooks: Optional[List[Dict]] = None,
    ) -> Dict:
        """Start a task and immediately returns the Run object.

        https://docs.apify.com/api/v2#/reference/actor-tasks/run-collection/run-task

        Args:
            task_input (dict, optional): Input for the task
            build (str, optional): Specifies the actor build to run. It can be either a build tag or build number.
                                   By default, the run uses the build specified in the task settings (typically latest).
            memory (int, optional): Memory limit for the run, in megabytes. By default, the run uses a memory limit specified in the task settings.
            timeout: (int, optional): Optional timeout for the run, in seconds. By default, the run uses a timeout specified in the task settings.
            wait_for_finish: (bool, optional): If set, the client will not return until the run finishes.
            webhooks (list, optional): Specifies optional webhooks associated with the actor run, which can be used to receive a notification
                                       e.g. when the actor finished or failed.


        Returns:
            The run object

        """
        pass


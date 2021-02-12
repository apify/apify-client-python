from typing import Any, Dict, List, Optional

from ..._utils import _encode_json_to_base64, _filter_out_none_values_recursively, _parse_date_fields, _pluck_data
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
        task_input: Optional[Dict] = None,
        build: Optional[str] = None,
        memory_mb: Optional[int] = None,
        timeout_secs: Optional[int] = None,
    ) -> Dict:
        """Update the task with specified fields.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/update-task

        Args:
            name (string, optional): Name of the task
            build (str, optional): Specifies the actor build to run. It can be either a build tag or build number.
                                   By default, the run uses the build specified in the task settings (typically latest).
            memory_mb (int, optional): Memory limit for the run, in megabytes. By default, the run uses a memory limit specified in the task settings.
            timeout_secs: (int, optional): Optional timeout for the run, in seconds. By default, the run uses timeout specified in the task settings.
            task_input (dict, optional): Task input dictionary

        Returns:
            The updated task
        """
        new_fields = {
            "name": name,
            "options": {
                "build": build,
                "memoryMbytes": memory_mb,
                "timeoutSecs": timeout_secs,
            },
            "input": task_input,
        }

        return self._update(_filter_out_none_values_recursively(new_fields))

    def delete(self) -> None:
        """Delete the task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/delete-task
        """
        return self._delete()

    def start(
        self,
        *,
        task_input: Optional[Dict[str, Any]] = None,
        build: Optional[str] = None,
        memory_mb: Optional[int] = None,
        timeout_secs: Optional[int] = None,
        wait_for_finish: Optional[int] = None,
        webhooks: Optional[List[Dict]] = None,
    ) -> Dict:
        """Start a task and immediately return the Run object.

        https://docs.apify.com/api/v2#/reference/actor-tasks/run-collection/run-task

        Args:
            task_input (dict, optional): Task input dictionary
            build (str, optional): Specifies the actor build to run. It can be either a build tag or build number.
                                   By default, the run uses the build specified in the task settings (typically latest).
            memory_mb (int, optional): Memory limit for the run, in megabytes. By default, the run uses a memory limit specified in the task settings.
            timeout_secs: (int, optional): Optional timeout for the run, in seconds. By default, the run uses timeout specified in the task settings.
            wait_for_finish: (bool, optional): The maximum number of seconds the server waits for the run to finish.
                                               By default, it is 0, the maximum value is 300.
            webhooks (list, optional): Specifies optional webhooks associated with the actor run, which can be used to receive a notification
                                       e.g. when the actor finished or failed. Note: if you already have a webhook set up for the actor or task,
                                       you do not have to add it again here.

        Returns:
            The run object
        """
        request_params = self._params(
            build=build,
            memory=memory_mb,
            timeout=timeout_secs,
            waitForFinish=wait_for_finish,
            webhooks=_encode_json_to_base64(webhooks) if webhooks is not None else [],
        )

        response = self.http_client.call(
            url=self._url('runs'),
            method='POST',
            headers={'content-type': 'application/json; charset=utf-8'},
            json=task_input,
            params=request_params,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    def call(
        self,
        *,
        task_input: Optional[Dict[str, Any]] = None,
        build: Optional[str] = None,
        memory_mb: Optional[int] = None,
        timeout_secs: Optional[int] = None,
        wait_for_finish: Optional[int] = None,
        webhooks: Optional[List[Dict]] = None,
    ) -> Dict:
        """Start a task and wait for it to finish before returning the Run object.

        It waits indefinitely, unless the wait_secs argument is provided.

        https://docs.apify.com/api/v2#/reference/actor-tasks/run-collection/run-task

        Args:
            task_input (dict, optional): Task input dictionary
            build (str, optional): Specifies the actor build to run. It can be either a build tag or build number.
                                   By default, the run uses the build specified in the task settings (typically latest).
            memory_mb (int, optional): Memory limit for the run, in megabytes. By default, the run uses a memory limit specified in the task settings.
            timeout_secs: (int, optional): Optional timeout for the run, in seconds. By default, the run uses timeout specified in the task settings.
            wait_for_finish: (bool, optional): The maximum number of seconds the server waits for the run to finish.
                                               By default, it is 0, the maximum value is 300.
            webhooks (list, optional): Specifies optional webhooks associated with the actor run, which can be used to receive a notification
                                       e.g. when the actor finished or failed. Note: if you already have a webhook set up for the actor or task,
                                       you do not have to add it again here.

        Returns:
            The run object
        """

        raise ValueError('Method not yet finished. Blocked by Run subclient')

        # run = self.start(
        #     task_input=task_input,
        #     build=build,
        #     memory_mb=memory_mb,
        #     timeout_secs=timeout_secs,
        #     wait_for_finish=wait_for_finish,
        #     webhooks=webhooks,
        # )

        # TODO - retrieve the run using Run client and wait on it


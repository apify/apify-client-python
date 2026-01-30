from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from apify_client._models import CreateTaskResponse, GetRunResponse, Run, RunOrigin, Task
from apify_client._representations import get_task_representation
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import (
    catch_not_found_or_throw,
    encode_webhook_list_to_base64,
    enum_to_value,
    filter_none_values,
    response_to_dict,
)
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from datetime import timedelta

    from apify_client._consts import ActorJobStatus
    from apify_client._resource_clients import (
        RunClient,
        RunClientAsync,
        RunCollectionClient,
        RunCollectionClientAsync,
        WebhookCollectionClient,
        WebhookCollectionClientAsync,
    )


class TaskClient(ResourceClient):
    """Sub-client for manipulating a single task."""

    def __init__(
        self,
        *,
        resource_id: str,
        resource_path: str = 'actor-tasks',
        **kwargs: Any,
    ) -> None:
        super().__init__(resource_id=resource_id, resource_path=resource_path, **kwargs)

    def get(self) -> Task | None:
        """Retrieve the task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/get-task

        Returns:
            The retrieved task.
        """
        try:
            response = self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(),
            )
            result = response_to_dict(response)
            return CreateTaskResponse.model_validate(result).data
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            return None

    def update(
        self,
        *,
        name: str | None = None,
        task_input: dict | None = None,
        build: str | None = None,
        max_items: int | None = None,
        memory_mbytes: int | None = None,
        timeout: timedelta | None = None,
        restart_on_error: bool | None = None,
        title: str | None = None,
        actor_standby_desired_requests_per_actor_run: int | None = None,
        actor_standby_max_requests_per_actor_run: int | None = None,
        actor_standby_idle_timeout: timedelta | None = None,
        actor_standby_build: str | None = None,
        actor_standby_memory_mbytes: int | None = None,
    ) -> Task:
        """Update the task with specified fields.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/update-task

        Args:
            name: Name of the task.
            build: Actor build to run. It can be either a build tag or build number. By default, the run uses
                the build specified in the task settings (typically latest).
            max_items: Maximum number of results that will be returned by this run. If the Actor is charged per result,
                you will not be charged for more results than the given limit.
            memory_mbytes: Memory limit for the run, in megabytes. By default, the run uses a memory limit specified
                in the task settings.
            timeout: Optional timeout for the run. By default, the run uses timeout specified
                in the task settings.
            restart_on_error: If true, the Task run process will be restarted whenever it exits with
                a non-zero status code.
            task_input: Task input dictionary.
            title: A human-friendly equivalent of the name.
            actor_standby_desired_requests_per_actor_run: The desired number of concurrent HTTP requests for
                a single Actor Standby run.
            actor_standby_max_requests_per_actor_run: The maximum number of concurrent HTTP requests for
                a single Actor Standby run.
            actor_standby_idle_timeout: If the Actor run does not receive any requests for this time,
                it will be shut down.
            actor_standby_build: The build tag or number to run when the Actor is in Standby mode.
            actor_standby_memory_mbytes: The memory in megabytes to use when the Actor is in Standby mode.

        Returns:
            The updated task.
        """
        task_representation = get_task_representation(
            name=name,
            task_input=task_input,
            build=build,
            max_items=max_items,
            memory_mbytes=memory_mbytes,
            timeout=timeout,
            restart_on_error=restart_on_error,
            title=title,
            actor_standby_desired_requests_per_actor_run=actor_standby_desired_requests_per_actor_run,
            actor_standby_max_requests_per_actor_run=actor_standby_max_requests_per_actor_run,
            actor_standby_idle_timeout=actor_standby_idle_timeout,
            actor_standby_build=actor_standby_build,
            actor_standby_memory_mbytes=actor_standby_memory_mbytes,
        )
        cleaned = filter_none_values(task_representation, remove_empty_dicts=True)

        response = self._http_client.call(
            url=self._build_url(),
            method='PUT',
            params=self._build_params(),
            json=cleaned,
        )
        result = response_to_dict(response)
        return CreateTaskResponse.model_validate(result).data

    def delete(self) -> None:
        """Delete the task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/delete-task
        """
        try:
            self._http_client.call(
                url=self._build_url(),
                method='DELETE',
                params=self._build_params(),
            )
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

    def start(
        self,
        *,
        task_input: dict | None = None,
        build: str | None = None,
        max_items: int | None = None,
        memory_mbytes: int | None = None,
        timeout: timedelta | None = None,
        restart_on_error: bool | None = None,
        wait_for_finish: int | None = None,
        webhooks: list[dict] | None = None,
    ) -> Run:
        """Start the task and immediately return the Run object.

        https://docs.apify.com/api/v2#/reference/actor-tasks/run-collection/run-task

        Args:
            task_input: Task input dictionary.
            build: Specifies the Actor build to run. It can be either a build tag or build number. By default,
                the run uses the build specified in the task settings (typically latest).
            max_items: Maximum number of results that will be returned by this run. If the Actor is charged
                per result, you will not be charged for more results than the given limit.
            memory_mbytes: Memory limit for the run, in megabytes. By default, the run uses a memory limit specified
                in the task settings.
            timeout: Optional timeout for the run. By default, the run uses timeout specified
                in the task settings.
            restart_on_error: If true, the Task run process will be restarted whenever it exits with
                a non-zero status code.
            wait_for_finish: The maximum number of seconds the server waits for the run to finish. By default,
                it is 0, the maximum value is 60.
            webhooks: Optional ad-hoc webhooks (https://docs.apify.com/webhooks/ad-hoc-webhooks) associated with
                the Actor run which can be used to receive a notification, e.g. when the Actor finished or failed.
                If you already have a webhook set up for the Actor or task, you do not have to add it again here.
                Each webhook is represented by a dictionary containing these items:
                    * `event_types`: List of ``WebhookEventType`` values which trigger the webhook.
                    * `request_url`: URL to which to send the webhook HTTP request.
                    * `payload_template`: Optional template for the request payload.

        Returns:
            The run object.
        """
        request_params = self._build_params(
            build=build,
            maxItems=max_items,
            memory=memory_mbytes,
            timeout=int(timeout.total_seconds()) if timeout is not None else None,
            restartOnError=restart_on_error,
            waitForFinish=wait_for_finish,
            webhooks=encode_webhook_list_to_base64(webhooks) if webhooks is not None else None,
        )

        response = self._http_client.call(
            url=self._build_url('runs'),
            method='POST',
            headers={'content-type': 'application/json; charset=utf-8'},
            json=task_input,
            params=request_params,
        )

        result = response.json()
        return GetRunResponse.model_validate(result).data

    def call(
        self,
        *,
        task_input: dict | None = None,
        build: str | None = None,
        max_items: int | None = None,
        memory_mbytes: int | None = None,
        timeout: timedelta | None = None,
        restart_on_error: bool | None = None,
        webhooks: list[dict] | None = None,
        wait_duration: timedelta | None = None,
    ) -> Run | None:
        """Start a task and wait for it to finish before returning the Run object.

        It waits indefinitely, unless the wait_duration argument is provided.

        https://docs.apify.com/api/v2#/reference/actor-tasks/run-collection/run-task

        Args:
            task_input: Task input dictionary.
            build: Specifies the Actor build to run. It can be either a build tag or build number. By default,
                the run uses the build specified in the task settings (typically latest).
            max_items: Maximum number of results that will be returned by this run. If the Actor is charged per result,
                you will not be charged for more results than the given limit.
            memory_mbytes: Memory limit for the run, in megabytes. By default, the run uses a memory limit specified
                in the task settings.
            timeout: Optional timeout for the run. By default, the run uses timeout specified
                in the task settings.
            restart_on_error: If true, the Task run process will be restarted whenever it exits with
                a non-zero status code.
            webhooks: Specifies optional webhooks associated with the Actor run, which can be used to receive
                a notification e.g. when the Actor finished or failed. Note: if you already have a webhook set up for
                the Actor or task, you do not have to add it again here.
            wait_duration: The maximum time the server waits for the task run to finish. If not provided,
                waits indefinitely.

        Returns:
            The run object.
        """
        started_run = self.start(
            task_input=task_input,
            build=build,
            max_items=max_items,
            memory_mbytes=memory_mbytes,
            timeout=timeout,
            restart_on_error=restart_on_error,
            webhooks=webhooks,
        )

        run_client = self._client_registry.run_client(
            resource_id=started_run.id,
            base_url=self._base_url,
            public_base_url=self._public_base_url,
            http_client=self._http_client,
            client_registry=self._client_registry,
        )
        return run_client.wait_for_finish(wait_duration=wait_duration)

    def get_input(self) -> dict | None:
        """Retrieve the default input for this task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-input-object/get-task-input

        Returns:
            Retrieved task input.
        """
        try:
            response = self._http_client.call(
                url=self._build_url('input'),
                method='GET',
                params=self._build_params(),
            )
            return cast('dict', response.json())
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
        return None

    def update_input(self, *, task_input: dict) -> dict:
        """Update the default input for this task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-input-object/update-task-input

        Args:
            task_input: The new default input for this task.

        Returns:
            The updated task input.
        """
        response = self._http_client.call(
            url=self._build_url('input'),
            method='PUT',
            params=self._build_params(),
            json=task_input,
        )
        return cast('dict', response.json())

    def runs(self) -> RunCollectionClient:
        """Retrieve a client for the runs of this task."""
        return self._client_registry.run_collection_client(
            resource_path='runs',
            **self._base_client_kwargs,
        )

    def last_run(self, *, status: ActorJobStatus | None = None, origin: RunOrigin | None = None) -> RunClient:
        """Retrieve the client for the last run of this task.

        Last run is retrieved based on the start time of the runs.

        Args:
            status: Consider only runs with this status.
            origin: Consider only runs started with this origin.

        Returns:
            The resource client for the last run of this task.
        """
        return self._client_registry.run_client(
            resource_id='last',
            resource_path='runs',
            base_url=self._resource_url,
            public_base_url=self._public_base_url,
            http_client=self._http_client,
            client_registry=self._client_registry,
            params=self._build_params(status=enum_to_value(status), origin=enum_to_value(origin)),
        )

    def webhooks(self) -> WebhookCollectionClient:
        """Retrieve a client for webhooks associated with this task."""
        return self._client_registry.webhook_collection_client(**self._base_client_kwargs)


class TaskClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single task."""

    def __init__(
        self,
        *,
        resource_id: str,
        resource_path: str = 'actor-tasks',
        **kwargs: Any,
    ) -> None:
        super().__init__(resource_id=resource_id, resource_path=resource_path, **kwargs)

    async def get(self) -> Task | None:
        """Retrieve the task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/get-task

        Returns:
            The retrieved task.
        """
        try:
            response = await self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(),
            )
            result = response_to_dict(response)
            return CreateTaskResponse.model_validate(result).data
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            return None

    async def update(
        self,
        *,
        name: str | None = None,
        task_input: dict | None = None,
        build: str | None = None,
        max_items: int | None = None,
        memory_mbytes: int | None = None,
        timeout: timedelta | None = None,
        restart_on_error: bool | None = None,
        title: str | None = None,
        actor_standby_desired_requests_per_actor_run: int | None = None,
        actor_standby_max_requests_per_actor_run: int | None = None,
        actor_standby_idle_timeout: timedelta | None = None,
        actor_standby_build: str | None = None,
        actor_standby_memory_mbytes: int | None = None,
    ) -> Task:
        """Update the task with specified fields.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/update-task

        Args:
            name: Name of the task.
            build: Actor build to run. It can be either a build tag or build number. By default, the run uses
                the build specified in the task settings (typically latest).
            max_items: Maximum number of results that will be returned by this run. If the Actor is charged per result,
                you will not be charged for more results than the given limit.
            memory_mbytes: Memory limit for the run, in megabytes. By default, the run uses a memory limit specified
                in the task settings.
            timeout: Optional timeout for the run. By default, the run uses timeout specified
                in the task settings.
            restart_on_error: If true, the Task run process will be restarted whenever it exits with
                a non-zero status code.
            task_input: Task input dictionary.
            title: A human-friendly equivalent of the name.
            actor_standby_desired_requests_per_actor_run: The desired number of concurrent HTTP requests for
                a single Actor Standby run.
            actor_standby_max_requests_per_actor_run: The maximum number of concurrent HTTP requests for
                a single Actor Standby run.
            actor_standby_idle_timeout: If the Actor run does not receive any requests for this time,
                it will be shut down.
            actor_standby_build: The build tag or number to run when the Actor is in Standby mode.
            actor_standby_memory_mbytes: The memory in megabytes to use when the Actor is in Standby mode.

        Returns:
            The updated task.
        """
        task_representation = get_task_representation(
            name=name,
            task_input=task_input,
            build=build,
            max_items=max_items,
            memory_mbytes=memory_mbytes,
            timeout=timeout,
            restart_on_error=restart_on_error,
            title=title,
            actor_standby_desired_requests_per_actor_run=actor_standby_desired_requests_per_actor_run,
            actor_standby_max_requests_per_actor_run=actor_standby_max_requests_per_actor_run,
            actor_standby_idle_timeout=actor_standby_idle_timeout,
            actor_standby_build=actor_standby_build,
            actor_standby_memory_mbytes=actor_standby_memory_mbytes,
        )
        cleaned = filter_none_values(task_representation, remove_empty_dicts=True)

        response = await self._http_client.call(
            url=self._build_url(),
            method='PUT',
            params=self._build_params(),
            json=cleaned,
        )
        result = response_to_dict(response)
        return CreateTaskResponse.model_validate(result).data

    async def delete(self) -> None:
        """Delete the task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/delete-task
        """
        try:
            await self._http_client.call(
                url=self._build_url(),
                method='DELETE',
                params=self._build_params(),
            )
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

    async def start(
        self,
        *,
        task_input: dict | None = None,
        build: str | None = None,
        max_items: int | None = None,
        memory_mbytes: int | None = None,
        timeout: timedelta | None = None,
        restart_on_error: bool | None = None,
        wait_for_finish: int | None = None,
        webhooks: list[dict] | None = None,
    ) -> Run:
        """Start the task and immediately return the Run object.

        https://docs.apify.com/api/v2#/reference/actor-tasks/run-collection/run-task

        Args:
            task_input: Task input dictionary.
            build: Specifies the Actor build to run. It can be either a build tag or build number. By default,
                the run uses the build specified in the task settings (typically latest).
            max_items: Maximum number of results that will be returned by this run. If the Actor is charged
                per result, you will not be charged for more results than the given limit.
            memory_mbytes: Memory limit for the run, in megabytes. By default, the run uses a memory limit specified
                in the task settings.
            timeout: Optional timeout for the run. By default, the run uses timeout specified
                in the task settings.
            restart_on_error: If true, the Task run process will be restarted whenever it exits with
                a non-zero status code.
            wait_for_finish: The maximum number of seconds the server waits for the run to finish. By default,
                it is 0, the maximum value is 60.
            webhooks: Optional ad-hoc webhooks (https://docs.apify.com/webhooks/ad-hoc-webhooks) associated with
                the Actor run which can be used to receive a notification, e.g. when the Actor finished or failed.
                If you already have a webhook set up for the Actor or task, you do not have to add it again here.
                Each webhook is represented by a dictionary containing these items:
                    * `event_types`: List of ``WebhookEventType`` values which trigger the webhook.
                    * `request_url`: URL to which to send the webhook HTTP request.
                    * `payload_template`: Optional template for the request payload.

        Returns:
            The run object.
        """
        request_params = self._build_params(
            build=build,
            maxItems=max_items,
            memory=memory_mbytes,
            timeout=int(timeout.total_seconds()) if timeout is not None else None,
            restartOnError=restart_on_error,
            waitForFinish=wait_for_finish,
            webhooks=encode_webhook_list_to_base64(webhooks) if webhooks is not None else None,
        )

        response = await self._http_client.call(
            url=self._build_url('runs'),
            method='POST',
            headers={'content-type': 'application/json; charset=utf-8'},
            json=task_input,
            params=request_params,
        )

        result = response.json()
        return GetRunResponse.model_validate(result).data

    async def call(
        self,
        *,
        task_input: dict | None = None,
        build: str | None = None,
        max_items: int | None = None,
        memory_mbytes: int | None = None,
        timeout: timedelta | None = None,
        restart_on_error: bool | None = None,
        webhooks: list[dict] | None = None,
        wait_duration: timedelta | None = None,
    ) -> Run | None:
        """Start a task and wait for it to finish before returning the Run object.

        It waits indefinitely, unless the wait_duration argument is provided.

        https://docs.apify.com/api/v2#/reference/actor-tasks/run-collection/run-task

        Args:
            task_input: Task input dictionary.
            build: Specifies the Actor build to run. It can be either a build tag or build number. By default,
                the run uses the build specified in the task settings (typically latest).
            max_items: Maximum number of results that will be returned by this run. If the Actor is charged per result,
                you will not be charged for more results than the given limit.
            memory_mbytes: Memory limit for the run, in megabytes. By default, the run uses a memory limit specified
                in the task settings.
            timeout: Optional timeout for the run. By default, the run uses timeout specified
                in the task settings.
            restart_on_error: If true, the Task run process will be restarted whenever it exits with
                a non-zero status code.
            webhooks: Specifies optional webhooks associated with the Actor run, which can be used to receive
                a notification e.g. when the Actor finished or failed. Note: if you already have a webhook set up for
                the Actor or task, you do not have to add it again here.
            wait_duration: The maximum time the server waits for the task run to finish. If not provided,
                waits indefinitely.

        Returns:
            The run object.
        """
        started_run = await self.start(
            task_input=task_input,
            build=build,
            max_items=max_items,
            memory_mbytes=memory_mbytes,
            timeout=timeout,
            restart_on_error=restart_on_error,
            webhooks=webhooks,
        )
        run_client = self._client_registry.run_client(
            resource_id=started_run.id,
            base_url=self._base_url,
            public_base_url=self._public_base_url,
            http_client=self._http_client,
            client_registry=self._client_registry,
        )
        return await run_client.wait_for_finish(wait_duration=wait_duration)

    async def get_input(self) -> dict | None:
        """Retrieve the default input for this task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-input-object/get-task-input

        Returns:
            Retrieved task input.
        """
        try:
            response = await self._http_client.call(
                url=self._build_url('input'),
                method='GET',
                params=self._build_params(),
            )
            return cast('dict', response.json())
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
        return None

    async def update_input(self, *, task_input: dict) -> dict:
        """Update the default input for this task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-input-object/update-task-input

        Args:
            task_input: The new default input for this task.

        Returns:
            The updated task input.
        """
        response = await self._http_client.call(
            url=self._build_url('input'),
            method='PUT',
            params=self._build_params(),
            json=task_input,
        )
        return cast('dict', response.json())

    def runs(self) -> RunCollectionClientAsync:
        """Retrieve a client for the runs of this task."""
        return self._client_registry.run_collection_client(
            resource_path='runs',
            **self._base_client_kwargs,
        )

    def last_run(self, *, status: ActorJobStatus | None = None, origin: RunOrigin | None = None) -> RunClientAsync:
        """Retrieve the client for the last run of this task.

        Last run is retrieved based on the start time of the runs.

        Args:
            status: Consider only runs with this status.
            origin: Consider only runs started with this origin.

        Returns:
            The resource client for the last run of this task.
        """
        return self._client_registry.run_client(
            resource_id='last',
            resource_path='runs',
            base_url=self._resource_url,
            public_base_url=self._public_base_url,
            http_client=self._http_client,
            client_registry=self._client_registry,
            params=self._build_params(status=enum_to_value(status), origin=enum_to_value(origin)),
        )

    def webhooks(self) -> WebhookCollectionClientAsync:
        """Retrieve a client for webhooks associated with this task."""
        return self._client_registry.webhook_collection_client(**self._base_client_kwargs)

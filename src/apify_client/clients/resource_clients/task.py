from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from apify_shared.utils import (
    filter_out_none_values_recursively,
    ignore_docs,
    maybe_extract_enum_member_value,
    parse_date_fields,
)

from apify_client._errors import ApifyApiError
from apify_client._utils import catch_not_found_or_throw, encode_webhook_list_to_base64, pluck_data
from apify_client.clients.base import ResourceClient, ResourceClientAsync
from apify_client.clients.resource_clients.run import RunClient, RunClientAsync
from apify_client.clients.resource_clients.run_collection import RunCollectionClient, RunCollectionClientAsync
from apify_client.clients.resource_clients.webhook_collection import (
    WebhookCollectionClient,
    WebhookCollectionClientAsync,
)

if TYPE_CHECKING:
    from apify_shared.consts import ActorJobStatus, MetaOrigin


def get_task_representation(
    actor_id: str | None = None,
    name: str | None = None,
    task_input: dict | None = None,
    build: str | None = None,
    max_items: int | None = None,
    memory_mbytes: int | None = None,
    timeout_secs: int | None = None,
    title: str | None = None,
    actor_standby_desired_requests_per_actor_run: int | None = None,
    actor_standby_max_requests_per_actor_run: int | None = None,
    actor_standby_idle_timeout_secs: int | None = None,
    actor_standby_build: str | None = None,
    actor_standby_memory_mbytes: int | None = None,
) -> dict:
    """Get the dictionary representation of a task."""
    return {
        'actId': actor_id,
        'name': name,
        'options': {
            'build': build,
            'maxItems': max_items,
            'memoryMbytes': memory_mbytes,
            'timeoutSecs': timeout_secs,
        },
        'input': task_input,
        'title': title,
        'actorStandby': {
            'desiredRequestsPerActorRun': actor_standby_desired_requests_per_actor_run,
            'maxRequestsPerActorRun': actor_standby_max_requests_per_actor_run,
            'idleTimeoutSecs': actor_standby_idle_timeout_secs,
            'build': actor_standby_build,
            'memoryMbytes': actor_standby_memory_mbytes,
        },
    }


class TaskClient(ResourceClient):
    """Sub-client for manipulating a single task."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'actor-tasks')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> dict | None:
        """Retrieve the task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/get-task

        Returns:
            The retrieved task.
        """
        return self._get()

    def update(
        self,
        *,
        name: str | None = None,
        task_input: dict | None = None,
        build: str | None = None,
        max_items: int | None = None,
        memory_mbytes: int | None = None,
        timeout_secs: int | None = None,
        title: str | None = None,
        actor_standby_desired_requests_per_actor_run: int | None = None,
        actor_standby_max_requests_per_actor_run: int | None = None,
        actor_standby_idle_timeout_secs: int | None = None,
        actor_standby_build: str | None = None,
        actor_standby_memory_mbytes: int | None = None,
    ) -> dict:
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
            timeout_secs: Optional timeout for the run, in seconds. By default, the run uses timeout specified
                in the task settings.
            task_input: Task input dictionary.
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
            The updated task.
        """
        task_representation = get_task_representation(
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

        return self._update(filter_out_none_values_recursively(task_representation))

    def delete(self) -> None:
        """Delete the task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/delete-task
        """
        return self._delete()

    def start(
        self,
        *,
        task_input: dict | None = None,
        build: str | None = None,
        max_items: int | None = None,
        memory_mbytes: int | None = None,
        timeout_secs: int | None = None,
        wait_for_finish: int | None = None,
        webhooks: list[dict] | None = None,
    ) -> dict:
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
            timeout_secs: Optional timeout for the run, in seconds. By default, the run uses timeout specified
                in the task settings.
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
        request_params = self._params(
            build=build,
            maxItems=max_items,
            memory=memory_mbytes,
            timeout=timeout_secs,
            waitForFinish=wait_for_finish,
            webhooks=encode_webhook_list_to_base64(webhooks) if webhooks is not None else None,
        )

        response = self.http_client.call(
            url=self._url('runs'),
            method='POST',
            headers={'content-type': 'application/json; charset=utf-8'},
            json=task_input,
            params=request_params,
        )

        return parse_date_fields(pluck_data(response.json()))

    def call(
        self,
        *,
        task_input: dict | None = None,
        build: str | None = None,
        max_items: int | None = None,
        memory_mbytes: int | None = None,
        timeout_secs: int | None = None,
        webhooks: list[dict] | None = None,
        wait_secs: int | None = None,
    ) -> dict | None:
        """Start a task and wait for it to finish before returning the Run object.

        It waits indefinitely, unless the wait_secs argument is provided.

        https://docs.apify.com/api/v2#/reference/actor-tasks/run-collection/run-task

        Args:
            task_input: Task input dictionary.
            build: Specifies the Actor build to run. It can be either a build tag or build number. By default,
                the run uses the build specified in the task settings (typically latest).
            max_items: Maximum number of results that will be returned by this run. If the Actor is charged per result,
                you will not be charged for more results than the given limit.
            memory_mbytes: Memory limit for the run, in megabytes. By default, the run uses a memory limit specified
                in the task settings.
            timeout_secs: Optional timeout for the run, in seconds. By default, the run uses timeout specified
                in the task settings.
            webhooks: Specifies optional webhooks associated with the Actor run, which can be used to receive
                a notification e.g. when the Actor finished or failed. Note: if you already have a webhook set up for
                the Actor or task, you do not have to add it again here.
            wait_secs: The maximum number of seconds the server waits for the task run to finish. If not provided,
                waits indefinitely.

        Returns:
            The run object.
        """
        started_run = self.start(
            task_input=task_input,
            build=build,
            max_items=max_items,
            memory_mbytes=memory_mbytes,
            timeout_secs=timeout_secs,
            webhooks=webhooks,
        )

        return self.root_client.run(started_run['id']).wait_for_finish(wait_secs=wait_secs)

    def get_input(self) -> dict | None:
        """Retrieve the default input for this task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-input-object/get-task-input

        Returns:
            Retrieved task input.
        """
        try:
            response = self.http_client.call(
                url=self._url('input'),
                method='GET',
                params=self._params(),
            )
            return cast('dict', response.json())
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
        return None

    def update_input(self, *, task_input: dict) -> dict:
        """Update the default input for this task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-input-object/update-task-input

        Returns:
            Retrieved task input.
        """
        response = self.http_client.call(
            url=self._url('input'),
            method='PUT',
            params=self._params(),
            json=task_input,
        )
        return cast('dict', response.json())

    def runs(self) -> RunCollectionClient:
        """Retrieve a client for the runs of this task."""
        return RunCollectionClient(**self._sub_resource_init_options(resource_path='runs'))

    def last_run(self, *, status: ActorJobStatus | None = None, origin: MetaOrigin | None = None) -> RunClient:
        """Retrieve the client for the last run of this task.

        Last run is retrieved based on the start time of the runs.

        Args:
            status: Consider only runs with this status.
            origin: Consider only runs started with this origin.

        Returns:
            The resource client for the last run of this task.
        """
        return RunClient(
            **self._sub_resource_init_options(
                resource_id='last',
                resource_path='runs',
                params=self._params(
                    status=maybe_extract_enum_member_value(status),
                    origin=maybe_extract_enum_member_value(origin),
                ),
            )
        )

    def webhooks(self) -> WebhookCollectionClient:
        """Retrieve a client for webhooks associated with this task."""
        return WebhookCollectionClient(**self._sub_resource_init_options())


class TaskClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single task."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'actor-tasks')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self) -> dict | None:
        """Retrieve the task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/get-task

        Returns:
            The retrieved task.
        """
        return await self._get()

    async def update(
        self,
        *,
        name: str | None = None,
        task_input: dict | None = None,
        build: str | None = None,
        max_items: int | None = None,
        memory_mbytes: int | None = None,
        timeout_secs: int | None = None,
        title: str | None = None,
        actor_standby_desired_requests_per_actor_run: int | None = None,
        actor_standby_max_requests_per_actor_run: int | None = None,
        actor_standby_idle_timeout_secs: int | None = None,
        actor_standby_build: str | None = None,
        actor_standby_memory_mbytes: int | None = None,
    ) -> dict:
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
            timeout_secs: Optional timeout for the run, in seconds. By default, the run uses timeout specified
                in the task settings.
            task_input: Task input dictionary.
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
            The updated task.
        """
        task_representation = get_task_representation(
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

        return await self._update(filter_out_none_values_recursively(task_representation))

    async def delete(self) -> None:
        """Delete the task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/delete-task
        """
        return await self._delete()

    async def start(
        self,
        *,
        task_input: dict | None = None,
        build: str | None = None,
        max_items: int | None = None,
        memory_mbytes: int | None = None,
        timeout_secs: int | None = None,
        wait_for_finish: int | None = None,
        webhooks: list[dict] | None = None,
    ) -> dict:
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
            timeout_secs: Optional timeout for the run, in seconds. By default, the run uses timeout specified
                in the task settings.
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
        request_params = self._params(
            build=build,
            maxItems=max_items,
            memory=memory_mbytes,
            timeout=timeout_secs,
            waitForFinish=wait_for_finish,
            webhooks=encode_webhook_list_to_base64(webhooks) if webhooks is not None else None,
        )

        response = await self.http_client.call(
            url=self._url('runs'),
            method='POST',
            headers={'content-type': 'application/json; charset=utf-8'},
            json=task_input,
            params=request_params,
        )

        return parse_date_fields(pluck_data(response.json()))

    async def call(
        self,
        *,
        task_input: dict | None = None,
        build: str | None = None,
        max_items: int | None = None,
        memory_mbytes: int | None = None,
        timeout_secs: int | None = None,
        webhooks: list[dict] | None = None,
        wait_secs: int | None = None,
    ) -> dict | None:
        """Start a task and wait for it to finish before returning the Run object.

        It waits indefinitely, unless the wait_secs argument is provided.

        https://docs.apify.com/api/v2#/reference/actor-tasks/run-collection/run-task

        Args:
            task_input: Task input dictionary.
            build: Specifies the Actor build to run. It can be either a build tag or build number. By default,
                the run uses the build specified in the task settings (typically latest).
            max_items: Maximum number of results that will be returned by this run. If the Actor is charged per result,
                you will not be charged for more results than the given limit.
            memory_mbytes: Memory limit for the run, in megabytes. By default, the run uses a memory limit specified
                in the task settings.
            timeout_secs: Optional timeout for the run, in seconds. By default, the run uses timeout specified
                in the task settings.
            webhooks: Specifies optional webhooks associated with the Actor run, which can be used to receive
                a notification e.g. when the Actor finished or failed. Note: if you already have a webhook set up for
                the Actor or task, you do not have to add it again here.
            wait_secs: The maximum number of seconds the server waits for the task run to finish. If not provided,
                waits indefinitely.

        Returns:
            The run object.
        """
        started_run = await self.start(
            task_input=task_input,
            build=build,
            max_items=max_items,
            memory_mbytes=memory_mbytes,
            timeout_secs=timeout_secs,
            webhooks=webhooks,
        )

        return await self.root_client.run(started_run['id']).wait_for_finish(wait_secs=wait_secs)

    async def get_input(self) -> dict | None:
        """Retrieve the default input for this task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-input-object/get-task-input

        Returns:
            Retrieved task input.
        """
        try:
            response = await self.http_client.call(
                url=self._url('input'),
                method='GET',
                params=self._params(),
            )
            return cast('dict', response.json())
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
        return None

    async def update_input(self, *, task_input: dict) -> dict:
        """Update the default input for this task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-input-object/update-task-input

        Returns:
            Retrieved task input.
        """
        response = await self.http_client.call(
            url=self._url('input'),
            method='PUT',
            params=self._params(),
            json=task_input,
        )
        return cast('dict', response.json())

    def runs(self) -> RunCollectionClientAsync:
        """Retrieve a client for the runs of this task."""
        return RunCollectionClientAsync(**self._sub_resource_init_options(resource_path='runs'))

    def last_run(self, *, status: ActorJobStatus | None = None, origin: MetaOrigin | None = None) -> RunClientAsync:
        """Retrieve the client for the last run of this task.

        Last run is retrieved based on the start time of the runs.

        Args:
            status: Consider only runs with this status.
            origin: Consider only runs started with this origin.

        Returns:
            The resource client for the last run of this task.
        """
        return RunClientAsync(
            **self._sub_resource_init_options(
                resource_id='last',
                resource_path='runs',
                params=self._params(
                    status=maybe_extract_enum_member_value(status),
                    origin=maybe_extract_enum_member_value(origin),
                ),
            )
        )

    def webhooks(self) -> WebhookCollectionClientAsync:
        """Retrieve a client for webhooks associated with this task."""
        return WebhookCollectionClientAsync(**self._sub_resource_init_options())

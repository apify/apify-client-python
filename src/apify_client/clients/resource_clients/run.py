from __future__ import annotations

from typing import Any

from apify_shared.utils import filter_out_none_values_recursively, ignore_docs, parse_date_fields

from apify_client._utils import encode_key_value_store_record_value, pluck_data, to_safe_id
from apify_client.clients.base import ActorJobBaseClient, ActorJobBaseClientAsync
from apify_client.clients.resource_clients.dataset import DatasetClient, DatasetClientAsync
from apify_client.clients.resource_clients.key_value_store import KeyValueStoreClient, KeyValueStoreClientAsync
from apify_client.clients.resource_clients.log import LogClient, LogClientAsync
from apify_client.clients.resource_clients.request_queue import RequestQueueClient, RequestQueueClientAsync


class RunClient(ActorJobBaseClient):
    """Sub-client for manipulating a single Actor run."""

    @ignore_docs
    def __init__(self: RunClient, *args: Any, **kwargs: Any) -> None:
        """Initialize the RunClient."""
        resource_path = kwargs.pop('resource_path', 'actor-runs')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self: RunClient) -> dict | None:
        """Return information about the Actor run.

        https://docs.apify.com/api/v2#/reference/actor-runs/run-object/get-run

        Returns:
            dict: The retrieved Actor run data
        """
        return self._get()

    def update(self: RunClient, *, status_message: str | None = None, is_status_message_terminal: bool | None = None) -> dict:
        """Update the run with the specified fields.

        https://docs.apify.com/api/v2#/reference/actor-runs/run-object/update-run

        Args:
            status_message (str, optional): The new status message for the run
            is_status_message_terminal (bool, optional): Set this flag to True if this is the final status message of the Actor run.

        Returns:
            dict: The updated run
        """
        updated_fields = {
            'statusMessage': status_message,
            'isStatusMessageTerminal': is_status_message_terminal,
        }

        return self._update(filter_out_none_values_recursively(updated_fields))

    def delete(self: RunClient) -> None:
        """Delete the run.

        https://docs.apify.com/api/v2#/reference/actor-runs/delete-run/delete-run
        """
        return self._delete()

    def abort(self: RunClient, *, gracefully: bool | None = None) -> dict:
        """Abort the Actor run which is starting or currently running and return its details.

        https://docs.apify.com/api/v2#/reference/actor-runs/abort-run/abort-run

        Args:
            gracefully (bool, optional): If True, the Actor run will abort gracefully.
                It will send ``aborting`` and ``persistStates`` events into the run and force-stop the run after 30 seconds.
                It is helpful in cases where you plan to resurrect the run later.

        Returns:
            dict: The data of the aborted Actor run
        """
        return self._abort(gracefully=gracefully)

    def wait_for_finish(self: RunClient, *, wait_secs: int | None = None) -> dict | None:
        """Wait synchronously until the run finishes or the server times out.

        Args:
            wait_secs (int, optional): how long does the client wait for run to finish. None for indefinite.

        Returns:
            dict, optional: The Actor run data. If the status on the object is not one of the terminal statuses
                (SUCEEDED, FAILED, TIMED_OUT, ABORTED), then the run has not yet finished.
        """
        return self._wait_for_finish(wait_secs=wait_secs)

    def metamorph(
        self: RunClient,
        *,
        target_actor_id: str,
        target_actor_build: str | None = None,
        run_input: Any = None,
        content_type: str | None = None,
    ) -> dict:
        """Transform an Actor run into a run of another Actor with a new input.

        https://docs.apify.com/api/v2#/reference/actor-runs/metamorph-run/metamorph-run

        Args:
            target_actor_id (str): ID of the target Actor that the run should be transformed into
            target_actor_build (str, optional): The build of the target Actor. It can be either a build tag or build number.
                By default, the run uses the build specified in the default run configuration for the target Actor (typically the latest build).
            run_input (Any, optional): The input to pass to the new run.
            content_type (str, optional): The content type of the input.

        Returns:
            dict: The Actor run data.
        """
        run_input, content_type = encode_key_value_store_record_value(run_input, content_type)

        safe_target_actor_id = to_safe_id(target_actor_id)

        request_params = self._params(
            targetActorId=safe_target_actor_id,
            build=target_actor_build,
        )

        response = self.http_client.call(
            url=self._url('metamorph'),
            method='POST',
            headers={'content-type': content_type},
            data=run_input,
            params=request_params,
        )

        return parse_date_fields(pluck_data(response.json()))

    def resurrect(
        self: RunClient,
        *,
        build: str | None = None,
        memory_mbytes: int | None = None,
        timeout_secs: int | None = None,
    ) -> dict:
        """Resurrect a finished Actor run.

        Only finished runs, i.e. runs with status FINISHED, FAILED, ABORTED and TIMED-OUT can be resurrected.
        Run status will be updated to RUNNING and its container will be restarted with the same default storages.

        https://docs.apify.com/api/v2#/reference/actor-runs/resurrect-run/resurrect-run

        Args:
            build (str, optional): Which Actor build the resurrected run should use. It can be either a build tag or build number.
                                   By default, the resurrected run uses the same build as before.
            memory_mbytes (int, optional): New memory limit for the resurrected run, in megabytes.
                                           By default, the resurrected run uses the same memory limit as before.
            timeout_secs (int, optional): New timeout for the resurrected run, in seconds.
                                           By default, the resurrected run uses the same timeout as before.

        Returns:
            dict: The Actor run data.
        """
        request_params = self._params(
            build=build,
            memory=memory_mbytes,
            timeout=timeout_secs,
        )

        response = self.http_client.call(
            url=self._url('resurrect'),
            method='POST',
            params=request_params,
        )

        return parse_date_fields(pluck_data(response.json()))

    def reboot(self: RunClient) -> dict:
        """Reboot an Actor run. Only runs that are running, i.e. runs with status RUNNING can be rebooted.

        https://docs.apify.com/api/v2#/reference/actor-runs/reboot-run/reboot-run

        Returns:
            dict: The Actor run data.
        """
        response = self.http_client.call(
            url=self._url('reboot'),
            method='POST',
        )
        return parse_date_fields(pluck_data(response.json()))

    def dataset(self: RunClient) -> DatasetClient:
        """Get the client for the default dataset of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            DatasetClient: A client allowing access to the default dataset of this Actor run.
        """
        return DatasetClient(
            **self._sub_resource_init_options(resource_path='dataset'),
        )

    def key_value_store(self: RunClient) -> KeyValueStoreClient:
        """Get the client for the default key-value store of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            KeyValueStoreClient: A client allowing access to the default key-value store of this Actor run.
        """
        return KeyValueStoreClient(
            **self._sub_resource_init_options(resource_path='key-value-store'),
        )

    def request_queue(self: RunClient) -> RequestQueueClient:
        """Get the client for the default request queue of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            RequestQueueClient: A client allowing access to the default request_queue of this Actor run.
        """
        return RequestQueueClient(
            **self._sub_resource_init_options(resource_path='request-queue'),
        )

    def log(self: RunClient) -> LogClient:
        """Get the client for the log of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            LogClient: A client allowing access to the log of this Actor run.
        """
        return LogClient(
            **self._sub_resource_init_options(resource_path='log'),
        )


class RunClientAsync(ActorJobBaseClientAsync):
    """Async sub-client for manipulating a single Actor run."""

    @ignore_docs
    def __init__(self: RunClientAsync, *args: Any, **kwargs: Any) -> None:
        """Initialize the RunClientAsync."""
        resource_path = kwargs.pop('resource_path', 'actor-runs')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self: RunClientAsync) -> dict | None:
        """Return information about the Actor run.

        https://docs.apify.com/api/v2#/reference/actor-runs/run-object/get-run

        Returns:
            dict: The retrieved Actor run data
        """
        return await self._get()

    async def update(self: RunClientAsync, *, status_message: str | None = None, is_status_message_terminal: bool | None = None) -> dict:
        """Update the run with the specified fields.

        https://docs.apify.com/api/v2#/reference/actor-runs/run-object/update-run

        Args:
            status_message (str, optional): The new status message for the run
            is_status_message_terminal (bool, optional): Set this flag to True if this is the final status message of the Actor run.

        Returns:
            dict: The updated run
        """
        updated_fields = {
            'statusMessage': status_message,
            'isStatusMessageTerminal': is_status_message_terminal,
        }

        return await self._update(filter_out_none_values_recursively(updated_fields))

    async def abort(self: RunClientAsync, *, gracefully: bool | None = None) -> dict:
        """Abort the Actor run which is starting or currently running and return its details.

        https://docs.apify.com/api/v2#/reference/actor-runs/abort-run/abort-run

        Args:
            gracefully (bool, optional): If True, the Actor run will abort gracefully.
                It will send ``aborting`` and ``persistStates`` events into the run and force-stop the run after 30 seconds.
                It is helpful in cases where you plan to resurrect the run later.

        Returns:
            dict: The data of the aborted Actor run
        """
        return await self._abort(gracefully=gracefully)

    async def wait_for_finish(self: RunClientAsync, *, wait_secs: int | None = None) -> dict | None:
        """Wait synchronously until the run finishes or the server times out.

        Args:
            wait_secs (int, optional): how long does the client wait for run to finish. None for indefinite.

        Returns:
            dict, optional: The Actor run data. If the status on the object is not one of the terminal statuses
                (SUCEEDED, FAILED, TIMED_OUT, ABORTED), then the run has not yet finished.
        """
        return await self._wait_for_finish(wait_secs=wait_secs)

    async def delete(self: RunClientAsync) -> None:
        """Delete the run.

        https://docs.apify.com/api/v2#/reference/actor-runs/delete-run/delete-run
        """
        return await self._delete()

    async def metamorph(
        self: RunClientAsync,
        *,
        target_actor_id: str,
        target_actor_build: str | None = None,
        run_input: Any = None,
        content_type: str | None = None,
    ) -> dict:
        """Transform an Actor run into a run of another Actor with a new input.

        https://docs.apify.com/api/v2#/reference/actor-runs/metamorph-run/metamorph-run

        Args:
            target_actor_id (str): ID of the target Actor that the run should be transformed into
            target_actor_build (str, optional): The build of the target Actor. It can be either a build tag or build number.
                By default, the run uses the build specified in the default run configuration for the target Actor (typically the latest build).
            run_input (Any, optional): The input to pass to the new run.
            content_type (str, optional): The content type of the input.

        Returns:
            dict: The Actor run data.
        """
        run_input, content_type = encode_key_value_store_record_value(run_input, content_type)

        safe_target_actor_id = to_safe_id(target_actor_id)

        request_params = self._params(
            targetActorId=safe_target_actor_id,
            build=target_actor_build,
        )

        response = await self.http_client.call(
            url=self._url('metamorph'),
            method='POST',
            headers={'content-type': content_type},
            data=run_input,
            params=request_params,
        )

        return parse_date_fields(pluck_data(response.json()))

    async def resurrect(
        self: RunClientAsync,
        *,
        build: str | None = None,
        memory_mbytes: int | None = None,
        timeout_secs: int | None = None,
    ) -> dict:
        """Resurrect a finished Actor run.

        Only finished runs, i.e. runs with status FINISHED, FAILED, ABORTED and TIMED-OUT can be resurrected.
        Run status will be updated to RUNNING and its container will be restarted with the same default storages.

        https://docs.apify.com/api/v2#/reference/actor-runs/resurrect-run/resurrect-run

        Args:
            build (str, optional): Which Actor build the resurrected run should use. It can be either a build tag or build number.
                                   By default, the resurrected run uses the same build as before.
            memory_mbytes (int, optional): New memory limit for the resurrected run, in megabytes.
                                           By default, the resurrected run uses the same memory limit as before.
            timeout_secs (int, optional): New timeout for the resurrected run, in seconds.
                                           By default, the resurrected run uses the same timeout as before.

        Returns:
            dict: The Actor run data.
        """
        request_params = self._params(
            build=build,
            memory=memory_mbytes,
            timeout=timeout_secs,
        )

        response = await self.http_client.call(
            url=self._url('resurrect'),
            method='POST',
            params=request_params,
        )

        return parse_date_fields(pluck_data(response.json()))

    async def reboot(self: RunClientAsync) -> dict:
        """Reboot an Actor run. Only runs that are running, i.e. runs with status RUNNING can be rebooted.

        https://docs.apify.com/api/v2#/reference/actor-runs/reboot-run/reboot-run

        Returns:
            dict: The Actor run data.
        """
        response = await self.http_client.call(
            url=self._url('reboot'),
            method='POST',
        )
        return parse_date_fields(pluck_data(response.json()))

    def dataset(self: RunClientAsync) -> DatasetClientAsync:
        """Get the client for the default dataset of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            DatasetClientAsync: A client allowing access to the default dataset of this Actor run.
        """
        return DatasetClientAsync(
            **self._sub_resource_init_options(resource_path='dataset'),
        )

    def key_value_store(self: RunClientAsync) -> KeyValueStoreClientAsync:
        """Get the client for the default key-value store of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            KeyValueStoreClientAsync: A client allowing access to the default key-value store of this Actor run.
        """
        return KeyValueStoreClientAsync(
            **self._sub_resource_init_options(resource_path='key-value-store'),
        )

    def request_queue(self: RunClientAsync) -> RequestQueueClientAsync:
        """Get the client for the default request queue of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            RequestQueueClientAsync: A client allowing access to the default request_queue of this Actor run.
        """
        return RequestQueueClientAsync(
            **self._sub_resource_init_options(resource_path='request-queue'),
        )

    def log(self: RunClientAsync) -> LogClientAsync:
        """Get the client for the log of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            LogClientAsync: A client allowing access to the log of this Actor run.
        """
        return LogClientAsync(
            **self._sub_resource_init_options(resource_path='log'),
        )

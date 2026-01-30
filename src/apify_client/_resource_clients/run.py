from __future__ import annotations

import json
import random
import string
import time
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from apify_client._logging import create_redirect_logger
from apify_client._models import GetRunResponse, Run
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import (
    catch_not_found_or_throw,
    encode_key_value_store_record_value,
    filter_none_values,
    response_to_dict,
    to_safe_id,
    to_seconds,
)
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    import logging
    from decimal import Decimal

    from apify_client._models import GeneralAccessEnum
    from apify_client._resource_clients import (
        DatasetClient,
        DatasetClientAsync,
        KeyValueStoreClient,
        KeyValueStoreClientAsync,
        LogClient,
        LogClientAsync,
        RequestQueueClient,
        RequestQueueClientAsync,
        StatusMessageWatcherAsync,
        StatusMessageWatcherSync,
        StreamedLogAsync,
        StreamedLogSync,
    )


class RunClient(ResourceClient):
    """Sub-client for manipulating a single Actor run."""

    def __init__(
        self,
        *,
        resource_id: str,
        resource_path: str = 'actor-runs',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_id=resource_id,
            resource_path=resource_path,
            **kwargs,
        )

    def get(self) -> Run | None:
        """Return information about the Actor run.

        https://docs.apify.com/api/v2#/reference/actor-runs/run-object/get-run

        Returns:
            The retrieved Actor run data.
        """
        try:
            response = self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(),
            )
            result = response_to_dict(response)
            return GetRunResponse.model_validate(result).data
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            return None

    def update(
        self,
        *,
        status_message: str | None = None,
        is_status_message_terminal: bool | None = None,
        general_access: GeneralAccessEnum | None = None,
    ) -> Run:
        """Update the run with the specified fields.

        https://docs.apify.com/api/v2#/reference/actor-runs/run-object/update-run

        Args:
            status_message: The new status message for the run.
            is_status_message_terminal: Set this flag to True if this is the final status message of the Actor run.
            general_access: Determines how others can access the run and its storages.

        Returns:
            The updated run.
        """
        updated_fields = {
            'statusMessage': status_message,
            'isStatusMessageTerminal': is_status_message_terminal,
            'generalAccess': general_access,
        }
        cleaned = filter_none_values(updated_fields)

        response = self._http_client.call(
            url=self._build_url(),
            method='PUT',
            params=self._build_params(),
            json=cleaned,
        )
        result = response_to_dict(response)
        return GetRunResponse.model_validate(result).data

    def delete(self) -> None:
        """Delete the run.

        https://docs.apify.com/api/v2#/reference/actor-runs/delete-run/delete-run
        """
        try:
            self._http_client.call(
                url=self._build_url(),
                method='DELETE',
                params=self._build_params(),
            )
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

    def abort(self, *, gracefully: bool | None = None) -> Run:
        """Abort the Actor run which is starting or currently running and return its details.

        https://docs.apify.com/api/v2#/reference/actor-runs/abort-run/abort-run

        Args:
            gracefully: If True, the Actor run will abort gracefully. It will send `aborting` and `persistStates`
                events into the run and force-stop the run after 30 seconds. It is helpful in cases where you plan
                to resurrect the run later.

        Returns:
            The data of the aborted Actor run.
        """
        response = self._http_client.call(
            url=self._build_url('abort'),
            method='POST',
            params=self._build_params(gracefully=gracefully),
        )
        result = response_to_dict(response)
        return GetRunResponse.model_validate(result).data

    def wait_for_finish(self, *, wait_duration: timedelta | None = None) -> Run | None:
        """Wait synchronously until the run finishes or the server times out.

        Args:
            wait_duration: How long does the client wait for run to finish. None for indefinite.

        Returns:
            The Actor run data. If the status on the object is not one of the terminal statuses (SUCCEEDED, FAILED,
                TIMED_OUT, ABORTED), then the run has not yet finished.
        """
        response = self._wait_for_finish(
            url=self._build_url(),
            params=self._build_params(),
            wait_duration=wait_duration,
        )

        if response is None:
            return None

        return Run.model_validate(response)

    def metamorph(
        self,
        *,
        target_actor_id: str,
        target_actor_build: str | None = None,
        run_input: Any = None,
        content_type: str | None = None,
    ) -> Run:
        """Transform an Actor run into a run of another Actor with a new input.

        https://docs.apify.com/api/v2#/reference/actor-runs/metamorph-run/metamorph-run

        Args:
            target_actor_id: ID of the target Actor that the run should be transformed into.
            target_actor_build: The build of the target Actor. It can be either a build tag or build number.
                By default, the run uses the build specified in the default run configuration for the target Actor
                (typically the latest build).
            run_input: The input to pass to the new run.
            content_type: The content type of the input.

        Returns:
            The Actor run data.
        """
        run_input, content_type = encode_key_value_store_record_value(run_input, content_type)

        safe_target_actor_id = to_safe_id(target_actor_id)

        request_params = self._build_params(targetActorId=safe_target_actor_id, build=target_actor_build)

        response = self._http_client.call(
            url=self._build_url('metamorph'),
            method='POST',
            headers={'content-type': content_type},
            data=run_input,
            params=request_params,
        )

        response_as_dict = response_to_dict(response)
        return GetRunResponse.model_validate(response_as_dict).data

    def resurrect(
        self,
        *,
        build: str | None = None,
        memory_mbytes: int | None = None,
        timeout: timedelta | None = None,
        max_items: int | None = None,
        max_total_charge_usd: Decimal | None = None,
        restart_on_error: bool | None = None,
    ) -> Run:
        """Resurrect a finished Actor run.

        Only finished runs, i.e. runs with status FINISHED, FAILED, ABORTED and TIMED-OUT can be resurrected.
        Run status will be updated to RUNNING and its container will be restarted with the same default storages.

        https://docs.apify.com/api/v2#/reference/actor-runs/resurrect-run/resurrect-run

        Args:
            build: Which Actor build the resurrected run should use. It can be either a build tag or build number.
                By default, the resurrected run uses the same build as before.
            memory_mbytes: New memory limit for the resurrected run, in megabytes. By default, the resurrected run
                uses the same memory limit as before.
            timeout: New timeout for the resurrected run. By default, the resurrected run uses the
                same timeout as before.
            max_items: Maximum number of items that the resurrected pay-per-result run will return. By default, the
                resurrected run uses the same limit as before. Limit can be only increased.
            max_total_charge_usd: Maximum cost for the resurrected pay-per-event run in USD. By default, the
                resurrected run uses the same limit as before. Limit can be only increased.
            restart_on_error: Determines whether the resurrected run will be restarted if it fails.
                By default, the resurrected run uses the same setting as before.

        Returns:
            The Actor run data.
        """
        request_params = self._build_params(
            build=build,
            memory=memory_mbytes,
            timeout=to_seconds(timeout, as_int=True),
            maxItems=max_items,
            maxTotalChargeUsd=max_total_charge_usd,
            restartOnError=restart_on_error,
        )

        response = self._http_client.call(
            url=self._build_url('resurrect'),
            method='POST',
            params=request_params,
        )

        response_as_dict = response_to_dict(response)
        return GetRunResponse.model_validate(response_as_dict).data

    def reboot(self) -> Run:
        """Reboot an Actor run. Only runs that are running, i.e. runs with status RUNNING can be rebooted.

        https://docs.apify.com/api/v2#/reference/actor-runs/reboot-run/reboot-run

        Returns:
            The Actor run data.
        """
        response = self._http_client.call(
            url=self._build_url('reboot'),
            method='POST',
        )
        response_as_dict = response_to_dict(response)
        return GetRunResponse.model_validate(response_as_dict).data

    def dataset(self) -> DatasetClient:
        """Get the client for the default dataset of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            A client allowing access to the default dataset of this Actor run.
        """
        return self._client_registry.dataset_client(
            resource_path='dataset',
            **self._base_client_kwargs,
        )

    def key_value_store(self) -> KeyValueStoreClient:
        """Get the client for the default key-value store of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            A client allowing access to the default key-value store of this Actor run.
        """
        return self._client_registry.key_value_store_client(
            resource_path='key-value-store',
            **self._base_client_kwargs,
        )

    def request_queue(self) -> RequestQueueClient:
        """Get the client for the default request queue of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            A client allowing access to the default request_queue of this Actor run.
        """
        return self._client_registry.request_queue_client(
            resource_path='request-queue',
            **self._base_client_kwargs,
        )

    def log(self) -> LogClient:
        """Get the client for the log of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            A client allowing access to the log of this Actor run.
        """
        return self._client_registry.log_client(
            resource_path='log',
            **self._base_client_kwargs,
        )

    def get_streamed_log(self, to_logger: logging.Logger | None = None, *, from_start: bool = True) -> StreamedLogSync:
        """Get `StreamedLog` instance that can be used to redirect logs.

         `StreamedLog` can be explicitly started and stopped or used as a context manager.

        Args:
            to_logger: `Logger` used for logging the redirected messages. If not provided, a new logger is created
            from_start: If `True`, all logs from the start of the Actor run will be redirected. If `False`, only newly
                arrived logs will be redirected. This can be useful for redirecting only a small portion of relevant
                logs for long-running Actors in stand-by.

        Returns:
            `StreamedLog` instance for redirected logs.
        """
        run_data = self.get()
        run_id = f'runId:{run_data.id}' if run_data and run_data.id else ''

        actor_id = run_data.act_id if run_data else ''
        actor_data = None
        if actor_id:
            actor_client = self._client_registry.actor_client(
                resource_id=actor_id,
                base_url=self._base_url,
                public_base_url=self._public_base_url,
                http_client=self._http_client,
                client_registry=self._client_registry,
            )
            actor_data = actor_client.get()
        actor_name = actor_data.name if actor_data else ''

        if not to_logger:
            name = ' '.join(part for part in (actor_name, run_id) if part)
            to_logger = create_redirect_logger(f'apify.{name}')

        return self._client_registry.streamed_log(log_client=self.log(), to_logger=to_logger, from_start=from_start)

    def charge(
        self,
        event_name: str,
        count: int | None = None,
        idempotency_key: str | None = None,
    ) -> None:
        """Charge for an event of a Pay-Per-Event Actor run.

        https://docs.apify.com/api/v2#/reference/actor-runs/charge-events-in-run

        Args:
            event_name: The name of the event to charge for.
            count: The number of events to charge. Defaults to 1 if not provided.
            idempotency_key: A unique key to ensure idempotent charging. If not provided,
                one will be auto-generated.

        Raises:
            ValueError: If event_name is empty or not provided.
        """
        if not event_name:
            raise ValueError('event_name is required for charging an event')

        if idempotency_key is None:
            random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            timestamp_ms = int(time.time() * 1000)
            idempotency_key = f'{self._resource_id}-{event_name}-{timestamp_ms}-{random_suffix}'

        self._http_client.call(
            url=self._build_url('charge'),
            method='POST',
            headers={
                'idempotency-key': idempotency_key,
                'content-type': 'application/json',
            },
            data=json.dumps(
                {
                    'eventName': event_name,
                    'count': count or 1,
                }
            ),
        )

    def get_status_message_watcher(
        self, to_logger: logging.Logger | None = None, check_period: timedelta = timedelta(seconds=1)
    ) -> StatusMessageWatcherSync:
        """Get `StatusMessageWatcher` instance that can be used to redirect status and status messages to logs.

        `StatusMessageWatcher` can be explicitly started and stopped or used as a context manager.

        Args:
            to_logger: `Logger` used for logging the status and status messages. If not provided, a new logger is
            created.
            check_period: The period with which the status message will be polled.

        Returns:
            `StatusMessageWatcher` instance.
        """
        run_data = self.get()
        run_id = f'runId:{run_data.id}' if run_data and run_data.id else ''

        actor_id = run_data.act_id if run_data else ''
        actor_data = None
        if actor_id:
            actor_client = self._client_registry.actor_client(
                resource_id=actor_id,
                base_url=self._base_url,
                public_base_url=self._public_base_url,
                http_client=self._http_client,
                client_registry=self._client_registry,
            )
            actor_data = actor_client.get()
        actor_name = actor_data.name if actor_data else ''

        if not to_logger:
            name = ' '.join(part for part in (actor_name, run_id) if part)
            to_logger = create_redirect_logger(f'apify.{name}')

        return self._client_registry.status_message_watcher(
            run_client=self, to_logger=to_logger, check_period=check_period
        )


class RunClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single Actor run."""

    def __init__(
        self,
        *,
        resource_id: str,
        resource_path: str = 'actor-runs',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_id=resource_id,
            resource_path=resource_path,
            **kwargs,
        )

    async def get(self) -> Run | None:
        """Return information about the Actor run.

        https://docs.apify.com/api/v2#/reference/actor-runs/run-object/get-run

        Returns:
            The retrieved Actor run data.
        """
        try:
            response = await self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(),
            )
            result = response_to_dict(response)
            return GetRunResponse.model_validate(result).data
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            return None

    async def update(
        self,
        *,
        status_message: str | None = None,
        is_status_message_terminal: bool | None = None,
        general_access: GeneralAccessEnum | None = None,
    ) -> Run:
        """Update the run with the specified fields.

        https://docs.apify.com/api/v2#/reference/actor-runs/run-object/update-run

        Args:
            status_message: The new status message for the run.
            is_status_message_terminal: Set this flag to True if this is the final status message of the Actor run.
            general_access: Determines how others can access the run and its storages.

        Returns:
            The updated run.
        """
        updated_fields = {
            'statusMessage': status_message,
            'isStatusMessageTerminal': is_status_message_terminal,
            'generalAccess': general_access,
        }
        cleaned = filter_none_values(updated_fields)

        response = await self._http_client.call(
            url=self._build_url(),
            method='PUT',
            params=self._build_params(),
            json=cleaned,
        )
        result = response_to_dict(response)
        return GetRunResponse.model_validate(result).data

    async def abort(self, *, gracefully: bool | None = None) -> Run:
        """Abort the Actor run which is starting or currently running and return its details.

        https://docs.apify.com/api/v2#/reference/actor-runs/abort-run/abort-run

        Args:
            gracefully: If True, the Actor run will abort gracefully. It will send `aborting` and `persistStates`
                events into the run and force-stop the run after 30 seconds. It is helpful in cases where you plan
                to resurrect the run later.

        Returns:
            The data of the aborted Actor run.
        """
        response = await self._http_client.call(
            url=self._build_url('abort'),
            method='POST',
            params=self._build_params(gracefully=gracefully),
        )
        result = response_to_dict(response)
        return GetRunResponse.model_validate(result).data

    async def wait_for_finish(self, *, wait_duration: timedelta | None = None) -> Run | None:
        """Wait asynchronously until the run finishes or the server times out.

        Args:
            wait_duration: How long does the client wait for run to finish. None for indefinite.

        Returns:
            The Actor run data. If the status on the object is not one of the terminal statuses (SUCCEEDED, FAILED,
                TIMED_OUT, ABORTED), then the run has not yet finished.
        """
        response = await self._wait_for_finish(
            url=self._build_url(),
            params=self._build_params(),
            wait_duration=wait_duration,
        )
        return Run.model_validate(response) if response is not None else None

    async def delete(self) -> None:
        """Delete the run.

        https://docs.apify.com/api/v2#/reference/actor-runs/delete-run/delete-run
        """
        try:
            await self._http_client.call(
                url=self._build_url(),
                method='DELETE',
                params=self._build_params(),
            )
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

    async def metamorph(
        self,
        *,
        target_actor_id: str,
        target_actor_build: str | None = None,
        run_input: Any = None,
        content_type: str | None = None,
    ) -> Run:
        """Transform an Actor run into a run of another Actor with a new input.

        https://docs.apify.com/api/v2#/reference/actor-runs/metamorph-run/metamorph-run

        Args:
            target_actor_id: ID of the target Actor that the run should be transformed into.
            target_actor_build: The build of the target Actor. It can be either a build tag or build number.
                By default, the run uses the build specified in the default run configuration for the target Actor
                (typically the latest build).
            run_input: The input to pass to the new run.
            content_type: The content type of the input.

        Returns:
            The Actor run data.
        """
        run_input, content_type = encode_key_value_store_record_value(run_input, content_type)

        safe_target_actor_id = to_safe_id(target_actor_id)

        request_params = self._build_params(
            targetActorId=safe_target_actor_id,
            build=target_actor_build,
        )

        response = await self._http_client.call(
            url=self._build_url('metamorph'),
            method='POST',
            headers={'content-type': content_type},
            data=run_input,
            params=request_params,
        )

        response_as_dict = response_to_dict(response)
        return GetRunResponse.model_validate(response_as_dict).data

    async def resurrect(
        self,
        *,
        build: str | None = None,
        memory_mbytes: int | None = None,
        timeout: timedelta | None = None,
        max_items: int | None = None,
        max_total_charge_usd: Decimal | None = None,
        restart_on_error: bool | None = None,
    ) -> Run:
        """Resurrect a finished Actor run.

        Only finished runs, i.e. runs with status FINISHED, FAILED, ABORTED and TIMED-OUT can be resurrected.
        Run status will be updated to RUNNING and its container will be restarted with the same default storages.

        https://docs.apify.com/api/v2#/reference/actor-runs/resurrect-run/resurrect-run

        Args:
            build: Which Actor build the resurrected run should use. It can be either a build tag or build number.
                By default, the resurrected run uses the same build as before.
            memory_mbytes: New memory limit for the resurrected run, in megabytes. By default, the resurrected run
                uses the same memory limit as before.
            timeout: New timeout for the resurrected run. By default, the resurrected run uses the
                same timeout as before.
            max_items: Maximum number of items that the resurrected pay-per-result run will return. By default, the
                resurrected run uses the same limit as before. Limit can be only increased.
            max_total_charge_usd: Maximum cost for the resurrected pay-per-event run in USD. By default, the
                resurrected run uses the same limit as before. Limit can be only increased.
            restart_on_error: Determines whether the resurrected run will be restarted if it fails.
                By default, the resurrected run uses the same setting as before.

        Returns:
            The Actor run data.
        """
        request_params = self._build_params(
            build=build,
            memory=memory_mbytes,
            timeout=to_seconds(timeout, as_int=True),
            maxItems=max_items,
            maxTotalChargeUsd=max_total_charge_usd,
            restartOnError=restart_on_error,
        )

        response = await self._http_client.call(
            url=self._build_url('resurrect'),
            method='POST',
            params=request_params,
        )

        response_as_dict = response_to_dict(response)
        return GetRunResponse.model_validate(response_as_dict).data

    async def reboot(self) -> Run:
        """Reboot an Actor run. Only runs that are running, i.e. runs with status RUNNING can be rebooted.

        https://docs.apify.com/api/v2#/reference/actor-runs/reboot-run/reboot-run

        Returns:
            The Actor run data.
        """
        response = await self._http_client.call(
            url=self._build_url('reboot'),
            method='POST',
        )
        response_as_dict = response_to_dict(response)
        return GetRunResponse.model_validate(response_as_dict).data

    def dataset(self) -> DatasetClientAsync:
        """Get the client for the default dataset of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            A client allowing access to the default dataset of this Actor run.
        """
        return self._client_registry.dataset_client(
            resource_path='dataset',
            **self._base_client_kwargs,
        )

    def key_value_store(self) -> KeyValueStoreClientAsync:
        """Get the client for the default key-value store of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            A client allowing access to the default key-value store of this Actor run.
        """
        return self._client_registry.key_value_store_client(
            resource_path='key-value-store',
            **self._base_client_kwargs,
        )

    def request_queue(self) -> RequestQueueClientAsync:
        """Get the client for the default request queue of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            A client allowing access to the default request_queue of this Actor run.
        """
        return self._client_registry.request_queue_client(
            resource_path='request-queue',
            **self._base_client_kwargs,
        )

    def log(self) -> LogClientAsync:
        """Get the client for the log of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            A client allowing access to the log of this Actor run.
        """
        return self._client_registry.log_client(
            resource_path='log',
            **self._base_client_kwargs,
        )

    async def get_streamed_log(
        self, to_logger: logging.Logger | None = None, *, from_start: bool = True
    ) -> StreamedLogAsync:
        """Get `StreamedLog` instance that can be used to redirect logs.

         `StreamedLog` can be explicitly started and stopped or used as a context manager.

        Args:
            to_logger: `Logger` used for logging the redirected messages. If not provided, a new logger is created
            from_start: If `True`, all logs from the start of the Actor run will be redirected. If `False`, only newly
                arrived logs will be redirected. This can be useful for redirecting only a small portion of relevant
                logs for long-running Actors in stand-by.

        Returns:
            `StreamedLog` instance for redirected logs.
        """
        run_data = await self.get()
        run_id = f'runId:{run_data.id}' if run_data and run_data.id else ''

        actor_id = run_data.act_id if run_data else ''
        actor_data = None
        if actor_id:
            actor_client = self._client_registry.actor_client(
                resource_id=actor_id,
                base_url=self._base_url,
                public_base_url=self._public_base_url,
                http_client=self._http_client,
                client_registry=self._client_registry,
            )
            actor_data = await actor_client.get()
        actor_name = actor_data.name if actor_data else ''

        if not to_logger:
            name = ' '.join(part for part in (actor_name, run_id) if part)
            to_logger = create_redirect_logger(f'apify.{name}')

        return self._client_registry.streamed_log(log_client=self.log(), to_logger=to_logger, from_start=from_start)

    async def charge(
        self,
        event_name: str,
        count: int | None = None,
        idempotency_key: str | None = None,
    ) -> None:
        """Charge for an event of a Pay-Per-Event Actor run.

        https://docs.apify.com/api/v2#/reference/actor-runs/charge-events-in-run

        Args:
            event_name: The name of the event to charge for.
            count: The number of events to charge. Defaults to 1 if not provided.
            idempotency_key: A unique key to ensure idempotent charging. If not provided,
                one will be auto-generated.

        Raises:
            ValueError: If event_name is empty or not provided.
        """
        if not event_name:
            raise ValueError('event_name is required for charging an event')

        if idempotency_key is None:
            random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            timestamp_ms = int(time.time() * 1000)
            idempotency_key = f'{self._resource_id}-{event_name}-{timestamp_ms}-{random_suffix}'

        await self._http_client.call(
            url=self._build_url('charge'),
            method='POST',
            headers={
                'idempotency-key': idempotency_key,
                'content-type': 'application/json',
            },
            data=json.dumps(
                {
                    'eventName': event_name,
                    'count': count or 1,
                }
            ),
        )

    async def get_status_message_watcher(
        self,
        to_logger: logging.Logger | None = None,
        check_period: timedelta = timedelta(seconds=1),
    ) -> StatusMessageWatcherAsync:
        """Get `StatusMessageWatcher` instance that can be used to redirect status and status messages to logs.

        `StatusMessageWatcher` can be explicitly started and stopped or used as a context manager.

        Args:
            to_logger: `Logger` used for logging the status and status messages. If not provided, a new logger is
            created.
            check_period: The period with which the status message will be polled.

        Returns:
            `StatusMessageWatcher` instance.
        """
        run_data = await self.get()

        run_id = f'runId:{run_data.id}' if run_data and run_data.id else ''

        actor_id = run_data.act_id if run_data else ''
        actor_data = None
        if actor_id:
            actor_client = self._client_registry.actor_client(
                resource_id=actor_id,
                base_url=self._base_url,
                public_base_url=self._public_base_url,
                http_client=self._http_client,
                client_registry=self._client_registry,
            )
            actor_data = await actor_client.get()
        actor_name = actor_data.name if actor_data else ''

        if not to_logger:
            name = ' '.join(part for part in (actor_name, run_id) if part)
            to_logger = create_redirect_logger(f'apify.{name}')

        return self._client_registry.status_message_watcher(
            run_client=self, to_logger=to_logger, check_period=check_period
        )

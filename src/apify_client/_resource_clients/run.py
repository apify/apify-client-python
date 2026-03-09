from __future__ import annotations

import json
import random
import string
import time
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._logging import create_redirect_logger
from apify_client._models import Run, RunResponse
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._status_message_watcher import StatusMessageWatcher, StatusMessageWatcherAsync
from apify_client._streamed_log import StreamedLog, StreamedLogAsync
from apify_client._utils import (
    encode_key_value_store_record_value,
    response_to_dict,
    to_safe_id,
    to_seconds,
)

if TYPE_CHECKING:
    import logging
    from decimal import Decimal

    from apify_client._models import GeneralAccess
    from apify_client._resource_clients import (
        DatasetClient,
        DatasetClientAsync,
        KeyValueStoreClient,
        KeyValueStoreClientAsync,
        LogClient,
        LogClientAsync,
        RequestQueueClient,
        RequestQueueClientAsync,
    )
    from apify_client._types import Timeout


@docs_group('Resource clients')
class RunClient(ResourceClient):
    """Sub-client for managing a specific Actor run.

    Provides methods to manage a specific Actor run, e.g. get it, update it, abort it, or wait for it to finish.
    Obtain an instance via an appropriate method on the `ApifyClient` class.
    """

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

    def get(self, *, timeout: Timeout = 'long') -> Run | None:
        """Return information about the Actor run.

        https://docs.apify.com/api/v2#/reference/actor-runs/run-object/get-run

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved Actor run data.
        """
        result = self._get(timeout=timeout)
        if result is None:
            return None
        return RunResponse.model_validate(result).data

    def update(
        self,
        *,
        status_message: str | None = None,
        is_status_message_terminal: bool | None = None,
        general_access: GeneralAccess | None = None,
        timeout: Timeout = 'long',
    ) -> Run:
        """Update the run with the specified fields.

        https://docs.apify.com/api/v2#/reference/actor-runs/run-object/update-run

        Args:
            status_message: The new status message for the run.
            is_status_message_terminal: Set this flag to True if this is the final status message of the Actor run.
            general_access: Determines how others can access the run and its storages.
            timeout: Timeout for the API HTTP request.

        Returns:
            The updated run.
        """
        result = self._update(
            timeout=timeout,
            statusMessage=status_message,
            isStatusMessageTerminal=is_status_message_terminal,
            generalAccess=general_access,
        )
        return RunResponse.model_validate(result).data

    def delete(self, *, timeout: Timeout = 'long') -> None:
        """Delete the run.

        https://docs.apify.com/api/v2#/reference/actor-runs/delete-run/delete-run

        Args:
            timeout: Timeout for the API HTTP request.
        """
        self._delete(timeout=timeout)

    def abort(self, *, gracefully: bool | None = None, timeout: Timeout = 'long') -> Run:
        """Abort the Actor run which is starting or currently running and return its details.

        https://docs.apify.com/api/v2#/reference/actor-runs/abort-run/abort-run

        Args:
            gracefully: If True, the Actor run will abort gracefully. It will send `aborting` and `persistStates`
                events into the run and force-stop the run after 30 seconds. It is helpful in cases where you plan
                to resurrect the run later.
            timeout: Timeout for the API HTTP request.

        Returns:
            The data of the aborted Actor run.
        """
        response = self._http_client.call(
            url=self._build_url('abort'),
            method='POST',
            params=self._build_params(gracefully=gracefully),
            timeout=timeout,
        )
        result = response_to_dict(response)
        return RunResponse.model_validate(result).data

    def wait_for_finish(
        self,
        *,
        wait_duration: timedelta | None = None,
        timeout: Timeout = 'no_timeout',
    ) -> Run | None:
        """Wait synchronously until the run finishes or the server times out.

        Args:
            wait_duration: How long does the client wait for run to finish. None for indefinite.
            timeout: Timeout for the API HTTP request.

        Returns:
            The Actor run data. If the status on the object is not one of the terminal statuses (SUCCEEDED, FAILED,
                TIMED_OUT, ABORTED), then the run has not yet finished.
        """
        response = self._wait_for_finish(
            url=self._build_url(),
            params=self._build_params(),
            wait_duration=wait_duration,
            timeout=timeout,
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
        timeout: Timeout = 'long',
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
            timeout: Timeout for the API HTTP request.

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
            timeout=timeout,
        )

        result = response_to_dict(response)
        return RunResponse.model_validate(result).data

    def resurrect(
        self,
        *,
        build: str | None = None,
        memory_mbytes: int | None = None,
        run_timeout: timedelta | None = None,
        max_items: int | None = None,
        max_total_charge_usd: Decimal | None = None,
        restart_on_error: bool | None = None,
        timeout: Timeout = 'long',
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
            run_timeout: New timeout for the resurrected run. By default, the resurrected run uses the
                same timeout as before.
            max_items: Maximum number of items that the resurrected pay-per-result run will return. By default, the
                resurrected run uses the same limit as before. Limit can be only increased.
            max_total_charge_usd: Maximum cost for the resurrected pay-per-event run in USD. By default, the
                resurrected run uses the same limit as before. Limit can be only increased.
            restart_on_error: Determines whether the resurrected run will be restarted if it fails.
                By default, the resurrected run uses the same setting as before.
            timeout: Timeout for the API HTTP request.

        Returns:
            The Actor run data.
        """
        request_params = self._build_params(
            build=build,
            memory=memory_mbytes,
            timeout=to_seconds(run_timeout, as_int=True),
            maxItems=max_items,
            maxTotalChargeUsd=max_total_charge_usd,
            restartOnError=restart_on_error,
        )

        response = self._http_client.call(
            url=self._build_url('resurrect'),
            method='POST',
            params=request_params,
            timeout=timeout,
        )

        result = response_to_dict(response)
        return RunResponse.model_validate(result).data

    def reboot(self, *, timeout: Timeout = 'long') -> Run:
        """Reboot an Actor run. Only runs that are running, i.e. runs with status RUNNING can be rebooted.

        https://docs.apify.com/api/v2#/reference/actor-runs/reboot-run/reboot-run

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The Actor run data.
        """
        response = self._http_client.call(
            url=self._build_url('reboot'),
            method='POST',
            timeout=timeout,
        )
        result = response_to_dict(response)
        return RunResponse.model_validate(result).data

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

    def get_streamed_log(
        self,
        to_logger: logging.Logger | None = None,
        *,
        from_start: bool = True,
        timeout: Timeout = 'long',
    ) -> StreamedLog:
        """Get `StreamedLog` instance that can be used to redirect logs.

         `StreamedLog` can be explicitly started and stopped or used as a context manager.

        Args:
            to_logger: `Logger` used for logging the redirected messages. If not provided, a new logger is created
            from_start: If `True`, all logs from the start of the Actor run will be redirected. If `False`, only newly
                arrived logs will be redirected. This can be useful for redirecting only a small portion of relevant
                logs for long-running Actors in stand-by.
            timeout: Timeout for the API HTTP request.

        Returns:
            `StreamedLog` instance for redirected logs.
        """
        run_data = self.get(timeout=timeout)
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
            actor_data = actor_client.get(timeout=timeout)
        actor_name = actor_data.name if actor_data else ''

        if not to_logger:
            name = ' '.join(part for part in (actor_name, run_id) if part)
            to_logger = create_redirect_logger(f'apify.{name}')

        return StreamedLog(log_client=self.log(), to_logger=to_logger, from_start=from_start)

    def charge(
        self,
        event_name: str,
        count: int | None = None,
        idempotency_key: str | None = None,
        timeout: Timeout = 'long',
    ) -> None:
        """Charge for an event of a Pay-Per-Event Actor run.

        https://docs.apify.com/api/v2#/reference/actor-runs/charge-events-in-run

        Args:
            event_name: The name of the event to charge for.
            count: The number of events to charge. Defaults to 1 if not provided.
            idempotency_key: A unique key to ensure idempotent charging. If not provided,
                one will be auto-generated.
            timeout: Timeout for the API HTTP request.

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
            timeout=timeout,
        )

    def get_status_message_watcher(
        self,
        to_logger: logging.Logger | None = None,
        check_period: timedelta = timedelta(seconds=1),
        *,
        timeout: Timeout = 'long',
    ) -> StatusMessageWatcher:
        """Get `StatusMessageWatcher` instance that can be used to redirect status and status messages to logs.

        `StatusMessageWatcher` can be explicitly started and stopped or used as a context manager.

        Args:
            to_logger: `Logger` used for logging the status and status messages. If not provided, a new logger is
            created.
            check_period: The period with which the status message will be polled.
            timeout: Timeout for the API HTTP request.

        Returns:
            `StatusMessageWatcher` instance.
        """
        run_data = self.get(timeout=timeout)
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
            actor_data = actor_client.get(timeout=timeout)
        actor_name = actor_data.name if actor_data else ''

        if not to_logger:
            name = ' '.join(part for part in (actor_name, run_id) if part)
            to_logger = create_redirect_logger(f'apify.{name}')

        return StatusMessageWatcher(run_client=self, to_logger=to_logger, check_period=check_period)


@docs_group('Resource clients')
class RunClientAsync(ResourceClientAsync):
    """Sub-client for managing a specific Actor run.

    Provides methods to manage a specific Actor run, e.g. get it, update it, abort it, or wait for it to finish.
    Obtain an instance via an appropriate method on the `ApifyClientAsync` class.
    """

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

    async def get(self, *, timeout: Timeout = 'long') -> Run | None:
        """Return information about the Actor run.

        https://docs.apify.com/api/v2#/reference/actor-runs/run-object/get-run

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved Actor run data.
        """
        result = await self._get(timeout=timeout)
        if result is None:
            return None
        return RunResponse.model_validate(result).data

    async def update(
        self,
        *,
        status_message: str | None = None,
        is_status_message_terminal: bool | None = None,
        general_access: GeneralAccess | None = None,
        timeout: Timeout = 'long',
    ) -> Run:
        """Update the run with the specified fields.

        https://docs.apify.com/api/v2#/reference/actor-runs/run-object/update-run

        Args:
            status_message: The new status message for the run.
            is_status_message_terminal: Set this flag to True if this is the final status message of the Actor run.
            general_access: Determines how others can access the run and its storages.
            timeout: Timeout for the API HTTP request.

        Returns:
            The updated run.
        """
        result = await self._update(
            timeout=timeout,
            statusMessage=status_message,
            isStatusMessageTerminal=is_status_message_terminal,
            generalAccess=general_access,
        )
        return RunResponse.model_validate(result).data

    async def abort(self, *, gracefully: bool | None = None, timeout: Timeout = 'long') -> Run:
        """Abort the Actor run which is starting or currently running and return its details.

        https://docs.apify.com/api/v2#/reference/actor-runs/abort-run/abort-run

        Args:
            gracefully: If True, the Actor run will abort gracefully. It will send `aborting` and `persistStates`
                events into the run and force-stop the run after 30 seconds. It is helpful in cases where you plan
                to resurrect the run later.
            timeout: Timeout for the API HTTP request.

        Returns:
            The data of the aborted Actor run.
        """
        response = await self._http_client.call(
            url=self._build_url('abort'),
            method='POST',
            params=self._build_params(gracefully=gracefully),
            timeout=timeout,
        )
        result = response_to_dict(response)
        return RunResponse.model_validate(result).data

    async def wait_for_finish(
        self,
        *,
        wait_duration: timedelta | None = None,
        timeout: Timeout = 'no_timeout',
    ) -> Run | None:
        """Wait asynchronously until the run finishes or the server times out.

        Args:
            wait_duration: How long does the client wait for run to finish. None for indefinite.
            timeout: Timeout for the API HTTP request.

        Returns:
            The Actor run data. If the status on the object is not one of the terminal statuses (SUCCEEDED, FAILED,
                TIMED_OUT, ABORTED), then the run has not yet finished.
        """
        response = await self._wait_for_finish(
            url=self._build_url(),
            params=self._build_params(),
            wait_duration=wait_duration,
            timeout=timeout,
        )
        return Run.model_validate(response) if response is not None else None

    async def delete(self, *, timeout: Timeout = 'long') -> None:
        """Delete the run.

        https://docs.apify.com/api/v2#/reference/actor-runs/delete-run/delete-run

        Args:
            timeout: Timeout for the API HTTP request.
        """
        await self._delete(timeout=timeout)

    async def metamorph(
        self,
        *,
        target_actor_id: str,
        target_actor_build: str | None = None,
        run_input: Any = None,
        content_type: str | None = None,
        timeout: Timeout = 'long',
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
            timeout: Timeout for the API HTTP request.

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
            timeout=timeout,
        )

        result = response_to_dict(response)
        return RunResponse.model_validate(result).data

    async def resurrect(
        self,
        *,
        build: str | None = None,
        memory_mbytes: int | None = None,
        run_timeout: timedelta | None = None,
        max_items: int | None = None,
        max_total_charge_usd: Decimal | None = None,
        restart_on_error: bool | None = None,
        timeout: Timeout = 'long',
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
            run_timeout: New timeout for the resurrected run. By default, the resurrected run uses the
                same timeout as before.
            max_items: Maximum number of items that the resurrected pay-per-result run will return. By default, the
                resurrected run uses the same limit as before. Limit can be only increased.
            max_total_charge_usd: Maximum cost for the resurrected pay-per-event run in USD. By default, the
                resurrected run uses the same limit as before. Limit can be only increased.
            restart_on_error: Determines whether the resurrected run will be restarted if it fails.
                By default, the resurrected run uses the same setting as before.
            timeout: Timeout for the API HTTP request.

        Returns:
            The Actor run data.
        """
        request_params = self._build_params(
            build=build,
            memory=memory_mbytes,
            timeout=to_seconds(run_timeout, as_int=True),
            maxItems=max_items,
            maxTotalChargeUsd=max_total_charge_usd,
            restartOnError=restart_on_error,
        )

        response = await self._http_client.call(
            url=self._build_url('resurrect'),
            method='POST',
            params=request_params,
            timeout=timeout,
        )

        result = response_to_dict(response)
        return RunResponse.model_validate(result).data

    async def reboot(self, *, timeout: Timeout = 'long') -> Run:
        """Reboot an Actor run. Only runs that are running, i.e. runs with status RUNNING can be rebooted.

        https://docs.apify.com/api/v2#/reference/actor-runs/reboot-run/reboot-run

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The Actor run data.
        """
        response = await self._http_client.call(
            url=self._build_url('reboot'),
            method='POST',
            timeout=timeout,
        )
        result = response_to_dict(response)
        return RunResponse.model_validate(result).data

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
        self,
        to_logger: logging.Logger | None = None,
        *,
        from_start: bool = True,
        timeout: Timeout = 'long',
    ) -> StreamedLogAsync:
        """Get `StreamedLog` instance that can be used to redirect logs.

         `StreamedLog` can be explicitly started and stopped or used as a context manager.

        Args:
            to_logger: `Logger` used for logging the redirected messages. If not provided, a new logger is created
            from_start: If `True`, all logs from the start of the Actor run will be redirected. If `False`, only newly
                arrived logs will be redirected. This can be useful for redirecting only a small portion of relevant
                logs for long-running Actors in stand-by.
            timeout: Timeout for the API HTTP request.

        Returns:
            `StreamedLog` instance for redirected logs.
        """
        run_data = await self.get(timeout=timeout)
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
            actor_data = await actor_client.get(timeout=timeout)
        actor_name = actor_data.name if actor_data else ''

        if not to_logger:
            name = ' '.join(part for part in (actor_name, run_id) if part)
            to_logger = create_redirect_logger(f'apify.{name}')

        return StreamedLogAsync(log_client=self.log(), to_logger=to_logger, from_start=from_start)

    async def charge(
        self,
        event_name: str,
        count: int | None = None,
        idempotency_key: str | None = None,
        timeout: Timeout = 'long',
    ) -> None:
        """Charge for an event of a Pay-Per-Event Actor run.

        https://docs.apify.com/api/v2#/reference/actor-runs/charge-events-in-run

        Args:
            event_name: The name of the event to charge for.
            count: The number of events to charge. Defaults to 1 if not provided.
            idempotency_key: A unique key to ensure idempotent charging. If not provided,
                one will be auto-generated.
            timeout: Timeout for the API HTTP request.

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
            timeout=timeout,
        )

    async def get_status_message_watcher(
        self,
        to_logger: logging.Logger | None = None,
        check_period: timedelta = timedelta(seconds=1),
        *,
        timeout: Timeout = 'long',
    ) -> StatusMessageWatcherAsync:
        """Get `StatusMessageWatcher` instance that can be used to redirect status and status messages to logs.

        `StatusMessageWatcher` can be explicitly started and stopped or used as a context manager.

        Args:
            to_logger: `Logger` used for logging the status and status messages. If not provided, a new logger is
            created.
            check_period: The period with which the status message will be polled.
            timeout: Timeout for the API HTTP request.

        Returns:
            `StatusMessageWatcher` instance.
        """
        run_data = await self.get(timeout=timeout)

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
            actor_data = await actor_client.get(timeout=timeout)
        actor_name = actor_data.name if actor_data else ''

        if not to_logger:
            name = ' '.join(part for part in (actor_name, run_id) if part)
            to_logger = create_redirect_logger(f'apify.{name}')

        return StatusMessageWatcherAsync(run_client=self, to_logger=to_logger, check_period=check_period)

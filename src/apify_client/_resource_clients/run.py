from __future__ import annotations

import json
import random
import string
import time
from datetime import timedelta
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import logging
    from decimal import Decimal

    from apify_client._consts import RunGeneralAccess
    from apify_client._resource_clients.log import (
        LogClient,
        LogClientAsync,
        StatusMessageWatcherAsync,
        StatusMessageWatcherSync,
        StreamedLogAsync,
        StreamedLogSync,
    )


from apify_client._logging import create_redirect_logger
from apify_client._models import GetRunResponse, Run
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._resource_clients.dataset import DatasetClient, DatasetClientAsync
from apify_client._resource_clients.key_value_store import KeyValueStoreClient, KeyValueStoreClientAsync
from apify_client._resource_clients.request_queue import RequestQueueClient, RequestQueueClientAsync
from apify_client._utils import (
    catch_not_found_or_throw,
    encode_key_value_store_record_value,
    filter_none_values,
    response_to_dict,
    to_safe_id,
    wait_for_finish_async,
    wait_for_finish_sync,
)
from apify_client.errors import ApifyApiError


class RunClient(ResourceClient):
    """Sub-client for manipulating a single Actor run."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'actor-runs')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> Run | None:
        """Return information about the Actor run.

        https://docs.apify.com/api/v2#/reference/actor-runs/run-object/get-run

        Returns:
            The retrieved Actor run data.
        """
        try:
            response = self.http_client.call(
                url=self.url,
                method='GET',
                params=self.params,
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
        general_access: RunGeneralAccess | None = None,
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

        response = self.http_client.call(
            url=self.url,
            method='PUT',
            params=self.params,
            json=cleaned,
        )
        result = response_to_dict(response)
        return GetRunResponse.model_validate(result).data

    def delete(self) -> None:
        """Delete the run.

        https://docs.apify.com/api/v2#/reference/actor-runs/delete-run/delete-run
        """
        try:
            self.http_client.call(
                url=self.url,
                method='DELETE',
                params=self.params,
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
        response = self.http_client.call(
            url=self._url('abort'),
            method='POST',
            params=self._build_params(gracefully=gracefully),
        )
        result = response_to_dict(response)
        return GetRunResponse.model_validate(result).data

    def wait_for_finish(self, *, wait_secs: int | None = None) -> Run | None:
        """Wait synchronously until the run finishes or the server times out.

        Args:
            wait_secs: How long does the client wait for run to finish. None for indefinite.

        Returns:
            The Actor run data. If the status on the object is not one of the terminal statuses (SUCCEEDED, FAILED,
                TIMED_OUT, ABORTED), then the run has not yet finished.
        """
        response = wait_for_finish_sync(
            http_client=self.http_client,
            url=self.url,
            params=self.params,
            wait_secs=wait_secs,
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

        response = self.http_client.call(
            url=self._url('metamorph'),
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
        timeout_secs: int | None = None,
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
            timeout_secs: New timeout for the resurrected run, in seconds. By default, the resurrected run uses the
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
            timeout=timeout_secs,
            maxItems=max_items,
            maxTotalChargeUsd=max_total_charge_usd,
            restartOnError=restart_on_error,
        )

        response = self.http_client.call(
            url=self._url('resurrect'),
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
        response = self.http_client.call(
            url=self._url('reboot'),
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
        return DatasetClient(
            **self._nested_client_config(resource_path='dataset'),
        )

    def key_value_store(self) -> KeyValueStoreClient:
        """Get the client for the default key-value store of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            A client allowing access to the default key-value store of this Actor run.
        """
        return KeyValueStoreClient(
            **self._nested_client_config(resource_path='key-value-store'),
        )

    def request_queue(self) -> RequestQueueClient:
        """Get the client for the default request queue of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            A client allowing access to the default request_queue of this Actor run.
        """
        return RequestQueueClient(
            **self._nested_client_config(resource_path='request-queue'),
        )

    def log(self) -> LogClient:
        """Get the client for the log of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            A client allowing access to the log of this Actor run.
        """
        # Import inline to avoid circular dependency with log.py
        from apify_client._resource_clients.log import LogClient  # noqa: PLC0415

        return LogClient(
            **self._nested_client_config(resource_path='log'),
        )

    def get_streamed_log(self, to_logger: logging.Logger | None = None, *, from_start: bool = True) -> StreamedLogSync:
        """Get `StreamedLog` instance that can be used to redirect logs.

         `StreamedLog` can be explicitly started and stopped or used as a context manager.

        Args:
            to_logger: `Logger` used for logging the redirected messages. If not provided, a new logger is created
            from_start: If `True`, all logs from the start of the actor run will be redirected. If `False`, only newly
                arrived logs will be redirected. This can be useful for redirecting only a small portion of relevant
                logs for long-running actors in stand-by.

        Returns:
            `StreamedLog` instance for redirected logs.
        """
        run_data = self.get()
        run_id = f'runId:{run_data.id}' if run_data and run_data.id else ''

        actor_id = run_data.act_id if run_data else ''
        actor_data = None
        if actor_id:
            # Import inline to avoid circular dependency: run.py ← actor.py → run.py
            from apify_client._resource_clients.actor import ActorClient  # noqa: PLC0415

            actor_client = self._create_sibling_client(ActorClient, resource_id=actor_id)
            actor_data = actor_client.get()
        actor_name = actor_data.name if actor_data else ''

        if not to_logger:
            name = ' '.join(part for part in (actor_name, run_id) if part)
            to_logger = create_redirect_logger(f'apify.{name}')

        # Import inline to avoid circular dependency with log.py
        from apify_client._resource_clients.log import StreamedLogSync  # noqa: PLC0415

        return StreamedLogSync(log_client=self.log(), to_logger=to_logger, from_start=from_start)

    def charge(
        self,
        event_name: str,
        count: int | None = None,
        idempotency_key: str | None = None,
    ) -> None:
        """Charge for an event of a Pay-Per-Event Actor run.

        https://docs.apify.com/api/v2#/reference/actor-runs/charge-events-in-run

        Returns:
            Status and message of the charge event.
        """
        if not event_name:
            raise ValueError('event_name is required for charging an event')

        idempotency_key = (
            idempotency_key
            or f'{self.resource_id}-{event_name}-{int(time.time() * 1000)}-{"".join(random.choices(string.ascii_letters + string.digits, k=6))}'  # noqa: E501
        )

        self.http_client.call(
            url=self._url('charge'),
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
            # Import inline to avoid circular dependency: run.py ← actor.py → run.py
            from apify_client._resource_clients.actor import ActorClient  # noqa: PLC0415

            actor_client = self._create_sibling_client(ActorClient, resource_id=actor_id)
            actor_data = actor_client.get()
        actor_name = actor_data.name if actor_data else ''

        if not to_logger:
            name = ' '.join(part for part in (actor_name, run_id) if part)
            to_logger = create_redirect_logger(f'apify.{name}')

        # Import inline to avoid circular dependency with log.py
        from apify_client._resource_clients.log import StatusMessageWatcherSync  # noqa: PLC0415

        return StatusMessageWatcherSync(run_client=self, to_logger=to_logger, check_period=check_period)


class RunClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single Actor run."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'actor-runs')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self) -> Run | None:
        """Return information about the Actor run.

        https://docs.apify.com/api/v2#/reference/actor-runs/run-object/get-run

        Returns:
            The retrieved Actor run data.
        """
        try:
            response = await self.http_client.call(
                url=self.url,
                method='GET',
                params=self.params,
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
        general_access: RunGeneralAccess | None = None,
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

        response = await self.http_client.call(
            url=self.url,
            method='PUT',
            params=self.params,
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
        response = await self.http_client.call(
            url=self._url('abort'),
            method='POST',
            params=self._build_params(gracefully=gracefully),
        )
        result = response_to_dict(response)
        return GetRunResponse.model_validate(result).data

    async def wait_for_finish(self, *, wait_secs: int | None = None) -> Run | None:
        """Wait synchronously until the run finishes or the server times out.

        Args:
            wait_secs: How long does the client wait for run to finish. None for indefinite.

        Returns:
            The Actor run data. If the status on the object is not one of the terminal statuses (SUCCEEDED, FAILED,
                TIMED_OUT, ABORTED), then the run has not yet finished.
        """
        response = await wait_for_finish_async(
            http_client=self.http_client,
            url=self.url,
            params=self.params,
            wait_secs=wait_secs,
        )
        return Run.model_validate(response) if response is not None else None

    async def delete(self) -> None:
        """Delete the run.

        https://docs.apify.com/api/v2#/reference/actor-runs/delete-run/delete-run
        """
        try:
            await self.http_client.call(
                url=self.url,
                method='DELETE',
                params=self.params,
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

        response = await self.http_client.call(
            url=self._url('metamorph'),
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
        timeout_secs: int | None = None,
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
            timeout_secs: New timeout for the resurrected run, in seconds. By default, the resurrected run uses the
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
            timeout=timeout_secs,
            maxItems=max_items,
            maxTotalChargeUsd=max_total_charge_usd,
            restartOnError=restart_on_error,
        )

        response = await self.http_client.call(
            url=self._url('resurrect'),
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
        response = await self.http_client.call(
            url=self._url('reboot'),
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
        return DatasetClientAsync(
            **self._nested_client_config(resource_path='dataset'),
        )

    def key_value_store(self) -> KeyValueStoreClientAsync:
        """Get the client for the default key-value store of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            A client allowing access to the default key-value store of this Actor run.
        """
        return KeyValueStoreClientAsync(
            **self._nested_client_config(resource_path='key-value-store'),
        )

    def request_queue(self) -> RequestQueueClientAsync:
        """Get the client for the default request queue of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            A client allowing access to the default request_queue of this Actor run.
        """
        return RequestQueueClientAsync(
            **self._nested_client_config(resource_path='request-queue'),
        )

    def log(self) -> LogClientAsync:
        """Get the client for the log of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            A client allowing access to the log of this Actor run.
        """
        # Import inline to avoid circular dependency with log.py
        from apify_client._resource_clients.log import LogClientAsync  # noqa: PLC0415

        return LogClientAsync(
            **self._nested_client_config(resource_path='log'),
        )

    async def get_streamed_log(
        self, to_logger: logging.Logger | None = None, *, from_start: bool = True
    ) -> StreamedLogAsync:
        """Get `StreamedLog` instance that can be used to redirect logs.

         `StreamedLog` can be explicitly started and stopped or used as a context manager.

        Args:
            to_logger: `Logger` used for logging the redirected messages. If not provided, a new logger is created
            from_start: If `True`, all logs from the start of the actor run will be redirected. If `False`, only newly
                arrived logs will be redirected. This can be useful for redirecting only a small portion of relevant
                logs for long-running actors in stand-by.

        Returns:
            `StreamedLog` instance for redirected logs.
        """
        run_data = await self.get()
        run_id = f'runId:{run_data.id}' if run_data and run_data.id else ''

        actor_id = run_data.act_id if run_data else ''
        actor_data = None
        if actor_id:
            # Import inline to avoid circular dependency: run.py ← actor.py → run.py
            from apify_client._resource_clients.actor import ActorClientAsync  # noqa: PLC0415

            actor_client = self._create_sibling_client(ActorClientAsync, resource_id=actor_id)
            actor_data = await actor_client.get()
        actor_name = actor_data.name if actor_data else ''

        if not to_logger:
            name = ' '.join(part for part in (actor_name, run_id) if part)
            to_logger = create_redirect_logger(f'apify.{name}')

        # Import inline to avoid circular dependency with log.py
        from apify_client._resource_clients.log import StreamedLogAsync  # noqa: PLC0415

        return StreamedLogAsync(log_client=self.log(), to_logger=to_logger, from_start=from_start)

    async def charge(
        self,
        event_name: str,
        count: int | None = None,
        idempotency_key: str | None = None,
    ) -> None:
        """Charge for an event of a Pay-Per-Event Actor run.

        https://docs.apify.com/api/v2#/reference/actor-runs/charge-events-in-run

        Returns:
            Status and message of the charge event.
        """
        if not event_name:
            raise ValueError('event_name is required for charging an event')

        idempotency_key = idempotency_key or (
            f'{self.resource_id}-{event_name}-{int(time.time() * 1000)}-{"".join(random.choices(string.ascii_letters + string.digits, k=6))}'  # noqa: E501
        )

        await self.http_client.call(
            url=self._url('charge'),
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
            # Import inline to avoid circular dependency: run.py ← actor.py → run.py
            from apify_client._resource_clients.actor import ActorClientAsync  # noqa: PLC0415

            actor_client = self._create_sibling_client(ActorClientAsync, resource_id=actor_id)
            actor_data = await actor_client.get()
        actor_name = actor_data.name if actor_data else ''

        if not to_logger:
            name = ' '.join(part for part in (actor_name, run_id) if part)
            to_logger = create_redirect_logger(f'apify.{name}')

        # Import inline to avoid circular dependency with log.py
        from apify_client._resource_clients.log import StatusMessageWatcherAsync  # noqa: PLC0415

        return StatusMessageWatcherAsync(run_client=self, to_logger=to_logger, check_period=check_period)

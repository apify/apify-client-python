from __future__ import annotations

import json
import random
import string
import time
from typing import TYPE_CHECKING, Any

from apify_shared.utils import filter_out_none_values_recursively, ignore_docs, parse_date_fields

from apify_client._logging import create_redirect_logger
from apify_client._utils import encode_key_value_store_record_value, pluck_data, to_safe_id
from apify_client.clients.base import ActorJobBaseClient, ActorJobBaseClientAsync
from apify_client.clients.resource_clients.dataset import DatasetClient, DatasetClientAsync
from apify_client.clients.resource_clients.key_value_store import KeyValueStoreClient, KeyValueStoreClientAsync
from apify_client.clients.resource_clients.log import (
    LogClient,
    LogClientAsync,
    StreamedLogAsync,
    StreamedLogSync,
)
from apify_client.clients.resource_clients.request_queue import RequestQueueClient, RequestQueueClientAsync

if TYPE_CHECKING:
    import logging
    from decimal import Decimal

    from apify_shared.consts import RunGeneralAccess


class RunClient(ActorJobBaseClient):
    """Sub-client for manipulating a single Actor run."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'actor-runs')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> dict | None:
        """Return information about the Actor run.

        https://docs.apify.com/api/v2#/reference/actor-runs/run-object/get-run

        Returns:
            The retrieved Actor run data.
        """
        return self._get()

    def update(
        self,
        *,
        status_message: str | None = None,
        is_status_message_terminal: bool | None = None,
        general_access: RunGeneralAccess | None = None,
    ) -> dict:
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

        return self._update(filter_out_none_values_recursively(updated_fields))

    def delete(self) -> None:
        """Delete the run.

        https://docs.apify.com/api/v2#/reference/actor-runs/delete-run/delete-run
        """
        return self._delete()

    def abort(self, *, gracefully: bool | None = None) -> dict:
        """Abort the Actor run which is starting or currently running and return its details.

        https://docs.apify.com/api/v2#/reference/actor-runs/abort-run/abort-run

        Args:
            gracefully: If True, the Actor run will abort gracefully. It will send `aborting` and `persistStates`
                events into the run and force-stop the run after 30 seconds. It is helpful in cases where you plan
                to resurrect the run later.

        Returns:
            The data of the aborted Actor run.
        """
        return self._abort(gracefully=gracefully)

    def wait_for_finish(self, *, wait_secs: int | None = None) -> dict | None:
        """Wait synchronously until the run finishes or the server times out.

        Args:
            wait_secs: How long does the client wait for run to finish. None for indefinite.

        Returns:
            The Actor run data. If the status on the object is not one of the terminal statuses (SUCEEDED, FAILED,
                TIMED_OUT, ABORTED), then the run has not yet finished.
        """
        return self._wait_for_finish(wait_secs=wait_secs)

    def metamorph(
        self,
        *,
        target_actor_id: str,
        target_actor_build: str | None = None,
        run_input: Any = None,
        content_type: str | None = None,
    ) -> dict:
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

        request_params = self._params(targetActorId=safe_target_actor_id, build=target_actor_build)

        response = self.http_client.call(
            url=self._url('metamorph'),
            method='POST',
            headers={'content-type': content_type},
            data=run_input,
            params=request_params,
        )

        return parse_date_fields(pluck_data(response.json()))

    def resurrect(
        self,
        *,
        build: str | None = None,
        memory_mbytes: int | None = None,
        timeout_secs: int | None = None,
        max_items: int | None = None,
        max_total_charge_usd: Decimal | None = None,
    ) -> dict:
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

        Returns:
            The Actor run data.
        """
        request_params = self._params(
            build=build,
            memory=memory_mbytes,
            timeout=timeout_secs,
            maxItems=max_items,
            maxTotalChargeUsd=max_total_charge_usd,
        )

        response = self.http_client.call(
            url=self._url('resurrect'),
            method='POST',
            params=request_params,
        )

        return parse_date_fields(pluck_data(response.json()))

    def reboot(self) -> dict:
        """Reboot an Actor run. Only runs that are running, i.e. runs with status RUNNING can be rebooted.

        https://docs.apify.com/api/v2#/reference/actor-runs/reboot-run/reboot-run

        Returns:
            The Actor run data.
        """
        response = self.http_client.call(
            url=self._url('reboot'),
            method='POST',
        )
        return parse_date_fields(pluck_data(response.json()))

    def dataset(self) -> DatasetClient:
        """Get the client for the default dataset of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            A client allowing access to the default dataset of this Actor run.
        """
        return DatasetClient(
            **self._sub_resource_init_options(resource_path='dataset'),
        )

    def key_value_store(self) -> KeyValueStoreClient:
        """Get the client for the default key-value store of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            A client allowing access to the default key-value store of this Actor run.
        """
        return KeyValueStoreClient(
            **self._sub_resource_init_options(resource_path='key-value-store'),
        )

    def request_queue(self) -> RequestQueueClient:
        """Get the client for the default request queue of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            A client allowing access to the default request_queue of this Actor run.
        """
        return RequestQueueClient(
            **self._sub_resource_init_options(resource_path='request-queue'),
        )

    def log(self) -> LogClient:
        """Get the client for the log of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            A client allowing access to the log of this Actor run.
        """
        return LogClient(
            **self._sub_resource_init_options(resource_path='log'),
        )

    def get_streamed_log(self, to_logger: logging.Logger | None = None, *, from_start: bool = True) -> StreamedLogSync:
        """Get `StreamedLog` instance that can be used to redirect logs.

         `StreamedLog` can be directly called or used as a context manager.

        Args:
            to_logger: `Logger` used for logging the redirected messages. If not provided, a new logger is created
            from_start: If `True`, all logs from the start of the actor run will be redirected. If `False`, only newly
                arrived logs will be redirected. This can be useful for redirecting only a small portion of relevant
                logs for long-running actors in stand-by.

        Returns:
            `StreamedLog` instance for redirected logs.
        """
        run_data = self.get()
        run_id = run_data.get('id', '') if run_data else ''

        actor_id = run_data.get('actId', '') if run_data else ''
        actor_data = self.root_client.actor(actor_id=actor_id).get() or {}
        actor_name = actor_data.get('name', '') if run_data else ''

        if not to_logger:
            name = '-'.join(part for part in (actor_name, run_id) if part)
            to_logger = create_redirect_logger(f'apify.{name}')

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


class RunClientAsync(ActorJobBaseClientAsync):
    """Async sub-client for manipulating a single Actor run."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'actor-runs')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self) -> dict | None:
        """Return information about the Actor run.

        https://docs.apify.com/api/v2#/reference/actor-runs/run-object/get-run

        Returns:
            The retrieved Actor run data.
        """
        return await self._get()

    async def update(
        self,
        *,
        status_message: str | None = None,
        is_status_message_terminal: bool | None = None,
        general_access: RunGeneralAccess | None = None,
    ) -> dict:
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

        return await self._update(filter_out_none_values_recursively(updated_fields))

    async def abort(self, *, gracefully: bool | None = None) -> dict:
        """Abort the Actor run which is starting or currently running and return its details.

        https://docs.apify.com/api/v2#/reference/actor-runs/abort-run/abort-run

        Args:
            gracefully: If True, the Actor run will abort gracefully. It will send `aborting` and `persistStates`
                events into the run and force-stop the run after 30 seconds. It is helpful in cases where you plan
                to resurrect the run later.

        Returns:
            The data of the aborted Actor run.
        """
        return await self._abort(gracefully=gracefully)

    async def wait_for_finish(self, *, wait_secs: int | None = None) -> dict | None:
        """Wait synchronously until the run finishes or the server times out.

        Args:
            wait_secs: How long does the client wait for run to finish. None for indefinite.

        Returns:
            The Actor run data. If the status on the object is not one of the terminal statuses (SUCEEDED, FAILED,
                TIMED_OUT, ABORTED), then the run has not yet finished.
        """
        return await self._wait_for_finish(wait_secs=wait_secs)

    async def delete(self) -> None:
        """Delete the run.

        https://docs.apify.com/api/v2#/reference/actor-runs/delete-run/delete-run
        """
        return await self._delete()

    async def metamorph(
        self,
        *,
        target_actor_id: str,
        target_actor_build: str | None = None,
        run_input: Any = None,
        content_type: str | None = None,
    ) -> dict:
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
        self,
        *,
        build: str | None = None,
        memory_mbytes: int | None = None,
        timeout_secs: int | None = None,
        max_items: int | None = None,
        max_total_charge_usd: Decimal | None = None,
    ) -> dict:
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

        Returns:
            The Actor run data.
        """
        request_params = self._params(
            build=build,
            memory=memory_mbytes,
            timeout=timeout_secs,
            maxItems=max_items,
            maxTotalChargeUsd=max_total_charge_usd,
        )

        response = await self.http_client.call(
            url=self._url('resurrect'),
            method='POST',
            params=request_params,
        )

        return parse_date_fields(pluck_data(response.json()))

    async def reboot(self) -> dict:
        """Reboot an Actor run. Only runs that are running, i.e. runs with status RUNNING can be rebooted.

        https://docs.apify.com/api/v2#/reference/actor-runs/reboot-run/reboot-run

        Returns:
            The Actor run data.
        """
        response = await self.http_client.call(
            url=self._url('reboot'),
            method='POST',
        )
        return parse_date_fields(pluck_data(response.json()))

    def dataset(self) -> DatasetClientAsync:
        """Get the client for the default dataset of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            A client allowing access to the default dataset of this Actor run.
        """
        return DatasetClientAsync(
            **self._sub_resource_init_options(resource_path='dataset'),
        )

    def key_value_store(self) -> KeyValueStoreClientAsync:
        """Get the client for the default key-value store of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            A client allowing access to the default key-value store of this Actor run.
        """
        return KeyValueStoreClientAsync(
            **self._sub_resource_init_options(resource_path='key-value-store'),
        )

    def request_queue(self) -> RequestQueueClientAsync:
        """Get the client for the default request queue of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            A client allowing access to the default request_queue of this Actor run.
        """
        return RequestQueueClientAsync(
            **self._sub_resource_init_options(resource_path='request-queue'),
        )

    def log(self) -> LogClientAsync:
        """Get the client for the log of the Actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            A client allowing access to the log of this Actor run.
        """
        return LogClientAsync(
            **self._sub_resource_init_options(resource_path='log'),
        )

    async def get_streamed_log(
        self, to_logger: logging.Logger | None = None, *, from_start: bool = True
    ) -> StreamedLogAsync:
        """Get `StreamedLog` instance that can be used to redirect logs.

         `StreamedLog` can be directly called or used as a context manager.

        Args:
            to_logger: `Logger` used for logging the redirected messages. If not provided, a new logger is created
            from_start: If `True`, all logs from the start of the actor run will be redirected. If `False`, only newly
                arrived logs will be redirected. This can be useful for redirecting only a small portion of relevant
                logs for long-running actors in stand-by.

        Returns:
            `StreamedLog` instance for redirected logs.
        """
        run_data = await self.get()
        run_id = run_data.get('id', '') if run_data else ''

        actor_id = run_data.get('actId', '') if run_data else ''
        actor_data = await self.root_client.actor(actor_id=actor_id).get() or {}
        actor_name = actor_data.get('name', '') if run_data else ''

        if not to_logger:
            name = '-'.join(part for part in (actor_name, run_id) if part)
            to_logger = create_redirect_logger(f'apify.{name}')

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

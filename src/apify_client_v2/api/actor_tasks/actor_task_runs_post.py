from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.actor_task_runs_post_body import ActorTaskRunsPostBody
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    actor_task_id: str,
    *,
    body: ActorTaskRunsPostBody,
    timeout: float | Unset = UNSET,
    memory: float | Unset = UNSET,
    max_items: float | Unset = UNSET,
    max_total_charge_usd: float | Unset = UNSET,
    restart_on_error: bool | Unset = UNSET,
    build: str | Unset = UNSET,
    wait_for_finish: float | Unset = UNSET,
    webhooks: str | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    params: dict[str, Any] = {}

    params["timeout"] = timeout

    params["memory"] = memory

    params["maxItems"] = max_items

    params["maxTotalChargeUsd"] = max_total_charge_usd

    params["restartOnError"] = restart_on_error

    params["build"] = build

    params["waitForFinish"] = wait_for_finish

    params["webhooks"] = webhooks


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v2/actor-tasks/{actor_task_id}/runs".format(actor_task_id=actor_task_id,),
        "params": params,
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | None:
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    actor_task_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ActorTaskRunsPostBody,
    timeout: float | Unset = UNSET,
    memory: float | Unset = UNSET,
    max_items: float | Unset = UNSET,
    max_total_charge_usd: float | Unset = UNSET,
    restart_on_error: bool | Unset = UNSET,
    build: str | Unset = UNSET,
    wait_for_finish: float | Unset = UNSET,
    webhooks: str | Unset = UNSET,

) -> Response[Any]:
    """ Run task

     Runs an Actor task and immediately returns without waiting for the run to
    finish.

    Optionally, you can override the Actor input configuration by passing a JSON
    object as the POST payload and setting the `Content-Type: application/json` HTTP header.

    Note that if the object in the POST payload does not define a particular
    input property, the Actor run uses the default value defined by the task (or Actor's input
    schema if not defined by the task).

    The response is the Actor Run object as returned by the [Get
    run](#/reference/actor-runs/run-object-and-its-storages/get-run) endpoint.

    If you want to wait for the run to finish and receive the actual output of
    the Actor run as the response, use one of the [Run task
    synchronously](#/reference/actor-tasks/run-task-synchronously) API endpoints
    instead.

    To fetch the Actor run results that are typically stored in the default
    dataset, you'll need to pass the ID received in the `defaultDatasetId` field
    received in the response JSON to the
    [Get items](#/reference/datasets/item-collection/get-items) API endpoint.

    Args:
        actor_task_id (str):  Example: janedoe~my-task.
        timeout (float | Unset):  Example: 60.
        memory (float | Unset):  Example: 256.
        max_items (float | Unset):  Example: 1000.
        max_total_charge_usd (float | Unset):  Example: 5.
        restart_on_error (bool | Unset):
        build (str | Unset):  Example: 0.1.234.
        wait_for_finish (float | Unset):  Example: 60.
        webhooks (str | Unset):  Example: dGhpcyBpcyBqdXN0IGV4YW1wbGUK....
        body (ActorTaskRunsPostBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        actor_task_id=actor_task_id,
body=body,
timeout=timeout,
memory=memory,
max_items=max_items,
max_total_charge_usd=max_total_charge_usd,
restart_on_error=restart_on_error,
build=build,
wait_for_finish=wait_for_finish,
webhooks=webhooks,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    actor_task_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ActorTaskRunsPostBody,
    timeout: float | Unset = UNSET,
    memory: float | Unset = UNSET,
    max_items: float | Unset = UNSET,
    max_total_charge_usd: float | Unset = UNSET,
    restart_on_error: bool | Unset = UNSET,
    build: str | Unset = UNSET,
    wait_for_finish: float | Unset = UNSET,
    webhooks: str | Unset = UNSET,

) -> Response[Any]:
    """ Run task

     Runs an Actor task and immediately returns without waiting for the run to
    finish.

    Optionally, you can override the Actor input configuration by passing a JSON
    object as the POST payload and setting the `Content-Type: application/json` HTTP header.

    Note that if the object in the POST payload does not define a particular
    input property, the Actor run uses the default value defined by the task (or Actor's input
    schema if not defined by the task).

    The response is the Actor Run object as returned by the [Get
    run](#/reference/actor-runs/run-object-and-its-storages/get-run) endpoint.

    If you want to wait for the run to finish and receive the actual output of
    the Actor run as the response, use one of the [Run task
    synchronously](#/reference/actor-tasks/run-task-synchronously) API endpoints
    instead.

    To fetch the Actor run results that are typically stored in the default
    dataset, you'll need to pass the ID received in the `defaultDatasetId` field
    received in the response JSON to the
    [Get items](#/reference/datasets/item-collection/get-items) API endpoint.

    Args:
        actor_task_id (str):  Example: janedoe~my-task.
        timeout (float | Unset):  Example: 60.
        memory (float | Unset):  Example: 256.
        max_items (float | Unset):  Example: 1000.
        max_total_charge_usd (float | Unset):  Example: 5.
        restart_on_error (bool | Unset):
        build (str | Unset):  Example: 0.1.234.
        wait_for_finish (float | Unset):  Example: 60.
        webhooks (str | Unset):  Example: dGhpcyBpcyBqdXN0IGV4YW1wbGUK....
        body (ActorTaskRunsPostBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        actor_task_id=actor_task_id,
body=body,
timeout=timeout,
memory=memory,
max_items=max_items,
max_total_charge_usd=max_total_charge_usd,
restart_on_error=restart_on_error,
build=build,
wait_for_finish=wait_for_finish,
webhooks=webhooks,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)


from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.actor_task_run_sync_post_body import ActorTaskRunSyncPostBody
from ...models.actor_task_run_sync_post_response_201 import ActorTaskRunSyncPostResponse201
from ...models.error_response import ErrorResponse
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    actor_task_id: str,
    *,
    body: ActorTaskRunSyncPostBody,
    timeout: float | Unset = UNSET,
    memory: float | Unset = UNSET,
    max_items: float | Unset = UNSET,
    max_total_charge_usd: float | Unset = UNSET,
    restart_on_error: bool | Unset = UNSET,
    build: str | Unset = UNSET,
    output_record_key: str | Unset = UNSET,
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

    params["outputRecordKey"] = output_record_key

    params["webhooks"] = webhooks


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v2/actor-tasks/{actor_task_id}/run-sync".format(actor_task_id=actor_task_id,),
        "params": params,
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ActorTaskRunSyncPostResponse201 | ErrorResponse | None:
    if response.status_code == 201:
        response_201 = ActorTaskRunSyncPostResponse201.from_dict(response.json())



        return response_201

    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())



        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ActorTaskRunSyncPostResponse201 | ErrorResponse]:
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
    body: ActorTaskRunSyncPostBody,
    timeout: float | Unset = UNSET,
    memory: float | Unset = UNSET,
    max_items: float | Unset = UNSET,
    max_total_charge_usd: float | Unset = UNSET,
    restart_on_error: bool | Unset = UNSET,
    build: str | Unset = UNSET,
    output_record_key: str | Unset = UNSET,
    webhooks: str | Unset = UNSET,

) -> Response[ActorTaskRunSyncPostResponse201 | ErrorResponse]:
    """ Run task synchronously

     Runs an Actor task and synchronously returns its output.

    The run must finish in 300<!-- MAX_ACTOR_JOB_SYNC_WAIT_SECS --> seconds
    otherwise the HTTP request fails with a timeout error (this won't abort
    the run itself).

    Optionally, you can override the Actor input configuration by passing a JSON
    object as the POST payload and setting the `Content-Type: application/json` HTTP header.

    Note that if the object in the POST payload does not define a particular
    input property, the Actor run uses the default value defined by the task (or Actor's input
    schema if not defined by the task).

    Beware that it might be impossible to maintain an idle HTTP connection for
    an extended period, due to client timeout or network conditions. Make sure your HTTP client is
    configured to have a long enough connection timeout.

    If the connection breaks, you will not receive any information about the run
    and its status.

    Input fields from Actor task configuration can be overloaded with values
    passed as the POST payload.

    Just make sure to specify `Content-Type` header to be `application/json` and
    input to be an object.

    To run the task asynchronously, use the [Run
    task](#/reference/actor-tasks/run-collection/run-task) API endpoint instead.

    Args:
        actor_task_id (str):  Example: janedoe~my-task.
        timeout (float | Unset):  Example: 60.
        memory (float | Unset):  Example: 256.
        max_items (float | Unset):  Example: 1000.
        max_total_charge_usd (float | Unset):  Example: 5.
        restart_on_error (bool | Unset):
        build (str | Unset):  Example: 0.1.234.
        output_record_key (str | Unset):  Example: OUTPUT.
        webhooks (str | Unset):  Example: dGhpcyBpcyBqdXN0IGV4YW1wbGUK....
        body (ActorTaskRunSyncPostBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActorTaskRunSyncPostResponse201 | ErrorResponse]
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
output_record_key=output_record_key,
webhooks=webhooks,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    actor_task_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ActorTaskRunSyncPostBody,
    timeout: float | Unset = UNSET,
    memory: float | Unset = UNSET,
    max_items: float | Unset = UNSET,
    max_total_charge_usd: float | Unset = UNSET,
    restart_on_error: bool | Unset = UNSET,
    build: str | Unset = UNSET,
    output_record_key: str | Unset = UNSET,
    webhooks: str | Unset = UNSET,

) -> ActorTaskRunSyncPostResponse201 | ErrorResponse | None:
    """ Run task synchronously

     Runs an Actor task and synchronously returns its output.

    The run must finish in 300<!-- MAX_ACTOR_JOB_SYNC_WAIT_SECS --> seconds
    otherwise the HTTP request fails with a timeout error (this won't abort
    the run itself).

    Optionally, you can override the Actor input configuration by passing a JSON
    object as the POST payload and setting the `Content-Type: application/json` HTTP header.

    Note that if the object in the POST payload does not define a particular
    input property, the Actor run uses the default value defined by the task (or Actor's input
    schema if not defined by the task).

    Beware that it might be impossible to maintain an idle HTTP connection for
    an extended period, due to client timeout or network conditions. Make sure your HTTP client is
    configured to have a long enough connection timeout.

    If the connection breaks, you will not receive any information about the run
    and its status.

    Input fields from Actor task configuration can be overloaded with values
    passed as the POST payload.

    Just make sure to specify `Content-Type` header to be `application/json` and
    input to be an object.

    To run the task asynchronously, use the [Run
    task](#/reference/actor-tasks/run-collection/run-task) API endpoint instead.

    Args:
        actor_task_id (str):  Example: janedoe~my-task.
        timeout (float | Unset):  Example: 60.
        memory (float | Unset):  Example: 256.
        max_items (float | Unset):  Example: 1000.
        max_total_charge_usd (float | Unset):  Example: 5.
        restart_on_error (bool | Unset):
        build (str | Unset):  Example: 0.1.234.
        output_record_key (str | Unset):  Example: OUTPUT.
        webhooks (str | Unset):  Example: dGhpcyBpcyBqdXN0IGV4YW1wbGUK....
        body (ActorTaskRunSyncPostBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ActorTaskRunSyncPostResponse201 | ErrorResponse
     """


    return sync_detailed(
        actor_task_id=actor_task_id,
client=client,
body=body,
timeout=timeout,
memory=memory,
max_items=max_items,
max_total_charge_usd=max_total_charge_usd,
restart_on_error=restart_on_error,
build=build,
output_record_key=output_record_key,
webhooks=webhooks,

    ).parsed

async def asyncio_detailed(
    actor_task_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ActorTaskRunSyncPostBody,
    timeout: float | Unset = UNSET,
    memory: float | Unset = UNSET,
    max_items: float | Unset = UNSET,
    max_total_charge_usd: float | Unset = UNSET,
    restart_on_error: bool | Unset = UNSET,
    build: str | Unset = UNSET,
    output_record_key: str | Unset = UNSET,
    webhooks: str | Unset = UNSET,

) -> Response[ActorTaskRunSyncPostResponse201 | ErrorResponse]:
    """ Run task synchronously

     Runs an Actor task and synchronously returns its output.

    The run must finish in 300<!-- MAX_ACTOR_JOB_SYNC_WAIT_SECS --> seconds
    otherwise the HTTP request fails with a timeout error (this won't abort
    the run itself).

    Optionally, you can override the Actor input configuration by passing a JSON
    object as the POST payload and setting the `Content-Type: application/json` HTTP header.

    Note that if the object in the POST payload does not define a particular
    input property, the Actor run uses the default value defined by the task (or Actor's input
    schema if not defined by the task).

    Beware that it might be impossible to maintain an idle HTTP connection for
    an extended period, due to client timeout or network conditions. Make sure your HTTP client is
    configured to have a long enough connection timeout.

    If the connection breaks, you will not receive any information about the run
    and its status.

    Input fields from Actor task configuration can be overloaded with values
    passed as the POST payload.

    Just make sure to specify `Content-Type` header to be `application/json` and
    input to be an object.

    To run the task asynchronously, use the [Run
    task](#/reference/actor-tasks/run-collection/run-task) API endpoint instead.

    Args:
        actor_task_id (str):  Example: janedoe~my-task.
        timeout (float | Unset):  Example: 60.
        memory (float | Unset):  Example: 256.
        max_items (float | Unset):  Example: 1000.
        max_total_charge_usd (float | Unset):  Example: 5.
        restart_on_error (bool | Unset):
        build (str | Unset):  Example: 0.1.234.
        output_record_key (str | Unset):  Example: OUTPUT.
        webhooks (str | Unset):  Example: dGhpcyBpcyBqdXN0IGV4YW1wbGUK....
        body (ActorTaskRunSyncPostBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActorTaskRunSyncPostResponse201 | ErrorResponse]
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
output_record_key=output_record_key,
webhooks=webhooks,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    actor_task_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ActorTaskRunSyncPostBody,
    timeout: float | Unset = UNSET,
    memory: float | Unset = UNSET,
    max_items: float | Unset = UNSET,
    max_total_charge_usd: float | Unset = UNSET,
    restart_on_error: bool | Unset = UNSET,
    build: str | Unset = UNSET,
    output_record_key: str | Unset = UNSET,
    webhooks: str | Unset = UNSET,

) -> ActorTaskRunSyncPostResponse201 | ErrorResponse | None:
    """ Run task synchronously

     Runs an Actor task and synchronously returns its output.

    The run must finish in 300<!-- MAX_ACTOR_JOB_SYNC_WAIT_SECS --> seconds
    otherwise the HTTP request fails with a timeout error (this won't abort
    the run itself).

    Optionally, you can override the Actor input configuration by passing a JSON
    object as the POST payload and setting the `Content-Type: application/json` HTTP header.

    Note that if the object in the POST payload does not define a particular
    input property, the Actor run uses the default value defined by the task (or Actor's input
    schema if not defined by the task).

    Beware that it might be impossible to maintain an idle HTTP connection for
    an extended period, due to client timeout or network conditions. Make sure your HTTP client is
    configured to have a long enough connection timeout.

    If the connection breaks, you will not receive any information about the run
    and its status.

    Input fields from Actor task configuration can be overloaded with values
    passed as the POST payload.

    Just make sure to specify `Content-Type` header to be `application/json` and
    input to be an object.

    To run the task asynchronously, use the [Run
    task](#/reference/actor-tasks/run-collection/run-task) API endpoint instead.

    Args:
        actor_task_id (str):  Example: janedoe~my-task.
        timeout (float | Unset):  Example: 60.
        memory (float | Unset):  Example: 256.
        max_items (float | Unset):  Example: 1000.
        max_total_charge_usd (float | Unset):  Example: 5.
        restart_on_error (bool | Unset):
        build (str | Unset):  Example: 0.1.234.
        output_record_key (str | Unset):  Example: OUTPUT.
        webhooks (str | Unset):  Example: dGhpcyBpcyBqdXN0IGV4YW1wbGUK....
        body (ActorTaskRunSyncPostBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ActorTaskRunSyncPostResponse201 | ErrorResponse
     """


    return (await asyncio_detailed(
        actor_task_id=actor_task_id,
client=client,
body=body,
timeout=timeout,
memory=memory,
max_items=max_items,
max_total_charge_usd=max_total_charge_usd,
restart_on_error=restart_on_error,
build=build,
output_record_key=output_record_key,
webhooks=webhooks,

    )).parsed

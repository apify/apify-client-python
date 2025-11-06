from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.actor_task_run_sync_get_response_201 import ActorTaskRunSyncGetResponse201
from ...models.error_response import ErrorResponse
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    actor_task_id: str,
    *,
    timeout: float | Unset = UNSET,
    memory: float | Unset = UNSET,
    max_items: float | Unset = UNSET,
    build: str | Unset = UNSET,
    output_record_key: str | Unset = UNSET,
    webhooks: str | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["timeout"] = timeout

    params["memory"] = memory

    params["maxItems"] = max_items

    params["build"] = build

    params["outputRecordKey"] = output_record_key

    params["webhooks"] = webhooks


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/actor-tasks/{actor_task_id}/run-sync".format(actor_task_id=actor_task_id,),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ActorTaskRunSyncGetResponse201 | ErrorResponse | None:
    if response.status_code == 201:
        response_201 = ActorTaskRunSyncGetResponse201.from_dict(response.json())



        return response_201

    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())



        return response_400

    if response.status_code == 408:
        response_408 = ErrorResponse.from_dict(response.json())



        return response_408

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ActorTaskRunSyncGetResponse201 | ErrorResponse]:
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
    timeout: float | Unset = UNSET,
    memory: float | Unset = UNSET,
    max_items: float | Unset = UNSET,
    build: str | Unset = UNSET,
    output_record_key: str | Unset = UNSET,
    webhooks: str | Unset = UNSET,

) -> Response[ActorTaskRunSyncGetResponse201 | ErrorResponse]:
    """ Run task synchronously

     Run a specific task and return its output.

    The run must finish in 300<!-- MAX_ACTOR_JOB_SYNC_WAIT_SECS --> seconds
    otherwise the HTTP request fails with a timeout error (this won't abort
    the run itself).

    Beware that it might be impossible to maintain an idle HTTP connection for
    an extended period, due to client timeout or network conditions. Make sure your HTTP client is
    configured to have a long enough connection timeout.

    If the connection breaks, you will not receive any information about the run
    and its status.

    To run the Task asynchronously, use the
    [Run task asynchronously](#/reference/actor-tasks/run-collection/run-task)
    endpoint instead.

    Args:
        actor_task_id (str):  Example: janedoe~my-task.
        timeout (float | Unset):  Example: 60.
        memory (float | Unset):  Example: 256.
        max_items (float | Unset):  Example: 1000.
        build (str | Unset):  Example: 0.1.234.
        output_record_key (str | Unset):  Example: OUTPUT.
        webhooks (str | Unset):  Example: dGhpcyBpcyBqdXN0IGV4YW1wbGUK....

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActorTaskRunSyncGetResponse201 | ErrorResponse]
     """


    kwargs = _get_kwargs(
        actor_task_id=actor_task_id,
timeout=timeout,
memory=memory,
max_items=max_items,
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
    timeout: float | Unset = UNSET,
    memory: float | Unset = UNSET,
    max_items: float | Unset = UNSET,
    build: str | Unset = UNSET,
    output_record_key: str | Unset = UNSET,
    webhooks: str | Unset = UNSET,

) -> ActorTaskRunSyncGetResponse201 | ErrorResponse | None:
    """ Run task synchronously

     Run a specific task and return its output.

    The run must finish in 300<!-- MAX_ACTOR_JOB_SYNC_WAIT_SECS --> seconds
    otherwise the HTTP request fails with a timeout error (this won't abort
    the run itself).

    Beware that it might be impossible to maintain an idle HTTP connection for
    an extended period, due to client timeout or network conditions. Make sure your HTTP client is
    configured to have a long enough connection timeout.

    If the connection breaks, you will not receive any information about the run
    and its status.

    To run the Task asynchronously, use the
    [Run task asynchronously](#/reference/actor-tasks/run-collection/run-task)
    endpoint instead.

    Args:
        actor_task_id (str):  Example: janedoe~my-task.
        timeout (float | Unset):  Example: 60.
        memory (float | Unset):  Example: 256.
        max_items (float | Unset):  Example: 1000.
        build (str | Unset):  Example: 0.1.234.
        output_record_key (str | Unset):  Example: OUTPUT.
        webhooks (str | Unset):  Example: dGhpcyBpcyBqdXN0IGV4YW1wbGUK....

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ActorTaskRunSyncGetResponse201 | ErrorResponse
     """


    return sync_detailed(
        actor_task_id=actor_task_id,
client=client,
timeout=timeout,
memory=memory,
max_items=max_items,
build=build,
output_record_key=output_record_key,
webhooks=webhooks,

    ).parsed

async def asyncio_detailed(
    actor_task_id: str,
    *,
    client: AuthenticatedClient | Client,
    timeout: float | Unset = UNSET,
    memory: float | Unset = UNSET,
    max_items: float | Unset = UNSET,
    build: str | Unset = UNSET,
    output_record_key: str | Unset = UNSET,
    webhooks: str | Unset = UNSET,

) -> Response[ActorTaskRunSyncGetResponse201 | ErrorResponse]:
    """ Run task synchronously

     Run a specific task and return its output.

    The run must finish in 300<!-- MAX_ACTOR_JOB_SYNC_WAIT_SECS --> seconds
    otherwise the HTTP request fails with a timeout error (this won't abort
    the run itself).

    Beware that it might be impossible to maintain an idle HTTP connection for
    an extended period, due to client timeout or network conditions. Make sure your HTTP client is
    configured to have a long enough connection timeout.

    If the connection breaks, you will not receive any information about the run
    and its status.

    To run the Task asynchronously, use the
    [Run task asynchronously](#/reference/actor-tasks/run-collection/run-task)
    endpoint instead.

    Args:
        actor_task_id (str):  Example: janedoe~my-task.
        timeout (float | Unset):  Example: 60.
        memory (float | Unset):  Example: 256.
        max_items (float | Unset):  Example: 1000.
        build (str | Unset):  Example: 0.1.234.
        output_record_key (str | Unset):  Example: OUTPUT.
        webhooks (str | Unset):  Example: dGhpcyBpcyBqdXN0IGV4YW1wbGUK....

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActorTaskRunSyncGetResponse201 | ErrorResponse]
     """


    kwargs = _get_kwargs(
        actor_task_id=actor_task_id,
timeout=timeout,
memory=memory,
max_items=max_items,
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
    timeout: float | Unset = UNSET,
    memory: float | Unset = UNSET,
    max_items: float | Unset = UNSET,
    build: str | Unset = UNSET,
    output_record_key: str | Unset = UNSET,
    webhooks: str | Unset = UNSET,

) -> ActorTaskRunSyncGetResponse201 | ErrorResponse | None:
    """ Run task synchronously

     Run a specific task and return its output.

    The run must finish in 300<!-- MAX_ACTOR_JOB_SYNC_WAIT_SECS --> seconds
    otherwise the HTTP request fails with a timeout error (this won't abort
    the run itself).

    Beware that it might be impossible to maintain an idle HTTP connection for
    an extended period, due to client timeout or network conditions. Make sure your HTTP client is
    configured to have a long enough connection timeout.

    If the connection breaks, you will not receive any information about the run
    and its status.

    To run the Task asynchronously, use the
    [Run task asynchronously](#/reference/actor-tasks/run-collection/run-task)
    endpoint instead.

    Args:
        actor_task_id (str):  Example: janedoe~my-task.
        timeout (float | Unset):  Example: 60.
        memory (float | Unset):  Example: 256.
        max_items (float | Unset):  Example: 1000.
        build (str | Unset):  Example: 0.1.234.
        output_record_key (str | Unset):  Example: OUTPUT.
        webhooks (str | Unset):  Example: dGhpcyBpcyBqdXN0IGV4YW1wbGUK....

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ActorTaskRunSyncGetResponse201 | ErrorResponse
     """


    return (await asyncio_detailed(
        actor_task_id=actor_task_id,
client=client,
timeout=timeout,
memory=memory,
max_items=max_items,
build=build,
output_record_key=output_record_key,
webhooks=webhooks,

    )).parsed

from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.act_run_sync_post_body import ActRunSyncPostBody
from ...models.act_run_sync_post_response_201 import ActRunSyncPostResponse201
from ...models.error_response import ErrorResponse
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    actor_id: str,
    *,
    body: ActRunSyncPostBody,
    output_record_key: str | Unset = UNSET,
    timeout: float | Unset = UNSET,
    memory: float | Unset = UNSET,
    max_items: float | Unset = UNSET,
    max_total_charge_usd: float | Unset = UNSET,
    restart_on_error: bool | Unset = UNSET,
    build: str | Unset = UNSET,
    webhooks: str | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    params: dict[str, Any] = {}

    params["outputRecordKey"] = output_record_key

    params["timeout"] = timeout

    params["memory"] = memory

    params["maxItems"] = max_items

    params["maxTotalChargeUsd"] = max_total_charge_usd

    params["restartOnError"] = restart_on_error

    params["build"] = build

    params["webhooks"] = webhooks


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v2/acts/{actor_id}/run-sync".format(actor_id=actor_id,),
        "params": params,
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ActRunSyncPostResponse201 | ErrorResponse | None:
    if response.status_code == 201:
        response_201 = ActRunSyncPostResponse201.from_dict(response.json())



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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ActRunSyncPostResponse201 | ErrorResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    actor_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ActRunSyncPostBody,
    output_record_key: str | Unset = UNSET,
    timeout: float | Unset = UNSET,
    memory: float | Unset = UNSET,
    max_items: float | Unset = UNSET,
    max_total_charge_usd: float | Unset = UNSET,
    restart_on_error: bool | Unset = UNSET,
    build: str | Unset = UNSET,
    webhooks: str | Unset = UNSET,

) -> Response[ActRunSyncPostResponse201 | ErrorResponse]:
    """ Run Actor synchronously with input and return output

     Runs a specific Actor and returns its output.

    The POST payload including its `Content-Type` header is passed as `INPUT` to
    the Actor (usually <code>application/json</code>).
    The HTTP response contains Actors `OUTPUT` record from its default
    key-value store.

    The Actor is started with the default options; you can override them using
    various URL query parameters.
    If the Actor run exceeds 300<!-- MAX_ACTOR_JOB_SYNC_WAIT_SECS --> seconds,
    the HTTP response will have status 408 (Request Timeout).

    Beware that it might be impossible to maintain an idle HTTP connection for a
    long period of time, due to client timeout or network conditions. Make sure your HTTP client is
    configured to have a long enough connection timeout.
    If the connection breaks, you will not receive any information about the run
    and its status.

    To run the Actor asynchronously, use the [Run
    Actor](#/reference/actors/run-collection/run-actor) API endpoint instead.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        output_record_key (str | Unset):  Example: OUTPUT.
        timeout (float | Unset):  Example: 60.
        memory (float | Unset):  Example: 256.
        max_items (float | Unset):  Example: 1000.
        max_total_charge_usd (float | Unset):  Example: 5.
        restart_on_error (bool | Unset):
        build (str | Unset):  Example: 0.1.234.
        webhooks (str | Unset):  Example: dGhpcyBpcyBqdXN0IGV4YW1wbGUK....
        body (ActRunSyncPostBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActRunSyncPostResponse201 | ErrorResponse]
     """


    kwargs = _get_kwargs(
        actor_id=actor_id,
body=body,
output_record_key=output_record_key,
timeout=timeout,
memory=memory,
max_items=max_items,
max_total_charge_usd=max_total_charge_usd,
restart_on_error=restart_on_error,
build=build,
webhooks=webhooks,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    actor_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ActRunSyncPostBody,
    output_record_key: str | Unset = UNSET,
    timeout: float | Unset = UNSET,
    memory: float | Unset = UNSET,
    max_items: float | Unset = UNSET,
    max_total_charge_usd: float | Unset = UNSET,
    restart_on_error: bool | Unset = UNSET,
    build: str | Unset = UNSET,
    webhooks: str | Unset = UNSET,

) -> ActRunSyncPostResponse201 | ErrorResponse | None:
    """ Run Actor synchronously with input and return output

     Runs a specific Actor and returns its output.

    The POST payload including its `Content-Type` header is passed as `INPUT` to
    the Actor (usually <code>application/json</code>).
    The HTTP response contains Actors `OUTPUT` record from its default
    key-value store.

    The Actor is started with the default options; you can override them using
    various URL query parameters.
    If the Actor run exceeds 300<!-- MAX_ACTOR_JOB_SYNC_WAIT_SECS --> seconds,
    the HTTP response will have status 408 (Request Timeout).

    Beware that it might be impossible to maintain an idle HTTP connection for a
    long period of time, due to client timeout or network conditions. Make sure your HTTP client is
    configured to have a long enough connection timeout.
    If the connection breaks, you will not receive any information about the run
    and its status.

    To run the Actor asynchronously, use the [Run
    Actor](#/reference/actors/run-collection/run-actor) API endpoint instead.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        output_record_key (str | Unset):  Example: OUTPUT.
        timeout (float | Unset):  Example: 60.
        memory (float | Unset):  Example: 256.
        max_items (float | Unset):  Example: 1000.
        max_total_charge_usd (float | Unset):  Example: 5.
        restart_on_error (bool | Unset):
        build (str | Unset):  Example: 0.1.234.
        webhooks (str | Unset):  Example: dGhpcyBpcyBqdXN0IGV4YW1wbGUK....
        body (ActRunSyncPostBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ActRunSyncPostResponse201 | ErrorResponse
     """


    return sync_detailed(
        actor_id=actor_id,
client=client,
body=body,
output_record_key=output_record_key,
timeout=timeout,
memory=memory,
max_items=max_items,
max_total_charge_usd=max_total_charge_usd,
restart_on_error=restart_on_error,
build=build,
webhooks=webhooks,

    ).parsed

async def asyncio_detailed(
    actor_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ActRunSyncPostBody,
    output_record_key: str | Unset = UNSET,
    timeout: float | Unset = UNSET,
    memory: float | Unset = UNSET,
    max_items: float | Unset = UNSET,
    max_total_charge_usd: float | Unset = UNSET,
    restart_on_error: bool | Unset = UNSET,
    build: str | Unset = UNSET,
    webhooks: str | Unset = UNSET,

) -> Response[ActRunSyncPostResponse201 | ErrorResponse]:
    """ Run Actor synchronously with input and return output

     Runs a specific Actor and returns its output.

    The POST payload including its `Content-Type` header is passed as `INPUT` to
    the Actor (usually <code>application/json</code>).
    The HTTP response contains Actors `OUTPUT` record from its default
    key-value store.

    The Actor is started with the default options; you can override them using
    various URL query parameters.
    If the Actor run exceeds 300<!-- MAX_ACTOR_JOB_SYNC_WAIT_SECS --> seconds,
    the HTTP response will have status 408 (Request Timeout).

    Beware that it might be impossible to maintain an idle HTTP connection for a
    long period of time, due to client timeout or network conditions. Make sure your HTTP client is
    configured to have a long enough connection timeout.
    If the connection breaks, you will not receive any information about the run
    and its status.

    To run the Actor asynchronously, use the [Run
    Actor](#/reference/actors/run-collection/run-actor) API endpoint instead.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        output_record_key (str | Unset):  Example: OUTPUT.
        timeout (float | Unset):  Example: 60.
        memory (float | Unset):  Example: 256.
        max_items (float | Unset):  Example: 1000.
        max_total_charge_usd (float | Unset):  Example: 5.
        restart_on_error (bool | Unset):
        build (str | Unset):  Example: 0.1.234.
        webhooks (str | Unset):  Example: dGhpcyBpcyBqdXN0IGV4YW1wbGUK....
        body (ActRunSyncPostBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActRunSyncPostResponse201 | ErrorResponse]
     """


    kwargs = _get_kwargs(
        actor_id=actor_id,
body=body,
output_record_key=output_record_key,
timeout=timeout,
memory=memory,
max_items=max_items,
max_total_charge_usd=max_total_charge_usd,
restart_on_error=restart_on_error,
build=build,
webhooks=webhooks,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    actor_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ActRunSyncPostBody,
    output_record_key: str | Unset = UNSET,
    timeout: float | Unset = UNSET,
    memory: float | Unset = UNSET,
    max_items: float | Unset = UNSET,
    max_total_charge_usd: float | Unset = UNSET,
    restart_on_error: bool | Unset = UNSET,
    build: str | Unset = UNSET,
    webhooks: str | Unset = UNSET,

) -> ActRunSyncPostResponse201 | ErrorResponse | None:
    """ Run Actor synchronously with input and return output

     Runs a specific Actor and returns its output.

    The POST payload including its `Content-Type` header is passed as `INPUT` to
    the Actor (usually <code>application/json</code>).
    The HTTP response contains Actors `OUTPUT` record from its default
    key-value store.

    The Actor is started with the default options; you can override them using
    various URL query parameters.
    If the Actor run exceeds 300<!-- MAX_ACTOR_JOB_SYNC_WAIT_SECS --> seconds,
    the HTTP response will have status 408 (Request Timeout).

    Beware that it might be impossible to maintain an idle HTTP connection for a
    long period of time, due to client timeout or network conditions. Make sure your HTTP client is
    configured to have a long enough connection timeout.
    If the connection breaks, you will not receive any information about the run
    and its status.

    To run the Actor asynchronously, use the [Run
    Actor](#/reference/actors/run-collection/run-actor) API endpoint instead.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        output_record_key (str | Unset):  Example: OUTPUT.
        timeout (float | Unset):  Example: 60.
        memory (float | Unset):  Example: 256.
        max_items (float | Unset):  Example: 1000.
        max_total_charge_usd (float | Unset):  Example: 5.
        restart_on_error (bool | Unset):
        build (str | Unset):  Example: 0.1.234.
        webhooks (str | Unset):  Example: dGhpcyBpcyBqdXN0IGV4YW1wbGUK....
        body (ActRunSyncPostBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ActRunSyncPostResponse201 | ErrorResponse
     """


    return (await asyncio_detailed(
        actor_id=actor_id,
client=client,
body=body,
output_record_key=output_record_key,
timeout=timeout,
memory=memory,
max_items=max_items,
max_total_charge_usd=max_total_charge_usd,
restart_on_error=restart_on_error,
build=build,
webhooks=webhooks,

    )).parsed

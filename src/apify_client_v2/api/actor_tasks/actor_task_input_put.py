from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.actor_task_input_put_body import ActorTaskInputPutBody
from ...models.actor_task_input_put_response_200 import ActorTaskInputPutResponse200
from typing import cast



def _get_kwargs(
    actor_task_id: str,
    *,
    body: ActorTaskInputPutBody,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v2/actor-tasks/{actor_task_id}/input".format(actor_task_id=actor_task_id,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ActorTaskInputPutResponse200 | None:
    if response.status_code == 200:
        response_200 = ActorTaskInputPutResponse200.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ActorTaskInputPutResponse200]:
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
    body: ActorTaskInputPutBody,

) -> Response[ActorTaskInputPutResponse200]:
    """ Update task input

     Updates the input of a task using values specified by an object passed as
    JSON in the PUT payload.

    If the object does not define a specific property, its value is not updated.

    The response is the full task input as returned by the
    [Get task input](#/reference/tasks/task-input-object/get-task-input) endpoint.

    The request needs to specify the `Content-Type: application/json` HTTP
    header!

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    Args:
        actor_task_id (str):  Example: janedoe~my-task.
        body (ActorTaskInputPutBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActorTaskInputPutResponse200]
     """


    kwargs = _get_kwargs(
        actor_task_id=actor_task_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    actor_task_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ActorTaskInputPutBody,

) -> ActorTaskInputPutResponse200 | None:
    """ Update task input

     Updates the input of a task using values specified by an object passed as
    JSON in the PUT payload.

    If the object does not define a specific property, its value is not updated.

    The response is the full task input as returned by the
    [Get task input](#/reference/tasks/task-input-object/get-task-input) endpoint.

    The request needs to specify the `Content-Type: application/json` HTTP
    header!

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    Args:
        actor_task_id (str):  Example: janedoe~my-task.
        body (ActorTaskInputPutBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ActorTaskInputPutResponse200
     """


    return sync_detailed(
        actor_task_id=actor_task_id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    actor_task_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ActorTaskInputPutBody,

) -> Response[ActorTaskInputPutResponse200]:
    """ Update task input

     Updates the input of a task using values specified by an object passed as
    JSON in the PUT payload.

    If the object does not define a specific property, its value is not updated.

    The response is the full task input as returned by the
    [Get task input](#/reference/tasks/task-input-object/get-task-input) endpoint.

    The request needs to specify the `Content-Type: application/json` HTTP
    header!

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    Args:
        actor_task_id (str):  Example: janedoe~my-task.
        body (ActorTaskInputPutBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActorTaskInputPutResponse200]
     """


    kwargs = _get_kwargs(
        actor_task_id=actor_task_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    actor_task_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ActorTaskInputPutBody,

) -> ActorTaskInputPutResponse200 | None:
    """ Update task input

     Updates the input of a task using values specified by an object passed as
    JSON in the PUT payload.

    If the object does not define a specific property, its value is not updated.

    The response is the full task input as returned by the
    [Get task input](#/reference/tasks/task-input-object/get-task-input) endpoint.

    The request needs to specify the `Content-Type: application/json` HTTP
    header!

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    Args:
        actor_task_id (str):  Example: janedoe~my-task.
        body (ActorTaskInputPutBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ActorTaskInputPutResponse200
     """


    return (await asyncio_detailed(
        actor_task_id=actor_task_id,
client=client,
body=body,

    )).parsed

from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.update_task_request import UpdateTaskRequest
from typing import cast



def _get_kwargs(
    actor_task_id: str,
    *,
    body: UpdateTaskRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v2/actor-tasks/{actor_task_id}".format(actor_task_id=actor_task_id,),
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
    body: UpdateTaskRequest,

) -> Response[Any]:
    """ Update task

     Update settings of a task using values specified by an object passed as JSON
    in the POST payload.

    If the object does not define a specific property, its value is not updated.

    The response is the full task object as returned by the
    [Get task](#/reference/tasks/task-object/get-task) endpoint.

    The request needs to specify the `Content-Type: application/json` HTTP
    header!

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    Args:
        actor_task_id (str):  Example: janedoe~my-task.
        body (UpdateTaskRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        actor_task_id=actor_task_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    actor_task_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateTaskRequest,

) -> Response[Any]:
    """ Update task

     Update settings of a task using values specified by an object passed as JSON
    in the POST payload.

    If the object does not define a specific property, its value is not updated.

    The response is the full task object as returned by the
    [Get task](#/reference/tasks/task-object/get-task) endpoint.

    The request needs to specify the `Content-Type: application/json` HTTP
    header!

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    Args:
        actor_task_id (str):  Example: janedoe~my-task.
        body (UpdateTaskRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        actor_task_id=actor_task_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)


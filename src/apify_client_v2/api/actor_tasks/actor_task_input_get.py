from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.actor_task_input_get_response_200 import ActorTaskInputGetResponse200
from typing import cast



def _get_kwargs(
    actor_task_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/actor-tasks/{actor_task_id}/input".format(actor_task_id=actor_task_id,),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ActorTaskInputGetResponse200 | None:
    if response.status_code == 200:
        response_200 = ActorTaskInputGetResponse200.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ActorTaskInputGetResponse200]:
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

) -> Response[ActorTaskInputGetResponse200]:
    """ Get task input

     Returns the input of a given task.

    Args:
        actor_task_id (str):  Example: janedoe~my-task.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActorTaskInputGetResponse200]
     """


    kwargs = _get_kwargs(
        actor_task_id=actor_task_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    actor_task_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> ActorTaskInputGetResponse200 | None:
    """ Get task input

     Returns the input of a given task.

    Args:
        actor_task_id (str):  Example: janedoe~my-task.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ActorTaskInputGetResponse200
     """


    return sync_detailed(
        actor_task_id=actor_task_id,
client=client,

    ).parsed

async def asyncio_detailed(
    actor_task_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[ActorTaskInputGetResponse200]:
    """ Get task input

     Returns the input of a given task.

    Args:
        actor_task_id (str):  Example: janedoe~my-task.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActorTaskInputGetResponse200]
     """


    kwargs = _get_kwargs(
        actor_task_id=actor_task_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    actor_task_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> ActorTaskInputGetResponse200 | None:
    """ Get task input

     Returns the input of a given task.

    Args:
        actor_task_id (str):  Example: janedoe~my-task.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ActorTaskInputGetResponse200
     """


    return (await asyncio_detailed(
        actor_task_id=actor_task_id,
client=client,

    )).parsed

from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.actor_tasks_get_response_200 import ActorTasksGetResponse200
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    *,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    desc: bool | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["offset"] = offset

    params["limit"] = limit

    params["desc"] = desc


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/actor-tasks",
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ActorTasksGetResponse200 | None:
    if response.status_code == 200:
        response_200 = ActorTasksGetResponse200.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ActorTasksGetResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    desc: bool | Unset = UNSET,

) -> Response[ActorTasksGetResponse200]:
    """ Get list of tasks

     Gets the complete list of tasks that a user has created or used.

    The response is a list of objects in which each object contains essential
    information about a single task.

    The endpoint supports pagination using the `limit` and `offset` parameters,
    and it does not return more than a 1000 records.

    By default, the records are sorted by the `createdAt` field in ascending
    order; therefore you can use pagination to incrementally fetch all tasks while new
    ones are still being created. To sort the records in descending order, use
    the `desc=1` parameter.

    Args:
        offset (float | Unset):  Example: 10.
        limit (float | Unset):  Example: 99.
        desc (bool | Unset):  Example: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActorTasksGetResponse200]
     """


    kwargs = _get_kwargs(
        offset=offset,
limit=limit,
desc=desc,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient | Client,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    desc: bool | Unset = UNSET,

) -> ActorTasksGetResponse200 | None:
    """ Get list of tasks

     Gets the complete list of tasks that a user has created or used.

    The response is a list of objects in which each object contains essential
    information about a single task.

    The endpoint supports pagination using the `limit` and `offset` parameters,
    and it does not return more than a 1000 records.

    By default, the records are sorted by the `createdAt` field in ascending
    order; therefore you can use pagination to incrementally fetch all tasks while new
    ones are still being created. To sort the records in descending order, use
    the `desc=1` parameter.

    Args:
        offset (float | Unset):  Example: 10.
        limit (float | Unset):  Example: 99.
        desc (bool | Unset):  Example: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ActorTasksGetResponse200
     """


    return sync_detailed(
        client=client,
offset=offset,
limit=limit,
desc=desc,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    desc: bool | Unset = UNSET,

) -> Response[ActorTasksGetResponse200]:
    """ Get list of tasks

     Gets the complete list of tasks that a user has created or used.

    The response is a list of objects in which each object contains essential
    information about a single task.

    The endpoint supports pagination using the `limit` and `offset` parameters,
    and it does not return more than a 1000 records.

    By default, the records are sorted by the `createdAt` field in ascending
    order; therefore you can use pagination to incrementally fetch all tasks while new
    ones are still being created. To sort the records in descending order, use
    the `desc=1` parameter.

    Args:
        offset (float | Unset):  Example: 10.
        limit (float | Unset):  Example: 99.
        desc (bool | Unset):  Example: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActorTasksGetResponse200]
     """


    kwargs = _get_kwargs(
        offset=offset,
limit=limit,
desc=desc,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    desc: bool | Unset = UNSET,

) -> ActorTasksGetResponse200 | None:
    """ Get list of tasks

     Gets the complete list of tasks that a user has created or used.

    The response is a list of objects in which each object contains essential
    information about a single task.

    The endpoint supports pagination using the `limit` and `offset` parameters,
    and it does not return more than a 1000 records.

    By default, the records are sorted by the `createdAt` field in ascending
    order; therefore you can use pagination to incrementally fetch all tasks while new
    ones are still being created. To sort the records in descending order, use
    the `desc=1` parameter.

    Args:
        offset (float | Unset):  Example: 10.
        limit (float | Unset):  Example: 99.
        desc (bool | Unset):  Example: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ActorTasksGetResponse200
     """


    return (await asyncio_detailed(
        client=client,
offset=offset,
limit=limit,
desc=desc,

    )).parsed

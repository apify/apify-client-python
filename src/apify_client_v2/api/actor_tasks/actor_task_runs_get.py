from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.actor_task_runs_get_response_200 import ActorTaskRunsGetResponse200
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    actor_task_id: str,
    *,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    desc: bool | Unset = UNSET,
    status: str | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["offset"] = offset

    params["limit"] = limit

    params["desc"] = desc

    params["status"] = status


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/actor-tasks/{actor_task_id}/runs".format(actor_task_id=actor_task_id,),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ActorTaskRunsGetResponse200 | None:
    if response.status_code == 200:
        response_200 = ActorTaskRunsGetResponse200.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ActorTaskRunsGetResponse200]:
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
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    desc: bool | Unset = UNSET,
    status: str | Unset = UNSET,

) -> Response[ActorTaskRunsGetResponse200]:
    """ Get list of task runs

     Get a list of runs of a specific task. The response is a list of objects,
    where each object contains essential information about a single task run.

    The endpoint supports pagination using the `limit` and `offset` parameters,
    and it does not return more than a 1000 array elements.

    By default, the records are sorted by the `startedAt` field in ascending
    order; therefore you can use pagination to incrementally fetch all records while
    new ones are still being created. To sort the records in descending order, use
    the `desc=1` parameter. You can also filter runs by status ([available
    statuses](https://docs.apify.com/platform/actors/running/runs-and-builds#lifecycle)).

    Args:
        actor_task_id (str):  Example: janedoe~my-task.
        offset (float | Unset):  Example: 10.
        limit (float | Unset):  Example: 99.
        desc (bool | Unset):  Example: True.
        status (str | Unset):  Example: SUCCEEDED.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActorTaskRunsGetResponse200]
     """


    kwargs = _get_kwargs(
        actor_task_id=actor_task_id,
offset=offset,
limit=limit,
desc=desc,
status=status,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    actor_task_id: str,
    *,
    client: AuthenticatedClient | Client,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    desc: bool | Unset = UNSET,
    status: str | Unset = UNSET,

) -> ActorTaskRunsGetResponse200 | None:
    """ Get list of task runs

     Get a list of runs of a specific task. The response is a list of objects,
    where each object contains essential information about a single task run.

    The endpoint supports pagination using the `limit` and `offset` parameters,
    and it does not return more than a 1000 array elements.

    By default, the records are sorted by the `startedAt` field in ascending
    order; therefore you can use pagination to incrementally fetch all records while
    new ones are still being created. To sort the records in descending order, use
    the `desc=1` parameter. You can also filter runs by status ([available
    statuses](https://docs.apify.com/platform/actors/running/runs-and-builds#lifecycle)).

    Args:
        actor_task_id (str):  Example: janedoe~my-task.
        offset (float | Unset):  Example: 10.
        limit (float | Unset):  Example: 99.
        desc (bool | Unset):  Example: True.
        status (str | Unset):  Example: SUCCEEDED.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ActorTaskRunsGetResponse200
     """


    return sync_detailed(
        actor_task_id=actor_task_id,
client=client,
offset=offset,
limit=limit,
desc=desc,
status=status,

    ).parsed

async def asyncio_detailed(
    actor_task_id: str,
    *,
    client: AuthenticatedClient | Client,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    desc: bool | Unset = UNSET,
    status: str | Unset = UNSET,

) -> Response[ActorTaskRunsGetResponse200]:
    """ Get list of task runs

     Get a list of runs of a specific task. The response is a list of objects,
    where each object contains essential information about a single task run.

    The endpoint supports pagination using the `limit` and `offset` parameters,
    and it does not return more than a 1000 array elements.

    By default, the records are sorted by the `startedAt` field in ascending
    order; therefore you can use pagination to incrementally fetch all records while
    new ones are still being created. To sort the records in descending order, use
    the `desc=1` parameter. You can also filter runs by status ([available
    statuses](https://docs.apify.com/platform/actors/running/runs-and-builds#lifecycle)).

    Args:
        actor_task_id (str):  Example: janedoe~my-task.
        offset (float | Unset):  Example: 10.
        limit (float | Unset):  Example: 99.
        desc (bool | Unset):  Example: True.
        status (str | Unset):  Example: SUCCEEDED.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActorTaskRunsGetResponse200]
     """


    kwargs = _get_kwargs(
        actor_task_id=actor_task_id,
offset=offset,
limit=limit,
desc=desc,
status=status,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    actor_task_id: str,
    *,
    client: AuthenticatedClient | Client,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    desc: bool | Unset = UNSET,
    status: str | Unset = UNSET,

) -> ActorTaskRunsGetResponse200 | None:
    """ Get list of task runs

     Get a list of runs of a specific task. The response is a list of objects,
    where each object contains essential information about a single task run.

    The endpoint supports pagination using the `limit` and `offset` parameters,
    and it does not return more than a 1000 array elements.

    By default, the records are sorted by the `startedAt` field in ascending
    order; therefore you can use pagination to incrementally fetch all records while
    new ones are still being created. To sort the records in descending order, use
    the `desc=1` parameter. You can also filter runs by status ([available
    statuses](https://docs.apify.com/platform/actors/running/runs-and-builds#lifecycle)).

    Args:
        actor_task_id (str):  Example: janedoe~my-task.
        offset (float | Unset):  Example: 10.
        limit (float | Unset):  Example: 99.
        desc (bool | Unset):  Example: True.
        status (str | Unset):  Example: SUCCEEDED.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ActorTaskRunsGetResponse200
     """


    return (await asyncio_detailed(
        actor_task_id=actor_task_id,
client=client,
offset=offset,
limit=limit,
desc=desc,
status=status,

    )).parsed

from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.get_user_runs_list_response import GetUserRunsListResponse
from ...types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
import datetime



def _get_kwargs(
    *,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    desc: bool | Unset = UNSET,
    status: str | Unset = UNSET,
    started_after: datetime.datetime | Unset = UNSET,
    started_before: datetime.datetime | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["offset"] = offset

    params["limit"] = limit

    params["desc"] = desc

    params["status"] = status

    json_started_after: str | Unset = UNSET
    if not isinstance(started_after, Unset):
        json_started_after = started_after.isoformat()
    params["startedAfter"] = json_started_after

    json_started_before: str | Unset = UNSET
    if not isinstance(started_before, Unset):
        json_started_before = started_before.isoformat()
    params["startedBefore"] = json_started_before


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/actor-runs",
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetUserRunsListResponse | None:
    if response.status_code == 200:
        response_200 = GetUserRunsListResponse.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetUserRunsListResponse]:
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
    status: str | Unset = UNSET,
    started_after: datetime.datetime | Unset = UNSET,
    started_before: datetime.datetime | Unset = UNSET,

) -> Response[GetUserRunsListResponse]:
    """ Get user runs list

     Gets a list of all runs for a user. The response is a list of objects, where
    each object contains basic information about a single Actor run.

    The endpoint supports pagination using the `limit` and `offset` parameters
    and it will not return more than 1000 array elements.

    By default, the records are sorted by the `startedAt` field in ascending
    order. Therefore, you can use pagination to incrementally fetch all records while
    new ones are still being created. To sort the records in descending order, use
    `desc=1` parameter. You can also filter runs by `startedAt`` and `status`` fields ([available
    statuses](https://docs.apify.com/platform/actors/running/runs-and-builds#lifecycle)).

    Args:
        offset (float | Unset):  Example: 10.
        limit (float | Unset):  Example: 99.
        desc (bool | Unset):  Example: True.
        status (str | Unset):  Example: SUCCEEDED.
        started_after (datetime.datetime | Unset):  Example: 2025-09-01T00:00:00.000Z.
        started_before (datetime.datetime | Unset):  Example: 2025-09-17T23:59:59.000Z.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetUserRunsListResponse]
     """


    kwargs = _get_kwargs(
        offset=offset,
limit=limit,
desc=desc,
status=status,
started_after=started_after,
started_before=started_before,

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
    status: str | Unset = UNSET,
    started_after: datetime.datetime | Unset = UNSET,
    started_before: datetime.datetime | Unset = UNSET,

) -> GetUserRunsListResponse | None:
    """ Get user runs list

     Gets a list of all runs for a user. The response is a list of objects, where
    each object contains basic information about a single Actor run.

    The endpoint supports pagination using the `limit` and `offset` parameters
    and it will not return more than 1000 array elements.

    By default, the records are sorted by the `startedAt` field in ascending
    order. Therefore, you can use pagination to incrementally fetch all records while
    new ones are still being created. To sort the records in descending order, use
    `desc=1` parameter. You can also filter runs by `startedAt`` and `status`` fields ([available
    statuses](https://docs.apify.com/platform/actors/running/runs-and-builds#lifecycle)).

    Args:
        offset (float | Unset):  Example: 10.
        limit (float | Unset):  Example: 99.
        desc (bool | Unset):  Example: True.
        status (str | Unset):  Example: SUCCEEDED.
        started_after (datetime.datetime | Unset):  Example: 2025-09-01T00:00:00.000Z.
        started_before (datetime.datetime | Unset):  Example: 2025-09-17T23:59:59.000Z.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetUserRunsListResponse
     """


    return sync_detailed(
        client=client,
offset=offset,
limit=limit,
desc=desc,
status=status,
started_after=started_after,
started_before=started_before,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    desc: bool | Unset = UNSET,
    status: str | Unset = UNSET,
    started_after: datetime.datetime | Unset = UNSET,
    started_before: datetime.datetime | Unset = UNSET,

) -> Response[GetUserRunsListResponse]:
    """ Get user runs list

     Gets a list of all runs for a user. The response is a list of objects, where
    each object contains basic information about a single Actor run.

    The endpoint supports pagination using the `limit` and `offset` parameters
    and it will not return more than 1000 array elements.

    By default, the records are sorted by the `startedAt` field in ascending
    order. Therefore, you can use pagination to incrementally fetch all records while
    new ones are still being created. To sort the records in descending order, use
    `desc=1` parameter. You can also filter runs by `startedAt`` and `status`` fields ([available
    statuses](https://docs.apify.com/platform/actors/running/runs-and-builds#lifecycle)).

    Args:
        offset (float | Unset):  Example: 10.
        limit (float | Unset):  Example: 99.
        desc (bool | Unset):  Example: True.
        status (str | Unset):  Example: SUCCEEDED.
        started_after (datetime.datetime | Unset):  Example: 2025-09-01T00:00:00.000Z.
        started_before (datetime.datetime | Unset):  Example: 2025-09-17T23:59:59.000Z.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetUserRunsListResponse]
     """


    kwargs = _get_kwargs(
        offset=offset,
limit=limit,
desc=desc,
status=status,
started_after=started_after,
started_before=started_before,

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
    status: str | Unset = UNSET,
    started_after: datetime.datetime | Unset = UNSET,
    started_before: datetime.datetime | Unset = UNSET,

) -> GetUserRunsListResponse | None:
    """ Get user runs list

     Gets a list of all runs for a user. The response is a list of objects, where
    each object contains basic information about a single Actor run.

    The endpoint supports pagination using the `limit` and `offset` parameters
    and it will not return more than 1000 array elements.

    By default, the records are sorted by the `startedAt` field in ascending
    order. Therefore, you can use pagination to incrementally fetch all records while
    new ones are still being created. To sort the records in descending order, use
    `desc=1` parameter. You can also filter runs by `startedAt`` and `status`` fields ([available
    statuses](https://docs.apify.com/platform/actors/running/runs-and-builds#lifecycle)).

    Args:
        offset (float | Unset):  Example: 10.
        limit (float | Unset):  Example: 99.
        desc (bool | Unset):  Example: True.
        status (str | Unset):  Example: SUCCEEDED.
        started_after (datetime.datetime | Unset):  Example: 2025-09-01T00:00:00.000Z.
        started_before (datetime.datetime | Unset):  Example: 2025-09-17T23:59:59.000Z.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetUserRunsListResponse
     """


    return (await asyncio_detailed(
        client=client,
offset=offset,
limit=limit,
desc=desc,
status=status,
started_after=started_after,
started_before=started_before,

    )).parsed

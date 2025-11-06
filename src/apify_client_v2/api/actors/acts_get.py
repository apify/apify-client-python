from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.acts_get_sort_by import ActsGetSortBy
from ...models.get_list_of_actors_response import GetListOfActorsResponse
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    *,
    my: bool | Unset = UNSET,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    desc: bool | Unset = UNSET,
    sort_by: ActsGetSortBy | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["my"] = my

    params["offset"] = offset

    params["limit"] = limit

    params["desc"] = desc

    json_sort_by: str | Unset = UNSET
    if not isinstance(sort_by, Unset):
        json_sort_by = sort_by.value

    params["sortBy"] = json_sort_by


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/acts",
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetListOfActorsResponse | None:
    if response.status_code == 200:
        response_200 = GetListOfActorsResponse.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetListOfActorsResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    my: bool | Unset = UNSET,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    desc: bool | Unset = UNSET,
    sort_by: ActsGetSortBy | Unset = UNSET,

) -> Response[GetListOfActorsResponse]:
    """ Get list of Actors

     Gets the list of all Actors that the user created or used. The response is a
    list of objects, where each object contains a basic information about a single Actor.

    To only get Actors created by the user, add the `my=1` query parameter.

    The endpoint supports pagination using the `limit` and `offset` parameters
    and it will not return more than 1000 records.

    By default, the records are sorted by the `createdAt` field in ascending
    order, therefore you can use pagination to incrementally fetch all Actors while new
    ones are still being created. To sort the records in descending order, use the `desc=1` parameter.

    You can also sort by your last run by using the `sortBy=stats.lastRunStartedAt` query parameter.
    In this case, descending order means the most recently run Actor appears first.

    Args:
        my (bool | Unset):  Example: True.
        offset (float | Unset):  Example: 10.
        limit (float | Unset):  Example: 99.
        desc (bool | Unset):  Example: True.
        sort_by (ActsGetSortBy | Unset):  Example: createdAt.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetListOfActorsResponse]
     """


    kwargs = _get_kwargs(
        my=my,
offset=offset,
limit=limit,
desc=desc,
sort_by=sort_by,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient | Client,
    my: bool | Unset = UNSET,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    desc: bool | Unset = UNSET,
    sort_by: ActsGetSortBy | Unset = UNSET,

) -> GetListOfActorsResponse | None:
    """ Get list of Actors

     Gets the list of all Actors that the user created or used. The response is a
    list of objects, where each object contains a basic information about a single Actor.

    To only get Actors created by the user, add the `my=1` query parameter.

    The endpoint supports pagination using the `limit` and `offset` parameters
    and it will not return more than 1000 records.

    By default, the records are sorted by the `createdAt` field in ascending
    order, therefore you can use pagination to incrementally fetch all Actors while new
    ones are still being created. To sort the records in descending order, use the `desc=1` parameter.

    You can also sort by your last run by using the `sortBy=stats.lastRunStartedAt` query parameter.
    In this case, descending order means the most recently run Actor appears first.

    Args:
        my (bool | Unset):  Example: True.
        offset (float | Unset):  Example: 10.
        limit (float | Unset):  Example: 99.
        desc (bool | Unset):  Example: True.
        sort_by (ActsGetSortBy | Unset):  Example: createdAt.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetListOfActorsResponse
     """


    return sync_detailed(
        client=client,
my=my,
offset=offset,
limit=limit,
desc=desc,
sort_by=sort_by,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    my: bool | Unset = UNSET,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    desc: bool | Unset = UNSET,
    sort_by: ActsGetSortBy | Unset = UNSET,

) -> Response[GetListOfActorsResponse]:
    """ Get list of Actors

     Gets the list of all Actors that the user created or used. The response is a
    list of objects, where each object contains a basic information about a single Actor.

    To only get Actors created by the user, add the `my=1` query parameter.

    The endpoint supports pagination using the `limit` and `offset` parameters
    and it will not return more than 1000 records.

    By default, the records are sorted by the `createdAt` field in ascending
    order, therefore you can use pagination to incrementally fetch all Actors while new
    ones are still being created. To sort the records in descending order, use the `desc=1` parameter.

    You can also sort by your last run by using the `sortBy=stats.lastRunStartedAt` query parameter.
    In this case, descending order means the most recently run Actor appears first.

    Args:
        my (bool | Unset):  Example: True.
        offset (float | Unset):  Example: 10.
        limit (float | Unset):  Example: 99.
        desc (bool | Unset):  Example: True.
        sort_by (ActsGetSortBy | Unset):  Example: createdAt.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetListOfActorsResponse]
     """


    kwargs = _get_kwargs(
        my=my,
offset=offset,
limit=limit,
desc=desc,
sort_by=sort_by,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    my: bool | Unset = UNSET,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    desc: bool | Unset = UNSET,
    sort_by: ActsGetSortBy | Unset = UNSET,

) -> GetListOfActorsResponse | None:
    """ Get list of Actors

     Gets the list of all Actors that the user created or used. The response is a
    list of objects, where each object contains a basic information about a single Actor.

    To only get Actors created by the user, add the `my=1` query parameter.

    The endpoint supports pagination using the `limit` and `offset` parameters
    and it will not return more than 1000 records.

    By default, the records are sorted by the `createdAt` field in ascending
    order, therefore you can use pagination to incrementally fetch all Actors while new
    ones are still being created. To sort the records in descending order, use the `desc=1` parameter.

    You can also sort by your last run by using the `sortBy=stats.lastRunStartedAt` query parameter.
    In this case, descending order means the most recently run Actor appears first.

    Args:
        my (bool | Unset):  Example: True.
        offset (float | Unset):  Example: 10.
        limit (float | Unset):  Example: 99.
        desc (bool | Unset):  Example: True.
        sort_by (ActsGetSortBy | Unset):  Example: createdAt.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetListOfActorsResponse
     """


    return (await asyncio_detailed(
        client=client,
my=my,
offset=offset,
limit=limit,
desc=desc,
sort_by=sort_by,

    )).parsed

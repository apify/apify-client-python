from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.get_list_of_datasets_response import GetListOfDatasetsResponse
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    *,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    desc: bool | Unset = UNSET,
    unnamed: bool | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["offset"] = offset

    params["limit"] = limit

    params["desc"] = desc

    params["unnamed"] = unnamed


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/datasets",
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetListOfDatasetsResponse | None:
    if response.status_code == 200:
        response_200 = GetListOfDatasetsResponse.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetListOfDatasetsResponse]:
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
    unnamed: bool | Unset = UNSET,

) -> Response[GetListOfDatasetsResponse]:
    """ Get list of datasets

     Lists all of a user's datasets.

    The response is a JSON array of objects,
    where each object contains basic information about one dataset.

    By default, the objects are sorted by the `createdAt` field in ascending
    order, therefore you can use pagination to incrementally fetch all datasets while new
    ones are still being created. To sort them in descending order, use `desc=1`
    parameter. The endpoint supports pagination using `limit` and `offset`
    parameters and it will not return more than 1000 array elements.

    Args:
        offset (float | Unset):  Example: 10.
        limit (float | Unset):  Example: 99.
        desc (bool | Unset):  Example: True.
        unnamed (bool | Unset):  Example: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetListOfDatasetsResponse]
     """


    kwargs = _get_kwargs(
        offset=offset,
limit=limit,
desc=desc,
unnamed=unnamed,

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
    unnamed: bool | Unset = UNSET,

) -> GetListOfDatasetsResponse | None:
    """ Get list of datasets

     Lists all of a user's datasets.

    The response is a JSON array of objects,
    where each object contains basic information about one dataset.

    By default, the objects are sorted by the `createdAt` field in ascending
    order, therefore you can use pagination to incrementally fetch all datasets while new
    ones are still being created. To sort them in descending order, use `desc=1`
    parameter. The endpoint supports pagination using `limit` and `offset`
    parameters and it will not return more than 1000 array elements.

    Args:
        offset (float | Unset):  Example: 10.
        limit (float | Unset):  Example: 99.
        desc (bool | Unset):  Example: True.
        unnamed (bool | Unset):  Example: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetListOfDatasetsResponse
     """


    return sync_detailed(
        client=client,
offset=offset,
limit=limit,
desc=desc,
unnamed=unnamed,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    desc: bool | Unset = UNSET,
    unnamed: bool | Unset = UNSET,

) -> Response[GetListOfDatasetsResponse]:
    """ Get list of datasets

     Lists all of a user's datasets.

    The response is a JSON array of objects,
    where each object contains basic information about one dataset.

    By default, the objects are sorted by the `createdAt` field in ascending
    order, therefore you can use pagination to incrementally fetch all datasets while new
    ones are still being created. To sort them in descending order, use `desc=1`
    parameter. The endpoint supports pagination using `limit` and `offset`
    parameters and it will not return more than 1000 array elements.

    Args:
        offset (float | Unset):  Example: 10.
        limit (float | Unset):  Example: 99.
        desc (bool | Unset):  Example: True.
        unnamed (bool | Unset):  Example: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetListOfDatasetsResponse]
     """


    kwargs = _get_kwargs(
        offset=offset,
limit=limit,
desc=desc,
unnamed=unnamed,

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
    unnamed: bool | Unset = UNSET,

) -> GetListOfDatasetsResponse | None:
    """ Get list of datasets

     Lists all of a user's datasets.

    The response is a JSON array of objects,
    where each object contains basic information about one dataset.

    By default, the objects are sorted by the `createdAt` field in ascending
    order, therefore you can use pagination to incrementally fetch all datasets while new
    ones are still being created. To sort them in descending order, use `desc=1`
    parameter. The endpoint supports pagination using `limit` and `offset`
    parameters and it will not return more than 1000 array elements.

    Args:
        offset (float | Unset):  Example: 10.
        limit (float | Unset):  Example: 99.
        desc (bool | Unset):  Example: True.
        unnamed (bool | Unset):  Example: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetListOfDatasetsResponse
     """


    return (await asyncio_detailed(
        client=client,
offset=offset,
limit=limit,
desc=desc,
unnamed=unnamed,

    )).parsed

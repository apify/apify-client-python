from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.dataset_response import DatasetResponse
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    *,
    name: str | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["name"] = name


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v2/datasets",
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> DatasetResponse | None:
    if response.status_code == 201:
        response_201 = DatasetResponse.from_dict(response.json())



        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[DatasetResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    name: str | Unset = UNSET,

) -> Response[DatasetResponse]:
    """ Create dataset

     Creates a dataset and returns its object.
    Keep in mind that data stored under unnamed dataset follows [data retention
    period](https://docs.apify.com/platform/storage#data-retention).
    It creates a dataset with the given name if the parameter name is used.
    If a dataset with the given name already exists then returns its object.

    Args:
        name (str | Unset):  Example: eshop-items.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DatasetResponse]
     """


    kwargs = _get_kwargs(
        name=name,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient | Client,
    name: str | Unset = UNSET,

) -> DatasetResponse | None:
    """ Create dataset

     Creates a dataset and returns its object.
    Keep in mind that data stored under unnamed dataset follows [data retention
    period](https://docs.apify.com/platform/storage#data-retention).
    It creates a dataset with the given name if the parameter name is used.
    If a dataset with the given name already exists then returns its object.

    Args:
        name (str | Unset):  Example: eshop-items.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DatasetResponse
     """


    return sync_detailed(
        client=client,
name=name,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    name: str | Unset = UNSET,

) -> Response[DatasetResponse]:
    """ Create dataset

     Creates a dataset and returns its object.
    Keep in mind that data stored under unnamed dataset follows [data retention
    period](https://docs.apify.com/platform/storage#data-retention).
    It creates a dataset with the given name if the parameter name is used.
    If a dataset with the given name already exists then returns its object.

    Args:
        name (str | Unset):  Example: eshop-items.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DatasetResponse]
     """


    kwargs = _get_kwargs(
        name=name,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    name: str | Unset = UNSET,

) -> DatasetResponse | None:
    """ Create dataset

     Creates a dataset and returns its object.
    Keep in mind that data stored under unnamed dataset follows [data retention
    period](https://docs.apify.com/platform/storage#data-retention).
    It creates a dataset with the given name if the parameter name is used.
    If a dataset with the given name already exists then returns its object.

    Args:
        name (str | Unset):  Example: eshop-items.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DatasetResponse
     """


    return (await asyncio_detailed(
        client=client,
name=name,

    )).parsed

from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.get_store_response import GetStoreResponse
from typing import cast



def _get_kwargs(
    store_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/key-value-stores/{store_id}".format(store_id=store_id,),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetStoreResponse | None:
    if response.status_code == 200:
        response_200 = GetStoreResponse.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetStoreResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    store_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[GetStoreResponse]:
    """ Get store

     Gets an object that contains all the details about a specific key-value
    store.

    Args:
        store_id (str):  Example: WkzbQMuFYuamGv3YF.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetStoreResponse]
     """


    kwargs = _get_kwargs(
        store_id=store_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    store_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> GetStoreResponse | None:
    """ Get store

     Gets an object that contains all the details about a specific key-value
    store.

    Args:
        store_id (str):  Example: WkzbQMuFYuamGv3YF.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetStoreResponse
     """


    return sync_detailed(
        store_id=store_id,
client=client,

    ).parsed

async def asyncio_detailed(
    store_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[GetStoreResponse]:
    """ Get store

     Gets an object that contains all the details about a specific key-value
    store.

    Args:
        store_id (str):  Example: WkzbQMuFYuamGv3YF.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetStoreResponse]
     """


    kwargs = _get_kwargs(
        store_id=store_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    store_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> GetStoreResponse | None:
    """ Get store

     Gets an object that contains all the details about a specific key-value
    store.

    Args:
        store_id (str):  Example: WkzbQMuFYuamGv3YF.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetStoreResponse
     """


    return (await asyncio_detailed(
        store_id=store_id,
client=client,

    )).parsed

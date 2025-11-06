from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.create_key_value_store_response import CreateKeyValueStoreResponse
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
        "url": "/v2/key-value-stores",
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> CreateKeyValueStoreResponse | None:
    if response.status_code == 201:
        response_201 = CreateKeyValueStoreResponse.from_dict(response.json())



        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[CreateKeyValueStoreResponse]:
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

) -> Response[CreateKeyValueStoreResponse]:
    """ Create key-value store

     Creates a key-value store and returns its object. The response is the same
    object as returned by the [Get store](#/reference/key-value-stores/store-object/get-store)
    endpoint.

    Keep in mind that data stored under unnamed store follows [data retention
    period](https://docs.apify.com/platform/storage#data-retention).

    It creates a store with the given name if the parameter name is used.
    If there is another store with the same name, the endpoint does not create a
    new one and returns the existing object instead.

    Args:
        name (str | Unset):  Example: eshop-values.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateKeyValueStoreResponse]
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

) -> CreateKeyValueStoreResponse | None:
    """ Create key-value store

     Creates a key-value store and returns its object. The response is the same
    object as returned by the [Get store](#/reference/key-value-stores/store-object/get-store)
    endpoint.

    Keep in mind that data stored under unnamed store follows [data retention
    period](https://docs.apify.com/platform/storage#data-retention).

    It creates a store with the given name if the parameter name is used.
    If there is another store with the same name, the endpoint does not create a
    new one and returns the existing object instead.

    Args:
        name (str | Unset):  Example: eshop-values.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateKeyValueStoreResponse
     """


    return sync_detailed(
        client=client,
name=name,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    name: str | Unset = UNSET,

) -> Response[CreateKeyValueStoreResponse]:
    """ Create key-value store

     Creates a key-value store and returns its object. The response is the same
    object as returned by the [Get store](#/reference/key-value-stores/store-object/get-store)
    endpoint.

    Keep in mind that data stored under unnamed store follows [data retention
    period](https://docs.apify.com/platform/storage#data-retention).

    It creates a store with the given name if the parameter name is used.
    If there is another store with the same name, the endpoint does not create a
    new one and returns the existing object instead.

    Args:
        name (str | Unset):  Example: eshop-values.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateKeyValueStoreResponse]
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

) -> CreateKeyValueStoreResponse | None:
    """ Create key-value store

     Creates a key-value store and returns its object. The response is the same
    object as returned by the [Get store](#/reference/key-value-stores/store-object/get-store)
    endpoint.

    Keep in mind that data stored under unnamed store follows [data retention
    period](https://docs.apify.com/platform/storage#data-retention).

    It creates a store with the given name if the parameter name is used.
    If there is another store with the same name, the endpoint does not create a
    new one and returns the existing object instead.

    Args:
        name (str | Unset):  Example: eshop-values.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateKeyValueStoreResponse
     """


    return (await asyncio_detailed(
        client=client,
name=name,

    )).parsed

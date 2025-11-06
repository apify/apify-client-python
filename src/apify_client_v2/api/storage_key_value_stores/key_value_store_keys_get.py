from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.get_list_of_keys_response import GetListOfKeysResponse
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    store_id: str,
    *,
    exclusive_start_key: str | Unset = UNSET,
    limit: float | Unset = UNSET,
    collection: str | Unset = UNSET,
    prefix: str | Unset = UNSET,
    signature: str | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["exclusiveStartKey"] = exclusive_start_key

    params["limit"] = limit

    params["collection"] = collection

    params["prefix"] = prefix

    params["signature"] = signature


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/key-value-stores/{store_id}/keys".format(store_id=store_id,),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetListOfKeysResponse | None:
    if response.status_code == 200:
        response_200 = GetListOfKeysResponse.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetListOfKeysResponse]:
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
    exclusive_start_key: str | Unset = UNSET,
    limit: float | Unset = UNSET,
    collection: str | Unset = UNSET,
    prefix: str | Unset = UNSET,
    signature: str | Unset = UNSET,

) -> Response[GetListOfKeysResponse]:
    """ Get list of keys

     Returns a list of objects describing keys of a given key-value store, as
    well as some information about the values (e.g. size).

    This endpoint is paginated using `exclusiveStartKey` and `limit` parameters
    - see [Pagination](/api/v2#using-key) for more details.

    Args:
        store_id (str):  Example: WkzbQMuFYuamGv3YF.
        exclusive_start_key (str | Unset):  Example: Ihnsp8YrvJ8102Kj.
        limit (float | Unset):  Example: 100.
        collection (str | Unset):  Example: postImages.
        prefix (str | Unset):  Example: post-images-.
        signature (str | Unset):  Example: 2wTI46Bg8qWQrV7tavlPI.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetListOfKeysResponse]
     """


    kwargs = _get_kwargs(
        store_id=store_id,
exclusive_start_key=exclusive_start_key,
limit=limit,
collection=collection,
prefix=prefix,
signature=signature,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    store_id: str,
    *,
    client: AuthenticatedClient | Client,
    exclusive_start_key: str | Unset = UNSET,
    limit: float | Unset = UNSET,
    collection: str | Unset = UNSET,
    prefix: str | Unset = UNSET,
    signature: str | Unset = UNSET,

) -> GetListOfKeysResponse | None:
    """ Get list of keys

     Returns a list of objects describing keys of a given key-value store, as
    well as some information about the values (e.g. size).

    This endpoint is paginated using `exclusiveStartKey` and `limit` parameters
    - see [Pagination](/api/v2#using-key) for more details.

    Args:
        store_id (str):  Example: WkzbQMuFYuamGv3YF.
        exclusive_start_key (str | Unset):  Example: Ihnsp8YrvJ8102Kj.
        limit (float | Unset):  Example: 100.
        collection (str | Unset):  Example: postImages.
        prefix (str | Unset):  Example: post-images-.
        signature (str | Unset):  Example: 2wTI46Bg8qWQrV7tavlPI.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetListOfKeysResponse
     """


    return sync_detailed(
        store_id=store_id,
client=client,
exclusive_start_key=exclusive_start_key,
limit=limit,
collection=collection,
prefix=prefix,
signature=signature,

    ).parsed

async def asyncio_detailed(
    store_id: str,
    *,
    client: AuthenticatedClient | Client,
    exclusive_start_key: str | Unset = UNSET,
    limit: float | Unset = UNSET,
    collection: str | Unset = UNSET,
    prefix: str | Unset = UNSET,
    signature: str | Unset = UNSET,

) -> Response[GetListOfKeysResponse]:
    """ Get list of keys

     Returns a list of objects describing keys of a given key-value store, as
    well as some information about the values (e.g. size).

    This endpoint is paginated using `exclusiveStartKey` and `limit` parameters
    - see [Pagination](/api/v2#using-key) for more details.

    Args:
        store_id (str):  Example: WkzbQMuFYuamGv3YF.
        exclusive_start_key (str | Unset):  Example: Ihnsp8YrvJ8102Kj.
        limit (float | Unset):  Example: 100.
        collection (str | Unset):  Example: postImages.
        prefix (str | Unset):  Example: post-images-.
        signature (str | Unset):  Example: 2wTI46Bg8qWQrV7tavlPI.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetListOfKeysResponse]
     """


    kwargs = _get_kwargs(
        store_id=store_id,
exclusive_start_key=exclusive_start_key,
limit=limit,
collection=collection,
prefix=prefix,
signature=signature,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    store_id: str,
    *,
    client: AuthenticatedClient | Client,
    exclusive_start_key: str | Unset = UNSET,
    limit: float | Unset = UNSET,
    collection: str | Unset = UNSET,
    prefix: str | Unset = UNSET,
    signature: str | Unset = UNSET,

) -> GetListOfKeysResponse | None:
    """ Get list of keys

     Returns a list of objects describing keys of a given key-value store, as
    well as some information about the values (e.g. size).

    This endpoint is paginated using `exclusiveStartKey` and `limit` parameters
    - see [Pagination](/api/v2#using-key) for more details.

    Args:
        store_id (str):  Example: WkzbQMuFYuamGv3YF.
        exclusive_start_key (str | Unset):  Example: Ihnsp8YrvJ8102Kj.
        limit (float | Unset):  Example: 100.
        collection (str | Unset):  Example: postImages.
        prefix (str | Unset):  Example: post-images-.
        signature (str | Unset):  Example: 2wTI46Bg8qWQrV7tavlPI.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetListOfKeysResponse
     """


    return (await asyncio_detailed(
        store_id=store_id,
client=client,
exclusive_start_key=exclusive_start_key,
limit=limit,
collection=collection,
prefix=prefix,
signature=signature,

    )).parsed

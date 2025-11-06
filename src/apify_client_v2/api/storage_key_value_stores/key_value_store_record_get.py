from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.key_value_store_record_get_response_200 import KeyValueStoreRecordGetResponse200
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    store_id: str,
    record_key: str,
    *,
    signature: str | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["signature"] = signature


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/key-value-stores/{store_id}/records/{record_key}".format(store_id=store_id,record_key=record_key,),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | KeyValueStoreRecordGetResponse200 | None:
    if response.status_code == 200:
        response_200 = KeyValueStoreRecordGetResponse200.from_dict(response.json())



        return response_200

    if response.status_code == 302:
        response_302 = cast(Any, None)
        return response_302

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | KeyValueStoreRecordGetResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    store_id: str,
    record_key: str,
    *,
    client: AuthenticatedClient | Client,
    signature: str | Unset = UNSET,

) -> Response[Any | KeyValueStoreRecordGetResponse200]:
    """ Get record

     Gets a value stored in the key-value store under a specific key.

    The response body has the same `Content-Encoding` header as it was set in
    [Put record](#tag/Key-value-storesRecord/operation/keyValueStore_record_put).

    If the request does not define the `Accept-Encoding` HTTP header with the
    right encoding, the record will be decompressed.

    Most HTTP clients support decompression by default. After using the HTTP
    client with decompression support, the `Accept-Encoding` header is set by
    the client and body is decompressed automatically.

    Args:
        store_id (str):  Example: WkzbQMuFYuamGv3YF.
        record_key (str):  Example: someKey.
        signature (str | Unset):  Example: 2wTI46Bg8qWQrV7tavlPI.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | KeyValueStoreRecordGetResponse200]
     """


    kwargs = _get_kwargs(
        store_id=store_id,
record_key=record_key,
signature=signature,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    store_id: str,
    record_key: str,
    *,
    client: AuthenticatedClient | Client,
    signature: str | Unset = UNSET,

) -> Any | KeyValueStoreRecordGetResponse200 | None:
    """ Get record

     Gets a value stored in the key-value store under a specific key.

    The response body has the same `Content-Encoding` header as it was set in
    [Put record](#tag/Key-value-storesRecord/operation/keyValueStore_record_put).

    If the request does not define the `Accept-Encoding` HTTP header with the
    right encoding, the record will be decompressed.

    Most HTTP clients support decompression by default. After using the HTTP
    client with decompression support, the `Accept-Encoding` header is set by
    the client and body is decompressed automatically.

    Args:
        store_id (str):  Example: WkzbQMuFYuamGv3YF.
        record_key (str):  Example: someKey.
        signature (str | Unset):  Example: 2wTI46Bg8qWQrV7tavlPI.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | KeyValueStoreRecordGetResponse200
     """


    return sync_detailed(
        store_id=store_id,
record_key=record_key,
client=client,
signature=signature,

    ).parsed

async def asyncio_detailed(
    store_id: str,
    record_key: str,
    *,
    client: AuthenticatedClient | Client,
    signature: str | Unset = UNSET,

) -> Response[Any | KeyValueStoreRecordGetResponse200]:
    """ Get record

     Gets a value stored in the key-value store under a specific key.

    The response body has the same `Content-Encoding` header as it was set in
    [Put record](#tag/Key-value-storesRecord/operation/keyValueStore_record_put).

    If the request does not define the `Accept-Encoding` HTTP header with the
    right encoding, the record will be decompressed.

    Most HTTP clients support decompression by default. After using the HTTP
    client with decompression support, the `Accept-Encoding` header is set by
    the client and body is decompressed automatically.

    Args:
        store_id (str):  Example: WkzbQMuFYuamGv3YF.
        record_key (str):  Example: someKey.
        signature (str | Unset):  Example: 2wTI46Bg8qWQrV7tavlPI.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | KeyValueStoreRecordGetResponse200]
     """


    kwargs = _get_kwargs(
        store_id=store_id,
record_key=record_key,
signature=signature,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    store_id: str,
    record_key: str,
    *,
    client: AuthenticatedClient | Client,
    signature: str | Unset = UNSET,

) -> Any | KeyValueStoreRecordGetResponse200 | None:
    """ Get record

     Gets a value stored in the key-value store under a specific key.

    The response body has the same `Content-Encoding` header as it was set in
    [Put record](#tag/Key-value-storesRecord/operation/keyValueStore_record_put).

    If the request does not define the `Accept-Encoding` HTTP header with the
    right encoding, the record will be decompressed.

    Most HTTP clients support decompression by default. After using the HTTP
    client with decompression support, the `Accept-Encoding` header is set by
    the client and body is decompressed automatically.

    Args:
        store_id (str):  Example: WkzbQMuFYuamGv3YF.
        record_key (str):  Example: someKey.
        signature (str | Unset):  Example: 2wTI46Bg8qWQrV7tavlPI.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | KeyValueStoreRecordGetResponse200
     """


    return (await asyncio_detailed(
        store_id=store_id,
record_key=record_key,
client=client,
signature=signature,

    )).parsed

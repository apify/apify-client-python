from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.key_value_store_record_put_content_encoding import KeyValueStoreRecordPutContentEncoding
from ...models.key_value_store_record_put_response_201 import KeyValueStoreRecordPutResponse201
from ...models.put_record_request import PutRecordRequest
from typing import cast



def _get_kwargs(
    store_id: str,
    record_key: str,
    *,
    body: PutRecordRequest,
    content_encoding: KeyValueStoreRecordPutContentEncoding,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Content-Encoding"] = str(content_encoding)




    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v2/key-value-stores/{store_id}/records/{record_key}".format(store_id=store_id,record_key=record_key,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> KeyValueStoreRecordPutResponse201 | None:
    if response.status_code == 201:
        response_201 = KeyValueStoreRecordPutResponse201.from_dict(response.json())



        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[KeyValueStoreRecordPutResponse201]:
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
    body: PutRecordRequest,
    content_encoding: KeyValueStoreRecordPutContentEncoding,

) -> Response[KeyValueStoreRecordPutResponse201]:
    """ Store record

     Stores a value under a specific key to the key-value store.

    The value is passed as the PUT payload and it is stored with a MIME content
    type defined by the `Content-Type` header and with encoding defined by the
    `Content-Encoding` header.

    To save bandwidth, storage, and speed up your upload, send the request
    payload compressed with Gzip compression and add the `Content-Encoding: gzip`
    header. It is possible to set up another compression type with `Content-Encoding`
    request header.

    Below is a list of supported `Content-Encoding` types.

    * Gzip compression: `Content-Encoding: gzip`
    * Deflate compression: `Content-Encoding: deflate`
    * Brotli compression: `Content-Encoding: br`

    Args:
        store_id (str):  Example: WkzbQMuFYuamGv3YF.
        record_key (str):  Example: someKey.
        content_encoding (KeyValueStoreRecordPutContentEncoding):  Example: gzip.
        body (PutRecordRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[KeyValueStoreRecordPutResponse201]
     """


    kwargs = _get_kwargs(
        store_id=store_id,
record_key=record_key,
body=body,
content_encoding=content_encoding,

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
    body: PutRecordRequest,
    content_encoding: KeyValueStoreRecordPutContentEncoding,

) -> KeyValueStoreRecordPutResponse201 | None:
    """ Store record

     Stores a value under a specific key to the key-value store.

    The value is passed as the PUT payload and it is stored with a MIME content
    type defined by the `Content-Type` header and with encoding defined by the
    `Content-Encoding` header.

    To save bandwidth, storage, and speed up your upload, send the request
    payload compressed with Gzip compression and add the `Content-Encoding: gzip`
    header. It is possible to set up another compression type with `Content-Encoding`
    request header.

    Below is a list of supported `Content-Encoding` types.

    * Gzip compression: `Content-Encoding: gzip`
    * Deflate compression: `Content-Encoding: deflate`
    * Brotli compression: `Content-Encoding: br`

    Args:
        store_id (str):  Example: WkzbQMuFYuamGv3YF.
        record_key (str):  Example: someKey.
        content_encoding (KeyValueStoreRecordPutContentEncoding):  Example: gzip.
        body (PutRecordRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        KeyValueStoreRecordPutResponse201
     """


    return sync_detailed(
        store_id=store_id,
record_key=record_key,
client=client,
body=body,
content_encoding=content_encoding,

    ).parsed

async def asyncio_detailed(
    store_id: str,
    record_key: str,
    *,
    client: AuthenticatedClient | Client,
    body: PutRecordRequest,
    content_encoding: KeyValueStoreRecordPutContentEncoding,

) -> Response[KeyValueStoreRecordPutResponse201]:
    """ Store record

     Stores a value under a specific key to the key-value store.

    The value is passed as the PUT payload and it is stored with a MIME content
    type defined by the `Content-Type` header and with encoding defined by the
    `Content-Encoding` header.

    To save bandwidth, storage, and speed up your upload, send the request
    payload compressed with Gzip compression and add the `Content-Encoding: gzip`
    header. It is possible to set up another compression type with `Content-Encoding`
    request header.

    Below is a list of supported `Content-Encoding` types.

    * Gzip compression: `Content-Encoding: gzip`
    * Deflate compression: `Content-Encoding: deflate`
    * Brotli compression: `Content-Encoding: br`

    Args:
        store_id (str):  Example: WkzbQMuFYuamGv3YF.
        record_key (str):  Example: someKey.
        content_encoding (KeyValueStoreRecordPutContentEncoding):  Example: gzip.
        body (PutRecordRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[KeyValueStoreRecordPutResponse201]
     """


    kwargs = _get_kwargs(
        store_id=store_id,
record_key=record_key,
body=body,
content_encoding=content_encoding,

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
    body: PutRecordRequest,
    content_encoding: KeyValueStoreRecordPutContentEncoding,

) -> KeyValueStoreRecordPutResponse201 | None:
    """ Store record

     Stores a value under a specific key to the key-value store.

    The value is passed as the PUT payload and it is stored with a MIME content
    type defined by the `Content-Type` header and with encoding defined by the
    `Content-Encoding` header.

    To save bandwidth, storage, and speed up your upload, send the request
    payload compressed with Gzip compression and add the `Content-Encoding: gzip`
    header. It is possible to set up another compression type with `Content-Encoding`
    request header.

    Below is a list of supported `Content-Encoding` types.

    * Gzip compression: `Content-Encoding: gzip`
    * Deflate compression: `Content-Encoding: deflate`
    * Brotli compression: `Content-Encoding: br`

    Args:
        store_id (str):  Example: WkzbQMuFYuamGv3YF.
        record_key (str):  Example: someKey.
        content_encoding (KeyValueStoreRecordPutContentEncoding):  Example: gzip.
        body (PutRecordRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        KeyValueStoreRecordPutResponse201
     """


    return (await asyncio_detailed(
        store_id=store_id,
record_key=record_key,
client=client,
body=body,
content_encoding=content_encoding,

    )).parsed

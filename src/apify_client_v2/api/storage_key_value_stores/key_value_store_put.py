from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.update_store_request import UpdateStoreRequest
from ...models.update_store_response import UpdateStoreResponse
from typing import cast



def _get_kwargs(
    store_id: str,
    *,
    body: UpdateStoreRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v2/key-value-stores/{store_id}".format(store_id=store_id,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> UpdateStoreResponse | None:
    if response.status_code == 200:
        response_200 = UpdateStoreResponse.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[UpdateStoreResponse]:
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
    body: UpdateStoreRequest,

) -> Response[UpdateStoreResponse]:
    """ Update store

     Updates a key-value store's name using a value specified by a JSON object
    passed in the PUT payload.

    The response is the updated key-value store object, as returned by the [Get
    store](#/reference/key-value-stores/store-object/get-store) API endpoint.

    Args:
        store_id (str):  Example: WkzbQMuFYuamGv3YF.
        body (UpdateStoreRequest):  Example: {'name': 'new-store-name'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UpdateStoreResponse]
     """


    kwargs = _get_kwargs(
        store_id=store_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    store_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateStoreRequest,

) -> UpdateStoreResponse | None:
    """ Update store

     Updates a key-value store's name using a value specified by a JSON object
    passed in the PUT payload.

    The response is the updated key-value store object, as returned by the [Get
    store](#/reference/key-value-stores/store-object/get-store) API endpoint.

    Args:
        store_id (str):  Example: WkzbQMuFYuamGv3YF.
        body (UpdateStoreRequest):  Example: {'name': 'new-store-name'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UpdateStoreResponse
     """


    return sync_detailed(
        store_id=store_id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    store_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateStoreRequest,

) -> Response[UpdateStoreResponse]:
    """ Update store

     Updates a key-value store's name using a value specified by a JSON object
    passed in the PUT payload.

    The response is the updated key-value store object, as returned by the [Get
    store](#/reference/key-value-stores/store-object/get-store) API endpoint.

    Args:
        store_id (str):  Example: WkzbQMuFYuamGv3YF.
        body (UpdateStoreRequest):  Example: {'name': 'new-store-name'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UpdateStoreResponse]
     """


    kwargs = _get_kwargs(
        store_id=store_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    store_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateStoreRequest,

) -> UpdateStoreResponse | None:
    """ Update store

     Updates a key-value store's name using a value specified by a JSON object
    passed in the PUT payload.

    The response is the updated key-value store object, as returned by the [Get
    store](#/reference/key-value-stores/store-object/get-store) API endpoint.

    Args:
        store_id (str):  Example: WkzbQMuFYuamGv3YF.
        body (UpdateStoreRequest):  Example: {'name': 'new-store-name'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UpdateStoreResponse
     """


    return (await asyncio_detailed(
        store_id=store_id,
client=client,
body=body,

    )).parsed

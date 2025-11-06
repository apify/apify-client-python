from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors




def _get_kwargs(
    store_id: str,
    record_key: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "head",
        "url": "/v2/key-value-stores/{store_id}/records/{record_key}".format(store_id=store_id,record_key=record_key,),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | None:
    if response.status_code == 200:
        return None

    if response.status_code == 404:
        return None

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any]:
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

) -> Response[Any]:
    """ Check if a record exists

     Check if a value is stored in the key-value store under a specific key.

    Args:
        store_id (str):  Example: WkzbQMuFYuamGv3YF.
        record_key (str):  Example: someKey.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        store_id=store_id,
record_key=record_key,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    store_id: str,
    record_key: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[Any]:
    """ Check if a record exists

     Check if a value is stored in the key-value store under a specific key.

    Args:
        store_id (str):  Example: WkzbQMuFYuamGv3YF.
        record_key (str):  Example: someKey.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        store_id=store_id,
record_key=record_key,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)


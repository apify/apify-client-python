from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.get_webhook_dispatch_response import GetWebhookDispatchResponse
from typing import cast



def _get_kwargs(
    dispatch_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/webhook-dispatches/{dispatch_id}".format(dispatch_id=dispatch_id,),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetWebhookDispatchResponse | None:
    if response.status_code == 200:
        response_200 = GetWebhookDispatchResponse.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetWebhookDispatchResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    dispatch_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[GetWebhookDispatchResponse]:
    """ Get webhook dispatch

     Gets webhook dispatch object with all details.

    Args:
        dispatch_id (str):  Example: Zib4xbZsmvZeK55ua.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetWebhookDispatchResponse]
     """


    kwargs = _get_kwargs(
        dispatch_id=dispatch_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    dispatch_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> GetWebhookDispatchResponse | None:
    """ Get webhook dispatch

     Gets webhook dispatch object with all details.

    Args:
        dispatch_id (str):  Example: Zib4xbZsmvZeK55ua.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetWebhookDispatchResponse
     """


    return sync_detailed(
        dispatch_id=dispatch_id,
client=client,

    ).parsed

async def asyncio_detailed(
    dispatch_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[GetWebhookDispatchResponse]:
    """ Get webhook dispatch

     Gets webhook dispatch object with all details.

    Args:
        dispatch_id (str):  Example: Zib4xbZsmvZeK55ua.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetWebhookDispatchResponse]
     """


    kwargs = _get_kwargs(
        dispatch_id=dispatch_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    dispatch_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> GetWebhookDispatchResponse | None:
    """ Get webhook dispatch

     Gets webhook dispatch object with all details.

    Args:
        dispatch_id (str):  Example: Zib4xbZsmvZeK55ua.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetWebhookDispatchResponse
     """


    return (await asyncio_detailed(
        dispatch_id=dispatch_id,
client=client,

    )).parsed

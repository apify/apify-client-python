from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.webhook_dispatch_list import WebhookDispatchList
from typing import cast



def _get_kwargs(
    webhook_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/webhooks/{webhook_id}/dispatches".format(webhook_id=webhook_id,),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> WebhookDispatchList | None:
    if response.status_code == 200:
        response_200 = WebhookDispatchList.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[WebhookDispatchList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    webhook_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[WebhookDispatchList]:
    """ Get collection

     Gets a given webhook's list of dispatches.

    Args:
        webhook_id (str):  Example: pVJtoTelgYUq4qJOt.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[WebhookDispatchList]
     """


    kwargs = _get_kwargs(
        webhook_id=webhook_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    webhook_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> WebhookDispatchList | None:
    """ Get collection

     Gets a given webhook's list of dispatches.

    Args:
        webhook_id (str):  Example: pVJtoTelgYUq4qJOt.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        WebhookDispatchList
     """


    return sync_detailed(
        webhook_id=webhook_id,
client=client,

    ).parsed

async def asyncio_detailed(
    webhook_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[WebhookDispatchList]:
    """ Get collection

     Gets a given webhook's list of dispatches.

    Args:
        webhook_id (str):  Example: pVJtoTelgYUq4qJOt.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[WebhookDispatchList]
     """


    kwargs = _get_kwargs(
        webhook_id=webhook_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    webhook_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> WebhookDispatchList | None:
    """ Get collection

     Gets a given webhook's list of dispatches.

    Args:
        webhook_id (str):  Example: pVJtoTelgYUq4qJOt.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        WebhookDispatchList
     """


    return (await asyncio_detailed(
        webhook_id=webhook_id,
client=client,

    )).parsed

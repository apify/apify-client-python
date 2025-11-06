from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.webhook_delete_response_204 import WebhookDeleteResponse204
from typing import cast



def _get_kwargs(
    webhook_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/v2/webhooks/{webhook_id}".format(webhook_id=webhook_id,),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> WebhookDeleteResponse204 | None:
    if response.status_code == 204:
        response_204 = WebhookDeleteResponse204.from_dict(response.json())



        return response_204

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[WebhookDeleteResponse204]:
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

) -> Response[WebhookDeleteResponse204]:
    """ Delete webhook

     Deletes a webhook.

    Args:
        webhook_id (str):  Example: Zib4xbZsmvZeK55ua.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[WebhookDeleteResponse204]
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

) -> WebhookDeleteResponse204 | None:
    """ Delete webhook

     Deletes a webhook.

    Args:
        webhook_id (str):  Example: Zib4xbZsmvZeK55ua.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        WebhookDeleteResponse204
     """


    return sync_detailed(
        webhook_id=webhook_id,
client=client,

    ).parsed

async def asyncio_detailed(
    webhook_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[WebhookDeleteResponse204]:
    """ Delete webhook

     Deletes a webhook.

    Args:
        webhook_id (str):  Example: Zib4xbZsmvZeK55ua.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[WebhookDeleteResponse204]
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

) -> WebhookDeleteResponse204 | None:
    """ Delete webhook

     Deletes a webhook.

    Args:
        webhook_id (str):  Example: Zib4xbZsmvZeK55ua.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        WebhookDeleteResponse204
     """


    return (await asyncio_detailed(
        webhook_id=webhook_id,
client=client,

    )).parsed

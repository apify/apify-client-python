from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.update_webhook_response import UpdateWebhookResponse
from ...models.webhook_update import WebhookUpdate
from typing import cast



def _get_kwargs(
    webhook_id: str,
    *,
    body: WebhookUpdate,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v2/webhooks/{webhook_id}".format(webhook_id=webhook_id,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> UpdateWebhookResponse | None:
    if response.status_code == 200:
        response_200 = UpdateWebhookResponse.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[UpdateWebhookResponse]:
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
    body: WebhookUpdate,

) -> Response[UpdateWebhookResponse]:
    """ Update webhook

     Updates a webhook using values specified by a webhook object passed as JSON
    in the POST payload.
    If the object does not define a specific property, its value will not be
    updated.

    The response is the full webhook object as returned by the
    [Get webhook](#/reference/webhooks/webhook-object/get-webhook) endpoint.

    The request needs to specify the `Content-Type: application/json` HTTP
    header!

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    Args:
        webhook_id (str):  Example: Zib4xbZsmvZeK55ua.
        body (WebhookUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UpdateWebhookResponse]
     """


    kwargs = _get_kwargs(
        webhook_id=webhook_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    webhook_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: WebhookUpdate,

) -> UpdateWebhookResponse | None:
    """ Update webhook

     Updates a webhook using values specified by a webhook object passed as JSON
    in the POST payload.
    If the object does not define a specific property, its value will not be
    updated.

    The response is the full webhook object as returned by the
    [Get webhook](#/reference/webhooks/webhook-object/get-webhook) endpoint.

    The request needs to specify the `Content-Type: application/json` HTTP
    header!

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    Args:
        webhook_id (str):  Example: Zib4xbZsmvZeK55ua.
        body (WebhookUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UpdateWebhookResponse
     """


    return sync_detailed(
        webhook_id=webhook_id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    webhook_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: WebhookUpdate,

) -> Response[UpdateWebhookResponse]:
    """ Update webhook

     Updates a webhook using values specified by a webhook object passed as JSON
    in the POST payload.
    If the object does not define a specific property, its value will not be
    updated.

    The response is the full webhook object as returned by the
    [Get webhook](#/reference/webhooks/webhook-object/get-webhook) endpoint.

    The request needs to specify the `Content-Type: application/json` HTTP
    header!

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    Args:
        webhook_id (str):  Example: Zib4xbZsmvZeK55ua.
        body (WebhookUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UpdateWebhookResponse]
     """


    kwargs = _get_kwargs(
        webhook_id=webhook_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    webhook_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: WebhookUpdate,

) -> UpdateWebhookResponse | None:
    """ Update webhook

     Updates a webhook using values specified by a webhook object passed as JSON
    in the POST payload.
    If the object does not define a specific property, its value will not be
    updated.

    The response is the full webhook object as returned by the
    [Get webhook](#/reference/webhooks/webhook-object/get-webhook) endpoint.

    The request needs to specify the `Content-Type: application/json` HTTP
    header!

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    Args:
        webhook_id (str):  Example: Zib4xbZsmvZeK55ua.
        body (WebhookUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UpdateWebhookResponse
     """


    return (await asyncio_detailed(
        webhook_id=webhook_id,
client=client,
body=body,

    )).parsed

from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.get_list_of_webhooks_response import GetListOfWebhooksResponse
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    actor_id: str,
    *,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    desc: bool | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["offset"] = offset

    params["limit"] = limit

    params["desc"] = desc


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/acts/{actor_id}/webhooks".format(actor_id=actor_id,),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetListOfWebhooksResponse | None:
    if response.status_code == 200:
        response_200 = GetListOfWebhooksResponse.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetListOfWebhooksResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    actor_id: str,
    *,
    client: AuthenticatedClient | Client,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    desc: bool | Unset = UNSET,

) -> Response[GetListOfWebhooksResponse]:
    """ Get list of webhooks

     Gets the list of webhooks of a specific Actor. The response is a JSON with
    the list of objects, where each object contains basic information about a single webhook.

    The endpoint supports pagination using the `limit` and `offset` parameters
    and it will not return more than 1000 records.

    By default, the records are sorted by the `createdAt` field in ascending
    order, to sort the records in descending order, use the `desc=1` parameter.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        offset (float | Unset):  Example: 10.
        limit (float | Unset):  Example: 99.
        desc (bool | Unset):  Example: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetListOfWebhooksResponse]
     """


    kwargs = _get_kwargs(
        actor_id=actor_id,
offset=offset,
limit=limit,
desc=desc,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    actor_id: str,
    *,
    client: AuthenticatedClient | Client,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    desc: bool | Unset = UNSET,

) -> GetListOfWebhooksResponse | None:
    """ Get list of webhooks

     Gets the list of webhooks of a specific Actor. The response is a JSON with
    the list of objects, where each object contains basic information about a single webhook.

    The endpoint supports pagination using the `limit` and `offset` parameters
    and it will not return more than 1000 records.

    By default, the records are sorted by the `createdAt` field in ascending
    order, to sort the records in descending order, use the `desc=1` parameter.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        offset (float | Unset):  Example: 10.
        limit (float | Unset):  Example: 99.
        desc (bool | Unset):  Example: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetListOfWebhooksResponse
     """


    return sync_detailed(
        actor_id=actor_id,
client=client,
offset=offset,
limit=limit,
desc=desc,

    ).parsed

async def asyncio_detailed(
    actor_id: str,
    *,
    client: AuthenticatedClient | Client,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    desc: bool | Unset = UNSET,

) -> Response[GetListOfWebhooksResponse]:
    """ Get list of webhooks

     Gets the list of webhooks of a specific Actor. The response is a JSON with
    the list of objects, where each object contains basic information about a single webhook.

    The endpoint supports pagination using the `limit` and `offset` parameters
    and it will not return more than 1000 records.

    By default, the records are sorted by the `createdAt` field in ascending
    order, to sort the records in descending order, use the `desc=1` parameter.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        offset (float | Unset):  Example: 10.
        limit (float | Unset):  Example: 99.
        desc (bool | Unset):  Example: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetListOfWebhooksResponse]
     """


    kwargs = _get_kwargs(
        actor_id=actor_id,
offset=offset,
limit=limit,
desc=desc,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    actor_id: str,
    *,
    client: AuthenticatedClient | Client,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    desc: bool | Unset = UNSET,

) -> GetListOfWebhooksResponse | None:
    """ Get list of webhooks

     Gets the list of webhooks of a specific Actor. The response is a JSON with
    the list of objects, where each object contains basic information about a single webhook.

    The endpoint supports pagination using the `limit` and `offset` parameters
    and it will not return more than 1000 records.

    By default, the records are sorted by the `createdAt` field in ascending
    order, to sort the records in descending order, use the `desc=1` parameter.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        offset (float | Unset):  Example: 10.
        limit (float | Unset):  Example: 99.
        desc (bool | Unset):  Example: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetListOfWebhooksResponse
     """


    return (await asyncio_detailed(
        actor_id=actor_id,
client=client,
offset=offset,
limit=limit,
desc=desc,

    )).parsed

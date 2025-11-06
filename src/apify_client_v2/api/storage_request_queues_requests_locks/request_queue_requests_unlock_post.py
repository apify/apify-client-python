from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.request_queue_requests_unlock_post_response_200 import RequestQueueRequestsUnlockPostResponse200
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    queue_id: str,
    *,
    client_key: str | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["clientKey"] = client_key


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v2/request-queues/{queue_id}/requests/unlock".format(queue_id=queue_id,),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> RequestQueueRequestsUnlockPostResponse200 | None:
    if response.status_code == 200:
        response_200 = RequestQueueRequestsUnlockPostResponse200.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[RequestQueueRequestsUnlockPostResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    queue_id: str,
    *,
    client: AuthenticatedClient | Client,
    client_key: str | Unset = UNSET,

) -> Response[RequestQueueRequestsUnlockPostResponse200]:
    """ Unlock requests

     Unlocks requests in the queue that are currently locked by the client.

    * If the client is within an Actor run, it unlocks all requests locked by that specific run plus all
    requests locked by the same clientKey.
    * If the client is outside of an Actor run, it unlocks all requests locked using the same clientKey.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        client_key (str | Unset):  Example: client-abc.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RequestQueueRequestsUnlockPostResponse200]
     """


    kwargs = _get_kwargs(
        queue_id=queue_id,
client_key=client_key,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    queue_id: str,
    *,
    client: AuthenticatedClient | Client,
    client_key: str | Unset = UNSET,

) -> RequestQueueRequestsUnlockPostResponse200 | None:
    """ Unlock requests

     Unlocks requests in the queue that are currently locked by the client.

    * If the client is within an Actor run, it unlocks all requests locked by that specific run plus all
    requests locked by the same clientKey.
    * If the client is outside of an Actor run, it unlocks all requests locked using the same clientKey.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        client_key (str | Unset):  Example: client-abc.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RequestQueueRequestsUnlockPostResponse200
     """


    return sync_detailed(
        queue_id=queue_id,
client=client,
client_key=client_key,

    ).parsed

async def asyncio_detailed(
    queue_id: str,
    *,
    client: AuthenticatedClient | Client,
    client_key: str | Unset = UNSET,

) -> Response[RequestQueueRequestsUnlockPostResponse200]:
    """ Unlock requests

     Unlocks requests in the queue that are currently locked by the client.

    * If the client is within an Actor run, it unlocks all requests locked by that specific run plus all
    requests locked by the same clientKey.
    * If the client is outside of an Actor run, it unlocks all requests locked using the same clientKey.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        client_key (str | Unset):  Example: client-abc.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RequestQueueRequestsUnlockPostResponse200]
     """


    kwargs = _get_kwargs(
        queue_id=queue_id,
client_key=client_key,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    queue_id: str,
    *,
    client: AuthenticatedClient | Client,
    client_key: str | Unset = UNSET,

) -> RequestQueueRequestsUnlockPostResponse200 | None:
    """ Unlock requests

     Unlocks requests in the queue that are currently locked by the client.

    * If the client is within an Actor run, it unlocks all requests locked by that specific run plus all
    requests locked by the same clientKey.
    * If the client is outside of an Actor run, it unlocks all requests locked using the same clientKey.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        client_key (str | Unset):  Example: client-abc.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RequestQueueRequestsUnlockPostResponse200
     """


    return (await asyncio_detailed(
        queue_id=queue_id,
client=client,
client_key=client_key,

    )).parsed

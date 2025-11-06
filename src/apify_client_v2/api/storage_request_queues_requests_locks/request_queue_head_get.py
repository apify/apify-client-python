from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.request_queue_head_get_response_200 import RequestQueueHeadGetResponse200
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    queue_id: str,
    *,
    limit: float | Unset = UNSET,
    client_key: str | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["limit"] = limit

    params["clientKey"] = client_key


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/request-queues/{queue_id}/head".format(queue_id=queue_id,),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> RequestQueueHeadGetResponse200 | None:
    if response.status_code == 200:
        response_200 = RequestQueueHeadGetResponse200.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[RequestQueueHeadGetResponse200]:
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
    limit: float | Unset = UNSET,
    client_key: str | Unset = UNSET,

) -> Response[RequestQueueHeadGetResponse200]:
    """ Get head

     Returns given number of first requests from the queue.

    The response contains the `hadMultipleClients` boolean field which indicates
    that the queue was accessed by more than one client (with unique or empty
    `clientKey`).
    This field is used by [Apify SDK](https://sdk.apify.com) to determine
    whether the local cache is consistent with the request queue, and thus
    optimize performance of certain operations.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        limit (float | Unset):  Example: 100.
        client_key (str | Unset):  Example: client-abc.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RequestQueueHeadGetResponse200]
     """


    kwargs = _get_kwargs(
        queue_id=queue_id,
limit=limit,
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
    limit: float | Unset = UNSET,
    client_key: str | Unset = UNSET,

) -> RequestQueueHeadGetResponse200 | None:
    """ Get head

     Returns given number of first requests from the queue.

    The response contains the `hadMultipleClients` boolean field which indicates
    that the queue was accessed by more than one client (with unique or empty
    `clientKey`).
    This field is used by [Apify SDK](https://sdk.apify.com) to determine
    whether the local cache is consistent with the request queue, and thus
    optimize performance of certain operations.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        limit (float | Unset):  Example: 100.
        client_key (str | Unset):  Example: client-abc.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RequestQueueHeadGetResponse200
     """


    return sync_detailed(
        queue_id=queue_id,
client=client,
limit=limit,
client_key=client_key,

    ).parsed

async def asyncio_detailed(
    queue_id: str,
    *,
    client: AuthenticatedClient | Client,
    limit: float | Unset = UNSET,
    client_key: str | Unset = UNSET,

) -> Response[RequestQueueHeadGetResponse200]:
    """ Get head

     Returns given number of first requests from the queue.

    The response contains the `hadMultipleClients` boolean field which indicates
    that the queue was accessed by more than one client (with unique or empty
    `clientKey`).
    This field is used by [Apify SDK](https://sdk.apify.com) to determine
    whether the local cache is consistent with the request queue, and thus
    optimize performance of certain operations.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        limit (float | Unset):  Example: 100.
        client_key (str | Unset):  Example: client-abc.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RequestQueueHeadGetResponse200]
     """


    kwargs = _get_kwargs(
        queue_id=queue_id,
limit=limit,
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
    limit: float | Unset = UNSET,
    client_key: str | Unset = UNSET,

) -> RequestQueueHeadGetResponse200 | None:
    """ Get head

     Returns given number of first requests from the queue.

    The response contains the `hadMultipleClients` boolean field which indicates
    that the queue was accessed by more than one client (with unique or empty
    `clientKey`).
    This field is used by [Apify SDK](https://sdk.apify.com) to determine
    whether the local cache is consistent with the request queue, and thus
    optimize performance of certain operations.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        limit (float | Unset):  Example: 100.
        client_key (str | Unset):  Example: client-abc.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RequestQueueHeadGetResponse200
     """


    return (await asyncio_detailed(
        queue_id=queue_id,
client=client,
limit=limit,
client_key=client_key,

    )).parsed

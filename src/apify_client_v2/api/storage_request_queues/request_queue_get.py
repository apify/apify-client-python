from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.request_queue_get_response_200 import RequestQueueGetResponse200
from typing import cast



def _get_kwargs(
    queue_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/request-queues/{queue_id}".format(queue_id=queue_id,),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> RequestQueueGetResponse200 | None:
    if response.status_code == 200:
        response_200 = RequestQueueGetResponse200.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[RequestQueueGetResponse200]:
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

) -> Response[RequestQueueGetResponse200]:
    """ Get request queue

     Returns queue object for given queue ID.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RequestQueueGetResponse200]
     """


    kwargs = _get_kwargs(
        queue_id=queue_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    queue_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> RequestQueueGetResponse200 | None:
    """ Get request queue

     Returns queue object for given queue ID.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RequestQueueGetResponse200
     """


    return sync_detailed(
        queue_id=queue_id,
client=client,

    ).parsed

async def asyncio_detailed(
    queue_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[RequestQueueGetResponse200]:
    """ Get request queue

     Returns queue object for given queue ID.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RequestQueueGetResponse200]
     """


    kwargs = _get_kwargs(
        queue_id=queue_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    queue_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> RequestQueueGetResponse200 | None:
    """ Get request queue

     Returns queue object for given queue ID.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RequestQueueGetResponse200
     """


    return (await asyncio_detailed(
        queue_id=queue_id,
client=client,

    )).parsed

from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.request_queue_put_body import RequestQueuePutBody
from ...models.request_queue_put_response_200 import RequestQueuePutResponse200
from typing import cast



def _get_kwargs(
    queue_id: str,
    *,
    body: RequestQueuePutBody,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v2/request-queues/{queue_id}".format(queue_id=queue_id,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> RequestQueuePutResponse200 | None:
    if response.status_code == 200:
        response_200 = RequestQueuePutResponse200.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[RequestQueuePutResponse200]:
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
    body: RequestQueuePutBody,

) -> Response[RequestQueuePutResponse200]:
    """ Update request queue

     Updates a request queue's name using a value specified by a JSON object
    passed in the PUT payload.

    The response is the updated request queue object, as returned by the
    [Get request queue](#/reference/request-queues/queue-collection/get-request-queue) API endpoint.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        body (RequestQueuePutBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RequestQueuePutResponse200]
     """


    kwargs = _get_kwargs(
        queue_id=queue_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    queue_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: RequestQueuePutBody,

) -> RequestQueuePutResponse200 | None:
    """ Update request queue

     Updates a request queue's name using a value specified by a JSON object
    passed in the PUT payload.

    The response is the updated request queue object, as returned by the
    [Get request queue](#/reference/request-queues/queue-collection/get-request-queue) API endpoint.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        body (RequestQueuePutBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RequestQueuePutResponse200
     """


    return sync_detailed(
        queue_id=queue_id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    queue_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: RequestQueuePutBody,

) -> Response[RequestQueuePutResponse200]:
    """ Update request queue

     Updates a request queue's name using a value specified by a JSON object
    passed in the PUT payload.

    The response is the updated request queue object, as returned by the
    [Get request queue](#/reference/request-queues/queue-collection/get-request-queue) API endpoint.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        body (RequestQueuePutBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RequestQueuePutResponse200]
     """


    kwargs = _get_kwargs(
        queue_id=queue_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    queue_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: RequestQueuePutBody,

) -> RequestQueuePutResponse200 | None:
    """ Update request queue

     Updates a request queue's name using a value specified by a JSON object
    passed in the PUT payload.

    The response is the updated request queue object, as returned by the
    [Get request queue](#/reference/request-queues/queue-collection/get-request-queue) API endpoint.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        body (RequestQueuePutBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RequestQueuePutResponse200
     """


    return (await asyncio_detailed(
        queue_id=queue_id,
client=client,
body=body,

    )).parsed

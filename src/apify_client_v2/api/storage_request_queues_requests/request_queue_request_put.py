from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.request_queue_request_put_body import RequestQueueRequestPutBody
from ...models.request_queue_request_put_response_200 import RequestQueueRequestPutResponse200
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    queue_id: str,
    request_id: str,
    *,
    body: RequestQueueRequestPutBody,
    forefront: str | Unset = UNSET,
    client_key: str | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    params: dict[str, Any] = {}

    params["forefront"] = forefront

    params["clientKey"] = client_key


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v2/request-queues/{queue_id}/requests/{request_id}".format(queue_id=queue_id,request_id=request_id,),
        "params": params,
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> RequestQueueRequestPutResponse200 | None:
    if response.status_code == 200:
        response_200 = RequestQueueRequestPutResponse200.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[RequestQueueRequestPutResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    queue_id: str,
    request_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: RequestQueueRequestPutBody,
    forefront: str | Unset = UNSET,
    client_key: str | Unset = UNSET,

) -> Response[RequestQueueRequestPutResponse200]:
    """ Update request

     Updates a request in a queue. Mark request as handled by setting
    `request.handledAt = new Date()`.
    If `handledAt` is set, the request will be removed from head of the queue (and unlocked, if
    applicable).

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        request_id (str):  Example: xpsmkDlspokDSmklS.
        forefront (str | Unset):  Example: false.
        client_key (str | Unset):  Example: client-abc.
        body (RequestQueueRequestPutBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RequestQueueRequestPutResponse200]
     """


    kwargs = _get_kwargs(
        queue_id=queue_id,
request_id=request_id,
body=body,
forefront=forefront,
client_key=client_key,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    queue_id: str,
    request_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: RequestQueueRequestPutBody,
    forefront: str | Unset = UNSET,
    client_key: str | Unset = UNSET,

) -> RequestQueueRequestPutResponse200 | None:
    """ Update request

     Updates a request in a queue. Mark request as handled by setting
    `request.handledAt = new Date()`.
    If `handledAt` is set, the request will be removed from head of the queue (and unlocked, if
    applicable).

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        request_id (str):  Example: xpsmkDlspokDSmklS.
        forefront (str | Unset):  Example: false.
        client_key (str | Unset):  Example: client-abc.
        body (RequestQueueRequestPutBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RequestQueueRequestPutResponse200
     """


    return sync_detailed(
        queue_id=queue_id,
request_id=request_id,
client=client,
body=body,
forefront=forefront,
client_key=client_key,

    ).parsed

async def asyncio_detailed(
    queue_id: str,
    request_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: RequestQueueRequestPutBody,
    forefront: str | Unset = UNSET,
    client_key: str | Unset = UNSET,

) -> Response[RequestQueueRequestPutResponse200]:
    """ Update request

     Updates a request in a queue. Mark request as handled by setting
    `request.handledAt = new Date()`.
    If `handledAt` is set, the request will be removed from head of the queue (and unlocked, if
    applicable).

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        request_id (str):  Example: xpsmkDlspokDSmklS.
        forefront (str | Unset):  Example: false.
        client_key (str | Unset):  Example: client-abc.
        body (RequestQueueRequestPutBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RequestQueueRequestPutResponse200]
     """


    kwargs = _get_kwargs(
        queue_id=queue_id,
request_id=request_id,
body=body,
forefront=forefront,
client_key=client_key,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    queue_id: str,
    request_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: RequestQueueRequestPutBody,
    forefront: str | Unset = UNSET,
    client_key: str | Unset = UNSET,

) -> RequestQueueRequestPutResponse200 | None:
    """ Update request

     Updates a request in a queue. Mark request as handled by setting
    `request.handledAt = new Date()`.
    If `handledAt` is set, the request will be removed from head of the queue (and unlocked, if
    applicable).

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        request_id (str):  Example: xpsmkDlspokDSmklS.
        forefront (str | Unset):  Example: false.
        client_key (str | Unset):  Example: client-abc.
        body (RequestQueueRequestPutBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RequestQueueRequestPutResponse200
     """


    return (await asyncio_detailed(
        queue_id=queue_id,
request_id=request_id,
client=client,
body=body,
forefront=forefront,
client_key=client_key,

    )).parsed

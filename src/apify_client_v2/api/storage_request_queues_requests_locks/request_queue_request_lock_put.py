from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.request_queue_request_lock_put_response_200 import RequestQueueRequestLockPutResponse200
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    queue_id: str,
    request_id: str,
    *,
    lock_secs: float,
    client_key: str | Unset = UNSET,
    forefront: str | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["lockSecs"] = lock_secs

    params["clientKey"] = client_key

    params["forefront"] = forefront


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v2/request-queues/{queue_id}/requests/{request_id}/lock".format(queue_id=queue_id,request_id=request_id,),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> RequestQueueRequestLockPutResponse200 | None:
    if response.status_code == 200:
        response_200 = RequestQueueRequestLockPutResponse200.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[RequestQueueRequestLockPutResponse200]:
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
    lock_secs: float,
    client_key: str | Unset = UNSET,
    forefront: str | Unset = UNSET,

) -> Response[RequestQueueRequestLockPutResponse200]:
    """ Prolong request lock

     Prolongs request lock. The request lock can be prolonged only by the client
    that has locked it using [Get and lock head
    operation](#/reference/request-queues/queue-head-with-locks).

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        request_id (str):  Example: xpsmkDlspokDSmklS.
        lock_secs (float):  Example: 60.
        client_key (str | Unset):  Example: client-abc.
        forefront (str | Unset):  Example: false.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RequestQueueRequestLockPutResponse200]
     """


    kwargs = _get_kwargs(
        queue_id=queue_id,
request_id=request_id,
lock_secs=lock_secs,
client_key=client_key,
forefront=forefront,

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
    lock_secs: float,
    client_key: str | Unset = UNSET,
    forefront: str | Unset = UNSET,

) -> RequestQueueRequestLockPutResponse200 | None:
    """ Prolong request lock

     Prolongs request lock. The request lock can be prolonged only by the client
    that has locked it using [Get and lock head
    operation](#/reference/request-queues/queue-head-with-locks).

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        request_id (str):  Example: xpsmkDlspokDSmklS.
        lock_secs (float):  Example: 60.
        client_key (str | Unset):  Example: client-abc.
        forefront (str | Unset):  Example: false.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RequestQueueRequestLockPutResponse200
     """


    return sync_detailed(
        queue_id=queue_id,
request_id=request_id,
client=client,
lock_secs=lock_secs,
client_key=client_key,
forefront=forefront,

    ).parsed

async def asyncio_detailed(
    queue_id: str,
    request_id: str,
    *,
    client: AuthenticatedClient | Client,
    lock_secs: float,
    client_key: str | Unset = UNSET,
    forefront: str | Unset = UNSET,

) -> Response[RequestQueueRequestLockPutResponse200]:
    """ Prolong request lock

     Prolongs request lock. The request lock can be prolonged only by the client
    that has locked it using [Get and lock head
    operation](#/reference/request-queues/queue-head-with-locks).

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        request_id (str):  Example: xpsmkDlspokDSmklS.
        lock_secs (float):  Example: 60.
        client_key (str | Unset):  Example: client-abc.
        forefront (str | Unset):  Example: false.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RequestQueueRequestLockPutResponse200]
     """


    kwargs = _get_kwargs(
        queue_id=queue_id,
request_id=request_id,
lock_secs=lock_secs,
client_key=client_key,
forefront=forefront,

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
    lock_secs: float,
    client_key: str | Unset = UNSET,
    forefront: str | Unset = UNSET,

) -> RequestQueueRequestLockPutResponse200 | None:
    """ Prolong request lock

     Prolongs request lock. The request lock can be prolonged only by the client
    that has locked it using [Get and lock head
    operation](#/reference/request-queues/queue-head-with-locks).

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        request_id (str):  Example: xpsmkDlspokDSmklS.
        lock_secs (float):  Example: 60.
        client_key (str | Unset):  Example: client-abc.
        forefront (str | Unset):  Example: false.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RequestQueueRequestLockPutResponse200
     """


    return (await asyncio_detailed(
        queue_id=queue_id,
request_id=request_id,
client=client,
lock_secs=lock_secs,
client_key=client_key,
forefront=forefront,

    )).parsed

from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.request_queue_request_lock_delete_content_type import RequestQueueRequestLockDeleteContentType
from ...types import UNSET, Unset



def _get_kwargs(
    queue_id: str,
    request_id: str,
    *,
    client_key: str | Unset = UNSET,
    forefront: str | Unset = UNSET,
    content_type: RequestQueueRequestLockDeleteContentType,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Content-Type"] = str(content_type)




    

    params: dict[str, Any] = {}

    params["clientKey"] = client_key

    params["forefront"] = forefront


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/v2/request-queues/{queue_id}/requests/{request_id}/lock".format(queue_id=queue_id,request_id=request_id,),
        "params": params,
    }


    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | None:
    if response.status_code == 204:
        return None

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any]:
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
    client_key: str | Unset = UNSET,
    forefront: str | Unset = UNSET,
    content_type: RequestQueueRequestLockDeleteContentType,

) -> Response[Any]:
    """ Delete request lock

     Deletes a request lock. The request lock can be deleted only by the client
    that has locked it using [Get and lock head
    operation](#/reference/request-queues/queue-head-with-locks).

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        request_id (str):  Example: xpsmkDlspokDSmklS.
        client_key (str | Unset):  Example: client-abc.
        forefront (str | Unset):  Example: false.
        content_type (RequestQueueRequestLockDeleteContentType):  Example: application/json.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        queue_id=queue_id,
request_id=request_id,
client_key=client_key,
forefront=forefront,
content_type=content_type,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    queue_id: str,
    request_id: str,
    *,
    client: AuthenticatedClient | Client,
    client_key: str | Unset = UNSET,
    forefront: str | Unset = UNSET,
    content_type: RequestQueueRequestLockDeleteContentType,

) -> Response[Any]:
    """ Delete request lock

     Deletes a request lock. The request lock can be deleted only by the client
    that has locked it using [Get and lock head
    operation](#/reference/request-queues/queue-head-with-locks).

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        request_id (str):  Example: xpsmkDlspokDSmklS.
        client_key (str | Unset):  Example: client-abc.
        forefront (str | Unset):  Example: false.
        content_type (RequestQueueRequestLockDeleteContentType):  Example: application/json.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        queue_id=queue_id,
request_id=request_id,
client_key=client_key,
forefront=forefront,
content_type=content_type,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)


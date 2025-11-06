from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.request_queue_requests_post_body import RequestQueueRequestsPostBody
from ...models.request_queue_requests_post_response_201 import RequestQueueRequestsPostResponse201
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    queue_id: str,
    *,
    body: RequestQueueRequestsPostBody,
    client_key: str | Unset = UNSET,
    forefront: str | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    params: dict[str, Any] = {}

    params["clientKey"] = client_key

    params["forefront"] = forefront


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v2/request-queues/{queue_id}/requests".format(queue_id=queue_id,),
        "params": params,
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> RequestQueueRequestsPostResponse201 | None:
    if response.status_code == 201:
        response_201 = RequestQueueRequestsPostResponse201.from_dict(response.json())



        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[RequestQueueRequestsPostResponse201]:
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
    body: RequestQueueRequestsPostBody,
    client_key: str | Unset = UNSET,
    forefront: str | Unset = UNSET,

) -> Response[RequestQueueRequestsPostResponse201]:
    """ Add request

     Adds request to the queue. Response contains ID of the request and info if
    request was already present in the queue or handled.

    If request with same `uniqueKey` was already present in the queue then
    returns an ID of existing request.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        client_key (str | Unset):  Example: client-abc.
        forefront (str | Unset):  Example: false.
        body (RequestQueueRequestsPostBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RequestQueueRequestsPostResponse201]
     """


    kwargs = _get_kwargs(
        queue_id=queue_id,
body=body,
client_key=client_key,
forefront=forefront,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    queue_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: RequestQueueRequestsPostBody,
    client_key: str | Unset = UNSET,
    forefront: str | Unset = UNSET,

) -> RequestQueueRequestsPostResponse201 | None:
    """ Add request

     Adds request to the queue. Response contains ID of the request and info if
    request was already present in the queue or handled.

    If request with same `uniqueKey` was already present in the queue then
    returns an ID of existing request.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        client_key (str | Unset):  Example: client-abc.
        forefront (str | Unset):  Example: false.
        body (RequestQueueRequestsPostBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RequestQueueRequestsPostResponse201
     """


    return sync_detailed(
        queue_id=queue_id,
client=client,
body=body,
client_key=client_key,
forefront=forefront,

    ).parsed

async def asyncio_detailed(
    queue_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: RequestQueueRequestsPostBody,
    client_key: str | Unset = UNSET,
    forefront: str | Unset = UNSET,

) -> Response[RequestQueueRequestsPostResponse201]:
    """ Add request

     Adds request to the queue. Response contains ID of the request and info if
    request was already present in the queue or handled.

    If request with same `uniqueKey` was already present in the queue then
    returns an ID of existing request.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        client_key (str | Unset):  Example: client-abc.
        forefront (str | Unset):  Example: false.
        body (RequestQueueRequestsPostBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RequestQueueRequestsPostResponse201]
     """


    kwargs = _get_kwargs(
        queue_id=queue_id,
body=body,
client_key=client_key,
forefront=forefront,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    queue_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: RequestQueueRequestsPostBody,
    client_key: str | Unset = UNSET,
    forefront: str | Unset = UNSET,

) -> RequestQueueRequestsPostResponse201 | None:
    """ Add request

     Adds request to the queue. Response contains ID of the request and info if
    request was already present in the queue or handled.

    If request with same `uniqueKey` was already present in the queue then
    returns an ID of existing request.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        client_key (str | Unset):  Example: client-abc.
        forefront (str | Unset):  Example: false.
        body (RequestQueueRequestsPostBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RequestQueueRequestsPostResponse201
     """


    return (await asyncio_detailed(
        queue_id=queue_id,
client=client,
body=body,
client_key=client_key,
forefront=forefront,

    )).parsed

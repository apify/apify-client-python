from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.request_queue_requests_batch_post_response_201 import RequestQueueRequestsBatchPostResponse201
from ...models.request_without_id import RequestWithoutId
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    queue_id: str,
    *,
    body: list[RequestWithoutId],
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
        "url": "/v2/request-queues/{queue_id}/requests/batch".format(queue_id=queue_id,),
        "params": params,
    }

    _kwargs["json"] = []
    for body_item_data in body:
        body_item = body_item_data.to_dict()
        _kwargs["json"].append(body_item)




    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> RequestQueueRequestsBatchPostResponse201 | None:
    if response.status_code == 201:
        response_201 = RequestQueueRequestsBatchPostResponse201.from_dict(response.json())



        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[RequestQueueRequestsBatchPostResponse201]:
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
    body: list[RequestWithoutId],
    client_key: str | Unset = UNSET,
    forefront: str | Unset = UNSET,

) -> Response[RequestQueueRequestsBatchPostResponse201]:
    """ Add requests

     Adds requests to the queue in batch. The maximum requests in batch is limit
    to 25. The response contains an array of unprocessed and processed requests.
    If any add operation fails because the request queue rate limit is exceeded
    or an internal failure occurs,
    the failed request is returned in the unprocessedRequests response
    parameter.
    You can resend these requests to add. It is recommended to use exponential
    backoff algorithm for these retries.
    If a request with the same `uniqueKey` was already present in the queue,
    then it returns an ID of the existing request.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        client_key (str | Unset):  Example: client-abc.
        forefront (str | Unset):  Example: false.
        body (list[RequestWithoutId]):  Example: [{'uniqueKey': 'http://example.com', 'url':
            'http://example.com', 'method': 'GET'}, {'uniqueKey': 'http://example.com/2', 'url':
            'http://example.com/2', 'method': 'GET'}].

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RequestQueueRequestsBatchPostResponse201]
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
    body: list[RequestWithoutId],
    client_key: str | Unset = UNSET,
    forefront: str | Unset = UNSET,

) -> RequestQueueRequestsBatchPostResponse201 | None:
    """ Add requests

     Adds requests to the queue in batch. The maximum requests in batch is limit
    to 25. The response contains an array of unprocessed and processed requests.
    If any add operation fails because the request queue rate limit is exceeded
    or an internal failure occurs,
    the failed request is returned in the unprocessedRequests response
    parameter.
    You can resend these requests to add. It is recommended to use exponential
    backoff algorithm for these retries.
    If a request with the same `uniqueKey` was already present in the queue,
    then it returns an ID of the existing request.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        client_key (str | Unset):  Example: client-abc.
        forefront (str | Unset):  Example: false.
        body (list[RequestWithoutId]):  Example: [{'uniqueKey': 'http://example.com', 'url':
            'http://example.com', 'method': 'GET'}, {'uniqueKey': 'http://example.com/2', 'url':
            'http://example.com/2', 'method': 'GET'}].

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RequestQueueRequestsBatchPostResponse201
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
    body: list[RequestWithoutId],
    client_key: str | Unset = UNSET,
    forefront: str | Unset = UNSET,

) -> Response[RequestQueueRequestsBatchPostResponse201]:
    """ Add requests

     Adds requests to the queue in batch. The maximum requests in batch is limit
    to 25. The response contains an array of unprocessed and processed requests.
    If any add operation fails because the request queue rate limit is exceeded
    or an internal failure occurs,
    the failed request is returned in the unprocessedRequests response
    parameter.
    You can resend these requests to add. It is recommended to use exponential
    backoff algorithm for these retries.
    If a request with the same `uniqueKey` was already present in the queue,
    then it returns an ID of the existing request.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        client_key (str | Unset):  Example: client-abc.
        forefront (str | Unset):  Example: false.
        body (list[RequestWithoutId]):  Example: [{'uniqueKey': 'http://example.com', 'url':
            'http://example.com', 'method': 'GET'}, {'uniqueKey': 'http://example.com/2', 'url':
            'http://example.com/2', 'method': 'GET'}].

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RequestQueueRequestsBatchPostResponse201]
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
    body: list[RequestWithoutId],
    client_key: str | Unset = UNSET,
    forefront: str | Unset = UNSET,

) -> RequestQueueRequestsBatchPostResponse201 | None:
    """ Add requests

     Adds requests to the queue in batch. The maximum requests in batch is limit
    to 25. The response contains an array of unprocessed and processed requests.
    If any add operation fails because the request queue rate limit is exceeded
    or an internal failure occurs,
    the failed request is returned in the unprocessedRequests response
    parameter.
    You can resend these requests to add. It is recommended to use exponential
    backoff algorithm for these retries.
    If a request with the same `uniqueKey` was already present in the queue,
    then it returns an ID of the existing request.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        client_key (str | Unset):  Example: client-abc.
        forefront (str | Unset):  Example: false.
        body (list[RequestWithoutId]):  Example: [{'uniqueKey': 'http://example.com', 'url':
            'http://example.com', 'method': 'GET'}, {'uniqueKey': 'http://example.com/2', 'url':
            'http://example.com/2', 'method': 'GET'}].

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RequestQueueRequestsBatchPostResponse201
     """


    return (await asyncio_detailed(
        queue_id=queue_id,
client=client,
body=body,
client_key=client_key,
forefront=forefront,

    )).parsed

from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.request_queue_requests_batch_delete_content_type import RequestQueueRequestsBatchDeleteContentType
from ...models.request_queue_requests_batch_delete_response_204 import RequestQueueRequestsBatchDeleteResponse204
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    queue_id: str,
    *,
    client_key: str | Unset = UNSET,
    content_type: RequestQueueRequestsBatchDeleteContentType,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Content-Type"] = str(content_type)




    

    params: dict[str, Any] = {}

    params["clientKey"] = client_key


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/v2/request-queues/{queue_id}/requests/batch".format(queue_id=queue_id,),
        "params": params,
    }


    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> RequestQueueRequestsBatchDeleteResponse204 | None:
    if response.status_code == 204:
        response_204 = RequestQueueRequestsBatchDeleteResponse204.from_dict(response.json())



        return response_204

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[RequestQueueRequestsBatchDeleteResponse204]:
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
    content_type: RequestQueueRequestsBatchDeleteContentType,

) -> Response[RequestQueueRequestsBatchDeleteResponse204]:
    """ Delete requests

     Batch-deletes given requests from the queue. The number of requests in a
    batch is limited to 25. The response contains an array of unprocessed and
    processed requests.
    If any delete operation fails because the request queue rate limit is
    exceeded or an internal failure occurs,
    the failed request is returned in the `unprocessedRequests` response
    parameter.
    You can re-send these delete requests. It is recommended to use an
    exponential backoff algorithm for these retries.
    Each request is identified by its ID or uniqueKey parameter. You can use
    either of them to identify the request.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        client_key (str | Unset):  Example: client-abc.
        content_type (RequestQueueRequestsBatchDeleteContentType):  Example: application/json.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RequestQueueRequestsBatchDeleteResponse204]
     """


    kwargs = _get_kwargs(
        queue_id=queue_id,
client_key=client_key,
content_type=content_type,

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
    content_type: RequestQueueRequestsBatchDeleteContentType,

) -> RequestQueueRequestsBatchDeleteResponse204 | None:
    """ Delete requests

     Batch-deletes given requests from the queue. The number of requests in a
    batch is limited to 25. The response contains an array of unprocessed and
    processed requests.
    If any delete operation fails because the request queue rate limit is
    exceeded or an internal failure occurs,
    the failed request is returned in the `unprocessedRequests` response
    parameter.
    You can re-send these delete requests. It is recommended to use an
    exponential backoff algorithm for these retries.
    Each request is identified by its ID or uniqueKey parameter. You can use
    either of them to identify the request.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        client_key (str | Unset):  Example: client-abc.
        content_type (RequestQueueRequestsBatchDeleteContentType):  Example: application/json.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RequestQueueRequestsBatchDeleteResponse204
     """


    return sync_detailed(
        queue_id=queue_id,
client=client,
client_key=client_key,
content_type=content_type,

    ).parsed

async def asyncio_detailed(
    queue_id: str,
    *,
    client: AuthenticatedClient | Client,
    client_key: str | Unset = UNSET,
    content_type: RequestQueueRequestsBatchDeleteContentType,

) -> Response[RequestQueueRequestsBatchDeleteResponse204]:
    """ Delete requests

     Batch-deletes given requests from the queue. The number of requests in a
    batch is limited to 25. The response contains an array of unprocessed and
    processed requests.
    If any delete operation fails because the request queue rate limit is
    exceeded or an internal failure occurs,
    the failed request is returned in the `unprocessedRequests` response
    parameter.
    You can re-send these delete requests. It is recommended to use an
    exponential backoff algorithm for these retries.
    Each request is identified by its ID or uniqueKey parameter. You can use
    either of them to identify the request.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        client_key (str | Unset):  Example: client-abc.
        content_type (RequestQueueRequestsBatchDeleteContentType):  Example: application/json.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RequestQueueRequestsBatchDeleteResponse204]
     """


    kwargs = _get_kwargs(
        queue_id=queue_id,
client_key=client_key,
content_type=content_type,

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
    content_type: RequestQueueRequestsBatchDeleteContentType,

) -> RequestQueueRequestsBatchDeleteResponse204 | None:
    """ Delete requests

     Batch-deletes given requests from the queue. The number of requests in a
    batch is limited to 25. The response contains an array of unprocessed and
    processed requests.
    If any delete operation fails because the request queue rate limit is
    exceeded or an internal failure occurs,
    the failed request is returned in the `unprocessedRequests` response
    parameter.
    You can re-send these delete requests. It is recommended to use an
    exponential backoff algorithm for these retries.
    Each request is identified by its ID or uniqueKey parameter. You can use
    either of them to identify the request.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        client_key (str | Unset):  Example: client-abc.
        content_type (RequestQueueRequestsBatchDeleteContentType):  Example: application/json.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RequestQueueRequestsBatchDeleteResponse204
     """


    return (await asyncio_detailed(
        queue_id=queue_id,
client=client,
client_key=client_key,
content_type=content_type,

    )).parsed

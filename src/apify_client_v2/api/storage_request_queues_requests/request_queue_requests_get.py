from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.request_queue_requests_get_response_200 import RequestQueueRequestsGetResponse200
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    queue_id: str,
    *,
    client_key: str | Unset = UNSET,
    exclusive_start_id: str | Unset = UNSET,
    limit: float | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["clientKey"] = client_key

    params["exclusiveStartId"] = exclusive_start_id

    params["limit"] = limit


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/request-queues/{queue_id}/requests".format(queue_id=queue_id,),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> RequestQueueRequestsGetResponse200 | None:
    if response.status_code == 200:
        response_200 = RequestQueueRequestsGetResponse200.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[RequestQueueRequestsGetResponse200]:
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
    exclusive_start_id: str | Unset = UNSET,
    limit: float | Unset = UNSET,

) -> Response[RequestQueueRequestsGetResponse200]:
    """ List requests

     Returns a list of requests. This endpoint is paginated using
    exclusiveStartId and limit parameters.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        client_key (str | Unset):  Example: client-abc.
        exclusive_start_id (str | Unset):  Example: Ihnsp8YrvJ8102Kj.
        limit (float | Unset):  Example: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RequestQueueRequestsGetResponse200]
     """


    kwargs = _get_kwargs(
        queue_id=queue_id,
client_key=client_key,
exclusive_start_id=exclusive_start_id,
limit=limit,

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
    exclusive_start_id: str | Unset = UNSET,
    limit: float | Unset = UNSET,

) -> RequestQueueRequestsGetResponse200 | None:
    """ List requests

     Returns a list of requests. This endpoint is paginated using
    exclusiveStartId and limit parameters.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        client_key (str | Unset):  Example: client-abc.
        exclusive_start_id (str | Unset):  Example: Ihnsp8YrvJ8102Kj.
        limit (float | Unset):  Example: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RequestQueueRequestsGetResponse200
     """


    return sync_detailed(
        queue_id=queue_id,
client=client,
client_key=client_key,
exclusive_start_id=exclusive_start_id,
limit=limit,

    ).parsed

async def asyncio_detailed(
    queue_id: str,
    *,
    client: AuthenticatedClient | Client,
    client_key: str | Unset = UNSET,
    exclusive_start_id: str | Unset = UNSET,
    limit: float | Unset = UNSET,

) -> Response[RequestQueueRequestsGetResponse200]:
    """ List requests

     Returns a list of requests. This endpoint is paginated using
    exclusiveStartId and limit parameters.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        client_key (str | Unset):  Example: client-abc.
        exclusive_start_id (str | Unset):  Example: Ihnsp8YrvJ8102Kj.
        limit (float | Unset):  Example: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RequestQueueRequestsGetResponse200]
     """


    kwargs = _get_kwargs(
        queue_id=queue_id,
client_key=client_key,
exclusive_start_id=exclusive_start_id,
limit=limit,

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
    exclusive_start_id: str | Unset = UNSET,
    limit: float | Unset = UNSET,

) -> RequestQueueRequestsGetResponse200 | None:
    """ List requests

     Returns a list of requests. This endpoint is paginated using
    exclusiveStartId and limit parameters.

    Args:
        queue_id (str):  Example: WkzbQMuFYuamGv3YF.
        client_key (str | Unset):  Example: client-abc.
        exclusive_start_id (str | Unset):  Example: Ihnsp8YrvJ8102Kj.
        limit (float | Unset):  Example: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RequestQueueRequestsGetResponse200
     """


    return (await asyncio_detailed(
        queue_id=queue_id,
client=client,
client_key=client_key,
exclusive_start_id=exclusive_start_id,
limit=limit,

    )).parsed

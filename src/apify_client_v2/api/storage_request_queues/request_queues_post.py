from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.request_queues_post_response_201 import RequestQueuesPostResponse201
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    *,
    name: str | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["name"] = name


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v2/request-queues",
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> RequestQueuesPostResponse201 | None:
    if response.status_code == 201:
        response_201 = RequestQueuesPostResponse201.from_dict(response.json())



        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[RequestQueuesPostResponse201]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    name: str | Unset = UNSET,

) -> Response[RequestQueuesPostResponse201]:
    """ Create request queue

     Creates a request queue and returns its object.
    Keep in mind that requests stored under unnamed queue follows [data
    retention period](https://docs.apify.com/platform/storage#data-retention).

    It creates a queue of given name if the parameter name is used. If a queue
    with the given name already exists then the endpoint returns
    its object.

    Args:
        name (str | Unset):  Example: example-com.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RequestQueuesPostResponse201]
     """


    kwargs = _get_kwargs(
        name=name,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient | Client,
    name: str | Unset = UNSET,

) -> RequestQueuesPostResponse201 | None:
    """ Create request queue

     Creates a request queue and returns its object.
    Keep in mind that requests stored under unnamed queue follows [data
    retention period](https://docs.apify.com/platform/storage#data-retention).

    It creates a queue of given name if the parameter name is used. If a queue
    with the given name already exists then the endpoint returns
    its object.

    Args:
        name (str | Unset):  Example: example-com.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RequestQueuesPostResponse201
     """


    return sync_detailed(
        client=client,
name=name,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    name: str | Unset = UNSET,

) -> Response[RequestQueuesPostResponse201]:
    """ Create request queue

     Creates a request queue and returns its object.
    Keep in mind that requests stored under unnamed queue follows [data
    retention period](https://docs.apify.com/platform/storage#data-retention).

    It creates a queue of given name if the parameter name is used. If a queue
    with the given name already exists then the endpoint returns
    its object.

    Args:
        name (str | Unset):  Example: example-com.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RequestQueuesPostResponse201]
     """


    kwargs = _get_kwargs(
        name=name,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    name: str | Unset = UNSET,

) -> RequestQueuesPostResponse201 | None:
    """ Create request queue

     Creates a request queue and returns its object.
    Keep in mind that requests stored under unnamed queue follows [data
    retention period](https://docs.apify.com/platform/storage#data-retention).

    It creates a queue of given name if the parameter name is used. If a queue
    with the given name already exists then the endpoint returns
    its object.

    Args:
        name (str | Unset):  Example: example-com.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RequestQueuesPostResponse201
     """


    return (await asyncio_detailed(
        client=client,
name=name,

    )).parsed

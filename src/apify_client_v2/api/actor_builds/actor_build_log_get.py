from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors




def _get_kwargs(
    build_id: str,
    *,
    stream: bool,
    download: bool,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["stream"] = stream

    params["download"] = download


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/actor-builds/{build_id}/log".format(build_id=build_id,),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> str | None:
    if response.status_code == 200:
        response_200 = response.text
        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[str]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    build_id: str,
    *,
    client: AuthenticatedClient | Client,
    stream: bool,
    download: bool,

) -> Response[str]:
    """ Get log

     Check out [Logs](#/reference/logs) for full reference.

    Args:
        build_id (str):  Example: HG7ML7M8z78YcAPEB.
        stream (bool):
        download (bool):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[str]
     """


    kwargs = _get_kwargs(
        build_id=build_id,
stream=stream,
download=download,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    build_id: str,
    *,
    client: AuthenticatedClient | Client,
    stream: bool,
    download: bool,

) -> str | None:
    """ Get log

     Check out [Logs](#/reference/logs) for full reference.

    Args:
        build_id (str):  Example: HG7ML7M8z78YcAPEB.
        stream (bool):
        download (bool):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        str
     """


    return sync_detailed(
        build_id=build_id,
client=client,
stream=stream,
download=download,

    ).parsed

async def asyncio_detailed(
    build_id: str,
    *,
    client: AuthenticatedClient | Client,
    stream: bool,
    download: bool,

) -> Response[str]:
    """ Get log

     Check out [Logs](#/reference/logs) for full reference.

    Args:
        build_id (str):  Example: HG7ML7M8z78YcAPEB.
        stream (bool):
        download (bool):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[str]
     """


    kwargs = _get_kwargs(
        build_id=build_id,
stream=stream,
download=download,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    build_id: str,
    *,
    client: AuthenticatedClient | Client,
    stream: bool,
    download: bool,

) -> str | None:
    """ Get log

     Check out [Logs](#/reference/logs) for full reference.

    Args:
        build_id (str):  Example: HG7ML7M8z78YcAPEB.
        stream (bool):
        download (bool):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        str
     """


    return (await asyncio_detailed(
        build_id=build_id,
client=client,
stream=stream,
download=download,

    )).parsed

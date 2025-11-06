from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...types import UNSET, Unset



def _get_kwargs(
    build_or_run_id: str,
    *,
    stream: bool,
    download: bool,
    raw: bool | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["stream"] = stream

    params["download"] = download

    params["raw"] = raw


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/logs/{build_or_run_id}".format(build_or_run_id=build_or_run_id,),
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
    build_or_run_id: str,
    *,
    client: AuthenticatedClient | Client,
    stream: bool,
    download: bool,
    raw: bool | Unset = UNSET,

) -> Response[str]:
    """ Get log

     Retrieves logs for a specific Actor build or run.

    Args:
        build_or_run_id (str):  Example: HG7ML7M8z78YcAPEB.
        stream (bool):
        download (bool):
        raw (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[str]
     """


    kwargs = _get_kwargs(
        build_or_run_id=build_or_run_id,
stream=stream,
download=download,
raw=raw,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    build_or_run_id: str,
    *,
    client: AuthenticatedClient | Client,
    stream: bool,
    download: bool,
    raw: bool | Unset = UNSET,

) -> str | None:
    """ Get log

     Retrieves logs for a specific Actor build or run.

    Args:
        build_or_run_id (str):  Example: HG7ML7M8z78YcAPEB.
        stream (bool):
        download (bool):
        raw (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        str
     """


    return sync_detailed(
        build_or_run_id=build_or_run_id,
client=client,
stream=stream,
download=download,
raw=raw,

    ).parsed

async def asyncio_detailed(
    build_or_run_id: str,
    *,
    client: AuthenticatedClient | Client,
    stream: bool,
    download: bool,
    raw: bool | Unset = UNSET,

) -> Response[str]:
    """ Get log

     Retrieves logs for a specific Actor build or run.

    Args:
        build_or_run_id (str):  Example: HG7ML7M8z78YcAPEB.
        stream (bool):
        download (bool):
        raw (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[str]
     """


    kwargs = _get_kwargs(
        build_or_run_id=build_or_run_id,
stream=stream,
download=download,
raw=raw,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    build_or_run_id: str,
    *,
    client: AuthenticatedClient | Client,
    stream: bool,
    download: bool,
    raw: bool | Unset = UNSET,

) -> str | None:
    """ Get log

     Retrieves logs for a specific Actor build or run.

    Args:
        build_or_run_id (str):  Example: HG7ML7M8z78YcAPEB.
        stream (bool):
        download (bool):
        raw (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        str
     """


    return (await asyncio_detailed(
        build_or_run_id=build_or_run_id,
client=client,
stream=stream,
download=download,
raw=raw,

    )).parsed

from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors




def _get_kwargs(
    run_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v2/actor-runs/{run_id}/reboot".format(run_id=run_id,),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | None:
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
    run_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[Any]:
    """ Reboot run

     Reboots an Actor run and returns an object that contains all the details
    about the rebooted run.

    Only runs that are running, i.e. runs with status `RUNNING` can be rebooted.

    The run's container will be restarted, so any data not persisted in the
    key-value store, dataset, or request queue will be lost.

    Args:
        run_id (str):  Example: 3KH8gEpp4d8uQSe8T.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        run_id=run_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    run_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[Any]:
    """ Reboot run

     Reboots an Actor run and returns an object that contains all the details
    about the rebooted run.

    Only runs that are running, i.e. runs with status `RUNNING` can be rebooted.

    The run's container will be restarted, so any data not persisted in the
    key-value store, dataset, or request queue will be lost.

    Args:
        run_id (str):  Example: 3KH8gEpp4d8uQSe8T.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        run_id=run_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)


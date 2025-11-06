from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...types import UNSET, Unset



def _get_kwargs(
    actor_id: str,
    run_id: str,
    *,
    gracefully: bool | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["gracefully"] = gracefully


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v2/acts/{actor_id}/runs/{run_id}/abort".format(actor_id=actor_id,run_id=run_id,),
        "params": params,
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
    actor_id: str,
    run_id: str,
    *,
    client: AuthenticatedClient | Client,
    gracefully: bool | Unset = UNSET,

) -> Response[Any]:
    """ Abort run

     **[DEPRECATED]** API endpoints related to run of the Actor were moved under
    new namespace [`actor-runs`](#/reference/actor-runs). Aborts an Actor run and
    returns an object that contains all the details about the run.

    Only runs that are starting or running are aborted. For runs with status
    `FINISHED`, `FAILED`, `ABORTING` and `TIMED-OUT` this call does nothing.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        run_id (str):  Example: 3KH8gEpp4d8uQSe8T.
        gracefully (bool | Unset):  Example: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        actor_id=actor_id,
run_id=run_id,
gracefully=gracefully,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    actor_id: str,
    run_id: str,
    *,
    client: AuthenticatedClient | Client,
    gracefully: bool | Unset = UNSET,

) -> Response[Any]:
    """ Abort run

     **[DEPRECATED]** API endpoints related to run of the Actor were moved under
    new namespace [`actor-runs`](#/reference/actor-runs). Aborts an Actor run and
    returns an object that contains all the details about the run.

    Only runs that are starting or running are aborted. For runs with status
    `FINISHED`, `FAILED`, `ABORTING` and `TIMED-OUT` this call does nothing.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        run_id (str):  Example: 3KH8gEpp4d8uQSe8T.
        gracefully (bool | Unset):  Example: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        actor_id=actor_id,
run_id=run_id,
gracefully=gracefully,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)


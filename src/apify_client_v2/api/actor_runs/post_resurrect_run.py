from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...types import UNSET, Unset



def _get_kwargs(
    run_id: str,
    *,
    build: str | Unset = UNSET,
    timeout: float | Unset = UNSET,
    memory: float | Unset = UNSET,
    max_items: float | Unset = UNSET,
    max_total_charge_usd: float | Unset = UNSET,
    restart_on_error: bool | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["build"] = build

    params["timeout"] = timeout

    params["memory"] = memory

    params["maxItems"] = max_items

    params["maxTotalChargeUsd"] = max_total_charge_usd

    params["restartOnError"] = restart_on_error


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v2/actor-runs/{run_id}/resurrect".format(run_id=run_id,),
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
    run_id: str,
    *,
    client: AuthenticatedClient | Client,
    build: str | Unset = UNSET,
    timeout: float | Unset = UNSET,
    memory: float | Unset = UNSET,
    max_items: float | Unset = UNSET,
    max_total_charge_usd: float | Unset = UNSET,
    restart_on_error: bool | Unset = UNSET,

) -> Response[Any]:
    """ Resurrect run

     Resurrects a finished Actor run and returns an object that contains all the details about the
    resurrected run.
    Only finished runs, i.e. runs with status `FINISHED`, `FAILED`, `ABORTED` and `TIMED-OUT` can be
    resurrected.
    Run status will be updated to RUNNING and its container will be restarted with the same storages
    (the same behaviour as when the run gets migrated to the new server).

    For more information, see the [Actor docs](https://docs.apify.com/platform/actors/running/runs-and-
    builds#resurrection-of-finished-run).

    Args:
        run_id (str):
        build (str | Unset):
        timeout (float | Unset):
        memory (float | Unset):
        max_items (float | Unset):
        max_total_charge_usd (float | Unset):
        restart_on_error (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        run_id=run_id,
build=build,
timeout=timeout,
memory=memory,
max_items=max_items,
max_total_charge_usd=max_total_charge_usd,
restart_on_error=restart_on_error,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    run_id: str,
    *,
    client: AuthenticatedClient | Client,
    build: str | Unset = UNSET,
    timeout: float | Unset = UNSET,
    memory: float | Unset = UNSET,
    max_items: float | Unset = UNSET,
    max_total_charge_usd: float | Unset = UNSET,
    restart_on_error: bool | Unset = UNSET,

) -> Response[Any]:
    """ Resurrect run

     Resurrects a finished Actor run and returns an object that contains all the details about the
    resurrected run.
    Only finished runs, i.e. runs with status `FINISHED`, `FAILED`, `ABORTED` and `TIMED-OUT` can be
    resurrected.
    Run status will be updated to RUNNING and its container will be restarted with the same storages
    (the same behaviour as when the run gets migrated to the new server).

    For more information, see the [Actor docs](https://docs.apify.com/platform/actors/running/runs-and-
    builds#resurrection-of-finished-run).

    Args:
        run_id (str):
        build (str | Unset):
        timeout (float | Unset):
        memory (float | Unset):
        max_items (float | Unset):
        max_total_charge_usd (float | Unset):
        restart_on_error (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        run_id=run_id,
build=build,
timeout=timeout,
memory=memory,
max_items=max_items,
max_total_charge_usd=max_total_charge_usd,
restart_on_error=restart_on_error,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)


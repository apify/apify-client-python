from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...types import UNSET, Unset



def _get_kwargs(
    actor_id: str,
    *,
    wait_for_finish: float | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["waitForFinish"] = wait_for_finish


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/acts/{actor_id}/builds/default".format(actor_id=actor_id,),
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
    *,
    client: AuthenticatedClient | Client,
    wait_for_finish: float | Unset = UNSET,

) -> Response[Any]:
    """ Get default build

     Get the default build for an Actor.

    Use the optional `waitForFinish` parameter to synchronously wait for the build to finish.
    This avoids the need for periodic polling when waiting for the build to complete.

    This endpoint does not require an authentication token. Instead, calls are authenticated using the
    Actor's unique ID.
    However, if you access the endpoint without a token, certain attributes (e.g., `usageUsd` and
    `usageTotalUsd`) will be hidden.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        wait_for_finish (float | Unset):  Example: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        actor_id=actor_id,
wait_for_finish=wait_for_finish,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    actor_id: str,
    *,
    client: AuthenticatedClient | Client,
    wait_for_finish: float | Unset = UNSET,

) -> Response[Any]:
    """ Get default build

     Get the default build for an Actor.

    Use the optional `waitForFinish` parameter to synchronously wait for the build to finish.
    This avoids the need for periodic polling when waiting for the build to complete.

    This endpoint does not require an authentication token. Instead, calls are authenticated using the
    Actor's unique ID.
    However, if you access the endpoint without a token, certain attributes (e.g., `usageUsd` and
    `usageTotalUsd`) will be hidden.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        wait_for_finish (float | Unset):  Example: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        actor_id=actor_id,
wait_for_finish=wait_for_finish,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)


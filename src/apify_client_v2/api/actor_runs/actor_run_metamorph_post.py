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
    target_actor_id: str,
    build: str | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["targetActorId"] = target_actor_id

    params["build"] = build


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v2/actor-runs/{run_id}/metamorph".format(run_id=run_id,),
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
    target_actor_id: str,
    build: str | Unset = UNSET,

) -> Response[Any]:
    """ Metamorph run

     Transforms an Actor run into a run of another Actor with a new input.

    This is useful if you want to use another Actor to finish the work
    of your current Actor run, without the need to create a completely new run
    and waiting for its finish.

    For the users of your Actors, the metamorph operation is transparent, they
    will just see your Actor got the work done.

    Internally, the system stops the Docker container corresponding to the Actor
    run and starts a new container using a different Docker image.

    All the default storages are preserved and the new input is stored under the
    `INPUT-METAMORPH-1` key in the same default key-value store.

    For more information, see the [Actor
    docs](https://docs.apify.com/platform/actors/development/programming-interface/metamorph).

    Args:
        run_id (str):  Example: 3KH8gEpp4d8uQSe8T.
        target_actor_id (str):  Example: HDSasDasz78YcAPEB.
        build (str | Unset):  Example: beta.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        run_id=run_id,
target_actor_id=target_actor_id,
build=build,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    run_id: str,
    *,
    client: AuthenticatedClient | Client,
    target_actor_id: str,
    build: str | Unset = UNSET,

) -> Response[Any]:
    """ Metamorph run

     Transforms an Actor run into a run of another Actor with a new input.

    This is useful if you want to use another Actor to finish the work
    of your current Actor run, without the need to create a completely new run
    and waiting for its finish.

    For the users of your Actors, the metamorph operation is transparent, they
    will just see your Actor got the work done.

    Internally, the system stops the Docker container corresponding to the Actor
    run and starts a new container using a different Docker image.

    All the default storages are preserved and the new input is stored under the
    `INPUT-METAMORPH-1` key in the same default key-value store.

    For more information, see the [Actor
    docs](https://docs.apify.com/platform/actors/development/programming-interface/metamorph).

    Args:
        run_id (str):  Example: 3KH8gEpp4d8uQSe8T.
        target_actor_id (str):  Example: HDSasDasz78YcAPEB.
        build (str | Unset):  Example: beta.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        run_id=run_id,
target_actor_id=target_actor_id,
build=build,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)


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
    version: str,
    use_cache: bool | Unset = UNSET,
    beta_packages: bool | Unset = UNSET,
    tag: str | Unset = UNSET,
    wait_for_finish: float | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["version"] = version

    params["useCache"] = use_cache

    params["betaPackages"] = beta_packages

    params["tag"] = tag

    params["waitForFinish"] = wait_for_finish


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v2/acts/{actor_id}/builds".format(actor_id=actor_id,),
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
    version: str,
    use_cache: bool | Unset = UNSET,
    beta_packages: bool | Unset = UNSET,
    tag: str | Unset = UNSET,
    wait_for_finish: float | Unset = UNSET,

) -> Response[Any]:
    """ Build Actor

     Builds an Actor.
    The response is the build object as returned by the
    [Get build](#/reference/actors/build-object/get-build) endpoint.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        version (str):  Example: 0.0.
        use_cache (bool | Unset):  Example: True.
        beta_packages (bool | Unset):  Example: True.
        tag (str | Unset):  Example: latest.
        wait_for_finish (float | Unset):  Example: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        actor_id=actor_id,
version=version,
use_cache=use_cache,
beta_packages=beta_packages,
tag=tag,
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
    version: str,
    use_cache: bool | Unset = UNSET,
    beta_packages: bool | Unset = UNSET,
    tag: str | Unset = UNSET,
    wait_for_finish: float | Unset = UNSET,

) -> Response[Any]:
    """ Build Actor

     Builds an Actor.
    The response is the build object as returned by the
    [Get build](#/reference/actors/build-object/get-build) endpoint.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        version (str):  Example: 0.0.
        use_cache (bool | Unset):  Example: True.
        beta_packages (bool | Unset):  Example: True.
        tag (str | Unset):  Example: latest.
        wait_for_finish (float | Unset):  Example: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        actor_id=actor_id,
version=version,
use_cache=use_cache,
beta_packages=beta_packages,
tag=tag,
wait_for_finish=wait_for_finish,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)


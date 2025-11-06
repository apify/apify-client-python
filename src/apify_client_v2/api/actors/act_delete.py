from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.act_delete_response_204 import ActDeleteResponse204
from typing import cast



def _get_kwargs(
    actor_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/v2/acts/{actor_id}".format(actor_id=actor_id,),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ActDeleteResponse204 | None:
    if response.status_code == 204:
        response_204 = ActDeleteResponse204.from_dict(response.json())



        return response_204

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ActDeleteResponse204]:
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

) -> Response[ActDeleteResponse204]:
    """ Delete Actor

     Deletes an Actor.

    Args:
        actor_id (str):  Example: janedoe~my-actor.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActDeleteResponse204]
     """


    kwargs = _get_kwargs(
        actor_id=actor_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    actor_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> ActDeleteResponse204 | None:
    """ Delete Actor

     Deletes an Actor.

    Args:
        actor_id (str):  Example: janedoe~my-actor.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ActDeleteResponse204
     """


    return sync_detailed(
        actor_id=actor_id,
client=client,

    ).parsed

async def asyncio_detailed(
    actor_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[ActDeleteResponse204]:
    """ Delete Actor

     Deletes an Actor.

    Args:
        actor_id (str):  Example: janedoe~my-actor.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActDeleteResponse204]
     """


    kwargs = _get_kwargs(
        actor_id=actor_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    actor_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> ActDeleteResponse204 | None:
    """ Delete Actor

     Deletes an Actor.

    Args:
        actor_id (str):  Example: janedoe~my-actor.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ActDeleteResponse204
     """


    return (await asyncio_detailed(
        actor_id=actor_id,
client=client,

    )).parsed

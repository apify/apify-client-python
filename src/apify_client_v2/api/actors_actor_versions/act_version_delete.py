from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.act_version_delete_response_204 import ActVersionDeleteResponse204
from typing import cast



def _get_kwargs(
    actor_id: str,
    version_number: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/v2/acts/{actor_id}/versions/{version_number}".format(actor_id=actor_id,version_number=version_number,),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ActVersionDeleteResponse204 | None:
    if response.status_code == 204:
        response_204 = ActVersionDeleteResponse204.from_dict(response.json())



        return response_204

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ActVersionDeleteResponse204]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    actor_id: str,
    version_number: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[ActVersionDeleteResponse204]:
    """ Delete version

     Deletes a specific version of Actor's source code.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        version_number (str):  Example: 1.0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActVersionDeleteResponse204]
     """


    kwargs = _get_kwargs(
        actor_id=actor_id,
version_number=version_number,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    actor_id: str,
    version_number: str,
    *,
    client: AuthenticatedClient | Client,

) -> ActVersionDeleteResponse204 | None:
    """ Delete version

     Deletes a specific version of Actor's source code.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        version_number (str):  Example: 1.0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ActVersionDeleteResponse204
     """


    return sync_detailed(
        actor_id=actor_id,
version_number=version_number,
client=client,

    ).parsed

async def asyncio_detailed(
    actor_id: str,
    version_number: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[ActVersionDeleteResponse204]:
    """ Delete version

     Deletes a specific version of Actor's source code.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        version_number (str):  Example: 1.0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActVersionDeleteResponse204]
     """


    kwargs = _get_kwargs(
        actor_id=actor_id,
version_number=version_number,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    actor_id: str,
    version_number: str,
    *,
    client: AuthenticatedClient | Client,

) -> ActVersionDeleteResponse204 | None:
    """ Delete version

     Deletes a specific version of Actor's source code.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        version_number (str):  Example: 1.0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ActVersionDeleteResponse204
     """


    return (await asyncio_detailed(
        actor_id=actor_id,
version_number=version_number,
client=client,

    )).parsed

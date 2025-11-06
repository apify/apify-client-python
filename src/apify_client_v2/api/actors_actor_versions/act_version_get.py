from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.get_version_response import GetVersionResponse
from typing import cast



def _get_kwargs(
    actor_id: str,
    version_number: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/acts/{actor_id}/versions/{version_number}".format(actor_id=actor_id,version_number=version_number,),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetVersionResponse | None:
    if response.status_code == 200:
        response_200 = GetVersionResponse.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetVersionResponse]:
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

) -> Response[GetVersionResponse]:
    """ Get version

     Gets a [Version object](#/reference/actors/version-object) that contains all the details about a
    specific version of an Actor.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        version_number (str):  Example: 1.0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetVersionResponse]
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

) -> GetVersionResponse | None:
    """ Get version

     Gets a [Version object](#/reference/actors/version-object) that contains all the details about a
    specific version of an Actor.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        version_number (str):  Example: 1.0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetVersionResponse
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

) -> Response[GetVersionResponse]:
    """ Get version

     Gets a [Version object](#/reference/actors/version-object) that contains all the details about a
    specific version of an Actor.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        version_number (str):  Example: 1.0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetVersionResponse]
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

) -> GetVersionResponse | None:
    """ Get version

     Gets a [Version object](#/reference/actors/version-object) that contains all the details about a
    specific version of an Actor.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        version_number (str):  Example: 1.0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetVersionResponse
     """


    return (await asyncio_detailed(
        actor_id=actor_id,
version_number=version_number,
client=client,

    )).parsed

from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.get_version_list_response import GetVersionListResponse
from typing import cast



def _get_kwargs(
    actor_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/acts/{actor_id}/versions".format(actor_id=actor_id,),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetVersionListResponse | None:
    if response.status_code == 200:
        response_200 = GetVersionListResponse.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetVersionListResponse]:
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

) -> Response[GetVersionListResponse]:
    """ Get list of versions

     Gets the list of versions of a specific Actor. The response is a JSON object
    with the list of [Version objects](#/reference/actors/version-object), where each
    contains basic information about a single version.

    Args:
        actor_id (str):  Example: janedoe~my-actor.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetVersionListResponse]
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

) -> GetVersionListResponse | None:
    """ Get list of versions

     Gets the list of versions of a specific Actor. The response is a JSON object
    with the list of [Version objects](#/reference/actors/version-object), where each
    contains basic information about a single version.

    Args:
        actor_id (str):  Example: janedoe~my-actor.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetVersionListResponse
     """


    return sync_detailed(
        actor_id=actor_id,
client=client,

    ).parsed

async def asyncio_detailed(
    actor_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[GetVersionListResponse]:
    """ Get list of versions

     Gets the list of versions of a specific Actor. The response is a JSON object
    with the list of [Version objects](#/reference/actors/version-object), where each
    contains basic information about a single version.

    Args:
        actor_id (str):  Example: janedoe~my-actor.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetVersionListResponse]
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

) -> GetVersionListResponse | None:
    """ Get list of versions

     Gets the list of versions of a specific Actor. The response is a JSON object
    with the list of [Version objects](#/reference/actors/version-object), where each
    contains basic information about a single version.

    Args:
        actor_id (str):  Example: janedoe~my-actor.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetVersionListResponse
     """


    return (await asyncio_detailed(
        actor_id=actor_id,
client=client,

    )).parsed

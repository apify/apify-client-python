from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.get_env_var_list_response import GetEnvVarListResponse
from typing import cast



def _get_kwargs(
    actor_id: str,
    version_number: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/acts/{actor_id}/versions/{version_number}/env-vars".format(actor_id=actor_id,version_number=version_number,),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetEnvVarListResponse | None:
    if response.status_code == 200:
        response_200 = GetEnvVarListResponse.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetEnvVarListResponse]:
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

) -> Response[GetEnvVarListResponse]:
    """ Get list of environment variables

     Gets the list of environment variables for a specific version of an Actor.
    The response is a JSON object with the list of [EnvVar objects](#/reference/actors/environment-
    variable-object), where each contains basic information about a single environment variable.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        version_number (str):  Example: 0.1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetEnvVarListResponse]
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

) -> GetEnvVarListResponse | None:
    """ Get list of environment variables

     Gets the list of environment variables for a specific version of an Actor.
    The response is a JSON object with the list of [EnvVar objects](#/reference/actors/environment-
    variable-object), where each contains basic information about a single environment variable.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        version_number (str):  Example: 0.1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetEnvVarListResponse
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

) -> Response[GetEnvVarListResponse]:
    """ Get list of environment variables

     Gets the list of environment variables for a specific version of an Actor.
    The response is a JSON object with the list of [EnvVar objects](#/reference/actors/environment-
    variable-object), where each contains basic information about a single environment variable.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        version_number (str):  Example: 0.1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetEnvVarListResponse]
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

) -> GetEnvVarListResponse | None:
    """ Get list of environment variables

     Gets the list of environment variables for a specific version of an Actor.
    The response is a JSON object with the list of [EnvVar objects](#/reference/actors/environment-
    variable-object), where each contains basic information about a single environment variable.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        version_number (str):  Example: 0.1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetEnvVarListResponse
     """


    return (await asyncio_detailed(
        actor_id=actor_id,
version_number=version_number,
client=client,

    )).parsed

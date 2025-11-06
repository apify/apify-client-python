from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.get_open_api_response import GetOpenApiResponse
from typing import cast



def _get_kwargs(
    actor_id: str,
    build_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/acts/{actor_id}/builds/{build_id}/openapi.json".format(actor_id=actor_id,build_id=build_id,),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetOpenApiResponse | None:
    if response.status_code == 200:
        response_200 = GetOpenApiResponse.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetOpenApiResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    actor_id: str,
    build_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[GetOpenApiResponse]:
    """ Get OpenAPI definition

     
    Get the OpenAPI definition for Actor builds. Two similar endpoints are available:

    - [First endpoint](/api/v2/act-openapi-json-get): Requires both `actorId` and `buildId`. Use
    `default` as the `buildId` to get the OpenAPI schema for the default Actor build.
    - [Second endpoint](/api/v2/actor-build-openapi-json-get): Requires only `buildId`.

    Get the OpenAPI definition for a specific Actor build.

    To fetch the default Actor build, simply pass `default` as the `buildId`.
    Authentication is based on the build's unique ID. No authentication token is required.

    :::note

    You can also use the [`/api/v2/actor-build-openapi-json-get`](/api/v2/actor-build-openapi-json-get)
    endpoint to get the OpenAPI definition for a build.

    :::

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        build_id (str):  Example: soSkq9ekdmfOslopH.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetOpenApiResponse]
     """


    kwargs = _get_kwargs(
        actor_id=actor_id,
build_id=build_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    actor_id: str,
    build_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> GetOpenApiResponse | None:
    """ Get OpenAPI definition

     
    Get the OpenAPI definition for Actor builds. Two similar endpoints are available:

    - [First endpoint](/api/v2/act-openapi-json-get): Requires both `actorId` and `buildId`. Use
    `default` as the `buildId` to get the OpenAPI schema for the default Actor build.
    - [Second endpoint](/api/v2/actor-build-openapi-json-get): Requires only `buildId`.

    Get the OpenAPI definition for a specific Actor build.

    To fetch the default Actor build, simply pass `default` as the `buildId`.
    Authentication is based on the build's unique ID. No authentication token is required.

    :::note

    You can also use the [`/api/v2/actor-build-openapi-json-get`](/api/v2/actor-build-openapi-json-get)
    endpoint to get the OpenAPI definition for a build.

    :::

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        build_id (str):  Example: soSkq9ekdmfOslopH.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetOpenApiResponse
     """


    return sync_detailed(
        actor_id=actor_id,
build_id=build_id,
client=client,

    ).parsed

async def asyncio_detailed(
    actor_id: str,
    build_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[GetOpenApiResponse]:
    """ Get OpenAPI definition

     
    Get the OpenAPI definition for Actor builds. Two similar endpoints are available:

    - [First endpoint](/api/v2/act-openapi-json-get): Requires both `actorId` and `buildId`. Use
    `default` as the `buildId` to get the OpenAPI schema for the default Actor build.
    - [Second endpoint](/api/v2/actor-build-openapi-json-get): Requires only `buildId`.

    Get the OpenAPI definition for a specific Actor build.

    To fetch the default Actor build, simply pass `default` as the `buildId`.
    Authentication is based on the build's unique ID. No authentication token is required.

    :::note

    You can also use the [`/api/v2/actor-build-openapi-json-get`](/api/v2/actor-build-openapi-json-get)
    endpoint to get the OpenAPI definition for a build.

    :::

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        build_id (str):  Example: soSkq9ekdmfOslopH.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetOpenApiResponse]
     """


    kwargs = _get_kwargs(
        actor_id=actor_id,
build_id=build_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    actor_id: str,
    build_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> GetOpenApiResponse | None:
    """ Get OpenAPI definition

     
    Get the OpenAPI definition for Actor builds. Two similar endpoints are available:

    - [First endpoint](/api/v2/act-openapi-json-get): Requires both `actorId` and `buildId`. Use
    `default` as the `buildId` to get the OpenAPI schema for the default Actor build.
    - [Second endpoint](/api/v2/actor-build-openapi-json-get): Requires only `buildId`.

    Get the OpenAPI definition for a specific Actor build.

    To fetch the default Actor build, simply pass `default` as the `buildId`.
    Authentication is based on the build's unique ID. No authentication token is required.

    :::note

    You can also use the [`/api/v2/actor-build-openapi-json-get`](/api/v2/actor-build-openapi-json-get)
    endpoint to get the OpenAPI definition for a build.

    :::

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        build_id (str):  Example: soSkq9ekdmfOslopH.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetOpenApiResponse
     """


    return (await asyncio_detailed(
        actor_id=actor_id,
build_id=build_id,
client=client,

    )).parsed

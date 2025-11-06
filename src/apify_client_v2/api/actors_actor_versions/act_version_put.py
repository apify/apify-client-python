from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.create_or_update_version_request import CreateOrUpdateVersionRequest
from ...models.get_version_response import GetVersionResponse
from typing import cast



def _get_kwargs(
    actor_id: str,
    version_number: str,
    *,
    body: CreateOrUpdateVersionRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v2/acts/{actor_id}/versions/{version_number}".format(actor_id=actor_id,version_number=version_number,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
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
    body: CreateOrUpdateVersionRequest,

) -> Response[GetVersionResponse]:
    """ Update version

     Updates Actor version using values specified by a [Version object](#/reference/actors/version-
    object) passed as JSON in the POST payload.

    If the object does not define a specific property, its value will not be
    updated.

    The request needs to specify the `Content-Type: application/json` HTTP
    header!

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    The response is the [Version object](#/reference/actors/version-object) as
    returned by the [Get version](#/reference/actors/version-object/get-version) endpoint.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        version_number (str):  Example: 1.0.
        body (CreateOrUpdateVersionRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetVersionResponse]
     """


    kwargs = _get_kwargs(
        actor_id=actor_id,
version_number=version_number,
body=body,

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
    body: CreateOrUpdateVersionRequest,

) -> GetVersionResponse | None:
    """ Update version

     Updates Actor version using values specified by a [Version object](#/reference/actors/version-
    object) passed as JSON in the POST payload.

    If the object does not define a specific property, its value will not be
    updated.

    The request needs to specify the `Content-Type: application/json` HTTP
    header!

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    The response is the [Version object](#/reference/actors/version-object) as
    returned by the [Get version](#/reference/actors/version-object/get-version) endpoint.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        version_number (str):  Example: 1.0.
        body (CreateOrUpdateVersionRequest):

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
body=body,

    ).parsed

async def asyncio_detailed(
    actor_id: str,
    version_number: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateOrUpdateVersionRequest,

) -> Response[GetVersionResponse]:
    """ Update version

     Updates Actor version using values specified by a [Version object](#/reference/actors/version-
    object) passed as JSON in the POST payload.

    If the object does not define a specific property, its value will not be
    updated.

    The request needs to specify the `Content-Type: application/json` HTTP
    header!

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    The response is the [Version object](#/reference/actors/version-object) as
    returned by the [Get version](#/reference/actors/version-object/get-version) endpoint.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        version_number (str):  Example: 1.0.
        body (CreateOrUpdateVersionRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetVersionResponse]
     """


    kwargs = _get_kwargs(
        actor_id=actor_id,
version_number=version_number,
body=body,

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
    body: CreateOrUpdateVersionRequest,

) -> GetVersionResponse | None:
    """ Update version

     Updates Actor version using values specified by a [Version object](#/reference/actors/version-
    object) passed as JSON in the POST payload.

    If the object does not define a specific property, its value will not be
    updated.

    The request needs to specify the `Content-Type: application/json` HTTP
    header!

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    The response is the [Version object](#/reference/actors/version-object) as
    returned by the [Get version](#/reference/actors/version-object/get-version) endpoint.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        version_number (str):  Example: 1.0.
        body (CreateOrUpdateVersionRequest):

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
body=body,

    )).parsed

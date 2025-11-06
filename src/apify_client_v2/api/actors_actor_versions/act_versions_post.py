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
    *,
    body: CreateOrUpdateVersionRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v2/acts/{actor_id}/versions".format(actor_id=actor_id,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetVersionResponse | None:
    if response.status_code == 201:
        response_201 = GetVersionResponse.from_dict(response.json())



        return response_201

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
    *,
    client: AuthenticatedClient | Client,
    body: CreateOrUpdateVersionRequest,

) -> Response[GetVersionResponse]:
    r""" Create version

     Creates a version of an Actor using values specified in a [Version
    object](#/reference/actors/version-object) passed as JSON in the POST
    payload.

    The request must specify `versionNumber` and `sourceType` parameters (as
    strings) in the JSON payload and a `Content-Type: application/json` HTTP
    header.

    Each `sourceType` requires its own additional properties to be passed to the
    JSON payload object. These are outlined in the [Version
    object](#/reference/actors/version-object) table below and in more detail in
    the [Apify
    documentation](https://docs.apify.com/platform/actors/development/deployment/source-types).

    For example, if an Actor's source code is stored in a [GitHub
    repository](https://docs.apify.com/platform/actors/development/deployment/source-types#git-
    repository),
    you will set the `sourceType` to `GIT_REPO` and pass the repository's URL in
    the `gitRepoUrl` property.

    ```
    {
        \"versionNumber\": \"0.1\",
        \"sourceType\": \"GIT_REPO\",
        \"gitRepoUrl\": \"https://github.com/my-github-account/actor-repo\"
    }
    ```

    The response is the [Version object](#/reference/actors/version-object) as
    returned by the [Get version](#/reference/actors/version-object/get-version) endpoint.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        body (CreateOrUpdateVersionRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetVersionResponse]
     """


    kwargs = _get_kwargs(
        actor_id=actor_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    actor_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateOrUpdateVersionRequest,

) -> GetVersionResponse | None:
    r""" Create version

     Creates a version of an Actor using values specified in a [Version
    object](#/reference/actors/version-object) passed as JSON in the POST
    payload.

    The request must specify `versionNumber` and `sourceType` parameters (as
    strings) in the JSON payload and a `Content-Type: application/json` HTTP
    header.

    Each `sourceType` requires its own additional properties to be passed to the
    JSON payload object. These are outlined in the [Version
    object](#/reference/actors/version-object) table below and in more detail in
    the [Apify
    documentation](https://docs.apify.com/platform/actors/development/deployment/source-types).

    For example, if an Actor's source code is stored in a [GitHub
    repository](https://docs.apify.com/platform/actors/development/deployment/source-types#git-
    repository),
    you will set the `sourceType` to `GIT_REPO` and pass the repository's URL in
    the `gitRepoUrl` property.

    ```
    {
        \"versionNumber\": \"0.1\",
        \"sourceType\": \"GIT_REPO\",
        \"gitRepoUrl\": \"https://github.com/my-github-account/actor-repo\"
    }
    ```

    The response is the [Version object](#/reference/actors/version-object) as
    returned by the [Get version](#/reference/actors/version-object/get-version) endpoint.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        body (CreateOrUpdateVersionRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetVersionResponse
     """


    return sync_detailed(
        actor_id=actor_id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    actor_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateOrUpdateVersionRequest,

) -> Response[GetVersionResponse]:
    r""" Create version

     Creates a version of an Actor using values specified in a [Version
    object](#/reference/actors/version-object) passed as JSON in the POST
    payload.

    The request must specify `versionNumber` and `sourceType` parameters (as
    strings) in the JSON payload and a `Content-Type: application/json` HTTP
    header.

    Each `sourceType` requires its own additional properties to be passed to the
    JSON payload object. These are outlined in the [Version
    object](#/reference/actors/version-object) table below and in more detail in
    the [Apify
    documentation](https://docs.apify.com/platform/actors/development/deployment/source-types).

    For example, if an Actor's source code is stored in a [GitHub
    repository](https://docs.apify.com/platform/actors/development/deployment/source-types#git-
    repository),
    you will set the `sourceType` to `GIT_REPO` and pass the repository's URL in
    the `gitRepoUrl` property.

    ```
    {
        \"versionNumber\": \"0.1\",
        \"sourceType\": \"GIT_REPO\",
        \"gitRepoUrl\": \"https://github.com/my-github-account/actor-repo\"
    }
    ```

    The response is the [Version object](#/reference/actors/version-object) as
    returned by the [Get version](#/reference/actors/version-object/get-version) endpoint.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        body (CreateOrUpdateVersionRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetVersionResponse]
     """


    kwargs = _get_kwargs(
        actor_id=actor_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    actor_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateOrUpdateVersionRequest,

) -> GetVersionResponse | None:
    r""" Create version

     Creates a version of an Actor using values specified in a [Version
    object](#/reference/actors/version-object) passed as JSON in the POST
    payload.

    The request must specify `versionNumber` and `sourceType` parameters (as
    strings) in the JSON payload and a `Content-Type: application/json` HTTP
    header.

    Each `sourceType` requires its own additional properties to be passed to the
    JSON payload object. These are outlined in the [Version
    object](#/reference/actors/version-object) table below and in more detail in
    the [Apify
    documentation](https://docs.apify.com/platform/actors/development/deployment/source-types).

    For example, if an Actor's source code is stored in a [GitHub
    repository](https://docs.apify.com/platform/actors/development/deployment/source-types#git-
    repository),
    you will set the `sourceType` to `GIT_REPO` and pass the repository's URL in
    the `gitRepoUrl` property.

    ```
    {
        \"versionNumber\": \"0.1\",
        \"sourceType\": \"GIT_REPO\",
        \"gitRepoUrl\": \"https://github.com/my-github-account/actor-repo\"
    }
    ```

    The response is the [Version object](#/reference/actors/version-object) as
    returned by the [Get version](#/reference/actors/version-object/get-version) endpoint.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        body (CreateOrUpdateVersionRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetVersionResponse
     """


    return (await asyncio_detailed(
        actor_id=actor_id,
client=client,
body=body,

    )).parsed

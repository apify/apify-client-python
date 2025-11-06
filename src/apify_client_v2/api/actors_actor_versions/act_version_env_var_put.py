from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.create_environment_variable_response import CreateEnvironmentVariableResponse
from ...models.create_or_update_env_var_request import CreateOrUpdateEnvVarRequest
from typing import cast



def _get_kwargs(
    actor_id: str,
    version_number: str,
    env_var_name: str,
    *,
    body: CreateOrUpdateEnvVarRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v2/acts/{actor_id}/versions/{version_number}/env-vars/{env_var_name}".format(actor_id=actor_id,version_number=version_number,env_var_name=env_var_name,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> CreateEnvironmentVariableResponse | None:
    if response.status_code == 200:
        response_200 = CreateEnvironmentVariableResponse.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[CreateEnvironmentVariableResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    actor_id: str,
    version_number: str,
    env_var_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateOrUpdateEnvVarRequest,

) -> Response[CreateEnvironmentVariableResponse]:
    """ Update environment variable

     Updates Actor environment variable using values specified by a [EnvVar
    object](#/reference/actors/environment-variable-object)
    passed as JSON in the POST payload.
    If the object does not define a specific property, its value will not be
    updated.

    The request needs to specify the `Content-Type: application/json` HTTP
    header!

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    The response is the [EnvVar object](#/reference/actors/environment-variable-object) as returned by
    the
    [Get environment variable](#/reference/actors/environment-variable-object/get-environment-variable)
    endpoint.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        version_number (str):  Example: 0.1.
        env_var_name (str):  Example: MY_ENV_VAR.
        body (CreateOrUpdateEnvVarRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateEnvironmentVariableResponse]
     """


    kwargs = _get_kwargs(
        actor_id=actor_id,
version_number=version_number,
env_var_name=env_var_name,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    actor_id: str,
    version_number: str,
    env_var_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateOrUpdateEnvVarRequest,

) -> CreateEnvironmentVariableResponse | None:
    """ Update environment variable

     Updates Actor environment variable using values specified by a [EnvVar
    object](#/reference/actors/environment-variable-object)
    passed as JSON in the POST payload.
    If the object does not define a specific property, its value will not be
    updated.

    The request needs to specify the `Content-Type: application/json` HTTP
    header!

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    The response is the [EnvVar object](#/reference/actors/environment-variable-object) as returned by
    the
    [Get environment variable](#/reference/actors/environment-variable-object/get-environment-variable)
    endpoint.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        version_number (str):  Example: 0.1.
        env_var_name (str):  Example: MY_ENV_VAR.
        body (CreateOrUpdateEnvVarRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateEnvironmentVariableResponse
     """


    return sync_detailed(
        actor_id=actor_id,
version_number=version_number,
env_var_name=env_var_name,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    actor_id: str,
    version_number: str,
    env_var_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateOrUpdateEnvVarRequest,

) -> Response[CreateEnvironmentVariableResponse]:
    """ Update environment variable

     Updates Actor environment variable using values specified by a [EnvVar
    object](#/reference/actors/environment-variable-object)
    passed as JSON in the POST payload.
    If the object does not define a specific property, its value will not be
    updated.

    The request needs to specify the `Content-Type: application/json` HTTP
    header!

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    The response is the [EnvVar object](#/reference/actors/environment-variable-object) as returned by
    the
    [Get environment variable](#/reference/actors/environment-variable-object/get-environment-variable)
    endpoint.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        version_number (str):  Example: 0.1.
        env_var_name (str):  Example: MY_ENV_VAR.
        body (CreateOrUpdateEnvVarRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateEnvironmentVariableResponse]
     """


    kwargs = _get_kwargs(
        actor_id=actor_id,
version_number=version_number,
env_var_name=env_var_name,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    actor_id: str,
    version_number: str,
    env_var_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateOrUpdateEnvVarRequest,

) -> CreateEnvironmentVariableResponse | None:
    """ Update environment variable

     Updates Actor environment variable using values specified by a [EnvVar
    object](#/reference/actors/environment-variable-object)
    passed as JSON in the POST payload.
    If the object does not define a specific property, its value will not be
    updated.

    The request needs to specify the `Content-Type: application/json` HTTP
    header!

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    The response is the [EnvVar object](#/reference/actors/environment-variable-object) as returned by
    the
    [Get environment variable](#/reference/actors/environment-variable-object/get-environment-variable)
    endpoint.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        version_number (str):  Example: 0.1.
        env_var_name (str):  Example: MY_ENV_VAR.
        body (CreateOrUpdateEnvVarRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateEnvironmentVariableResponse
     """


    return (await asyncio_detailed(
        actor_id=actor_id,
version_number=version_number,
env_var_name=env_var_name,
client=client,
body=body,

    )).parsed

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
    *,
    body: CreateOrUpdateEnvVarRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v2/acts/{actor_id}/versions/{version_number}/env-vars".format(actor_id=actor_id,version_number=version_number,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> CreateEnvironmentVariableResponse | None:
    if response.status_code == 201:
        response_201 = CreateEnvironmentVariableResponse.from_dict(response.json())



        return response_201

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
    *,
    client: AuthenticatedClient | Client,
    body: CreateOrUpdateEnvVarRequest,

) -> Response[CreateEnvironmentVariableResponse]:
    r""" Create environment variable

     Creates an environment variable of an Actor using values specified in a
    [EnvVar object](#/reference/actors/environment-variable-object) passed as
    JSON in the POST payload.

    The request must specify `name` and `value` parameters (as strings) in the
    JSON payload and a `Content-Type: application/json` HTTP header.

    ```
    {
        \"name\": \"ENV_VAR_NAME\",
        \"value\": \"my-env-var\"
    }
    ```

    The response is the [EnvVar
    object](#/reference/actors/environment-variable-object) as returned by the [Get environment
    variable](#/reference/actors/environment-variable-object/get-environment-variable)
    endpoint.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        version_number (str):  Example: 0.1.
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
    body: CreateOrUpdateEnvVarRequest,

) -> CreateEnvironmentVariableResponse | None:
    r""" Create environment variable

     Creates an environment variable of an Actor using values specified in a
    [EnvVar object](#/reference/actors/environment-variable-object) passed as
    JSON in the POST payload.

    The request must specify `name` and `value` parameters (as strings) in the
    JSON payload and a `Content-Type: application/json` HTTP header.

    ```
    {
        \"name\": \"ENV_VAR_NAME\",
        \"value\": \"my-env-var\"
    }
    ```

    The response is the [EnvVar
    object](#/reference/actors/environment-variable-object) as returned by the [Get environment
    variable](#/reference/actors/environment-variable-object/get-environment-variable)
    endpoint.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        version_number (str):  Example: 0.1.
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
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    actor_id: str,
    version_number: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateOrUpdateEnvVarRequest,

) -> Response[CreateEnvironmentVariableResponse]:
    r""" Create environment variable

     Creates an environment variable of an Actor using values specified in a
    [EnvVar object](#/reference/actors/environment-variable-object) passed as
    JSON in the POST payload.

    The request must specify `name` and `value` parameters (as strings) in the
    JSON payload and a `Content-Type: application/json` HTTP header.

    ```
    {
        \"name\": \"ENV_VAR_NAME\",
        \"value\": \"my-env-var\"
    }
    ```

    The response is the [EnvVar
    object](#/reference/actors/environment-variable-object) as returned by the [Get environment
    variable](#/reference/actors/environment-variable-object/get-environment-variable)
    endpoint.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        version_number (str):  Example: 0.1.
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
    body: CreateOrUpdateEnvVarRequest,

) -> CreateEnvironmentVariableResponse | None:
    r""" Create environment variable

     Creates an environment variable of an Actor using values specified in a
    [EnvVar object](#/reference/actors/environment-variable-object) passed as
    JSON in the POST payload.

    The request must specify `name` and `value` parameters (as strings) in the
    JSON payload and a `Content-Type: application/json` HTTP header.

    ```
    {
        \"name\": \"ENV_VAR_NAME\",
        \"value\": \"my-env-var\"
    }
    ```

    The response is the [EnvVar
    object](#/reference/actors/environment-variable-object) as returned by the [Get environment
    variable](#/reference/actors/environment-variable-object/get-environment-variable)
    endpoint.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        version_number (str):  Example: 0.1.
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
client=client,
body=body,

    )).parsed

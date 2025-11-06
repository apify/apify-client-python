from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.update_limits_request import UpdateLimitsRequest
from ...models.users_me_limits_put_response_201 import UsersMeLimitsPutResponse201
from typing import cast



def _get_kwargs(
    *,
    body: UpdateLimitsRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v2/users/me/limits",
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> UsersMeLimitsPutResponse201 | None:
    if response.status_code == 201:
        response_201 = UsersMeLimitsPutResponse201.from_dict(response.json())



        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[UsersMeLimitsPutResponse201]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: UpdateLimitsRequest,

) -> Response[UsersMeLimitsPutResponse201]:
    """ Update limits

     Updates the account's limits manageable on your account's [Limits
    page](https://console.apify.com/billing#/limits).
    Specifically the: `maxMonthlyUsageUsd` and `dataRetentionDays` limits (see request body schema for
    more details).

    Args:
        body (UpdateLimitsRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UsersMeLimitsPutResponse201]
     """


    kwargs = _get_kwargs(
        body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient | Client,
    body: UpdateLimitsRequest,

) -> UsersMeLimitsPutResponse201 | None:
    """ Update limits

     Updates the account's limits manageable on your account's [Limits
    page](https://console.apify.com/billing#/limits).
    Specifically the: `maxMonthlyUsageUsd` and `dataRetentionDays` limits (see request body schema for
    more details).

    Args:
        body (UpdateLimitsRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UsersMeLimitsPutResponse201
     """


    return sync_detailed(
        client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: UpdateLimitsRequest,

) -> Response[UsersMeLimitsPutResponse201]:
    """ Update limits

     Updates the account's limits manageable on your account's [Limits
    page](https://console.apify.com/billing#/limits).
    Specifically the: `maxMonthlyUsageUsd` and `dataRetentionDays` limits (see request body schema for
    more details).

    Args:
        body (UpdateLimitsRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UsersMeLimitsPutResponse201]
     """


    kwargs = _get_kwargs(
        body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: UpdateLimitsRequest,

) -> UsersMeLimitsPutResponse201 | None:
    """ Update limits

     Updates the account's limits manageable on your account's [Limits
    page](https://console.apify.com/billing#/limits).
    Specifically the: `maxMonthlyUsageUsd` and `dataRetentionDays` limits (see request body schema for
    more details).

    Args:
        body (UpdateLimitsRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UsersMeLimitsPutResponse201
     """


    return (await asyncio_detailed(
        client=client,
body=body,

    )).parsed

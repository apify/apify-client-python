from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.get_limits_response import GetLimitsResponse
from typing import cast



def _get_kwargs(
    
) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/users/me/limits",
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetLimitsResponse | None:
    if response.status_code == 200:
        response_200 = GetLimitsResponse.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetLimitsResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,

) -> Response[GetLimitsResponse]:
    """ Get limits

     Returns a complete summary of your account's limits. It is the same
    information you will see on your account's [Limits page](https://console.apify.com/billing#/limits).
    The returned data
    includes the current usage cycle, a summary of your limits, and your current usage.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetLimitsResponse]
     """


    kwargs = _get_kwargs(
        
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient | Client,

) -> GetLimitsResponse | None:
    """ Get limits

     Returns a complete summary of your account's limits. It is the same
    information you will see on your account's [Limits page](https://console.apify.com/billing#/limits).
    The returned data
    includes the current usage cycle, a summary of your limits, and your current usage.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetLimitsResponse
     """


    return sync_detailed(
        client=client,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,

) -> Response[GetLimitsResponse]:
    """ Get limits

     Returns a complete summary of your account's limits. It is the same
    information you will see on your account's [Limits page](https://console.apify.com/billing#/limits).
    The returned data
    includes the current usage cycle, a summary of your limits, and your current usage.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetLimitsResponse]
     """


    kwargs = _get_kwargs(
        
    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient | Client,

) -> GetLimitsResponse | None:
    """ Get limits

     Returns a complete summary of your account's limits. It is the same
    information you will see on your account's [Limits page](https://console.apify.com/billing#/limits).
    The returned data
    includes the current usage cycle, a summary of your limits, and your current usage.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetLimitsResponse
     """


    return (await asyncio_detailed(
        client=client,

    )).parsed

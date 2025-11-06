from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.get_monthly_usage_response import GetMonthlyUsageResponse
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    *,
    date: str | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["date"] = date


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/users/me/usage/monthly",
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetMonthlyUsageResponse | None:
    if response.status_code == 200:
        response_200 = GetMonthlyUsageResponse.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetMonthlyUsageResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    date: str | Unset = UNSET,

) -> Response[GetMonthlyUsageResponse]:
    """ Get monthly usage

     Returns a complete summary of your usage for the current usage cycle,
    an overall sum, as well as a daily breakdown of usage. It is the same
    information you will see on your account's [Billing page](https://console.apify.com/billing#/usage).
    The information
    includes your use of storage, data transfer, and request queue usage.

    Using the `date` parameter will show your usage in the usage cycle that
    includes that date.

    Args:
        date (str | Unset):  Example: 2020-06-14.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetMonthlyUsageResponse]
     """


    kwargs = _get_kwargs(
        date=date,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient | Client,
    date: str | Unset = UNSET,

) -> GetMonthlyUsageResponse | None:
    """ Get monthly usage

     Returns a complete summary of your usage for the current usage cycle,
    an overall sum, as well as a daily breakdown of usage. It is the same
    information you will see on your account's [Billing page](https://console.apify.com/billing#/usage).
    The information
    includes your use of storage, data transfer, and request queue usage.

    Using the `date` parameter will show your usage in the usage cycle that
    includes that date.

    Args:
        date (str | Unset):  Example: 2020-06-14.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetMonthlyUsageResponse
     """


    return sync_detailed(
        client=client,
date=date,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    date: str | Unset = UNSET,

) -> Response[GetMonthlyUsageResponse]:
    """ Get monthly usage

     Returns a complete summary of your usage for the current usage cycle,
    an overall sum, as well as a daily breakdown of usage. It is the same
    information you will see on your account's [Billing page](https://console.apify.com/billing#/usage).
    The information
    includes your use of storage, data transfer, and request queue usage.

    Using the `date` parameter will show your usage in the usage cycle that
    includes that date.

    Args:
        date (str | Unset):  Example: 2020-06-14.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetMonthlyUsageResponse]
     """


    kwargs = _get_kwargs(
        date=date,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    date: str | Unset = UNSET,

) -> GetMonthlyUsageResponse | None:
    """ Get monthly usage

     Returns a complete summary of your usage for the current usage cycle,
    an overall sum, as well as a daily breakdown of usage. It is the same
    information you will see on your account's [Billing page](https://console.apify.com/billing#/usage).
    The information
    includes your use of storage, data transfer, and request queue usage.

    Using the `date` parameter will show your usage in the usage cycle that
    includes that date.

    Args:
        date (str | Unset):  Example: 2020-06-14.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetMonthlyUsageResponse
     """


    return (await asyncio_detailed(
        client=client,
date=date,

    )).parsed

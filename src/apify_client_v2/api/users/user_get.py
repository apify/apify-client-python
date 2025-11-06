from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.get_public_user_data_response import GetPublicUserDataResponse
from typing import cast



def _get_kwargs(
    user_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/users/{user_id}".format(user_id=user_id,),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetPublicUserDataResponse | None:
    if response.status_code == 200:
        response_200 = GetPublicUserDataResponse.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetPublicUserDataResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    user_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[GetPublicUserDataResponse]:
    """ Get public user data

     Returns public information about a specific user account, similar to what
    can be seen on public profile pages (e.g. https://apify.com/apify).

    This operation requires no authentication token.

    Args:
        user_id (str):  Example: HGzIk8z78YcAPEB.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetPublicUserDataResponse]
     """


    kwargs = _get_kwargs(
        user_id=user_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    user_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> GetPublicUserDataResponse | None:
    """ Get public user data

     Returns public information about a specific user account, similar to what
    can be seen on public profile pages (e.g. https://apify.com/apify).

    This operation requires no authentication token.

    Args:
        user_id (str):  Example: HGzIk8z78YcAPEB.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetPublicUserDataResponse
     """


    return sync_detailed(
        user_id=user_id,
client=client,

    ).parsed

async def asyncio_detailed(
    user_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[GetPublicUserDataResponse]:
    """ Get public user data

     Returns public information about a specific user account, similar to what
    can be seen on public profile pages (e.g. https://apify.com/apify).

    This operation requires no authentication token.

    Args:
        user_id (str):  Example: HGzIk8z78YcAPEB.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetPublicUserDataResponse]
     """


    kwargs = _get_kwargs(
        user_id=user_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    user_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> GetPublicUserDataResponse | None:
    """ Get public user data

     Returns public information about a specific user account, similar to what
    can be seen on public profile pages (e.g. https://apify.com/apify).

    This operation requires no authentication token.

    Args:
        user_id (str):  Example: HGzIk8z78YcAPEB.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetPublicUserDataResponse
     """


    return (await asyncio_detailed(
        user_id=user_id,
client=client,

    )).parsed

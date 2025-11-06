from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.get_list_of_actors_in_store_response import GetListOfActorsInStoreResponse
from ...models.store_get_pricing_model import StoreGetPricingModel
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    *,
    limit: float | Unset = UNSET,
    offset: float | Unset = UNSET,
    search: str | Unset = UNSET,
    sort_by: str | Unset = UNSET,
    category: str | Unset = UNSET,
    username: str | Unset = UNSET,
    pricing_model: StoreGetPricingModel | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["limit"] = limit

    params["offset"] = offset

    params["search"] = search

    params["sortBy"] = sort_by

    params["category"] = category

    params["username"] = username

    json_pricing_model: str | Unset = UNSET
    if not isinstance(pricing_model, Unset):
        json_pricing_model = pricing_model.value

    params["pricingModel"] = json_pricing_model


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/store",
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetListOfActorsInStoreResponse | None:
    if response.status_code == 200:
        response_200 = GetListOfActorsInStoreResponse.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetListOfActorsInStoreResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    limit: float | Unset = UNSET,
    offset: float | Unset = UNSET,
    search: str | Unset = UNSET,
    sort_by: str | Unset = UNSET,
    category: str | Unset = UNSET,
    username: str | Unset = UNSET,
    pricing_model: StoreGetPricingModel | Unset = UNSET,

) -> Response[GetListOfActorsInStoreResponse]:
    """ Get list of Actors in store

     Gets the list of public Actors in Apify Store. You can use `search`
    parameter to search Actors by string in title, name, description, username
    and readme.
    If you need detailed info about a specific Actor, use the [Get
    Actor](#/reference/actors/actor-object/get-actor) endpoint.

    The endpoint supports pagination using the `limit` and `offset` parameters.
    It will not return more than 1,000 records.

    Args:
        limit (float | Unset):  Example: 99.
        offset (float | Unset):  Example: 10.
        search (str | Unset):  Example: web scraper.
        sort_by (str | Unset):  Example: 'popularity'.
        category (str | Unset):  Example: 'AI'.
        username (str | Unset):  Example: 'apify'.
        pricing_model (StoreGetPricingModel | Unset):  Example: 'FREE'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetListOfActorsInStoreResponse]
     """


    kwargs = _get_kwargs(
        limit=limit,
offset=offset,
search=search,
sort_by=sort_by,
category=category,
username=username,
pricing_model=pricing_model,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient | Client,
    limit: float | Unset = UNSET,
    offset: float | Unset = UNSET,
    search: str | Unset = UNSET,
    sort_by: str | Unset = UNSET,
    category: str | Unset = UNSET,
    username: str | Unset = UNSET,
    pricing_model: StoreGetPricingModel | Unset = UNSET,

) -> GetListOfActorsInStoreResponse | None:
    """ Get list of Actors in store

     Gets the list of public Actors in Apify Store. You can use `search`
    parameter to search Actors by string in title, name, description, username
    and readme.
    If you need detailed info about a specific Actor, use the [Get
    Actor](#/reference/actors/actor-object/get-actor) endpoint.

    The endpoint supports pagination using the `limit` and `offset` parameters.
    It will not return more than 1,000 records.

    Args:
        limit (float | Unset):  Example: 99.
        offset (float | Unset):  Example: 10.
        search (str | Unset):  Example: web scraper.
        sort_by (str | Unset):  Example: 'popularity'.
        category (str | Unset):  Example: 'AI'.
        username (str | Unset):  Example: 'apify'.
        pricing_model (StoreGetPricingModel | Unset):  Example: 'FREE'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetListOfActorsInStoreResponse
     """


    return sync_detailed(
        client=client,
limit=limit,
offset=offset,
search=search,
sort_by=sort_by,
category=category,
username=username,
pricing_model=pricing_model,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    limit: float | Unset = UNSET,
    offset: float | Unset = UNSET,
    search: str | Unset = UNSET,
    sort_by: str | Unset = UNSET,
    category: str | Unset = UNSET,
    username: str | Unset = UNSET,
    pricing_model: StoreGetPricingModel | Unset = UNSET,

) -> Response[GetListOfActorsInStoreResponse]:
    """ Get list of Actors in store

     Gets the list of public Actors in Apify Store. You can use `search`
    parameter to search Actors by string in title, name, description, username
    and readme.
    If you need detailed info about a specific Actor, use the [Get
    Actor](#/reference/actors/actor-object/get-actor) endpoint.

    The endpoint supports pagination using the `limit` and `offset` parameters.
    It will not return more than 1,000 records.

    Args:
        limit (float | Unset):  Example: 99.
        offset (float | Unset):  Example: 10.
        search (str | Unset):  Example: web scraper.
        sort_by (str | Unset):  Example: 'popularity'.
        category (str | Unset):  Example: 'AI'.
        username (str | Unset):  Example: 'apify'.
        pricing_model (StoreGetPricingModel | Unset):  Example: 'FREE'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetListOfActorsInStoreResponse]
     """


    kwargs = _get_kwargs(
        limit=limit,
offset=offset,
search=search,
sort_by=sort_by,
category=category,
username=username,
pricing_model=pricing_model,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    limit: float | Unset = UNSET,
    offset: float | Unset = UNSET,
    search: str | Unset = UNSET,
    sort_by: str | Unset = UNSET,
    category: str | Unset = UNSET,
    username: str | Unset = UNSET,
    pricing_model: StoreGetPricingModel | Unset = UNSET,

) -> GetListOfActorsInStoreResponse | None:
    """ Get list of Actors in store

     Gets the list of public Actors in Apify Store. You can use `search`
    parameter to search Actors by string in title, name, description, username
    and readme.
    If you need detailed info about a specific Actor, use the [Get
    Actor](#/reference/actors/actor-object/get-actor) endpoint.

    The endpoint supports pagination using the `limit` and `offset` parameters.
    It will not return more than 1,000 records.

    Args:
        limit (float | Unset):  Example: 99.
        offset (float | Unset):  Example: 10.
        search (str | Unset):  Example: web scraper.
        sort_by (str | Unset):  Example: 'popularity'.
        category (str | Unset):  Example: 'AI'.
        username (str | Unset):  Example: 'apify'.
        pricing_model (StoreGetPricingModel | Unset):  Example: 'FREE'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetListOfActorsInStoreResponse
     """


    return (await asyncio_detailed(
        client=client,
limit=limit,
offset=offset,
search=search,
sort_by=sort_by,
category=category,
username=username,
pricing_model=pricing_model,

    )).parsed

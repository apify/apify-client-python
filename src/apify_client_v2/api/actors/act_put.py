from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.act_update import ActUpdate
from ...models.update_actor_response import UpdateActorResponse
from typing import cast



def _get_kwargs(
    actor_id: str,
    *,
    body: ActUpdate,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v2/acts/{actor_id}".format(actor_id=actor_id,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> UpdateActorResponse | None:
    if response.status_code == 200:
        response_200 = UpdateActorResponse.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[UpdateActorResponse]:
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
    body: ActUpdate,

) -> Response[UpdateActorResponse]:
    """ Update Actor

     Updates settings of an Actor using values specified by an Actor object
    passed as JSON in the POST payload.
    If the object does not define a specific property, its value will not be
    updated.

    The response is the full Actor object as returned by the
    [Get Actor](#/reference/actors/actor-object/get-actor) endpoint.

    The request needs to specify the `Content-Type: application/json` HTTP header!

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    If you want to make your Actor
    [public](https://docs.apify.com/platform/actors/publishing) using `isPublic:
    true`, you will need to provide the Actor's `title` and the `categories`
    under which that Actor will be classified in Apify Store. For this, it's
    best to use the [constants from our `apify-shared-js`
    package](https://github.com/apify/apify-shared-
    js/blob/2d43ebc41ece9ad31cd6525bd523fb86939bf860/packages/consts/src/consts.ts#L452-L471).

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        body (ActUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UpdateActorResponse]
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
    body: ActUpdate,

) -> UpdateActorResponse | None:
    """ Update Actor

     Updates settings of an Actor using values specified by an Actor object
    passed as JSON in the POST payload.
    If the object does not define a specific property, its value will not be
    updated.

    The response is the full Actor object as returned by the
    [Get Actor](#/reference/actors/actor-object/get-actor) endpoint.

    The request needs to specify the `Content-Type: application/json` HTTP header!

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    If you want to make your Actor
    [public](https://docs.apify.com/platform/actors/publishing) using `isPublic:
    true`, you will need to provide the Actor's `title` and the `categories`
    under which that Actor will be classified in Apify Store. For this, it's
    best to use the [constants from our `apify-shared-js`
    package](https://github.com/apify/apify-shared-
    js/blob/2d43ebc41ece9ad31cd6525bd523fb86939bf860/packages/consts/src/consts.ts#L452-L471).

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        body (ActUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UpdateActorResponse
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
    body: ActUpdate,

) -> Response[UpdateActorResponse]:
    """ Update Actor

     Updates settings of an Actor using values specified by an Actor object
    passed as JSON in the POST payload.
    If the object does not define a specific property, its value will not be
    updated.

    The response is the full Actor object as returned by the
    [Get Actor](#/reference/actors/actor-object/get-actor) endpoint.

    The request needs to specify the `Content-Type: application/json` HTTP header!

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    If you want to make your Actor
    [public](https://docs.apify.com/platform/actors/publishing) using `isPublic:
    true`, you will need to provide the Actor's `title` and the `categories`
    under which that Actor will be classified in Apify Store. For this, it's
    best to use the [constants from our `apify-shared-js`
    package](https://github.com/apify/apify-shared-
    js/blob/2d43ebc41ece9ad31cd6525bd523fb86939bf860/packages/consts/src/consts.ts#L452-L471).

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        body (ActUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UpdateActorResponse]
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
    body: ActUpdate,

) -> UpdateActorResponse | None:
    """ Update Actor

     Updates settings of an Actor using values specified by an Actor object
    passed as JSON in the POST payload.
    If the object does not define a specific property, its value will not be
    updated.

    The response is the full Actor object as returned by the
    [Get Actor](#/reference/actors/actor-object/get-actor) endpoint.

    The request needs to specify the `Content-Type: application/json` HTTP header!

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    If you want to make your Actor
    [public](https://docs.apify.com/platform/actors/publishing) using `isPublic:
    true`, you will need to provide the Actor's `title` and the `categories`
    under which that Actor will be classified in Apify Store. For this, it's
    best to use the [constants from our `apify-shared-js`
    package](https://github.com/apify/apify-shared-
    js/blob/2d43ebc41ece9ad31cd6525bd523fb86939bf860/packages/consts/src/consts.ts#L452-L471).

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        body (ActUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UpdateActorResponse
     """


    return (await asyncio_detailed(
        actor_id=actor_id,
client=client,
body=body,

    )).parsed

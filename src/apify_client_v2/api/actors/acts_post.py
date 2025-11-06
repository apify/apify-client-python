from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.create_actor_request import CreateActorRequest
from ...models.create_actor_response import CreateActorResponse
from typing import cast



def _get_kwargs(
    *,
    body: CreateActorRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v2/acts",
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> CreateActorResponse | None:
    if response.status_code == 201:
        response_201 = CreateActorResponse.from_dict(response.json())



        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[CreateActorResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateActorRequest,

) -> Response[CreateActorResponse]:
    """ Create Actor

     Creates a new Actor with settings specified in an Actor object passed as
    JSON in the POST payload.
    The response is the full Actor object as returned by the
    [Get Actor](#/reference/actors/actor-object/get-actor) endpoint.

    The HTTP request must have the `Content-Type: application/json` HTTP header!

    The Actor needs to define at least one version of the source code.
    For more information, see [Version object](#/reference/actors/version-object).

    If you want to make your Actor
    [public](https://docs.apify.com/platform/actors/publishing) using `isPublic:
    true`, you will need to provide the Actor's `title` and the `categories`
    under which that Actor will be classified in Apify Store. For this, it's
    best to use the [constants from our `apify-shared-js`
    package](https://github.com/apify/apify-shared-
    js/blob/2d43ebc41ece9ad31cd6525bd523fb86939bf860/packages/consts/src/consts.ts#L452-L471).

    Args:
        body (CreateActorRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateActorResponse]
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
    body: CreateActorRequest,

) -> CreateActorResponse | None:
    """ Create Actor

     Creates a new Actor with settings specified in an Actor object passed as
    JSON in the POST payload.
    The response is the full Actor object as returned by the
    [Get Actor](#/reference/actors/actor-object/get-actor) endpoint.

    The HTTP request must have the `Content-Type: application/json` HTTP header!

    The Actor needs to define at least one version of the source code.
    For more information, see [Version object](#/reference/actors/version-object).

    If you want to make your Actor
    [public](https://docs.apify.com/platform/actors/publishing) using `isPublic:
    true`, you will need to provide the Actor's `title` and the `categories`
    under which that Actor will be classified in Apify Store. For this, it's
    best to use the [constants from our `apify-shared-js`
    package](https://github.com/apify/apify-shared-
    js/blob/2d43ebc41ece9ad31cd6525bd523fb86939bf860/packages/consts/src/consts.ts#L452-L471).

    Args:
        body (CreateActorRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateActorResponse
     """


    return sync_detailed(
        client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateActorRequest,

) -> Response[CreateActorResponse]:
    """ Create Actor

     Creates a new Actor with settings specified in an Actor object passed as
    JSON in the POST payload.
    The response is the full Actor object as returned by the
    [Get Actor](#/reference/actors/actor-object/get-actor) endpoint.

    The HTTP request must have the `Content-Type: application/json` HTTP header!

    The Actor needs to define at least one version of the source code.
    For more information, see [Version object](#/reference/actors/version-object).

    If you want to make your Actor
    [public](https://docs.apify.com/platform/actors/publishing) using `isPublic:
    true`, you will need to provide the Actor's `title` and the `categories`
    under which that Actor will be classified in Apify Store. For this, it's
    best to use the [constants from our `apify-shared-js`
    package](https://github.com/apify/apify-shared-
    js/blob/2d43ebc41ece9ad31cd6525bd523fb86939bf860/packages/consts/src/consts.ts#L452-L471).

    Args:
        body (CreateActorRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateActorResponse]
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
    body: CreateActorRequest,

) -> CreateActorResponse | None:
    """ Create Actor

     Creates a new Actor with settings specified in an Actor object passed as
    JSON in the POST payload.
    The response is the full Actor object as returned by the
    [Get Actor](#/reference/actors/actor-object/get-actor) endpoint.

    The HTTP request must have the `Content-Type: application/json` HTTP header!

    The Actor needs to define at least one version of the source code.
    For more information, see [Version object](#/reference/actors/version-object).

    If you want to make your Actor
    [public](https://docs.apify.com/platform/actors/publishing) using `isPublic:
    true`, you will need to provide the Actor's `title` and the `categories`
    under which that Actor will be classified in Apify Store. For this, it's
    best to use the [constants from our `apify-shared-js`
    package](https://github.com/apify/apify-shared-
    js/blob/2d43ebc41ece9ad31cd6525bd523fb86939bf860/packages/consts/src/consts.ts#L452-L471).

    Args:
        body (CreateActorRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateActorResponse
     """


    return (await asyncio_detailed(
        client=client,
body=body,

    )).parsed

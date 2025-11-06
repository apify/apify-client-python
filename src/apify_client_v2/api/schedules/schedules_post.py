from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.create_schedule_response import CreateScheduleResponse
from ...models.schedule_create import ScheduleCreate
from typing import cast



def _get_kwargs(
    *,
    body: ScheduleCreate,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v2/schedules",
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> CreateScheduleResponse | None:
    if response.status_code == 201:
        response_201 = CreateScheduleResponse.from_dict(response.json())



        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[CreateScheduleResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ScheduleCreate,

) -> Response[CreateScheduleResponse]:
    """ Create schedule

     Creates a new schedule with settings provided by the schedule object passed
    as JSON in the payload. The response is the created schedule object.

    The request needs to specify the `Content-Type: application/json` HTTP header!

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    Args:
        body (ScheduleCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateScheduleResponse]
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
    body: ScheduleCreate,

) -> CreateScheduleResponse | None:
    """ Create schedule

     Creates a new schedule with settings provided by the schedule object passed
    as JSON in the payload. The response is the created schedule object.

    The request needs to specify the `Content-Type: application/json` HTTP header!

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    Args:
        body (ScheduleCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateScheduleResponse
     """


    return sync_detailed(
        client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ScheduleCreate,

) -> Response[CreateScheduleResponse]:
    """ Create schedule

     Creates a new schedule with settings provided by the schedule object passed
    as JSON in the payload. The response is the created schedule object.

    The request needs to specify the `Content-Type: application/json` HTTP header!

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    Args:
        body (ScheduleCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateScheduleResponse]
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
    body: ScheduleCreate,

) -> CreateScheduleResponse | None:
    """ Create schedule

     Creates a new schedule with settings provided by the schedule object passed
    as JSON in the payload. The response is the created schedule object.

    The request needs to specify the `Content-Type: application/json` HTTP header!

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    Args:
        body (ScheduleCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateScheduleResponse
     """


    return (await asyncio_detailed(
        client=client,
body=body,

    )).parsed

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
    schedule_id: str,
    *,
    body: ScheduleCreate,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v2/schedules/{schedule_id}".format(schedule_id=schedule_id,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> CreateScheduleResponse | None:
    if response.status_code == 200:
        response_200 = CreateScheduleResponse.from_dict(response.json())



        return response_200

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
    schedule_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ScheduleCreate,

) -> Response[CreateScheduleResponse]:
    """ Update schedule

     Updates a schedule using values specified by a schedule object passed as
    JSON in the POST payload. If the object does not define a specific property,
    its value will not be updated.

    The response is the full schedule object as returned by the
    [Get schedule](#/reference/schedules/schedule-object/get-schedule) endpoint.

    **The request needs to specify the `Content-Type: application/json` HTTP
    header!**

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    Args:
        schedule_id (str):  Example: asdLZtadYvn4mBZmm.
        body (ScheduleCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateScheduleResponse]
     """


    kwargs = _get_kwargs(
        schedule_id=schedule_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    schedule_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ScheduleCreate,

) -> CreateScheduleResponse | None:
    """ Update schedule

     Updates a schedule using values specified by a schedule object passed as
    JSON in the POST payload. If the object does not define a specific property,
    its value will not be updated.

    The response is the full schedule object as returned by the
    [Get schedule](#/reference/schedules/schedule-object/get-schedule) endpoint.

    **The request needs to specify the `Content-Type: application/json` HTTP
    header!**

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    Args:
        schedule_id (str):  Example: asdLZtadYvn4mBZmm.
        body (ScheduleCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateScheduleResponse
     """


    return sync_detailed(
        schedule_id=schedule_id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    schedule_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ScheduleCreate,

) -> Response[CreateScheduleResponse]:
    """ Update schedule

     Updates a schedule using values specified by a schedule object passed as
    JSON in the POST payload. If the object does not define a specific property,
    its value will not be updated.

    The response is the full schedule object as returned by the
    [Get schedule](#/reference/schedules/schedule-object/get-schedule) endpoint.

    **The request needs to specify the `Content-Type: application/json` HTTP
    header!**

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    Args:
        schedule_id (str):  Example: asdLZtadYvn4mBZmm.
        body (ScheduleCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateScheduleResponse]
     """


    kwargs = _get_kwargs(
        schedule_id=schedule_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    schedule_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ScheduleCreate,

) -> CreateScheduleResponse | None:
    """ Update schedule

     Updates a schedule using values specified by a schedule object passed as
    JSON in the POST payload. If the object does not define a specific property,
    its value will not be updated.

    The response is the full schedule object as returned by the
    [Get schedule](#/reference/schedules/schedule-object/get-schedule) endpoint.

    **The request needs to specify the `Content-Type: application/json` HTTP
    header!**

    When providing your API authentication token, we recommend using the
    request's `Authorization` header, rather than the URL. ([More
    info](#/introduction/authentication)).

    Args:
        schedule_id (str):  Example: asdLZtadYvn4mBZmm.
        body (ScheduleCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateScheduleResponse
     """


    return (await asyncio_detailed(
        schedule_id=schedule_id,
client=client,
body=body,

    )).parsed

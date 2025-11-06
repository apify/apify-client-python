from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.get_schedule_log_response import GetScheduleLogResponse
from typing import cast



def _get_kwargs(
    schedule_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/schedules/{schedule_id}/log".format(schedule_id=schedule_id,),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetScheduleLogResponse | None:
    if response.status_code == 200:
        response_200 = GetScheduleLogResponse.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetScheduleLogResponse]:
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

) -> Response[GetScheduleLogResponse]:
    """ Get schedule log

     Gets the schedule log as a JSON array containing information about up to a
    1000 invocations of the schedule.

    Args:
        schedule_id (str):  Example: asdLZtadYvn4mBZmm.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetScheduleLogResponse]
     """


    kwargs = _get_kwargs(
        schedule_id=schedule_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    schedule_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> GetScheduleLogResponse | None:
    """ Get schedule log

     Gets the schedule log as a JSON array containing information about up to a
    1000 invocations of the schedule.

    Args:
        schedule_id (str):  Example: asdLZtadYvn4mBZmm.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetScheduleLogResponse
     """


    return sync_detailed(
        schedule_id=schedule_id,
client=client,

    ).parsed

async def asyncio_detailed(
    schedule_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[GetScheduleLogResponse]:
    """ Get schedule log

     Gets the schedule log as a JSON array containing information about up to a
    1000 invocations of the schedule.

    Args:
        schedule_id (str):  Example: asdLZtadYvn4mBZmm.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetScheduleLogResponse]
     """


    kwargs = _get_kwargs(
        schedule_id=schedule_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    schedule_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> GetScheduleLogResponse | None:
    """ Get schedule log

     Gets the schedule log as a JSON array containing information about up to a
    1000 invocations of the schedule.

    Args:
        schedule_id (str):  Example: asdLZtadYvn4mBZmm.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetScheduleLogResponse
     """


    return (await asyncio_detailed(
        schedule_id=schedule_id,
client=client,

    )).parsed

from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.schedule_delete_response_204 import ScheduleDeleteResponse204
from typing import cast



def _get_kwargs(
    schedule_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/v2/schedules/{schedule_id}".format(schedule_id=schedule_id,),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ScheduleDeleteResponse204 | None:
    if response.status_code == 204:
        response_204 = ScheduleDeleteResponse204.from_dict(response.json())



        return response_204

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ScheduleDeleteResponse204]:
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

) -> Response[ScheduleDeleteResponse204]:
    """ Delete schedule

     Deletes a schedule.

    Args:
        schedule_id (str):  Example: asdLZtadYvn4mBZmm.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ScheduleDeleteResponse204]
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

) -> ScheduleDeleteResponse204 | None:
    """ Delete schedule

     Deletes a schedule.

    Args:
        schedule_id (str):  Example: asdLZtadYvn4mBZmm.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ScheduleDeleteResponse204
     """


    return sync_detailed(
        schedule_id=schedule_id,
client=client,

    ).parsed

async def asyncio_detailed(
    schedule_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[ScheduleDeleteResponse204]:
    """ Delete schedule

     Deletes a schedule.

    Args:
        schedule_id (str):  Example: asdLZtadYvn4mBZmm.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ScheduleDeleteResponse204]
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

) -> ScheduleDeleteResponse204 | None:
    """ Delete schedule

     Deletes a schedule.

    Args:
        schedule_id (str):  Example: asdLZtadYvn4mBZmm.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ScheduleDeleteResponse204
     """


    return (await asyncio_detailed(
        schedule_id=schedule_id,
client=client,

    )).parsed

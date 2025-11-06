from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.get_dataset_statistics_response import GetDatasetStatisticsResponse
from typing import cast



def _get_kwargs(
    dataset_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/datasets/{dataset_id}/statistics".format(dataset_id=dataset_id,),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetDatasetStatisticsResponse | None:
    if response.status_code == 200:
        response_200 = GetDatasetStatisticsResponse.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetDatasetStatisticsResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[GetDatasetStatisticsResponse]:
    """ Get dataset statistics

     Returns statistics for given dataset.

    Provides only [field statistics](https://docs.apify.com/platform/actors/development/actor-
    definition/dataset-schema/validation#dataset-field-statistics).

    Args:
        dataset_id (str):  Example: WkzbQMuFYuamGv3YF.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetDatasetStatisticsResponse]
     """


    kwargs = _get_kwargs(
        dataset_id=dataset_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> GetDatasetStatisticsResponse | None:
    """ Get dataset statistics

     Returns statistics for given dataset.

    Provides only [field statistics](https://docs.apify.com/platform/actors/development/actor-
    definition/dataset-schema/validation#dataset-field-statistics).

    Args:
        dataset_id (str):  Example: WkzbQMuFYuamGv3YF.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetDatasetStatisticsResponse
     """


    return sync_detailed(
        dataset_id=dataset_id,
client=client,

    ).parsed

async def asyncio_detailed(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[GetDatasetStatisticsResponse]:
    """ Get dataset statistics

     Returns statistics for given dataset.

    Provides only [field statistics](https://docs.apify.com/platform/actors/development/actor-
    definition/dataset-schema/validation#dataset-field-statistics).

    Args:
        dataset_id (str):  Example: WkzbQMuFYuamGv3YF.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetDatasetStatisticsResponse]
     """


    kwargs = _get_kwargs(
        dataset_id=dataset_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> GetDatasetStatisticsResponse | None:
    """ Get dataset statistics

     Returns statistics for given dataset.

    Provides only [field statistics](https://docs.apify.com/platform/actors/development/actor-
    definition/dataset-schema/validation#dataset-field-statistics).

    Args:
        dataset_id (str):  Example: WkzbQMuFYuamGv3YF.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetDatasetStatisticsResponse
     """


    return (await asyncio_detailed(
        dataset_id=dataset_id,
client=client,

    )).parsed

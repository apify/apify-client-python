from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.dataset_response import DatasetResponse
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    dataset_id: str,
    *,
    token: str | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["token"] = token


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/datasets/{dataset_id}".format(dataset_id=dataset_id,),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> DatasetResponse | None:
    if response.status_code == 200:
        response_200 = DatasetResponse.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[DatasetResponse]:
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
    token: str | Unset = UNSET,

) -> Response[DatasetResponse]:
    """ Get dataset

     Returns dataset object for given dataset ID.

    This does not return dataset items, only information about the storage itself.
    To retrieve dataset items, use the [List dataset items](/api/v2/dataset-items-get) endpoint.

    :::note

    Keep in mind that attributes `itemCount` and `cleanItemCount` are not propagated right away after
    data are pushed into a dataset.

    :::

    There is a short period (up to 5 seconds) during which these counters may not match with exact
    counts in dataset items.

    Args:
        dataset_id (str):  Example: WkzbQMuFYuamGv3YF.
        token (str | Unset):  Example: soSkq9ekdmfOslopH.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DatasetResponse]
     """


    kwargs = _get_kwargs(
        dataset_id=dataset_id,
token=token,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    token: str | Unset = UNSET,

) -> DatasetResponse | None:
    """ Get dataset

     Returns dataset object for given dataset ID.

    This does not return dataset items, only information about the storage itself.
    To retrieve dataset items, use the [List dataset items](/api/v2/dataset-items-get) endpoint.

    :::note

    Keep in mind that attributes `itemCount` and `cleanItemCount` are not propagated right away after
    data are pushed into a dataset.

    :::

    There is a short period (up to 5 seconds) during which these counters may not match with exact
    counts in dataset items.

    Args:
        dataset_id (str):  Example: WkzbQMuFYuamGv3YF.
        token (str | Unset):  Example: soSkq9ekdmfOslopH.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DatasetResponse
     """


    return sync_detailed(
        dataset_id=dataset_id,
client=client,
token=token,

    ).parsed

async def asyncio_detailed(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    token: str | Unset = UNSET,

) -> Response[DatasetResponse]:
    """ Get dataset

     Returns dataset object for given dataset ID.

    This does not return dataset items, only information about the storage itself.
    To retrieve dataset items, use the [List dataset items](/api/v2/dataset-items-get) endpoint.

    :::note

    Keep in mind that attributes `itemCount` and `cleanItemCount` are not propagated right away after
    data are pushed into a dataset.

    :::

    There is a short period (up to 5 seconds) during which these counters may not match with exact
    counts in dataset items.

    Args:
        dataset_id (str):  Example: WkzbQMuFYuamGv3YF.
        token (str | Unset):  Example: soSkq9ekdmfOslopH.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DatasetResponse]
     """


    kwargs = _get_kwargs(
        dataset_id=dataset_id,
token=token,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    token: str | Unset = UNSET,

) -> DatasetResponse | None:
    """ Get dataset

     Returns dataset object for given dataset ID.

    This does not return dataset items, only information about the storage itself.
    To retrieve dataset items, use the [List dataset items](/api/v2/dataset-items-get) endpoint.

    :::note

    Keep in mind that attributes `itemCount` and `cleanItemCount` are not propagated right away after
    data are pushed into a dataset.

    :::

    There is a short period (up to 5 seconds) during which these counters may not match with exact
    counts in dataset items.

    Args:
        dataset_id (str):  Example: WkzbQMuFYuamGv3YF.
        token (str | Unset):  Example: soSkq9ekdmfOslopH.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DatasetResponse
     """


    return (await asyncio_detailed(
        dataset_id=dataset_id,
client=client,
token=token,

    )).parsed

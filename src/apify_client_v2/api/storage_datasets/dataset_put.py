from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.dataset_response import DatasetResponse
from ...models.update_dataset_request import UpdateDatasetRequest
from typing import cast



def _get_kwargs(
    dataset_id: str,
    *,
    body: UpdateDatasetRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v2/datasets/{dataset_id}".format(dataset_id=dataset_id,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
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
    body: UpdateDatasetRequest,

) -> Response[DatasetResponse]:
    """ Update dataset

     Updates a dataset's name using a value specified by a JSON object passed in the PUT payload.
    The response is the updated dataset object, as returned by the [Get
    dataset](#/reference/datasets/dataset-collection/get-dataset) API endpoint.

    Args:
        dataset_id (str):  Example: WkzbQMuFYuamGv3YF.
        body (UpdateDatasetRequest):  Example: {'name': 'new-dataset-name'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DatasetResponse]
     """


    kwargs = _get_kwargs(
        dataset_id=dataset_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateDatasetRequest,

) -> DatasetResponse | None:
    """ Update dataset

     Updates a dataset's name using a value specified by a JSON object passed in the PUT payload.
    The response is the updated dataset object, as returned by the [Get
    dataset](#/reference/datasets/dataset-collection/get-dataset) API endpoint.

    Args:
        dataset_id (str):  Example: WkzbQMuFYuamGv3YF.
        body (UpdateDatasetRequest):  Example: {'name': 'new-dataset-name'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DatasetResponse
     """


    return sync_detailed(
        dataset_id=dataset_id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateDatasetRequest,

) -> Response[DatasetResponse]:
    """ Update dataset

     Updates a dataset's name using a value specified by a JSON object passed in the PUT payload.
    The response is the updated dataset object, as returned by the [Get
    dataset](#/reference/datasets/dataset-collection/get-dataset) API endpoint.

    Args:
        dataset_id (str):  Example: WkzbQMuFYuamGv3YF.
        body (UpdateDatasetRequest):  Example: {'name': 'new-dataset-name'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DatasetResponse]
     """


    kwargs = _get_kwargs(
        dataset_id=dataset_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateDatasetRequest,

) -> DatasetResponse | None:
    """ Update dataset

     Updates a dataset's name using a value specified by a JSON object passed in the PUT payload.
    The response is the updated dataset object, as returned by the [Get
    dataset](#/reference/datasets/dataset-collection/get-dataset) API endpoint.

    Args:
        dataset_id (str):  Example: WkzbQMuFYuamGv3YF.
        body (UpdateDatasetRequest):  Example: {'name': 'new-dataset-name'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DatasetResponse
     """


    return (await asyncio_detailed(
        dataset_id=dataset_id,
client=client,
body=body,

    )).parsed

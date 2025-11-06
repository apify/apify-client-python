from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.dataset_items_post_response_201 import DatasetItemsPostResponse201
from ...models.dataset_items_post_response_400 import DatasetItemsPostResponse400
from ...models.put_items_request import PutItemsRequest
from typing import cast



def _get_kwargs(
    dataset_id: str,
    *,
    body: list[PutItemsRequest],

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v2/datasets/{dataset_id}/items".format(dataset_id=dataset_id,),
    }

    _kwargs["json"] = []
    for body_item_data in body:
        body_item = body_item_data.to_dict()
        _kwargs["json"].append(body_item)




    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> DatasetItemsPostResponse201 | DatasetItemsPostResponse400 | None:
    if response.status_code == 201:
        response_201 = DatasetItemsPostResponse201.from_dict(response.json())



        return response_201

    if response.status_code == 400:
        response_400 = DatasetItemsPostResponse400.from_dict(response.json())



        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[DatasetItemsPostResponse201 | DatasetItemsPostResponse400]:
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
    body: list[PutItemsRequest],

) -> Response[DatasetItemsPostResponse201 | DatasetItemsPostResponse400]:
    """ Store items

     Appends an item or an array of items to the end of the dataset.
    The POST payload is a JSON object or a JSON array of objects to save into the dataset.

    If the data you attempt to store in the dataset is invalid (meaning any of the items received by the
    API fails the validation), the whole request is discarded and the API will return a response with
    status code 400.
    For more information about dataset schema validation, see [Dataset
    schema](https://docs.apify.com/platform/actors/development/actor-definition/dataset-
    schema/validation).

    **IMPORTANT:** The limit of request payload size for the dataset is 5 MB. If the array exceeds the
    size, you'll need to split it into a number of smaller arrays.

    Args:
        dataset_id (str):  Example: WkzbQMuFYuamGv3YF.
        body (list[PutItemsRequest]):  Example: [{'foo': 'bar'}, {'foo': 'hotel'}, {'foo':
            'restaurant'}].

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DatasetItemsPostResponse201 | DatasetItemsPostResponse400]
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
    body: list[PutItemsRequest],

) -> DatasetItemsPostResponse201 | DatasetItemsPostResponse400 | None:
    """ Store items

     Appends an item or an array of items to the end of the dataset.
    The POST payload is a JSON object or a JSON array of objects to save into the dataset.

    If the data you attempt to store in the dataset is invalid (meaning any of the items received by the
    API fails the validation), the whole request is discarded and the API will return a response with
    status code 400.
    For more information about dataset schema validation, see [Dataset
    schema](https://docs.apify.com/platform/actors/development/actor-definition/dataset-
    schema/validation).

    **IMPORTANT:** The limit of request payload size for the dataset is 5 MB. If the array exceeds the
    size, you'll need to split it into a number of smaller arrays.

    Args:
        dataset_id (str):  Example: WkzbQMuFYuamGv3YF.
        body (list[PutItemsRequest]):  Example: [{'foo': 'bar'}, {'foo': 'hotel'}, {'foo':
            'restaurant'}].

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DatasetItemsPostResponse201 | DatasetItemsPostResponse400
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
    body: list[PutItemsRequest],

) -> Response[DatasetItemsPostResponse201 | DatasetItemsPostResponse400]:
    """ Store items

     Appends an item or an array of items to the end of the dataset.
    The POST payload is a JSON object or a JSON array of objects to save into the dataset.

    If the data you attempt to store in the dataset is invalid (meaning any of the items received by the
    API fails the validation), the whole request is discarded and the API will return a response with
    status code 400.
    For more information about dataset schema validation, see [Dataset
    schema](https://docs.apify.com/platform/actors/development/actor-definition/dataset-
    schema/validation).

    **IMPORTANT:** The limit of request payload size for the dataset is 5 MB. If the array exceeds the
    size, you'll need to split it into a number of smaller arrays.

    Args:
        dataset_id (str):  Example: WkzbQMuFYuamGv3YF.
        body (list[PutItemsRequest]):  Example: [{'foo': 'bar'}, {'foo': 'hotel'}, {'foo':
            'restaurant'}].

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DatasetItemsPostResponse201 | DatasetItemsPostResponse400]
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
    body: list[PutItemsRequest],

) -> DatasetItemsPostResponse201 | DatasetItemsPostResponse400 | None:
    """ Store items

     Appends an item or an array of items to the end of the dataset.
    The POST payload is a JSON object or a JSON array of objects to save into the dataset.

    If the data you attempt to store in the dataset is invalid (meaning any of the items received by the
    API fails the validation), the whole request is discarded and the API will return a response with
    status code 400.
    For more information about dataset schema validation, see [Dataset
    schema](https://docs.apify.com/platform/actors/development/actor-definition/dataset-
    schema/validation).

    **IMPORTANT:** The limit of request payload size for the dataset is 5 MB. If the array exceeds the
    size, you'll need to split it into a number of smaller arrays.

    Args:
        dataset_id (str):  Example: WkzbQMuFYuamGv3YF.
        body (list[PutItemsRequest]):  Example: [{'foo': 'bar'}, {'foo': 'hotel'}, {'foo':
            'restaurant'}].

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DatasetItemsPostResponse201 | DatasetItemsPostResponse400
     """


    return (await asyncio_detailed(
        dataset_id=dataset_id,
client=client,
body=body,

    )).parsed

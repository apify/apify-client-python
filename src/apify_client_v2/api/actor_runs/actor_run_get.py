from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...types import UNSET, Unset



def _get_kwargs(
    run_id: str,
    *,
    wait_for_finish: float | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["waitForFinish"] = wait_for_finish


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/actor-runs/{run_id}".format(run_id=run_id,),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | None:
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    run_id: str,
    *,
    client: AuthenticatedClient | Client,
    wait_for_finish: float | Unset = UNSET,

) -> Response[Any]:
    """ Get run

     This is not a single endpoint, but an entire group of endpoints that lets
    you retrieve the run or any of its default storages.

    The endpoints accept the same HTTP methods and query parameters as
    the respective storage endpoints.

    The base path that represents the Actor run object is:

    `/v2/actor-runs/{runId}{?token}`

    In order to access the default storages of the Actor run, i.e. log,
    key-value store, dataset and request queue, use the following endpoints:

    * `/v2/actor-runs/{runId}/log{?token}`
    * `/v2/actor-runs/{runId}/key-value-store{?token}`
    * `/v2/actor-runs/{runId}/dataset{?token}`
    * `/v2/actor-runs/{runId}/request-queue{?token}`

    These API endpoints have the same usage as the equivalent storage endpoints.

    For example, `/v2/actor-runs/{runId}/key-value-store` has the same HTTP method and
    parameters as the [Key-value store object](#/reference/key-value-stores/store-object) endpoint.

    Additionally, each of the above API endpoints supports all sub-endpoints
    of the original one:

    #### Log

    * `/v2/actor-runs/{runId}/log` [Log](#/reference/logs)

    #### Key-value store

    * `/v2/actor-runs/{runId}/key-value-store/keys{?token}` [Key
    collection](#/reference/key-value-stores/key-collection)
    * `/v2/actor-runs/{runId}/key-value-store/records/{recordKey}{?token}`
    [Record](#/reference/key-value-stores/record)

    #### Dataset

    * `/v2/actor-runs/{runId}/dataset/items{?token}` [Item
    collection](#/reference/datasets/item-collection)

    #### Request queue

    * `/v2/actor-runs/{runId}/request-queue/requests{?token}` [Request
    collection](#/reference/request-queues/request-collection)
    * `/v2/actor-runs/{runId}/request-queue/requests/{requestId}{?token}`
    [Request collection](#/reference/request-queues/request)
    * `/v2/actor-runs/{runId}/request-queue/head{?token}` [Queue
    head](#/reference/request-queues/queue-head)

    For example, to download data from a dataset of the Actor run in XML format,
    send HTTP GET request to the following URL:

    ```
    https://api.apify.com/v2/actor-runs/{runId}/dataset/items?format=xml
    ```

    In order to save new items to the dataset, send HTTP POST request with JSON
    payload to the same URL.

    Gets an object that contains all the details about a
    specific run of an Actor.

    By passing the optional `waitForFinish` parameter the API endpoint will synchronously wait
    for the run to finish. This is useful to avoid periodic polling when waiting for Actor run to
    complete.

    This endpoint does not require the authentication token. Instead, calls are authenticated using a
    hard-to-guess ID of the run. However,
    if you access the endpoint without the token, certain attributes, such as `usageUsd` and
    `usageTotalUsd`, will be hidden.

    Args:
        run_id (str):  Example: 3KH8gEpp4d8uQSe8T.
        wait_for_finish (float | Unset):  Example: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        run_id=run_id,
wait_for_finish=wait_for_finish,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    run_id: str,
    *,
    client: AuthenticatedClient | Client,
    wait_for_finish: float | Unset = UNSET,

) -> Response[Any]:
    """ Get run

     This is not a single endpoint, but an entire group of endpoints that lets
    you retrieve the run or any of its default storages.

    The endpoints accept the same HTTP methods and query parameters as
    the respective storage endpoints.

    The base path that represents the Actor run object is:

    `/v2/actor-runs/{runId}{?token}`

    In order to access the default storages of the Actor run, i.e. log,
    key-value store, dataset and request queue, use the following endpoints:

    * `/v2/actor-runs/{runId}/log{?token}`
    * `/v2/actor-runs/{runId}/key-value-store{?token}`
    * `/v2/actor-runs/{runId}/dataset{?token}`
    * `/v2/actor-runs/{runId}/request-queue{?token}`

    These API endpoints have the same usage as the equivalent storage endpoints.

    For example, `/v2/actor-runs/{runId}/key-value-store` has the same HTTP method and
    parameters as the [Key-value store object](#/reference/key-value-stores/store-object) endpoint.

    Additionally, each of the above API endpoints supports all sub-endpoints
    of the original one:

    #### Log

    * `/v2/actor-runs/{runId}/log` [Log](#/reference/logs)

    #### Key-value store

    * `/v2/actor-runs/{runId}/key-value-store/keys{?token}` [Key
    collection](#/reference/key-value-stores/key-collection)
    * `/v2/actor-runs/{runId}/key-value-store/records/{recordKey}{?token}`
    [Record](#/reference/key-value-stores/record)

    #### Dataset

    * `/v2/actor-runs/{runId}/dataset/items{?token}` [Item
    collection](#/reference/datasets/item-collection)

    #### Request queue

    * `/v2/actor-runs/{runId}/request-queue/requests{?token}` [Request
    collection](#/reference/request-queues/request-collection)
    * `/v2/actor-runs/{runId}/request-queue/requests/{requestId}{?token}`
    [Request collection](#/reference/request-queues/request)
    * `/v2/actor-runs/{runId}/request-queue/head{?token}` [Queue
    head](#/reference/request-queues/queue-head)

    For example, to download data from a dataset of the Actor run in XML format,
    send HTTP GET request to the following URL:

    ```
    https://api.apify.com/v2/actor-runs/{runId}/dataset/items?format=xml
    ```

    In order to save new items to the dataset, send HTTP POST request with JSON
    payload to the same URL.

    Gets an object that contains all the details about a
    specific run of an Actor.

    By passing the optional `waitForFinish` parameter the API endpoint will synchronously wait
    for the run to finish. This is useful to avoid periodic polling when waiting for Actor run to
    complete.

    This endpoint does not require the authentication token. Instead, calls are authenticated using a
    hard-to-guess ID of the run. However,
    if you access the endpoint without the token, certain attributes, such as `usageUsd` and
    `usageTotalUsd`, will be hidden.

    Args:
        run_id (str):  Example: 3KH8gEpp4d8uQSe8T.
        wait_for_finish (float | Unset):  Example: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        run_id=run_id,
wait_for_finish=wait_for_finish,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)


from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...types import UNSET, Unset



def _get_kwargs(
    actor_task_id: str,
    *,
    status: str | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["status"] = status


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/actor-tasks/{actor_task_id}/runs/last".format(actor_task_id=actor_task_id,),
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
    actor_task_id: str,
    *,
    client: AuthenticatedClient | Client,
    status: str | Unset = UNSET,

) -> Response[Any]:
    """ Get last run

     This is not a single endpoint, but an entire group of endpoints that lets you to
    retrieve and manage the last run of given actor task or any of its default storages.
    All the endpoints require an authentication token.

    The endpoints accept the same HTTP methods and query parameters as
    the respective storage endpoints.
    The base path represents the last actor task run object is:

    `/v2/actor-tasks/{actorTaskId}/runs/last{?token,status}`

    Using the `status` query parameter you can ensure to only get a run with a certain status
    (e.g. `status=SUCCEEDED`). The output of this endpoint and other query parameters
    are the same as in the [Run object](/api/v2/actor-run-get) endpoint.

    In order to access the default storages of the last actor task run, i.e. log, key-value store,
    dataset and request queue,
    use the following endpoints:

    * `/v2/actor-tasks/{actorTaskId}/runs/last/log{?token,status}`
    * `/v2/actor-tasks/{actorTaskId}/runs/last/key-value-store{?token,status}`
    * `/v2/actor-tasks/{actorTaskId}/runs/last/dataset{?token,status}`
    * `/v2/actor-tasks/{actorTaskId}/runs/last/request-queue{?token,status}`

    These API endpoints have the same usage as the equivalent storage endpoints.
    For example,
    `/v2/actor-tasks/{actorTaskId}/runs/last/key-value-store` has the same HTTP method and parameters as
    the
    [Key-value store object](/api/v2/storage-key-value-stores) endpoint.

    Additionally, each of the above API endpoints supports all sub-endpoints
    of the original one:

    ##### Storage endpoints

    * [Dataset - introduction](/api/v2/storage-datasets)

    * [Key-value store - introduction](/api/v2/storage-key-value-stores)

    * [Request queue - introduction](/api/v2/storage-request-queues)

    For example, to download data from a dataset of the last succeeded actor task run in XML format,
    send HTTP GET request to the following URL:

    ```
    https://api.apify.com/v2/actor-
    tasks/{actorTaskId}/runs/last/dataset/items?token={yourApiToken}&format=xml&status=SUCCEEDED
    ```

    In order to save new items to the dataset, send HTTP POST request with JSON payload to the same URL.

    Args:
        actor_task_id (str):  Example: janedoe~my-task.
        status (str | Unset):  Example: SUCCEEDED.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        actor_task_id=actor_task_id,
status=status,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    actor_task_id: str,
    *,
    client: AuthenticatedClient | Client,
    status: str | Unset = UNSET,

) -> Response[Any]:
    """ Get last run

     This is not a single endpoint, but an entire group of endpoints that lets you to
    retrieve and manage the last run of given actor task or any of its default storages.
    All the endpoints require an authentication token.

    The endpoints accept the same HTTP methods and query parameters as
    the respective storage endpoints.
    The base path represents the last actor task run object is:

    `/v2/actor-tasks/{actorTaskId}/runs/last{?token,status}`

    Using the `status` query parameter you can ensure to only get a run with a certain status
    (e.g. `status=SUCCEEDED`). The output of this endpoint and other query parameters
    are the same as in the [Run object](/api/v2/actor-run-get) endpoint.

    In order to access the default storages of the last actor task run, i.e. log, key-value store,
    dataset and request queue,
    use the following endpoints:

    * `/v2/actor-tasks/{actorTaskId}/runs/last/log{?token,status}`
    * `/v2/actor-tasks/{actorTaskId}/runs/last/key-value-store{?token,status}`
    * `/v2/actor-tasks/{actorTaskId}/runs/last/dataset{?token,status}`
    * `/v2/actor-tasks/{actorTaskId}/runs/last/request-queue{?token,status}`

    These API endpoints have the same usage as the equivalent storage endpoints.
    For example,
    `/v2/actor-tasks/{actorTaskId}/runs/last/key-value-store` has the same HTTP method and parameters as
    the
    [Key-value store object](/api/v2/storage-key-value-stores) endpoint.

    Additionally, each of the above API endpoints supports all sub-endpoints
    of the original one:

    ##### Storage endpoints

    * [Dataset - introduction](/api/v2/storage-datasets)

    * [Key-value store - introduction](/api/v2/storage-key-value-stores)

    * [Request queue - introduction](/api/v2/storage-request-queues)

    For example, to download data from a dataset of the last succeeded actor task run in XML format,
    send HTTP GET request to the following URL:

    ```
    https://api.apify.com/v2/actor-
    tasks/{actorTaskId}/runs/last/dataset/items?token={yourApiToken}&format=xml&status=SUCCEEDED
    ```

    In order to save new items to the dataset, send HTTP POST request with JSON payload to the same URL.

    Args:
        actor_task_id (str):  Example: janedoe~my-task.
        status (str | Unset):  Example: SUCCEEDED.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        actor_task_id=actor_task_id,
status=status,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)


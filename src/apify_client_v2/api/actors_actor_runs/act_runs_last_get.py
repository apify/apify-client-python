from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...types import UNSET, Unset



def _get_kwargs(
    actor_id: str,
    *,
    status: str | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["status"] = status


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/acts/{actor_id}/runs/last".format(actor_id=actor_id,),
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
    actor_id: str,
    *,
    client: AuthenticatedClient | Client,
    status: str | Unset = UNSET,

) -> Response[Any]:
    """ Get last run

     This is not a single endpoint, but an entire group of endpoints that lets you to
    retrieve and manage the last run of given Actor or any of its default storages.
    All the endpoints require an authentication token.

    The endpoints accept the same HTTP methods and query parameters as
    the respective storage endpoints.
    The base path represents the last Actor run object is:

    `/v2/acts/{actorId}/runs/last{?token,status}`

    Using the `status` query parameter you can ensure to only get a run with a certain status
    (e.g. `status=SUCCEEDED`). The output of this endpoint and other query parameters
    are the same as in the [Run object](#/reference/actors/run-object) endpoint.

    In order to access the default storages of the last Actor run, i.e. log, key-value store, dataset
    and request queue,
    use the following endpoints:

    * `/v2/acts/{actorId}/runs/last/log{?token,status}`
    * `/v2/acts/{actorId}/runs/last/key-value-store{?token,status}`
    * `/v2/acts/{actorId}/runs/last/dataset{?token,status}`
    * `/v2/acts/{actorId}/runs/last/request-queue{?token,status}`

    These API endpoints have the same usage as the equivalent storage endpoints.
    For example,
    `/v2/acts/{actorId}/runs/last/key-value-store` has the same HTTP method and parameters as the
    [Key-value store object](#/reference/key-value-stores/store-object) endpoint.

    Additionally, each of the above API endpoints supports all sub-endpoints
    of the original one:

    #### Key-value store

    * `/v2/acts/{actorId}/runs/last/key-value-store/keys{?token,status}` [Key
    collection](#/reference/key-value-stores/key-collection)
    * `/v2/acts/{actorId}/runs/last/key-value-store/records/{recordKey}{?token,status}`
    [Record](#/reference/key-value-stores/record)

    #### Dataset

    * `/v2/acts/{actorId}/runs/last/dataset/items{?token,status}` [Item
    collection](#/reference/datasets/item-collection)

    #### Request queue

    * `/v2/acts/{actorId}/runs/last/request-queue/requests{?token,status}` [Request
    collection](#/reference/request-queues/request-collection)
    * `/v2/acts/{actorId}/runs/last/request-queue/requests/{requestId}{?token,status}` [Request
    collection](#/reference/request-queues/request)
    * `/v2/acts/{actorId}/runs/last/request-queue/head{?token,status}` [Queue head](#/reference/request-
    queues/queue-head)

    For example, to download data from a dataset of the last succeeded Actor run in XML format,
    send HTTP GET request to the following URL:

    ```
    https://api.apify.com/v2/acts/{actorId}/runs/last/dataset/items?token={yourApiToken}&format=xml&stat
    us=SUCCEEDED
    ```

    In order to save new items to the dataset, send HTTP POST request with JSON payload to the same URL.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        status (str | Unset):  Example: SUCCEEDED.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        actor_id=actor_id,
status=status,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    actor_id: str,
    *,
    client: AuthenticatedClient | Client,
    status: str | Unset = UNSET,

) -> Response[Any]:
    """ Get last run

     This is not a single endpoint, but an entire group of endpoints that lets you to
    retrieve and manage the last run of given Actor or any of its default storages.
    All the endpoints require an authentication token.

    The endpoints accept the same HTTP methods and query parameters as
    the respective storage endpoints.
    The base path represents the last Actor run object is:

    `/v2/acts/{actorId}/runs/last{?token,status}`

    Using the `status` query parameter you can ensure to only get a run with a certain status
    (e.g. `status=SUCCEEDED`). The output of this endpoint and other query parameters
    are the same as in the [Run object](#/reference/actors/run-object) endpoint.

    In order to access the default storages of the last Actor run, i.e. log, key-value store, dataset
    and request queue,
    use the following endpoints:

    * `/v2/acts/{actorId}/runs/last/log{?token,status}`
    * `/v2/acts/{actorId}/runs/last/key-value-store{?token,status}`
    * `/v2/acts/{actorId}/runs/last/dataset{?token,status}`
    * `/v2/acts/{actorId}/runs/last/request-queue{?token,status}`

    These API endpoints have the same usage as the equivalent storage endpoints.
    For example,
    `/v2/acts/{actorId}/runs/last/key-value-store` has the same HTTP method and parameters as the
    [Key-value store object](#/reference/key-value-stores/store-object) endpoint.

    Additionally, each of the above API endpoints supports all sub-endpoints
    of the original one:

    #### Key-value store

    * `/v2/acts/{actorId}/runs/last/key-value-store/keys{?token,status}` [Key
    collection](#/reference/key-value-stores/key-collection)
    * `/v2/acts/{actorId}/runs/last/key-value-store/records/{recordKey}{?token,status}`
    [Record](#/reference/key-value-stores/record)

    #### Dataset

    * `/v2/acts/{actorId}/runs/last/dataset/items{?token,status}` [Item
    collection](#/reference/datasets/item-collection)

    #### Request queue

    * `/v2/acts/{actorId}/runs/last/request-queue/requests{?token,status}` [Request
    collection](#/reference/request-queues/request-collection)
    * `/v2/acts/{actorId}/runs/last/request-queue/requests/{requestId}{?token,status}` [Request
    collection](#/reference/request-queues/request)
    * `/v2/acts/{actorId}/runs/last/request-queue/head{?token,status}` [Queue head](#/reference/request-
    queues/queue-head)

    For example, to download data from a dataset of the last succeeded Actor run in XML format,
    send HTTP GET request to the following URL:

    ```
    https://api.apify.com/v2/acts/{actorId}/runs/last/dataset/items?token={yourApiToken}&format=xml&stat
    us=SUCCEEDED
    ```

    In order to save new items to the dataset, send HTTP POST request with JSON payload to the same URL.

    Args:
        actor_id (str):  Example: janedoe~my-actor.
        status (str | Unset):  Example: SUCCEEDED.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        actor_id=actor_id,
status=status,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)


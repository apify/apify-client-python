from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.actor_task_run_sync_get_dataset_items_get_response_201 import ActorTaskRunSyncGetDatasetItemsGetResponse201
from ...models.error_response import ErrorResponse
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    actor_task_id: str,
    *,
    timeout: float | Unset = UNSET,
    memory: float | Unset = UNSET,
    max_items: float | Unset = UNSET,
    build: str | Unset = UNSET,
    webhooks: str | Unset = UNSET,
    format_: str | Unset = UNSET,
    clean: bool | Unset = UNSET,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    fields: str | Unset = UNSET,
    omit: str | Unset = UNSET,
    unwind: str | Unset = UNSET,
    flatten: str | Unset = UNSET,
    desc: bool | Unset = UNSET,
    attachment: bool | Unset = UNSET,
    delimiter: str | Unset = UNSET,
    bom: bool | Unset = UNSET,
    xml_root: str | Unset = UNSET,
    xml_row: str | Unset = UNSET,
    skip_header_row: bool | Unset = UNSET,
    skip_hidden: bool | Unset = UNSET,
    skip_empty: bool | Unset = UNSET,
    simplified: bool | Unset = UNSET,
    skip_failed_pages: bool | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["timeout"] = timeout

    params["memory"] = memory

    params["maxItems"] = max_items

    params["build"] = build

    params["webhooks"] = webhooks

    params["format"] = format_

    params["clean"] = clean

    params["offset"] = offset

    params["limit"] = limit

    params["fields"] = fields

    params["omit"] = omit

    params["unwind"] = unwind

    params["flatten"] = flatten

    params["desc"] = desc

    params["attachment"] = attachment

    params["delimiter"] = delimiter

    params["bom"] = bom

    params["xmlRoot"] = xml_root

    params["xmlRow"] = xml_row

    params["skipHeaderRow"] = skip_header_row

    params["skipHidden"] = skip_hidden

    params["skipEmpty"] = skip_empty

    params["simplified"] = simplified

    params["skipFailedPages"] = skip_failed_pages


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/actor-tasks/{actor_task_id}/run-sync-get-dataset-items".format(actor_task_id=actor_task_id,),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ActorTaskRunSyncGetDatasetItemsGetResponse201 | ErrorResponse | None:
    if response.status_code == 201:
        response_201 = ActorTaskRunSyncGetDatasetItemsGetResponse201.from_dict(response.json())



        return response_201

    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())



        return response_400

    if response.status_code == 408:
        response_408 = ErrorResponse.from_dict(response.json())



        return response_408

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ActorTaskRunSyncGetDatasetItemsGetResponse201 | ErrorResponse]:
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
    timeout: float | Unset = UNSET,
    memory: float | Unset = UNSET,
    max_items: float | Unset = UNSET,
    build: str | Unset = UNSET,
    webhooks: str | Unset = UNSET,
    format_: str | Unset = UNSET,
    clean: bool | Unset = UNSET,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    fields: str | Unset = UNSET,
    omit: str | Unset = UNSET,
    unwind: str | Unset = UNSET,
    flatten: str | Unset = UNSET,
    desc: bool | Unset = UNSET,
    attachment: bool | Unset = UNSET,
    delimiter: str | Unset = UNSET,
    bom: bool | Unset = UNSET,
    xml_root: str | Unset = UNSET,
    xml_row: str | Unset = UNSET,
    skip_header_row: bool | Unset = UNSET,
    skip_hidden: bool | Unset = UNSET,
    skip_empty: bool | Unset = UNSET,
    simplified: bool | Unset = UNSET,
    skip_failed_pages: bool | Unset = UNSET,

) -> Response[ActorTaskRunSyncGetDatasetItemsGetResponse201 | ErrorResponse]:
    """ Run task synchronously and get dataset items

     Run a specific task and return its dataset items.

    The run must finish in 300<!-- MAX_ACTOR_JOB_SYNC_WAIT_SECS --> seconds
    otherwise the HTTP request fails with a timeout error (this won't abort
    the run itself).

    You can send all the same options in parameters as the [Get Dataset
    Items](#/reference/datasets/item-collection/get-items) API endpoint.

    Beware that it might be impossible to maintain an idle HTTP connection for
    an extended period, due to client timeout or network conditions. Make sure your HTTP client is
    configured to have a long enough connection timeout.

    If the connection breaks, you will not receive any information about the run
    and its status.

    To run the Task asynchronously, use the [Run task
    asynchronously](#/reference/actor-tasks/run-collection/run-task) endpoint
    instead.

    Args:
        actor_task_id (str):  Example: janedoe~my-task.
        timeout (float | Unset):  Example: 60.
        memory (float | Unset):  Example: 256.
        max_items (float | Unset):  Example: 1000.
        build (str | Unset):  Example: 0.1.234.
        webhooks (str | Unset):  Example: dGhpcyBpcyBqdXN0IGV4YW1wbGUK....
        format_ (str | Unset):  Example: json.
        clean (bool | Unset):
        offset (float | Unset):
        limit (float | Unset):  Example: 99.
        fields (str | Unset):  Example: myValue,myOtherValue.
        omit (str | Unset):  Example: myValue,myOtherValue.
        unwind (str | Unset):  Example: myValue,myOtherValue.
        flatten (str | Unset):  Example: myValue.
        desc (bool | Unset):  Example: True.
        attachment (bool | Unset):  Example: True.
        delimiter (str | Unset):  Example: ;.
        bom (bool | Unset):
        xml_root (str | Unset):  Example: items.
        xml_row (str | Unset):  Example: item.
        skip_header_row (bool | Unset):  Example: True.
        skip_hidden (bool | Unset):
        skip_empty (bool | Unset):
        simplified (bool | Unset):
        skip_failed_pages (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActorTaskRunSyncGetDatasetItemsGetResponse201 | ErrorResponse]
     """


    kwargs = _get_kwargs(
        actor_task_id=actor_task_id,
timeout=timeout,
memory=memory,
max_items=max_items,
build=build,
webhooks=webhooks,
format_=format_,
clean=clean,
offset=offset,
limit=limit,
fields=fields,
omit=omit,
unwind=unwind,
flatten=flatten,
desc=desc,
attachment=attachment,
delimiter=delimiter,
bom=bom,
xml_root=xml_root,
xml_row=xml_row,
skip_header_row=skip_header_row,
skip_hidden=skip_hidden,
skip_empty=skip_empty,
simplified=simplified,
skip_failed_pages=skip_failed_pages,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    actor_task_id: str,
    *,
    client: AuthenticatedClient | Client,
    timeout: float | Unset = UNSET,
    memory: float | Unset = UNSET,
    max_items: float | Unset = UNSET,
    build: str | Unset = UNSET,
    webhooks: str | Unset = UNSET,
    format_: str | Unset = UNSET,
    clean: bool | Unset = UNSET,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    fields: str | Unset = UNSET,
    omit: str | Unset = UNSET,
    unwind: str | Unset = UNSET,
    flatten: str | Unset = UNSET,
    desc: bool | Unset = UNSET,
    attachment: bool | Unset = UNSET,
    delimiter: str | Unset = UNSET,
    bom: bool | Unset = UNSET,
    xml_root: str | Unset = UNSET,
    xml_row: str | Unset = UNSET,
    skip_header_row: bool | Unset = UNSET,
    skip_hidden: bool | Unset = UNSET,
    skip_empty: bool | Unset = UNSET,
    simplified: bool | Unset = UNSET,
    skip_failed_pages: bool | Unset = UNSET,

) -> ActorTaskRunSyncGetDatasetItemsGetResponse201 | ErrorResponse | None:
    """ Run task synchronously and get dataset items

     Run a specific task and return its dataset items.

    The run must finish in 300<!-- MAX_ACTOR_JOB_SYNC_WAIT_SECS --> seconds
    otherwise the HTTP request fails with a timeout error (this won't abort
    the run itself).

    You can send all the same options in parameters as the [Get Dataset
    Items](#/reference/datasets/item-collection/get-items) API endpoint.

    Beware that it might be impossible to maintain an idle HTTP connection for
    an extended period, due to client timeout or network conditions. Make sure your HTTP client is
    configured to have a long enough connection timeout.

    If the connection breaks, you will not receive any information about the run
    and its status.

    To run the Task asynchronously, use the [Run task
    asynchronously](#/reference/actor-tasks/run-collection/run-task) endpoint
    instead.

    Args:
        actor_task_id (str):  Example: janedoe~my-task.
        timeout (float | Unset):  Example: 60.
        memory (float | Unset):  Example: 256.
        max_items (float | Unset):  Example: 1000.
        build (str | Unset):  Example: 0.1.234.
        webhooks (str | Unset):  Example: dGhpcyBpcyBqdXN0IGV4YW1wbGUK....
        format_ (str | Unset):  Example: json.
        clean (bool | Unset):
        offset (float | Unset):
        limit (float | Unset):  Example: 99.
        fields (str | Unset):  Example: myValue,myOtherValue.
        omit (str | Unset):  Example: myValue,myOtherValue.
        unwind (str | Unset):  Example: myValue,myOtherValue.
        flatten (str | Unset):  Example: myValue.
        desc (bool | Unset):  Example: True.
        attachment (bool | Unset):  Example: True.
        delimiter (str | Unset):  Example: ;.
        bom (bool | Unset):
        xml_root (str | Unset):  Example: items.
        xml_row (str | Unset):  Example: item.
        skip_header_row (bool | Unset):  Example: True.
        skip_hidden (bool | Unset):
        skip_empty (bool | Unset):
        simplified (bool | Unset):
        skip_failed_pages (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ActorTaskRunSyncGetDatasetItemsGetResponse201 | ErrorResponse
     """


    return sync_detailed(
        actor_task_id=actor_task_id,
client=client,
timeout=timeout,
memory=memory,
max_items=max_items,
build=build,
webhooks=webhooks,
format_=format_,
clean=clean,
offset=offset,
limit=limit,
fields=fields,
omit=omit,
unwind=unwind,
flatten=flatten,
desc=desc,
attachment=attachment,
delimiter=delimiter,
bom=bom,
xml_root=xml_root,
xml_row=xml_row,
skip_header_row=skip_header_row,
skip_hidden=skip_hidden,
skip_empty=skip_empty,
simplified=simplified,
skip_failed_pages=skip_failed_pages,

    ).parsed

async def asyncio_detailed(
    actor_task_id: str,
    *,
    client: AuthenticatedClient | Client,
    timeout: float | Unset = UNSET,
    memory: float | Unset = UNSET,
    max_items: float | Unset = UNSET,
    build: str | Unset = UNSET,
    webhooks: str | Unset = UNSET,
    format_: str | Unset = UNSET,
    clean: bool | Unset = UNSET,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    fields: str | Unset = UNSET,
    omit: str | Unset = UNSET,
    unwind: str | Unset = UNSET,
    flatten: str | Unset = UNSET,
    desc: bool | Unset = UNSET,
    attachment: bool | Unset = UNSET,
    delimiter: str | Unset = UNSET,
    bom: bool | Unset = UNSET,
    xml_root: str | Unset = UNSET,
    xml_row: str | Unset = UNSET,
    skip_header_row: bool | Unset = UNSET,
    skip_hidden: bool | Unset = UNSET,
    skip_empty: bool | Unset = UNSET,
    simplified: bool | Unset = UNSET,
    skip_failed_pages: bool | Unset = UNSET,

) -> Response[ActorTaskRunSyncGetDatasetItemsGetResponse201 | ErrorResponse]:
    """ Run task synchronously and get dataset items

     Run a specific task and return its dataset items.

    The run must finish in 300<!-- MAX_ACTOR_JOB_SYNC_WAIT_SECS --> seconds
    otherwise the HTTP request fails with a timeout error (this won't abort
    the run itself).

    You can send all the same options in parameters as the [Get Dataset
    Items](#/reference/datasets/item-collection/get-items) API endpoint.

    Beware that it might be impossible to maintain an idle HTTP connection for
    an extended period, due to client timeout or network conditions. Make sure your HTTP client is
    configured to have a long enough connection timeout.

    If the connection breaks, you will not receive any information about the run
    and its status.

    To run the Task asynchronously, use the [Run task
    asynchronously](#/reference/actor-tasks/run-collection/run-task) endpoint
    instead.

    Args:
        actor_task_id (str):  Example: janedoe~my-task.
        timeout (float | Unset):  Example: 60.
        memory (float | Unset):  Example: 256.
        max_items (float | Unset):  Example: 1000.
        build (str | Unset):  Example: 0.1.234.
        webhooks (str | Unset):  Example: dGhpcyBpcyBqdXN0IGV4YW1wbGUK....
        format_ (str | Unset):  Example: json.
        clean (bool | Unset):
        offset (float | Unset):
        limit (float | Unset):  Example: 99.
        fields (str | Unset):  Example: myValue,myOtherValue.
        omit (str | Unset):  Example: myValue,myOtherValue.
        unwind (str | Unset):  Example: myValue,myOtherValue.
        flatten (str | Unset):  Example: myValue.
        desc (bool | Unset):  Example: True.
        attachment (bool | Unset):  Example: True.
        delimiter (str | Unset):  Example: ;.
        bom (bool | Unset):
        xml_root (str | Unset):  Example: items.
        xml_row (str | Unset):  Example: item.
        skip_header_row (bool | Unset):  Example: True.
        skip_hidden (bool | Unset):
        skip_empty (bool | Unset):
        simplified (bool | Unset):
        skip_failed_pages (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActorTaskRunSyncGetDatasetItemsGetResponse201 | ErrorResponse]
     """


    kwargs = _get_kwargs(
        actor_task_id=actor_task_id,
timeout=timeout,
memory=memory,
max_items=max_items,
build=build,
webhooks=webhooks,
format_=format_,
clean=clean,
offset=offset,
limit=limit,
fields=fields,
omit=omit,
unwind=unwind,
flatten=flatten,
desc=desc,
attachment=attachment,
delimiter=delimiter,
bom=bom,
xml_root=xml_root,
xml_row=xml_row,
skip_header_row=skip_header_row,
skip_hidden=skip_hidden,
skip_empty=skip_empty,
simplified=simplified,
skip_failed_pages=skip_failed_pages,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    actor_task_id: str,
    *,
    client: AuthenticatedClient | Client,
    timeout: float | Unset = UNSET,
    memory: float | Unset = UNSET,
    max_items: float | Unset = UNSET,
    build: str | Unset = UNSET,
    webhooks: str | Unset = UNSET,
    format_: str | Unset = UNSET,
    clean: bool | Unset = UNSET,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    fields: str | Unset = UNSET,
    omit: str | Unset = UNSET,
    unwind: str | Unset = UNSET,
    flatten: str | Unset = UNSET,
    desc: bool | Unset = UNSET,
    attachment: bool | Unset = UNSET,
    delimiter: str | Unset = UNSET,
    bom: bool | Unset = UNSET,
    xml_root: str | Unset = UNSET,
    xml_row: str | Unset = UNSET,
    skip_header_row: bool | Unset = UNSET,
    skip_hidden: bool | Unset = UNSET,
    skip_empty: bool | Unset = UNSET,
    simplified: bool | Unset = UNSET,
    skip_failed_pages: bool | Unset = UNSET,

) -> ActorTaskRunSyncGetDatasetItemsGetResponse201 | ErrorResponse | None:
    """ Run task synchronously and get dataset items

     Run a specific task and return its dataset items.

    The run must finish in 300<!-- MAX_ACTOR_JOB_SYNC_WAIT_SECS --> seconds
    otherwise the HTTP request fails with a timeout error (this won't abort
    the run itself).

    You can send all the same options in parameters as the [Get Dataset
    Items](#/reference/datasets/item-collection/get-items) API endpoint.

    Beware that it might be impossible to maintain an idle HTTP connection for
    an extended period, due to client timeout or network conditions. Make sure your HTTP client is
    configured to have a long enough connection timeout.

    If the connection breaks, you will not receive any information about the run
    and its status.

    To run the Task asynchronously, use the [Run task
    asynchronously](#/reference/actor-tasks/run-collection/run-task) endpoint
    instead.

    Args:
        actor_task_id (str):  Example: janedoe~my-task.
        timeout (float | Unset):  Example: 60.
        memory (float | Unset):  Example: 256.
        max_items (float | Unset):  Example: 1000.
        build (str | Unset):  Example: 0.1.234.
        webhooks (str | Unset):  Example: dGhpcyBpcyBqdXN0IGV4YW1wbGUK....
        format_ (str | Unset):  Example: json.
        clean (bool | Unset):
        offset (float | Unset):
        limit (float | Unset):  Example: 99.
        fields (str | Unset):  Example: myValue,myOtherValue.
        omit (str | Unset):  Example: myValue,myOtherValue.
        unwind (str | Unset):  Example: myValue,myOtherValue.
        flatten (str | Unset):  Example: myValue.
        desc (bool | Unset):  Example: True.
        attachment (bool | Unset):  Example: True.
        delimiter (str | Unset):  Example: ;.
        bom (bool | Unset):
        xml_root (str | Unset):  Example: items.
        xml_row (str | Unset):  Example: item.
        skip_header_row (bool | Unset):  Example: True.
        skip_hidden (bool | Unset):
        skip_empty (bool | Unset):
        simplified (bool | Unset):
        skip_failed_pages (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ActorTaskRunSyncGetDatasetItemsGetResponse201 | ErrorResponse
     """


    return (await asyncio_detailed(
        actor_task_id=actor_task_id,
client=client,
timeout=timeout,
memory=memory,
max_items=max_items,
build=build,
webhooks=webhooks,
format_=format_,
clean=clean,
offset=offset,
limit=limit,
fields=fields,
omit=omit,
unwind=unwind,
flatten=flatten,
desc=desc,
attachment=attachment,
delimiter=delimiter,
bom=bom,
xml_root=xml_root,
xml_row=xml_row,
skip_header_row=skip_header_row,
skip_hidden=skip_hidden,
skip_empty=skip_empty,
simplified=simplified,
skip_failed_pages=skip_failed_pages,

    )).parsed

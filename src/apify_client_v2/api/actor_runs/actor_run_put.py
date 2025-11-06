from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.actor_run_put_body import ActorRunPutBody
from typing import cast



def _get_kwargs(
    run_id: str,
    *,
    body: ActorRunPutBody,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v2/actor-runs/{run_id}".format(run_id=run_id,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
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
    body: ActorRunPutBody,

) -> Response[Any]:
    """ Update status message

     You can set a single status message on your run that will be displayed in
    the Apify Console UI. During an Actor run, you will typically do this in order
    to inform users of your Actor about the Actor's progress.

    The request body must contain `runId` and `statusMessage` properties. The
    `isStatusMessageTerminal` property is optional and it indicates if the
    status message is the very last one. In the absence of a status message, the
    platform will try to substitute sensible defaults.

    Args:
        run_id (str):  Example: 3KH8gEpp4d8uQSe8T.
        body (ActorRunPutBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        run_id=run_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    run_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ActorRunPutBody,

) -> Response[Any]:
    """ Update status message

     You can set a single status message on your run that will be displayed in
    the Apify Console UI. During an Actor run, you will typically do this in order
    to inform users of your Actor about the Actor's progress.

    The request body must contain `runId` and `statusMessage` properties. The
    `isStatusMessageTerminal` property is optional and it indicates if the
    status message is the very last one. In the absence of a status message, the
    platform will try to substitute sensible defaults.

    Args:
        run_id (str):  Example: 3KH8gEpp4d8uQSe8T.
        body (ActorRunPutBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        run_id=run_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)


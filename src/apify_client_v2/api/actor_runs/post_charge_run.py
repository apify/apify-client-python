from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.charge_run_request import ChargeRunRequest
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    run_id: str,
    *,
    body: ChargeRunRequest,
    idempotency_key: str | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(idempotency_key, Unset):
        headers["idempotency-key"] = idempotency_key



    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v2/actor-runs/{run_id}/charge".format(run_id=run_id,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | None:
    if response.status_code == 201:
        return None

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
    body: ChargeRunRequest,
    idempotency_key: str | Unset = UNSET,

) -> Response[Any]:
    """ Charge events in run

     Charge for events in the run of your [pay per event
    Actor](https://docs.apify.com/platform/actors/running/actors-in-store#pay-per-event).
    The event you are charging for must be one of the configured events in your Actor. If the Actor is
    not set up as pay per event, or if the event is not configured,
    the endpoint will return an error. The endpoint must be called from the Actor run itself, with the
    same API token that the run was started with.

    :::info Learn more about pay-per-event pricing

    For more details about pay-per-event (PPE) pricing, refer to our [PPE
    documentation](/platform/actors/publishing/monetize/pay-per-event).

    :::

    Args:
        run_id (str):
        idempotency_key (str | Unset):
        body (ChargeRunRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        run_id=run_id,
body=body,
idempotency_key=idempotency_key,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    run_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ChargeRunRequest,
    idempotency_key: str | Unset = UNSET,

) -> Response[Any]:
    """ Charge events in run

     Charge for events in the run of your [pay per event
    Actor](https://docs.apify.com/platform/actors/running/actors-in-store#pay-per-event).
    The event you are charging for must be one of the configured events in your Actor. If the Actor is
    not set up as pay per event, or if the event is not configured,
    the endpoint will return an error. The endpoint must be called from the Actor run itself, with the
    same API token that the run was started with.

    :::info Learn more about pay-per-event pricing

    For more details about pay-per-event (PPE) pricing, refer to our [PPE
    documentation](/platform/actors/publishing/monetize/pay-per-event).

    :::

    Args:
        run_id (str):
        idempotency_key (str | Unset):
        body (ChargeRunRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        run_id=run_id,
body=body,
idempotency_key=idempotency_key,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)


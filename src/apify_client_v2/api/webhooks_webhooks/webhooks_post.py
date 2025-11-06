from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.create_webhook_response import CreateWebhookResponse
from ...models.webhook_create import WebhookCreate
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    *,
    body: WebhookCreate,
    limit: str | Unset = UNSET,
    offset: str | Unset = UNSET,
    desc: str | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    params: dict[str, Any] = {}

    params["limit"] = limit

    params["offset"] = offset

    params["desc"] = desc


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v2/webhooks",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> CreateWebhookResponse | None:
    if response.status_code == 201:
        response_201 = CreateWebhookResponse.from_dict(response.json())



        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[CreateWebhookResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: WebhookCreate,
    limit: str | Unset = UNSET,
    offset: str | Unset = UNSET,
    desc: str | Unset = UNSET,

) -> Response[CreateWebhookResponse]:
    r""" Create webhook

     Creates a new webhook with settings provided by the webhook object passed as
    JSON in the payload.
    The response is the created webhook object.

    To avoid duplicating a webhook, use the `idempotencyKey` parameter in the
    request body.
    Multiple calls to create a webhook with the same `idempotencyKey` will only
    create the webhook with the first call and return the existing webhook on
    subsequent calls.
    Idempotency keys must be unique, so use a UUID or another random string with
    enough entropy.

    To assign the new webhook to an Actor or task, the request body must contain
    `requestUrl`, `eventTypes`, and `condition` properties.

    * `requestUrl` is the webhook's target URL, to which data is sent as a POST
    request with a JSON payload.
    * `eventTypes` is a list of events that will trigger the webhook, e.g. when
    the Actor run succeeds.
    * `condition` should be an object containing the ID of the Actor or task to
    which the webhook will be assigned.
    * `payloadTemplate` is a JSON-like string, whose syntax is extended with the
    use of variables.
    * `headersTemplate` is a JSON-like string, whose syntax is extended with the
    use of variables. Following values will be re-written to defaults: \"host\",
    \"Content-Type\", \"X-Apify-Webhook\", \"X-Apify-Webhook-Dispatch-Id\",
    \"X-Apify-Request-Origin\"
    * `description` is an optional string.
    * `shouldInterpolateStrings` is a boolean indicating whether to interpolate
    variables contained inside strings in the `payloadTemplate`

    ```
        \"isAdHoc\" : false,
        \"requestUrl\" : \"https://example.com\",
        \"eventTypes\" : [
            \"ACTOR.RUN.SUCCEEDED\",
            \"ACTOR.RUN.ABORTED\"
        ],
        \"condition\" : {
            \"actorId\": \"janedoe~my-actor\",
            \"actorTaskId\" : \"W9bs9JE9v7wprjAnJ\"
        },
        \"payloadTemplate\": \"\",
        \"headersTemplate\": \"\",
        \"description\": \"my awesome webhook\",
        \"shouldInterpolateStrings\": false,
    ```

    **Important**: The request must specify the `Content-Type: application/json`
    HTTP header.

    Args:
        limit (str | Unset):
        offset (str | Unset):
        desc (str | Unset):
        body (WebhookCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateWebhookResponse]
     """


    kwargs = _get_kwargs(
        body=body,
limit=limit,
offset=offset,
desc=desc,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient | Client,
    body: WebhookCreate,
    limit: str | Unset = UNSET,
    offset: str | Unset = UNSET,
    desc: str | Unset = UNSET,

) -> CreateWebhookResponse | None:
    r""" Create webhook

     Creates a new webhook with settings provided by the webhook object passed as
    JSON in the payload.
    The response is the created webhook object.

    To avoid duplicating a webhook, use the `idempotencyKey` parameter in the
    request body.
    Multiple calls to create a webhook with the same `idempotencyKey` will only
    create the webhook with the first call and return the existing webhook on
    subsequent calls.
    Idempotency keys must be unique, so use a UUID or another random string with
    enough entropy.

    To assign the new webhook to an Actor or task, the request body must contain
    `requestUrl`, `eventTypes`, and `condition` properties.

    * `requestUrl` is the webhook's target URL, to which data is sent as a POST
    request with a JSON payload.
    * `eventTypes` is a list of events that will trigger the webhook, e.g. when
    the Actor run succeeds.
    * `condition` should be an object containing the ID of the Actor or task to
    which the webhook will be assigned.
    * `payloadTemplate` is a JSON-like string, whose syntax is extended with the
    use of variables.
    * `headersTemplate` is a JSON-like string, whose syntax is extended with the
    use of variables. Following values will be re-written to defaults: \"host\",
    \"Content-Type\", \"X-Apify-Webhook\", \"X-Apify-Webhook-Dispatch-Id\",
    \"X-Apify-Request-Origin\"
    * `description` is an optional string.
    * `shouldInterpolateStrings` is a boolean indicating whether to interpolate
    variables contained inside strings in the `payloadTemplate`

    ```
        \"isAdHoc\" : false,
        \"requestUrl\" : \"https://example.com\",
        \"eventTypes\" : [
            \"ACTOR.RUN.SUCCEEDED\",
            \"ACTOR.RUN.ABORTED\"
        ],
        \"condition\" : {
            \"actorId\": \"janedoe~my-actor\",
            \"actorTaskId\" : \"W9bs9JE9v7wprjAnJ\"
        },
        \"payloadTemplate\": \"\",
        \"headersTemplate\": \"\",
        \"description\": \"my awesome webhook\",
        \"shouldInterpolateStrings\": false,
    ```

    **Important**: The request must specify the `Content-Type: application/json`
    HTTP header.

    Args:
        limit (str | Unset):
        offset (str | Unset):
        desc (str | Unset):
        body (WebhookCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateWebhookResponse
     """


    return sync_detailed(
        client=client,
body=body,
limit=limit,
offset=offset,
desc=desc,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: WebhookCreate,
    limit: str | Unset = UNSET,
    offset: str | Unset = UNSET,
    desc: str | Unset = UNSET,

) -> Response[CreateWebhookResponse]:
    r""" Create webhook

     Creates a new webhook with settings provided by the webhook object passed as
    JSON in the payload.
    The response is the created webhook object.

    To avoid duplicating a webhook, use the `idempotencyKey` parameter in the
    request body.
    Multiple calls to create a webhook with the same `idempotencyKey` will only
    create the webhook with the first call and return the existing webhook on
    subsequent calls.
    Idempotency keys must be unique, so use a UUID or another random string with
    enough entropy.

    To assign the new webhook to an Actor or task, the request body must contain
    `requestUrl`, `eventTypes`, and `condition` properties.

    * `requestUrl` is the webhook's target URL, to which data is sent as a POST
    request with a JSON payload.
    * `eventTypes` is a list of events that will trigger the webhook, e.g. when
    the Actor run succeeds.
    * `condition` should be an object containing the ID of the Actor or task to
    which the webhook will be assigned.
    * `payloadTemplate` is a JSON-like string, whose syntax is extended with the
    use of variables.
    * `headersTemplate` is a JSON-like string, whose syntax is extended with the
    use of variables. Following values will be re-written to defaults: \"host\",
    \"Content-Type\", \"X-Apify-Webhook\", \"X-Apify-Webhook-Dispatch-Id\",
    \"X-Apify-Request-Origin\"
    * `description` is an optional string.
    * `shouldInterpolateStrings` is a boolean indicating whether to interpolate
    variables contained inside strings in the `payloadTemplate`

    ```
        \"isAdHoc\" : false,
        \"requestUrl\" : \"https://example.com\",
        \"eventTypes\" : [
            \"ACTOR.RUN.SUCCEEDED\",
            \"ACTOR.RUN.ABORTED\"
        ],
        \"condition\" : {
            \"actorId\": \"janedoe~my-actor\",
            \"actorTaskId\" : \"W9bs9JE9v7wprjAnJ\"
        },
        \"payloadTemplate\": \"\",
        \"headersTemplate\": \"\",
        \"description\": \"my awesome webhook\",
        \"shouldInterpolateStrings\": false,
    ```

    **Important**: The request must specify the `Content-Type: application/json`
    HTTP header.

    Args:
        limit (str | Unset):
        offset (str | Unset):
        desc (str | Unset):
        body (WebhookCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateWebhookResponse]
     """


    kwargs = _get_kwargs(
        body=body,
limit=limit,
offset=offset,
desc=desc,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: WebhookCreate,
    limit: str | Unset = UNSET,
    offset: str | Unset = UNSET,
    desc: str | Unset = UNSET,

) -> CreateWebhookResponse | None:
    r""" Create webhook

     Creates a new webhook with settings provided by the webhook object passed as
    JSON in the payload.
    The response is the created webhook object.

    To avoid duplicating a webhook, use the `idempotencyKey` parameter in the
    request body.
    Multiple calls to create a webhook with the same `idempotencyKey` will only
    create the webhook with the first call and return the existing webhook on
    subsequent calls.
    Idempotency keys must be unique, so use a UUID or another random string with
    enough entropy.

    To assign the new webhook to an Actor or task, the request body must contain
    `requestUrl`, `eventTypes`, and `condition` properties.

    * `requestUrl` is the webhook's target URL, to which data is sent as a POST
    request with a JSON payload.
    * `eventTypes` is a list of events that will trigger the webhook, e.g. when
    the Actor run succeeds.
    * `condition` should be an object containing the ID of the Actor or task to
    which the webhook will be assigned.
    * `payloadTemplate` is a JSON-like string, whose syntax is extended with the
    use of variables.
    * `headersTemplate` is a JSON-like string, whose syntax is extended with the
    use of variables. Following values will be re-written to defaults: \"host\",
    \"Content-Type\", \"X-Apify-Webhook\", \"X-Apify-Webhook-Dispatch-Id\",
    \"X-Apify-Request-Origin\"
    * `description` is an optional string.
    * `shouldInterpolateStrings` is a boolean indicating whether to interpolate
    variables contained inside strings in the `payloadTemplate`

    ```
        \"isAdHoc\" : false,
        \"requestUrl\" : \"https://example.com\",
        \"eventTypes\" : [
            \"ACTOR.RUN.SUCCEEDED\",
            \"ACTOR.RUN.ABORTED\"
        ],
        \"condition\" : {
            \"actorId\": \"janedoe~my-actor\",
            \"actorTaskId\" : \"W9bs9JE9v7wprjAnJ\"
        },
        \"payloadTemplate\": \"\",
        \"headersTemplate\": \"\",
        \"description\": \"my awesome webhook\",
        \"shouldInterpolateStrings\": false,
    ```

    **Important**: The request must specify the `Content-Type: application/json`
    HTTP header.

    Args:
        limit (str | Unset):
        offset (str | Unset):
        desc (str | Unset):
        body (WebhookCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateWebhookResponse
     """


    return (await asyncio_detailed(
        client=client,
body=body,
limit=limit,
offset=offset,
desc=desc,

    )).parsed

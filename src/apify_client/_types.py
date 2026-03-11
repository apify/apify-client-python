from __future__ import annotations

import json
from base64 import b64encode
from datetime import timedelta
from typing import Annotated, Any, Literal

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, RootModel, model_validator

from apify_client._models import ActorJobStatus, WebhookCreate  # noqa: TC001

Timeout = timedelta | Literal['no_timeout', 'short', 'medium', 'long']
"""Type for the `timeout` parameter on resource client methods.

`'short'`, `'medium'`, and `'long'` are tier literals resolved by the HTTP client to configured values.
A `timedelta` overrides the timeout for this call, and `'no_timeout'` disables the timeout entirely.
"""

JsonSerializable = str | int | float | bool | None | dict[str, Any] | list[Any]
"""Type for representing json-serializable values. It's close enough to the real thing supported by json.parse.
It was suggested in a discussion with (and approved by) Guido van Rossum, so I'd consider it correct enough.
"""


class ActorJob(BaseModel):
    """Minimal model for an Actor job (run or build) with status.

    Used for validation during polling operations. Allows extra fields so the full response data is preserved.
    """

    model_config = ConfigDict(extra='allow', populate_by_name=True)

    status: ActorJobStatus


class ActorJobResponse(BaseModel):
    """Response wrapper for an Actor job (run or build).

    Used for minimal validation during polling operations. Allows extra fields so the full response data is preserved.
    """

    model_config = ConfigDict(extra='allow', populate_by_name=True)

    data: ActorJob


class WebhookRepresentation(BaseModel):
    """Representation of a webhook for base64-encoded API transmission.

    Contains only the fields needed for the webhook payload sent via query parameters.
    """

    model_config = ConfigDict(populate_by_name=True, extra='ignore')

    event_types: Annotated[list[str], Field(alias='eventTypes')]
    request_url: Annotated[str, Field(alias='requestUrl')]
    payload_template: Annotated[str | None, Field(alias='payloadTemplate')] = None
    headers_template: Annotated[str | None, Field(alias='headersTemplate')] = None


class WebhookRepresentationList(RootModel[list[WebhookRepresentation]]):
    """List of webhook representations with base64 encoding support."""

    @classmethod
    def from_webhooks(cls, webhooks: list[dict | WebhookCreate]) -> WebhookRepresentationList:
        """Construct from a list of `WebhookCreate` models or plain dicts.

        Dicts are validated directly as `WebhookRepresentation`, so only the minimal ad-hoc webhook fields
        (`event_types`, `request_url`, and optionally `payload_template`/`headers_template`) are required.
        """
        representations = list[WebhookRepresentation]()

        for webhook in webhooks:
            if isinstance(webhook, dict):
                representations.append(WebhookRepresentation.model_validate(webhook))
            else:
                webhook_dict = webhook.model_dump(mode='json', exclude_none=True)
                representations.append(WebhookRepresentation.model_validate(webhook_dict))

        return cls(representations)

    def to_base64(self) -> str | None:
        """Encode this list of webhook representations to a base64 string.

        Returns `None` if the list is empty, so that the query parameter is omitted.
        """
        if not self.root:
            return None

        data = [r.model_dump(by_alias=True, exclude_none=True) for r in self.root]
        json_string = json.dumps(data).encode(encoding='utf-8')
        return b64encode(json_string).decode(encoding='ascii')


class RequestInput(BaseModel):
    """Input model for adding requests to a request queue.

    Both `url` and `unique_key` are required. The API defaults `method` to `GET` when not provided.
    """

    model_config = ConfigDict(
        extra='allow',
        populate_by_name=True,
    )

    id: Annotated[str | None, Field(examples=['sbJ7klsdf7ujN9l'])] = None
    """A unique identifier assigned to the request."""

    unique_key: Annotated[
        str,
        Field(alias='uniqueKey', examples=['GET|60d83e70|e3b0c442|https://apify.com']),
    ]
    """A unique key used for request de-duplication."""

    url: Annotated[AnyUrl, Field(examples=['https://apify.com'])]
    """The URL of the request."""

    method: Annotated[str | None, Field(examples=['GET'])] = None
    """The HTTP method of the request. Defaults to `GET` on the API side if not provided."""


class RequestDeleteInput(BaseModel):
    """Input model for deleting requests from a request queue.

    Requests are identified by `id` or `unique_key`. At least one must be provided.
    """

    model_config = ConfigDict(
        extra='allow',
        populate_by_name=True,
    )

    id: Annotated[str | None, Field(examples=['sbJ7klsdf7ujN9l'])] = None
    """A unique identifier assigned to the request."""

    unique_key: Annotated[
        str | None,
        Field(alias='uniqueKey', examples=['GET|60d83e70|e3b0c442|https://apify.com']),
    ] = None
    """A unique key used for request de-duplication."""

    @model_validator(mode='after')
    def _check_at_least_one_identifier(self) -> RequestDeleteInput:
        if self.id is None and self.unique_key is None:
            raise ValueError('At least one of `id` or `unique_key` must be provided')
        return self

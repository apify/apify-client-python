"""Hand-written Pydantic models for shapes not exposed by the OpenAPI spec or that need local logic.

Generated models live in `apify_client._models_generated`; import from there directly.
"""

from __future__ import annotations

import json
from base64 import b64encode
from typing import TYPE_CHECKING, Annotated

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, RootModel, model_validator

from apify_client._docs import docs_group
from apify_client._literals_generated import ActorJobStatus
from apify_client._models_generated import WebhookCreate

if TYPE_CHECKING:
    from apify_client._literals import WebhooksList


@docs_group('Models')
class ActorJob(BaseModel):
    """Minimal model for an Actor job (run or build) with status.

    Used for validation during polling operations. Allows extra fields so the full response data is preserved.
    """

    model_config = ConfigDict(extra='allow', populate_by_name=True)

    status: ActorJobStatus
    """The current status of the Actor job."""


@docs_group('Models')
class ActorJobResponse(BaseModel):
    """Response wrapper for an Actor job (run or build).

    Used for minimal validation during polling operations. Allows extra fields so the full response data is preserved.
    """

    model_config = ConfigDict(extra='allow', populate_by_name=True)

    data: ActorJob
    """The Actor job payload."""


@docs_group('Models')
class WebhookRepresentation(BaseModel):
    """Representation of a webhook for base64-encoded API transmission.

    Contains only the fields needed for the webhook payload sent via query parameters.
    """

    model_config = ConfigDict(populate_by_name=True, extra='ignore')

    event_types: Annotated[list[str], Field(alias='eventTypes')]
    """The list of Actor events that trigger this webhook."""

    request_url: Annotated[str, Field(alias='requestUrl')]
    """The URL to which the webhook sends its payload."""

    payload_template: Annotated[str | None, Field(alias='payloadTemplate')] = None
    """Optional template for the JSON payload sent by the webhook."""

    headers_template: Annotated[str | None, Field(alias='headersTemplate')] = None
    """Optional template for the HTTP headers sent by the webhook."""


@docs_group('Models')
class WebhookRepresentationList(RootModel[list[WebhookRepresentation]]):
    """List of webhook representations with base64 encoding support."""

    @classmethod
    def from_webhooks(cls, webhooks: WebhooksList) -> WebhookRepresentationList:
        """Construct from a list of webhooks.

        See `WebhooksList` for the accepted shapes. `WebhookRepresentation` instances are used as-is; all
        other shapes are validated into `WebhookRepresentation`, keeping only its fields and ignoring any
        extras (e.g. `condition`).
        """
        representations = list[WebhookRepresentation]()

        for webhook in webhooks:
            if isinstance(webhook, WebhookRepresentation):
                representations.append(webhook)
            elif isinstance(webhook, WebhookCreate):
                webhook_dict = webhook.model_dump(mode='json', exclude_none=True)
                webhook_representation = WebhookRepresentation.model_validate(webhook_dict)
                representations.append(webhook_representation)
            else:
                webhook_representation = WebhookRepresentation.model_validate(webhook)
                representations.append(webhook_representation)

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


@docs_group('Models')
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


@docs_group('Models')
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
        """Ensure at least one of `id` or `unique_key` is set."""
        if self.id is None and self.unique_key is None:
            raise ValueError('At least one of `id` or `unique_key` must be provided')
        return self

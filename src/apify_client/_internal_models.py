"""Internal Pydantic models that are not part of the public API and are therefore not generated."""

from __future__ import annotations

import json
from base64 import b64encode
from typing import Annotated, overload

from pydantic import BaseModel, ConfigDict, Field, RootModel

from apify_client._models import ActorJobStatus, WebhookCreate


class ActorJob(BaseModel):
    """Minimal model for an Actor job (run or build) with status.

    Used for validation during polling operations. Allows extra fields so the full response data is preserved.
    """

    model_config = ConfigDict(extra='allow')

    status: ActorJobStatus


class ActorJobResponse(BaseModel):
    """Response wrapper for an Actor job (run or build).

    Used for minimal validation during polling operations. Allows extra fields so the full response data is preserved.
    """

    model_config = ConfigDict(extra='allow')

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
        """Construct from a list of webhook dictionaries."""
        representations = []
        for webhook in webhooks:
            webhook_dict = webhook.model_dump(exclude_none=True) if isinstance(webhook, WebhookCreate) else webhook
            representations.append(WebhookRepresentation.model_validate(webhook_dict))
        return cls(representations)

    def to_base64(self) -> str:
        """Encode this list of webhook representations to a base64 string."""
        data = [r.model_dump(by_alias=True, exclude_none=True) for r in self.root]
        return b64encode(json.dumps(data).encode('utf-8')).decode('ascii')

    @overload
    @classmethod
    def encode_to_base64(cls, webhooks: None) -> None: ...

    @overload
    @classmethod
    def encode_to_base64(cls, webhooks: list[dict | WebhookCreate]) -> str: ...

    @classmethod
    def encode_to_base64(cls, webhooks: list[dict | WebhookCreate] | None) -> str | None:
        """Encode a list of webhooks to base64 for API transmission.

        Args:
            webhooks: A list of webhooks with keys like `event_types`, `request_url`, etc.
                If None, returns None.

        Returns:
            A base64-encoded JSON string, or None if webhooks is None.
        """
        if webhooks is None:
            return None
        return cls.from_webhooks(webhooks).to_base64()

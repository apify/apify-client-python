"""Hand-written TypedDicts for resource-client method inputs not exposed by the OpenAPI spec.

Generated TypedDicts live in `apify_client._typeddicts_generated`; import from there directly.
"""

from __future__ import annotations

from typing import NotRequired, TypedDict

from apify_client._docs import docs_group


@docs_group('Typed dicts')
class RequestInputDict(TypedDict):
    """TypedDict counterpart of `RequestInput` for adding requests to a request queue."""

    unique_key: str
    """A unique key used for request de-duplication."""

    url: str
    """The URL of the request."""

    id: NotRequired[str | None]
    """A unique identifier assigned to the request."""

    method: NotRequired[str | None]
    """The HTTP method of the request. Defaults to `GET` on the API side if not provided."""


@docs_group('Typed dicts')
class RequestDeleteInputDict(TypedDict):
    """TypedDict counterpart of `RequestDeleteInput` for deleting requests from a request queue.

    The TypedDict cannot enforce "at least one of id/unique_key" — that check still happens at the Pydantic-model
    level when dicts are validated at call time.
    """

    id: NotRequired[str | None]
    """A unique identifier assigned to the request."""

    unique_key: NotRequired[str | None]
    """A unique key used for request de-duplication."""


@docs_group('Typed dicts')
class WebhookRepresentationDict(TypedDict):
    """TypedDict counterpart of `WebhookRepresentation` for ad-hoc webhooks.

    Captures the minimal shape the Apify API actually requires when attaching ad-hoc webhooks to a run:
    only `event_types` and `request_url` are mandatory. Unlike `WebhookCreateDict`, there is no `condition`
    field — the API does not use it for ad-hoc webhooks.
    """

    event_types: list[str]
    """The list of Actor events that trigger this webhook."""

    request_url: str
    """The URL to which the webhook sends its payload."""

    payload_template: NotRequired[str | None]
    """Optional template for the JSON payload sent by the webhook."""

    headers_template: NotRequired[str | None]
    """Optional template for the HTTP headers sent by the webhook."""

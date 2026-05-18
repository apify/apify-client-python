from __future__ import annotations

from typing import Literal

from apify_client._models import WebhookCreate, WebhookRepresentation
from apify_client._typeddicts import (
    WebhookCreateCamelDict,
    WebhookCreateDict,
    WebhookRepresentationCamelDict,
    WebhookRepresentationDict,
)

WebhooksList = (
    list[WebhookCreate]
    | list[WebhookCreateDict]
    | list[WebhookCreateCamelDict]
    | list[WebhookRepresentation]
    | list[WebhookRepresentationDict]
    | list[WebhookRepresentationCamelDict]
)
"""Type for the `webhooks` parameter on resource-client `start`/`call` methods and `from_webhooks`.

`WebhookRepresentation` / `WebhookRepresentationDict` / `WebhookRepresentationCamelDict` are the minimal ad-hoc
webhook shape (only `event_types` and `request_url` required). `WebhookCreate` / `WebhookCreateDict` /
`WebhookCreateCamelDict` are accepted so a persistent-webhook definition can be reused; their fields not relevant
to ad-hoc webhooks (e.g. `condition`) are ignored at runtime. The `*CamelDict` variants accept camelCase keys
matching the Apify API spelling.
"""

TerminalActorJobStatus = Literal['SUCCEEDED', 'FAILED', 'TIMED-OUT', 'ABORTED']
"""Subset of `ActorJobStatus` values that indicate the job has finished and will not change again."""

JsonSerializable = dict[str, 'JsonSerializable'] | list['JsonSerializable'] | str | int | float | bool | None
"""Recursive type for JSON-serializable values - primitives plus objects and arrays with JSON-serializable contents.

Based on the definition discussed in https://github.com/python/typing/issues/182.
"""

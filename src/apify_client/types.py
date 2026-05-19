from __future__ import annotations

from datetime import timedelta
from typing import Literal

from apify_client._models import WebhookCreate, WebhookRepresentation
from apify_client._typeddicts import (
    WebhookCreateCamelDict,
    WebhookCreateDict,
    WebhookRepresentationCamelDict,
    WebhookRepresentationDict,
)

Timeout = timedelta | Literal['no_timeout', 'short', 'medium', 'long']
"""Type for the `timeout` parameter on resource client methods.

`'short'`, `'medium'`, and `'long'` are tier literals resolved by the HTTP client to configured values.
A `timedelta` overrides the timeout for this call, and `'no_timeout'` disables the timeout entirely.
"""

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

JsonSerializable = dict[str, 'JsonSerializable'] | list['JsonSerializable'] | str | int | float | bool | None
"""Recursive type for JSON-serializable values - primitives plus objects and arrays with JSON-serializable contents.

Based on the definition discussed in https://github.com/python/typing/issues/182.
"""

__all__ = [
    'JsonSerializable',
    'Timeout',
    'WebhooksList',
]

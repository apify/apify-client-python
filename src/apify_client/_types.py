from __future__ import annotations

from datetime import timedelta
from typing import Literal

from apify_client._models import WebhookCreate, WebhookRepresentation
from apify_client._typeddicts import WebhookCreateDict, WebhookRepresentationDict

WebhooksList = (
    list[WebhookCreate] | list[WebhookCreateDict] | list[WebhookRepresentation] | list[WebhookRepresentationDict]
)
"""Type for the `webhooks` parameter on resource-client `start`/`call` methods and `from_webhooks`.

`WebhookRepresentation` / `WebhookRepresentationDict` are the minimal ad-hoc webhook shape (only
`event_types` and `request_url` required). `WebhookCreate` / `WebhookCreateDict` are accepted so a
persistent-webhook definition can be reused; their fields not relevant to ad-hoc webhooks (e.g.
`condition`) are ignored at runtime.
"""

TerminalActorJobStatus = Literal['SUCCEEDED', 'FAILED', 'TIMED-OUT', 'ABORTED']
"""Subset of `ActorJobStatus` values that indicate the job has finished and will not change again."""

Timeout = timedelta | Literal['no_timeout', 'short', 'medium', 'long']
"""Type for the `timeout` parameter on resource client methods.

`'short'`, `'medium'`, and `'long'` are tier literals resolved by the HTTP client to configured values.
A `timedelta` overrides the timeout for this call, and `'no_timeout'` disables the timeout entirely.
"""

JsonSerializable = dict[str, 'JsonSerializable'] | list['JsonSerializable'] | str | int | float | bool | None
"""Recursive type for JSON-serializable values - primitives plus objects and arrays with JSON-serializable contents.

Based on the definition discussed in https://github.com/python/typing/issues/182.
"""

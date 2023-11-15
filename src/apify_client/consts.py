from __future__ import annotations

import warnings
from typing import Any

from apify_shared.consts import ActorJobStatus as _ActorJobStatus  # noqa: F401
from apify_shared.consts import ActorSourceType as _ActorSourceType  # noqa: F401
from apify_shared.consts import MetaOrigin as _MetaOrigin  # noqa: F401
from apify_shared.consts import WebhookEventType as _WebhookEventType  # noqa: F401

DEPRECATED_NAMES = [
    'ActorJobStatus',
    'ActorSourceType',
    'MetaOrigin',
    'WebhookEventType',
]


# The following piece of code is highly inspired by the example in https://peps.python.org/pep-0562.
# The else branch is missing intentionally! Check the following discussion for details:
# https://github.com/apify/apify-client-python/pull/132#discussion_r1277294315.
def __getattr__(name: str) -> Any:
    if name in DEPRECATED_NAMES:
        warnings.warn(
            (
                f'Importing "{name}" from "apify_client.consts" is deprecated and will be removed in the future. '
                'Please use "apify_shared" library instead.'
            ),
            category=DeprecationWarning,
            stacklevel=2,
        )
        return globals()[f'_{name}']
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')

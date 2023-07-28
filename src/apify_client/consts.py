import warnings
from typing import Any

from apify_shared.consts import ActorJobStatus as ActorJobStatus_
from apify_shared.consts import ActorSourceType as ActorSourceType_
from apify_shared.consts import MetaOrigin as MetaOrigin_
from apify_shared.consts import WebhookEventType as WebhookEventType_

DEPRECATED_NAMES = [
    'ActorJobStatus',
    'ActorSourceType',
    'MetaOrigin',
    'WebhookEventType',
]


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
        return globals()[f'{name}_']
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')

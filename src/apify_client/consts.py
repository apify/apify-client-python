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
        return globals()[f'{name}_']
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')

import warnings
from typing import Any

from apify_shared.consts import BOOL_ENV_VARS as BOOL_ENV_VARS_
from apify_shared.consts import BOOL_ENV_VARS_TYPE as BOOL_ENV_VARS_TYPE_
from apify_shared.consts import DATETIME_ENV_VARS as DATETIME_ENV_VARS_
from apify_shared.consts import DATETIME_ENV_VARS_TYPE as DATETIME_ENV_VARS_TYPE_
from apify_shared.consts import FLOAT_ENV_VARS as FLOAT_ENV_VARS_
from apify_shared.consts import FLOAT_ENV_VARS_TYPE as FLOAT_ENV_VARS_TYPE_
from apify_shared.consts import INTEGER_ENV_VARS as INTEGER_ENV_VARS_
from apify_shared.consts import INTEGER_ENV_VARS_TYPE as INTEGER_ENV_VARS_TYPE_
from apify_shared.consts import STRING_ENV_VARS as STRING_ENV_VARS_
from apify_shared.consts import STRING_ENV_VARS_TYPE as STRING_ENV_VARS_TYPE_
from apify_shared.consts import ActorEventTypes as ActorEventTypes_
from apify_shared.consts import ActorExitCodes as ActorExitCodes_
from apify_shared.consts import ActorJobStatus as ActorJobStatus_
from apify_shared.consts import ActorSourceType as ActorSourceType_
from apify_shared.consts import ApifyEnvVars as ApifyEnvVars_
from apify_shared.consts import MetaOrigin as MetaOrigin_
from apify_shared.consts import WebhookEventType as WebhookEventType_

DEPRECATED_NAMES = [
    'BOOL_ENV_VARS',
    'BOOL_ENV_VARS_TYPE',
    'DATETIME_ENV_VARS',
    'DATETIME_ENV_VARS_TYPE',
    'FLOAT_ENV_VARS',
    'FLOAT_ENV_VARS_TYPE',
    'INTEGER_ENV_VARS',
    'INTEGER_ENV_VARS_TYPE',
    'STRING_ENV_VARS',
    'STRING_ENV_VARS_TYPE',
    'ActorEventTypes',
    'ActorExitCodes',
    'ActorJobStatus',
    'ActorSourceType',
    'ApifyEnvVars',
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

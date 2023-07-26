import warnings

from apify_shared.consts import (
    BOOL_ENV_VARS,
    BOOL_ENV_VARS_TYPE,
    DATETIME_ENV_VARS,
    DATETIME_ENV_VARS_TYPE,
    FLOAT_ENV_VARS,
    FLOAT_ENV_VARS_TYPE,
    INTEGER_ENV_VARS,
    INTEGER_ENV_VARS_TYPE,
    STRING_ENV_VARS,
    STRING_ENV_VARS_TYPE,
    ActorEventTypes,
    ActorExitCodes,
    ActorJobStatus,
    ActorSourceType,
    ApifyEnvVars,
    MetaOrigin,
    WebhookEventType,
)

# Trigger DeprecationWarning
warnings.warn(
    ('Importing constants from "apify_client.consts" is deprecated and will be removed in the future. '
     'Please use "apify_shared" library instead.'),
    category=DeprecationWarning,
    stacklevel=2,
)

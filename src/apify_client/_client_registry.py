from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apify_client._resource_clients import (
        ActorClient,
        ActorClientAsync,
        ActorEnvVarClient,
        ActorEnvVarClientAsync,
        ActorEnvVarCollectionClient,
        ActorEnvVarCollectionClientAsync,
        ActorVersionClient,
        ActorVersionClientAsync,
        ActorVersionCollectionClient,
        ActorVersionCollectionClientAsync,
        BuildClient,
        BuildClientAsync,
        BuildCollectionClient,
        BuildCollectionClientAsync,
        DatasetClient,
        DatasetClientAsync,
        KeyValueStoreClient,
        KeyValueStoreClientAsync,
        LogClient,
        LogClientAsync,
        RequestQueueClient,
        RequestQueueClientAsync,
        RunClient,
        RunClientAsync,
        RunCollectionClient,
        RunCollectionClientAsync,
        WebhookClient,
        WebhookClientAsync,
        WebhookCollectionClient,
        WebhookCollectionClientAsync,
        WebhookDispatchCollectionClient,
        WebhookDispatchCollectionClientAsync,
    )


@dataclass
class ClientRegistry:
    """Bundle of all sync client classes for dependency injection.

    This config object is passed through the client hierarchy to avoid
    parameter explosion when clients need to create other clients.
    Each resource client receives this config and can instantiate other
    clients as needed without knowing about transitive dependencies.
    """

    # Actor-related
    actor_client: type[ActorClient]
    actor_version_client: type[ActorVersionClient]
    actor_version_collection_client: type[ActorVersionCollectionClient]
    actor_env_var_client: type[ActorEnvVarClient]
    actor_env_var_collection_client: type[ActorEnvVarCollectionClient]

    # Build-related
    build_client: type[BuildClient]
    build_collection_client: type[BuildCollectionClient]

    # Run-related
    run_client: type[RunClient]
    run_collection_client: type[RunCollectionClient]

    # Storage-related
    dataset_client: type[DatasetClient]
    key_value_store_client: type[KeyValueStoreClient]
    request_queue_client: type[RequestQueueClient]

    # Webhook-related
    webhook_client: type[WebhookClient]
    webhook_collection_client: type[WebhookCollectionClient]
    webhook_dispatch_collection_client: type[WebhookDispatchCollectionClient]

    # Utilities
    log_client: type[LogClient]


@dataclass
class ClientRegistryAsync:
    """Bundle of all async client classes for dependency injection.

    Async version of ClientRegistry for use with ApifyClientAsync.
    """

    # Actor-related
    actor_client: type[ActorClientAsync]
    actor_version_client: type[ActorVersionClientAsync]
    actor_version_collection_client: type[ActorVersionCollectionClientAsync]
    actor_env_var_client: type[ActorEnvVarClientAsync]
    actor_env_var_collection_client: type[ActorEnvVarCollectionClientAsync]

    # Build-related
    build_client: type[BuildClientAsync]
    build_collection_client: type[BuildCollectionClientAsync]

    # Run-related
    run_client: type[RunClientAsync]
    run_collection_client: type[RunCollectionClientAsync]

    # Storage-related
    dataset_client: type[DatasetClientAsync]
    key_value_store_client: type[KeyValueStoreClientAsync]
    request_queue_client: type[RequestQueueClientAsync]

    # Webhook-related
    webhook_client: type[WebhookClientAsync]
    webhook_collection_client: type[WebhookCollectionClientAsync]
    webhook_dispatch_collection_client: type[WebhookDispatchCollectionClientAsync]

    # Utilities
    log_client: type[LogClientAsync]

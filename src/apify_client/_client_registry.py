from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apify_client._resource_clients import (
        ActorClient,
        ActorClientAsync,
        ActorCollectionClient,
        ActorCollectionClientAsync,
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
        DatasetCollectionClient,
        DatasetCollectionClientAsync,
        KeyValueStoreClient,
        KeyValueStoreClientAsync,
        KeyValueStoreCollectionClient,
        KeyValueStoreCollectionClientAsync,
        LogClient,
        LogClientAsync,
        RequestQueueClient,
        RequestQueueClientAsync,
        RequestQueueCollectionClient,
        RequestQueueCollectionClientAsync,
        RunClient,
        RunClientAsync,
        RunCollectionClient,
        RunCollectionClientAsync,
        ScheduleClient,
        ScheduleClientAsync,
        ScheduleCollectionClient,
        ScheduleCollectionClientAsync,
        StatusMessageWatcherAsync,
        StatusMessageWatcherSync,
        StoreCollectionClient,
        StoreCollectionClientAsync,
        StreamedLogAsync,
        StreamedLogSync,
        TaskClient,
        TaskClientAsync,
        TaskCollectionClient,
        TaskCollectionClientAsync,
        UserClient,
        UserClientAsync,
        WebhookClient,
        WebhookClientAsync,
        WebhookCollectionClient,
        WebhookCollectionClientAsync,
        WebhookDispatchClient,
        WebhookDispatchClientAsync,
        WebhookDispatchCollectionClient,
        WebhookDispatchCollectionClientAsync,
    )


@dataclass
class ClientRegistry:
    """Bundle of all sync client classes for dependency injection.

    This config object is passed to the resource clients to avoid circular dependencies. Each resource client
    receives this config and can instantiate other clients as needed.
    """

    actor_client: type[ActorClient]
    actor_collection_client: type[ActorCollectionClient]
    actor_env_var_client: type[ActorEnvVarClient]
    actor_env_var_collection_client: type[ActorEnvVarCollectionClient]
    actor_version_client: type[ActorVersionClient]
    actor_version_collection_client: type[ActorVersionCollectionClient]
    build_client: type[BuildClient]
    build_collection_client: type[BuildCollectionClient]
    dataset_client: type[DatasetClient]
    dataset_collection_client: type[DatasetCollectionClient]
    key_value_store_client: type[KeyValueStoreClient]
    key_value_store_collection_client: type[KeyValueStoreCollectionClient]
    log_client: type[LogClient]
    status_message_watcher: type[StatusMessageWatcherSync]
    streamed_log: type[StreamedLogSync]
    request_queue_client: type[RequestQueueClient]
    request_queue_collection_client: type[RequestQueueCollectionClient]
    run_client: type[RunClient]
    run_collection_client: type[RunCollectionClient]
    schedule_client: type[ScheduleClient]
    schedule_collection_client: type[ScheduleCollectionClient]
    store_collection_client: type[StoreCollectionClient]
    task_client: type[TaskClient]
    task_collection_client: type[TaskCollectionClient]
    user_client: type[UserClient]
    webhook_client: type[WebhookClient]
    webhook_collection_client: type[WebhookCollectionClient]
    webhook_dispatch_client: type[WebhookDispatchClient]
    webhook_dispatch_collection_client: type[WebhookDispatchCollectionClient]


@dataclass
class ClientRegistryAsync:
    """Bundle of all async client classes for dependency injection.

    This config object is passed to the resource clients to avoid circular dependencies. Each resource client
    receives this config and can instantiate other clients as needed.
    """

    actor_client: type[ActorClientAsync]
    actor_collection_client: type[ActorCollectionClientAsync]
    actor_env_var_client: type[ActorEnvVarClientAsync]
    actor_env_var_collection_client: type[ActorEnvVarCollectionClientAsync]
    actor_version_client: type[ActorVersionClientAsync]
    actor_version_collection_client: type[ActorVersionCollectionClientAsync]
    build_client: type[BuildClientAsync]
    build_collection_client: type[BuildCollectionClientAsync]
    dataset_client: type[DatasetClientAsync]
    dataset_collection_client: type[DatasetCollectionClientAsync]
    key_value_store_client: type[KeyValueStoreClientAsync]
    key_value_store_collection_client: type[KeyValueStoreCollectionClientAsync]
    log_client: type[LogClientAsync]
    status_message_watcher: type[StatusMessageWatcherAsync]
    streamed_log: type[StreamedLogAsync]
    request_queue_client: type[RequestQueueClientAsync]
    request_queue_collection_client: type[RequestQueueCollectionClientAsync]
    run_client: type[RunClientAsync]
    run_collection_client: type[RunCollectionClientAsync]
    schedule_client: type[ScheduleClientAsync]
    schedule_collection_client: type[ScheduleCollectionClientAsync]
    store_collection_client: type[StoreCollectionClientAsync]
    task_client: type[TaskClientAsync]
    task_collection_client: type[TaskCollectionClientAsync]
    user_client: type[UserClientAsync]
    webhook_client: type[WebhookClientAsync]
    webhook_collection_client: type[WebhookCollectionClientAsync]
    webhook_dispatch_client: type[WebhookDispatchClientAsync]
    webhook_dispatch_collection_client: type[WebhookDispatchCollectionClientAsync]

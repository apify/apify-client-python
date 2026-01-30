from __future__ import annotations

from datetime import timedelta  # noqa: TC003 - Used at runtime
from functools import cached_property

from apify_client._client_registry import ClientRegistry, ClientRegistryAsync
from apify_client._consts import (
    API_VERSION,
    DEFAULT_API_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_MIN_DELAY_BETWEEN_RETRIES,
    DEFAULT_TIMEOUT,
)
from apify_client._http_clients import AsyncHttpClient, SyncHttpClient
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
from apify_client._statistics import ClientStatistics


class ApifyClient:
    """The Apify API client."""

    def __init__(
        self,
        token: str | None = None,
        *,
        api_url: str = DEFAULT_API_URL,
        api_public_url: str | None = DEFAULT_API_URL,
        max_retries: int = DEFAULT_MAX_RETRIES,
        min_delay_between_retries: timedelta = DEFAULT_MIN_DELAY_BETWEEN_RETRIES,
        timeout: timedelta = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize a new instance.

        Args:
            token: The Apify API token.
            api_url: The URL of the Apify API server to which to connect. Defaults to https://api.apify.com. It can
                be an internal URL that is not globally accessible, in such case `api_public_url` should be set as well.
            api_public_url: The globally accessible URL of the Apify API server. It should be set only if the `api_url`
                is an internal URL that is not globally accessible. Defaults to https://api.apify.com.
            max_retries: How many times to retry a failed request at most.
            min_delay_between_retries: How long will the client wait between retrying requests
                (increases exponentially from this value).
            timeout: The socket timeout of the HTTP requests sent to the Apify API.
        """
        # We need to do this because of mocking in tests and default mutable arguments.
        api_url = DEFAULT_API_URL if api_url is None else api_url
        api_public_url = DEFAULT_API_URL if api_public_url is None else api_public_url

        self._token = token
        """Apify API token for authentication."""

        self._base_url = f'{api_url.rstrip("/")}/{API_VERSION}'
        """Base URL of the Apify API."""

        self._public_base_url = f'{api_public_url.rstrip("/")}/{API_VERSION}'
        """Public base URL for CDN access."""

        self._statistics = ClientStatistics()
        """Collector for client request statistics."""

        self._http_client = SyncHttpClient(
            token=token,
            timeout=timeout or DEFAULT_TIMEOUT,
            max_retries=max_retries or DEFAULT_MAX_RETRIES,
            min_delay_between_retries=min_delay_between_retries or DEFAULT_MIN_DELAY_BETWEEN_RETRIES,
            statistics=self._statistics,
        )
        """HTTP client used to communicate with the Apify API."""

        self._client_registry = ClientRegistry(
            actor_client=ActorClient,
            actor_collection_client=ActorCollectionClient,
            actor_env_var_client=ActorEnvVarClient,
            actor_env_var_collection_client=ActorEnvVarCollectionClient,
            actor_version_client=ActorVersionClient,
            actor_version_collection_client=ActorVersionCollectionClient,
            build_client=BuildClient,
            build_collection_client=BuildCollectionClient,
            dataset_client=DatasetClient,
            dataset_collection_client=DatasetCollectionClient,
            key_value_store_client=KeyValueStoreClient,
            key_value_store_collection_client=KeyValueStoreCollectionClient,
            log_client=LogClient,
            status_message_watcher=StatusMessageWatcherSync,
            streamed_log=StreamedLogSync,
            request_queue_client=RequestQueueClient,
            request_queue_collection_client=RequestQueueCollectionClient,
            run_client=RunClient,
            run_collection_client=RunCollectionClient,
            schedule_client=ScheduleClient,
            schedule_collection_client=ScheduleCollectionClient,
            store_collection_client=StoreCollectionClient,
            task_client=TaskClient,
            task_collection_client=TaskCollectionClient,
            user_client=UserClient,
            webhook_client=WebhookClient,
            webhook_collection_client=WebhookCollectionClient,
            webhook_dispatch_client=WebhookDispatchClient,
            webhook_dispatch_collection_client=WebhookDispatchCollectionClient,
        )
        """Registry of resource client classes used for dependency injection."""

    @cached_property
    def _base_kwargs(self) -> dict:
        """Base keyword arguments for resource client construction."""
        return {
            'base_url': self._base_url,
            'public_base_url': self._public_base_url,
            'http_client': self._http_client,
            'client_registry': self._client_registry,
        }

    @property
    def token(self) -> str | None:
        """The Apify API token used by the client."""
        return self._token

    def actor(self, actor_id: str) -> ActorClient:
        """Retrieve the sub-client for manipulating a single Actor.

        Args:
            actor_id: ID of the Actor to be manipulated.
        """
        return ActorClient(resource_id=actor_id, **self._base_kwargs)

    def actors(self) -> ActorCollectionClient:
        """Retrieve the sub-client for manipulating Actors."""
        return ActorCollectionClient(**self._base_kwargs)

    def build(self, build_id: str) -> BuildClient:
        """Retrieve the sub-client for manipulating a single Actor build.

        Args:
            build_id: ID of the Actor build to be manipulated.
        """
        return BuildClient(resource_id=build_id, **self._base_kwargs)

    def builds(self) -> BuildCollectionClient:
        """Retrieve the sub-client for querying multiple builds of a user."""
        return BuildCollectionClient(**self._base_kwargs)

    def run(self, run_id: str) -> RunClient:
        """Retrieve the sub-client for manipulating a single Actor run.

        Args:
            run_id: ID of the Actor run to be manipulated.
        """
        return RunClient(resource_id=run_id, **self._base_kwargs)

    def runs(self) -> RunCollectionClient:
        """Retrieve the sub-client for querying multiple Actor runs of a user."""
        return RunCollectionClient(**self._base_kwargs)

    def dataset(self, dataset_id: str) -> DatasetClient:
        """Retrieve the sub-client for manipulating a single dataset.

        Args:
            dataset_id: ID of the dataset to be manipulated.
        """
        return DatasetClient(resource_id=dataset_id, **self._base_kwargs)

    def datasets(self) -> DatasetCollectionClient:
        """Retrieve the sub-client for manipulating datasets."""
        return DatasetCollectionClient(**self._base_kwargs)

    def key_value_store(self, key_value_store_id: str) -> KeyValueStoreClient:
        """Retrieve the sub-client for manipulating a single key-value store.

        Args:
            key_value_store_id: ID of the key-value store to be manipulated.
        """
        return KeyValueStoreClient(resource_id=key_value_store_id, **self._base_kwargs)

    def key_value_stores(self) -> KeyValueStoreCollectionClient:
        """Retrieve the sub-client for manipulating key-value stores."""
        return KeyValueStoreCollectionClient(**self._base_kwargs)

    def request_queue(self, request_queue_id: str, *, client_key: str | None = None) -> RequestQueueClient:
        """Retrieve the sub-client for manipulating a single request queue.

        Args:
            request_queue_id: ID of the request queue to be manipulated.
            client_key: A unique identifier of the client accessing the request queue.
        """
        return RequestQueueClient(resource_id=request_queue_id, client_key=client_key, **self._base_kwargs)

    def request_queues(self) -> RequestQueueCollectionClient:
        """Retrieve the sub-client for manipulating request queues."""
        return RequestQueueCollectionClient(**self._base_kwargs)

    def webhook(self, webhook_id: str) -> WebhookClient:
        """Retrieve the sub-client for manipulating a single webhook.

        Args:
            webhook_id: ID of the webhook to be manipulated.
        """
        return WebhookClient(resource_id=webhook_id, **self._base_kwargs)

    def webhooks(self) -> WebhookCollectionClient:
        """Retrieve the sub-client for querying multiple webhooks of a user."""
        return WebhookCollectionClient(**self._base_kwargs)

    def webhook_dispatch(self, webhook_dispatch_id: str) -> WebhookDispatchClient:
        """Retrieve the sub-client for accessing a single webhook dispatch.

        Args:
            webhook_dispatch_id: ID of the webhook dispatch to access.
        """
        return WebhookDispatchClient(resource_id=webhook_dispatch_id, **self._base_kwargs)

    def webhook_dispatches(self) -> WebhookDispatchCollectionClient:
        """Retrieve the sub-client for querying multiple webhook dispatches of a user."""
        return WebhookDispatchCollectionClient(**self._base_kwargs)

    def schedule(self, schedule_id: str) -> ScheduleClient:
        """Retrieve the sub-client for manipulating a single schedule.

        Args:
            schedule_id: ID of the schedule to be manipulated.
        """
        return ScheduleClient(resource_id=schedule_id, **self._base_kwargs)

    def schedules(self) -> ScheduleCollectionClient:
        """Retrieve the sub-client for manipulating schedules."""
        return ScheduleCollectionClient(**self._base_kwargs)

    def log(self, build_or_run_id: str) -> LogClient:
        """Retrieve the sub-client for retrieving logs.

        Args:
            build_or_run_id: ID of the Actor build or run for which to access the log.
        """
        return LogClient(resource_id=build_or_run_id, **self._base_kwargs)

    def task(self, task_id: str) -> TaskClient:
        """Retrieve the sub-client for manipulating a single task.

        Args:
            task_id: ID of the task to be manipulated.
        """
        return TaskClient(resource_id=task_id, **self._base_kwargs)

    def tasks(self) -> TaskCollectionClient:
        """Retrieve the sub-client for manipulating tasks."""
        return TaskCollectionClient(**self._base_kwargs)

    def user(self, user_id: str | None = None) -> UserClient:
        """Retrieve the sub-client for querying users.

        Args:
            user_id: ID of user to be queried. If None, queries the user belonging to the token supplied to the client.
        """
        return UserClient(resource_id=user_id, **self._base_kwargs)

    def store(self) -> StoreCollectionClient:
        """Retrieve the sub-client for Apify store."""
        return StoreCollectionClient(**self._base_kwargs)


class ApifyClientAsync:
    """The asynchronous version of the Apify API client."""

    def __init__(
        self,
        token: str | None = None,
        *,
        api_url: str = DEFAULT_API_URL,
        api_public_url: str | None = DEFAULT_API_URL,
        max_retries: int = DEFAULT_MAX_RETRIES,
        min_delay_between_retries: timedelta = DEFAULT_MIN_DELAY_BETWEEN_RETRIES,
        timeout: timedelta = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize a new instance.

        Args:
            token: The Apify API token.
            api_url: The URL of the Apify API server to which to connect. Defaults to https://api.apify.com. It can
                be an internal URL that is not globally accessible, in such case `api_public_url` should be set as well.
            api_public_url: The globally accessible URL of the Apify API server. It should be set only if the `api_url`
                is an internal URL that is not globally accessible. Defaults to https://api.apify.com.
            max_retries: How many times to retry a failed request at most.
            min_delay_between_retries: How long will the client wait between retrying requests
                (increases exponentially from this value).
            timeout: The socket timeout of the HTTP requests sent to the Apify API.
        """
        # We need to do this because of mocking in tests and default mutable arguments.
        api_url = DEFAULT_API_URL if api_url is None else api_url
        api_public_url = DEFAULT_API_URL if api_public_url is None else api_public_url

        self._token = token
        """Apify API token for authentication."""

        self._base_url = f'{api_url.rstrip("/")}/{API_VERSION}'
        """Base URL of the Apify API."""

        self._public_base_url = f'{api_public_url.rstrip("/")}/{API_VERSION}'
        """Public base URL for CDN access."""

        self._statistics = ClientStatistics()
        """Collector for client request statistics."""

        self._http_client = AsyncHttpClient(
            token=token,
            timeout=timeout or DEFAULT_TIMEOUT,
            max_retries=max_retries or DEFAULT_MAX_RETRIES,
            min_delay_between_retries=min_delay_between_retries or DEFAULT_MIN_DELAY_BETWEEN_RETRIES,
            statistics=self._statistics,
        )
        """HTTP client used to communicate with the Apify API."""

        self._client_registry = ClientRegistryAsync(
            actor_client=ActorClientAsync,
            actor_collection_client=ActorCollectionClientAsync,
            actor_env_var_client=ActorEnvVarClientAsync,
            actor_env_var_collection_client=ActorEnvVarCollectionClientAsync,
            actor_version_client=ActorVersionClientAsync,
            actor_version_collection_client=ActorVersionCollectionClientAsync,
            build_client=BuildClientAsync,
            build_collection_client=BuildCollectionClientAsync,
            dataset_client=DatasetClientAsync,
            dataset_collection_client=DatasetCollectionClientAsync,
            key_value_store_client=KeyValueStoreClientAsync,
            key_value_store_collection_client=KeyValueStoreCollectionClientAsync,
            log_client=LogClientAsync,
            status_message_watcher=StatusMessageWatcherAsync,
            streamed_log=StreamedLogAsync,
            request_queue_client=RequestQueueClientAsync,
            request_queue_collection_client=RequestQueueCollectionClientAsync,
            run_client=RunClientAsync,
            run_collection_client=RunCollectionClientAsync,
            schedule_client=ScheduleClientAsync,
            schedule_collection_client=ScheduleCollectionClientAsync,
            store_collection_client=StoreCollectionClientAsync,
            task_client=TaskClientAsync,
            task_collection_client=TaskCollectionClientAsync,
            user_client=UserClientAsync,
            webhook_client=WebhookClientAsync,
            webhook_collection_client=WebhookCollectionClientAsync,
            webhook_dispatch_client=WebhookDispatchClientAsync,
            webhook_dispatch_collection_client=WebhookDispatchCollectionClientAsync,
        )
        """Registry of resource client classes used for dependency injection."""

    @cached_property
    def _base_kwargs(self) -> dict:
        """Base keyword arguments for resource client construction."""
        return {
            'base_url': self._base_url,
            'public_base_url': self._public_base_url,
            'http_client': self._http_client,
            'client_registry': self._client_registry,
        }

    @property
    def token(self) -> str | None:
        """The Apify API token used by the client."""
        return self._token

    def actor(self, actor_id: str) -> ActorClientAsync:
        """Retrieve the sub-client for manipulating a single Actor.

        Args:
            actor_id: ID of the Actor to be manipulated.
        """
        return ActorClientAsync(resource_id=actor_id, **self._base_kwargs)

    def actors(self) -> ActorCollectionClientAsync:
        """Retrieve the sub-client for manipulating Actors."""
        return ActorCollectionClientAsync(**self._base_kwargs)

    def build(self, build_id: str) -> BuildClientAsync:
        """Retrieve the sub-client for manipulating a single Actor build.

        Args:
            build_id: ID of the Actor build to be manipulated.
        """
        return BuildClientAsync(resource_id=build_id, **self._base_kwargs)

    def builds(self) -> BuildCollectionClientAsync:
        """Retrieve the sub-client for querying multiple builds of a user."""
        return BuildCollectionClientAsync(**self._base_kwargs)

    def run(self, run_id: str) -> RunClientAsync:
        """Retrieve the sub-client for manipulating a single Actor run.

        Args:
            run_id: ID of the Actor run to be manipulated.
        """
        return RunClientAsync(resource_id=run_id, **self._base_kwargs)

    def runs(self) -> RunCollectionClientAsync:
        """Retrieve the sub-client for querying multiple Actor runs of a user."""
        return RunCollectionClientAsync(**self._base_kwargs)

    def dataset(self, dataset_id: str) -> DatasetClientAsync:
        """Retrieve the sub-client for manipulating a single dataset.

        Args:
            dataset_id: ID of the dataset to be manipulated.
        """
        return DatasetClientAsync(resource_id=dataset_id, **self._base_kwargs)

    def datasets(self) -> DatasetCollectionClientAsync:
        """Retrieve the sub-client for manipulating datasets."""
        return DatasetCollectionClientAsync(**self._base_kwargs)

    def key_value_store(self, key_value_store_id: str) -> KeyValueStoreClientAsync:
        """Retrieve the sub-client for manipulating a single key-value store.

        Args:
            key_value_store_id: ID of the key-value store to be manipulated.
        """
        return KeyValueStoreClientAsync(resource_id=key_value_store_id, **self._base_kwargs)

    def key_value_stores(self) -> KeyValueStoreCollectionClientAsync:
        """Retrieve the sub-client for manipulating key-value stores."""
        return KeyValueStoreCollectionClientAsync(**self._base_kwargs)

    def request_queue(self, request_queue_id: str, *, client_key: str | None = None) -> RequestQueueClientAsync:
        """Retrieve the sub-client for manipulating a single request queue.

        Args:
            request_queue_id: ID of the request queue to be manipulated.
            client_key: A unique identifier of the client accessing the request queue.
        """
        return RequestQueueClientAsync(resource_id=request_queue_id, client_key=client_key, **self._base_kwargs)

    def request_queues(self) -> RequestQueueCollectionClientAsync:
        """Retrieve the sub-client for manipulating request queues."""
        return RequestQueueCollectionClientAsync(**self._base_kwargs)

    def webhook(self, webhook_id: str) -> WebhookClientAsync:
        """Retrieve the sub-client for manipulating a single webhook.

        Args:
            webhook_id: ID of the webhook to be manipulated.
        """
        return WebhookClientAsync(resource_id=webhook_id, **self._base_kwargs)

    def webhooks(self) -> WebhookCollectionClientAsync:
        """Retrieve the sub-client for querying multiple webhooks of a user."""
        return WebhookCollectionClientAsync(**self._base_kwargs)

    def webhook_dispatch(self, webhook_dispatch_id: str) -> WebhookDispatchClientAsync:
        """Retrieve the sub-client for accessing a single webhook dispatch.

        Args:
            webhook_dispatch_id: ID of the webhook dispatch to access.
        """
        return WebhookDispatchClientAsync(resource_id=webhook_dispatch_id, **self._base_kwargs)

    def webhook_dispatches(self) -> WebhookDispatchCollectionClientAsync:
        """Retrieve the sub-client for querying multiple webhook dispatches of a user."""
        return WebhookDispatchCollectionClientAsync(**self._base_kwargs)

    def schedule(self, schedule_id: str) -> ScheduleClientAsync:
        """Retrieve the sub-client for manipulating a single schedule.

        Args:
            schedule_id: ID of the schedule to be manipulated.
        """
        return ScheduleClientAsync(resource_id=schedule_id, **self._base_kwargs)

    def schedules(self) -> ScheduleCollectionClientAsync:
        """Retrieve the sub-client for manipulating schedules."""
        return ScheduleCollectionClientAsync(**self._base_kwargs)

    def log(self, build_or_run_id: str) -> LogClientAsync:
        """Retrieve the sub-client for retrieving logs.

        Args:
            build_or_run_id: ID of the Actor build or run for which to access the log.
        """
        return LogClientAsync(resource_id=build_or_run_id, **self._base_kwargs)

    def task(self, task_id: str) -> TaskClientAsync:
        """Retrieve the sub-client for manipulating a single task.

        Args:
            task_id: ID of the task to be manipulated.
        """
        return TaskClientAsync(resource_id=task_id, **self._base_kwargs)

    def tasks(self) -> TaskCollectionClientAsync:
        """Retrieve the sub-client for manipulating tasks."""
        return TaskCollectionClientAsync(**self._base_kwargs)

    def user(self, user_id: str | None = None) -> UserClientAsync:
        """Retrieve the sub-client for querying users.

        Args:
            user_id: ID of user to be queried. If None, queries the user belonging to the token supplied to the client.
        """
        return UserClientAsync(resource_id=user_id, **self._base_kwargs)

    def store(self) -> StoreCollectionClientAsync:
        """Retrieve the sub-client for Apify store."""
        return StoreCollectionClientAsync(**self._base_kwargs)

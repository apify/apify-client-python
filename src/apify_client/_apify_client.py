from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from apify_client._client_registry import ClientRegistry, ClientRegistryAsync
from apify_client._consts import (
    API_VERSION,
    DEFAULT_API_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_MIN_DELAY_BETWEEN_RETRIES,
    DEFAULT_TIMEOUT_LONG,
    DEFAULT_TIMEOUT_MAX,
    DEFAULT_TIMEOUT_MEDIUM,
    DEFAULT_TIMEOUT_SHORT,
)
from apify_client._docs import docs_group
from apify_client._http_clients import HttpClient, HttpClientAsync, ImpitHttpClient, ImpitHttpClientAsync
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
    StoreCollectionClient,
    StoreCollectionClientAsync,
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
from apify_client._utils import check_custom_headers

if TYPE_CHECKING:
    from datetime import timedelta


@docs_group('Apify API clients')
class ApifyClient:
    """Synchronous client for the Apify API.

    This is the main entry point for interacting with the Apify platform. It provides methods to access
    resource-specific sub-clients for managing Actors, runs, datasets, key-value stores, request queues,
    schedules, webhooks, and more.

    The client automatically handles retries with exponential backoff for failed or rate-limited requests.

    ### Usage

    ```python
    from apify_client import ApifyClient

    client = ApifyClient(token='MY-APIFY-TOKEN')

    # Start an Actor and wait for it to finish.
    actor_client = client.actor('apify/python-example')
    run = actor_client.call(run_input={'first_number': 1, 'second_number': 2})

    # Fetch results from the run's default dataset.
    if run is not None:
        dataset_client = client.dataset(run.default_dataset_id)
        items = dataset_client.list_items().items
        for item in items:
            print(item)
    ```
    """

    def __init__(
        self,
        token: str | None = None,
        *,
        api_url: str = DEFAULT_API_URL,
        api_public_url: str | None = DEFAULT_API_URL,
        max_retries: int = DEFAULT_MAX_RETRIES,
        min_delay_between_retries: timedelta = DEFAULT_MIN_DELAY_BETWEEN_RETRIES,
        timeout_short: timedelta = DEFAULT_TIMEOUT_SHORT,
        timeout_medium: timedelta = DEFAULT_TIMEOUT_MEDIUM,
        timeout_long: timedelta = DEFAULT_TIMEOUT_LONG,
        timeout_max: timedelta = DEFAULT_TIMEOUT_MAX,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Initialize the Apify API client.

        To use a custom HTTP client, use the `with_custom_http_client` class method instead.

        Args:
            token: The Apify API token. You can find your token on the
                [Integrations](https://console.apify.com/account/integrations) page in the Apify Console.
            api_url: The URL of the Apify API server to connect to. Defaults to https://api.apify.com. It can
                be an internal URL that is not globally accessible, in which case `api_public_url` should be set
                as well.
            api_public_url: The globally accessible URL of the Apify API server. Should be set only if `api_url`
                is an internal URL that is not globally accessible. Defaults to https://api.apify.com.
            max_retries: How many times to retry a failed request at most.
            min_delay_between_retries: How long will the client wait between retrying requests
                (increases exponentially from this value).
            timeout_short: Default timeout for short-duration API operations (simple CRUD operations, ...).
            timeout_medium: Default timeout for medium-duration API operations (batch operations, listing, ...).
            timeout_long: Default timeout for long-duration API operations (long-polling, streaming, ...).
            timeout_max: Maximum timeout cap for exponential timeout growth across retries.
            headers: Additional HTTP headers to include in all API requests.
        """
        # We need to do this because of mocking in tests and default mutable arguments.
        api_url = DEFAULT_API_URL if api_url is None else api_url
        api_public_url = DEFAULT_API_URL if api_public_url is None else api_public_url

        if headers:
            check_custom_headers(self.__class__.__name__, headers)

        self._token = token
        """Apify API token for authentication."""

        self._base_url = f'{api_url.rstrip("/")}/{API_VERSION}'
        """Base URL of the Apify API."""

        self._public_base_url = f'{api_public_url.rstrip("/")}/{API_VERSION}'
        """Public base URL for CDN access."""

        self._statistics = ClientStatistics()
        """Collector for client request statistics."""

        self._http_client: HttpClient | None = None
        """HTTP client used to communicate with the Apify API. Lazily initialized on first access."""

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

        # Configuration for the default HTTP client (used if a custom client is not provided).
        self._max_retries = max_retries
        self._min_delay_between_retries = min_delay_between_retries
        self._timeout_short = timeout_short
        self._timeout_medium = timeout_medium
        self._timeout_long = timeout_long
        self._timeout_max = timeout_max
        self._headers = headers

    @classmethod
    def with_custom_http_client(
        cls,
        token: str | None = None,
        *,
        api_url: str = DEFAULT_API_URL,
        api_public_url: str | None = DEFAULT_API_URL,
        http_client: HttpClient,
    ) -> ApifyClient:
        """Create an `ApifyClient` instance with a custom HTTP client.

        Use this alternative constructor when you want to provide your own HTTP client implementation
        instead of the default one. The custom client is responsible for its own configuration
        (retries, timeouts, headers, etc.).

        ### Usage

        ```python
        from apify_client import ApifyClient, HttpClient, HttpResponse

        class MyHttpClient(HttpClient):
            def call(self, *, method, url, **kwargs) -> HttpResponse:
                ...

        client = ApifyClient.with_custom_http_client(
            token='MY-APIFY-TOKEN',
            http_client=MyHttpClient(),
        )
        ```

        Args:
            token: The Apify API token.
            api_url: The URL of the Apify API server to connect to. Defaults to https://api.apify.com.
            api_public_url: The globally accessible URL of the Apify API server. Defaults to https://api.apify.com.
            http_client: A custom HTTP client instance extending `HttpClient`.
        """
        instance = cls(token=token, api_url=api_url, api_public_url=api_public_url)
        instance._http_client = http_client
        return instance

    @property
    def token(self) -> str | None:
        """The Apify API token used by the client."""
        return self._token

    @property
    def http_client(self) -> HttpClient:
        """The HTTP client instance used for API communication.

        Returns the custom HTTP client if one was provided via `with_custom_http_client`,
        or the default `ImpitHttpClient` otherwise (lazily created on first access).
        """
        if self._http_client is None:
            self._http_client = ImpitHttpClient(
                token=self._token,
                timeout_short=self._timeout_short,
                timeout_medium=self._timeout_medium,
                timeout_long=self._timeout_long,
                timeout_max=self._timeout_max,
                max_retries=self._max_retries,
                min_delay_between_retries=self._min_delay_between_retries,
                statistics=self._statistics,
                headers=self._headers,
            )

        return self._http_client

    @cached_property
    def _base_kwargs(self) -> dict:
        """Base keyword arguments for resource client construction."""
        return {
            'base_url': self._base_url,
            'public_base_url': self._public_base_url,
            'http_client': self.http_client,
            'client_registry': self._client_registry,
        }

    def actor(self, actor_id: str) -> ActorClient:
        """Get the sub-client for a specific Actor.

        Args:
            actor_id: ID of the Actor to be manipulated.
        """
        return ActorClient(resource_id=actor_id, **self._base_kwargs)

    def actors(self) -> ActorCollectionClient:
        """Get the sub-client for the Actor collection, allowing to list and create Actors."""
        return ActorCollectionClient(**self._base_kwargs)

    def build(self, build_id: str) -> BuildClient:
        """Get the sub-client for a specific Actor build.

        Args:
            build_id: ID of the Actor build to be manipulated.
        """
        return BuildClient(resource_id=build_id, **self._base_kwargs)

    def builds(self) -> BuildCollectionClient:
        """Get the sub-client for the build collection, allowing to list builds."""
        return BuildCollectionClient(**self._base_kwargs)

    def run(self, run_id: str) -> RunClient:
        """Get the sub-client for a specific Actor run.

        Args:
            run_id: ID of the Actor run to be manipulated.
        """
        return RunClient(resource_id=run_id, **self._base_kwargs)

    def runs(self) -> RunCollectionClient:
        """Get the sub-client for the run collection, allowing to list Actor runs."""
        return RunCollectionClient(**self._base_kwargs)

    def dataset(self, dataset_id: str) -> DatasetClient:
        """Get the sub-client for a specific dataset.

        Args:
            dataset_id: ID of the dataset to be manipulated.
        """
        return DatasetClient(resource_id=dataset_id, **self._base_kwargs)

    def datasets(self) -> DatasetCollectionClient:
        """Get the sub-client for the dataset collection, allowing to list and create datasets."""
        return DatasetCollectionClient(**self._base_kwargs)

    def key_value_store(self, key_value_store_id: str) -> KeyValueStoreClient:
        """Get the sub-client for a specific key-value store.

        Args:
            key_value_store_id: ID of the key-value store to be manipulated.
        """
        return KeyValueStoreClient(resource_id=key_value_store_id, **self._base_kwargs)

    def key_value_stores(self) -> KeyValueStoreCollectionClient:
        """Get the sub-client for the key-value store collection, allowing to list and create key-value stores."""
        return KeyValueStoreCollectionClient(**self._base_kwargs)

    def request_queue(self, request_queue_id: str, *, client_key: str | None = None) -> RequestQueueClient:
        """Get the sub-client for a specific request queue.

        Args:
            request_queue_id: ID of the request queue to be manipulated.
            client_key: A unique identifier of the client accessing the request queue.
        """
        return RequestQueueClient(resource_id=request_queue_id, client_key=client_key, **self._base_kwargs)

    def request_queues(self) -> RequestQueueCollectionClient:
        """Get the sub-client for the request queue collection, allowing to list and create request queues."""
        return RequestQueueCollectionClient(**self._base_kwargs)

    def webhook(self, webhook_id: str) -> WebhookClient:
        """Get the sub-client for a specific webhook.

        Args:
            webhook_id: ID of the webhook to be manipulated.
        """
        return WebhookClient(resource_id=webhook_id, **self._base_kwargs)

    def webhooks(self) -> WebhookCollectionClient:
        """Get the sub-client for the webhook collection, allowing to list and create webhooks."""
        return WebhookCollectionClient(**self._base_kwargs)

    def webhook_dispatch(self, webhook_dispatch_id: str) -> WebhookDispatchClient:
        """Get the sub-client for a specific webhook dispatch.

        Args:
            webhook_dispatch_id: ID of the webhook dispatch to access.
        """
        return WebhookDispatchClient(resource_id=webhook_dispatch_id, **self._base_kwargs)

    def webhook_dispatches(self) -> WebhookDispatchCollectionClient:
        """Get the sub-client for the webhook dispatch collection, allowing to list webhook dispatches."""
        return WebhookDispatchCollectionClient(**self._base_kwargs)

    def schedule(self, schedule_id: str) -> ScheduleClient:
        """Get the sub-client for a specific schedule.

        Args:
            schedule_id: ID of the schedule to be manipulated.
        """
        return ScheduleClient(resource_id=schedule_id, **self._base_kwargs)

    def schedules(self) -> ScheduleCollectionClient:
        """Get the sub-client for the schedule collection, allowing to list and create schedules."""
        return ScheduleCollectionClient(**self._base_kwargs)

    def log(self, build_or_run_id: str) -> LogClient:
        """Get the sub-client for retrieving logs of an Actor build or run.

        Args:
            build_or_run_id: ID of the Actor build or run for which to access the log.
        """
        return LogClient(resource_id=build_or_run_id, **self._base_kwargs)

    def task(self, task_id: str) -> TaskClient:
        """Get the sub-client for a specific Actor task.

        Args:
            task_id: ID of the task to be manipulated.
        """
        return TaskClient(resource_id=task_id, **self._base_kwargs)

    def tasks(self) -> TaskCollectionClient:
        """Get the sub-client for the task collection, allowing to list and create Actor tasks."""
        return TaskCollectionClient(**self._base_kwargs)

    def user(self, user_id: str | None = None) -> UserClient:
        """Get the sub-client for querying user data.

        Args:
            user_id: ID of user to be queried. If None, queries the user belonging to the token supplied to the client.
        """
        return UserClient(resource_id=user_id, **self._base_kwargs)

    def store(self) -> StoreCollectionClient:
        """Get the sub-client for the Apify Store, allowing to list Actors published in the store."""
        return StoreCollectionClient(**self._base_kwargs)


@docs_group('Apify API clients')
class ApifyClientAsync:
    """Asynchronous client for the Apify API.

    This is the main entry point for interacting with the Apify platform using async/await. It provides
    methods to access resource-specific sub-clients for managing Actors, runs, datasets, key-value stores,
    request queues, schedules, webhooks, and more.

    The client automatically handles retries with exponential backoff for failed or rate-limited requests.

    ### Usage

    ```python
    import asyncio

    from apify_client import ApifyClientAsync


    async def main() -> None:
        client = ApifyClientAsync(token='MY-APIFY-TOKEN')

        # Start an Actor and wait for it to finish.
        actor_client = client.actor('apify/python-example')
        run = await actor_client.call(run_input={'first_number': 1, 'second_number': 2})

        # Fetch results from the run's default dataset.
        if run is not None:
            dataset_client = client.dataset(run.default_dataset_id)
            items = (await dataset_client.list_items()).items
            for item in items:
                print(item)


    asyncio.run(main())
    ```
    """

    def __init__(
        self,
        token: str | None = None,
        *,
        api_url: str = DEFAULT_API_URL,
        api_public_url: str | None = DEFAULT_API_URL,
        max_retries: int = DEFAULT_MAX_RETRIES,
        min_delay_between_retries: timedelta = DEFAULT_MIN_DELAY_BETWEEN_RETRIES,
        timeout_short: timedelta = DEFAULT_TIMEOUT_SHORT,
        timeout_medium: timedelta = DEFAULT_TIMEOUT_MEDIUM,
        timeout_long: timedelta = DEFAULT_TIMEOUT_LONG,
        timeout_max: timedelta = DEFAULT_TIMEOUT_MAX,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Initialize the Apify API client.

        To use a custom HTTP client, use the `with_custom_http_client` class method instead.

        Args:
            token: The Apify API token. You can find your token on the
                [Integrations](https://console.apify.com/account/integrations) page in the Apify Console.
            api_url: The URL of the Apify API server to connect to. Defaults to https://api.apify.com. It can
                be an internal URL that is not globally accessible, in which case `api_public_url` should be set
                as well.
            api_public_url: The globally accessible URL of the Apify API server. Should be set only if `api_url`
                is an internal URL that is not globally accessible. Defaults to https://api.apify.com.
            max_retries: How many times to retry a failed request at most.
            min_delay_between_retries: How long will the client wait between retrying requests
                (increases exponentially from this value).
            timeout_short: Default timeout for short-duration API operations (simple CRUD operations, ...).
            timeout_medium: Default timeout for medium-duration API operations (batch operations, listing, ...).
            timeout_long: Default timeout for long-duration API operations (long-polling, streaming, ...).
            timeout_max: Maximum timeout cap for exponential timeout growth across retries.
            headers: Additional HTTP headers to include in all API requests.
        """
        # We need to do this because of mocking in tests and default mutable arguments.
        api_url = DEFAULT_API_URL if api_url is None else api_url
        api_public_url = DEFAULT_API_URL if api_public_url is None else api_public_url

        if headers:
            check_custom_headers(self.__class__.__name__, headers)

        self._token = token
        """Apify API token for authentication."""

        self._base_url = f'{api_url.rstrip("/")}/{API_VERSION}'
        """Base URL of the Apify API."""

        self._public_base_url = f'{api_public_url.rstrip("/")}/{API_VERSION}'
        """Public base URL for CDN access."""

        self._statistics = ClientStatistics()
        """Collector for client request statistics."""

        self._http_client: HttpClientAsync | None = None
        """HTTP client used to communicate with the Apify API. Lazily initialized on first access."""

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

        # Configuration for the default HTTP client (used if a custom client is not provided).
        self._max_retries = max_retries
        self._min_delay_between_retries = min_delay_between_retries
        self._timeout_short = timeout_short
        self._timeout_medium = timeout_medium
        self._timeout_long = timeout_long
        self._timeout_max = timeout_max
        self._headers = headers

    @classmethod
    def with_custom_http_client(
        cls,
        token: str | None = None,
        *,
        api_url: str = DEFAULT_API_URL,
        api_public_url: str | None = DEFAULT_API_URL,
        http_client: HttpClientAsync,
    ) -> ApifyClientAsync:
        """Create an `ApifyClientAsync` instance with a custom HTTP client.

        Use this alternative constructor when you want to provide your own HTTP client implementation
        instead of the default one. The custom client is responsible for its own configuration
        (retries, timeouts, headers, etc.).

        ### Usage

        ```python
        from apify_client import ApifyClientAsync, HttpClientAsync, HttpResponse

        class MyHttpClient(HttpClientAsync):
            async def call(self, *, method, url, **kwargs) -> HttpResponse:
                ...

        client = ApifyClientAsync.with_custom_http_client(
            token='MY-APIFY-TOKEN',
            http_client=MyHttpClient(),
        )
        ```

        Args:
            token: The Apify API token.
            api_url: The URL of the Apify API server to connect to. Defaults to https://api.apify.com.
            api_public_url: The globally accessible URL of the Apify API server. Defaults to https://api.apify.com.
            http_client: A custom HTTP client instance extending `HttpClientAsync`.
        """
        instance = cls(token=token, api_url=api_url, api_public_url=api_public_url)
        instance._http_client = http_client
        return instance

    @property
    def token(self) -> str | None:
        """The Apify API token used by the client."""
        return self._token

    @property
    def http_client(self) -> HttpClientAsync:
        """The HTTP client instance used for API communication.

        Returns the custom HTTP client if one was provided via `with_custom_http_client`,
        or the default `ImpitHttpClientAsync` otherwise (lazily created on first access).
        """
        if self._http_client is None:
            self._http_client = ImpitHttpClientAsync(
                token=self._token,
                timeout_short=self._timeout_short,
                timeout_medium=self._timeout_medium,
                timeout_long=self._timeout_long,
                timeout_max=self._timeout_max,
                max_retries=self._max_retries,
                min_delay_between_retries=self._min_delay_between_retries,
                statistics=self._statistics,
                headers=self._headers,
            )
        return self._http_client

    @cached_property
    def _base_kwargs(self) -> dict:
        """Base keyword arguments for resource client construction."""
        return {
            'base_url': self._base_url,
            'public_base_url': self._public_base_url,
            'http_client': self.http_client,
            'client_registry': self._client_registry,
        }

    def actor(self, actor_id: str) -> ActorClientAsync:
        """Get the sub-client for a specific Actor.

        Args:
            actor_id: ID of the Actor to be manipulated.
        """
        return ActorClientAsync(resource_id=actor_id, **self._base_kwargs)

    def actors(self) -> ActorCollectionClientAsync:
        """Get the sub-client for the Actor collection, allowing to list and create Actors."""
        return ActorCollectionClientAsync(**self._base_kwargs)

    def build(self, build_id: str) -> BuildClientAsync:
        """Get the sub-client for a specific Actor build.

        Args:
            build_id: ID of the Actor build to be manipulated.
        """
        return BuildClientAsync(resource_id=build_id, **self._base_kwargs)

    def builds(self) -> BuildCollectionClientAsync:
        """Get the sub-client for the build collection, allowing to list builds."""
        return BuildCollectionClientAsync(**self._base_kwargs)

    def run(self, run_id: str) -> RunClientAsync:
        """Get the sub-client for a specific Actor run.

        Args:
            run_id: ID of the Actor run to be manipulated.
        """
        return RunClientAsync(resource_id=run_id, **self._base_kwargs)

    def runs(self) -> RunCollectionClientAsync:
        """Get the sub-client for the run collection, allowing to list Actor runs."""
        return RunCollectionClientAsync(**self._base_kwargs)

    def dataset(self, dataset_id: str) -> DatasetClientAsync:
        """Get the sub-client for a specific dataset.

        Args:
            dataset_id: ID of the dataset to be manipulated.
        """
        return DatasetClientAsync(resource_id=dataset_id, **self._base_kwargs)

    def datasets(self) -> DatasetCollectionClientAsync:
        """Get the sub-client for the dataset collection, allowing to list and create datasets."""
        return DatasetCollectionClientAsync(**self._base_kwargs)

    def key_value_store(self, key_value_store_id: str) -> KeyValueStoreClientAsync:
        """Get the sub-client for a specific key-value store.

        Args:
            key_value_store_id: ID of the key-value store to be manipulated.
        """
        return KeyValueStoreClientAsync(resource_id=key_value_store_id, **self._base_kwargs)

    def key_value_stores(self) -> KeyValueStoreCollectionClientAsync:
        """Get the sub-client for the key-value store collection, allowing to list and create key-value stores."""
        return KeyValueStoreCollectionClientAsync(**self._base_kwargs)

    def request_queue(self, request_queue_id: str, *, client_key: str | None = None) -> RequestQueueClientAsync:
        """Get the sub-client for a specific request queue.

        Args:
            request_queue_id: ID of the request queue to be manipulated.
            client_key: A unique identifier of the client accessing the request queue.
        """
        return RequestQueueClientAsync(resource_id=request_queue_id, client_key=client_key, **self._base_kwargs)

    def request_queues(self) -> RequestQueueCollectionClientAsync:
        """Get the sub-client for the request queue collection, allowing to list and create request queues."""
        return RequestQueueCollectionClientAsync(**self._base_kwargs)

    def webhook(self, webhook_id: str) -> WebhookClientAsync:
        """Get the sub-client for a specific webhook.

        Args:
            webhook_id: ID of the webhook to be manipulated.
        """
        return WebhookClientAsync(resource_id=webhook_id, **self._base_kwargs)

    def webhooks(self) -> WebhookCollectionClientAsync:
        """Get the sub-client for the webhook collection, allowing to list and create webhooks."""
        return WebhookCollectionClientAsync(**self._base_kwargs)

    def webhook_dispatch(self, webhook_dispatch_id: str) -> WebhookDispatchClientAsync:
        """Get the sub-client for a specific webhook dispatch.

        Args:
            webhook_dispatch_id: ID of the webhook dispatch to access.
        """
        return WebhookDispatchClientAsync(resource_id=webhook_dispatch_id, **self._base_kwargs)

    def webhook_dispatches(self) -> WebhookDispatchCollectionClientAsync:
        """Get the sub-client for the webhook dispatch collection, allowing to list webhook dispatches."""
        return WebhookDispatchCollectionClientAsync(**self._base_kwargs)

    def schedule(self, schedule_id: str) -> ScheduleClientAsync:
        """Get the sub-client for a specific schedule.

        Args:
            schedule_id: ID of the schedule to be manipulated.
        """
        return ScheduleClientAsync(resource_id=schedule_id, **self._base_kwargs)

    def schedules(self) -> ScheduleCollectionClientAsync:
        """Get the sub-client for the schedule collection, allowing to list and create schedules."""
        return ScheduleCollectionClientAsync(**self._base_kwargs)

    def log(self, build_or_run_id: str) -> LogClientAsync:
        """Get the sub-client for retrieving logs of an Actor build or run.

        Args:
            build_or_run_id: ID of the Actor build or run for which to access the log.
        """
        return LogClientAsync(resource_id=build_or_run_id, **self._base_kwargs)

    def task(self, task_id: str) -> TaskClientAsync:
        """Get the sub-client for a specific Actor task.

        Args:
            task_id: ID of the task to be manipulated.
        """
        return TaskClientAsync(resource_id=task_id, **self._base_kwargs)

    def tasks(self) -> TaskCollectionClientAsync:
        """Get the sub-client for the task collection, allowing to list and create Actor tasks."""
        return TaskCollectionClientAsync(**self._base_kwargs)

    def user(self, user_id: str | None = None) -> UserClientAsync:
        """Get the sub-client for querying user data.

        Args:
            user_id: ID of user to be queried. If None, queries the user belonging to the token supplied to the client.
        """
        return UserClientAsync(resource_id=user_id, **self._base_kwargs)

    def store(self) -> StoreCollectionClientAsync:
        """Get the sub-client for the Apify Store, allowing to list Actors published in the store."""
        return StoreCollectionClientAsync(**self._base_kwargs)

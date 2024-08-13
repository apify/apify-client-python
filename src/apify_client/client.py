from __future__ import annotations

from apify_shared.utils import ignore_docs

from apify_client._http_client import HTTPClient, HTTPClientAsync
from apify_client.clients import (
    ActorClient,
    ActorClientAsync,
    ActorCollectionClient,
    ActorCollectionClientAsync,
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

DEFAULT_API_URL = 'https://api.apify.com'
API_VERSION = 'v2'


class _BaseApifyClient:
    http_client: HTTPClient | HTTPClientAsync

    @ignore_docs
    def __init__(
        self: _BaseApifyClient,
        token: str | None = None,
        *,
        api_url: str | None = None,
        max_retries: int | None = 8,
        min_delay_between_retries_millis: int | None = 500,
        timeout_secs: int | None = 360,
    ) -> None:
        """Initialize the Apify API Client.

        Args:
            token (str, optional): The Apify API token
            api_url (str, optional): The URL of the Apify API server to which to connect to. Defaults to https://api.apify.com
            max_retries (int, optional): How many times to retry a failed request at most
            min_delay_between_retries_millis (int, optional): How long will the client wait between retrying requests
                (increases exponentially from this value)
            timeout_secs (int, optional): The socket timeout of the HTTP requests sent to the Apify API
        """
        self.token = token
        api_url = (api_url or DEFAULT_API_URL).rstrip('/')
        self.base_url = f'{api_url}/{API_VERSION}'
        self.max_retries = max_retries or 8
        self.min_delay_between_retries_millis = min_delay_between_retries_millis or 500
        self.timeout_secs = timeout_secs or 360

    def _options(self: _BaseApifyClient) -> dict:
        return {
            'root_client': self,
            'base_url': self.base_url,
            'http_client': self.http_client,
        }


class ApifyClient(_BaseApifyClient):
    """The Apify API client."""

    http_client: HTTPClient

    def __init__(
        self: ApifyClient,
        token: str | None = None,
        *,
        api_url: str | None = None,
        max_retries: int | None = 8,
        min_delay_between_retries_millis: int | None = 500,
        timeout_secs: int | None = 360,
    ) -> None:
        """Initialize the ApifyClient.

        Args:
            token (str, optional): The Apify API token
            api_url (str, optional): The URL of the Apify API server to which to connect to. Defaults to https://api.apify.com
            max_retries (int, optional): How many times to retry a failed request at most
            min_delay_between_retries_millis (int, optional): How long will the client wait between retrying requests
                (increases exponentially from this value)
            timeout_secs (int, optional): The socket timeout of the HTTP requests sent to the Apify API
        """
        super().__init__(
            token,
            api_url=api_url,
            max_retries=max_retries,
            min_delay_between_retries_millis=min_delay_between_retries_millis,
            timeout_secs=timeout_secs,
        )

        self.http_client = HTTPClient(
            token=token,
            max_retries=self.max_retries,
            min_delay_between_retries_millis=self.min_delay_between_retries_millis,
            timeout_secs=self.timeout_secs,
        )

    def actor(self: ApifyClient, actor_id: str) -> ActorClient:
        """Retrieve the sub-client for manipulating a single Actor.

        Args:
            actor_id (str): ID of the Actor to be manipulated
        """
        return ActorClient(resource_id=actor_id, **self._options())

    def actors(self: ApifyClient) -> ActorCollectionClient:
        """Retrieve the sub-client for manipulating Actors."""
        return ActorCollectionClient(**self._options())

    def build(self: ApifyClient, build_id: str) -> BuildClient:
        """Retrieve the sub-client for manipulating a single Actor build.

        Args:
            build_id (str): ID of the Actor build to be manipulated
        """
        return BuildClient(resource_id=build_id, **self._options())

    def builds(self: ApifyClient) -> BuildCollectionClient:
        """Retrieve the sub-client for querying multiple builds of a user."""
        return BuildCollectionClient(**self._options())

    def run(self: ApifyClient, run_id: str) -> RunClient:
        """Retrieve the sub-client for manipulating a single Actor run.

        Args:
            run_id (str): ID of the Actor run to be manipulated
        """
        return RunClient(resource_id=run_id, **self._options())

    def runs(self: ApifyClient) -> RunCollectionClient:
        """Retrieve the sub-client for querying multiple Actor runs of a user."""
        return RunCollectionClient(**self._options())

    def dataset(self: ApifyClient, dataset_id: str) -> DatasetClient:
        """Retrieve the sub-client for manipulating a single dataset.

        Args:
            dataset_id (str): ID of the dataset to be manipulated
        """
        return DatasetClient(resource_id=dataset_id, **self._options())

    def datasets(self: ApifyClient) -> DatasetCollectionClient:
        """Retrieve the sub-client for manipulating datasets."""
        return DatasetCollectionClient(**self._options())

    def key_value_store(self: ApifyClient, key_value_store_id: str) -> KeyValueStoreClient:
        """Retrieve the sub-client for manipulating a single key-value store.

        Args:
            key_value_store_id (str): ID of the key-value store to be manipulated
        """
        return KeyValueStoreClient(resource_id=key_value_store_id, **self._options())

    def key_value_stores(self: ApifyClient) -> KeyValueStoreCollectionClient:
        """Retrieve the sub-client for manipulating key-value stores."""
        return KeyValueStoreCollectionClient(**self._options())

    def request_queue(self: ApifyClient, request_queue_id: str, *, client_key: str | None = None) -> RequestQueueClient:
        """Retrieve the sub-client for manipulating a single request queue.

        Args:
            request_queue_id (str): ID of the request queue to be manipulated
            client_key (str): A unique identifier of the client accessing the request queue
        """
        return RequestQueueClient(resource_id=request_queue_id, client_key=client_key, **self._options())

    def request_queues(self: ApifyClient) -> RequestQueueCollectionClient:
        """Retrieve the sub-client for manipulating request queues."""
        return RequestQueueCollectionClient(**self._options())

    def webhook(self: ApifyClient, webhook_id: str) -> WebhookClient:
        """Retrieve the sub-client for manipulating a single webhook.

        Args:
            webhook_id (str): ID of the webhook to be manipulated
        """
        return WebhookClient(resource_id=webhook_id, **self._options())

    def webhooks(self: ApifyClient) -> WebhookCollectionClient:
        """Retrieve the sub-client for querying multiple webhooks of a user."""
        return WebhookCollectionClient(**self._options())

    def webhook_dispatch(self: ApifyClient, webhook_dispatch_id: str) -> WebhookDispatchClient:
        """Retrieve the sub-client for accessing a single webhook dispatch.

        Args:
            webhook_dispatch_id (str): ID of the webhook dispatch to access
        """
        return WebhookDispatchClient(resource_id=webhook_dispatch_id, **self._options())

    def webhook_dispatches(self: ApifyClient) -> WebhookDispatchCollectionClient:
        """Retrieve the sub-client for querying multiple webhook dispatches of a user."""
        return WebhookDispatchCollectionClient(**self._options())

    def schedule(self: ApifyClient, schedule_id: str) -> ScheduleClient:
        """Retrieve the sub-client for manipulating a single schedule.

        Args:
            schedule_id (str): ID of the schedule to be manipulated
        """
        return ScheduleClient(resource_id=schedule_id, **self._options())

    def schedules(self: ApifyClient) -> ScheduleCollectionClient:
        """Retrieve the sub-client for manipulating schedules."""
        return ScheduleCollectionClient(**self._options())

    def log(self: ApifyClient, build_or_run_id: str) -> LogClient:
        """Retrieve the sub-client for retrieving logs.

        Args:
            build_or_run_id (str): ID of the Actor build or run for which to access the log
        """
        return LogClient(resource_id=build_or_run_id, **self._options())

    def task(self: ApifyClient, task_id: str) -> TaskClient:
        """Retrieve the sub-client for manipulating a single task.

        Args:
            task_id (str): ID of the task to be manipulated
        """
        return TaskClient(resource_id=task_id, **self._options())

    def tasks(self: ApifyClient) -> TaskCollectionClient:
        """Retrieve the sub-client for manipulating tasks."""
        return TaskCollectionClient(**self._options())

    def user(self: ApifyClient, user_id: str | None = None) -> UserClient:
        """Retrieve the sub-client for querying users.

        Args:
            user_id (str, optional): ID of user to be queried. If None, queries the user belonging to the token supplied to the client
        """
        return UserClient(resource_id=user_id, **self._options())

    def store(self: ApifyClient) -> StoreCollectionClient:
        """Retrieve the sub-client for Apify store."""
        return StoreCollectionClient(**self._options())


class ApifyClientAsync(_BaseApifyClient):
    """The asynchronous version of the Apify API client."""

    http_client: HTTPClientAsync

    def __init__(
        self: ApifyClientAsync,
        token: str | None = None,
        *,
        api_url: str | None = None,
        max_retries: int | None = 8,
        min_delay_between_retries_millis: int | None = 500,
        timeout_secs: int | None = 360,
    ) -> None:
        """Initialize the ApifyClientAsync.

        Args:
            token (str, optional): The Apify API token
            api_url (str, optional): The URL of the Apify API server to which to connect to. Defaults to https://api.apify.com
            max_retries (int, optional): How many times to retry a failed request at most
            min_delay_between_retries_millis (int, optional): How long will the client wait between retrying requests
                (increases exponentially from this value)
            timeout_secs (int, optional): The socket timeout of the HTTP requests sent to the Apify API
        """
        super().__init__(
            token,
            api_url=api_url,
            max_retries=max_retries,
            min_delay_between_retries_millis=min_delay_between_retries_millis,
            timeout_secs=timeout_secs,
        )

        self.http_client = HTTPClientAsync(
            token=token,
            max_retries=self.max_retries,
            min_delay_between_retries_millis=self.min_delay_between_retries_millis,
            timeout_secs=self.timeout_secs,
        )

    def actor(self: ApifyClientAsync, actor_id: str) -> ActorClientAsync:
        """Retrieve the sub-client for manipulating a single Actor.

        Args:
            actor_id (str): ID of the Actor to be manipulated
        """
        return ActorClientAsync(resource_id=actor_id, **self._options())

    def actors(self: ApifyClientAsync) -> ActorCollectionClientAsync:
        """Retrieve the sub-client for manipulating Actors."""
        return ActorCollectionClientAsync(**self._options())

    def build(self: ApifyClientAsync, build_id: str) -> BuildClientAsync:
        """Retrieve the sub-client for manipulating a single Actor build.

        Args:
            build_id (str): ID of the Actor build to be manipulated
        """
        return BuildClientAsync(resource_id=build_id, **self._options())

    def builds(self: ApifyClientAsync) -> BuildCollectionClientAsync:
        """Retrieve the sub-client for querying multiple builds of a user."""
        return BuildCollectionClientAsync(**self._options())

    def run(self: ApifyClientAsync, run_id: str) -> RunClientAsync:
        """Retrieve the sub-client for manipulating a single Actor run.

        Args:
            run_id (str): ID of the Actor run to be manipulated
        """
        return RunClientAsync(resource_id=run_id, **self._options())

    def runs(self: ApifyClientAsync) -> RunCollectionClientAsync:
        """Retrieve the sub-client for querying multiple Actor runs of a user."""
        return RunCollectionClientAsync(**self._options())

    def dataset(self: ApifyClientAsync, dataset_id: str) -> DatasetClientAsync:
        """Retrieve the sub-client for manipulating a single dataset.

        Args:
            dataset_id (str): ID of the dataset to be manipulated
        """
        return DatasetClientAsync(resource_id=dataset_id, **self._options())

    def datasets(self: ApifyClientAsync) -> DatasetCollectionClientAsync:
        """Retrieve the sub-client for manipulating datasets."""
        return DatasetCollectionClientAsync(**self._options())

    def key_value_store(self: ApifyClientAsync, key_value_store_id: str) -> KeyValueStoreClientAsync:
        """Retrieve the sub-client for manipulating a single key-value store.

        Args:
            key_value_store_id (str): ID of the key-value store to be manipulated
        """
        return KeyValueStoreClientAsync(resource_id=key_value_store_id, **self._options())

    def key_value_stores(self: ApifyClientAsync) -> KeyValueStoreCollectionClientAsync:
        """Retrieve the sub-client for manipulating key-value stores."""
        return KeyValueStoreCollectionClientAsync(**self._options())

    def request_queue(self: ApifyClientAsync, request_queue_id: str, *, client_key: str | None = None) -> RequestQueueClientAsync:
        """Retrieve the sub-client for manipulating a single request queue.

        Args:
            request_queue_id (str): ID of the request queue to be manipulated
            client_key (str): A unique identifier of the client accessing the request queue
        """
        return RequestQueueClientAsync(resource_id=request_queue_id, client_key=client_key, **self._options())

    def request_queues(self: ApifyClientAsync) -> RequestQueueCollectionClientAsync:
        """Retrieve the sub-client for manipulating request queues."""
        return RequestQueueCollectionClientAsync(**self._options())

    def webhook(self: ApifyClientAsync, webhook_id: str) -> WebhookClientAsync:
        """Retrieve the sub-client for manipulating a single webhook.

        Args:
            webhook_id (str): ID of the webhook to be manipulated
        """
        return WebhookClientAsync(resource_id=webhook_id, **self._options())

    def webhooks(self: ApifyClientAsync) -> WebhookCollectionClientAsync:
        """Retrieve the sub-client for querying multiple webhooks of a user."""
        return WebhookCollectionClientAsync(**self._options())

    def webhook_dispatch(self: ApifyClientAsync, webhook_dispatch_id: str) -> WebhookDispatchClientAsync:
        """Retrieve the sub-client for accessing a single webhook dispatch.

        Args:
            webhook_dispatch_id (str): ID of the webhook dispatch to access
        """
        return WebhookDispatchClientAsync(resource_id=webhook_dispatch_id, **self._options())

    def webhook_dispatches(self: ApifyClientAsync) -> WebhookDispatchCollectionClientAsync:
        """Retrieve the sub-client for querying multiple webhook dispatches of a user."""
        return WebhookDispatchCollectionClientAsync(**self._options())

    def schedule(self: ApifyClientAsync, schedule_id: str) -> ScheduleClientAsync:
        """Retrieve the sub-client for manipulating a single schedule.

        Args:
            schedule_id (str): ID of the schedule to be manipulated
        """
        return ScheduleClientAsync(resource_id=schedule_id, **self._options())

    def schedules(self: ApifyClientAsync) -> ScheduleCollectionClientAsync:
        """Retrieve the sub-client for manipulating schedules."""
        return ScheduleCollectionClientAsync(**self._options())

    def log(self: ApifyClientAsync, build_or_run_id: str) -> LogClientAsync:
        """Retrieve the sub-client for retrieving logs.

        Args:
            build_or_run_id (str): ID of the Actor build or run for which to access the log
        """
        return LogClientAsync(resource_id=build_or_run_id, **self._options())

    def task(self: ApifyClientAsync, task_id: str) -> TaskClientAsync:
        """Retrieve the sub-client for manipulating a single task.

        Args:
            task_id (str): ID of the task to be manipulated
        """
        return TaskClientAsync(resource_id=task_id, **self._options())

    def tasks(self: ApifyClientAsync) -> TaskCollectionClientAsync:
        """Retrieve the sub-client for manipulating tasks."""
        return TaskCollectionClientAsync(**self._options())

    def user(self: ApifyClientAsync, user_id: str | None = None) -> UserClientAsync:
        """Retrieve the sub-client for querying users.

        Args:
            user_id (str, optional): ID of user to be queried. If None, queries the user belonging to the token supplied to the client
        """
        return UserClientAsync(resource_id=user_id, **self._options())

    def store(self: ApifyClientAsync) -> StoreCollectionClientAsync:
        """Retrieve the sub-client for Apify store."""
        return StoreCollectionClientAsync(**self._options())

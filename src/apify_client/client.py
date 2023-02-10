from typing import Dict, Optional, Union

from ._http_client import _HTTPClient, _HTTPClientAsync
from ._utils import ignore_docs
from .clients import (
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
    http_client: Union[_HTTPClient, _HTTPClientAsync]

    @ignore_docs
    def __init__(
        self,
        token: Optional[str] = None,
        *,
        api_url: Optional[str] = None,
        max_retries: Optional[int] = 8,
        min_delay_between_retries_millis: Optional[int] = 500,
        timeout_secs: Optional[int] = 360,
    ):
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

    def _options(self) -> Dict:
        return {
            'root_client': self,
            'base_url': self.base_url,
            'http_client': self.http_client,
        }


class ApifyClient(_BaseApifyClient):
    """The Apify API client."""

    http_client: _HTTPClient

    def __init__(
        self,
        token: Optional[str] = None,
        *,
        api_url: Optional[str] = None,
        max_retries: Optional[int] = 8,
        min_delay_between_retries_millis: Optional[int] = 500,
        timeout_secs: Optional[int] = 360,
    ):
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

        self.http_client = _HTTPClient(
            token=token,
            max_retries=self.max_retries,
            min_delay_between_retries_millis=self.min_delay_between_retries_millis,
            timeout_secs=self.timeout_secs,
        )

    def actor(self, actor_id: str) -> ActorClient:
        """Retrieve the sub-client for manipulating a single actor.

        Args:
            actor_id (str): ID of the actor to be manipulated
        """
        return ActorClient(resource_id=actor_id, **self._options())

    def actors(self) -> ActorCollectionClient:
        """Retrieve the sub-client for manipulating actors."""
        return ActorCollectionClient(**self._options())

    def build(self, build_id: str) -> BuildClient:
        """Retrieve the sub-client for manipulating a single actor build.

        Args:
            build_id (str): ID of the actor build to be manipulated
        """
        return BuildClient(resource_id=build_id, **self._options())

    def builds(self) -> BuildCollectionClient:
        """Retrieve the sub-client for querying multiple builds of a user."""
        return BuildCollectionClient(**self._options())

    def run(self, run_id: str) -> RunClient:
        """Retrieve the sub-client for manipulating a single actor run.

        Args:
            run_id (str): ID of the actor run to be manipulated
        """
        return RunClient(resource_id=run_id, **self._options())

    def runs(self) -> RunCollectionClient:
        """Retrieve the sub-client for querying multiple actor runs of a user."""
        return RunCollectionClient(**self._options())

    def dataset(self, dataset_id: str) -> DatasetClient:
        """Retrieve the sub-client for manipulating a single dataset.

        Args:
            dataset_id (str): ID of the dataset to be manipulated
        """
        return DatasetClient(resource_id=dataset_id, **self._options())

    def datasets(self) -> DatasetCollectionClient:
        """Retrieve the sub-client for manipulating datasets."""
        return DatasetCollectionClient(**self._options())

    def key_value_store(self, key_value_store_id: str) -> KeyValueStoreClient:
        """Retrieve the sub-client for manipulating a single key-value store.

        Args:
            key_value_store_id (str): ID of the key-value store to be manipulated
        """
        return KeyValueStoreClient(resource_id=key_value_store_id, **self._options())

    def key_value_stores(self) -> KeyValueStoreCollectionClient:
        """Retrieve the sub-client for manipulating key-value stores."""
        return KeyValueStoreCollectionClient(**self._options())

    def request_queue(self, request_queue_id: str, *, client_key: Optional[str] = None) -> RequestQueueClient:
        """Retrieve the sub-client for manipulating a single request queue.

        Args:
            request_queue_id (str): ID of the request queue to be manipulated
            client_key (str): A unique identifier of the client accessing the request queue
        """
        return RequestQueueClient(resource_id=request_queue_id, client_key=client_key, **self._options())

    def request_queues(self) -> RequestQueueCollectionClient:
        """Retrieve the sub-client for manipulating request queues."""
        return RequestQueueCollectionClient(**self._options())

    def webhook(self, webhook_id: str) -> WebhookClient:
        """Retrieve the sub-client for manipulating a single webhook.

        Args:
            webhook_id (str): ID of the webhook to be manipulated
        """
        return WebhookClient(resource_id=webhook_id, **self._options())

    def webhooks(self) -> WebhookCollectionClient:
        """Retrieve the sub-client for querying multiple webhooks of a user."""
        return WebhookCollectionClient(**self._options())

    def webhook_dispatch(self, webhook_dispatch_id: str) -> WebhookDispatchClient:
        """Retrieve the sub-client for accessing a single webhook dispatch.

        Args:
            webhook_dispatch_id (str): ID of the webhook dispatch to access
        """
        return WebhookDispatchClient(resource_id=webhook_dispatch_id, **self._options())

    def webhook_dispatches(self) -> WebhookDispatchCollectionClient:
        """Retrieve the sub-client for querying multiple webhook dispatches of a user."""
        return WebhookDispatchCollectionClient(**self._options())

    def schedule(self, schedule_id: str) -> ScheduleClient:
        """Retrieve the sub-client for manipulating a single schedule.

        Args:
            schedule_id (str): ID of the schedule to be manipulated
        """
        return ScheduleClient(resource_id=schedule_id, **self._options())

    def schedules(self) -> ScheduleCollectionClient:
        """Retrieve the sub-client for manipulating schedules."""
        return ScheduleCollectionClient(**self._options())

    def log(self, build_or_run_id: str) -> LogClient:
        """Retrieve the sub-client for retrieving logs.

        Args:
            build_or_run_id (str): ID of the actor build or run for which to access the log
        """
        return LogClient(resource_id=build_or_run_id, **self._options())

    def task(self, task_id: str) -> TaskClient:
        """Retrieve the sub-client for manipulating a single task.

        Args:
            task_id (str): ID of the task to be manipulated
        """
        return TaskClient(resource_id=task_id, **self._options())

    def tasks(self) -> TaskCollectionClient:
        """Retrieve the sub-client for manipulating tasks."""
        return TaskCollectionClient(**self._options())

    def user(self, user_id: Optional[str] = None) -> UserClient:
        """Retrieve the sub-client for querying users.

        Args:
            user_id (str, optional): ID of user to be queried. If None, queries the user belonging to the token supplied to the client
        """
        return UserClient(resource_id=user_id, **self._options())


class ApifyClientAsync(_BaseApifyClient):
    """The asynchronous version of the Apify API client."""

    http_client: _HTTPClientAsync

    def __init__(
        self,
        token: Optional[str] = None,
        *,
        api_url: Optional[str] = None,
        max_retries: Optional[int] = 8,
        min_delay_between_retries_millis: Optional[int] = 500,
        timeout_secs: Optional[int] = 360,
    ):
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

        self.http_client = _HTTPClientAsync(
            token=token,
            max_retries=self.max_retries,
            min_delay_between_retries_millis=self.min_delay_between_retries_millis,
            timeout_secs=self.timeout_secs,
        )

    def actor(self, actor_id: str) -> ActorClientAsync:
        """Retrieve the sub-client for manipulating a single actor.

        Args:
            actor_id (str): ID of the actor to be manipulated
        """
        return ActorClientAsync(resource_id=actor_id, **self._options())

    def actors(self) -> ActorCollectionClientAsync:
        """Retrieve the sub-client for manipulating actors."""
        return ActorCollectionClientAsync(**self._options())

    def build(self, build_id: str) -> BuildClientAsync:
        """Retrieve the sub-client for manipulating a single actor build.

        Args:
            build_id (str): ID of the actor build to be manipulated
        """
        return BuildClientAsync(resource_id=build_id, **self._options())

    def builds(self) -> BuildCollectionClientAsync:
        """Retrieve the sub-client for querying multiple builds of a user."""
        return BuildCollectionClientAsync(**self._options())

    def run(self, run_id: str) -> RunClientAsync:
        """Retrieve the sub-client for manipulating a single actor run.

        Args:
            run_id (str): ID of the actor run to be manipulated
        """
        return RunClientAsync(resource_id=run_id, **self._options())

    def runs(self) -> RunCollectionClientAsync:
        """Retrieve the sub-client for querying multiple actor runs of a user."""
        return RunCollectionClientAsync(**self._options())

    def dataset(self, dataset_id: str) -> DatasetClientAsync:
        """Retrieve the sub-client for manipulating a single dataset.

        Args:
            dataset_id (str): ID of the dataset to be manipulated
        """
        return DatasetClientAsync(resource_id=dataset_id, **self._options())

    def datasets(self) -> DatasetCollectionClientAsync:
        """Retrieve the sub-client for manipulating datasets."""
        return DatasetCollectionClientAsync(**self._options())

    def key_value_store(self, key_value_store_id: str) -> KeyValueStoreClientAsync:
        """Retrieve the sub-client for manipulating a single key-value store.

        Args:
            key_value_store_id (str): ID of the key-value store to be manipulated
        """
        return KeyValueStoreClientAsync(resource_id=key_value_store_id, **self._options())

    def key_value_stores(self) -> KeyValueStoreCollectionClientAsync:
        """Retrieve the sub-client for manipulating key-value stores."""
        return KeyValueStoreCollectionClientAsync(**self._options())

    def request_queue(self, request_queue_id: str, *, client_key: Optional[str] = None) -> RequestQueueClientAsync:
        """Retrieve the sub-client for manipulating a single request queue.

        Args:
            request_queue_id (str): ID of the request queue to be manipulated
            client_key (str): A unique identifier of the client accessing the request queue
        """
        return RequestQueueClientAsync(resource_id=request_queue_id, client_key=client_key, **self._options())

    def request_queues(self) -> RequestQueueCollectionClientAsync:
        """Retrieve the sub-client for manipulating request queues."""
        return RequestQueueCollectionClientAsync(**self._options())

    def webhook(self, webhook_id: str) -> WebhookClientAsync:
        """Retrieve the sub-client for manipulating a single webhook.

        Args:
            webhook_id (str): ID of the webhook to be manipulated
        """
        return WebhookClientAsync(resource_id=webhook_id, **self._options())

    def webhooks(self) -> WebhookCollectionClientAsync:
        """Retrieve the sub-client for querying multiple webhooks of a user."""
        return WebhookCollectionClientAsync(**self._options())

    def webhook_dispatch(self, webhook_dispatch_id: str) -> WebhookDispatchClientAsync:
        """Retrieve the sub-client for accessing a single webhook dispatch.

        Args:
            webhook_dispatch_id (str): ID of the webhook dispatch to access
        """
        return WebhookDispatchClientAsync(resource_id=webhook_dispatch_id, **self._options())

    def webhook_dispatches(self) -> WebhookDispatchCollectionClientAsync:
        """Retrieve the sub-client for querying multiple webhook dispatches of a user."""
        return WebhookDispatchCollectionClientAsync(**self._options())

    def schedule(self, schedule_id: str) -> ScheduleClientAsync:
        """Retrieve the sub-client for manipulating a single schedule.

        Args:
            schedule_id (str): ID of the schedule to be manipulated
        """
        return ScheduleClientAsync(resource_id=schedule_id, **self._options())

    def schedules(self) -> ScheduleCollectionClientAsync:
        """Retrieve the sub-client for manipulating schedules."""
        return ScheduleCollectionClientAsync(**self._options())

    def log(self, build_or_run_id: str) -> LogClientAsync:
        """Retrieve the sub-client for retrieving logs.

        Args:
            build_or_run_id (str): ID of the actor build or run for which to access the log
        """
        return LogClientAsync(resource_id=build_or_run_id, **self._options())

    def task(self, task_id: str) -> TaskClientAsync:
        """Retrieve the sub-client for manipulating a single task.

        Args:
            task_id (str): ID of the task to be manipulated
        """
        return TaskClientAsync(resource_id=task_id, **self._options())

    def tasks(self) -> TaskCollectionClientAsync:
        """Retrieve the sub-client for manipulating tasks."""
        return TaskCollectionClientAsync(**self._options())

    def user(self, user_id: Optional[str] = None) -> UserClientAsync:
        """Retrieve the sub-client for querying users.

        Args:
            user_id (str, optional): ID of user to be queried. If None, queries the user belonging to the token supplied to the client
        """
        return UserClientAsync(resource_id=user_id, **self._options())

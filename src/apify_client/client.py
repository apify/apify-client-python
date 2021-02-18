from typing import Dict, Optional

from ._http_client import _HTTPClient
from .clients.resource_clients.build import BuildClient
from .clients.resource_clients.build_collection import BuildCollectionClient
from .clients.resource_clients.dataset import DatasetClient
from .clients.resource_clients.dataset_collection import DatasetCollectionClient
from .clients.resource_clients.key_value_store import KeyValueStoreClient
from .clients.resource_clients.key_value_store_collection import KeyValueStoreCollectionClient
from .clients.resource_clients.log import LogClient
from .clients.resource_clients.request_queue import RequestQueueClient
from .clients.resource_clients.request_queue_collection import RequestQueueCollectionClient
from .clients.resource_clients.schedule import ScheduleClient
from .clients.resource_clients.schedule_collection import ScheduleCollectionClient
from .clients.resource_clients.task import TaskClient
from .clients.resource_clients.task_collection import TaskCollectionClient
from .clients.resource_clients.user import UserClient
from .clients.resource_clients.webhook import WebhookClient
from .clients.resource_clients.webhook_collection import WebhookCollectionClient
from .clients.resource_clients.webhook_dispatch import WebhookDispatchClient
from .clients.resource_clients.webhook_dispatch_collection import WebhookDispatchCollectionClient

DEFAULT_BASE_API_URL = 'https://api.apify.com/v2'


class ApifyClient:
    """The Apify API client."""

    def __init__(
        self,
        token: Optional[str] = None,
        *,
        base_url: str = DEFAULT_BASE_API_URL,
        max_retries: int = 8,
        min_delay_between_retries_millis: int = 500,
    ):
        """Initialize the Apify API Client.

        Args:
            token: The Apify API token
            base_url: The URL of the Apify API server to which to connect to. Defaults to https://api.apify.com/v2
            max_retries: How many times to retry a failed request at most
            min_delay_between_retries_millis: How long will the client wait between retrying requests (increases exponentially from this value)
        """
        self.token = token
        self.base_url = base_url
        self.max_retries = max_retries
        self.min_delay_between_retries_millis = min_delay_between_retries_millis

        self.http_client = _HTTPClient(max_retries=max_retries, min_delay_between_retries_millis=min_delay_between_retries_millis)
        # TODO statistics
        # TODO logger

    def _options(self) -> Dict:
        return {
            'base_url': self.base_url,
            'http_client': self.http_client,
            'params': {
                'token': self.token,
            },
        }

    def build(self, build_id: str) -> BuildClient:
        """Retrieve the sub-client for manipulating a single actor build.

        Args:
            build_id (str): ID of the actor build to be manipulated
        """
        return BuildClient(resource_id=build_id, **self._options())

    def builds(self) -> BuildCollectionClient:
        """Retrieve the sub-client for querying multiple builds of a user."""
        return BuildCollectionClient(**self._options())

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
            request_queue_id (str) : ID of the request queue to be manipulated
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
            schedule_id (str) : ID of the schedule to be manipulated
        """
        return ScheduleClient(resource_id=schedule_id, **self._options())

    def schedules(self) -> ScheduleCollectionClient:
        """Retrieve the sub-client for manipulating schedules."""
        return ScheduleCollectionClient(**self._options())

    def log(self, build_or_run_id: str) -> LogClient:
        """Retrieve the sub-client for retrieving logs."""
        return LogClient(resource_id=build_or_run_id, **self._options())

    def task(self, task_id: str) -> TaskClient:
        """Retrieve the sub-client for manipulating a single task."""
        return TaskClient(resource_id=task_id, **self._options())

    def tasks(self) -> TaskCollectionClient:
        """Retrieve the sub-client for retrieving tasks."""
        return TaskCollectionClient(**self._options())

    def user(self, user_id: str) -> UserClient:
        """Retrieve the sub-client for querying users."""
        return UserClient(resource_id=user_id, **self._options())

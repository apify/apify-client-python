from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Awaitable, Callable, Generator, Iterator

from apify_client._models_generated import (
    ActorShort,
    BuildShort,
    DatasetListItem,
    EnvVar,
    KeyValueStore,
    KeyValueStoreKey,
    Request,
    RequestQueueShort,
    RunShort,
    ScheduleShort,
    StoreListActor,
    TaskShort,
    Version,
    WebhookDispatch,
    WebhookShort,
)

T = TypeVar('T')


@dataclass
class IterableOf(Generic[T]):
    _get_iterator: Callable[[], Iterator[T]] = field(repr=False, compare=False)

    def __iter__(self) -> Iterator[T]:
        return self._get_iterator()


@dataclass
class AsyncIterableOf(Generic[T]):
    _get_async_iterator: Callable[[], AsyncIterator[T]] = field(repr=False, compare=False)

    def __aiter__(self) -> AsyncIterator[T]:
        return self._get_async_iterator()


@dataclass
class PageWithItems(Generic[T]):
    items: list[T]


@dataclass
class PageWithTotal:
    total: int


@dataclass
class PageWithLimit:
    limit: int


@dataclass
class PageWithCount:
    count: int


@dataclass
class PageWithOffset:
    offset: int


@dataclass
class PageWithDesc:
    desc: bool


@dataclass
class PageOfItems(PageWithItems[T], PageWithTotal, PageWithLimit, PageWithCount, PageWithOffset, PageWithDesc): ...


@dataclass
class PageOfDatasetItems(PageOfItems[dict[str, Any]]): ...


@dataclass
class PageOfItemsOnlyTotal(PageWithItems[T], PageWithTotal): ...


@dataclass
class PageOfRequests(PageWithItems[Request], PageWithLimit):
    exclusive_start_id: str | None = None
    cursor: str | None = None
    next_cursor: str | None = None


@dataclass
class PageOfKeys(PageWithItems[KeyValueStoreKey], PageWithLimit, PageWithCount):
    is_truncated: bool
    exclusive_start_key: str | None = None
    next_exclusive_start_key: str | None = None


@dataclass
class AwaitablePage(Generic[T]):
    _awaitable_first_page: Awaitable[PageOfItems[T]] = field(repr=False, compare=False)

    def __await__(self) -> Generator[Any, Any, PageOfItems[T]]:
        return self._awaitable_first_page.__await__()


@dataclass
class AwaitablePageOnlyTotal(Generic[T]):
    _awaitable_first_page: Awaitable[PageOfItemsOnlyTotal[T]] = field(repr=False, compare=False)

    def __await__(self) -> Generator[Any, Any, PageOfItemsOnlyTotal[T]]:
        return self._awaitable_first_page.__await__()


@dataclass
class AwaitablePageOfDatasetItems:
    _awaitable_first_page: Awaitable[PageOfDatasetItems] = field(repr=False, compare=False)

    def __await__(self) -> Generator[Any, Any, PageOfDatasetItems]:
        return self._awaitable_first_page.__await__()


@dataclass
class AwaitablePageOfRequests:
    _awaitable_first_page: Awaitable[PageOfRequests] = field(repr=False, compare=False)

    def __await__(self) -> Generator[Any, Any, PageOfRequests]:
        return self._awaitable_first_page.__await__()


@dataclass
class AwaitablePageOfKeys:
    _awaitable_first_page: Awaitable[PageOfKeys] = field(repr=False, compare=False)

    def __await__(self) -> Generator[Any, Any, PageOfKeys]:
        return self._awaitable_first_page.__await__()


@dataclass
class IterablePageOfActors(PageOfItems[ActorShort], IterableOf[ActorShort]): ...


@dataclass
class IterablePageOfActorsAsync(AwaitablePage[ActorShort], AsyncIterableOf[ActorShort]): ...


@dataclass
class IterablePageOfBuilds(PageOfItems[BuildShort], IterableOf[BuildShort]): ...


@dataclass
class IterablePageOfBuildsAsync(AwaitablePage[BuildShort], AsyncIterableOf[BuildShort]): ...


@dataclass
class IterablePageOfDatasets(PageOfItems[DatasetListItem], IterableOf[DatasetListItem]): ...


@dataclass
class IterablePageOfDatasetsAsync(AwaitablePage[DatasetListItem], AsyncIterableOf[DatasetListItem]): ...


@dataclass
class IterablePageOfDatasetItems(PageOfDatasetItems, IterableOf[dict[str, Any]]): ...


@dataclass
class IterablePageOfDatasetItemsAsync(AwaitablePageOfDatasetItems, AsyncIterableOf[dict[str, Any]]): ...


@dataclass
class IterablePageOfKeyValueStores(PageOfItems[KeyValueStore], IterableOf[KeyValueStore]): ...


@dataclass
class IterablePageOfKeyValueStoresAsync(AwaitablePage[KeyValueStore], AsyncIterableOf[KeyValueStore]): ...


@dataclass
class IterablePageOfRequestQueues(PageOfItems[RequestQueueShort], IterableOf[RequestQueueShort]): ...


@dataclass
class IterablePageOfRequestQueuesAsync(AwaitablePage[RequestQueueShort], AsyncIterableOf[RequestQueueShort]): ...


@dataclass
class IterablePageOfRuns(PageOfItems[RunShort], IterableOf[RunShort]): ...


@dataclass
class IterablePageOfRunsAsync(AwaitablePage[RunShort], AsyncIterableOf[RunShort]): ...


@dataclass
class IterablePageOfSchedules(PageOfItems[ScheduleShort], IterableOf[ScheduleShort]): ...


@dataclass
class IterablePageOfSchedulesAsync(AwaitablePage[ScheduleShort], AsyncIterableOf[ScheduleShort]): ...


@dataclass
class IterablePageOfStoreActors(PageOfItems[StoreListActor], IterableOf[StoreListActor]): ...


@dataclass
class IterablePageOfStoreActorsAsync(AwaitablePage[StoreListActor], AsyncIterableOf[StoreListActor]): ...


@dataclass
class IterablePageOfTasks(PageOfItems[TaskShort], IterableOf[TaskShort]): ...


@dataclass
class IterablePageOfTasksAsync(AwaitablePage[TaskShort], AsyncIterableOf[TaskShort]): ...


@dataclass
class IterablePageOfWebhookDispatches(PageOfItems[WebhookDispatch], IterableOf[WebhookDispatch]): ...


@dataclass
class IterablePageOfWebhookDispatchesAsync(AwaitablePage[WebhookDispatch], AsyncIterableOf[WebhookDispatch]): ...


@dataclass
class IterablePageOfWebhooks(PageOfItems[WebhookShort], IterableOf[WebhookShort]): ...


@dataclass
class IterablePageOfWebhooksAsync(AwaitablePage[WebhookShort], AsyncIterableOf[WebhookShort]): ...


@dataclass
class IterablePageOfEnvVars(PageOfItemsOnlyTotal, IterableOf[EnvVar]): ...


@dataclass
class IterablePageOfEnvVarsAsync(AwaitablePageOnlyTotal[EnvVar], AsyncIterableOf[EnvVar]): ...


@dataclass
class IterablePageOfVersions(PageOfItemsOnlyTotal, IterableOf[Version]): ...


@dataclass
class IterablePageOfVersionsAsync(AwaitablePageOnlyTotal[Version], AsyncIterableOf[Version]): ...


@dataclass
class IterablePageOfRequests(PageOfRequests, IterableOf[Request]): ...


@dataclass
class IterablePageOfRequestsAsync(AwaitablePageOfRequests, AsyncIterableOf[Request]): ...


@dataclass
class IterablePageOfKeys(PageOfKeys, IterableOf[KeyValueStoreKey]): ...


@dataclass
class IterablePageOfKeysAsync(AwaitablePageOfKeys, AsyncIterableOf[KeyValueStoreKey]): ...

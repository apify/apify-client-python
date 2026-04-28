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
class PageWithTotal(Generic[T]):
    total: int


@dataclass
class PageWithLimit(Generic[T]):
    limit: int


@dataclass
class PageWithCount(Generic[T]):
    count: int


@dataclass
class PageWithOffset(Generic[T]):
    offset: int


@dataclass
class PageWithDesc(Generic[T]):
    desc: int


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
class ListPageOfActors(PageOfItems[ActorShort], IterableOf[ActorShort]): ...


@dataclass
class ListPageOfActorsAsync(AsyncIterableOf[ActorShort], AwaitablePage[ActorShort]): ...


@dataclass
class ListPageOfBuilds(PageOfItems[BuildShort], IterableOf[BuildShort]): ...


@dataclass
class ListPageOfBuildsAsync(AsyncIterableOf[BuildShort], AwaitablePage[BuildShort]): ...


@dataclass
class ListPageOfDatasets(PageOfItems[DatasetListItem], IterableOf[DatasetListItem]): ...


@dataclass
class ListPageOfDatasetsAsync(AsyncIterableOf[DatasetListItem], AwaitablePage[DatasetListItem]): ...


@dataclass
class ListPageOfDatasetItems(PageOfDatasetItems, IterableOf[dict[str, Any]]): ...


@dataclass
class ListPageOfDatasetItemsAsync(AsyncIterableOf[dict[str, Any]], AwaitablePageOfDatasetItems): ...


@dataclass
class ListPageOfKeyValueStores(PageOfItems[KeyValueStore], IterableOf[KeyValueStore]): ...


@dataclass
class ListPageOfKeyValueStoresAsync(AsyncIterableOf[KeyValueStore], AwaitablePage[KeyValueStore]): ...


@dataclass
class ListPageOfRequestQueues(PageOfItems[RequestQueueShort], IterableOf[RequestQueueShort]): ...


@dataclass
class ListPageOfRequestQueuesAsync(AsyncIterableOf[RequestQueueShort], AwaitablePage[RequestQueueShort]): ...


@dataclass
class ListPageOfRuns(PageOfItems[RunShort], IterableOf[RunShort]): ...


@dataclass
class ListPageOfRunsAsync(AsyncIterableOf[RunShort], AwaitablePage[RunShort]): ...


@dataclass
class ListPageOfSchedules(PageOfItems[ScheduleShort], IterableOf[ScheduleShort]): ...


@dataclass
class ListPageOfSchedulesAsync(AsyncIterableOf[ScheduleShort], AwaitablePage[ScheduleShort]): ...


@dataclass
class ListPageOfStoreActors(PageOfItems[StoreListActor], IterableOf[StoreListActor]): ...


@dataclass
class ListPageOfStoreActorsAsync(AsyncIterableOf[StoreListActor], AwaitablePage[StoreListActor]): ...


@dataclass
class ListPageOfTasks(PageOfItems[TaskShort], IterableOf[TaskShort]): ...


@dataclass
class ListPageOfTasksAsync(AsyncIterableOf[TaskShort], AwaitablePage[TaskShort]): ...


@dataclass
class ListPageOfWebhookDispatches(PageOfItems[WebhookDispatch], IterableOf[WebhookDispatch]): ...


@dataclass
class ListPageOfWebhookDispatchesAsync(AsyncIterableOf[WebhookDispatch], AwaitablePage[WebhookDispatch]): ...


@dataclass
class ListPageOfWebhooks(PageOfItems[WebhookShort], IterableOf[WebhookShort]): ...


@dataclass
class ListPageOfWebhooksAsync(AsyncIterableOf[WebhookShort], AwaitablePage[WebhookShort]): ...


@dataclass
class ListPageOfEnvVars(IterableOf[EnvVar], PageOfItemsOnlyTotal): ...


@dataclass
class ListPageOfEnvVarsAsync(AsyncIterableOf[EnvVar], AwaitablePageOnlyTotal[EnvVar]): ...


@dataclass
class ListPageOfVersions(IterableOf[Version], PageOfItemsOnlyTotal): ...


@dataclass
class ListPageOfVersionsAsync(AsyncIterableOf[Version], AwaitablePageOnlyTotal[Version]): ...


@dataclass
class ListPageOfRequests(PageOfRequests, IterableOf[Request]): ...


@dataclass
class ListPageOfRequestsAsync(AsyncIterableOf[Request], AwaitablePageOfRequests): ...


@dataclass
class ListPageOfKeys(PageOfKeys, IterableOf[KeyValueStoreKey]): ...


@dataclass
class ListPageOfKeysAsync(AsyncIterableOf[KeyValueStoreKey], AwaitablePageOfKeys): ...

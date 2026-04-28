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
class IterablePage(Generic[T]):
    _get_iterator: Callable[[], Iterator[T]] = field(repr=False, compare=False)

    def __iter__(self) -> Iterator[T]:
        return self._get_iterator()


@dataclass
class IterablePageAsync(Generic[T]):
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
class PaginatedPage(PageWithItems[T], PageWithTotal, PageWithLimit, PageWithCount, PageWithOffset, PageWithDesc): ...


@dataclass
class PaginatedPageOnlyTotal(PageWithItems[T], PageWithTotal): ...


@dataclass
class PageOfDatasetItems(
    PageWithItems[dict[str, Any]], PageWithLimit, PageWithCount, PageWithOffset, PageWithTotal, PageWithDesc
): ...


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
    _awaitable_first_page: Awaitable[PaginatedPage[T]] = field(repr=False, compare=False)

    def __await__(self) -> Generator[Any, Any, PaginatedPage[T]]:
        return self._awaitable_first_page.__await__()


@dataclass
class AwaitablePageOnlyTotal(Generic[T]):
    _awaitable_first_page: Awaitable[PaginatedPageOnlyTotal[T]] = field(repr=False, compare=False)

    def __await__(self) -> Generator[Any, Any, PaginatedPageOnlyTotal[T]]:
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
class ListPageOfActors(PaginatedPage[ActorShort], IterablePage[ActorShort]): ...


@dataclass
class ListPageOfActorsAsync(IterablePageAsync[ActorShort], AwaitablePage[ActorShort]): ...


@dataclass
class ListPageOfBuilds(PaginatedPage[BuildShort], IterablePage[BuildShort]): ...


@dataclass
class ListPageOfBuildsAsync(IterablePageAsync[BuildShort], AwaitablePage[BuildShort]): ...


@dataclass
class ListPageOfDatasets(PaginatedPage[DatasetListItem], IterablePage[DatasetListItem]): ...


@dataclass
class ListPageOfDatasetsAsync(IterablePageAsync[DatasetListItem], AwaitablePage[DatasetListItem]): ...


@dataclass
class ListPageOfDatasetItems(PageOfDatasetItems, IterablePage[dict[str, Any]]): ...


@dataclass
class ListPageOfDatasetItemsAsync(IterablePageAsync[dict[str, Any]], AwaitablePageOfDatasetItems): ...


@dataclass
class ListPageOfKeyValueStores(PaginatedPage[KeyValueStore], IterablePage[KeyValueStore]): ...


@dataclass
class ListPageOfKeyValueStoresAsync(IterablePageAsync[KeyValueStore], AwaitablePage[KeyValueStore]): ...


@dataclass
class ListPageOfRequestQueues(PaginatedPage[RequestQueueShort], IterablePage[RequestQueueShort]): ...


@dataclass
class ListPageOfRequestQueuesAsync(IterablePageAsync[RequestQueueShort], AwaitablePage[RequestQueueShort]): ...


@dataclass
class ListPageOfRuns(PaginatedPage[RunShort], IterablePage[RunShort]): ...


@dataclass
class ListPageOfRunsAsync(IterablePageAsync[RunShort], AwaitablePage[RunShort]): ...


@dataclass
class ListPageOfSchedules(PaginatedPage[ScheduleShort], IterablePage[ScheduleShort]): ...


@dataclass
class ListPageOfSchedulesAsync(IterablePageAsync[ScheduleShort], AwaitablePage[ScheduleShort]): ...


@dataclass
class ListPageOfStoreActors(PaginatedPage[StoreListActor], IterablePage[StoreListActor]): ...


@dataclass
class ListPageOfStoreActorsAsync(IterablePageAsync[StoreListActor], AwaitablePage[StoreListActor]): ...


@dataclass
class ListPageOfTasks(PaginatedPage[TaskShort], IterablePage[TaskShort]): ...


@dataclass
class ListPageOfTasksAsync(IterablePageAsync[TaskShort], AwaitablePage[TaskShort]): ...


@dataclass
class ListPageOfWebhookDispatches(PaginatedPage[WebhookDispatch], IterablePage[WebhookDispatch]): ...


@dataclass
class ListPageOfWebhookDispatchesAsync(IterablePageAsync[WebhookDispatch], AwaitablePage[WebhookDispatch]): ...


@dataclass
class ListPageOfWebhooks(PaginatedPage[WebhookShort], IterablePage[WebhookShort]): ...


@dataclass
class ListPageOfWebhooksAsync(IterablePageAsync[WebhookShort], AwaitablePage[WebhookShort]): ...


@dataclass
class ListPageOfEnvVars(IterablePage[EnvVar], PaginatedPageOnlyTotal): ...


@dataclass
class ListPageOfEnvVarsAsync(IterablePageAsync[EnvVar], AwaitablePageOnlyTotal[EnvVar]): ...


@dataclass
class ListPageOfVersions(IterablePage[Version], PaginatedPageOnlyTotal): ...


@dataclass
class ListPageOfVersionsAsync(IterablePageAsync[Version], AwaitablePageOnlyTotal[Version]): ...


@dataclass
class ListPageOfRequests(PageOfRequests, IterablePage[Request]): ...


@dataclass
class ListPageOfRequestsAsync(IterablePageAsync[Request], AwaitablePageOfRequests): ...


@dataclass
class ListPageOfKeys(PageOfKeys, IterablePage[KeyValueStoreKey]): ...


@dataclass
class ListPageOfKeysAsync(IterablePageAsync[KeyValueStoreKey], AwaitablePageOfKeys): ...

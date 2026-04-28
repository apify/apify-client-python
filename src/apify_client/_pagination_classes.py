from __future__ import annotations

from collections.abc import Callable, Iterator, AsyncIterator, Awaitable, Generator
from dataclasses import dataclass, InitVar, field
from typing import TYPE_CHECKING, Generic, TypeVar, Self, Any

from apify_client._iterable_list_page import HasItems
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
class AwaitablePage(Generic[T]):
    _awaitable_first_page: Awaitable[PaginatedPage[T]] = field(repr=False, compare=False)

    def __await__(self) -> Generator[Any, Any, PaginatedPage[T]]:
        return self._awaitable_first_page.__await__()


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
class PaginatedPage(PageWithItems[T], PageWithTotal, PageWithLimit, PageWithCount):
    offset: int
    desc: bool

@dataclass
class PaginatedPageOnlyTotal(PageWithItems[T], PageWithTotal): ...

@dataclass
class ListPageOfActors(PaginatedPage[ActorShort], IterablePage[ActorShort]): ...

@dataclass
class ListPageOfBuilds(PaginatedPage[BuildShort], IterablePage[BuildShort]): ...

@dataclass
class ListPageOfDatasets(PaginatedPage[DatasetListItem], IterablePage[DatasetListItem]): ...

@dataclass
class ListPageOfKeyValueStores(PaginatedPage[KeyValueStore], IterablePage[KeyValueStore]): ...

@dataclass
class ListPageOfRequestQueues(PaginatedPage[RequestQueueShort], IterablePage[RequestQueueShort]): ...

@dataclass
class ListPageOfRuns(PaginatedPage[RunShort], IterablePage[RunShort]): ...

@dataclass
class ListPageOfSchedules(PaginatedPage[ScheduleShort], IterablePage[ScheduleShort]): ...

@dataclass
class ListPageOfStoreActors(PaginatedPage[StoreListActor], IterablePage[StoreListActor]): ...

@dataclass
class ListPageOfTasks(PaginatedPage[TaskShort], IterablePage[TaskShort]): ...

@dataclass
class ListPageOfWebhookDispatches(PaginatedPage[WebhookDispatch], IterablePage[WebhookDispatch]): ...

@dataclass
class ListPageOfWebhookDispatchesAsync(IterablePageAsync[WebhookDispatch], AwaitablePage[WebhookDispatch]): ...

@dataclass
class ListPageOfWebhooks(PaginatedPage[WebhookShort], IterablePage[WebhookShort]): ...

@dataclass
class ListPageOfEnvVars(IterablePage[EnvVar], PaginatedPageOnlyTotal): ...

@dataclass
class ListPageOfVersions(IterablePage[Version], PaginatedPageOnlyTotal): ...

@dataclass
class ListPageOfRequests(IterablePage[Request]):
    limit: int
    count: int | None = None
    exclusive_start_id: str | None = None
    cursor: str | None = None
    next_cursor: str | None = None

@dataclass
class ListPageOfKeys(IterablePage[KeyValueStoreKey]):
    count: int
    limit: int
    is_truncated: bool
    exclusive_start_key: str | None = None
    next_exclusive_start_key: str | None = None

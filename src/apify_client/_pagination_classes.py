from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass, InitVar, field
from typing import TYPE_CHECKING, Generic, TypeVar


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
    items: list[T]
    get_iterator: InitVar[Callable[[], Iterator[T]]]
    _get_iterator: Callable[[], Iterator[T]] = field(init=False, repr=False, compare=False)

    def __post_init__(self, get_iterator: Callable[[], Iterator[T]]) -> None:
        self._get_iterator = get_iterator

    def __iter__(self) -> Iterator[T]:
        return self._get_iterator()


@dataclass
class PaginatedPage:
    count: int
    offset: int
    limit: int
    total: int
    desc: bool

@dataclass
class ListPageOfActors(PaginatedPage, IterablePage[ActorShort]): ...

@dataclass
class ListPageOfBuilds(PaginatedPage, IterablePage[BuildShort]): ...

@dataclass
class ListPageOfDatasets(PaginatedPage, IterablePage[DatasetListItem]): ...

@dataclass
class ListPageOfKeyValueStores(PaginatedPage, IterablePage[KeyValueStore]): ...

@dataclass
class ListPageOfRequestQueues(PaginatedPage, IterablePage[RequestQueueShort]): ...

@dataclass
class ListPageOfRuns(PaginatedPage, IterablePage[RunShort]): ...

@dataclass
class ListPageOfSchedules(PaginatedPage, IterablePage[ScheduleShort]): ...

@dataclass
class ListPageOfStoreActors(PaginatedPage, IterablePage[StoreListActor]): ...

@dataclass
class ListPageOfTasks(PaginatedPage, IterablePage[TaskShort]): ...

@dataclass
class ListPageOfWebhookDispatches(PaginatedPage, IterablePage[WebhookDispatch]): ...

@dataclass
class ListPageOfWebhooks(PaginatedPage, IterablePage[WebhookShort]): ...

@dataclass
class ListPageOfEnvVars(IterablePage[EnvVar]):
    total: int


@dataclass
class ListPageOfVersions(IterablePage[Version]):
    total: int

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

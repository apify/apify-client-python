from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Iterator
from typing import Any, Generic, Protocol, TypeVar

from apify_client.clients.base.base_client import ItemsDict

JSONSerializable = str | int | float | bool | None | dict[str, Any] | list[Any]
"""Type for representing json-serializable values. It's close enough to the real thing supported by json.parse.
It was suggested in a discussion with (and approved by) Guido van Rossum, so I'd consider it correct enough.
"""

T = TypeVar('T')


class PaginatedResponse(Protocol[T], Generic[T]):
    total: int
    """Total number of objects matching the API call criteria."""
    items: list[T]
    """List of returned objects on this page."""

class ListPage(Generic[T]):
    """A single page of items returned from a list() method."""

    items: list[T]
    """List of returned objects on this page."""

    count: int
    """Count of the returned objects on this page."""

    offset: int
    """The limit on the number of returned objects offset specified in the API call."""

    limit: int
    """The offset of the first object specified in the API call"""

    total: int
    """Total number of objects matching the API call criteria."""

    desc: bool
    """Whether the listing is descending or not."""

    def __init__(self, data: ItemsDict[T]) -> None:
        """Initialize a ListPage instance from the API response data."""
        self.item: list[T] = data['items']
        self.offset: int = data.get('offset', 0)
        self.limit: int = data.get('limit', 0)
        self.count: int = data.get('limit', len(self.items))
        self.total: int = data.get('total', self.offset + self.count)
        self.desc: bool = data.get('desc', False)


"""
Output differences in various list endpoints:

Normal (items, count, offset, limit, total, desc):
https://docs.apify.com/api/v2/acts-get
https://docs.apify.com/api/v2/act-builds-get
https://docs.apify.com/api/v2/act-runs-get
https://docs.apify.com/api/v2/act-webhooks-get
https://docs.apify.com/api/v2/actor-builds-get
https://docs.apify.com/api/v2/actor-runs-get
https://docs.apify.com/api/v2/actor-tasks-get
https://docs.apify.com/api/v2/actor-task-webhooks-get
https://docs.apify.com/api/v2/actor-task-runs-get
https://docs.apify.com/api/v2/webhooks-get
https://docs.apify.com/api/v2/webhook-dispatches-get
https://docs.apify.com/api/v2/schedules-get
https://docs.apify.com/api/v2/store-get

Only total+items:
https://docs.apify.com/api/v2/act-versions-get
https://docs.apify.com/api/v2/act-version-env-vars-get

Normal + undocumented unnamed:
https://docs.apify.com/api/v2/datasets-get
https://docs.apify.com/api/v2/key-value-stores-get
https://docs.apify.com/api/v2/request-queues-get

count, limit, exclusiveStartKey, isTruncated, nextExclusiveStartKey, items:
https://docs.apify.com/api/v2/key-value-store-keys-get

limit, exclusiveStartId(only if part of input arguments, otherwise missing!!!), items
https://docs.apify.com/api/v2/request-queue-requests-get

Only items, no pagination info in response. But it is in headers!!!:
https://docs.apify.com/api/v2/dataset-items-get

"""


class HasItems(Protocol[T]):
    items: list[T]
    """List of returned objects on this page."""


class HasTotal(Protocol):
    total: int
    """Total number of objects matching the API call criteria."""


class HasUnnamed(Protocol):
    unnamed: bool
    """Whether the unnamed storages are included."""


class HasCount(Protocol):
    count: int
    """Count of the returned objects on this page."""


class HasLimit(Protocol):
    limit: int
    """The offset of the first object specified in the API call"""


class HasOffset(Protocol):
    offset: int
    """The limit on the number of returned objects offset specified in the API call."""


class HasDesc(Protocol):
    desc: bool
    """Whether the listing is descending or not."""


class ItemsWithTotalProtocol(HasTotal, HasItems[T]):
    """Protocol for actor versions and actor version environment variables.

    https://docs.apify.com/api/v2/act-versions-get
    https://docs.apify.com/api/v2/act-version-env-vars-get
    """


class ListPageProtocol(HasCount, HasLimit, HasOffset, HasDesc, HasTotal, HasItems[T]):
    """Protocol for list method of common collection clients.

    https://docs.apify.com/api/v2/acts-get
    https://docs.apify.com/api/v2/act-builds-get
    https://docs.apify.com/api/v2/act-runs-get
    https://docs.apify.com/api/v2/act-webhooks-get
    https://docs.apify.com/api/v2/actor-builds-get
    https://docs.apify.com/api/v2/actor-runs-get
    https://docs.apify.com/api/v2/actor-tasks-get
    https://docs.apify.com/api/v2/actor-task-webhooks-get
    https://docs.apify.com/api/v2/actor-task-runs-get
    https://docs.apify.com/api/v2/webhooks-get
    https://docs.apify.com/api/v2/webhook-dispatches-get
    https://docs.apify.com/api/v2/schedules-get
    https://docs.apify.com/api/v2/store-get

    Information about pagination not in body, but in headers instead
    https://docs.apify.com/api/v2/datasets-get
    """


class ListPageStoragesProtocol(HasUnnamed, ListPageProtocol[T]):
    """Protocol for list method of storage collection clients.

    https://docs.apify.com/api/v2/datasets-get
    https://docs.apify.com/api/v2/key-value-stores-get
    https://docs.apify.com/api/v2/request-queues-get
    """


class ListPageKvsKeys(HasCount, HasLimit, HasItems[T]):
    """Protocol for list keys of KeyValueStoreClient.

    https://docs.apify.com/api/v2/key-value-store-keys-get
    """

    exclusive_start_key: None | str
    """All keys up to this one (including) are skipped from the result."""

    next_exclusive_start_key: None | str
    """Key that follows the last key returned."""

    is_truncated: bool
    """All keys up to this one (including) are skipped from the result."""


class ListPageRqRequests(HasLimit, HasItems[T]):
    """Protocol for list requests of RequestQueueClient.

    https://docs.apify.com/api/v2/request-queue-requests-get
    """

    exclusive_start_id: None | str
    """All requests up to this one (including) are skipped from the result."""


class _HasItemsIterable(HasItems[T], Protocol[T]):
    """Protocol for an object that can be both contains items and can be iterated over."""

    def __iter__(self) -> Iterator[T]: ...


class _HasItemsIterableAsync(Awaitable[HasItems[T]], Protocol[T]):
    """Protocol for an object that can be both awaited and asynchronously iterated over."""

    def __aiter__(self) -> AsyncIterator[T]: ...


# Example of usage
# Common collection clients list method return type
class ListPageProtocolIterable(ListPageProtocol[T], _HasItemsIterable[T]):
    """Protocol for an object that contains items and can be iterated over."""


class ListPageProtocolIterableAsync(Awaitable[ListPageProtocol[T]], _HasItemsIterableAsync[T]):
    """Protocol for an object that contains items and can be iterated over."""


# Storage collection clients list method return type
class ListPageStoragesProtocolIterable(ListPageStoragesProtocol[T], _HasItemsIterable[T]):
    """Protocol for an object that contains items and can be iterated over."""


class ListPageStoragesProtocolIterableAsync(Awaitable[ListPageStoragesProtocol[T]], _HasItemsIterableAsync[T]):
    """Protocol for an object that contains items and can be iterated over."""


# Actor versions collection clients list method return type
class ListPageBasicProtocolIterable(ItemsWithTotalProtocol[T], _HasItemsIterable[T]):
    """Protocol for an object that contains items and can be iterated over."""


class ListPageBasicProtocolIterableAsync(Awaitable[ItemsWithTotalProtocol[T]], _HasItemsIterableAsync[T]):
    """Protocol for an object that contains items and can be iterated over."""


# Kvs keys list method return type
class ListPageKvsKeysProtocolIterable(ListPageKvsKeys[T], _HasItemsIterable[T]):
    """Protocol for an object that contains items and can be iterated over."""


class ListPageKvsKeysProtocolIterableAsync(Awaitable[ListPageKvsKeys[T]], _HasItemsIterableAsync[T]):
    """Protocol for an object that contains items and can be iterated over."""


# Requests list method return type
class ListPageRqRequestsProtocolIterable(ListPageRqRequests[T], _HasItemsIterable[T]):
    """Protocol for an object that contains items and can be iterated over."""


class ListPageRqRequestsProtocolIterableAsync(Awaitable[ListPageRqRequests[T]], _HasItemsIterableAsync[T]):
    """Protocol for an object that contains items and can be iterated over."""

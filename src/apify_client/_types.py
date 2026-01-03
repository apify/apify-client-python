from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

JsonSerializable = str | int | float | bool | None | dict[str, Any] | list[Any]
"""Type for representing json-serializable values. It's close enough to the real thing supported by json.parse.
It was suggested in a discussion with (and approved by) Guido van Rossum, so I'd consider it correct enough.
"""

T = TypeVar('T')


class ListPage(Generic[T]):
    """A single page of items returned from a list() method."""

    items: list[T]
    """List of returned objects on this page."""

    count: int
    """Count of the returned objects on this page."""

    offset: int
    """The limit on the number of returned objects offset specified in the API call."""

    limit: int
    """The offset of the first object specified in the API call."""

    total: int
    """Total number of objects matching the API call criteria."""

    desc: bool
    """Whether the listing is descending or not."""

    def __init__(self, data: dict) -> None:
        """Initialize a new instance."""
        self.items = data.get('items', [])
        self.offset = data.get('offset', 0)
        self.limit = data.get('limit', 0)
        self.count = data['count'] if 'count' in data else len(self.items)
        self.total = data.get('total', self.offset + self.count)
        self.desc = data.get('desc', False)


@dataclass
class Statistics:
    """Statistics about API client usage and rate limit errors."""

    calls: int = 0
    """Total number of API method calls made by the client."""

    requests: int = 0
    """Total number of HTTP requests sent, including retries."""

    rate_limit_errors: defaultdict[int, int] = field(default_factory=lambda: defaultdict(int))
    """List tracking which retry attempts encountered rate limit (429) errors."""

    def add_rate_limit_error(self, attempt: int) -> None:
        """Add rate limit error for specific attempt.

        Args:
            attempt: The attempt number (1-based indexing).
        """
        if attempt < 1:
            raise ValueError('Attempt must be greater than 0')

        self.rate_limit_errors[attempt - 1] += 1

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

JsonSerializable = str | int | float | bool | None | dict[str, Any] | list[Any]
"""Type for representing json-serializable values. It's close enough to the real thing supported by json.parse.
It was suggested in a discussion with (and approved by) Guido van Rossum, so I'd consider it correct enough.
"""


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

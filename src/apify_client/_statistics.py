from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from apify_client._docs import docs_group


@docs_group('Other')
@dataclass
class ClientStatistics:
    """Statistics about API client usage and rate limit errors."""

    calls: int = 0
    """Total number of calls made by the client, including requests to Actor servers."""

    requests: int = 0
    """Total number of HTTP requests sent, including retries."""

    rate_limit_errors: defaultdict[int, int] = field(default_factory=lambda: defaultdict(int))
    """Number of rate limit (429) errors per attempt, keyed by the 0-based attempt index.

    Reading a missing key adds it with a count of `0`. Use `.get()` to read a count without changing the dict.
    """

    def add_rate_limit_error(self, attempt: int) -> None:
        """Add rate limit error for specific attempt.

        Args:
            attempt: The attempt number (1-based indexing).
        """
        if attempt < 1:
            raise ValueError('Attempt must be greater than 0')

        self.rate_limit_errors[attempt - 1] += 1

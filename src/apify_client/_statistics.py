from dataclasses import dataclass, field


@dataclass
class Statistics:
    """Statistics about API client usage and rate limit errors."""

    calls: int = 0
    requests: int = 0
    rate_limit_errors: list[int] = field(default_factory=list)

    def add_rate_limit_error(self, attempt: int) -> None:
        """Add rate limit error for specific attempt.

        Args:
            attempt: The attempt number (1-based indexing)
        """
        if attempt < 1:
            raise ValueError('Attempt must be greater than 0')

        index = attempt - 1
        self._ensure_list_capacity(index)
        self.rate_limit_errors[index] += 1

    def _ensure_list_capacity(self, index: int) -> None:
        """Ensure rate_limit_errors list has enough capacity.

        Args:
            index: Required index to access
        """
        if len(self.rate_limit_errors) <= index:
            self.rate_limit_errors.extend([0] * (index - len(self.rate_limit_errors) + 1))

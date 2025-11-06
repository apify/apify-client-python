from enum import Enum

class ActsGetSortBy(str, Enum):
    CREATEDAT = "createdAt"
    STATS_LASTRUNSTARTEDAT = "stats.lastRunStartedAt"

    def __str__(self) -> str:
        return str(self.value)

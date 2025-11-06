from enum import Enum

class KeyValueStoreRecordPutContentEncoding(str, Enum):
    GZIP = "gzip"

    def __str__(self) -> str:
        return str(self.value)

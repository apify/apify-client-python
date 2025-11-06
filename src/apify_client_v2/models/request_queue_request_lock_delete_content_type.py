from enum import Enum

class RequestQueueRequestLockDeleteContentType(str, Enum):
    APPLICATIONJSON = "application/json"

    def __str__(self) -> str:
        return str(self.value)

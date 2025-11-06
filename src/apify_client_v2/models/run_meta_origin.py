from enum import Enum

class RunMetaOrigin(str, Enum):
    ACTOR = "ACTOR"
    API = "API"
    CLI = "CLI"
    DEVELOPMENT = "DEVELOPMENT"
    SCHEDULER = "SCHEDULER"
    STANDBY = "STANDBY"
    TEST = "TEST"
    WEB = "WEB"
    WEBHOOK = "WEBHOOK"

    def __str__(self) -> str:
        return str(self.value)

from enum import Enum

class SourceCodeFileFormat(str, Enum):
    BASE64 = "BASE64"
    TEXT = "TEXT"

    def __str__(self) -> str:
        return str(self.value)

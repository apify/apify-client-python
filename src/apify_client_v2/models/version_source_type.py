from enum import Enum

class VersionSourceType(str, Enum):
    GITHUB_GIST = "GITHUB_GIST"
    GIT_REPO = "GIT_REPO"
    SOURCE_FILES = "SOURCE_FILES"
    TARBALL = "TARBALL"

    def __str__(self) -> str:
        return str(self.value)

from __future__ import annotations

import sys
from contextlib import contextmanager
from dataclasses import dataclass
from types import ModuleType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Any


@dataclass
class ImportState:
    """Describe whether an optional import succeeded."""

    available: bool = True


@contextmanager
def try_import(module_name: str, *symbol_names: str, dependency_name: str, extra_name: str) -> Iterator[ImportState]:
    """Context manager to attempt importing symbols into a module.

    If the named optional dependency is missing, the symbols are replaced with `FailedImport` objects whose message
    names the extra that installs it. Import errors caused by the importing module itself or by another dependency
    are propagated instead of being masked.
    """
    state = ImportState()
    try:
        yield state
    except ModuleNotFoundError as exc:
        if exc.name != dependency_name:
            raise
        state.available = False
        message = (
            f"{exc.args[0]}. Install the optional '{extra_name}' extra to use it: "
            f"pip install 'apify-client[{extra_name}]'"
        )
        for symbol_name in symbol_names:
            setattr(sys.modules[module_name], symbol_name, FailedImport(message))


def install_import_hook(module_name: str) -> None:
    """Install an import hook for a specified module."""
    sys.modules[module_name].__class__ = ImportWrapper


@dataclass
class FailedImport:
    """Represent a placeholder for a failed import."""

    message: str
    """The error message associated with the failed import."""


class ImportWrapper(ModuleType):
    """A wrapper class for modules to handle attribute access for failed imports."""

    def __getattribute__(self, name: str) -> Any:
        result = super().__getattribute__(name)

        if isinstance(result, FailedImport):
            raise ImportError(result.message)  # noqa: TRY004

        return result

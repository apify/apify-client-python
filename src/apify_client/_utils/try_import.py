from __future__ import annotations

import sys
from contextlib import contextmanager
from dataclasses import dataclass
from types import ModuleType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator


@dataclass
class _FailedImport:
    message: str


class _ImportWrapper(ModuleType):
    """Module subclass that converts `_FailedImport` attribute accesses into `ImportError`.

    Must override `__getattribute__` (not `__getattr__`): the `_FailedImport` placeholder lives in
    the module's `__dict__`, so a normal lookup would find it and `__getattr__` (the fallback for
    missing attributes) would never fire.
    """

    def __getattribute__(self, name: str) -> object:
        obj = super().__getattribute__(name)
        if isinstance(obj, _FailedImport):
            raise ImportError(obj.message)  # noqa: TRY004
        return obj


@contextmanager
def try_import(module_name: str, *symbol_names: str) -> Generator[None, None, None]:
    """Context manager for optional imports.

    If the import inside the block raises `ImportError`, each named symbol in the given module is
    replaced with a `_FailedImport` placeholder. Accessing that placeholder later (after
    `install_import_hook` has been called) raises a clear `ImportError` with the original message.

    Args:
        module_name: Fully-qualified name of the module whose namespace to update (pass `__name__`).
        symbol_names: The names that would have been imported, used as the placeholder keys.
    """
    try:
        yield
    except ImportError as exc:
        for symbol_name in symbol_names:
            setattr(sys.modules[module_name], symbol_name, _FailedImport(str(exc)))


def install_import_hook(module_name: str) -> None:
    """Replace a module's class with `_ImportWrapper` to activate deferred `ImportError` raising.

    Call this in the package `__init__.py` alongside the `try_import` blocks (see `http_compressors`).
    The placeholder is resolved lazily on attribute access, so the relative order of this call and
    the `try_import` blocks does not matter.

    Args:
        module_name: Fully-qualified name of the module to wrap (pass `__name__`).
    """
    sys.modules[module_name].__class__ = _ImportWrapper

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from griffe import Module, load

if TYPE_CHECKING:
    from collections.abc import Generator

    from griffe import Class, Function

SKIPPED_METHODS = {
    'with_custom_http_client',
}
"""Methods where the async and sync docstrings are intentionally different."""

SRC_PATH = Path(__file__).resolve().parent.parent / 'src'
"""Path to the source code of the apify_client package."""

_SUBSTITUTIONS = [
    (re.compile(r'Client'), 'ClientAsync'),
    (re.compile(r'\bsynchronously\b'), 'asynchronously'),
    (re.compile(r'\bSynchronously\b'), 'Asynchronously'),
    (re.compile(r'\bsynchronous\b'), 'asynchronous'),
    (re.compile(r'\bSynchronous\b'), 'Asynchronous'),
    (re.compile(r'Retry a function'), 'Retry an async function'),
    (re.compile(r'Function to retry'), 'Async function to retry'),
]
"""Patterns for converting sync docstrings to async docstrings."""


def load_package() -> Module:
    """Load the apify_client package using griffe."""
    package = load('apify_client', search_paths=[str(SRC_PATH)])
    if not isinstance(package, Module):
        raise TypeError('Expected griffe to load a Module')
    return package


def walk_modules(module: Module) -> Generator[Module]:
    """Recursively yield all modules in the package."""
    yield module
    for submodule in module.modules.values():
        yield from walk_modules(submodule)


def iter_docstring_mismatches(package: Module) -> Generator[tuple[Class, Function, Class, Function, str, bool]]:
    """Yield docstring mismatches between sync and async client methods.

    Yields (async_class, async_method, sync_class, sync_method, expected_docstring, has_existing).
    """
    for module in walk_modules(package):
        for async_class in module.classes.values():
            if not async_class.name.endswith('ClientAsync'):
                continue

            sync_class = module.classes.get(async_class.name.replace('ClientAsync', 'Client'))
            if not sync_class:
                continue

            for async_method in async_class.functions.values():
                if any(str(d.value) == 'ignore_docs' for d in async_method.decorators):
                    continue

                if async_method.name in SKIPPED_METHODS:
                    continue

                sync_method = sync_class.functions.get(async_method.name)
                if not sync_method or not sync_method.docstring:
                    continue

                expected_docstring = _sync_to_async_docstring(sync_method.docstring.value)

                if not async_method.docstring:
                    yield async_class, async_method, sync_class, sync_method, expected_docstring, False
                elif async_method.docstring.value != expected_docstring:
                    yield async_class, async_method, sync_class, sync_method, expected_docstring, True


def _sync_to_async_docstring(docstring: str) -> str:
    """Convert a docstring from a sync component version into a docstring for its async analogue."""
    result = docstring
    for pattern, replacement in _SUBSTITUTIONS:
        result = pattern.sub(replacement, result)
    return result

"""Check that async client docstrings are in sync with their sync counterparts."""

from __future__ import annotations

import sys

from ._utils import iter_docstring_mismatches, load_package


def main() -> None:
    """Check all async client methods for docstring mismatches."""
    package = load_package()
    found_issues = False

    for (
        async_class,
        async_method,
        sync_class,
        sync_method,
        _expected_docstring,
        has_existing,
    ) in iter_docstring_mismatches(package):
        found_issues = True
        if has_existing:
            print(
                f'Docstring mismatch: "{async_class.name}.{async_method.name}"'
                f' vs "{sync_class.name}.{sync_method.name}"'
            )
        else:
            print(f'Missing docstring for "{async_class.name}.{async_method.name}"!')

    if found_issues:
        print()
        print('Issues with async docstrings found. Fix them by running `uv run poe fix-docstrings`.')
        sys.exit(1)
    else:
        print('Success: async method docstrings are in sync with sync method docstrings.')


if __name__ == '__main__':
    main()

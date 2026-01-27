"""Utilities for data manipulation and cleaning."""

from __future__ import annotations

from typing import cast


def filter_none_values(
    data: dict,
    *,
    remove_empty_dicts: bool | None = None,
) -> dict:
    """Remove None values from a dictionary recursively.

    The Apify API ignores missing fields but may reject fields explicitly
    set to None. This prepares request payloads by recursively removing
    None values.

    Args:
        data: Dictionary to clean
        remove_empty_dicts: Also remove empty dicts after filtering None values

    Returns:
        New dictionary with None values removed at all nesting levels

    Example:
        >>> clean_request_dict({'a': 1, 'b': None, 'c': {'d': None, 'e': 2}})
        {'a': 1, 'c': {'e': 2}}
    """

    def _internal(dictionary: dict, *, remove_empty: bool | None = None) -> dict | None:
        result = {}
        for key, val in dictionary.items():
            if isinstance(val, dict):
                val = _internal(val, remove_empty=remove_empty)  # noqa: PLW2901
            if val is not None:
                result[key] = val
        if not result and remove_empty:
            return None
        return result

    return cast('dict', _internal(data, remove_empty=remove_empty_dicts))

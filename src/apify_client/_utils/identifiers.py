"""Utilities for handling resource identifiers."""

from __future__ import annotations


def to_safe_id(id: str) -> str:
    """Convert a resource ID to URL-safe format by replacing `/` with `~`.

    Args:
        id: The resource identifier (format: `resource_id` or `username/resource_id`).

    Returns:
        The resource identifier with `/` replaced by `~`.
    """
    return id.replace('/', '~')

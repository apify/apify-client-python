"""Utilities for handling enum values."""

from __future__ import annotations

from enum import Enum
from typing import Any


def enum_to_value(value: Any) -> Any:
    """Convert Enum member to its value, or return unchanged if not an Enum.

    Ensures Enum instances are converted to primitive values suitable
    for API transmission.

    Args:
        value: Value to potentially convert (Enum member or any other type)

    Returns:
        If value is an Enum, returns value.value; otherwise returns value unchanged

    Example:
        >>> enum_to_value(ActorJobStatus.SUCCEEDED)
        'SUCCEEDED'
        >>> enum_to_value('already_a_string')
        'already_a_string'
        >>> enum_to_value(None)
        None
    """
    if isinstance(value, Enum):
        return value.value
    return value

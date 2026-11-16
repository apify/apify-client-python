from __future__ import annotations

from datetime import timedelta
from typing import Literal, overload


@overload
def to_seconds(td: None, *, as_int: bool = ...) -> None: ...
@overload
def to_seconds(td: timedelta) -> float: ...
@overload
def to_seconds(td: timedelta, *, as_int: Literal[True]) -> int: ...
@overload
def to_seconds(td: timedelta, *, as_int: Literal[False]) -> float: ...


def to_seconds(td: timedelta | None, *, as_int: bool = False) -> float | int | None:
    """Convert timedelta to seconds.

    Args:
        td: The timedelta to convert, or None.
        as_int: If True, round and return as int. Defaults to False.

    Returns:
        The total seconds as a float (or int if as_int=True), or None if input is None.
    """
    if td is None:
        return None
    seconds = td.total_seconds()
    return int(seconds) if as_int else seconds


def to_whole_seconds(duration: timedelta | int | None) -> int | None:
    """Convert a duration given as a `timedelta` or as a number of seconds to whole seconds."""
    if isinstance(duration, timedelta):
        return to_seconds(duration, as_int=True)
    return duration

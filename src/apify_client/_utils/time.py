from __future__ import annotations

from typing import TYPE_CHECKING, Literal, overload

if TYPE_CHECKING:
    from datetime import timedelta


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

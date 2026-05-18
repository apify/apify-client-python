from __future__ import annotations

from datetime import timedelta
from typing import Literal

Timeout = timedelta | Literal['no_timeout', 'short', 'medium', 'long']
"""Type for the `timeout` parameter on resource client methods.

`'short'`, `'medium'`, and `'long'` are tier literals resolved by the HTTP client to configured values.
A `timedelta` overrides the timeout for this call, and `'no_timeout'` disables the timeout entirely.
"""

__all__ = [
    'Timeout',
]

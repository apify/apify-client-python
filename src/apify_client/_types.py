from __future__ import annotations

from datetime import timedelta
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from apify_client._models import ActorJobStatus  # noqa: TC001

Timeout = timedelta | Literal['no_timeout', 'short', 'medium', 'long']
"""Type for the `timeout` parameter on resource client methods.

`'short'`, `'medium'`, and `'long'` are tier literals resolved by the HTTP client to configured values.
A `timedelta` overrides the timeout for this call, and `'no_timeout'` disables the timeout entirely.
"""

JsonSerializable = str | int | float | bool | None | dict[str, Any] | list[Any]
"""Type for representing json-serializable values. It's close enough to the real thing supported by json.parse.
It was suggested in a discussion with (and approved by) Guido van Rossum, so I'd consider it correct enough.
"""


class ActorJob(BaseModel):
    """Minimal model for an Actor job (run or build) with status.

    Used for validation during polling operations. Allows extra fields so the full response data is preserved.
    """

    model_config = ConfigDict(extra='allow')

    status: ActorJobStatus


class ActorJobResponse(BaseModel):
    """Response wrapper for an Actor job (run or build).

    Used for minimal validation during polling operations. Allows extra fields so the full response data is preserved.
    """

    model_config = ConfigDict(extra='allow')

    data: ActorJob

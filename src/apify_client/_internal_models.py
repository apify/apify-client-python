"""Internal Pydantic models that are not part of the public API and are therefore not generated."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from apify_client._models import ActorJobStatus  # noqa: TC001


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

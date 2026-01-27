"""Constants and enums used by the Apify client."""

from __future__ import annotations

from enum import Enum


class ActorJobStatus(str, Enum):
    """Available statuses for Actor jobs (runs or builds).

    These statuses represent the lifecycle of an Actor execution,
    from initialization to completion or termination.
    """

    READY = 'READY'
    """Actor job has been initialized but not yet started."""

    RUNNING = 'RUNNING'
    """Actor job is currently executing."""

    SUCCEEDED = 'SUCCEEDED'
    """Actor job completed successfully without errors."""

    FAILED = 'FAILED'
    """Actor job or build failed due to an error or exception."""

    TIMING_OUT = 'TIMING-OUT'
    """Actor job is currently in the process of timing out."""

    TIMED_OUT = 'TIMED-OUT'
    """Actor job was terminated due to timeout."""

    ABORTING = 'ABORTING'
    """Actor job is currently being aborted by user request."""

    ABORTED = 'ABORTED'
    """Actor job was successfully aborted by user request."""

    @property
    def is_terminal(self: ActorJobStatus) -> bool:
        """Whether this Actor job status is terminal."""
        return self in (
            ActorJobStatus.SUCCEEDED,
            ActorJobStatus.FAILED,
            ActorJobStatus.TIMED_OUT,
            ActorJobStatus.ABORTED,
        )


class WebhookEventType(str, Enum):
    """Event types that can trigger webhook notifications.

    These events are sent to configured webhook URLs when specific
    Actor run or build lifecycle events occur, enabling integration
    with external systems and automated workflows.
    """

    ACTOR_RUN_CREATED = 'ACTOR.RUN.CREATED'
    """Triggered when a new Actor run is created and initialized."""

    ACTOR_RUN_SUCCEEDED = 'ACTOR.RUN.SUCCEEDED'
    """Triggered when an Actor run completes successfully."""

    ACTOR_RUN_FAILED = 'ACTOR.RUN.FAILED'
    """Triggered when an Actor run fails due to an error."""

    ACTOR_RUN_TIMED_OUT = 'ACTOR.RUN.TIMED_OUT'
    """Triggered when an Actor run is terminated due to timeout."""

    ACTOR_RUN_ABORTED = 'ACTOR.RUN.ABORTED'
    """Triggered when an Actor run is manually aborted by user."""

    ACTOR_RUN_RESURRECTED = 'ACTOR.RUN.RESURRECTED'
    """Triggered when a previously failed Actor run is automatically resurrected."""

    ACTOR_BUILD_CREATED = 'ACTOR.BUILD.CREATED'
    """Triggered when a new Actor build process is initiated."""

    ACTOR_BUILD_SUCCEEDED = 'ACTOR.BUILD.SUCCEEDED'
    """Triggered when an Actor build completes successfully."""

    ACTOR_BUILD_FAILED = 'ACTOR.BUILD.FAILED'
    """Triggered when an Actor build fails due to compilation or setup errors."""

    ACTOR_BUILD_TIMED_OUT = 'ACTOR.BUILD.TIMED_OUT'
    """Triggered when an Actor build process exceeds the time limit."""

    ACTOR_BUILD_ABORTED = 'ACTOR.BUILD.ABORTED'
    """Triggered when an Actor build is manually cancelled by user."""


class StorageGeneralAccess(str, Enum):
    """Storage setting determining how others can access the storage.

    This setting overrides the user setting of the storage owner.
    """

    FOLLOW_USER_SETTING = 'FOLLOW_USER_SETTING'
    """Respect the user setting of the storage owner (default behavior)."""

    RESTRICTED = 'RESTRICTED'
    """Only signed-in users with explicit access can read this storage."""

    ANYONE_WITH_ID_CAN_READ = 'ANYONE_WITH_ID_CAN_READ'
    """Anyone with a link or the unique storage ID can read this storage."""

    ANYONE_WITH_NAME_CAN_READ = 'ANYONE_WITH_NAME_CAN_READ'
    """Anyone with a link, ID, or storage name can read this storage."""


class RunGeneralAccess(str, Enum):
    """Run setting determining how others can access the run.

    This setting overrides the user setting of the run owner.
    """

    FOLLOW_USER_SETTING = 'FOLLOW_USER_SETTING'
    """Respect the user setting of the storage owner (default behavior)."""

    RESTRICTED = 'RESTRICTED'
    """Only signed-in users with explicit access can read this run."""

    ANYONE_WITH_ID_CAN_READ = 'ANYONE_WITH_ID_CAN_READ'
    """Anyone with a link or the unique run ID can read this run."""

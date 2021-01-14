from enum import Enum


class ActorJobStatus(Enum):
    """Available statuses for actor jobs (runs or builds)."""

    READY = 'READY'  # started but not allocated to any worker yet
    RUNNING = 'RUNNING'  # running on worker
    SUCCEEDED = 'SUCCEEDED'  # finished and all good
    FAILED = 'FAILED'  # run or build failed
    TIMING_OUT = 'TIMING_OUT'  # timing out now
    TIMED_OUT = 'TIMED_OUT'  # timed out
    ABORTING = 'ABORTING'  # being aborted by user
    ABORTED = 'ABORTED'  # aborted by user


# Actor job statuses that are considered terminal
TERMINAL_ACTOR_JOB_STATUSES = [
    ActorJobStatus.SUCCEEDED,
    ActorJobStatus.FAILED,
    ActorJobStatus.TIMED_OUT,
    ActorJobStatus.ABORTED,
]

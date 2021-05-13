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


class ActorSourceType(Enum):
    """Available source types for actors."""

    SOURCE_CODE = 'SOURCE_CODE'  # Source code is a single JavaScript/Node.js file
    SOURCE_FILES = 'SOURCE_FILES'  # Source code is comprised of multiple files
    GIT_REPO = 'GIT_REPO'  # Source code is cloned from a Git repository
    TARBALL = 'TARBALL'  # Source code is downloaded using a tarball or Zip file
    GITHUB_GIST = 'GITHUB_GIST'  # Source code is taken from a GitHub Gist


class WebhookEventType(Enum):
    """Events that can trigger a webhook."""

    ACTOR_RUN_CREATED = 'ACTOR.RUN.CREATED'
    ACTOR_RUN_SUCCEEDED = 'ACTOR.RUN.SUCCEEDED'
    ACTOR_RUN_FAILED = 'ACTOR.RUN.FAILED'
    ACTOR_RUN_TIMED_OUT = 'ACTOR.RUN.TIMED_OUT'
    ACTOR_RUN_ABORTED = 'ACTOR.RUN.ABORTED'
    ACTOR_RUN_RESURRECTED = 'ACTOR.RUN.RESURRECTED'


# Actor job statuses that are considered terminal
TERMINAL_ACTOR_JOB_STATUSES = [
    ActorJobStatus.SUCCEEDED,
    ActorJobStatus.FAILED,
    ActorJobStatus.TIMED_OUT,
    ActorJobStatus.ABORTED,
]

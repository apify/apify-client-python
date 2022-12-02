from enum import Enum


class ActorJobStatus(str, Enum):
    """Available statuses for actor jobs (runs or builds)."""

    #: Actor job initialized but not started yet
    READY = 'READY'
    #: Actor job in progress
    RUNNING = 'RUNNING'
    #: Actor job finished successfully
    SUCCEEDED = 'SUCCEEDED'
    #: Actor job or build failed
    FAILED = 'FAILED'
    #: Actor job currently timing out
    TIMING_OUT = 'TIMING-OUT'
    #: Actor job timed out
    TIMED_OUT = 'TIMED-OUT'
    #: Actor job currently being aborted by user
    ABORTING = 'ABORTING'
    #: Actor job aborted by user
    ABORTED = 'ABORTED'

    @property
    def _is_terminal(self) -> bool:
        """Whether this actor job status is terminal."""
        return self in (ActorJobStatus.SUCCEEDED, ActorJobStatus.FAILED, ActorJobStatus.TIMED_OUT, ActorJobStatus.ABORTED)


class ActorSourceType(str, Enum):
    """Available source types for actors."""

    #: Actor source code is comprised of multiple files
    SOURCE_FILES = 'SOURCE_FILES'
    #: Actor source code is cloned from a Git repository
    GIT_REPO = 'GIT_REPO'
    #: Actor source code is downloaded using a tarball or Zip file
    TARBALL = 'TARBALL'
    #: Actor source code is taken from a GitHub Gist
    GITHUB_GIST = 'GITHUB_GIST'


class WebhookEventType(str, Enum):
    """Events that can trigger a webhook."""

    #: The actor run was created
    ACTOR_RUN_CREATED = 'ACTOR.RUN.CREATED'
    #: The actor run has succeeded
    ACTOR_RUN_SUCCEEDED = 'ACTOR.RUN.SUCCEEDED'
    #: The actor run has failed
    ACTOR_RUN_FAILED = 'ACTOR.RUN.FAILED'
    #: The actor run has timed out
    ACTOR_RUN_TIMED_OUT = 'ACTOR.RUN.TIMED_OUT'
    #: The actor run was aborted
    ACTOR_RUN_ABORTED = 'ACTOR.RUN.ABORTED'
    #: The actor run was resurrected
    ACTOR_RUN_RESURRECTED = 'ACTOR.RUN.RESURRECTED'

    #: The actor build was created
    ACTOR_BUILD_CREATED = 'ACTOR.BUILD.CREATED'
    #: The actor build has succeeded
    ACTOR_BUILD_SUCCEEDED = 'ACTOR.BUILD.SUCCEEDED'
    #: The actor build has failed
    ACTOR_BUILD_FAILED = 'ACTOR.BUILD.FAILED'
    #: The actor build has timed out
    ACTOR_BUILD_TIMED_OUT = 'ACTOR.BUILD.TIMED_OUT'
    #: The actor build was aborted
    ACTOR_BUILD_ABORTED = 'ACTOR.BUILD.ABORTED'


class MetaOrigin(str, Enum):
    """Possible origins for actor runs, i.e. how were the jobs started."""

    #: Job started from Developer console in Source section of actor
    DEVELOPMENT = 'DEVELOPMENT'
    #: Job started from other place on the website (either console or task detail page)
    WEB = 'WEB'
    #: Job started through API
    API = 'API'
    #: Job started through Scheduler
    SCHEDULER = 'SCHEDULER'
    #: Job started through test actor page
    TEST = 'TEST'
    #: Job started by the webhook
    WEBHOOK = 'WEBHOOK'
    #: Job started by another actor run
    ACTOR = 'ACTOR'

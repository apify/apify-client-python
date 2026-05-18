from __future__ import annotations

from typing import Literal

TerminalActorJobStatus = Literal['SUCCEEDED', 'FAILED', 'TIMED-OUT', 'ABORTED']
"""Subset of `ActorJobStatus` values that indicate the job has finished and will not change again."""

from __future__ import annotations

import warnings
from typing import Any

from apify_client._models import ActorStandby
from apify_client._utils.time import to_seconds

DEPRECATED_SERVER_ARGS = {
    'actor_standby_is_enabled': 'server_is_enabled',
    'actor_standby_desired_requests_per_actor_run': 'server_desired_requests_per_actor_run',
    'actor_standby_max_requests_per_actor_run': 'server_max_requests_per_actor_run',
    'actor_standby_idle_timeout': 'server_idle_timeout',
    'actor_standby_build': 'server_build',
    'actor_standby_memory_mbytes': 'server_memory_mbytes',
    'actor_standby_disable_standby_fields_override': 'server_disable_fields_override',
    'actor_standby_should_pass_actor_input': 'server_should_pass_actor_input',
}
"""Deprecated `actor_standby_*` arguments, named after Actor Standby (the former name of Server Actors), mapped to the
`server_*` arguments that replace them."""


def build_actor_standby(server_args: dict[str, Any], deprecated_args: dict[str, Any]) -> ActorStandby:
    """Build the `actorStandby` field of an Actor or task from its `server_*` arguments.

    Each set deprecated `actor_standby_*` argument emits a `DeprecationWarning` pointing at the caller of the public
    method and is used as its `server_*` counterpart.

    Args:
        server_args: The `server_*` arguments by name.
        deprecated_args: The deprecated `actor_standby_*` arguments by name.

    Raises:
        ValueError: If both a deprecated argument and its `server_*` counterpart are set.
    """
    args = dict(server_args)
    for deprecated_name, value in deprecated_args.items():
        if value is None:
            continue
        name = DEPRECATED_SERVER_ARGS[deprecated_name]
        warnings.warn(
            f'The `{deprecated_name}` argument is deprecated and will be removed in v4. Use `{name}` instead.',
            DeprecationWarning,
            stacklevel=4,
        )
        if args.get(name) is not None:
            raise ValueError(f'Pass only one of `{name}` and `{deprecated_name}`.')
        args[name] = value

    return ActorStandby(
        is_enabled=args.get('server_is_enabled'),
        desired_requests_per_actor_run=args.get('server_desired_requests_per_actor_run'),
        max_requests_per_actor_run=args.get('server_max_requests_per_actor_run'),
        idle_timeout_secs=to_seconds(args.get('server_idle_timeout'), as_int=True),
        build=args.get('server_build'),
        memory_mbytes=args.get('server_memory_mbytes'),
        disable_standby_fields_override=args.get('server_disable_fields_override'),
        should_pass_actor_input=args.get('server_should_pass_actor_input'),
    )

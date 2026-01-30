"""Helper functions for building API request representations.

This module provides utilities for constructing dictionary representations of API resources. These representations
are used when creating or updating resources via the Apify API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._utils import enum_to_value, to_seconds

if TYPE_CHECKING:
    from datetime import timedelta

    from apify_client._models import ActorPermissionLevel, VersionSourceType, WebhookEventType


def build_actor_standby_dict(
    *,
    is_enabled: bool | None = None,
    desired_requests_per_actor_run: int | None = None,
    max_requests_per_actor_run: int | None = None,
    idle_timeout: timedelta | None = None,
    build: str | None = None,
    memory_mbytes: int | None = None,
) -> dict:
    """Build Actor standby configuration dictionary."""
    return {
        'isEnabled': is_enabled,
        'desiredRequestsPerActorRun': desired_requests_per_actor_run,
        'maxRequestsPerActorRun': max_requests_per_actor_run,
        'idleTimeoutSecs': to_seconds(idle_timeout),
        'build': build,
        'memoryMbytes': memory_mbytes,
    }


def build_default_run_options_dict(
    *,
    build: str | None = None,
    max_items: int | None = None,
    memory_mbytes: int | None = None,
    timeout: timedelta | None = None,
    restart_on_error: bool | None = None,
    force_permission_level: ActorPermissionLevel | None = None,
) -> dict:
    """Build default run options dictionary for Actor."""
    return {
        'build': build,
        'maxItems': max_items,
        'memoryMbytes': memory_mbytes,
        'timeoutSecs': to_seconds(timeout),
        'restartOnError': restart_on_error,
        'forcePermissionLevel': force_permission_level,
    }


def build_task_options_dict(
    *,
    build: str | None = None,
    max_items: int | None = None,
    memory_mbytes: int | None = None,
    timeout: timedelta | None = None,
    restart_on_error: bool | None = None,
) -> dict:
    """Build task options dictionary."""
    return {
        'build': build,
        'maxItems': max_items,
        'memoryMbytes': memory_mbytes,
        'timeoutSecs': to_seconds(timeout),
        'restartOnError': restart_on_error,
    }


def build_example_run_input_dict(
    *,
    body: Any = None,
    content_type: str | None = None,
) -> dict:
    """Build example run input dictionary for Actor."""
    return {
        'body': body,
        'contentType': content_type,
    }


def build_webhook_condition_dict(
    *,
    actor_id: str | None = None,
    actor_task_id: str | None = None,
    actor_run_id: str | None = None,
) -> dict:
    """Build webhook condition dictionary."""
    return {
        'actorRunId': actor_run_id,
        'actorTaskId': actor_task_id,
        'actorId': actor_id,
    }


def get_actor_repr(
    *,
    name: str | None,
    title: str | None = None,
    description: str | None = None,
    seo_title: str | None = None,
    seo_description: str | None = None,
    versions: list[dict] | None = None,
    restart_on_error: bool | None = None,
    is_public: bool | None = None,
    is_deprecated: bool | None = None,
    is_anonymously_runnable: bool | None = None,
    categories: list[str] | None = None,
    default_run_build: str | None = None,
    default_run_max_items: int | None = None,
    default_run_memory_mbytes: int | None = None,
    default_run_timeout: timedelta | None = None,
    default_run_force_permission_level: ActorPermissionLevel | None = None,
    example_run_input_body: Any = None,
    example_run_input_content_type: str | None = None,
    actor_standby_is_enabled: bool | None = None,
    actor_standby_desired_requests_per_actor_run: int | None = None,
    actor_standby_max_requests_per_actor_run: int | None = None,
    actor_standby_idle_timeout: timedelta | None = None,
    actor_standby_build: str | None = None,
    actor_standby_memory_mbytes: int | None = None,
    pricing_infos: list[dict] | None = None,
    actor_permission_level: ActorPermissionLevel | None = None,
    tagged_builds: dict[str, None | dict[str, str]] | None = None,
) -> dict:
    """Get dictionary representation of the Actor."""
    actor_dict: dict[str, Any] = {
        'name': name,
        'title': title,
        'description': description,
        'seoTitle': seo_title,
        'seoDescription': seo_description,
        'versions': versions,
        'isPublic': is_public,
        'isDeprecated': is_deprecated,
        'isAnonymouslyRunnable': is_anonymously_runnable,
        'categories': categories,
        'pricingInfos': pricing_infos,
        'actorPermissionLevel': actor_permission_level,
        'defaultRunOptions': build_default_run_options_dict(
            build=default_run_build,
            max_items=default_run_max_items,
            memory_mbytes=default_run_memory_mbytes,
            timeout=default_run_timeout,
            restart_on_error=restart_on_error,
            force_permission_level=default_run_force_permission_level,
        ),
        'actorStandby': build_actor_standby_dict(
            is_enabled=actor_standby_is_enabled,
            desired_requests_per_actor_run=actor_standby_desired_requests_per_actor_run,
            max_requests_per_actor_run=actor_standby_max_requests_per_actor_run,
            idle_timeout=actor_standby_idle_timeout,
            build=actor_standby_build,
            memory_mbytes=actor_standby_memory_mbytes,
        ),
        'exampleRunInput': build_example_run_input_dict(
            body=example_run_input_body,
            content_type=example_run_input_content_type,
        ),
    }

    # Include taggedBuilds if provided
    if tagged_builds is not None:
        actor_dict['taggedBuilds'] = tagged_builds

    return actor_dict


def get_task_repr(
    actor_id: str | None = None,
    name: str | None = None,
    task_input: dict | None = None,
    build: str | None = None,
    max_items: int | None = None,
    memory_mbytes: int | None = None,
    timeout: timedelta | None = None,
    title: str | None = None,
    actor_standby_desired_requests_per_actor_run: int | None = None,
    actor_standby_max_requests_per_actor_run: int | None = None,
    actor_standby_idle_timeout: timedelta | None = None,
    actor_standby_build: str | None = None,
    actor_standby_memory_mbytes: int | None = None,
    *,
    restart_on_error: bool | None = None,
) -> dict:
    """Get the dictionary representation of a task."""
    return {
        'actId': actor_id,
        'name': name,
        'title': title,
        'input': task_input,
        'options': build_task_options_dict(
            build=build,
            max_items=max_items,
            memory_mbytes=memory_mbytes,
            timeout=timeout,
            restart_on_error=restart_on_error,
        ),
        'actorStandby': build_actor_standby_dict(
            desired_requests_per_actor_run=actor_standby_desired_requests_per_actor_run,
            max_requests_per_actor_run=actor_standby_max_requests_per_actor_run,
            idle_timeout=actor_standby_idle_timeout,
            build=actor_standby_build,
            memory_mbytes=actor_standby_memory_mbytes,
        ),
    }


def get_actor_version_repr(
    *,
    version_number: str | None = None,
    build_tag: str | None = None,
    env_vars: list[dict] | None = None,
    apply_env_vars_to_build: bool | None = None,
    source_type: VersionSourceType | None = None,
    source_files: list[dict] | None = None,
    git_repo_url: str | None = None,
    tarball_url: str | None = None,
    github_gist_url: str | None = None,
) -> dict:
    """Get dictionary representation of an Actor version."""
    return {
        'versionNumber': version_number,
        'buildTag': build_tag,
        'envVars': env_vars,
        'applyEnvVarsToBuild': apply_env_vars_to_build,
        'sourceType': enum_to_value(source_type),
        'sourceFiles': source_files,
        'gitRepoUrl': git_repo_url,
        'tarballUrl': tarball_url,
        'gitHubGistUrl': github_gist_url,
    }


def get_schedule_repr(
    cron_expression: str | None = None,
    name: str | None = None,
    actions: list[dict] | None = None,
    description: str | None = None,
    timezone: str | None = None,
    title: str | None = None,
    *,
    is_enabled: bool | None = None,
    is_exclusive: bool | None = None,
) -> dict:
    """Get dictionary representation of a schedule."""
    return {
        'cronExpression': cron_expression,
        'isEnabled': is_enabled,
        'isExclusive': is_exclusive,
        'name': name,
        'actions': actions,
        'description': description,
        'timezone': timezone,
        'title': title,
    }


def get_webhook_repr(
    *,
    event_types: list[WebhookEventType] | None = None,
    request_url: str | None = None,
    payload_template: str | None = None,
    headers_template: str | None = None,
    actor_id: str | None = None,
    actor_task_id: str | None = None,
    actor_run_id: str | None = None,
    ignore_ssl_errors: bool | None = None,
    do_not_retry: bool | None = None,
    idempotency_key: str | None = None,
    is_ad_hoc: bool | None = None,
) -> dict:
    """Prepare webhook dictionary representation for clients."""
    webhook: dict[str, Any] = {
        'requestUrl': request_url,
        'payloadTemplate': payload_template,
        'headersTemplate': headers_template,
        'ignoreSslErrors': ignore_ssl_errors,
        'doNotRetry': do_not_retry,
        'idempotencyKey': idempotency_key,
        'isAdHoc': is_ad_hoc,
        'condition': build_webhook_condition_dict(
            actor_id=actor_id,
            actor_task_id=actor_task_id,
            actor_run_id=actor_run_id,
        ),
    }

    if actor_run_id is not None:
        webhook['isAdHoc'] = True

    if event_types is not None:
        webhook['eventTypes'] = [enum_to_value(event_type) for event_type in event_types]

    return webhook

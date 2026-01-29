"""Unified tests for run collection (sync + async)."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync
    from apify_client._models import ListOfRuns

from datetime import datetime, timezone

from .conftest import maybe_await
from apify_client._models import ActorJobStatus, Run

APIFY_HELLO_WORLD_ACTOR = 'apify/hello-world'


async def test_run_collection_list_multiple_statuses(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing runs with multiple statuses."""
    created_runs = list[Run]()

    result = await maybe_await(client.actor(APIFY_HELLO_WORLD_ACTOR).call())
    if result is not None:
        successful_run = cast('Run', result)
        created_runs.append(successful_run)

    result = await maybe_await(client.actor(APIFY_HELLO_WORLD_ACTOR).call(timeout_secs=1))
    if result is not None:
        timed_out_run = cast('Run', result)
        created_runs.append(timed_out_run)

    run_collection = client.actor(APIFY_HELLO_WORLD_ACTOR).runs()

    result = await maybe_await(run_collection.list(status=[ActorJobStatus.SUCCEEDED, ActorJobStatus.TIMED_OUT]))
    multiple_status_runs = cast('ListOfRuns', result)

    result = await maybe_await(run_collection.list(status=ActorJobStatus.SUCCEEDED))
    single_status_runs = cast('ListOfRuns', result)

    assert multiple_status_runs is not None
    assert single_status_runs is not None

    assert all(run.status in [ActorJobStatus.SUCCEEDED, ActorJobStatus.TIMED_OUT] for run in multiple_status_runs.items)
    assert all(run.status == ActorJobStatus.SUCCEEDED for run in single_status_runs.items)

    for run in created_runs:
        run_id = run.id
        if isinstance(run_id, str):
            await maybe_await(client.run(run_id).delete())


async def test_run_collection_list_accept_date_range(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing runs with date range parameters."""
    created_runs = list[Run]()

    result = await maybe_await(client.actor(APIFY_HELLO_WORLD_ACTOR).call())
    if result is not None:
        successful_run = cast('Run', result)
        created_runs.append(successful_run)

    result = await maybe_await(client.actor(APIFY_HELLO_WORLD_ACTOR).call(timeout_secs=1))
    if result is not None:
        timed_out_run = cast('Run', result)
        created_runs.append(timed_out_run)

    run_collection = client.runs()

    date_obj = datetime(2100, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    iso_date_str = date_obj.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Here we test that date fields can be passed both as datetime objects and as ISO 8601 strings
    result = await maybe_await(run_collection.list(started_before=date_obj, started_after=date_obj))
    runs_in_range_date_format = cast('ListOfRuns', result)  # noqa: F841

    result = await maybe_await(run_collection.list(started_before=iso_date_str, started_after=iso_date_str))
    runs_in_range_string_format = cast('ListOfRuns', result)  # noqa: F841

    for run in created_runs:
        run_id = run.id
        if isinstance(run_id, str):
            await maybe_await(client.run(run_id).delete())

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from apify_shared.consts import ActorJobStatus

from apify_client._models import Run

if TYPE_CHECKING:
    from apify_client import ApifyClient

APIFY_HELLO_WORLD_ACTOR = 'apify/hello-world'


def test_run_collection_list_multiple_statuses(apify_client: ApifyClient) -> None:
    created_runs = list[Run]()

    successful_run = apify_client.actor(APIFY_HELLO_WORLD_ACTOR).call()
    if successful_run is not None:
        created_runs.append(successful_run)

    timed_out_run = apify_client.actor(APIFY_HELLO_WORLD_ACTOR).call(timeout_secs=1)
    if timed_out_run is not None:
        created_runs.append(timed_out_run)

    run_collection = apify_client.actor(APIFY_HELLO_WORLD_ACTOR).runs()

    multiple_status_runs = run_collection.list(status=[ActorJobStatus.SUCCEEDED, ActorJobStatus.TIMED_OUT])
    single_status_runs = run_collection.list(status=ActorJobStatus.SUCCEEDED)

    assert multiple_status_runs is not None
    assert single_status_runs is not None

    assert hasattr(multiple_status_runs, 'items')
    assert hasattr(single_status_runs, 'items')

    assert all(run.status in [ActorJobStatus.SUCCEEDED, ActorJobStatus.TIMED_OUT] for run in multiple_status_runs.items)
    assert all(run.status == ActorJobStatus.SUCCEEDED for run in single_status_runs.items)

    for run in created_runs:
        run_id = run.id
        if isinstance(run_id, str):
            apify_client.run(run_id).delete()


def test_run_collection_list_accept_date_range(apify_client: ApifyClient) -> None:
    created_runs = list[Run]()

    successful_run = apify_client.actor(APIFY_HELLO_WORLD_ACTOR).call()
    if successful_run is not None:
        created_runs.append(successful_run)

    timed_out_run = apify_client.actor(APIFY_HELLO_WORLD_ACTOR).call(timeout_secs=1)
    if timed_out_run is not None:
        created_runs.append(timed_out_run)

    run_collection = apify_client.runs()

    date_obj = datetime(2100, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    iso_date_str = date_obj.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Here we test that date fields can be passed both as datetime objects and as ISO 8601 strings
    runs_in_range_date_format = run_collection.list(started_before=date_obj, started_after=date_obj)
    runs_in_range_string_format = run_collection.list(started_before=iso_date_str, started_after=iso_date_str)

    assert hasattr(runs_in_range_date_format, 'items')
    assert hasattr(runs_in_range_string_format, 'items')

    for run in created_runs:
        run_id = run.id
        if isinstance(run_id, str):
            apify_client.run(run_id).delete()

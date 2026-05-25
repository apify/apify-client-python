"""Unified tests for run (sync + async)."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from ._utils import maybe_await, maybe_sleep
from apify_client._models import Dataset, KeyValueStore, ListOfRuns, RequestQueue, Run, RunShort
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync

HELLO_WORLD_ACTOR = 'apify/hello-world'


async def test_run_collection_list_multiple_statuses(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing runs with multiple statuses."""
    created_runs = list[Run]()

    successful_run = await maybe_await(client.actor(HELLO_WORLD_ACTOR).call())
    if successful_run is not None:
        assert isinstance(successful_run, Run)
        created_runs.append(successful_run)

    timed_out_run = await maybe_await(client.actor(HELLO_WORLD_ACTOR).call(timeout=timedelta(seconds=1)))
    if timed_out_run is not None:
        assert isinstance(timed_out_run, Run)
        created_runs.append(timed_out_run)

    try:
        run_collection = client.actor(HELLO_WORLD_ACTOR).runs()

        multiple_status_runs = await maybe_await(run_collection.list(status=['SUCCEEDED', 'TIMED-OUT']))
        assert isinstance(multiple_status_runs, ListOfRuns)

        single_status_runs = await maybe_await(run_collection.list(status='SUCCEEDED'))
        assert isinstance(single_status_runs, ListOfRuns)

        assert all(run.status in ['SUCCEEDED', 'TIMED-OUT'] for run in multiple_status_runs.items)
        assert all(run.status == 'SUCCEEDED' for run in single_status_runs.items)
    finally:
        for run in created_runs:
            run_id = run.id
            if isinstance(run_id, str):
                await maybe_await(client.run(run_id).delete())


async def test_run_collection_list_accept_date_range(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing runs with date range parameters."""
    created_runs = list[Run]()

    successful_run = await maybe_await(client.actor(HELLO_WORLD_ACTOR).call())
    if successful_run is not None:
        assert isinstance(successful_run, Run)
        created_runs.append(successful_run)

    timed_out_run = await maybe_await(client.actor(HELLO_WORLD_ACTOR).call(timeout=timedelta(seconds=1)))
    if timed_out_run is not None:
        assert isinstance(timed_out_run, Run)
        created_runs.append(timed_out_run)

    try:
        run_collection = client.runs()

        date_obj = datetime(2100, 1, 1, 0, 0, 0, tzinfo=UTC)
        iso_date_str = date_obj.strftime('%Y-%m-%dT%H:%M:%SZ')

        # Here we test that date fields can be passed both as datetime objects and as ISO 8601 strings
        await maybe_await(run_collection.list(started_before=date_obj, started_after=date_obj))

        await maybe_await(run_collection.list(started_before=iso_date_str, started_after=iso_date_str))
    finally:
        for run in created_runs:
            run_id = run.id
            if isinstance(run_id, str):
                await maybe_await(client.run(run_id).delete())


async def test_run_get_and_delete(client: ApifyClient | ApifyClientAsync) -> None:
    """Test getting and deleting a run."""
    # Run actor
    actor = client.actor(HELLO_WORLD_ACTOR)
    run = await maybe_await(actor.call())
    assert isinstance(run, Run)

    # Get the run
    run_client = client.run(run.id)
    retrieved_run = await maybe_await(run_client.get())
    assert isinstance(retrieved_run, Run)
    assert retrieved_run.id == run.id
    assert retrieved_run.status == 'SUCCEEDED'

    # Delete the run
    await maybe_await(run_client.delete())

    # Verify it's gone
    deleted_run = await maybe_await(run_client.get())
    assert deleted_run is None


async def test_run_dataset(client: ApifyClient | ApifyClientAsync) -> None:
    """Test accessing run's default dataset."""
    # Run actor
    actor = client.actor(HELLO_WORLD_ACTOR)
    run = await maybe_await(actor.call())
    assert isinstance(run, Run)

    # Access run's dataset
    run_client = client.run(run.id)

    try:
        dataset_client = run_client.dataset()

        # Get dataset info
        dataset = await maybe_await(dataset_client.get())
        assert isinstance(dataset, Dataset)
        assert dataset.id == run.default_dataset_id
    finally:
        await maybe_await(run_client.delete())


async def test_run_key_value_store(client: ApifyClient | ApifyClientAsync) -> None:
    """Test accessing run's default key-value store."""
    # Run actor
    actor = client.actor(HELLO_WORLD_ACTOR)
    run = await maybe_await(actor.call())
    assert isinstance(run, Run)

    # Access run's key-value store
    run_client = client.run(run.id)

    try:
        kvs_client = run_client.key_value_store()

        # Get KVS info
        kvs = await maybe_await(kvs_client.get())
        assert isinstance(kvs, KeyValueStore)
        assert kvs.id == run.default_key_value_store_id
    finally:
        await maybe_await(run_client.delete())


async def test_run_request_queue(client: ApifyClient | ApifyClientAsync) -> None:
    """Test accessing run's default request queue."""
    # Run actor
    actor = client.actor(HELLO_WORLD_ACTOR)
    run = await maybe_await(actor.call())
    assert isinstance(run, Run)

    # Access run's request queue
    run_client = client.run(run.id)

    try:
        rq_client = run_client.request_queue()

        # Get RQ info
        rq = await maybe_await(rq_client.get())
        assert isinstance(rq, RequestQueue)
        assert rq.id == run.default_request_queue_id
    finally:
        await maybe_await(run_client.delete())


async def test_run_abort(client: ApifyClient | ApifyClientAsync) -> None:
    """Test aborting a running Actor."""
    # Start actor without waiting
    actor = client.actor(HELLO_WORLD_ACTOR)
    run = await maybe_await(actor.start())
    assert isinstance(run, Run)
    assert run.id is not None

    # Abort the run
    run_client = client.run(run.id)

    try:
        aborted_run = await maybe_await(run_client.abort())
        assert isinstance(aborted_run, Run)
        # Status should be ABORTING or ABORTED (or SUCCEEDED if too fast)
        assert aborted_run.status in ['ABORTING', 'ABORTED', 'SUCCEEDED']

        # Wait for abort to complete
        final_run = await maybe_await(run_client.wait_for_finish())
        assert isinstance(final_run, Run)
        assert final_run.status in ['ABORTED', 'SUCCEEDED']
    finally:
        await maybe_await(run_client.wait_for_finish())
        await maybe_await(run_client.delete())


async def test_run_update(client: ApifyClient | ApifyClientAsync) -> None:
    """Test updating a run's status message."""
    # Run actor
    actor = client.actor(HELLO_WORLD_ACTOR)
    run = await maybe_await(actor.call())
    assert isinstance(run, Run)

    run_client = client.run(run.id)

    try:
        # Update run status message
        updated_run = await maybe_await(
            run_client.update(
                status_message='Test status message',
                is_status_message_terminal=True,
            )
        )
        assert isinstance(updated_run, Run)
        assert updated_run.status_message == 'Test status message'

    finally:
        await maybe_await(run_client.delete())


async def test_run_resurrect(client: ApifyClient | ApifyClientAsync) -> None:
    """Test resurrecting a finished run."""
    # Run actor and wait for it to finish
    actor = client.actor(HELLO_WORLD_ACTOR)
    run = await maybe_await(actor.call())
    assert isinstance(run, Run)
    assert run.status == 'SUCCEEDED'

    run_client = client.run(run.id)

    try:
        # Resurrect the run
        resurrected_run = await maybe_await(run_client.resurrect())
        assert isinstance(resurrected_run, Run)
        # Status should be READY, RUNNING or already finished (if fast)
        assert resurrected_run.status in ['READY', 'RUNNING', 'SUCCEEDED']

        # Wait for it to finish before deleting
        final_run = await maybe_await(run_client.wait_for_finish())
        assert isinstance(final_run, Run)
        assert final_run.status == 'SUCCEEDED'

    finally:
        # Wait for run to finish before cleanup (resurrected run might still be running)
        await maybe_await(run_client.wait_for_finish())
    await maybe_await(run_client.delete())


async def test_run_log(client: ApifyClient | ApifyClientAsync) -> None:
    """Test accessing run's log."""
    # Run actor
    actor = client.actor(HELLO_WORLD_ACTOR)
    run = await maybe_await(actor.call())
    assert isinstance(run, Run)

    run_client = client.run(run.id)

    try:
        # Get log client
        log_client = run_client.log()

        # Get log content
        log_content = await maybe_await(log_client.get())
        assert isinstance(log_content, str)
        # Log should contain something (at least actor startup messages)
        assert len(log_content) > 0

    finally:
        await maybe_await(run_client.delete())


async def test_run_runs_client(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing runs through the run collection client."""
    # List runs (should return valid data structure)
    runs_page = await maybe_await(client.runs().list(limit=10))
    assert isinstance(runs_page, ListOfRuns)
    assert runs_page.items is not None
    assert isinstance(runs_page.items, list)
    # The user may have runs, verify the structure
    if runs_page.items:
        first_run = runs_page.items[0]
        assert first_run.id is not None
        assert first_run.act_id is not None


async def test_run_metamorph(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test metamorphing a run into another Actor."""
    # Start an actor that will run long enough to metamorph. We use hello-world and try to metamorph it into itself
    actor = client.actor(HELLO_WORLD_ACTOR)
    run = await maybe_await(actor.start())
    assert isinstance(run, Run)
    assert run.id is not None

    run_client = client.run(run.id)

    try:
        # Wait a bit for the run to start properly
        await maybe_sleep(2, is_async=is_async)

        # Metamorph the run into the same actor (allowed) with new input
        # Note: hello-world may finish before we can metamorph, so we handle that case
        try:
            metamorphed_run = await maybe_await(
                run_client.metamorph(
                    target_actor_id=HELLO_WORLD_ACTOR,
                    run_input={'message': 'Hello from metamorph!'},
                )
            )
            assert isinstance(metamorphed_run, Run)
            assert metamorphed_run.id == run.id  # Same run ID

            # Wait for the metamorphed run to finish
            final_run = await maybe_await(run_client.wait_for_finish())
            assert isinstance(final_run, Run)
        except ApifyApiError as exc:
            # If the actor finished before we could metamorph, that's OK - the test still verified the API call
            if 'already finished' not in str(exc):
                raise

    finally:
        await maybe_await(run_client.wait_for_finish())
    await maybe_await(run_client.delete())


async def test_run_reboot(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test rebooting a running Actor."""
    # Start an actor
    actor = client.actor(HELLO_WORLD_ACTOR)
    run = await maybe_await(actor.start())
    assert isinstance(run, Run)
    assert run.id is not None

    run_client = client.run(run.id)

    try:
        # Wait a bit and check if the run is still running
        await maybe_sleep(1, is_async=is_async)
        current_run = await maybe_await(run_client.get())

        # Only try to reboot if the run is still running
        # Note: There's a race condition - run may finish between check and reboot call
        if isinstance(current_run, Run) and current_run.status == 'RUNNING':
            try:
                rebooted_run = await maybe_await(run_client.reboot())
                assert isinstance(rebooted_run, Run)
                assert rebooted_run.id == run.id
            except ApifyApiError as exc:
                # If the actor finished before we could reboot, that's OK
                if 'already finished' not in str(exc):
                    raise

        # Wait for the run to finish
        final_run = await maybe_await(run_client.wait_for_finish())
        assert isinstance(final_run, Run)

    finally:
        await maybe_await(run_client.wait_for_finish())
    await maybe_await(run_client.delete())


async def test_run_charge(client: ApifyClient | ApifyClientAsync) -> None:
    """Test charging for an event in a pay-per-event run."""
    # Run an actor
    actor = client.actor(HELLO_WORLD_ACTOR)
    run = await maybe_await(actor.call())
    assert isinstance(run, Run)

    run_client = client.run(run.id)

    try:
        # Try to charge - this will fail for non-PPE actors but tests the API call
        try:
            await maybe_await(run_client.charge('test-event', count=1))
            # If it succeeds, the actor supports PPE
        except ApifyApiError as exc:
            # Expected error for non-PPE actors - re-raise if unexpected.
            # The API returns an error indicating this is not a PPE run.
            if exc.status_code not in [400, 403, 404]:
                raise

    finally:
        await maybe_await(run_client.delete())


async def test_runs_iterate(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test paginated iteration over user runs."""
    iterator = client.runs().iterate(limit=5)
    collected: list[RunShort] = []
    if is_async:
        assert isinstance(iterator, AsyncIterator)
        async for run in iterator:
            assert isinstance(run, RunShort)
            collected.append(run)
    else:
        assert isinstance(iterator, Iterator)
        for run in iterator:
            assert isinstance(run, RunShort)
            collected.append(run)

    assert len(collected) <= 5
    for run in collected:
        assert run.id is not None
        assert run.act_id is not None


async def test_run_collection_list_desc(client: ApifyClient | ApifyClientAsync) -> None:
    """Test that desc=True returns runs sorted by started_at descending."""
    runs_page = await maybe_await(client.runs().list(limit=10, desc=True))
    assert isinstance(runs_page, ListOfRuns)

    # The user run feed is shared across parallel test workers — brand-new RUNNING runs may
    # briefly lack `started_at`. Compare ordering on the timestamps that are present.
    timestamps = [run.started_at for run in runs_page.items if run.started_at is not None]
    if len(timestamps) >= 2:
        assert timestamps == sorted(timestamps, reverse=True)


async def test_run_get_nonexistent_returns_none(client: ApifyClient | ApifyClientAsync) -> None:
    """Test that get() on a non-existent run returns None."""
    run = await maybe_await(client.run('NoNExIsTeNtRuNiD123').get())
    assert run is None


async def test_run_collection_iterate_actor_runs(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test iterating over runs of a specific Actor."""
    actor = client.actor(HELLO_WORLD_ACTOR)
    # Ensure at least one run exists
    run = await maybe_await(actor.call())
    assert isinstance(run, Run)

    try:
        iterator = actor.runs().iterate(limit=3, desc=True)
        collected: list[RunShort] = []
        if is_async:
            assert isinstance(iterator, AsyncIterator)
            async for r in iterator:
                assert isinstance(r, RunShort)
                collected.append(r)
        else:
            assert isinstance(iterator, Iterator)
            for r in iterator:
                assert isinstance(r, RunShort)
                collected.append(r)

        assert len(collected) >= 1
        # All returned runs must be scoped to the requested actor.
        assert all(r.act_id == run.act_id for r in collected)
    finally:
        await maybe_await(client.run(run.id).delete())

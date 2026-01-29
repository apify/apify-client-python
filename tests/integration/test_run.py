"""Unified tests for run (sync + async)."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync
    from apify_client._models import Dataset, KeyValueStore, ListOfRuns, RequestQueue, Run


from datetime import datetime, timezone

from .conftest import maybe_await, maybe_sleep
from apify_client._models import ActorJobStatus, Run
from apify_client.errors import ApifyApiError

HELLO_WORLD_ACTOR = 'apify/hello-world'


async def test_run_collection_list_multiple_statuses(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing runs with multiple statuses."""
    created_runs = list[Run]()

    result = await maybe_await(client.actor(HELLO_WORLD_ACTOR).call())
    if result is not None:
        successful_run = cast('Run', result)
        created_runs.append(successful_run)

    result = await maybe_await(client.actor(HELLO_WORLD_ACTOR).call(timeout_secs=1))
    if result is not None:
        timed_out_run = cast('Run', result)
        created_runs.append(timed_out_run)

    run_collection = client.actor(HELLO_WORLD_ACTOR).runs()

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

    result = await maybe_await(client.actor(HELLO_WORLD_ACTOR).call())
    if result is not None:
        successful_run = cast('Run', result)
        created_runs.append(successful_run)

    result = await maybe_await(client.actor(HELLO_WORLD_ACTOR).call(timeout_secs=1))
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


async def test_run_get_and_delete(client: ApifyClient | ApifyClientAsync) -> None:
    """Test getting and deleting a run."""
    # Run actor
    actor = client.actor(HELLO_WORLD_ACTOR)
    result = await maybe_await(actor.call())
    run = cast('Run', result)
    assert run is not None

    # Get the run
    run_client = client.run(run.id)
    result = await maybe_await(run_client.get())
    retrieved_run = cast('Run', result)
    assert retrieved_run is not None
    assert retrieved_run.id == run.id
    assert retrieved_run.status.value == 'SUCCEEDED'

    # Delete the run
    await maybe_await(run_client.delete())

    # Verify it's gone
    deleted_run = await maybe_await(run_client.get())
    assert deleted_run is None


async def test_run_dataset(client: ApifyClient | ApifyClientAsync) -> None:
    """Test accessing run's default dataset."""
    # Run actor
    actor = client.actor(HELLO_WORLD_ACTOR)
    result = await maybe_await(actor.call())
    run = cast('Run', result)
    assert run is not None

    # Access run's dataset
    run_client = client.run(run.id)
    dataset_client = run_client.dataset()

    # Get dataset info
    result = await maybe_await(dataset_client.get())
    dataset = cast('Dataset', result)
    assert dataset is not None
    assert dataset.id == run.default_dataset_id

    # Cleanup
    await maybe_await(run_client.delete())


async def test_run_key_value_store(client: ApifyClient | ApifyClientAsync) -> None:
    """Test accessing run's default key-value store."""
    # Run actor
    actor = client.actor(HELLO_WORLD_ACTOR)
    result = await maybe_await(actor.call())
    run = cast('Run', result)
    assert run is not None

    # Access run's key-value store
    run_client = client.run(run.id)
    kvs_client = run_client.key_value_store()

    # Get KVS info
    result = await maybe_await(kvs_client.get())
    kvs = cast('KeyValueStore', result)
    assert kvs is not None
    assert kvs.id == run.default_key_value_store_id

    # Cleanup
    await maybe_await(run_client.delete())


async def test_run_request_queue(client: ApifyClient | ApifyClientAsync) -> None:
    """Test accessing run's default request queue."""
    # Run actor
    actor = client.actor(HELLO_WORLD_ACTOR)
    result = await maybe_await(actor.call())
    run = cast('Run', result)
    assert run is not None

    # Access run's request queue
    run_client = client.run(run.id)
    rq_client = run_client.request_queue()

    # Get RQ info
    result = await maybe_await(rq_client.get())
    rq = cast('RequestQueue', result)
    assert rq is not None
    assert rq.id == run.default_request_queue_id

    # Cleanup
    await maybe_await(run_client.delete())


async def test_run_abort(client: ApifyClient | ApifyClientAsync) -> None:
    """Test aborting a running Actor."""
    # Start actor without waiting
    actor = client.actor(HELLO_WORLD_ACTOR)
    result = await maybe_await(actor.start())
    run = cast('Run', result)
    assert run is not None
    assert run.id is not None

    # Abort the run
    run_client = client.run(run.id)
    result = await maybe_await(run_client.abort())
    aborted_run = cast('Run', result)

    assert aborted_run is not None
    # Status should be ABORTING or ABORTED (or SUCCEEDED if too fast)
    assert aborted_run.status.value in ['ABORTING', 'ABORTED', 'SUCCEEDED']

    # Wait for abort to complete
    result = await maybe_await(run_client.wait_for_finish())
    final_run = cast('Run', result)
    assert final_run is not None
    assert final_run.status.value in ['ABORTED', 'SUCCEEDED']

    # Cleanup
    await maybe_await(run_client.delete())


async def test_run_update(client: ApifyClient | ApifyClientAsync) -> None:
    """Test updating a run's status message."""
    # Run actor
    actor = client.actor(HELLO_WORLD_ACTOR)
    result = await maybe_await(actor.call())
    run = cast('Run', result)
    assert run is not None

    run_client = client.run(run.id)

    try:
        # Update run status message
        result = await maybe_await(
            run_client.update(
                status_message='Test status message',
                is_status_message_terminal=True,
            )
        )
        updated_run = cast('Run', result)
        assert updated_run is not None
        assert updated_run.status_message == 'Test status message'

    finally:
        # Cleanup
        await maybe_await(run_client.delete())


async def test_run_resurrect(client: ApifyClient | ApifyClientAsync) -> None:
    """Test resurrecting a finished run."""
    # Run actor and wait for it to finish
    actor = client.actor(HELLO_WORLD_ACTOR)
    result = await maybe_await(actor.call())
    run = cast('Run', result)
    assert run is not None
    assert run.status.value == 'SUCCEEDED'

    run_client = client.run(run.id)

    try:
        # Resurrect the run
        result = await maybe_await(run_client.resurrect())
        resurrected_run = cast('Run', result)
        assert resurrected_run is not None
        # Status should be READY, RUNNING or already finished (if fast)
        assert resurrected_run.status.value in ['READY', 'RUNNING', 'SUCCEEDED']

        # Wait for it to finish before deleting
        result = await maybe_await(run_client.wait_for_finish())
        final_run = cast('Run', result)
        assert final_run is not None
        assert final_run.status.value == 'SUCCEEDED'

    finally:
        # Wait for run to finish before cleanup (resurrected run might still be running)
        await maybe_await(run_client.wait_for_finish())
        await maybe_await(run_client.delete())


async def test_run_log(client: ApifyClient | ApifyClientAsync) -> None:
    """Test accessing run's log."""
    # Run actor
    actor = client.actor(HELLO_WORLD_ACTOR)
    result = await maybe_await(actor.call())
    run = cast('Run', result)
    assert run is not None

    run_client = client.run(run.id)

    try:
        # Get log client
        log_client = run_client.log()

        # Get log content
        result = await maybe_await(log_client.get())
        log_content = cast('str', result)
        assert log_content is not None
        # Log should contain something (at least actor startup messages)
        assert len(log_content) > 0

    finally:
        # Cleanup
        await maybe_await(run_client.delete())


async def test_run_runs_client(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing runs through the run collection client."""
    # List runs (should return valid data structure)
    result = await maybe_await(client.runs().list(limit=10))
    runs_page = cast('ListOfRuns', result)
    assert runs_page is not None
    assert runs_page.items is not None
    assert isinstance(runs_page.items, list)
    # The user may have runs, verify the structure
    if runs_page.items:
        first_run = runs_page.items[0]
        assert first_run.id is not None
        assert first_run.act_id is not None


async def test_run_metamorph(client: ApifyClient | ApifyClientAsync, is_async: bool) -> None:  # noqa: FBT001
    """Test metamorphing a run into another Actor."""
    # Start an actor that will run long enough to metamorph. We use hello-world and try to metamorph it into itself
    actor = client.actor(HELLO_WORLD_ACTOR)
    result = await maybe_await(actor.start())
    run = cast('Run', result)
    assert run is not None
    assert run.id is not None

    run_client = client.run(run.id)

    try:
        # Wait a bit for the run to start properly
        await maybe_sleep(2, is_async=is_async)

        # Metamorph the run into the same actor (allowed) with new input
        # Note: hello-world may finish before we can metamorph, so we handle that case
        try:
            result = await maybe_await(
                run_client.metamorph(
                    target_actor_id=HELLO_WORLD_ACTOR,
                    run_input={'message': 'Hello from metamorph!'},
                )
            )
            metamorphed_run = cast('Run', result)
            assert metamorphed_run is not None
            assert metamorphed_run.id == run.id  # Same run ID

            # Wait for the metamorphed run to finish
            result = await maybe_await(run_client.wait_for_finish())
            final_run = cast('Run', result)
            assert final_run is not None
        except ApifyApiError as exc:
            # If the actor finished before we could metamorph, that's OK - the test still verified the API call
            if 'already finished' not in str(exc):
                raise

    finally:
        # Cleanup
        await maybe_await(run_client.wait_for_finish())
        await maybe_await(run_client.delete())


async def test_run_reboot(client: ApifyClient | ApifyClientAsync, is_async: bool) -> None:  # noqa: FBT001
    """Test rebooting a running Actor."""
    # Start an actor
    actor = client.actor(HELLO_WORLD_ACTOR)
    result = await maybe_await(actor.start())
    run = cast('Run', result)
    assert run is not None
    assert run.id is not None

    run_client = client.run(run.id)

    try:
        # Wait a bit and check if the run is still running
        await maybe_sleep(1, is_async=is_async)
        result = await maybe_await(run_client.get())
        current_run = cast('Run | None', result)

        # Only try to reboot if the run is still running
        # Note: There's a race condition - run may finish between check and reboot call
        if current_run and current_run.status.value == 'RUNNING':
            try:
                result = await maybe_await(run_client.reboot())
                rebooted_run = cast('Run', result)
                assert rebooted_run is not None
                assert rebooted_run.id == run.id
            except ApifyApiError as exc:
                # If the actor finished before we could reboot, that's OK
                if 'already finished' not in str(exc):
                    raise

        # Wait for the run to finish
        result = await maybe_await(run_client.wait_for_finish())
        final_run = cast('Run', result)
        assert final_run is not None

    finally:
        # Cleanup
        await maybe_await(run_client.wait_for_finish())
        await maybe_await(run_client.delete())


async def test_run_charge(client: ApifyClient | ApifyClientAsync) -> None:
    """Test charging for an event in a pay-per-event run.

    Note: This test may fail if the actor is not a pay-per-event actor. The test verifies that the charge method can
    be called correctly.
    """
    # Run an actor
    actor = client.actor(HELLO_WORLD_ACTOR)
    result = await maybe_await(actor.call())
    run = cast('Run', result)
    assert run is not None

    run_client = client.run(run.id)

    try:
        # Try to charge - this will fail for non-PPE actors but tests the API call
        try:
            await maybe_await(run_client.charge(event_name='test-event', count=1))
            # If it succeeds, the actor supports PPE
        except ApifyApiError as exc:
            # Expected error for non-PPE actors - re-raise if unexpected.
            # The API returns an error indicating this is not a PPE run.
            if exc.status_code not in [400, 403, 404]:
                raise

    finally:
        # Cleanup
        await maybe_await(run_client.delete())

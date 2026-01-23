from __future__ import annotations

import time
from typing import TYPE_CHECKING

from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from apify_client import ApifyClient

HELLO_WORLD_ACTOR = 'apify/hello-world'


def test_run_get_and_delete(apify_client: ApifyClient) -> None:
    """Test getting and deleting a run."""
    # Run actor
    actor = apify_client.actor(HELLO_WORLD_ACTOR)
    run = actor.call()
    assert run is not None

    # Get the run
    run_client = apify_client.run(run.id)
    retrieved_run = run_client.get()
    assert retrieved_run is not None
    assert retrieved_run.id == run.id
    assert retrieved_run.status.value == 'SUCCEEDED'

    # Delete the run
    run_client.delete()

    # Verify it's gone
    deleted_run = run_client.get()
    assert deleted_run is None


def test_run_dataset(apify_client: ApifyClient) -> None:
    """Test accessing run's default dataset."""
    # Run actor
    actor = apify_client.actor(HELLO_WORLD_ACTOR)
    run = actor.call()
    assert run is not None

    # Access run's dataset
    run_client = apify_client.run(run.id)
    dataset_client = run_client.dataset()

    # Get dataset info
    dataset = dataset_client.get()
    assert dataset is not None
    assert dataset.id == run.default_dataset_id

    # Cleanup
    run_client.delete()


def test_run_key_value_store(apify_client: ApifyClient) -> None:
    """Test accessing run's default key-value store."""
    # Run actor
    actor = apify_client.actor(HELLO_WORLD_ACTOR)
    run = actor.call()
    assert run is not None

    # Access run's key-value store
    run_client = apify_client.run(run.id)
    kvs_client = run_client.key_value_store()

    # Get KVS info
    kvs = kvs_client.get()
    assert kvs is not None
    assert kvs.id == run.default_key_value_store_id

    # Cleanup
    run_client.delete()


def test_run_request_queue(apify_client: ApifyClient) -> None:
    """Test accessing run's default request queue."""
    # Run actor
    actor = apify_client.actor(HELLO_WORLD_ACTOR)
    run = actor.call()
    assert run is not None

    # Access run's request queue
    run_client = apify_client.run(run.id)
    rq_client = run_client.request_queue()

    # Get RQ info
    rq = rq_client.get()
    assert rq is not None
    assert rq.id == run.default_request_queue_id

    # Cleanup
    run_client.delete()


def test_run_abort(apify_client: ApifyClient) -> None:
    """Test aborting a running actor."""
    # Start actor without waiting
    actor = apify_client.actor(HELLO_WORLD_ACTOR)
    run = actor.start()
    assert run is not None
    assert run.id is not None

    # Abort the run
    run_client = apify_client.run(run.id)
    aborted_run = run_client.abort()

    assert aborted_run is not None
    # Status should be ABORTING or ABORTED (or SUCCEEDED if too fast)
    assert aborted_run.status.value in ['ABORTING', 'ABORTED', 'SUCCEEDED']

    # Wait for abort to complete
    final_run = run_client.wait_for_finish()
    assert final_run is not None
    assert final_run.status.value in ['ABORTED', 'SUCCEEDED']

    # Cleanup
    run_client.delete()


def test_run_update(apify_client: ApifyClient) -> None:
    """Test updating a run's status message."""
    # Run actor
    actor = apify_client.actor(HELLO_WORLD_ACTOR)
    run = actor.call()
    assert run is not None

    run_client = apify_client.run(run.id)

    try:
        # Update run status message
        updated_run = run_client.update(
            status_message='Test status message',
            is_status_message_terminal=True,
        )
        assert updated_run is not None
        assert updated_run.status_message == 'Test status message'

    finally:
        # Cleanup
        run_client.delete()


def test_run_resurrect(apify_client: ApifyClient) -> None:
    """Test resurrecting a finished run."""
    # Run actor and wait for it to finish
    actor = apify_client.actor(HELLO_WORLD_ACTOR)
    run = actor.call()
    assert run is not None
    assert run.status.value == 'SUCCEEDED'

    run_client = apify_client.run(run.id)

    try:
        # Resurrect the run
        resurrected_run = run_client.resurrect()
        assert resurrected_run is not None
        # Status should be READY, RUNNING or already finished (if fast)
        assert resurrected_run.status.value in ['READY', 'RUNNING', 'SUCCEEDED']

        # Wait for it to finish before deleting
        final_run = run_client.wait_for_finish()
        assert final_run is not None
        assert final_run.status.value == 'SUCCEEDED'

    finally:
        # Wait for run to finish before cleanup (resurrected run might still be running)
        run_client.wait_for_finish()
        run_client.delete()


def test_run_log(apify_client: ApifyClient) -> None:
    """Test accessing run's log."""
    # Run actor
    actor = apify_client.actor(HELLO_WORLD_ACTOR)
    run = actor.call()
    assert run is not None

    run_client = apify_client.run(run.id)

    try:
        # Get log client
        log_client = run_client.log()

        # Get log content
        log_content = log_client.get()
        assert log_content is not None
        # Log should contain something (at least actor startup messages)
        assert len(log_content) > 0

    finally:
        # Cleanup
        run_client.delete()


def test_run_runs_client(apify_client: ApifyClient) -> None:
    """Test listing runs through the run collection client."""
    # List runs (should return valid data structure)
    runs_page = apify_client.runs().list(limit=10)
    assert runs_page is not None
    assert runs_page.items is not None
    assert isinstance(runs_page.items, list)
    # The user may have runs, verify the structure
    if runs_page.items:
        first_run = runs_page.items[0]
        assert first_run.id is not None
        assert first_run.act_id is not None


def test_run_metamorph(apify_client: ApifyClient) -> None:
    """Test metamorphing a run into another actor."""
    # Start an actor that will run long enough to metamorph. We use hello-world and try to metamorph it into itself
    actor = apify_client.actor(HELLO_WORLD_ACTOR)
    run = actor.start()
    assert run is not None
    assert run.id is not None

    run_client = apify_client.run(run.id)

    try:
        # Wait a bit for the run to start properly
        time.sleep(2)

        # Metamorph the run into the same actor (allowed) with new input
        metamorphed_run = run_client.metamorph(
            target_actor_id=HELLO_WORLD_ACTOR,
            run_input={'message': 'Hello from metamorph!'},
        )
        assert metamorphed_run is not None
        assert metamorphed_run.id == run.id  # Same run ID

        # Wait for the metamorphed run to finish
        final_run = run_client.wait_for_finish()
        assert final_run is not None

    finally:
        # Cleanup
        run_client.wait_for_finish()
        run_client.delete()


def test_run_reboot(apify_client: ApifyClient) -> None:
    """Test rebooting a running actor."""
    # Start an actor
    actor = apify_client.actor(HELLO_WORLD_ACTOR)
    run = actor.start()
    assert run is not None
    assert run.id is not None

    run_client = apify_client.run(run.id)

    try:
        # Wait a bit and check if the run is still running
        time.sleep(1)
        current_run = run_client.get()

        # Only try to reboot if the run is still running
        if current_run and current_run.status.value == 'RUNNING':
            rebooted_run = run_client.reboot()
            assert rebooted_run is not None
            assert rebooted_run.id == run.id

        # Wait for the run to finish
        final_run = run_client.wait_for_finish()
        assert final_run is not None

    finally:
        # Cleanup
        run_client.wait_for_finish()
        run_client.delete()


def test_run_charge(apify_client: ApifyClient) -> None:
    """Test charging for an event in a pay-per-event run.

    Note: This test may fail if the actor is not a pay-per-event actor. The test verifies that the charge method can
    be called correctly.
    """
    # Run an actor
    actor = apify_client.actor(HELLO_WORLD_ACTOR)
    run = actor.call()
    assert run is not None

    run_client = apify_client.run(run.id)

    try:
        # Try to charge - this will fail for non-PPE actors but tests the API call
        try:
            run_client.charge(event_name='test-event', count=1)
            # If it succeeds, the actor supports PPE
        except ApifyApiError as exc:
            # Expected error for non-PPE actors - re-raise if unexpected.
            # The API returns an error indicating this is not a PPE run.
            if exc.status_code not in [400, 403, 404]:
                raise

    finally:
        # Cleanup
        run_client.delete()

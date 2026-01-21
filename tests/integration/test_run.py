from __future__ import annotations

from typing import TYPE_CHECKING

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

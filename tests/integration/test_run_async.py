from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from apify_client import ApifyClientAsync

HELLO_WORLD_ACTOR = 'apify/hello-world'


@pytest.mark.asyncio
async def test_run_get_and_delete(apify_client_async: ApifyClientAsync) -> None:
    """Test getting and deleting a run."""
    # Run actor
    actor = apify_client_async.actor(HELLO_WORLD_ACTOR)
    run = await actor.call()
    assert run is not None

    # Get the run
    run_client = apify_client_async.run(run.id)
    retrieved_run = await run_client.get()
    assert retrieved_run is not None
    assert retrieved_run.id == run.id
    assert retrieved_run.status.value == 'SUCCEEDED'

    # Delete the run
    await run_client.delete()

    # Verify it's gone
    deleted_run = await run_client.get()
    assert deleted_run is None


@pytest.mark.asyncio
async def test_run_dataset(apify_client_async: ApifyClientAsync) -> None:
    """Test accessing run's default dataset."""
    # Run actor
    actor = apify_client_async.actor(HELLO_WORLD_ACTOR)
    run = await actor.call()
    assert run is not None

    # Access run's dataset
    run_client = apify_client_async.run(run.id)
    dataset_client = run_client.dataset()

    # Get dataset info
    dataset = await dataset_client.get()
    assert dataset is not None
    assert dataset.id == run.default_dataset_id

    # Cleanup
    await run_client.delete()


@pytest.mark.asyncio
async def test_run_key_value_store(apify_client_async: ApifyClientAsync) -> None:
    """Test accessing run's default key-value store."""
    # Run actor
    actor = apify_client_async.actor(HELLO_WORLD_ACTOR)
    run = await actor.call()
    assert run is not None

    # Access run's key-value store
    run_client = apify_client_async.run(run.id)
    kvs_client = run_client.key_value_store()

    # Get KVS info
    kvs = await kvs_client.get()
    assert kvs is not None
    assert kvs.id == run.default_key_value_store_id

    # Cleanup
    await run_client.delete()


@pytest.mark.asyncio
async def test_run_request_queue(apify_client_async: ApifyClientAsync) -> None:
    """Test accessing run's default request queue."""
    # Run actor
    actor = apify_client_async.actor(HELLO_WORLD_ACTOR)
    run = await actor.call()
    assert run is not None

    # Access run's request queue
    run_client = apify_client_async.run(run.id)
    rq_client = run_client.request_queue()

    # Get RQ info
    rq = await rq_client.get()
    assert rq is not None
    assert rq.id == run.default_request_queue_id

    # Cleanup
    await run_client.delete()


@pytest.mark.asyncio
async def test_run_abort(apify_client_async: ApifyClientAsync) -> None:
    """Test aborting a running actor."""
    # Start actor without waiting
    actor = apify_client_async.actor(HELLO_WORLD_ACTOR)
    run = await actor.start()
    assert run is not None
    assert run.id is not None

    # Abort the run
    run_client = apify_client_async.run(run.id)
    aborted_run = await run_client.abort()

    assert aborted_run is not None
    # Status should be ABORTING or ABORTED (or SUCCEEDED if too fast)
    assert aborted_run.status.value in ['ABORTING', 'ABORTED', 'SUCCEEDED']

    # Wait for abort to complete
    final_run = await run_client.wait_for_finish()
    assert final_run is not None
    assert final_run.status.value in ['ABORTED', 'SUCCEEDED']

    # Cleanup
    await run_client.delete()

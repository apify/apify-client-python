from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from apify_client import ApifyClientAsync

# Use a simple, fast public actor for testing
HELLO_WORLD_ACTOR = 'apify/hello-world'


@pytest.mark.asyncio
async def test_log_get_from_run(apify_client_async: ApifyClientAsync) -> None:
    """Test retrieving log from an actor run."""
    # Run hello-world actor
    actor = apify_client_async.actor(HELLO_WORLD_ACTOR)
    run = await actor.call()
    assert run is not None

    # Get log as text
    run_client = apify_client_async.run(run.id)
    log = await run_client.log().get()

    assert log is not None
    assert isinstance(log, str)
    assert len(log) > 0

    # Cleanup
    await run_client.delete()


@pytest.mark.asyncio
async def test_log_get_from_build(apify_client_async: ApifyClientAsync) -> None:
    """Test retrieving log from a build."""
    # Get a build from hello-world actor
    actor = apify_client_async.actor(HELLO_WORLD_ACTOR)
    builds_page = await actor.builds().list(limit=1)
    assert builds_page.items
    build_id = builds_page.items[0]['id']

    # Get log from the build
    build = apify_client_async.build(build_id)
    log = await build.log().get()

    # Build log may be None or empty for some builds
    if log is not None:
        assert isinstance(log, str)


@pytest.mark.asyncio
async def test_log_get_as_bytes(apify_client_async: ApifyClientAsync) -> None:
    """Test retrieving log as raw bytes."""
    # Run hello-world actor
    actor = apify_client_async.actor(HELLO_WORLD_ACTOR)
    run = await actor.call()
    assert run is not None

    # Get log as bytes
    run_client = apify_client_async.run(run.id)
    log_bytes = await run_client.log().get_as_bytes()

    assert log_bytes is not None
    assert isinstance(log_bytes, bytes)
    assert len(log_bytes) > 0

    # Cleanup
    await run_client.delete()

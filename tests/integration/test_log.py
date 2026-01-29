"""Unified tests for log (sync + async)."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync
    from apify_client._models import ListOfBuilds, Run


from .conftest import maybe_await

# Use a simple, fast public actor for testing
HELLO_WORLD_ACTOR = 'apify/hello-world'


async def test_log_get_from_run(client: ApifyClient | ApifyClientAsync) -> None:
    """Test retrieving log from an Actor run."""
    # Run hello-world actor
    actor = client.actor(HELLO_WORLD_ACTOR)
    result = await maybe_await(actor.call())
    assert result is not None
    run = cast('Run', result)

    # Get log as text
    run_client = client.run(run.id)
    log = await maybe_await(run_client.log().get())

    assert log is not None
    assert isinstance(log, str)
    assert len(log) > 0

    # Cleanup
    await maybe_await(run_client.delete())


async def test_log_get_from_build(client: ApifyClient | ApifyClientAsync) -> None:
    """Test retrieving log from a build."""
    # Get a build from hello-world actor
    actor = client.actor(HELLO_WORLD_ACTOR)
    result = await maybe_await(actor.builds().list(limit=1))
    builds_page = cast('ListOfBuilds', result)
    assert builds_page.items
    build_id = builds_page.items[0].id

    # Get log from the build
    build = client.build(build_id)
    log = await maybe_await(build.log().get())

    # Build log may be None or empty for some builds
    if log is not None:
        assert isinstance(log, str)


async def test_log_get_as_bytes(client: ApifyClient | ApifyClientAsync) -> None:
    """Test retrieving log as raw bytes."""
    # Run hello-world actor
    actor = client.actor(HELLO_WORLD_ACTOR)
    result = await maybe_await(actor.call())
    assert result is not None
    run = cast('Run', result)

    # Get log as bytes
    run_client = client.run(run.id)
    log_bytes = await maybe_await(run_client.log().get_as_bytes())

    assert log_bytes is not None
    assert isinstance(log_bytes, bytes)
    assert len(log_bytes) > 0

    # Cleanup
    await maybe_await(run_client.delete())

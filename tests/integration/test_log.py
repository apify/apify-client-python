from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apify_client import ApifyClient

# Use a simple, fast public actor for testing
HELLO_WORLD_ACTOR = 'apify/hello-world'


def test_log_get_from_run(apify_client: ApifyClient) -> None:
    """Test retrieving log from an actor run."""
    # Run hello-world actor
    actor = apify_client.actor(HELLO_WORLD_ACTOR)
    run = actor.call()
    assert run is not None

    # Get log as text
    run_client = apify_client.run(run.id)
    log = run_client.log().get()

    assert log is not None
    assert isinstance(log, str)
    assert len(log) > 0

    # Cleanup
    run_client.delete()


def test_log_get_from_build(apify_client: ApifyClient) -> None:
    """Test retrieving log from a build."""
    # Get a build from hello-world actor
    actor = apify_client.actor(HELLO_WORLD_ACTOR)
    builds_page = actor.builds().list(limit=1)
    assert builds_page.items
    build_id = builds_page.items[0].id

    # Get log from the build
    build = apify_client.build(build_id)
    log = build.log().get()

    # Build log may be None or empty for some builds
    if log is not None:
        assert isinstance(log, str)


def test_log_get_as_bytes(apify_client: ApifyClient) -> None:
    """Test retrieving log as raw bytes."""
    # Run hello-world actor
    actor = apify_client.actor(HELLO_WORLD_ACTOR)
    run = actor.call()
    assert run is not None

    # Get log as bytes
    run_client = apify_client.run(run.id)
    log_bytes = run_client.log().get_as_bytes()

    assert log_bytes is not None
    assert isinstance(log_bytes, bytes)
    assert len(log_bytes) > 0

    # Cleanup
    run_client.delete()

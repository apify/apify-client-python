from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apify_client import ApifyClient

# Use a public actor that has builds available
HELLO_WORLD_ACTOR = 'apify/hello-world'


def test_build_list_for_actor(apify_client: ApifyClient) -> None:
    """Test listing builds for a public actor."""
    # Get builds for hello-world actor
    actor = apify_client.actor(HELLO_WORLD_ACTOR)
    builds_page = actor.builds().list(limit=10)

    assert builds_page is not None
    assert builds_page.items is not None
    assert len(builds_page.items) > 0  # hello-world should have at least one build

    # Verify build structure
    first_build = builds_page.items[0]
    assert first_build.id is not None
    assert first_build.act_id is not None


def test_build_get(apify_client: ApifyClient) -> None:
    """Test getting a specific build."""
    # First list builds to get a build ID
    actor = apify_client.actor(HELLO_WORLD_ACTOR)
    builds_page = actor.builds().list(limit=1)
    assert builds_page.items
    build_id = builds_page.items[0].id

    # Get the specific build
    build = apify_client.build(build_id).get()

    assert build is not None
    assert build.id == build_id
    assert build.act_id is not None
    assert build.status is not None


def test_user_builds_list(apify_client: ApifyClient) -> None:
    """Test listing all user builds."""
    # List user's builds (may be empty if user has no actors)
    builds_page = apify_client.builds().list(limit=10)

    assert builds_page is not None
    assert builds_page.items is not None
    # User may have 0 builds, so we just check the structure
    assert isinstance(builds_page.items, list)


def test_build_log(apify_client: ApifyClient) -> None:
    """Test getting build log."""
    # First list builds to get a completed build ID
    actor = apify_client.actor(HELLO_WORLD_ACTOR)
    builds_page = actor.builds().list(limit=5)
    assert builds_page.items

    # Find a completed build (SUCCEEDED status)
    completed_build = None
    for build in builds_page.items:
        if build.status and build.status.value == 'SUCCEEDED':
            completed_build = build
            break

    if completed_build is None:
        # If no succeeded build found, use any build
        completed_build = builds_page.items[0]

    # Get the build log
    log_client = apify_client.build(completed_build.id).log()
    log_content = log_client.get()

    # Build logs should be available for completed builds
    assert log_content is not None


def test_build_wait_for_finish(apify_client: ApifyClient) -> None:
    """Test wait_for_finish on an already completed build."""
    # First list builds to get a completed build ID
    actor = apify_client.actor(HELLO_WORLD_ACTOR)
    builds_page = actor.builds().list(limit=5)
    assert builds_page.items

    # Find a completed build (SUCCEEDED status)
    completed_build = None
    for build in builds_page.items:
        if build.status and build.status.value == 'SUCCEEDED':
            completed_build = build
            break

    if completed_build is None:
        # If no succeeded build found, use any finished build
        for build in builds_page.items:
            if build.status and build.status.value in ('SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED_OUT'):
                completed_build = build
                break

    if completed_build is None:
        completed_build = builds_page.items[0]

    # Wait for finish on already completed build (should return immediately)
    build = apify_client.build(completed_build.id).wait_for_finish(wait_secs=5)

    assert build is not None
    assert build.id == completed_build.id

"""Unified tests for build (sync + async)."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync
    from apify_client._models import Actor, Build, ListOfBuilds


from .conftest import maybe_await
from .utils import get_random_resource_name

# Use a public actor that has builds available
HELLO_WORLD_ACTOR = 'apify/hello-world'


async def test_build_list_for_actor(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing builds for a public Actor."""
    # Get builds for hello-world actor
    actor = client.actor(HELLO_WORLD_ACTOR)
    result = await maybe_await(actor.builds().list(limit=10))
    builds_page = cast('ListOfBuilds', result)

    assert builds_page is not None
    assert builds_page.items is not None
    assert len(builds_page.items) > 0  # hello-world should have at least one build

    # Verify build structure
    first_build = builds_page.items[0]
    assert first_build.id is not None
    assert first_build.act_id is not None


async def test_build_get(client: ApifyClient | ApifyClientAsync) -> None:
    """Test getting a specific build."""
    # First list builds to get a build ID
    actor = client.actor(HELLO_WORLD_ACTOR)
    result = await maybe_await(actor.builds().list(limit=1))
    builds_page = cast('ListOfBuilds', result)
    assert builds_page.items
    build_id = builds_page.items[0].id

    # Get the specific build
    result = await maybe_await(client.build(build_id).get())
    build = cast('Build | None', result)

    assert build is not None
    assert build.id == build_id
    assert build.act_id is not None
    assert build.status is not None


async def test_user_builds_list(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing all user builds."""
    # List user's builds (may be empty if user has no actors)
    result = await maybe_await(client.builds().list(limit=10))
    builds_page = cast('ListOfBuilds', result)

    assert builds_page is not None
    assert builds_page.items is not None
    # User may have 0 builds, so we just check the structure
    assert isinstance(builds_page.items, list)


async def test_build_log(client: ApifyClient | ApifyClientAsync) -> None:
    """Test getting build log."""
    # First list builds to get a completed build ID
    actor = client.actor(HELLO_WORLD_ACTOR)
    result = await maybe_await(actor.builds().list(limit=5))
    builds_page = cast('ListOfBuilds', result)
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
    log_client = client.build(completed_build.id).log()
    log_content = await maybe_await(log_client.get())

    # Build logs should be available for completed builds
    assert log_content is not None


async def test_build_wait_for_finish(client: ApifyClient | ApifyClientAsync) -> None:
    """Test wait_for_finish on an already completed build."""
    # First list builds to get a completed build ID
    actor = client.actor(HELLO_WORLD_ACTOR)
    result = await maybe_await(actor.builds().list(limit=5))
    builds_page = cast('ListOfBuilds', result)
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
    result = await maybe_await(client.build(completed_build.id).wait_for_finish(wait_secs=5))
    build = cast('Build | None', result)

    assert build is not None
    assert build.id == completed_build.id


async def test_build_delete_and_abort(client: ApifyClient | ApifyClientAsync) -> None:
    """Test deleting and aborting a build on our own Actor."""
    actor_name = get_random_resource_name('actor')

    # Create actor with two versions
    result = await maybe_await(
        client.actors().create(
            name=actor_name,
            title='Test Actor for Build Delete',
            versions=[
                {
                    'versionNumber': '0.1',
                    'sourceType': 'SOURCE_FILES',
                    'buildTag': 'beta',
                    'sourceFiles': [
                        {
                            'name': 'main.js',
                            'format': 'TEXT',
                            'content': 'console.log("Hello v0.1")',
                        }
                    ],
                },
                {
                    'versionNumber': '0.2',
                    'sourceType': 'SOURCE_FILES',
                    'buildTag': 'latest',
                    'sourceFiles': [
                        {
                            'name': 'main.js',
                            'format': 'TEXT',
                            'content': 'console.log("Hello v0.2")',
                        }
                    ],
                },
            ],
        )
    )
    created_actor = cast('Actor', result)
    assert created_actor is not None
    actor_client = client.actor(created_actor.id)

    try:
        # Build both versions - we need 2 builds because we can't delete the default build
        result = await maybe_await(actor_client.build(version_number='0.1'))
        first_build = cast('Build', result)
        assert first_build is not None
        first_build_client = client.build(first_build.id)
        await maybe_await(first_build_client.wait_for_finish())

        result = await maybe_await(actor_client.build(version_number='0.2'))
        second_build = cast('Build', result)
        assert second_build is not None
        second_build_client = client.build(second_build.id)

        # Wait for the second build to finish
        result = await maybe_await(second_build_client.wait_for_finish())
        finished_build = cast('Build | None', result)
        assert finished_build is not None
        assert finished_build.status.value in ('SUCCEEDED', 'FAILED')

        # Test abort on already finished build (should return the build in its current state)
        result = await maybe_await(second_build_client.abort())
        aborted_build = cast('Build', result)
        assert aborted_build is not None
        assert aborted_build.status.value in ('SUCCEEDED', 'FAILED', 'ABORTED')

        # Delete the first build (not the default/latest)
        await maybe_await(first_build_client.delete())

        # Verify the build is deleted
        result = await maybe_await(first_build_client.get())
        deleted_build = cast('Build | None', result)
        assert deleted_build is None

    finally:
        # Cleanup - delete actor
        await maybe_await(actor_client.delete())


async def test_build_get_open_api_definition(client: ApifyClient | ApifyClientAsync) -> None:
    """Test getting OpenAPI definition for a build."""
    # Get builds for hello-world actor
    actor = client.actor(HELLO_WORLD_ACTOR)
    result = await maybe_await(actor.builds().list(limit=1))
    builds_page = cast('ListOfBuilds', result)
    assert builds_page.items
    build_id = builds_page.items[0].id

    # Get the OpenAPI definition
    build_client = client.build(build_id)
    openapi_def = await maybe_await(build_client.get_open_api_definition())

    # OpenAPI definition should be a dict with standard OpenAPI fields
    # Note: May be None if the actor doesn't have an OpenAPI definition
    if openapi_def is not None:
        assert isinstance(openapi_def, dict)

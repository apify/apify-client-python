"""Unified tests for build (sync + async)."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from datetime import timedelta
from typing import TYPE_CHECKING

from ._utils import get_random_resource_name, maybe_await
from apify_client._models import Actor, Build, BuildShort, ListOfBuilds

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync

# Use a public actor that has builds available
HELLO_WORLD_ACTOR = 'apify/hello-world'

# Apify-owned actor whose `latest` build sets `minMemoryMbytes: 128` (well below the spec's
# previously-required minimum of 256). Also publishes `actorDefinition.version: "0.0.1"`,
# exercising the semver-triplet version pattern.
SMALL_MIN_MEMORY_ACTOR = 'apify/instagram-profile-scraper'

# Apify-owned actor whose builds list includes entries with `meta.origin: "CI"`
# from the internal CI pipeline. A deep `desc=True` pagination is needed because
# CI builds are infrequent and rotate out of the most-recent window.
CI_ORIGIN_ACTOR = 'apify/cheerio-scraper'


def _pick_build_id(actor: Actor) -> str:
    """Return a stable `build_id` from `actor.tagged_builds`, preferring the `latest` tag.

    Avoids relying on API-side dict ordering (`next(iter(...))` would otherwise pick
    whichever tag the API decides to serialize first).
    """
    assert actor.tagged_builds, f'{actor.username}/{actor.name} has no tagged builds'
    latest = actor.tagged_builds.get('latest')
    if latest is not None and latest.build_id is not None:
        return latest.build_id
    fallback = next(
        (info.build_id for info in actor.tagged_builds.values() if info and info.build_id),
        None,
    )
    assert fallback is not None, f'{actor.username}/{actor.name} has no tagged build with a build_id'
    return fallback


async def test_build_list_for_actor(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing builds for a public Actor."""
    # Get builds for hello-world actor
    actor = client.actor(HELLO_WORLD_ACTOR)
    builds_page = await maybe_await(actor.builds().list(limit=10))
    assert isinstance(builds_page, ListOfBuilds)
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
    builds_page = await maybe_await(actor.builds().list(limit=1))
    assert isinstance(builds_page, ListOfBuilds)
    assert builds_page.items
    build_id = builds_page.items[0].id

    # Get the specific build
    build = await maybe_await(client.build(build_id).get())
    assert isinstance(build, Build)
    assert build.id == build_id
    assert build.act_id is not None
    assert build.status is not None


async def test_user_builds_list(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing all user builds."""
    # List user's builds (may be empty if user has no actors)
    builds_page = await maybe_await(client.builds().list(limit=10))
    assert isinstance(builds_page, ListOfBuilds)
    assert builds_page.items is not None
    # User may have 0 builds, so we just check the structure
    assert isinstance(builds_page.items, list)


async def test_build_log(client: ApifyClient | ApifyClientAsync) -> None:
    """Test getting build log."""
    # First list builds to get a completed build ID
    actor = client.actor(HELLO_WORLD_ACTOR)
    builds_page = await maybe_await(actor.builds().list(limit=5))
    assert isinstance(builds_page, ListOfBuilds)
    assert builds_page.items

    # Find a completed build (SUCCEEDED status)
    completed_build = None
    for build in builds_page.items:
        if build.status and build.status == 'SUCCEEDED':
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
    builds_page = await maybe_await(actor.builds().list(limit=5))
    assert isinstance(builds_page, ListOfBuilds)
    assert builds_page.items

    # Find a completed build (SUCCEEDED status)
    completed_build = None
    for build in builds_page.items:
        if build.status and build.status == 'SUCCEEDED':
            completed_build = build
            break

    if completed_build is None:
        # If no succeeded build found, use any finished build
        for build in builds_page.items:
            if build.status and build.status in ('SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'):
                completed_build = build
                break

    if completed_build is None:
        completed_build = builds_page.items[0]

    # Wait for finish on already completed build (should return immediately)
    build = await maybe_await(client.build(completed_build.id).wait_for_finish(wait_duration=timedelta(seconds=5)))
    assert isinstance(build, Build)
    assert build.id == completed_build.id


async def test_build_delete_and_abort(client: ApifyClient | ApifyClientAsync) -> None:
    """Test deleting and aborting a build on our own Actor."""
    actor_name = get_random_resource_name('actor')

    # Create actor with two versions
    created_actor = await maybe_await(
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
    assert isinstance(created_actor, Actor)
    actor_client = client.actor(created_actor.id)

    try:
        # Build both versions - we need 2 builds because we can't delete the default build
        first_build = await maybe_await(actor_client.build(version_number='0.1'))
        assert isinstance(first_build, Build)
        first_build_client = client.build(first_build.id)
        await maybe_await(first_build_client.wait_for_finish())

        second_build = await maybe_await(actor_client.build(version_number='0.2'))
        assert isinstance(second_build, Build)
        second_build_client = client.build(second_build.id)

        # Wait for the second build to finish
        finished_build = await maybe_await(second_build_client.wait_for_finish())
        assert isinstance(finished_build, Build)
        assert finished_build.status in ('SUCCEEDED', 'FAILED')

        # Test abort on already finished build (should return the build in its current state)
        aborted_build = await maybe_await(second_build_client.abort())
        assert isinstance(aborted_build, Build)
        assert aborted_build.status in ('SUCCEEDED', 'FAILED')

        # Delete the first build (not the default/latest)
        await maybe_await(first_build_client.delete())

        # Verify the build is deleted
        deleted_build = await maybe_await(first_build_client.get())
        assert deleted_build is None

    finally:
        # Cleanup - delete actor
        await maybe_await(actor_client.delete())


async def test_build_get_accepts_small_min_memory_mbytes(client: ApifyClient | ApifyClientAsync) -> None:
    """Test that build.get() parses actorDefinition.minMemoryMbytes values below 256 MB."""
    actor = await maybe_await(client.actor(SMALL_MIN_MEMORY_ACTOR).get())
    assert isinstance(actor, Actor)
    build_id = _pick_build_id(actor)

    build = await maybe_await(client.build(build_id).get())
    assert isinstance(build, Build)
    assert build.actor_definition is not None, 'expected actorDefinition on a SUCCEEDED build'

    # Fixture-drift guard: only meaningful if the chosen build actually carries a value
    # below the old 256 threshold.
    actual_min = build.actor_definition.min_memory_mbytes
    assert actual_min is not None
    assert actual_min < 256, (
        f'{SMALL_MIN_MEMORY_ACTOR} latest build has min_memory_mbytes={actual_min!r} '
        '(expected <256). Pick a different fixture to keep this test meaningful.'
    )


async def test_actor_builds_list_accepts_ci_origin(client: ApifyClient | ApifyClientAsync) -> None:
    """Test that actor.builds().list() parses builds with meta.origin == 'CI'."""
    builds = await maybe_await(client.actor(CI_ORIGIN_ACTOR).builds().list(limit=100, desc=True))
    assert isinstance(builds, ListOfBuilds)
    assert builds.items, f'{CI_ORIGIN_ACTOR} should have builds'

    # Fixture-drift guard: only meaningful if the page actually contains a CI-origin build.
    # Pydantic already validated every `meta.origin` against `RunOrigin` at deserialization,
    # so the check is exercised iff at least one such entry exists.
    ci_origin_builds = [b for b in builds.items if b.meta is not None and b.meta.origin == 'CI']
    assert ci_origin_builds, (
        f'{CI_ORIGIN_ACTOR}: no builds with meta.origin == "CI" in the most-recent 100. '
        'CI builds may have rotated out of the window — pick a different actor or paginate deeper.'
    )


async def test_actor_definition_version_accepts_semver_triplet(client: ApifyClient | ApifyClientAsync) -> None:
    """Test that ActorDefinition.version accepts semver-triplet strings like '0.0.1'."""
    actor = await maybe_await(client.actor(SMALL_MIN_MEMORY_ACTOR).get())
    assert isinstance(actor, Actor)
    build_id = _pick_build_id(actor)

    build = await maybe_await(client.build(build_id).get())
    assert isinstance(build, Build)
    assert build.actor_definition is not None
    # Fixture-drift guard: only meaningful if the chosen build's version actually carries
    # more than one dot.
    version = build.actor_definition.version
    assert version is not None
    assert version.count('.') >= 2, (
        f'{SMALL_MIN_MEMORY_ACTOR} no longer publishes a multi-dot version (got {version!r}) — '
        'pick a different fixture to keep this test meaningful.'
    )


async def test_build_get_open_api_definition(client: ApifyClient | ApifyClientAsync) -> None:
    """Test getting OpenAPI definition for a build."""
    # Get builds for hello-world actor
    actor = client.actor(HELLO_WORLD_ACTOR)
    builds_page = await maybe_await(actor.builds().list(limit=1))
    assert isinstance(builds_page, ListOfBuilds)
    assert builds_page.items
    build_id = builds_page.items[0].id

    # Get the OpenAPI definition
    build_client = client.build(build_id)
    openapi_def = await maybe_await(build_client.get_open_api_definition())

    # OpenAPI definition should be a dict with standard OpenAPI fields
    # Note: May be None if the actor doesn't have an OpenAPI definition
    assert isinstance(openapi_def, dict)


async def test_builds_iterate_for_actor(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test paginated iteration over an Actor's builds."""
    iterator = client.actor(HELLO_WORLD_ACTOR).builds().iterate(limit=5)
    collected: list[BuildShort] = []
    if is_async:
        assert isinstance(iterator, AsyncIterator)
        async for b in iterator:
            assert isinstance(b, BuildShort)
            collected.append(b)
    else:
        assert isinstance(iterator, Iterator)
        for b in iterator:
            assert isinstance(b, BuildShort)
            collected.append(b)

    assert 1 <= len(collected) <= 5
    for build in collected:
        assert build.id is not None
        assert build.act_id is not None


async def test_user_builds_iterate(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test paginated iteration over the user's builds."""
    iterator = client.builds().iterate(limit=5)
    collected: list[BuildShort] = []
    if is_async:
        assert isinstance(iterator, AsyncIterator)
        async for b in iterator:
            assert isinstance(b, BuildShort)
            collected.append(b)
    else:
        assert isinstance(iterator, Iterator)
        for b in iterator:
            assert isinstance(b, BuildShort)
            collected.append(b)

    assert len(collected) <= 5
    for build in collected:
        assert build.id is not None


async def test_get_nonexistent_build_returns_none(client: ApifyClient | ApifyClientAsync) -> None:
    """Test that get() on a non-existent build returns None."""
    build = await maybe_await(client.build('NoNeXiStEnTbUiLd').get())
    assert build is None

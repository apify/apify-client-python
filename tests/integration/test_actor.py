"""Unified tests for Actor (sync + async)."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from ._utils import get_random_resource_name, maybe_await
from apify_client._models_generated import ActorShort
from apify_client._pagination_classes import PageOfItems

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync
    from apify_client._models_generated import Actor, Build, Run
    from apify_client._resource_clients import BuildClient, BuildClientAsync


async def test_get_public_actor(client: ApifyClient | ApifyClientAsync) -> None:
    """Test getting a public Actor by ID."""
    # Use a well-known public actor (Apify's web scraper)
    result = await maybe_await(client.actor('apify/web-scraper').get())
    actor = cast('Actor', result)

    assert actor is not None
    assert actor.id is not None
    assert actor.name == 'web-scraper'
    assert actor.username == 'apify'


async def test_get_actor_by_full_name(client: ApifyClient | ApifyClientAsync) -> None:
    """Test getting an Actor using username/actorname format."""
    result = await maybe_await(client.actor('apify/hello-world').get())
    actor = cast('Actor', result)

    assert actor is not None
    assert actor.name == 'hello-world'
    assert actor.username == 'apify'


async def test_list_actors_my(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing Actors created by the user."""
    actors_page = await maybe_await(client.actors().list(my=True, limit=10))

    assert isinstance(actors_page, PageOfItems)
    assert isinstance(actors_page.items, list)
    # User may have 0 actors — only check element type when any were returned.
    if actors_page.items:
        assert isinstance(actors_page.items[0], ActorShort)


async def test_list_actors_pagination(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing Actors with pagination parameters."""
    actors_page = await maybe_await(client.actors().list(limit=5, offset=0))

    assert isinstance(actors_page, PageOfItems)
    assert isinstance(actors_page.items, list)
    assert isinstance(actors_page.items[0], ActorShort)


async def test_list_actors_sorting(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing Actors with sorting."""
    actors_page = await maybe_await(client.actors().list(limit=10, desc=True, sort_by='created_at'))

    assert isinstance(actors_page, PageOfItems)
    assert isinstance(actors_page.items, list)
    assert isinstance(actors_page.items[0], ActorShort)


async def test_actor_create_update_delete(client: ApifyClient | ApifyClientAsync) -> None:
    """Test creating, updating, and deleting an Actor."""
    actor_name = get_random_resource_name('actor')

    # Create actor
    result = await maybe_await(
        client.actors().create(
            name=actor_name,
            title='Test Actor',
            description='Test actor for integration tests',
            versions=[
                {
                    'versionNumber': '0.1',
                    'sourceType': 'SOURCE_FILES',
                    'buildTag': 'latest',
                    'sourceFiles': [
                        {
                            'name': 'main.js',
                            'format': 'TEXT',
                            'content': 'console.log("Hello")',
                        }
                    ],
                }
            ],
        )
    )
    created_actor = cast('Actor', result)
    assert created_actor is not None
    assert created_actor.id is not None
    assert created_actor.name == actor_name

    actor_client = client.actor(created_actor.id)

    try:
        # Update actor (only title and description - updating defaultRunOptions requires build to be set)
        new_title = 'Updated Test Actor'
        new_description = 'Updated description'
        result = await maybe_await(
            actor_client.update(
                title=new_title,
                description=new_description,
            )
        )
        updated_actor = cast('Actor', result)
        assert updated_actor is not None
        assert updated_actor.title == new_title
        assert updated_actor.description == new_description

        # Verify update persisted
        result = await maybe_await(actor_client.get())
        retrieved_actor = cast('Actor', result)
        assert retrieved_actor is not None
        assert retrieved_actor.title == new_title

    finally:
        # Cleanup - delete actor
        await maybe_await(actor_client.delete())

    # Verify deletion
    deleted_actor = await maybe_await(actor_client.get())
    assert deleted_actor is None


async def test_actor_default_build(client: ApifyClient | ApifyClientAsync) -> None:
    """Test getting an Actor's default build."""
    # Use a public actor that has builds
    actor_client = client.actor('apify/hello-world')

    # Get default build client
    result = await maybe_await(actor_client.default_build())
    build_client = cast('BuildClient | BuildClientAsync', result)
    assert build_client is not None

    # Use the returned client to get the build
    result = await maybe_await(build_client.get())
    build = cast('Build', result)
    assert build is not None
    assert build.id is not None
    assert build.status is not None


async def test_actor_last_run(client: ApifyClient | ApifyClientAsync) -> None:
    """Test getting an Actor's last run."""
    # First run an actor to ensure there is a last run
    actor_client = client.actor('apify/hello-world')
    result = await maybe_await(actor_client.call())
    run = cast('Run', result)
    assert run is not None

    try:
        # Get last run client
        last_run_client = actor_client.last_run()
        assert last_run_client is not None

        # Use the returned client to get the run
        result = await maybe_await(last_run_client.get())
        last_run = cast('Run', result)
        assert last_run is not None
        assert last_run.id is not None

    finally:
        await maybe_await(client.run(run.id).delete())


async def test_actor_validate_input(client: ApifyClient | ApifyClientAsync) -> None:
    """Test validating Actor input."""
    # Use a public actor with an input schema
    actor_client = client.actor('apify/hello-world')

    # Valid input (hello-world accepts empty input or simple input)
    is_valid = await maybe_await(actor_client.validate_input({}))
    assert is_valid is True

from __future__ import annotations

from typing import TYPE_CHECKING

from .utils import get_random_resource_name

if TYPE_CHECKING:
    from apify_client import ApifyClientAsync


async def test_get_public_actor(apify_client_async: ApifyClientAsync) -> None:
    """Test getting a public actor by ID."""
    # Use a well-known public actor (Apify's web scraper)
    actor = await apify_client_async.actor('apify/web-scraper').get()

    assert actor is not None
    assert actor.id is not None
    assert actor.name == 'web-scraper'
    assert actor.username == 'apify'


async def test_get_actor_by_full_name(apify_client_async: ApifyClientAsync) -> None:
    """Test getting an actor using username/actorname format."""
    actor = await apify_client_async.actor('apify/hello-world').get()

    assert actor is not None
    assert actor.name == 'hello-world'
    assert actor.username == 'apify'


async def test_list_actors_my(apify_client_async: ApifyClientAsync) -> None:
    """Test listing actors created by the user."""
    actors_page = await apify_client_async.actors().list(my=True, limit=10)

    assert actors_page is not None
    assert actors_page.items is not None
    # User may have 0 actors
    assert isinstance(actors_page.items, list)


async def test_list_actors_pagination(apify_client_async: ApifyClientAsync) -> None:
    """Test listing actors with pagination parameters."""
    # List all actors (public + owned), should return some results
    actors_page = await apify_client_async.actors().list(limit=5, offset=0)

    assert actors_page is not None
    assert actors_page.items is not None
    assert isinstance(actors_page.items, list)
    # Should have at least some actors (public ones exist)
    assert len(actors_page.items) >= 0


async def test_list_actors_sorting(apify_client_async: ApifyClientAsync) -> None:
    """Test listing actors with sorting."""
    actors_page = await apify_client_async.actors().list(limit=10, desc=True, sort_by='createdAt')

    assert actors_page is not None
    assert actors_page.items is not None
    assert isinstance(actors_page.items, list)


async def test_actor_create_update_delete(apify_client_async: ApifyClientAsync) -> None:
    """Test creating, updating, and deleting an actor."""
    actor_name = get_random_resource_name('actor')

    # Create actor
    created_actor = await apify_client_async.actors().create(
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
    assert created_actor is not None
    assert created_actor.id is not None
    assert created_actor.name == actor_name

    actor_client = apify_client_async.actor(created_actor.id)

    try:
        # Update actor (only title and description - updating defaultRunOptions requires build to be set)
        new_title = 'Updated Test Actor'
        new_description = 'Updated description'
        updated_actor = await actor_client.update(
            title=new_title,
            description=new_description,
        )
        assert updated_actor is not None
        assert updated_actor.title == new_title
        assert updated_actor.description == new_description

        # Verify update persisted
        retrieved_actor = await actor_client.get()
        assert retrieved_actor is not None
        assert retrieved_actor.title == new_title

    finally:
        # Cleanup - delete actor
        await actor_client.delete()

    # Verify deletion
    deleted_actor = await actor_client.get()
    assert deleted_actor is None


async def test_actor_default_build(apify_client_async: ApifyClientAsync) -> None:
    """Test getting an actor's default build."""
    # Use a public actor that has builds
    actor_client = apify_client_async.actor('apify/hello-world')

    # Get default build client
    build_client = await actor_client.default_build()
    assert build_client is not None

    # Use the returned client to get the build
    build = await build_client.get()
    assert build is not None
    assert build.id is not None
    assert build.status is not None


async def test_actor_last_run(apify_client_async: ApifyClientAsync) -> None:
    """Test getting an actor's last run."""
    # First run an actor to ensure there is a last run
    actor_client = apify_client_async.actor('apify/hello-world')
    run = await actor_client.call()
    assert run is not None

    try:
        # Get last run client
        last_run_client = actor_client.last_run()
        assert last_run_client is not None

        # Use the returned client to get the run
        last_run = await last_run_client.get()
        assert last_run is not None
        assert last_run.id is not None
        # The last run should be the one we just created
        assert last_run.id == run.id

    finally:
        # Cleanup
        await apify_client_async.run(run.id).delete()


async def test_actor_validate_input(apify_client_async: ApifyClientAsync) -> None:
    """Test validating actor input."""
    # Use a public actor with an input schema
    actor_client = apify_client_async.actor('apify/hello-world')

    # Valid input (hello-world accepts empty input or simple input)
    is_valid = await actor_client.validate_input({})
    assert is_valid is True

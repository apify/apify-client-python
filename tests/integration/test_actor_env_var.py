"""Unified tests for Actor environment variables (sync + async)."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING

from ._utils import get_random_resource_name, maybe_await
from apify_client._models import Actor, EnvVar, ListOfEnvVars

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync


async def test_actor_env_var_list(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing Actor version environment variables."""
    actor_name = get_random_resource_name('actor')

    # Create an actor with a version that has env vars
    actor = await maybe_await(
        client.actors().create(
            name=actor_name,
            versions=[
                {
                    'versionNumber': '0.0',
                    'sourceType': 'SOURCE_FILES',
                    'buildTag': 'latest',
                    'sourceFiles': [
                        {
                            'name': 'main.js',
                            'format': 'TEXT',
                            'content': 'console.log("Hello")',
                        }
                    ],
                    'envVars': [
                        {
                            'name': 'TEST_VAR',
                            'value': 'test_value',
                            'isSecret': False,
                        }
                    ],
                }
            ],
        )
    )
    assert isinstance(actor, Actor)
    actor_client = client.actor(actor.id)
    version_client = actor_client.version('0.0')

    try:
        # List env vars
        env_vars = await maybe_await(version_client.env_vars().list())
        assert isinstance(env_vars, ListOfEnvVars)
        assert env_vars.items is not None
        assert len(env_vars.items) >= 1

        # Verify env var fields
        env_var = env_vars.items[0]
        assert env_var.name == 'TEST_VAR'
        assert env_var.value == 'test_value'

    finally:
        await maybe_await(actor_client.delete())


async def test_actor_env_var_create_and_get(client: ApifyClient | ApifyClientAsync) -> None:
    """Test creating and getting an Actor version environment variable."""
    actor_name = get_random_resource_name('actor')

    # Create an actor with a version
    actor = await maybe_await(
        client.actors().create(
            name=actor_name,
            versions=[
                {
                    'versionNumber': '1.0',
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
    assert isinstance(actor, Actor)
    actor_client = client.actor(actor.id)
    version_client = actor_client.version('1.0')

    try:
        # Create a new env var
        created_env_var = await maybe_await(
            version_client.env_vars().create(
                name='MY_VAR',
                value='my_value',
                is_secret=False,
            )
        )
        assert isinstance(created_env_var, EnvVar)
        assert created_env_var.name == 'MY_VAR'
        assert created_env_var.value == 'my_value'
        assert created_env_var.is_secret is False

        # Get the same env var
        env_var_client = version_client.env_var('MY_VAR')
        retrieved_env_var = await maybe_await(env_var_client.get())
        assert isinstance(retrieved_env_var, EnvVar)
        assert retrieved_env_var.name == 'MY_VAR'
        assert retrieved_env_var.value == 'my_value'

    finally:
        await maybe_await(actor_client.delete())


async def test_actor_env_var_update(client: ApifyClient | ApifyClientAsync) -> None:
    """Test updating an Actor version environment variable."""
    actor_name = get_random_resource_name('actor')

    # Create an actor with a version and env var
    actor = await maybe_await(
        client.actors().create(
            name=actor_name,
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
                    'envVars': [
                        {
                            'name': 'UPDATE_VAR',
                            'value': 'initial_value',
                            'isSecret': False,
                        }
                    ],
                }
            ],
        )
    )
    assert isinstance(actor, Actor)
    actor_client = client.actor(actor.id)
    version_client = actor_client.version('0.1')
    env_var_client = version_client.env_var('UPDATE_VAR')

    try:
        # Update the env var
        updated_env_var = await maybe_await(
            env_var_client.update(
                name='UPDATE_VAR',
                value='updated_value',
            )
        )
        assert isinstance(updated_env_var, EnvVar)
        assert updated_env_var.name == 'UPDATE_VAR'
        assert updated_env_var.value == 'updated_value'

        # Verify the update persisted
        retrieved_env_var = await maybe_await(env_var_client.get())
        assert isinstance(retrieved_env_var, EnvVar)
        assert retrieved_env_var.value == 'updated_value'

    finally:
        await maybe_await(actor_client.delete())


async def test_actor_env_var_delete(client: ApifyClient | ApifyClientAsync) -> None:
    """Test deleting an Actor version environment variable."""
    actor_name = get_random_resource_name('actor')

    # Create an actor with a version and two env vars
    actor = await maybe_await(
        client.actors().create(
            name=actor_name,
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
                    'envVars': [
                        {
                            'name': 'VAR_TO_DELETE',
                            'value': 'delete_me',
                            'isSecret': False,
                        },
                        {
                            'name': 'VAR_TO_KEEP',
                            'value': 'keep_me',
                            'isSecret': False,
                        },
                    ],
                }
            ],
        )
    )
    assert isinstance(actor, Actor)
    actor_client = client.actor(actor.id)
    version_client = actor_client.version('0.1')

    try:
        # Delete the first env var
        env_var_client = version_client.env_var('VAR_TO_DELETE')
        await maybe_await(env_var_client.delete())

        # Verify it's gone
        deleted_env_var = await maybe_await(env_var_client.get())
        assert deleted_env_var is None

        # Verify the other env var still exists
        remaining_env_var = await maybe_await(version_client.env_var('VAR_TO_KEEP').get())
        assert isinstance(remaining_env_var, EnvVar)
        assert remaining_env_var.name == 'VAR_TO_KEEP'

    finally:
        await maybe_await(actor_client.delete())


async def test_actor_env_var_collection_iterate(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test iterating over a version's environment variables."""
    actor_name = get_random_resource_name('actor')

    actor = await maybe_await(
        client.actors().create(
            name=actor_name,
            versions=[
                {
                    'versionNumber': '0.0',
                    'sourceType': 'SOURCE_FILES',
                    'buildTag': 'latest',
                    'sourceFiles': [{'name': 'main.js', 'format': 'TEXT', 'content': 'console.log("Hello")'}],
                    'envVars': [{'name': f'VAR_{i}', 'value': f'value_{i}', 'isSecret': False} for i in range(3)],
                }
            ],
        )
    )
    assert isinstance(actor, Actor)
    actor_client = client.actor(actor.id)
    version_client = actor_client.version('0.0')

    try:
        iterator = version_client.env_vars().iterate()
        collected: list[EnvVar] = []
        if is_async:
            assert isinstance(iterator, AsyncIterator)
            async for e in iterator:
                assert isinstance(e, EnvVar)
                collected.append(e)
        else:
            assert isinstance(iterator, Iterator)
            for e in iterator:
                assert isinstance(e, EnvVar)
                collected.append(e)

        assert len(collected) == 3
        names = {e.name for e in collected}
        assert names == {'VAR_0', 'VAR_1', 'VAR_2'}
    finally:
        await maybe_await(actor_client.delete())


async def test_actor_env_var_secret(client: ApifyClient | ApifyClientAsync) -> None:
    """Test that creating a secret env var hides its plaintext value on retrieval."""
    actor_name = get_random_resource_name('actor')

    actor = await maybe_await(
        client.actors().create(
            name=actor_name,
            versions=[
                {
                    'versionNumber': '0.0',
                    'sourceType': 'SOURCE_FILES',
                    'buildTag': 'latest',
                    'sourceFiles': [{'name': 'main.js', 'format': 'TEXT', 'content': 'console.log("Hello")'}],
                }
            ],
        )
    )
    assert isinstance(actor, Actor)
    actor_client = client.actor(actor.id)
    version_client = actor_client.version('0.0')

    try:
        created = await maybe_await(
            version_client.env_vars().create(
                name='MY_SECRET',
                value='super-secret-token',
                is_secret=True,
            )
        )
        assert isinstance(created, EnvVar)
        assert created.name == 'MY_SECRET'
        assert created.is_secret is True

        # When retrieved, secret values must not be exposed back to the API client
        retrieved = await maybe_await(version_client.env_var('MY_SECRET').get())
        assert isinstance(retrieved, EnvVar)
        assert retrieved.is_secret is True
        assert retrieved.value is None
    finally:
        await maybe_await(actor_client.delete())


async def test_actor_env_var_get_nonexistent_returns_none(
    client: ApifyClient | ApifyClientAsync,
) -> None:
    """Test that get() on a non-existent env var returns None."""
    actor_name = get_random_resource_name('actor')

    actor = await maybe_await(
        client.actors().create(
            name=actor_name,
            versions=[
                {
                    'versionNumber': '0.0',
                    'sourceType': 'SOURCE_FILES',
                    'buildTag': 'latest',
                    'sourceFiles': [{'name': 'main.js', 'format': 'TEXT', 'content': 'console.log("Hello")'}],
                }
            ],
        )
    )
    assert isinstance(actor, Actor)
    actor_client = client.actor(actor.id)
    version_client = actor_client.version('0.0')

    try:
        env_var = await maybe_await(version_client.env_var('THIS_DOES_NOT_EXIST').get())
        assert env_var is None
    finally:
        await maybe_await(actor_client.delete())

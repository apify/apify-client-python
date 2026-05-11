"""Unified tests for Actor version (sync + async)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._utils import get_random_resource_name, maybe_await
from apify_client._models import Actor, ListOfVersions, Version

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync


async def test_actor_version_list(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing Actor versions."""
    actor_name = get_random_resource_name('actor')

    # Create an actor with an initial version
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
                }
            ],
        )
    )
    assert isinstance(actor, Actor)
    actor_client = client.actor(actor.id)

    try:
        # List versions
        versions = await maybe_await(actor_client.versions().list())
        assert isinstance(versions, ListOfVersions)
        assert versions.items is not None
        assert len(versions.items) >= 1

        # Verify version fields
        version = versions.items[0]
        assert version.version_number == '0.0'
        assert version.build_tag == 'latest'

    finally:
        await maybe_await(actor_client.delete())


async def test_actor_version_create_and_get(client: ApifyClient | ApifyClientAsync) -> None:
    """Test creating and getting an Actor version."""
    actor_name = get_random_resource_name('actor')

    # Create an actor without versions
    actor = await maybe_await(client.actors().create(name=actor_name))
    assert isinstance(actor, Actor)
    actor_client = client.actor(actor.id)

    try:
        # Create a new version
        created_version = await maybe_await(
            actor_client.versions().create(
                version_number='1.0',
                source_type='SOURCE_FILES',
                build_tag='test',
                source_files=[
                    {
                        'name': 'main.js',
                        'format': 'TEXT',
                        'content': 'console.log("Hello from version 1.0")',
                    }
                ],
            )
        )
        assert isinstance(created_version, Version)
        assert created_version.version_number == '1.0'
        assert created_version.build_tag == 'test'
        assert created_version.source_type == 'SOURCE_FILES'

        # Get the same version
        version_client = actor_client.version('1.0')
        retrieved_version = await maybe_await(version_client.get())
        assert isinstance(retrieved_version, Version)
        assert retrieved_version.version_number == '1.0'
        assert retrieved_version.build_tag == 'test'

    finally:
        await maybe_await(actor_client.delete())


async def test_actor_version_update(client: ApifyClient | ApifyClientAsync) -> None:
    """Test updating an Actor version."""
    actor_name = get_random_resource_name('actor')

    # Create an actor with a version
    actor = await maybe_await(
        client.actors().create(
            name=actor_name,
            versions=[
                {
                    'versionNumber': '0.1',
                    'sourceType': 'SOURCE_FILES',
                    'buildTag': 'initial',
                    'sourceFiles': [
                        {
                            'name': 'main.js',
                            'format': 'TEXT',
                            'content': 'console.log("Initial")',
                        }
                    ],
                }
            ],
        )
    )
    assert isinstance(actor, Actor)
    actor_client = client.actor(actor.id)
    version_client = actor_client.version('0.1')

    try:
        # Update the version
        updated_version = await maybe_await(
            version_client.update(
                build_tag='updated',
                source_files=[
                    {
                        'name': 'main.js',
                        'format': 'TEXT',
                        'content': 'console.log("Updated")',
                    }
                ],
            )
        )
        assert isinstance(updated_version, Version)
        assert updated_version.version_number == '0.1'
        assert updated_version.build_tag == 'updated'

        # Verify the update persisted
        retrieved_version = await maybe_await(version_client.get())
        assert isinstance(retrieved_version, Version)
        assert retrieved_version.build_tag == 'updated'

    finally:
        await maybe_await(actor_client.delete())


async def test_actor_version_delete(client: ApifyClient | ApifyClientAsync) -> None:
    """Test deleting an Actor version."""
    actor_name = get_random_resource_name('actor')

    # Create an actor with two versions
    actor = await maybe_await(
        client.actors().create(
            name=actor_name,
            versions=[
                {
                    'versionNumber': '0.1',
                    'sourceType': 'SOURCE_FILES',
                    'buildTag': 'v1',
                    'sourceFiles': [
                        {
                            'name': 'main.js',
                            'format': 'TEXT',
                            'content': 'console.log("v1")',
                        }
                    ],
                },
                {
                    'versionNumber': '0.2',
                    'sourceType': 'SOURCE_FILES',
                    'buildTag': 'v2',
                    'sourceFiles': [
                        {
                            'name': 'main.js',
                            'format': 'TEXT',
                            'content': 'console.log("v2")',
                        }
                    ],
                },
            ],
        )
    )
    assert isinstance(actor, Actor)
    actor_client = client.actor(actor.id)

    try:
        # Delete version 0.1
        version_client = actor_client.version('0.1')
        await maybe_await(version_client.delete())

        # Verify it's gone
        deleted_version = await maybe_await(version_client.get())
        assert deleted_version is None

        # Verify version 0.2 still exists
        remaining_version = await maybe_await(actor_client.version('0.2').get())
        assert isinstance(remaining_version, Version)
        assert remaining_version.version_number == '0.2'

    finally:
        await maybe_await(actor_client.delete())

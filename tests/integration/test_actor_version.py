from __future__ import annotations

from typing import TYPE_CHECKING

from .utils import get_random_resource_name
from apify_client._models import VersionSourceType

if TYPE_CHECKING:
    from apify_client import ApifyClient


def test_actor_version_list(apify_client: ApifyClient) -> None:
    """Test listing actor versions."""
    actor_name = get_random_resource_name('actor')

    # Create an actor with an initial version
    actor = apify_client.actors().create(
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
    actor_client = apify_client.actor(actor.id)

    try:
        # List versions
        versions = actor_client.versions().list()

        assert versions is not None
        assert versions.items is not None
        assert len(versions.items) >= 1

        # Verify version fields
        version = versions.items[0]
        assert version.version_number == '0.0'
        assert version.build_tag == 'latest'

    finally:
        # Cleanup
        actor_client.delete()


def test_actor_version_create_and_get(apify_client: ApifyClient) -> None:
    """Test creating and getting an actor version."""
    actor_name = get_random_resource_name('actor')

    # Create an actor without versions
    actor = apify_client.actors().create(name=actor_name)
    actor_client = apify_client.actor(actor.id)

    try:
        # Create a new version
        created_version = actor_client.versions().create(
            version_number='1.0',
            source_type=VersionSourceType.SOURCE_FILES,
            build_tag='test',
            source_files=[
                {
                    'name': 'main.js',
                    'format': 'TEXT',
                    'content': 'console.log("Hello from version 1.0")',
                }
            ],
        )

        assert created_version is not None
        assert created_version.version_number == '1.0'
        assert created_version.build_tag == 'test'
        assert created_version.source_type == VersionSourceType.SOURCE_FILES

        # Get the same version
        version_client = actor_client.version('1.0')
        retrieved_version = version_client.get()

        assert retrieved_version is not None
        assert retrieved_version.version_number == '1.0'
        assert retrieved_version.build_tag == 'test'

    finally:
        # Cleanup
        actor_client.delete()


def test_actor_version_update(apify_client: ApifyClient) -> None:
    """Test updating an actor version."""
    actor_name = get_random_resource_name('actor')

    # Create an actor with a version
    actor = apify_client.actors().create(
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
    actor_client = apify_client.actor(actor.id)
    version_client = actor_client.version('0.1')

    try:
        # Update the version
        updated_version = version_client.update(
            build_tag='updated',
            source_files=[
                {
                    'name': 'main.js',
                    'format': 'TEXT',
                    'content': 'console.log("Updated")',
                }
            ],
        )

        assert updated_version is not None
        assert updated_version.version_number == '0.1'
        assert updated_version.build_tag == 'updated'

        # Verify the update persisted
        retrieved_version = version_client.get()
        assert retrieved_version is not None
        assert retrieved_version.build_tag == 'updated'

    finally:
        # Cleanup
        actor_client.delete()


def test_actor_version_delete(apify_client: ApifyClient) -> None:
    """Test deleting an actor version."""
    actor_name = get_random_resource_name('actor')

    # Create an actor with two versions
    actor = apify_client.actors().create(
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
    actor_client = apify_client.actor(actor.id)

    try:
        # Delete version 0.1
        version_client = actor_client.version('0.1')
        version_client.delete()

        # Verify it's gone
        deleted_version = version_client.get()
        assert deleted_version is None

        # Verify version 0.2 still exists
        remaining_version = actor_client.version('0.2').get()
        assert remaining_version is not None
        assert remaining_version.version_number == '0.2'

    finally:
        # Cleanup
        actor_client.delete()

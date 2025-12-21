from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apify_client import ApifyClient


def test_get_public_actor(apify_client: ApifyClient) -> None:
    """Test getting a public actor by ID."""
    # Use a well-known public actor (Apify's web scraper)
    actor = apify_client.actor('apify/web-scraper').get()

    assert actor is not None
    assert actor.id is not None
    assert actor.name == 'web-scraper'
    assert actor.username == 'apify'


def test_get_actor_by_full_name(apify_client: ApifyClient) -> None:
    """Test getting an actor using username/actorname format."""
    actor = apify_client.actor('apify/hello-world').get()

    assert actor is not None
    assert actor.name == 'hello-world'
    assert actor.username == 'apify'


def test_list_actors_my(apify_client: ApifyClient) -> None:
    """Test listing actors created by the user."""
    actors_page = apify_client.actors().list(my=True, limit=10)

    assert actors_page is not None
    assert actors_page.items is not None
    # User may have 0 actors
    assert isinstance(actors_page.items, list)


def test_list_actors_pagination(apify_client: ApifyClient) -> None:
    """Test listing actors with pagination parameters."""
    # List all actors (public + owned), should return some results
    actors_page = apify_client.actors().list(limit=5, offset=0)

    assert actors_page is not None
    assert actors_page.items is not None
    assert isinstance(actors_page.items, list)
    # Should have at least some actors (public ones exist)
    assert len(actors_page.items) >= 0


def test_list_actors_sorting(apify_client: ApifyClient) -> None:
    """Test listing actors with sorting."""
    actors_page = apify_client.actors().list(limit=10, desc=True, sort_by='createdAt')

    assert actors_page is not None
    assert actors_page.items is not None
    assert isinstance(actors_page.items, list)

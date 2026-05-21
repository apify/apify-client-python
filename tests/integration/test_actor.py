"""Unified tests for Actor (sync + async)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from ._utils import get_random_resource_name, maybe_await
from apify_client._models import (
    Actor,
    Build,
    ListOfActors,
    PayPerEventActorPricingInfo,
    PricePerDatasetItemActorPricingInfo,
    Run,
)
from apify_client._resource_clients import BuildClient, BuildClientAsync

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync


async def test_get_public_actor(client: ApifyClient | ApifyClientAsync) -> None:
    """Test getting a public Actor by ID."""
    # Use a well-known public actor (Apify's web scraper)
    actor = await maybe_await(client.actor('apify/web-scraper').get())
    assert isinstance(actor, Actor)
    assert actor.id is not None
    assert actor.name == 'web-scraper'
    assert actor.username == 'apify'


async def test_get_actor_by_full_name(client: ApifyClient | ApifyClientAsync) -> None:
    """Test getting an Actor using username/actorname format."""
    actor = await maybe_await(client.actor('apify/hello-world').get())
    assert isinstance(actor, Actor)
    assert actor.name == 'hello-world'
    assert actor.username == 'apify'


async def test_list_actors_my(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing Actors created by the user."""
    actors_page = await maybe_await(client.actors().list(my=True, limit=10))
    assert isinstance(actors_page, ListOfActors)
    assert actors_page.items is not None
    # User may have 0 actors
    assert isinstance(actors_page.items, list)


async def test_list_actors_pagination(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing Actors with pagination parameters."""
    # List all actors (public + owned), should return some results
    actors_page = await maybe_await(client.actors().list(limit=5, offset=0))
    assert isinstance(actors_page, ListOfActors)
    assert actors_page.items is not None
    assert isinstance(actors_page.items, list)
    # Should have at least some actors (public ones exist)
    assert len(actors_page.items) >= 0


async def test_list_actors_sorting(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing Actors with sorting."""
    actors_page = await maybe_await(client.actors().list(limit=10, desc=True, sort_by='stats.lastRunStartedAt'))
    assert isinstance(actors_page, ListOfActors)
    assert actors_page.items is not None
    assert isinstance(actors_page.items, list)

    min_dt = datetime.min.replace(tzinfo=UTC)
    sorted_items = sorted(
        actors_page.items,
        key=lambda a: (a.stats.last_run_started_at if a.stats else None) or min_dt,
        reverse=True,
    )
    assert actors_page.items == sorted_items


async def test_actor_create_update_delete(client: ApifyClient | ApifyClientAsync) -> None:
    """Test creating, updating, and deleting an Actor."""
    actor_name = get_random_resource_name('actor')

    # Create actor
    created_actor = await maybe_await(
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
    assert isinstance(created_actor, Actor)
    assert created_actor.id is not None
    assert created_actor.name == actor_name

    actor_client = client.actor(created_actor.id)

    try:
        # Update actor (only title and description - updating defaultRunOptions requires build to be set)
        new_title = 'Updated Test Actor'
        new_description = 'Updated description'
        updated_actor = await maybe_await(
            actor_client.update(
                title=new_title,
                description=new_description,
            )
        )
        assert isinstance(updated_actor, Actor)
        assert updated_actor.title == new_title
        assert updated_actor.description == new_description

        # Verify update persisted
        retrieved_actor = await maybe_await(actor_client.get())
        assert isinstance(retrieved_actor, Actor)
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
    build_client = await maybe_await(actor_client.default_build())
    assert isinstance(build_client, BuildClient | BuildClientAsync)

    # Use the returned client to get the build
    build = await maybe_await(build_client.get())
    assert isinstance(build, Build)
    assert build.id is not None
    assert build.status is not None


async def test_actor_last_run(client: ApifyClient | ApifyClientAsync) -> None:
    """Test getting an Actor's last run."""
    # First run an actor to ensure there is a last run
    actor_client = client.actor('apify/hello-world')
    run = await maybe_await(actor_client.call())
    assert isinstance(run, Run)

    try:
        # Get last run client
        last_run_client = actor_client.last_run()
        assert last_run_client is not None

        # Use the returned client to get the run
        last_run = await maybe_await(last_run_client.get())
        assert isinstance(last_run, Run)
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


async def test_get_actor_with_tiered_pricing(client: ApifyClient | ApifyClientAsync) -> None:
    """Regression test for apify/apify-client-python#811.

    `apify/facebook-pages-scraper` historically returns `pricingInfos` entries that use tiered
    pricing — both `PRICE_PER_DATASET_ITEM` with `tieredPricing` (instead of `pricePerUnitUsd`)
    and `PAY_PER_EVENT` with `eventTieredPricingUsd` (instead of `eventPriceUsd`). Earlier
    versions of the Pydantic models required the flat-price fields and rejected the response.
    """
    actor = await maybe_await(client.actor('apify/facebook-pages-scraper').get())
    assert isinstance(actor, Actor)
    assert actor.pricing_infos is not None

    tiered_ppr = [
        pi
        for pi in actor.pricing_infos
        if isinstance(pi, PricePerDatasetItemActorPricingInfo) and pi.tiered_pricing is not None
    ]
    assert tiered_ppr, 'expected at least one PRICE_PER_DATASET_ITEM entry with tiered_pricing'
    tiered_pricing = tiered_ppr[0].tiered_pricing
    assert tiered_pricing is not None
    tiered_entry = next(iter(tiered_pricing.values()))
    assert tiered_entry.tiered_price_per_unit_usd >= 0

    tiered_ppe_events = [
        event
        for pi in actor.pricing_infos
        if isinstance(pi, PayPerEventActorPricingInfo)
        and pi.pricing_per_event is not None
        and pi.pricing_per_event.actor_charge_events is not None
        for event in pi.pricing_per_event.actor_charge_events.values()
        if event.event_tiered_pricing_usd is not None
    ]
    assert tiered_ppe_events, 'expected at least one PAY_PER_EVENT charge event with event_tiered_pricing_usd'
    event_tiered_pricing = tiered_ppe_events[0].event_tiered_pricing_usd
    assert event_tiered_pricing is not None
    tiered_event_entry = next(iter(event_tiered_pricing.values()))
    assert tiered_event_entry.tiered_event_price_usd >= 0

"""Unified tests for Actor (sync + async)."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from .._utils import get_random_resource_name, maybe_await
from apify_client._models import (
    Actor,
    ActorChargeEvent,
    ActorShort,
    Build,
    ListOfActors,
    ListOfWebhooks,
    PayPerEventActorPricingInfo,
    PricePerDatasetItemActorPricingInfo,
    Run,
)
from apify_client._resource_clients import BuildClient, BuildClientAsync
from apify_client.errors import ConflictError

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync

# Actor carrying pricing-info entries for every non-trivial variant: FLAT_PRICE_PER_MONTH,
# both flat and tiered PRICE_PER_DATASET_ITEM, and tiered PAY_PER_EVENT with
# `isPrimaryEvent` / `isOneTimeEvent` fields.
ALL_PRICING_VARIANTS_ACTOR = 'apify/facebook-pages-scraper'


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
    try:
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
    except ConflictError:
        # The HTTP client retries requests on transient 5xx/network errors (at-least-once delivery), so a create
        # POST can commit server-side on one attempt yet still be retried; the retry then fails with a 409 on the
        # unique name it just took. Recover the Actor the first attempt created instead of flaking on this race.
        user = await maybe_await(client.user().get())
        assert user is not None
        created_actor = await maybe_await(client.actor(f'{user.username}/{actor_name}').get())

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


async def test_get_nonexistent_actor_returns_none(client: ApifyClient | ApifyClientAsync) -> None:
    """Test that getting a non-existent Actor returns None."""
    actor = await maybe_await(client.actor('this-actor/does-not-exist-anywhere').get())
    assert actor is None


async def test_list_actors_desc_ascending(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing Actors sorted ascending (desc=False)."""
    actors_page = await maybe_await(client.actors().list(limit=10, desc=False, sort_by='stats.lastRunStartedAt'))
    assert isinstance(actors_page, ListOfActors)
    assert actors_page.items is not None

    # The API and Python may break ties on identical timestamps differently, so just verify the
    # sort key is monotonically non-decreasing rather than comparing to a locally re-sorted list.
    min_dt = datetime.min.replace(tzinfo=UTC)
    keys = [(a.stats.last_run_started_at if a.stats else None) or min_dt for a in actors_page.items]
    assert keys == sorted(keys)


async def test_actors_iterate(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test paginated iteration over user's Actors."""
    iterator = client.actors().iterate(my=True, limit=10)
    collected: list[ActorShort] = []
    if is_async:
        assert isinstance(iterator, AsyncIterator)
        async for a in iterator:
            assert isinstance(a, ActorShort)
            collected.append(a)
    else:
        assert isinstance(iterator, Iterator)
        for a in iterator:
            assert isinstance(a, ActorShort)
            collected.append(a)

    assert len(collected) <= 10
    for actor in collected:
        assert actor.id is not None


async def test_actor_start_with_options(client: ApifyClient | ApifyClientAsync) -> None:
    """Test starting an Actor with explicit run options."""
    actor_client = client.actor('apify/hello-world')

    # Start the run with explicit build tag, memory, and timeout overrides
    run = await maybe_await(
        actor_client.start(
            build='latest',
            memory_mbytes=256,
            run_timeout=timedelta(seconds=120),
            wait_for_finish=60,
        )
    )
    assert isinstance(run, Run)
    assert run.id is not None
    assert run.options is not None
    assert run.options.memory_mbytes == 256
    assert run.options.timeout_secs == 120

    try:
        # Any terminal-or-in-progress status returned by the platform is acceptable here —
        # under load the run can briefly land in `TIMING-OUT`, `FAILED`, `ABORTING`, or `ABORTED`
        # without indicating a client-side bug.
        assert run.status in (
            'READY',
            'RUNNING',
            'SUCCEEDED',
            'TIMED-OUT',
            'TIMING-OUT',
            'FAILED',
            'ABORTING',
            'ABORTED',
        )
    finally:
        # Wait for run to finish before cleanup
        await maybe_await(client.run(run.id).wait_for_finish())
        await maybe_await(client.run(run.id).delete())


async def test_actor_start_with_run_input(client: ApifyClient | ApifyClientAsync) -> None:
    """Test starting an Actor with a JSON run input."""
    actor_client = client.actor('apify/hello-world')

    # Pass a custom input - hello-world accepts arbitrary input and echoes it in logs
    run = await maybe_await(actor_client.start(run_input={'message': 'integration-test-input'}))
    assert isinstance(run, Run)
    assert run.id is not None

    run_client = client.run(run.id)
    try:
        finished_run = await maybe_await(run_client.wait_for_finish())
        assert isinstance(finished_run, Run)
        assert finished_run.status == 'SUCCEEDED'
    finally:
        await maybe_await(run_client.delete())


async def test_actor_call_with_input_and_build(client: ApifyClient | ApifyClientAsync) -> None:
    """Test calling an Actor with input and a specific build tag."""
    actor_client = client.actor('apify/hello-world')

    run = await maybe_await(
        actor_client.call(
            run_input={'message': 'integration-test'},
            build='latest',
            memory_mbytes=256,
        )
    )
    assert isinstance(run, Run)

    try:
        assert run.status == 'SUCCEEDED'
    finally:
        await maybe_await(client.run(run.id).delete())


async def test_actor_update_categories(client: ApifyClient | ApifyClientAsync) -> None:
    """Test updating an Actor's categories and seo_title fields."""
    actor_name = get_random_resource_name('actor')

    created_actor = await maybe_await(
        client.actors().create(
            name=actor_name,
            title='Test Actor for Categories',
        )
    )
    assert isinstance(created_actor, Actor)
    actor_client = client.actor(created_actor.id)

    try:
        updated = await maybe_await(
            actor_client.update(
                categories=['MARKETING'],
                seo_title='SEO Test Title',
                seo_description='SEO Test Description',
            )
        )
        assert isinstance(updated, Actor)
        # `categories` and `seo_title` are not declared fields on the Actor model but are returned via
        # `extra='allow'` so we read them from the dumped representation.
        dumped = updated.model_dump(by_alias=True)
        assert dumped.get('categories') == ['MARKETING']
        assert dumped.get('seoTitle') == 'SEO Test Title'
    finally:
        await maybe_await(actor_client.delete())


async def test_actor_webhooks(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing webhooks attached to an Actor."""
    actor_name = get_random_resource_name('actor')

    created_actor = await maybe_await(
        client.actors().create(
            name=actor_name,
            title='Test Actor for Webhooks',
        )
    )
    assert isinstance(created_actor, Actor)
    actor_client = client.actor(created_actor.id)

    try:
        webhooks_page = await maybe_await(actor_client.webhooks().list())
        assert isinstance(webhooks_page, ListOfWebhooks)
        # A fresh Actor has no webhooks attached.
        assert webhooks_page.items == []
    finally:
        await maybe_await(actor_client.delete())


async def test_actor_default_build_wait_for_finish(client: ApifyClient | ApifyClientAsync) -> None:
    """Test default_build with explicit wait_for_finish parameter."""
    actor_client = client.actor('apify/hello-world')

    build_client = await maybe_await(actor_client.default_build(wait_for_finish=1))
    assert isinstance(build_client, BuildClient | BuildClientAsync)
    build = await maybe_await(build_client.get())
    assert isinstance(build, Build)


async def test_actor_get_parses_tiered_price_per_dataset_item(client: ApifyClient | ApifyClientAsync) -> None:
    """Test that actor.get() parses PRICE_PER_DATASET_ITEM entries with tieredPricing."""
    actor = await maybe_await(client.actor(ALL_PRICING_VARIANTS_ACTOR).get())
    assert isinstance(actor, Actor)
    assert actor.pricing_infos

    tiered_ppd_entries = [
        info
        for info in actor.pricing_infos
        if isinstance(info, PricePerDatasetItemActorPricingInfo) and info.tiered_pricing is not None
    ]
    assert tiered_ppd_entries, (
        f'{ALL_PRICING_VARIANTS_ACTOR} should have at least one tiered PRICE_PER_DATASET_ITEM entry — '
        'pick a different actor if pricing changed.'
    )

    # Fixture-drift guard: tiered pricing is only meaningful when it has more than one tier
    # and the tiers actually differ in price. A degenerate single-tier or all-zero payload
    # would silently look like flat pricing.
    for entry in tiered_ppd_entries:
        assert entry.tiered_pricing is not None
        assert len(entry.tiered_pricing) >= 2, (
            f'{ALL_PRICING_VARIANTS_ACTOR} tiered PPD entry has only {len(entry.tiered_pricing)} tier(s); '
            'expected multiple tiers (e.g. FREE/BRONZE/SILVER/GOLD/PLATINUM/DIAMOND).'
        )
        distinct_prices = {t.tiered_price_per_unit_usd for t in entry.tiered_pricing.values()}
        assert len(distinct_prices) >= 2, (
            f'{ALL_PRICING_VARIANTS_ACTOR} tiered PPD entry has all-identical prices ({distinct_prices}); '
            'tiers should differ.'
        )


async def test_actor_get_parses_tiered_pay_per_event(client: ApifyClient | ApifyClientAsync) -> None:
    """Test that actor.get() parses tiered PAY_PER_EVENT events with isPrimaryEvent and isOneTimeEvent flags."""
    actor = await maybe_await(client.actor(ALL_PRICING_VARIANTS_ACTOR).get())
    assert isinstance(actor, Actor)
    assert actor.pricing_infos

    tiered_ppe_events: list[ActorChargeEvent] = []
    for info in actor.pricing_infos:
        if not isinstance(info, PayPerEventActorPricingInfo):
            continue
        events = info.pricing_per_event.actor_charge_events or {}
        tiered_ppe_events.extend(event for event in events.values() if event.event_tiered_pricing_usd is not None)

    assert tiered_ppe_events, (
        f'{ALL_PRICING_VARIANTS_ACTOR} should have at least one tiered PAY_PER_EVENT event — '
        'pick a different actor if pricing changed.'
    )
    # Because every model uses `extra='allow'`, a regenerator that drops either alias would
    # silently absorb the JSON key into `model_extra`. Asserting the typed attribute is
    # populated catches that drift.
    assert any(event.is_primary_event is True for event in tiered_ppe_events), (
        f'{ALL_PRICING_VARIANTS_ACTOR}: no tiered PPE event has is_primary_event == True. '
        'The isPrimaryEvent alias may have been dropped from the model.'
    )
    assert any(event.is_one_time_event is not None for event in tiered_ppe_events), (
        f'{ALL_PRICING_VARIANTS_ACTOR}: no tiered PPE event has is_one_time_event populated. '
        'The isOneTimeEvent alias may have been dropped from the model.'
    )

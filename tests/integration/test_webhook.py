"""Unified tests for webhook (sync + async)."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync


from .._utils import collect_iterate_until_present, maybe_await
from apify_client._models import (
    ListOfRuns,
    ListOfWebhookDispatches,
    ListOfWebhooks,
    Run,
    Webhook,
    WebhookDispatch,
    WebhookShort,
)

HELLO_WORLD_ACTOR = 'apify/hello-world'


async def _get_finished_run_id(client: ApifyClient | ApifyClientAsync) -> str:
    """Get the ID of an already-completed run of the hello-world actor.

    Using a finished run's ID for webhook conditions ensures the webhook will never actually fire,
    since a completed run won't emit new events. If no completed runs exist, starts a new run and
    waits for it to finish.
    """
    runs_page = await maybe_await(client.actor(HELLO_WORLD_ACTOR).runs().list(limit=1, status='SUCCEEDED'))

    assert isinstance(runs_page, ListOfRuns)

    if len(runs_page.items) > 0:
        return runs_page.items[0].id

    # No completed runs found - start one and wait for it to finish
    run = await maybe_await(client.actor(HELLO_WORLD_ACTOR).call())

    assert isinstance(run, Run)

    return run.id


async def test_list_webhooks(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing webhooks."""
    webhooks_page = await maybe_await(client.webhooks().list(limit=10))

    assert isinstance(webhooks_page, ListOfWebhooks)
    assert isinstance(webhooks_page.items, list)


async def test_list_webhooks_pagination(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing webhooks with pagination."""
    webhooks_page = await maybe_await(client.webhooks().list(limit=5, offset=0))

    assert isinstance(webhooks_page, ListOfWebhooks)
    assert isinstance(webhooks_page.items, list)


async def test_webhook_create_and_get(client: ApifyClient | ApifyClientAsync) -> None:
    """Test creating a webhook and retrieving it."""
    run_id = await _get_finished_run_id(client)

    # Create webhook bound to a finished run (will never fire)
    created_webhook = await maybe_await(
        client.webhooks().create(
            event_types=['ACTOR.RUN.SUCCEEDED'],
            request_url='https://httpbin.org/post',
            actor_run_id=run_id,
            is_ad_hoc=True,
        )
    )

    try:
        assert isinstance(created_webhook, Webhook)

        # Get the same webhook
        webhook_client = client.webhook(created_webhook.id)
        retrieved_webhook = await maybe_await(webhook_client.get())

        assert isinstance(retrieved_webhook, Webhook)
        assert retrieved_webhook.id == created_webhook.id
    finally:
        await maybe_await(webhook_client.delete())


async def test_webhook_update(client: ApifyClient | ApifyClientAsync) -> None:
    """Test updating a webhook."""
    run_id = await _get_finished_run_id(client)

    # Create webhook bound to a finished run
    created_webhook = await maybe_await(
        client.webhooks().create(
            event_types=['ACTOR.RUN.SUCCEEDED'],
            request_url='https://httpbin.org/post',
            actor_run_id=run_id,
            is_ad_hoc=True,
        )
    )
    assert isinstance(created_webhook, Webhook)
    webhook_client = client.webhook(created_webhook.id)

    try:
        # Update webhook
        updated_webhook = await maybe_await(
            webhook_client.update(
                request_url='https://httpbin.org/anything',
                actor_run_id=run_id,
            )
        )
        assert isinstance(updated_webhook, Webhook)
        assert str(updated_webhook.request_url) == 'https://httpbin.org/anything'
    finally:
        await maybe_await(webhook_client.delete())


async def test_webhook_test(client: ApifyClient | ApifyClientAsync) -> None:
    """Test the webhook test endpoint."""
    run_id = await _get_finished_run_id(client)

    # Create webhook bound to a finished run
    created_webhook = await maybe_await(
        client.webhooks().create(
            event_types=['ACTOR.RUN.SUCCEEDED'],
            request_url='https://httpbin.org/post',
            actor_run_id=run_id,
            is_ad_hoc=True,
        )
    )
    assert isinstance(created_webhook, Webhook)
    webhook_client = client.webhook(created_webhook.id)

    try:
        # Test webhook (creates a dispatch with dummy payload)
        dispatch = await maybe_await(webhook_client.test())
        assert isinstance(dispatch, WebhookDispatch)
        assert dispatch.id is not None
    finally:
        await maybe_await(webhook_client.delete())


async def test_webhook_dispatches(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing webhook dispatches."""
    run_id = await _get_finished_run_id(client)

    # Create webhook bound to a finished run
    created_webhook = await maybe_await(
        client.webhooks().create(
            event_types=['ACTOR.RUN.SUCCEEDED'],
            request_url='https://httpbin.org/post',
            actor_run_id=run_id,
            is_ad_hoc=True,
        )
    )

    assert isinstance(created_webhook, Webhook)
    webhook_client = client.webhook(created_webhook.id)

    try:
        # Test webhook to create a dispatch
        await maybe_await(webhook_client.test())

        # List dispatches for this webhook
        dispatches = await maybe_await(webhook_client.dispatches().list())
        assert isinstance(dispatches, ListOfWebhookDispatches)
        assert len(dispatches.items) > 0

    finally:
        await maybe_await(webhook_client.delete())


async def test_webhook_delete(client: ApifyClient | ApifyClientAsync) -> None:
    """Test deleting a webhook."""
    run_id = await _get_finished_run_id(client)

    # Create webhook bound to a finished run
    created_webhook = await maybe_await(
        client.webhooks().create(
            event_types=['ACTOR.RUN.SUCCEEDED'],
            request_url='https://httpbin.org/post',
            actor_run_id=run_id,
            is_ad_hoc=True,
        )
    )
    assert isinstance(created_webhook, Webhook)
    webhook_client = client.webhook(created_webhook.id)

    # Delete webhook
    await maybe_await(webhook_client.delete())

    # Verify it's gone
    retrieved_webhook = await maybe_await(webhook_client.get())
    assert retrieved_webhook is None


async def test_webhook_collection_iterate(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test paginated iteration over user webhooks."""
    run_id = await _get_finished_run_id(client)

    created_ids: list[str] = []
    # Use distinct request URLs so the API does not dedupe webhooks by (event_types, run_id, url)
    for i in range(3):
        webhook = await maybe_await(
            client.webhooks().create(
                event_types=['ACTOR.RUN.SUCCEEDED'],
                request_url=f'https://httpbin.org/post?n={i}',
                actor_run_id=run_id,
                is_ad_hoc=True,
            )
        )
        assert isinstance(webhook, Webhook)
        created_ids.append(webhook.id)

    # The API must return 3 distinct webhooks - otherwise dedup happened
    assert len(set(created_ids)) == 3

    try:
        collected = await collect_iterate_until_present(
            lambda: client.webhooks().iterate(desc=True),
            set(created_ids),
            item_type=WebhookShort,
            is_async=is_async,
        )
        collected_ids = {w.id for w in collected}
        for webhook_id in created_ids:
            assert webhook_id in collected_ids
    finally:
        for webhook_id in created_ids:
            await maybe_await(client.webhook(webhook_id).delete())


async def test_webhook_get_nonexistent_returns_none(client: ApifyClient | ApifyClientAsync) -> None:
    """Test that get() on a non-existent webhook returns None."""
    webhook = await maybe_await(client.webhook('NoNeXiStEnTwH').get())
    assert webhook is None


async def test_webhook_dispatches_iterate(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test paginated iteration over a webhook's dispatches."""
    run_id = await _get_finished_run_id(client)

    created_webhook = await maybe_await(
        client.webhooks().create(
            event_types=['ACTOR.RUN.SUCCEEDED'],
            request_url='https://httpbin.org/post',
            actor_run_id=run_id,
            is_ad_hoc=True,
        )
    )
    assert isinstance(created_webhook, Webhook)
    webhook_client = client.webhook(created_webhook.id)

    try:
        # Generate at least one dispatch by hitting the test endpoint
        await maybe_await(webhook_client.test())

        iterator = webhook_client.dispatches().iterate(limit=10)
        collected: list[WebhookDispatch] = []
        if is_async:
            assert isinstance(iterator, AsyncIterator)
            async for d in iterator:
                assert isinstance(d, WebhookDispatch)
                collected.append(d)
        else:
            assert isinstance(iterator, Iterator)
            for d in iterator:
                assert isinstance(d, WebhookDispatch)
                collected.append(d)

        assert len(collected) >= 1
        for dispatch in collected:
            assert dispatch.id is not None
    finally:
        await maybe_await(webhook_client.delete())

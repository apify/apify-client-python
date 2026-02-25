"""Unified tests for webhook (sync + async)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync


from ._utils import maybe_await
from apify_client._models import (
    ActorJobStatus,
    ListOfRuns,
    ListOfWebhookDispatches,
    ListOfWebhooks,
    Webhook,
    WebhookDispatch,
    WebhookEventType,
)

HELLO_WORLD_ACTOR = 'apify/hello-world'


async def _get_finished_run_id(client: ApifyClient | ApifyClientAsync) -> str:
    """Get the ID of an already-completed run of the hello-world actor.

    Using a finished run's ID for webhook conditions ensures the webhook will never actually fire,
    since a completed run won't emit new events. If no completed runs exist, starts a new run and
    waits for it to finish.
    """
    runs_page = await maybe_await(client.actor(HELLO_WORLD_ACTOR).runs().list(limit=1, status=ActorJobStatus.SUCCEEDED))

    assert isinstance(runs_page, ListOfRuns)

    if len(runs_page.items) > 0:
        return runs_page.items[0].id

    # No completed runs found - start one and wait for it to finish
    run = await maybe_await(client.actor(HELLO_WORLD_ACTOR).call())

    assert isinstance(run, ListOfRuns)

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
            event_types=[WebhookEventType.ACTOR_RUN_SUCCEEDED],
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
            event_types=[WebhookEventType.ACTOR_RUN_SUCCEEDED],
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
            event_types=[WebhookEventType.ACTOR_RUN_SUCCEEDED],
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
            event_types=[WebhookEventType.ACTOR_RUN_SUCCEEDED],
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
            event_types=[WebhookEventType.ACTOR_RUN_SUCCEEDED],
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

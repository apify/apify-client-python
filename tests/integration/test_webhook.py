"""Unified tests for webhook (sync + async)."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync
    from apify_client._models import Actor, ListOfWebhookDispatches, ListOfWebhooks, Webhook, WebhookDispatch


from .conftest import maybe_await
from apify_client._models import WebhookEventType

HELLO_WORLD_ACTOR = 'apify/hello-world'


async def test_list_webhooks(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing webhooks."""
    result = await maybe_await(client.webhooks().list(limit=10))
    webhooks_page = cast('ListOfWebhooks', result)

    assert webhooks_page is not None
    assert webhooks_page.items is not None
    # User may have 0 webhooks
    assert isinstance(webhooks_page.items, list)


async def test_list_webhooks_pagination(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing webhooks with pagination."""
    result = await maybe_await(client.webhooks().list(limit=5, offset=0))
    webhooks_page = cast('ListOfWebhooks', result)

    assert webhooks_page is not None
    assert webhooks_page.items is not None
    assert isinstance(webhooks_page.items, list)


async def test_webhook_create_and_get(client: ApifyClient | ApifyClientAsync) -> None:
    """Test creating a webhook and retrieving it."""
    # Get actor ID for webhook condition
    result = await maybe_await(client.actor(HELLO_WORLD_ACTOR).get())
    actor = cast('Actor', result)
    assert actor is not None

    # Create webhook (use httpbin as dummy endpoint)
    result = await maybe_await(
        client.webhooks().create(
            event_types=[WebhookEventType.ACTOR_RUN_SUCCEEDED],
            request_url='https://httpbin.org/post',
            actor_id=actor.id,
        )
    )
    created_webhook = cast('Webhook', result)
    assert created_webhook is not None
    assert created_webhook.id is not None

    # Get the same webhook
    webhook_client = client.webhook(created_webhook.id)
    result = await maybe_await(webhook_client.get())
    retrieved_webhook = cast('Webhook', result)
    assert retrieved_webhook is not None
    assert retrieved_webhook.id == created_webhook.id

    # Cleanup
    await maybe_await(webhook_client.delete())


async def test_webhook_update(client: ApifyClient | ApifyClientAsync) -> None:
    """Test updating a webhook."""
    result = await maybe_await(client.actor(HELLO_WORLD_ACTOR).get())
    actor = cast('Actor', result)
    assert actor is not None

    # Create webhook
    result = await maybe_await(
        client.webhooks().create(
            event_types=[WebhookEventType.ACTOR_RUN_SUCCEEDED],
            request_url='https://httpbin.org/post',
            actor_id=actor.id,
        )
    )
    created_webhook = cast('Webhook', result)
    webhook_client = client.webhook(created_webhook.id)

    # Update webhook (must include actor_id as condition is required)
    result = await maybe_await(
        webhook_client.update(
            request_url='https://httpbin.org/anything',
            actor_id=actor.id,
        )
    )
    updated_webhook = cast('Webhook', result)
    assert str(updated_webhook.request_url) == 'https://httpbin.org/anything'

    # Cleanup
    await maybe_await(webhook_client.delete())


async def test_webhook_test(client: ApifyClient | ApifyClientAsync) -> None:
    """Test the webhook test endpoint."""
    result = await maybe_await(client.actor(HELLO_WORLD_ACTOR).get())
    actor = cast('Actor', result)
    assert actor is not None

    # Create webhook
    result = await maybe_await(
        client.webhooks().create(
            event_types=[WebhookEventType.ACTOR_RUN_SUCCEEDED],
            request_url='https://httpbin.org/post',
            actor_id=actor.id,
        )
    )
    created_webhook = cast('Webhook', result)
    webhook_client = client.webhook(created_webhook.id)

    # Test webhook (creates a dispatch)
    result = await maybe_await(webhook_client.test())
    dispatch = cast('WebhookDispatch', result)
    assert dispatch is not None
    assert dispatch.id is not None

    # Cleanup
    await maybe_await(webhook_client.delete())


async def test_webhook_dispatches(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing webhook dispatches."""
    result = await maybe_await(client.actor(HELLO_WORLD_ACTOR).get())
    actor = cast('Actor', result)
    assert actor is not None

    # Create webhook
    result = await maybe_await(
        client.webhooks().create(
            event_types=[WebhookEventType.ACTOR_RUN_SUCCEEDED],
            request_url='https://httpbin.org/post',
            actor_id=actor.id,
        )
    )
    created_webhook = cast('Webhook', result)
    webhook_client = client.webhook(created_webhook.id)

    # Test webhook to create a dispatch
    await maybe_await(webhook_client.test())

    # List dispatches for this webhook
    result = await maybe_await(webhook_client.dispatches().list())
    dispatches = cast('ListOfWebhookDispatches', result)
    assert dispatches is not None
    assert dispatches.items is not None
    assert len(dispatches.items) > 0

    # Cleanup
    await maybe_await(webhook_client.delete())


async def test_webhook_delete(client: ApifyClient | ApifyClientAsync) -> None:
    """Test deleting a webhook."""
    result = await maybe_await(client.actor(HELLO_WORLD_ACTOR).get())
    actor = cast('Actor', result)
    assert actor is not None

    # Create webhook
    result = await maybe_await(
        client.webhooks().create(
            event_types=[WebhookEventType.ACTOR_RUN_SUCCEEDED],
            request_url='https://httpbin.org/post',
            actor_id=actor.id,
        )
    )
    created_webhook = cast('Webhook', result)
    webhook_client = client.webhook(created_webhook.id)

    # Delete webhook
    await maybe_await(webhook_client.delete())

    # Verify it's gone
    retrieved_webhook = await maybe_await(webhook_client.get())
    assert retrieved_webhook is None

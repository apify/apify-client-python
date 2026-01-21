from __future__ import annotations

from typing import TYPE_CHECKING

from apify_shared.consts import WebhookEventType

if TYPE_CHECKING:
    from apify_client import ApifyClient

HELLO_WORLD_ACTOR = 'apify/hello-world'


def test_list_webhooks(apify_client: ApifyClient) -> None:
    """Test listing webhooks."""
    webhooks_page = apify_client.webhooks().list(limit=10)

    assert webhooks_page is not None
    assert webhooks_page.items is not None
    # User may have 0 webhooks
    assert isinstance(webhooks_page.items, list)


def test_list_webhooks_pagination(apify_client: ApifyClient) -> None:
    """Test listing webhooks with pagination."""
    webhooks_page = apify_client.webhooks().list(limit=5, offset=0)

    assert webhooks_page is not None
    assert webhooks_page.items is not None
    assert isinstance(webhooks_page.items, list)


def test_webhook_create_and_get(apify_client: ApifyClient) -> None:
    """Test creating a webhook and retrieving it."""
    # Get actor ID for webhook condition
    actor = apify_client.actor(HELLO_WORLD_ACTOR).get()
    assert actor is not None

    # Create webhook (use httpbin as dummy endpoint)
    created_webhook = apify_client.webhooks().create(
        event_types=[WebhookEventType.ACTOR_RUN_SUCCEEDED],
        request_url='https://httpbin.org/post',
        actor_id=actor.id,
    )
    assert created_webhook is not None
    assert created_webhook.id is not None

    # Get the same webhook
    webhook_client = apify_client.webhook(created_webhook.id)
    retrieved_webhook = webhook_client.get()
    assert retrieved_webhook is not None
    assert retrieved_webhook.id == created_webhook.id

    # Cleanup
    webhook_client.delete()


def test_webhook_update(apify_client: ApifyClient) -> None:
    """Test updating a webhook."""
    actor = apify_client.actor(HELLO_WORLD_ACTOR).get()
    assert actor is not None

    # Create webhook
    created_webhook = apify_client.webhooks().create(
        event_types=[WebhookEventType.ACTOR_RUN_SUCCEEDED],
        request_url='https://httpbin.org/post',
        actor_id=actor.id,
    )
    webhook_client = apify_client.webhook(created_webhook.id)

    # Update webhook (must include actor_id as condition is required)
    updated_webhook = webhook_client.update(
        request_url='https://httpbin.org/anything',
        actor_id=actor.id,
    )
    assert str(updated_webhook.request_url) == 'https://httpbin.org/anything'

    # Cleanup
    webhook_client.delete()


def test_webhook_test(apify_client: ApifyClient) -> None:
    """Test the webhook test endpoint."""
    actor = apify_client.actor(HELLO_WORLD_ACTOR).get()
    assert actor is not None

    # Create webhook
    created_webhook = apify_client.webhooks().create(
        event_types=[WebhookEventType.ACTOR_RUN_SUCCEEDED],
        request_url='https://httpbin.org/post',
        actor_id=actor.id,
    )
    webhook_client = apify_client.webhook(created_webhook.id)

    # Test webhook (creates a dispatch)
    dispatch = webhook_client.test()
    assert dispatch is not None
    assert dispatch.id is not None

    # Cleanup
    webhook_client.delete()


def test_webhook_dispatches(apify_client: ApifyClient) -> None:
    """Test listing webhook dispatches."""
    actor = apify_client.actor(HELLO_WORLD_ACTOR).get()
    assert actor is not None

    # Create webhook
    created_webhook = apify_client.webhooks().create(
        event_types=[WebhookEventType.ACTOR_RUN_SUCCEEDED],
        request_url='https://httpbin.org/post',
        actor_id=actor.id,
    )
    webhook_client = apify_client.webhook(created_webhook.id)

    # Test webhook to create a dispatch
    webhook_client.test()

    # List dispatches for this webhook
    dispatches = webhook_client.dispatches().list()
    assert dispatches is not None
    assert dispatches.items is not None
    assert len(dispatches.items) > 0

    # Cleanup
    webhook_client.delete()


def test_webhook_delete(apify_client: ApifyClient) -> None:
    """Test deleting a webhook."""
    actor = apify_client.actor(HELLO_WORLD_ACTOR).get()
    assert actor is not None

    # Create webhook
    created_webhook = apify_client.webhooks().create(
        event_types=[WebhookEventType.ACTOR_RUN_SUCCEEDED],
        request_url='https://httpbin.org/post',
        actor_id=actor.id,
    )
    webhook_client = apify_client.webhook(created_webhook.id)

    # Delete webhook
    webhook_client.delete()

    # Verify it's gone
    retrieved_webhook = webhook_client.get()
    assert retrieved_webhook is None

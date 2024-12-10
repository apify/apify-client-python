from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_shared.utils import filter_out_none_values_recursively, ignore_docs

from apify_client.clients.base import ResourceCollectionClient, ResourceCollectionClientAsync
from apify_client.clients.resource_clients.webhook import get_webhook_representation

if TYPE_CHECKING:
    from apify_shared.consts import WebhookEventType
    from apify_shared.models import ListPage


class WebhookCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating webhooks."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'webhooks')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListPage[dict]:
        """List the available webhooks.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-collection/get-list-of-webhooks

        Args:
            limit: How many webhooks to retrieve.
            offset: What webhook to include as first when retrieving the list.
            desc: Whether to sort the webhooks in descending order based on their date of creation.

        Returns:
            The list of available webhooks matching the specified filters.
        """
        return self._list(limit=limit, offset=offset, desc=desc)

    def create(
        self,
        *,
        event_types: list[WebhookEventType],  # type: ignore[valid-type]
        request_url: str,
        payload_template: str | None = None,
        headers_template: str | None = None,
        actor_id: str | None = None,
        actor_task_id: str | None = None,
        actor_run_id: str | None = None,
        ignore_ssl_errors: bool | None = None,
        do_not_retry: bool | None = None,
        idempotency_key: str | None = None,
        is_ad_hoc: bool | None = None,
    ) -> dict:
        """Create a new webhook.

        You have to specify exactly one out of actor_id, actor_task_id or actor_run_id.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-collection/create-webhook

        Args:
            event_types: List of event types that should trigger the webhook. At least one is required.
            request_url: URL that will be invoked once the webhook is triggered.
            payload_template: Specification of the payload that will be sent to request_url.
            headers_template: Headers that will be sent to the request_url.
            actor_id: Id of the Actor whose runs should trigger the webhook.
            actor_task_id: Id of the Actor task whose runs should trigger the webhook.
            actor_run_id: Id of the Actor run which should trigger the webhook.
            ignore_ssl_errors: Whether the webhook should ignore SSL errors returned by request_url.
            do_not_retry: Whether the webhook should retry sending the payload to request_url upon failure.
            idempotency_key: A unique identifier of a webhook. You can use it to ensure that you won't create
                the same webhook multiple times.
            is_ad_hoc: Set to True if you want the webhook to be triggered only the first time the condition
                is fulfilled. Only applicable when actor_run_id is filled.

        Returns:
           The created webhook.
        """
        webhook_representation = get_webhook_representation(
            event_types=event_types,
            request_url=request_url,
            payload_template=payload_template,
            headers_template=headers_template,
            actor_id=actor_id,
            actor_task_id=actor_task_id,
            actor_run_id=actor_run_id,
            ignore_ssl_errors=ignore_ssl_errors,
            do_not_retry=do_not_retry,
            idempotency_key=idempotency_key,
            is_ad_hoc=is_ad_hoc,
        )

        return self._create(filter_out_none_values_recursively(webhook_representation))


class WebhookCollectionClientAsync(ResourceCollectionClientAsync):
    """Async sub-client for manipulating webhooks."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'webhooks')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListPage[dict]:
        """List the available webhooks.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-collection/get-list-of-webhooks

        Args:
            limit: How many webhooks to retrieve.
            offset: What webhook to include as first when retrieving the list.
            desc: Whether to sort the webhooks in descending order based on their date of creation.

        Returns:
            The list of available webhooks matching the specified filters.
        """
        return await self._list(limit=limit, offset=offset, desc=desc)

    async def create(
        self,
        *,
        event_types: list[WebhookEventType],  # type: ignore[valid-type]
        request_url: str,
        payload_template: str | None = None,
        headers_template: str | None = None,
        actor_id: str | None = None,
        actor_task_id: str | None = None,
        actor_run_id: str | None = None,
        ignore_ssl_errors: bool | None = None,
        do_not_retry: bool | None = None,
        idempotency_key: str | None = None,
        is_ad_hoc: bool | None = None,
    ) -> dict:
        """Create a new webhook.

        You have to specify exactly one out of actor_id, actor_task_id or actor_run_id.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-collection/create-webhook

        Args:
            event_types: List of event types that should trigger the webhook. At least one is required.
            request_url: URL that will be invoked once the webhook is triggered.
            payload_template: Specification of the payload that will be sent to request_url.
            headers_template: Headers that will be sent to the request_url.
            actor_id: Id of the Actor whose runs should trigger the webhook.
            actor_task_id: Id of the Actor task whose runs should trigger the webhook.
            actor_run_id: Id of the Actor run which should trigger the webhook.
            ignore_ssl_errors: Whether the webhook should ignore SSL errors returned by request_url.
            do_not_retry: Whether the webhook should retry sending the payload to request_url upon failure.
            idempotency_key: A unique identifier of a webhook. You can use it to ensure that you won't create
                the same webhook multiple times.
            is_ad_hoc: Set to True if you want the webhook to be triggered only the first time the condition
                is fulfilled. Only applicable when actor_run_id is filled.

        Returns:
           The created webhook.
        """
        webhook_representation = get_webhook_representation(
            event_types=event_types,
            request_url=request_url,
            payload_template=payload_template,
            headers_template=headers_template,
            actor_id=actor_id,
            actor_task_id=actor_task_id,
            actor_run_id=actor_run_id,
            ignore_ssl_errors=ignore_ssl_errors,
            do_not_retry=do_not_retry,
            idempotency_key=idempotency_key,
            is_ad_hoc=is_ad_hoc,
        )

        return await self._create(filter_out_none_values_recursively(webhook_representation))

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._models_generated import (
    ListOfWebhooksResponse,
    WebhookCondition,
    WebhookCreate,
    WebhookResponse,
)
from apify_client._pagination import (
    _LazyTask,
    build_get_iterator,
    build_get_iterator_async,
)
from apify_client._pagination_classes import (
    IterablePageOfWebhooks,
    IterablePageOfWebhooksAsync,
    PageOfItems,
)
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync

if TYPE_CHECKING:
    from apify_client._models_generated import Webhook, WebhookEventType, WebhookShort
    from apify_client._types import Timeout


@docs_group('Resource clients')
class WebhookCollectionClient(ResourceClient):
    """Sub-client for the webhook collection.

    Provides methods to manage the webhook collection, e.g. list or create webhooks. Obtain an instance via an
    appropriate method on the `ApifyClient` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'webhooks',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_path=resource_path,
            **kwargs,
        )

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        timeout: Timeout = 'medium',
    ) -> IterablePageOfWebhooks:
        """List the available webhooks.

        The returned page also supports iteration: `for item in client.list(...)` yields individual webhooks
        and transparently fetches further pages from the API.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-collection/get-list-of-webhooks

        Args:
            limit: How many webhooks to retrieve.
            offset: What webhook to include as first when retrieving the list.
            desc: Whether to sort the webhooks in descending order based on their date of creation.
            timeout: Timeout for the API HTTP request.

        Returns:
            The list of available webhooks matching the specified filters.
        """

        def _callback(**kwargs: Any) -> PageOfItems[WebhookShort]:
            result = self._list(timeout=timeout, **kwargs)
            data = ListOfWebhooksResponse.model_validate(result).data
            return PageOfItems(
                items=data.items,
                count=data.count,
                limit=data.limit,
                total=data.total,
                offset=data.offset,
                desc=data.desc,
            )

        first_page = _callback(limit=limit, offset=offset, desc=desc)
        get_iterator = build_get_iterator(_callback, first_page, limit=limit, offset=offset, desc=desc)

        return IterablePageOfWebhooks(
            _get_iterator=get_iterator,
            items=first_page.items,
            count=first_page.count,
            limit=first_page.limit,
            total=first_page.total,
            offset=first_page.offset,
            desc=first_page.desc,
        )

    def create(
        self,
        *,
        event_types: list[WebhookEventType],  # ty: ignore[invalid-type-form]
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
        timeout: Timeout = 'short',
    ) -> Webhook:
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
            timeout: Timeout for the API HTTP request.

        Returns:
           The created webhook.
        """
        webhook_create = WebhookCreate(
            event_types=list(event_types),
            request_url=request_url,
            payload_template=payload_template,
            headers_template=headers_template,
            ignore_ssl_errors=ignore_ssl_errors,
            do_not_retry=do_not_retry,
            idempotency_key=idempotency_key,
            is_ad_hoc=is_ad_hoc if actor_run_id else None,
            condition=WebhookCondition(
                actor_run_id=actor_run_id,
                actor_task_id=actor_task_id,
                actor_id=actor_id,
            ),
        )
        result = self._create(timeout=timeout, **webhook_create.model_dump(by_alias=True, exclude_none=True))
        return WebhookResponse.model_validate(result).data


@docs_group('Resource clients')
class WebhookCollectionClientAsync(ResourceClientAsync):
    """Sub-client for the webhook collection.

    Provides methods to manage the webhook collection, e.g. list or create webhooks. Obtain an instance via an
    appropriate method on the `ApifyClientAsync` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'webhooks',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_path=resource_path,
            **kwargs,
        )

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        timeout: Timeout = 'medium',
    ) -> IterablePageOfWebhooksAsync:
        """List the available webhooks.

        The returned page also supports iteration: `async for item in client.list(...)` yields individual webhooks
        and transparently fetches further pages from the API.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-collection/get-list-of-webhooks

        Args:
            limit: How many webhooks to retrieve.
            offset: What webhook to include as first when retrieving the list.
            desc: Whether to sort the webhooks in descending order based on their date of creation.
            timeout: Timeout for the API HTTP request.

        Returns:
            The list of available webhooks matching the specified filters.
        """

        async def _callback(**kwargs: Any) -> PageOfItems[WebhookShort]:
            result = await self._list(timeout=timeout, **kwargs)
            data = ListOfWebhooksResponse.model_validate(result).data
            return PageOfItems(
                items=data.items,
                count=data.count,
                limit=data.limit,
                total=data.total,
                offset=data.offset,
                desc=data.desc,
            )

        fetch_first_page = _LazyTask(_callback(limit=limit, offset=offset, desc=desc))
        get_async_iterator = build_get_iterator_async(
            _callback, fetch_first_page, limit=limit, offset=offset, desc=desc
        )

        return IterablePageOfWebhooksAsync(
            _awaitable_first_page=fetch_first_page,
            _get_async_iterator=get_async_iterator,
        )

    async def create(
        self,
        *,
        event_types: list[WebhookEventType],  # ty: ignore[invalid-type-form]
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
        timeout: Timeout = 'short',
    ) -> Webhook:
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
            timeout: Timeout for the API HTTP request.

        Returns:
           The created webhook.
        """
        webhook_create = WebhookCreate(
            event_types=list(event_types),
            request_url=request_url,
            payload_template=payload_template,
            headers_template=headers_template,
            ignore_ssl_errors=ignore_ssl_errors,
            do_not_retry=do_not_retry,
            idempotency_key=idempotency_key,
            is_ad_hoc=is_ad_hoc if actor_run_id else None,
            condition=WebhookCondition(
                actor_run_id=actor_run_id,
                actor_task_id=actor_task_id,
                actor_id=actor_id,
            ),
        )
        result = await self._create(timeout=timeout, **webhook_create.model_dump(by_alias=True, exclude_none=True))
        return WebhookResponse.model_validate(result).data

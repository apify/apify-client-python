from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._iterable_list import (
    AwaitableAsyncIterable,
    IterableListOfWebhooks,
    build_awaitable_async_iterable_offset,
    build_iterable_offset,
)
from apify_client._models import (
    WebhookCondition,
    WebhookCreate,
    WebhookResponse,
)
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync

if TYPE_CHECKING:
    from apify_client._models import Webhook, WebhookEventType, WebhookShort
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
    ) -> IterableListOfWebhooks:
        """List the available webhooks.

        The returned value is a `ListOfWebhooks` that additionally implements `Iterable[WebhookShort]`:
        callers can use `.items` / `.total` / etc. for the first page's metadata, or iterate with
        `for item in client.list(...)` to transparently fetch further pages.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-collection/get-list-of-webhooks

        Args:
            limit: How many webhooks to retrieve.
            offset: What webhook to include as first when retrieving the list.
            desc: Whether to sort the webhooks in descending order based on their date of creation.
            timeout: Timeout for the API HTTP request.

        Returns:
            The list of available webhooks matching the specified filters.
        """

        def _callback(**kwargs: Any) -> IterableListOfWebhooks:
            result = self._list(timeout=timeout, **kwargs)
            # Validate directly into the iterable subclass so `isinstance(result, ListOfWebhooks)`
            # and typed field access work on the returned value without indirection.
            return IterableListOfWebhooks.model_validate(result.get('data') if isinstance(result, dict) else result)

        return build_iterable_offset(_callback, limit=limit, offset=offset, desc=desc)

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
    ) -> AwaitableAsyncIterable[IterableListOfWebhooks, WebhookShort]:
        """List the available webhooks.

        The returned value is a `ListOfWebhooks` that additionally implements `Iterable[WebhookShort]`:
        callers can use `.items` / `.total` / etc. for the first page's metadata, or iterate with
        `for item in client.list(...)` to transparently fetch further pages.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-collection/get-list-of-webhooks

        Args:
            limit: How many webhooks to retrieve.
            offset: What webhook to include as first when retrieving the list.
            desc: Whether to sort the webhooks in descending order based on their date of creation.
            timeout: Timeout for the API HTTP request.

        Returns:
            The list of available webhooks matching the specified filters.
        """

        async def _callback(**kwargs: Any) -> IterableListOfWebhooks:
            result = await self._list(timeout=timeout, **kwargs)
            return IterableListOfWebhooks.model_validate(result.get('data') if isinstance(result, dict) else result)

        return build_awaitable_async_iterable_offset(_callback, limit=limit, offset=offset, desc=desc)

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

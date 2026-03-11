from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import AnyUrl

from apify_client._docs import docs_group
from apify_client._models import (
    TestWebhookResponse,
    Webhook,
    WebhookCondition,
    WebhookDispatch,
    WebhookResponse,
    WebhookUpdate,
)
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import catch_not_found_or_throw, response_to_dict
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from apify_client._models import WebhookEventType
    from apify_client._resource_clients import WebhookDispatchCollectionClient, WebhookDispatchCollectionClientAsync
    from apify_client._types import Timeout


@docs_group('Resource clients')
class WebhookClient(ResourceClient):
    """Sub-client for managing a specific webhook.

    Provides methods to manage a specific webhook, e.g. get, update, or delete it. Obtain an instance via an
    appropriate method on the `ApifyClient` class.
    """

    def __init__(
        self,
        *,
        resource_id: str,
        resource_path: str = 'webhooks',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_id=resource_id,
            resource_path=resource_path,
            **kwargs,
        )

    def get(self, *, timeout: Timeout = 'short') -> Webhook | None:
        """Retrieve the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/get-webhook

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved webhook, or None if it does not exist.
        """
        result = self._get(timeout=timeout)
        if result is None:
            return None
        return WebhookResponse.model_validate(result).data

    def update(
        self,
        *,
        event_types: list[WebhookEventType] | None = None,
        request_url: str | None = None,
        payload_template: str | None = None,
        headers_template: str | None = None,
        actor_id: str | None = None,
        actor_task_id: str | None = None,
        actor_run_id: str | None = None,
        ignore_ssl_errors: bool | None = None,
        do_not_retry: bool | None = None,
        is_ad_hoc: bool | None = None,
        timeout: Timeout = 'short',
    ) -> Webhook:
        """Update the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/update-webhook

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
            is_ad_hoc: Set to True if you want the webhook to be triggered only the first time the condition
                is fulfilled. Only applicable when actor_run_id is filled.
            timeout: Timeout for the API HTTP request.

        Returns:
            The updated webhook.
        """
        webhook_update = WebhookUpdate(
            event_types=list(event_types) if event_types is not None else None,
            request_url=AnyUrl(request_url) if request_url is not None else None,
            payload_template=payload_template,
            headers_template=headers_template,
            ignore_ssl_errors=ignore_ssl_errors,
            do_not_retry=do_not_retry,
            is_ad_hoc=is_ad_hoc if actor_run_id else None,
            condition=WebhookCondition(
                actor_run_id=actor_run_id,
                actor_task_id=actor_task_id,
                actor_id=actor_id,
            ),
        )
        result = self._update(timeout=timeout, **webhook_update.model_dump(by_alias=True, exclude_none=True))
        return WebhookResponse.model_validate(result).data

    def delete(self, *, timeout: Timeout = 'short') -> None:
        """Delete the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/delete-webhook

        Args:
            timeout: Timeout for the API HTTP request.
        """
        self._delete(timeout=timeout)

    def test(self, *, timeout: Timeout = 'medium') -> WebhookDispatch | None:
        """Test a webhook.

        Creates a webhook dispatch with a dummy payload.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-test/test-webhook

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The webhook dispatch created by the test.
        """
        try:
            response = self._http_client.call(
                url=self._build_url('test'),
                method='POST',
                params=self._build_params(),
                timeout=timeout,
            )

            result = response_to_dict(response)
            return TestWebhookResponse.model_validate(result).data

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    def dispatches(self) -> WebhookDispatchCollectionClient:
        """Get dispatches of the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/dispatches-collection/get-collection

        Returns:
            A client allowing access to dispatches of this webhook using its list method.
        """
        return self._client_registry.webhook_dispatch_collection_client(
            resource_path='dispatches',
            **self._base_client_kwargs,
        )


@docs_group('Resource clients')
class WebhookClientAsync(ResourceClientAsync):
    """Sub-client for managing a specific webhook.

    Provides methods to manage a specific webhook, e.g. get, update, or delete it. Obtain an instance via an
    appropriate method on the `ApifyClientAsync` class.
    """

    def __init__(
        self,
        *,
        resource_id: str,
        resource_path: str = 'webhooks',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_id=resource_id,
            resource_path=resource_path,
            **kwargs,
        )

    async def get(self, *, timeout: Timeout = 'short') -> Webhook | None:
        """Retrieve the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/get-webhook

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved webhook, or None if it does not exist.
        """
        result = await self._get(timeout=timeout)
        if result is None:
            return None
        return WebhookResponse.model_validate(result).data

    async def update(
        self,
        *,
        event_types: list[WebhookEventType] | None = None,
        request_url: str | None = None,
        payload_template: str | None = None,
        headers_template: str | None = None,
        actor_id: str | None = None,
        actor_task_id: str | None = None,
        actor_run_id: str | None = None,
        ignore_ssl_errors: bool | None = None,
        do_not_retry: bool | None = None,
        is_ad_hoc: bool | None = None,
        timeout: Timeout = 'short',
    ) -> Webhook:
        """Update the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/update-webhook

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
            is_ad_hoc: Set to True if you want the webhook to be triggered only the first time the condition
                is fulfilled. Only applicable when actor_run_id is filled.
            timeout: Timeout for the API HTTP request.

        Returns:
            The updated webhook.
        """
        webhook_update = WebhookUpdate(
            event_types=list(event_types) if event_types is not None else None,
            request_url=AnyUrl(request_url) if request_url is not None else None,
            payload_template=payload_template,
            headers_template=headers_template,
            ignore_ssl_errors=ignore_ssl_errors,
            do_not_retry=do_not_retry,
            is_ad_hoc=is_ad_hoc if actor_run_id else None,
            condition=WebhookCondition(
                actor_run_id=actor_run_id,
                actor_task_id=actor_task_id,
                actor_id=actor_id,
            ),
        )
        result = await self._update(timeout=timeout, **webhook_update.model_dump(by_alias=True, exclude_none=True))
        return WebhookResponse.model_validate(result).data

    async def delete(self, *, timeout: Timeout = 'short') -> None:
        """Delete the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/delete-webhook

        Args:
            timeout: Timeout for the API HTTP request.
        """
        await self._delete(timeout=timeout)

    async def test(self, *, timeout: Timeout = 'medium') -> WebhookDispatch | None:
        """Test a webhook.

        Creates a webhook dispatch with a dummy payload.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-test/test-webhook

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The webhook dispatch created by the test.
        """
        try:
            response = await self._http_client.call(
                url=self._build_url('test'),
                method='POST',
                params=self._build_params(),
                timeout=timeout,
            )

            result = response_to_dict(response)
            return TestWebhookResponse.model_validate(result).data

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    def dispatches(self) -> WebhookDispatchCollectionClientAsync:
        """Get dispatches of the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/dispatches-collection/get-collection

        Returns:
            A client allowing access to dispatches of this webhook using its list method.
        """
        return self._client_registry.webhook_dispatch_collection_client(
            resource_path='dispatches',
            **self._base_client_kwargs,
        )

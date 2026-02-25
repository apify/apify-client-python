from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._models import (
    TestWebhookResponse,
    Webhook,
    WebhookDispatch,
    WebhookResponse,
)
from apify_client._representations import get_webhook_repr
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import catch_not_found_or_throw, filter_none_values, response_to_dict
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from apify_client._models import WebhookEventType
    from apify_client._resource_clients import WebhookDispatchCollectionClient, WebhookDispatchCollectionClientAsync


@docs_group('Resource clients')
class WebhookClient(ResourceClient):
    """Sub-client for managing a specific webhook.

    Provides methods to manage a specific webhook, e.g. get, update, or delete it. Obtain an instance via an
    appropriate method on the `ApifyClient` class.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'webhooks')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> Webhook | None:
        """Retrieve the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/get-webhook

        Returns:
            The retrieved webhook, or None if it does not exist.
        """
        result = self._get()
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

        Returns:
            The updated webhook.
        """
        webhook_representation = get_webhook_repr(
            event_types=event_types,
            request_url=request_url,
            payload_template=payload_template,
            headers_template=headers_template,
            actor_id=actor_id,
            actor_task_id=actor_task_id,
            actor_run_id=actor_run_id,
            ignore_ssl_errors=ignore_ssl_errors,
            do_not_retry=do_not_retry,
            is_ad_hoc=is_ad_hoc,
        )
        cleaned = filter_none_values(webhook_representation, remove_empty_dicts=True)

        result = self._update(cleaned)
        return WebhookResponse.model_validate(result).data

    def delete(self) -> None:
        """Delete the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/delete-webhook
        """
        self._delete()

    def test(self) -> WebhookDispatch | None:
        """Test a webhook.

        Creates a webhook dispatch with a dummy payload.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-test/test-webhook

        Returns:
            The webhook dispatch created by the test.
        """
        try:
            response = self._http_client.call(
                url=self._build_url('test'),
                method='POST',
                params=self._build_params(),
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

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'webhooks')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self) -> Webhook | None:
        """Retrieve the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/get-webhook

        Returns:
            The retrieved webhook, or None if it does not exist.
        """
        result = await self._get()
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

        Returns:
            The updated webhook.
        """
        webhook_representation = get_webhook_repr(
            event_types=event_types,
            request_url=request_url,
            payload_template=payload_template,
            headers_template=headers_template,
            actor_id=actor_id,
            actor_task_id=actor_task_id,
            actor_run_id=actor_run_id,
            ignore_ssl_errors=ignore_ssl_errors,
            do_not_retry=do_not_retry,
            is_ad_hoc=is_ad_hoc,
        )
        cleaned = filter_none_values(webhook_representation, remove_empty_dicts=True)

        result = await self._update(cleaned)
        return WebhookResponse.model_validate(result).data

    async def delete(self) -> None:
        """Delete the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/delete-webhook
        """
        await self._delete()

    async def test(self) -> WebhookDispatch | None:
        """Test a webhook.

        Creates a webhook dispatch with a dummy payload.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-test/test-webhook

        Returns:
            The webhook dispatch created by the test.
        """
        try:
            response = await self._http_client.call(
                url=self._build_url('test'),
                method='POST',
                params=self._build_params(),
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

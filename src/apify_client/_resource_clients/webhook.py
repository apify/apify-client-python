from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._models import (
    GetWebhookResponse,
    TestWebhookResponse,
    UpdateWebhookResponse,
    Webhook,
    WebhookDispatch,
)
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._resource_clients.webhook_dispatch_collection import (
    WebhookDispatchCollectionClient,
    WebhookDispatchCollectionClientAsync,
)
from apify_client._utils import (
    catch_not_found_or_throw,
    enum_to_value,
    filter_none_values,
    response_to_dict,
)
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from apify_client._consts import WebhookEventType


def get_webhook_representation(
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
    idempotency_key: str | None = None,
    is_ad_hoc: bool | None = None,
) -> dict:
    """Prepare webhook dictionary representation for clients."""
    webhook: dict = {
        'requestUrl': request_url,
        'payloadTemplate': payload_template,
        'headersTemplate': headers_template,
        'ignoreSslErrors': ignore_ssl_errors,
        'doNotRetry': do_not_retry,
        'idempotencyKey': idempotency_key,
        'isAdHoc': is_ad_hoc,
        'condition': {
            'actorRunId': actor_run_id,
            'actorTaskId': actor_task_id,
            'actorId': actor_id,
        },
    }

    if actor_run_id is not None:
        webhook['isAdHoc'] = True

    if event_types is not None:
        webhook['eventTypes'] = [enum_to_value(event_type) for event_type in event_types]

    return webhook


class WebhookClient(ResourceClient):
    """Sub-client for manipulating a single webhook."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'webhooks')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> Webhook | None:
        """Retrieve the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/get-webhook

        Returns:
            The retrieved webhook, or None if it does not exist.
        """
        try:
            response = self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(),
            )
            result = response_to_dict(response)
            return GetWebhookResponse.model_validate(result).data
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            return None

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
            is_ad_hoc=is_ad_hoc,
        )
        cleaned = filter_none_values(webhook_representation)

        response = self._http_client.call(
            url=self._build_url(),
            method='PUT',
            params=self._build_params(),
            json=cleaned,
        )
        result = response_to_dict(response)
        return UpdateWebhookResponse.model_validate(result).data

    def delete(self) -> None:
        """Delete the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/delete-webhook
        """
        try:
            self._http_client.call(
                url=self._build_url(),
                method='DELETE',
                params=self._build_params(),
            )
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

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

            result = response.json()
            return TestWebhookResponse.model_validate(result).data if result is not None else None

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    def dispatches(self) -> WebhookDispatchCollectionClient:
        """Get dispatches of the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/dispatches-collection/get-collection

        Returns:
            A client allowing access to dispatches of this webhook using its list method.
        """
        return WebhookDispatchCollectionClient(
            **self._nested_client_config(resource_path='dispatches'),
        )


class WebhookClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single webhook."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'webhooks')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self) -> Webhook | None:
        """Retrieve the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/get-webhook

        Returns:
            The retrieved webhook, or None if it does not exist.
        """
        try:
            response = await self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(),
            )
            result = response_to_dict(response)
            return GetWebhookResponse.model_validate(result).data
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            return None

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
            is_ad_hoc=is_ad_hoc,
        )
        cleaned = filter_none_values(webhook_representation)

        response = await self._http_client.call(
            url=self._build_url(),
            method='PUT',
            params=self._build_params(),
            json=cleaned,
        )
        result = response_to_dict(response)
        return UpdateWebhookResponse.model_validate(result).data

    async def delete(self) -> None:
        """Delete the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/delete-webhook
        """
        try:
            await self._http_client.call(
                url=self._build_url(),
                method='DELETE',
                params=self._build_params(),
            )
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

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

            result = response.json()
            return TestWebhookResponse.model_validate(result).data if result is not None else None

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    def dispatches(self) -> WebhookDispatchCollectionClientAsync:
        """Get dispatches of the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/dispatches-collection/get-collection

        Returns:
            A client allowing access to dispatches of this webhook using its list method.
        """
        return WebhookDispatchCollectionClientAsync(
            **self._nested_client_config(resource_path='dispatches'),
        )

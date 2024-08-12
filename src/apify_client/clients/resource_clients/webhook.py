from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_shared.utils import (
    filter_out_none_values_recursively,
    ignore_docs,
    maybe_extract_enum_member_value,
    parse_date_fields,
)

from apify_client._errors import ApifyApiError
from apify_client._utils import catch_not_found_or_throw, pluck_data
from apify_client.clients.base import ResourceClient, ResourceClientAsync
from apify_client.clients.resource_clients.webhook_dispatch_collection import WebhookDispatchCollectionClient, WebhookDispatchCollectionClientAsync

if TYPE_CHECKING:
    from apify_shared.consts import WebhookEventType


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
        webhook['eventTypes'] = [maybe_extract_enum_member_value(event_type) for event_type in event_types]

    return webhook


class WebhookClient(ResourceClient):
    """Sub-client for manipulating a single webhook."""

    @ignore_docs
    def __init__(self: WebhookClient, *args: Any, **kwargs: Any) -> None:
        """Initialize the WebhookClient."""
        resource_path = kwargs.pop('resource_path', 'webhooks')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self: WebhookClient) -> dict | None:
        """Retrieve the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/get-webhook

        Returns:
            dict, optional: The retrieved webhook, or None if it does not exist
        """
        return self._get()

    def update(
        self: WebhookClient,
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
    ) -> dict:
        """Update the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/update-webhook

        Args:
            event_types (list of WebhookEventType, optional): List of event types that should trigger the webhook. At least one is required.
            request_url (str, optional): URL that will be invoked once the webhook is triggered.
            payload_template (str, optional): Specification of the payload that will be sent to request_url
            headers_template (str, optional): Headers that will be sent to the request_url
            actor_id (str, optional): Id of the Actor whose runs should trigger the webhook.
            actor_task_id (str, optional): Id of the Actor task whose runs should trigger the webhook.
            actor_run_id (str, optional): Id of the Actor run which should trigger the webhook.
            ignore_ssl_errors (bool, optional): Whether the webhook should ignore SSL errors returned by request_url
            do_not_retry (bool, optional): Whether the webhook should retry sending the payload to request_url upon
                                           failure.
            is_ad_hoc (bool, optional): Set to True if you want the webhook to be triggered only the first time the
                                        condition is fulfilled. Only applicable when actor_run_id is filled.

        Returns:
            dict: The updated webhook
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

        return self._update(filter_out_none_values_recursively(webhook_representation))

    def delete(self: WebhookClient) -> None:
        """Delete the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/delete-webhook
        """
        return self._delete()

    def test(self: WebhookClient) -> dict | None:
        """Test a webhook.

        Creates a webhook dispatch with a dummy payload.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-test/test-webhook

        Returns:
            dict, optional: The webhook dispatch created by the test
        """
        try:
            response = self.http_client.call(
                url=self._url('test'),
                method='POST',
                params=self._params(),
            )

            return parse_date_fields(pluck_data(response.json()))

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    def dispatches(self: WebhookClient) -> WebhookDispatchCollectionClient:
        """Get dispatches of the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/dispatches-collection/get-collection

        Returns:
            WebhookDispatchCollectionClient: A client allowing access to dispatches of this webhook using its list method
        """
        return WebhookDispatchCollectionClient(
            **self._sub_resource_init_options(resource_path='dispatches'),
        )


class WebhookClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single webhook."""

    @ignore_docs
    def __init__(self: WebhookClientAsync, *args: Any, **kwargs: Any) -> None:
        """Initialize the WebhookClientAsync."""
        resource_path = kwargs.pop('resource_path', 'webhooks')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self: WebhookClientAsync) -> dict | None:
        """Retrieve the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/get-webhook

        Returns:
            dict, optional: The retrieved webhook, or None if it does not exist
        """
        return await self._get()

    async def update(
        self: WebhookClientAsync,
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
    ) -> dict:
        """Update the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/update-webhook

        Args:
            event_types (list of WebhookEventType, optional): List of event types that should trigger the webhook. At least one is required.
            request_url (str, optional): URL that will be invoked once the webhook is triggered.
            payload_template (str, optional): Specification of the payload that will be sent to request_url
            headers_template (str, optional): Headers that will be sent to the request_url
            actor_id (str, optional): Id of the Actor whose runs should trigger the webhook.
            actor_task_id (str, optional): Id of the Actor task whose runs should trigger the webhook.
            actor_run_id (str, optional): Id of the Actor run which should trigger the webhook.
            ignore_ssl_errors (bool, optional): Whether the webhook should ignore SSL errors returned by request_url
            do_not_retry (bool, optional): Whether the webhook should retry sending the payload to request_url upon
                                           failure.
            is_ad_hoc (bool, optional): Set to True if you want the webhook to be triggered only the first time the
                                        condition is fulfilled. Only applicable when actor_run_id is filled.

        Returns:
            dict: The updated webhook
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

        return await self._update(filter_out_none_values_recursively(webhook_representation))

    async def delete(self: WebhookClientAsync) -> None:
        """Delete the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/delete-webhook
        """
        return await self._delete()

    async def test(self: WebhookClientAsync) -> dict | None:
        """Test a webhook.

        Creates a webhook dispatch with a dummy payload.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-test/test-webhook

        Returns:
            dict, optional: The webhook dispatch created by the test
        """
        try:
            response = await self.http_client.call(
                url=self._url('test'),
                method='POST',
                params=self._params(),
            )

            return parse_date_fields(pluck_data(response.json()))

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    def dispatches(self: WebhookClientAsync) -> WebhookDispatchCollectionClientAsync:
        """Get dispatches of the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/dispatches-collection/get-collection

        Returns:
            WebhookDispatchCollectionClientAsync: A client allowing access to dispatches of this webhook using its list method
        """
        return WebhookDispatchCollectionClientAsync(
            **self._sub_resource_init_options(resource_path='dispatches'),
        )

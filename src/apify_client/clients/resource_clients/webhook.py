from typing import Any, Dict, List, Optional

from ..._errors import ApifyApiError
from ..._utils import (
    _catch_not_found_or_throw,
    _filter_out_none_values_recursively,
    _maybe_extract_enum_member_value,
    _parse_date_fields,
    _pluck_data,
    ignore_docs,
)
from ...consts import WebhookEventType
from ..base import ResourceClient, ResourceClientAsync
from .webhook_dispatch_collection import WebhookDispatchCollectionClient, WebhookDispatchCollectionClientAsync


def _get_webhook_representation(
    *,
    event_types: Optional[List[WebhookEventType]] = None,
    request_url: Optional[str] = None,
    payload_template: Optional[str] = None,
    actor_id: Optional[str] = None,
    actor_task_id: Optional[str] = None,
    actor_run_id: Optional[str] = None,
    ignore_ssl_errors: Optional[bool] = None,
    do_not_retry: Optional[bool] = None,
    idempotency_key: Optional[str] = None,
    is_ad_hoc: Optional[bool] = None,
) -> Dict:
    """Prepare webhook dictionary representation for clients."""
    webhook: Dict[str, Any] = {
        'requestUrl': request_url,
        'payloadTemplate': payload_template,
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
        webhook['eventTypes'] = [_maybe_extract_enum_member_value(event_type) for event_type in event_types]

    return webhook


class WebhookClient(ResourceClient):
    """Sub-client for manipulating a single webhook."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the WebhookClient."""
        resource_path = kwargs.pop('resource_path', 'webhooks')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> Optional[Dict]:
        """Retrieve the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/get-webhook

        Returns:
            dict, optional: The retrieved webhook, or None if it does not exist
        """
        return self._get()

    def update(
        self,
        *,
        event_types: Optional[List[WebhookEventType]] = None,
        request_url: Optional[str] = None,
        payload_template: Optional[str] = None,
        actor_id: Optional[str] = None,
        actor_task_id: Optional[str] = None,
        actor_run_id: Optional[str] = None,
        ignore_ssl_errors: Optional[bool] = None,
        do_not_retry: Optional[bool] = None,
        is_ad_hoc: Optional[bool] = None,
    ) -> Dict:
        """Update the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/update-webhook

        Args:
            event_types (list of WebhookEventType, optional): List of event types that should trigger the webhook. At least one is required.
            request_url (str, optional): URL that will be invoked once the webhook is triggered.
            payload_template (str, optional): Specification of the payload that will be sent to request_url
            actor_id (str, optional): Id of the actor whose runs should trigger the webhook.
            actor_task_id (str, optional): Id of the actor task whose runs should trigger the webhook.
            actor_run_id (str, optional): Id of the actor run which should trigger the webhook.
            ignore_ssl_errors (bool, optional): Whether the webhook should ignore SSL errors returned by request_url
            do_not_retry (bool, optional): Whether the webhook should retry sending the payload to request_url upon
                                           failure.
            is_ad_hoc (bool, optional): Set to True if you want the webhook to be triggered only the first time the
                                        condition is fulfilled. Only applicable when actor_run_id is filled.

        Returns:
            dict: The updated webhook
        """
        webhook_representation = _get_webhook_representation(
            event_types=event_types,
            request_url=request_url,
            payload_template=payload_template,
            actor_id=actor_id,
            actor_task_id=actor_task_id,
            actor_run_id=actor_run_id,
            ignore_ssl_errors=ignore_ssl_errors,
            do_not_retry=do_not_retry,
            is_ad_hoc=is_ad_hoc,
        )

        return self._update(_filter_out_none_values_recursively(webhook_representation))

    def delete(self) -> None:
        """Delete the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/delete-webhook
        """
        return self._delete()

    def test(self) -> Optional[Dict]:
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

            return _parse_date_fields(_pluck_data(response.json()))

        except ApifyApiError as exc:
            _catch_not_found_or_throw(exc)

        return None

    def dispatches(self) -> WebhookDispatchCollectionClient:
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
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the WebhookClientAsync."""
        resource_path = kwargs.pop('resource_path', 'webhooks')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self) -> Optional[Dict]:
        """Retrieve the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/get-webhook

        Returns:
            dict, optional: The retrieved webhook, or None if it does not exist
        """
        return await self._get()

    async def update(
        self,
        *,
        event_types: Optional[List[WebhookEventType]] = None,
        request_url: Optional[str] = None,
        payload_template: Optional[str] = None,
        actor_id: Optional[str] = None,
        actor_task_id: Optional[str] = None,
        actor_run_id: Optional[str] = None,
        ignore_ssl_errors: Optional[bool] = None,
        do_not_retry: Optional[bool] = None,
        is_ad_hoc: Optional[bool] = None,
    ) -> Dict:
        """Update the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/update-webhook

        Args:
            event_types (list of WebhookEventType, optional): List of event types that should trigger the webhook. At least one is required.
            request_url (str, optional): URL that will be invoked once the webhook is triggered.
            payload_template (str, optional): Specification of the payload that will be sent to request_url
            actor_id (str, optional): Id of the actor whose runs should trigger the webhook.
            actor_task_id (str, optional): Id of the actor task whose runs should trigger the webhook.
            actor_run_id (str, optional): Id of the actor run which should trigger the webhook.
            ignore_ssl_errors (bool, optional): Whether the webhook should ignore SSL errors returned by request_url
            do_not_retry (bool, optional): Whether the webhook should retry sending the payload to request_url upon
                                           failure.
            is_ad_hoc (bool, optional): Set to True if you want the webhook to be triggered only the first time the
                                        condition is fulfilled. Only applicable when actor_run_id is filled.

        Returns:
            dict: The updated webhook
        """
        webhook_representation = _get_webhook_representation(
            event_types=event_types,
            request_url=request_url,
            payload_template=payload_template,
            actor_id=actor_id,
            actor_task_id=actor_task_id,
            actor_run_id=actor_run_id,
            ignore_ssl_errors=ignore_ssl_errors,
            do_not_retry=do_not_retry,
            is_ad_hoc=is_ad_hoc,
        )

        return await self._update(_filter_out_none_values_recursively(webhook_representation))

    async def delete(self) -> None:
        """Delete the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/delete-webhook
        """
        return await self._delete()

    async def test(self) -> Optional[Dict]:
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

            return _parse_date_fields(_pluck_data(response.json()))

        except ApifyApiError as exc:
            _catch_not_found_or_throw(exc)

        return None

    def dispatches(self) -> WebhookDispatchCollectionClientAsync:
        """Get dispatches of the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/dispatches-collection/get-collection

        Returns:
            WebhookDispatchCollectionClientAsync: A client allowing access to dispatches of this webhook using its list method
        """
        return WebhookDispatchCollectionClientAsync(
            **self._sub_resource_init_options(resource_path='dispatches'),
        )

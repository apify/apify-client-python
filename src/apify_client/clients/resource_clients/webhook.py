from typing import Any, Dict, List, Optional

from ..._errors import ApifyApiError
from ..._utils import _catch_not_found_or_throw, _maybe_extract_enum_member_value, _parse_date_fields, _pluck_data, _snake_case_to_camel_case
from ...consts import WebhookEventType
from ..base import ResourceClient
from .webhook_dispatch_collection import WebhookDispatchCollectionClient


def _prepare_webhook_representation(
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
        _snake_case_to_camel_case(key): value
        for key, value in locals().items() if value is not None and key not in ['event_types', 'actor_run_id', 'actor_task_id', 'actor_id']
    }

    condition = {}

    if actor_run_id is not None:
        condition['actorRunId'] = actor_run_id
        webhook['isAdHoc'] = True
    elif actor_task_id is not None:
        condition['actorTaskId'] = actor_task_id
    elif actor_id is not None:
        condition['actorId'] = actor_id

    if condition != {}:
        webhook['condition'] = condition

    if event_types is not None:
        webhook['eventTypes'] = [_maybe_extract_enum_member_value(event_type) for event_type in event_types]

    return webhook


class WebhookClient(ResourceClient):
    """Sub-client for manipulating a single webhook."""

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
        parameters = locals()
        parameters.pop('self')
        webhook = _prepare_webhook_representation(**parameters)
        return self._update(webhook)

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

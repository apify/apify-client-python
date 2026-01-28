from apify_client._consts import WebhookEventType
from apify_client._utils import encode_webhook_list_to_base64, to_safe_id


def test__to_safe_id() -> None:
    assert to_safe_id('abc') == 'abc'
    assert to_safe_id('abc/def') == 'abc~def'
    assert to_safe_id('abc~def') == 'abc~def'


def test__encode_webhook_list_to_base64() -> None:
    assert encode_webhook_list_to_base64([]) == 'W10='
    assert (
        encode_webhook_list_to_base64(
            [
                {
                    'event_types': [WebhookEventType.ACTOR_RUN_CREATED],
                    'request_url': 'https://example.com/run-created',
                },
                {
                    'event_types': [WebhookEventType.ACTOR_RUN_SUCCEEDED],
                    'request_url': 'https://example.com/run-succeeded',
                    'payload_template': '{"hello": "world", "resource":{{resource}}}',
                },
            ]
        )
        == 'W3siZXZlbnRUeXBlcyI6IFsiQUNUT1IuUlVOLkNSRUFURUQiXSwgInJlcXVlc3RVcmwiOiAiaHR0cHM6Ly9leGFtcGxlLmNvbS9ydW4tY3JlYXRlZCJ9LCB7ImV2ZW50VHlwZXMiOiBbIkFDVE9SLlJVTi5TVUNDRUVERUQiXSwgInJlcXVlc3RVcmwiOiAiaHR0cHM6Ly9leGFtcGxlLmNvbS9ydW4tc3VjY2VlZGVkIiwgInBheWxvYWRUZW1wbGF0ZSI6ICJ7XCJoZWxsb1wiOiBcIndvcmxkXCIsIFwicmVzb3VyY2VcIjp7e3Jlc291cmNlfX19In1d'  # noqa: E501
    )

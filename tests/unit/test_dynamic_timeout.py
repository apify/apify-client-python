from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import respx
from httpx import Request, Response

from apify_client import ApifyClient, ApifyClientAsync

if TYPE_CHECKING:
    from apify_client._dynamic_timeout import DynamicTimeoutFunction, RequestContent


@pytest.fixture
def get_dynamic_timeout_function() -> DynamicTimeoutFunction:
    """Example of a dynamic timeout function."""

    def get_dynamic_timeout(method: str, url: str, content: RequestContent) -> int | None:
        """Return suitable timeout.

        For POST on endpoint v2/datasets/whatever/items timeout is proportional to the size of the content.
        For everything else return fixed 30."""
        if isinstance(content, bytes) and method == 'POST' and url.endswith('v2/datasets/whatever/items'):
            dynamic_timeout_based_on_size = int(len(content) / 10)
            return min(360, max(5, dynamic_timeout_based_on_size))  # Saturate in range 5-360 seconds
        return 30

    return get_dynamic_timeout


@respx.mock
@pytest.mark.parametrize(
    ('content', 'expected_timeout'),
    [
        pytest.param('abcd', 5, id='Small payload'),
        pytest.param('abcd' * 10000, 9, id='Payload in the dynamic timeout interval interval'),
        pytest.param('abcd' * 1000000, 360, id='Large payload'),
    ],
)
async def test_dynamic_timeout_async_client(
    get_dynamic_timeout_function: DynamicTimeoutFunction, content: str, expected_timeout: int
) -> None:
    def check_timeout(request: Request) -> Response:
        assert request.extensions['timeout'] == {
            'connect': expected_timeout,
            'pool': expected_timeout,
            'read': expected_timeout,
            'write': expected_timeout,
        }
        return Response(201)

    respx.post('https://api.apify.com/v2/datasets/whatever/items').mock(side_effect=check_timeout)
    client = ApifyClientAsync(get_dynamic_timeout=get_dynamic_timeout_function)
    await client.dataset(dataset_id='whatever').push_items({'some_key': content})


@respx.mock
async def test_dynamic_timeout_async_client_default() -> None:
    expected_timeout = 360

    def check_timeout(request: Request) -> Response:
        assert request.extensions['timeout'] == {
            'connect': expected_timeout,
            'pool': expected_timeout,
            'read': expected_timeout,
            'write': expected_timeout,
        }
        return Response(201)

    respx.post('https://api.apify.com/v2/datasets/whatever/items').mock(side_effect=check_timeout)
    client = ApifyClientAsync()
    await client.dataset(dataset_id='whatever').push_items({'some_key': 'abcd'})


@respx.mock
@pytest.mark.parametrize(
    ('content', 'expected_timeout'),
    [
        pytest.param('abcd', 5, id='Small payload'),
        pytest.param('abcd' * 10000, 9, id='Payload in the dynamic timeout interval interval'),
        pytest.param('abcd' * 1000000, 360, id='Large payload'),
    ],
)
def test_dynamic_timeout_sync_client(
    get_dynamic_timeout_function: DynamicTimeoutFunction, content: str, expected_timeout: int
) -> None:
    def check_timeout(request: Request) -> Response:
        assert request.extensions['timeout'] == {
            'connect': expected_timeout,
            'pool': expected_timeout,
            'read': expected_timeout,
            'write': expected_timeout,
        }
        return Response(201)

    respx.post('https://api.apify.com/v2/datasets/whatever/items').mock(side_effect=check_timeout)
    client = ApifyClient(get_dynamic_timeout=get_dynamic_timeout_function)
    client.dataset(dataset_id='whatever').push_items({'some_key': content})


@respx.mock
def test_dynamic_timeout_sync_client_default() -> None:
    expected_timeout = 360

    def check_timeout(request: Request) -> Response:
        assert request.extensions['timeout'] == {
            'connect': expected_timeout,
            'pool': expected_timeout,
            'read': expected_timeout,
            'write': expected_timeout,
        }
        return Response(201)

    respx.post('https://api.apify.com/v2/datasets/whatever/items').mock(side_effect=check_timeout)
    client = ApifyClient()
    client.dataset(dataset_id='whatever').push_items({'some_key': 'abcd'})

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, Mock

import impit
import pytest

from apify_client.http_clients import ImpitHttpClient, ImpitHttpClientAsync

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


def successful_response() -> Mock:
    return Mock(status_code=200)


def test_generic_http_error_is_retried(monkeypatch: MonkeyPatch) -> None:
    """A bare Impit HTTPError from a truncated body remains retryable (regression coverage)."""
    client = ImpitHttpClient(min_delay_between_retries=timedelta(0))
    send_request = Mock(
        side_effect=[impit.HTTPError('unexpected EOF'), impit.HTTPError('unexpected EOF'), successful_response()]
    )
    monkeypatch.setattr(client, 'send_request', send_request)

    response = client.call(method='GET', url='https://example.com')

    assert response.status_code == 200
    assert send_request.call_count == 3


async def test_generic_http_error_is_retried_async(monkeypatch: MonkeyPatch) -> None:
    """The async Impit adapter retains the same generic HTTPError retry regression coverage."""
    client = ImpitHttpClientAsync(min_delay_between_retries=timedelta(0))
    send_request = AsyncMock(
        side_effect=[impit.HTTPError('unexpected EOF'), impit.HTTPError('unexpected EOF'), successful_response()]
    )
    monkeypatch.setattr(client, 'send_request', send_request)

    response = await client.call(method='GET', url='https://example.com')

    assert response.status_code == 200
    assert send_request.call_count == 3


def test_permanent_transport_error_is_not_retried(monkeypatch: MonkeyPatch) -> None:
    """A transport error a retry cannot fix must fail on the first attempt instead of burning the whole backoff."""
    client = ImpitHttpClient(min_delay_between_retries=timedelta(0))
    send_request = Mock(side_effect=impit.UnsupportedProtocol('unsupported scheme'))
    monkeypatch.setattr(client, 'send_request', send_request)

    with pytest.raises(impit.UnsupportedProtocol):
        client.call(method='GET', url='https://example.com')

    assert send_request.call_count == 1


def test_error_response_read_failure_uses_transport_retry_policy(monkeypatch: MonkeyPatch) -> None:
    """Failures while reading a streamed 5xx error body are classified and retried like send failures."""
    client = ImpitHttpClient(max_retries=1, min_delay_between_retries=timedelta(0))
    responses = [Mock(status_code=500, read=Mock(side_effect=impit.ReadError('truncated'))) for _ in range(2)]
    send_request = Mock(side_effect=responses)
    monkeypatch.setattr(client, 'send_request', send_request)

    with pytest.raises(impit.ReadError):
        client.call(method='GET', url='https://example.com', stream=True)

    assert send_request.call_count == 2


async def test_error_response_read_failure_uses_transport_retry_policy_async(monkeypatch: MonkeyPatch) -> None:
    """The async base also classifies failures while buffering streamed error responses."""
    client = ImpitHttpClientAsync(max_retries=1, min_delay_between_retries=timedelta(0))
    responses = [Mock(status_code=500, aread=AsyncMock(side_effect=impit.ReadError('truncated'))) for _ in range(2)]
    send_request = AsyncMock(side_effect=responses)
    monkeypatch.setattr(client, 'send_request', send_request)

    with pytest.raises(impit.ReadError):
        await client.call(method='GET', url='https://example.com', stream=True)

    assert send_request.call_count == 2

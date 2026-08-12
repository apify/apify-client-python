from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, Mock

import impit
import pytest

from apify_client._logging import LoggerOnce, logger_name
from apify_client.http_clients import HttpClient, HttpClientAsync, ImpitHttpClient, ImpitHttpClientAsync
from apify_client.http_clients import _base as http_client_base

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture


@pytest.fixture
def fresh_logger_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace the module-level `LoggerOnce`, whose dedup state would otherwise leak between tests."""
    monkeypatch.setattr(http_client_base, 'logger_once', LoggerOnce(http_client_base.logger))


def successful_response() -> Mock:
    return Mock(status_code=200)


@pytest.mark.parametrize(
    ('timeout', 'expected'),
    [
        pytest.param('no_timeout', None, id='no-timeout'),
        pytest.param(None, 30.0, id='default-medium'),
        pytest.param('short', 5.0, id='short'),
        pytest.param('medium', 30.0, id='medium'),
        pytest.param('long', 300.0, id='long'),
    ],
)
def test_timeout_resolves_for_sync_clients(
    http_client_class: type[HttpClient],
    monkeypatch: pytest.MonkeyPatch,
    timeout: str | None,
    expected: float | None,
) -> None:
    """Every synchronous client resolves timeout tiers at the shared transport boundary."""
    client = http_client_class(
        timeout_short=timedelta(seconds=5),
        timeout_medium=timedelta(seconds=30),
        timeout_long=timedelta(seconds=300),
    )
    send_request = Mock(return_value=successful_response())
    monkeypatch.setattr(client, 'send_request', send_request)

    kwargs: dict[str, Any] = {'method': 'GET', 'url': 'https://example.com'}
    if timeout is not None:
        kwargs['timeout'] = timeout
    client.call(**kwargs)

    assert send_request.call_args.kwargs['timeout'] == expected


@pytest.mark.parametrize(
    ('timeout', 'expected'),
    [
        pytest.param('no_timeout', None, id='no-timeout'),
        pytest.param(None, 30.0, id='default-medium'),
        pytest.param('short', 5.0, id='short'),
        pytest.param('medium', 30.0, id='medium'),
        pytest.param('long', 300.0, id='long'),
    ],
)
async def test_timeout_resolves_for_async_clients(
    http_client_async_class: type[HttpClientAsync],
    monkeypatch: pytest.MonkeyPatch,
    timeout: str | None,
    expected: float | None,
) -> None:
    """Every asynchronous client resolves timeout tiers at the shared transport boundary."""
    client = http_client_async_class(
        timeout_short=timedelta(seconds=5),
        timeout_medium=timedelta(seconds=30),
        timeout_long=timedelta(seconds=300),
    )
    send_request = AsyncMock(return_value=successful_response())
    monkeypatch.setattr(client, 'send_request', send_request)

    kwargs: dict[str, Any] = {'method': 'GET', 'url': 'https://example.com'}
    if timeout is not None:
        kwargs['timeout'] = timeout
    await client.call(**kwargs)

    assert send_request.call_args.kwargs['timeout'] == expected


def test_compute_timeout_with_timedelta(http_client_class: type[HttpClient]) -> None:
    """Concrete timedeltas double per attempt and are capped at the configured maximum."""
    client = http_client_class(timeout_max=timedelta(seconds=20))

    assert client._compute_timeout(timedelta(seconds=5), attempt=1) == 5.0
    assert client._compute_timeout(timedelta(seconds=5), attempt=2) == 10.0
    assert client._compute_timeout(timedelta(seconds=5), attempt=3) == 20.0
    assert client._compute_timeout(timedelta(seconds=5), attempt=4) == 20.0
    assert client._compute_timeout('no_timeout', attempt=1) is None


@pytest.mark.usefixtures('fresh_logger_once')
def test_compute_timeout_explicit_timedelta_above_max_warns(
    http_client_class: type[HttpClient], caplog: LogCaptureFixture
) -> None:
    """An explicit timedelta larger than timeout_max is capped, and the cut-off is logged once."""
    client = http_client_class(timeout_max=timedelta(seconds=360))

    with caplog.at_level(logging.WARNING, logger=logger_name):
        assert client._compute_timeout(timedelta(minutes=30), attempt=1) == 360.0
        # Retries and later calls recompute the timeout, which must not repeat the warning.
        assert client._compute_timeout(timedelta(minutes=30), attempt=2) == 360.0
        assert client._compute_timeout(timedelta(minutes=45), attempt=1) == 360.0

    assert len(caplog.records) == 1
    assert '1800.0s exceeds `timeout_max` (360.0s)' in caplog.records[0].message


@pytest.mark.usefixtures('fresh_logger_once')
def test_compute_timeout_tier_above_max_warns(http_client_class: type[HttpClient], caplog: LogCaptureFixture) -> None:
    """A tier configured larger than timeout_max is capped, and the cut-off is logged too."""
    client = http_client_class(timeout_long=timedelta(seconds=600), timeout_max=timedelta(seconds=360))

    with caplog.at_level(logging.WARNING, logger=logger_name):
        assert client._compute_timeout('long', attempt=1) == 360.0

    assert len(caplog.records) == 1
    assert '600.0s exceeds `timeout_max` (360.0s)' in caplog.records[0].message


@pytest.mark.usefixtures('fresh_logger_once')
def test_compute_timeout_within_max_does_not_warn(
    http_client_class: type[HttpClient], caplog: LogCaptureFixture
) -> None:
    """A base timeout within timeout_max is used as-is, without a warning."""
    client = http_client_class(timeout_long=timedelta(seconds=300), timeout_max=timedelta(seconds=360))

    with caplog.at_level(logging.WARNING, logger=logger_name):
        assert client._compute_timeout(timedelta(seconds=120), attempt=1) == 120.0
        assert client._compute_timeout('long', attempt=1) == 300.0
        # Growth capped at `timeout_max` on a retry is expected, so it is not warned about.
        assert client._compute_timeout('long', attempt=2) == 360.0

    assert caplog.records == []


def test_dynamic_timeout_sync_client(http_client_class: type[HttpClient], monkeypatch: pytest.MonkeyPatch) -> None:
    """Synchronous clients increase timeout values after retryable transport errors."""
    client = http_client_class(
        timeout_short=timedelta(seconds=1),
        timeout_max=timedelta(seconds=5),
        min_delay_between_retries=timedelta(0),
    )
    timeouts: list[float | None] = []

    def send_request(*_args: Any, **kwargs: Any) -> Mock:
        timeouts.append(kwargs['timeout'])
        if len(timeouts) < 4:
            raise impit.TimeoutException('timeout')
        return successful_response()

    monkeypatch.setattr(client, 'send_request', send_request)

    response = client.call(method='GET', url='https://example.com', timeout=timedelta(seconds=1))

    assert timeouts == [1.0, 2.0, 4.0, 5.0]
    assert response.status_code == 200


async def test_dynamic_timeout_async_client(
    http_client_async_class: type[HttpClientAsync], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Asynchronous clients increase timeout values after retryable transport errors."""
    client = http_client_async_class(
        timeout_short=timedelta(seconds=1),
        timeout_max=timedelta(seconds=5),
        min_delay_between_retries=timedelta(0),
    )
    timeouts: list[float | None] = []

    async def send_request(*_args: Any, **kwargs: Any) -> Mock:
        timeouts.append(kwargs['timeout'])
        if len(timeouts) < 4:
            raise impit.TimeoutException('timeout')
        return successful_response()

    monkeypatch.setattr(client, 'send_request', send_request)

    response = await client.call(method='GET', url='https://example.com', timeout=timedelta(seconds=1))

    assert timeouts == [1.0, 2.0, 4.0, 5.0]
    assert response.status_code == 200


def test_no_timeout_mapping_for_sync_adapter() -> None:
    """The synchronous adapter maps no-timeout to Impit's effectively unbounded value."""
    client = ImpitHttpClient()
    client._impit_client = Mock(request=Mock(return_value=successful_response()))

    client.send_request(method='GET', url='https://example.com', headers={}, content=None, timeout=None, stream=False)

    assert client._impit_client.request.call_args.kwargs['timeout'] == 86_400


async def test_no_timeout_mapping_for_async_adapter() -> None:
    """The asynchronous adapter maps no-timeout to Impit's effectively unbounded value."""
    client = ImpitHttpClientAsync()
    client._impit_async_client = Mock(request=AsyncMock(return_value=successful_response()))

    await client.send_request(
        method='GET', url='https://example.com', headers={}, content=None, timeout=None, stream=False
    )

    assert client._impit_async_client.request.call_args.kwargs['timeout'] == 86_400

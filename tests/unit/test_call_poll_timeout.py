from __future__ import annotations

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from apify_client import ApifyClient, ApifyClientAsync
from apify_client._resource_clients import RunClient, RunClientAsync


@pytest.mark.parametrize('resource', [pytest.param('actor', id='actor'), pytest.param('task', id='task')])
def test_call_passes_timeout_to_poll_sync(monkeypatch: pytest.MonkeyPatch, resource: str) -> None:
    """Apply the per-request timeout to both the start and poll requests."""
    client = ApifyClient(token='test_token')
    sub_client = getattr(client, resource)('resource-id')
    start = Mock(return_value=Mock(id='run-id'))
    poll = Mock(return_value=Mock(id='run-id'))
    monkeypatch.setattr(sub_client, 'start', start)
    monkeypatch.setattr(RunClient, 'wait_for_finish', poll)

    timeout = timedelta(seconds=90)
    sub_client.call(timeout=timeout, wait_duration=timedelta(seconds=120), logger=None)

    assert start.call_args.kwargs['timeout'] == timeout
    poll.assert_called_once_with(wait_duration=timedelta(seconds=120), timeout=timeout)


@pytest.mark.parametrize('resource', [pytest.param('actor', id='actor'), pytest.param('task', id='task')])
async def test_call_passes_timeout_to_poll_async(monkeypatch: pytest.MonkeyPatch, resource: str) -> None:
    """Apply the per-request timeout to both async start and poll requests."""
    client = ApifyClientAsync(token='test_token')
    sub_client = getattr(client, resource)('resource-id')
    start = AsyncMock(return_value=Mock(id='run-id'))
    poll = AsyncMock(return_value=Mock(id='run-id'))
    monkeypatch.setattr(sub_client, 'start', start)
    monkeypatch.setattr(RunClientAsync, 'wait_for_finish', poll)

    timeout = timedelta(seconds=90)
    await sub_client.call(timeout=timeout, wait_duration=timedelta(seconds=120), logger=None)

    assert start.call_args.kwargs['timeout'] == timeout
    poll.assert_awaited_once_with(wait_duration=timedelta(seconds=120), timeout=timeout)


def test_actor_call_passes_timeout_to_poll_with_log_redirect(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the poll timeout when the default log redirect is active."""
    actor = ApifyClient(token='test_token').actor('actor-id')
    monkeypatch.setattr(actor, 'start', Mock(return_value=Mock(id='run-id')))
    poll = Mock()
    monkeypatch.setattr(RunClient, 'wait_for_finish', poll)
    monkeypatch.setattr(RunClient, 'get_status_message_watcher', Mock(return_value=MagicMock()))
    monkeypatch.setattr(RunClient, 'get_streamed_log', Mock(return_value=MagicMock()))

    timeout = timedelta(seconds=90)
    actor.call(timeout=timeout)

    poll.assert_called_once_with(wait_duration=None, timeout=timeout)


async def test_actor_call_passes_timeout_to_poll_with_log_redirect_async(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the async poll timeout when the default log redirect is active."""
    actor = ApifyClientAsync(token='test_token').actor('actor-id')
    monkeypatch.setattr(actor, 'start', AsyncMock(return_value=Mock(id='run-id')))
    poll = AsyncMock()
    monkeypatch.setattr(RunClientAsync, 'wait_for_finish', poll)
    monkeypatch.setattr(RunClientAsync, 'get_status_message_watcher', AsyncMock(return_value=MagicMock()))
    monkeypatch.setattr(RunClientAsync, 'get_streamed_log', AsyncMock(return_value=MagicMock()))

    timeout = timedelta(seconds=90)
    await actor.call(timeout=timeout)

    poll.assert_awaited_once_with(wait_duration=None, timeout=timeout)

"""Unified tests for log (sync + async)."""

from __future__ import annotations

import asyncio
import logging
import threading
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import TYPE_CHECKING

from .._utils import maybe_await
from apify_client._models import ListOfBuilds, Run
from apify_client._resource_clients import RunClient, RunClientAsync
from apify_client.http_clients import HttpResponse

if TYPE_CHECKING:
    import pytest
    from _pytest.logging import LogCaptureFixture

    from apify_client import ApifyClient, ApifyClientAsync
    from apify_client.types import Timeout

# Use a simple, fast public actor for testing
HELLO_WORLD_ACTOR = 'apify/hello-world'


async def test_log_get_from_run(client: ApifyClient | ApifyClientAsync) -> None:
    """Test retrieving log from an Actor run."""
    # Run hello-world actor
    actor = client.actor(HELLO_WORLD_ACTOR)
    run = await maybe_await(actor.call())
    assert isinstance(run, Run)

    # Get log as text
    run_client = client.run(run.id)
    log = await maybe_await(run_client.log().get())

    assert log is not None
    assert isinstance(log, str)
    assert len(log) > 0

    # Cleanup
    await maybe_await(run_client.delete())


async def test_log_get_from_build(client: ApifyClient | ApifyClientAsync) -> None:
    """Test retrieving log from a build."""
    # Get a build from hello-world actor
    actor = client.actor(HELLO_WORLD_ACTOR)
    builds_page = await maybe_await(actor.builds().list(limit=1))
    assert isinstance(builds_page, ListOfBuilds)
    assert builds_page.items
    build_id = builds_page.items[0].id

    # Get log from the build
    build = client.build(build_id)
    log = await maybe_await(build.log().get())

    # Build log may be None or empty for some builds
    if log is not None:
        assert isinstance(log, str)


async def test_log_get_as_bytes(client: ApifyClient | ApifyClientAsync) -> None:
    """Test retrieving log as raw bytes."""
    # Run hello-world actor
    actor = client.actor(HELLO_WORLD_ACTOR)
    run = await maybe_await(actor.call())
    assert isinstance(run, Run)

    # Get log as bytes
    run_client = client.run(run.id)
    log_bytes = await maybe_await(run_client.log().get_as_bytes())

    assert log_bytes is not None
    assert isinstance(log_bytes, bytes)
    assert len(log_bytes) > 0

    # Cleanup
    await maybe_await(run_client.delete())


async def test_log_stream_from_run(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test streaming a run's log via the stream() context manager."""
    actor = client.actor(HELLO_WORLD_ACTOR)
    run = await maybe_await(actor.call())
    assert isinstance(run, Run)

    run_client = client.run(run.id)
    try:
        log_client = run_client.log()

        stream_ctx = log_client.stream()
        if is_async:
            assert isinstance(stream_ctx, AbstractAsyncContextManager)
            async with stream_ctx as response:
                assert isinstance(response, HttpResponse)
                content = await response.aread()
                assert isinstance(content, bytes)
                assert len(content) > 0
        else:
            assert isinstance(stream_ctx, AbstractContextManager)
            with stream_ctx as response:
                assert isinstance(response, HttpResponse)
                content = response.read()
                assert isinstance(content, bytes)
                assert len(content) > 0
    finally:
        await maybe_await(run_client.delete())


async def test_actor_call_returns_run_when_status_poll_fails(
    client: ApifyClient | ApifyClientAsync,
    caplog: LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
    *,
    is_async: bool,
) -> None:
    """A failing status poll is reported to the logger and leaves `call` returning the run the platform finished."""
    logger = logging.getLogger(f'test-status-poll-failure-{"async" if is_async else "sync"}')

    # `call` polls the run status from a background task or thread and awaits the run itself on the main one, so
    # failing only the background polls leaves the rest of `call` talking to the real API.
    if is_async:
        main_task = asyncio.current_task()
        original_get_async = RunClientAsync.get

        async def failing_get_async(self: RunClientAsync, *, timeout: Timeout = 'short') -> Run | None:
            if asyncio.current_task() is main_task:
                return await original_get_async(self, timeout=timeout)
            raise RuntimeError('Simulated status poll failure')

        monkeypatch.setattr(RunClientAsync, 'get', failing_get_async)
    else:
        original_get = RunClient.get

        def failing_get(self: RunClient, *, timeout: Timeout = 'short') -> Run | None:
            if threading.current_thread() is threading.main_thread():
                return original_get(self, timeout=timeout)
            raise RuntimeError('Simulated status poll failure')

        monkeypatch.setattr(RunClient, 'get', failing_get)

    with caplog.at_level(logging.DEBUG, logger=logger.name):
        run = await maybe_await(client.actor(HELLO_WORLD_ACTOR).call(logger=logger))

    assert isinstance(run, Run)
    try:
        assert run.status == 'SUCCEEDED'
        assert any(
            record.levelno == logging.ERROR
            and record.message == 'Status message redirection stopped due to unexpected error:'
            for record in caplog.records
        )
    finally:
        await maybe_await(client.run(run.id).delete())

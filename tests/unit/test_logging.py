import asyncio
import json
import logging
import threading
import time
from collections.abc import AsyncIterator, Generator, Iterator
from datetime import datetime, timedelta
from unittest.mock import patch

import httpx
import pytest
import respx
from _pytest.logging import LogCaptureFixture
from apify_shared.consts import ActorJobStatus

from apify_client import ApifyClient, ApifyClientAsync
from apify_client._logging import RedirectLogFormatter
from apify_client.clients.resource_clients.log import StatusMessageWatcher, StreamedLog

_MOCKED_API_URL = 'https://example.com'
_MOCKED_RUN_ID = 'mocked_run_id'
_MOCKED_ACTOR_NAME = 'mocked_actor_name'
_MOCKED_ACTOR_ID = 'mocked_actor_id'
_MOCKED_ACTOR_LOGS = (
    b'2025-05-13T07:24:12.588Z ACTOR: Pulling Docker image of build.\n'
    b'2025-05-13T07:24:12.686Z ACTOR: Creating Docker container.\n'
    b'2025-05-13T07:24:12.745Z ACTOR: Starting Docker container.\n',  # Several logs merged into one chunk
    b'2025-05-13T07:26:14.132Z [apify] DEBUG \xc3',  # Chunked log split in the middle of the multibyte character
    b'\xa1\n',  # part 2
    b'2025-05-13T07:24:14.132Z [apify] INFO multiline \n log\n',
    b'2025-05-13T07:25:14.132Z [apify] WARNING some warning\n',
    b'2025-05-13T07:26:14.132Z [apify] DEBUG c\n',
    b'2025-05-13T0',  # Chunked log that got split in the marker
    b'7:26:14.132Z [apify] DEBUG d\n'  # part 2
    b'2025-05-13T07:27:14.132Z [apify] DEB',  # Chunked log that got split outside of marker
    b'UG e\n',  # part 2
    # Already redirected message
    b'2025-05-13T07:28:14.132Z [apify.redirect-logger runId:4U1oAnKau6jpzjUuA] -> 2025-05-13T07:27:14.132Z ACTOR:...\n',
)
_EXISTING_LOGS_BEFORE_REDIRECT_ATTACH = 3

_EXPECTED_MESSAGES_AND_LEVELS = (
    ('2025-05-13T07:24:12.588Z ACTOR: Pulling Docker image of build.', logging.INFO),
    ('2025-05-13T07:24:12.686Z ACTOR: Creating Docker container.', logging.INFO),
    ('2025-05-13T07:24:12.745Z ACTOR: Starting Docker container.', logging.INFO),
    ('2025-05-13T07:26:14.132Z [apify] DEBUG á', logging.DEBUG),
    ('2025-05-13T07:24:14.132Z [apify] INFO multiline \n log', logging.INFO),
    ('2025-05-13T07:25:14.132Z [apify] WARNING some warning', logging.WARNING),
    ('2025-05-13T07:26:14.132Z [apify] DEBUG c', logging.DEBUG),
    ('2025-05-13T07:26:14.132Z [apify] DEBUG d', logging.DEBUG),
    ('2025-05-13T07:27:14.132Z [apify] DEBUG e', logging.DEBUG),
    (
        '2025-05-13T07:28:14.132Z [apify.redirect-logger runId:4U1oAnKau6jpzjUuA] -> '
        '2025-05-13T07:27:14.132Z ACTOR:...',
        logging.INFO,
    ),
)

_EXPECTED_MESSAGES_AND_LEVELS_WITH_STATUS_MESSAGES = (
    ('Status: RUNNING, Message: Initial message', logging.INFO),
    *_EXPECTED_MESSAGES_AND_LEVELS,
    ('Status: RUNNING, Message: Another message', logging.INFO),
    ('Status: SUCCEEDED, Message: Final message', logging.INFO),
)


@pytest.fixture
def mock_api() -> None:
    test_server_lock = threading.Lock()

    def get_responses() -> Generator[httpx.Response, None, None]:
        """Simulate actor run that changes status 3 times."""
        for _ in range(5):
            yield httpx.Response(
                content=json.dumps(
                    {
                        'data': {
                            'id': _MOCKED_RUN_ID,
                            'actId': _MOCKED_ACTOR_ID,
                            'status': ActorJobStatus.RUNNING,
                            'statusMessage': 'Initial message',
                            'isStatusMessageTerminal': False,
                        }
                    }
                ),
                status_code=200,
            )
        for _ in range(5):
            yield httpx.Response(
                content=json.dumps(
                    {
                        'data': {
                            'id': _MOCKED_RUN_ID,
                            'actId': _MOCKED_ACTOR_ID,
                            'status': ActorJobStatus.RUNNING,
                            'statusMessage': 'Another message',
                            'isStatusMessageTerminal': False,
                        }
                    }
                ),
                status_code=200,
            )
        while True:
            yield httpx.Response(
                content=json.dumps(
                    {
                        'data': {
                            'id': _MOCKED_RUN_ID,
                            'actId': _MOCKED_ACTOR_ID,
                            'status': ActorJobStatus.SUCCEEDED,
                            'statusMessage': 'Final message',
                            'isStatusMessageTerminal': True,
                        }
                    }
                ),
                status_code=200,
            )

    responses = get_responses()

    def actor_runs_side_effect(_: httpx.Request) -> httpx.Response:
        test_server_lock.acquire()
        # To avoid multiple threads accessing at the same time and causing `ValueError: generator already executing`
        response = next(responses)
        test_server_lock.release_lock()
        return response

    respx.get(url=f'{_MOCKED_API_URL}/v2/actor-runs/{_MOCKED_RUN_ID}').mock(side_effect=actor_runs_side_effect)

    respx.get(url=f'{_MOCKED_API_URL}/v2/acts/{_MOCKED_ACTOR_ID}').mock(
        return_value=httpx.Response(content=json.dumps({'data': {'name': _MOCKED_ACTOR_NAME}}), status_code=200)
    )

    respx.post(url=f'{_MOCKED_API_URL}/v2/acts/{_MOCKED_ACTOR_ID}/runs').mock(
        return_value=httpx.Response(content=json.dumps({'data': {'id': _MOCKED_RUN_ID}}), status_code=200)
    )


@pytest.fixture
def mock_api_async(mock_api: None) -> None:  # noqa: ARG001, fixture
    class AsyncByteStream(httpx._types.AsyncByteStream):
        async def __aiter__(self) -> AsyncIterator[bytes]:
            for i in _MOCKED_ACTOR_LOGS:
                yield i
                await asyncio.sleep(0.01)

        async def aclose(self) -> None:
            pass

    respx.get(url=f'{_MOCKED_API_URL}/v2/actor-runs/{_MOCKED_RUN_ID}/log?stream=1&raw=1').mock(
        return_value=httpx.Response(stream=AsyncByteStream(), status_code=200)
    )


@pytest.fixture
def mock_api_sync(mock_api: None) -> None:  # noqa: ARG001, fixture
    class SyncByteStream(httpx._types.SyncByteStream):
        def __iter__(self) -> Iterator[bytes]:
            for i in _MOCKED_ACTOR_LOGS:
                yield i
                time.sleep(0.01)

        def close(self) -> None:
            pass

    respx.get(url=f'{_MOCKED_API_URL}/v2/actor-runs/{_MOCKED_RUN_ID}/log?stream=1&raw=1').mock(
        return_value=httpx.Response(stream=SyncByteStream(), status_code=200)
    )


@pytest.fixture
def propagate_stream_logs() -> None:
    # Enable propagation of logs to the caplog fixture
    StreamedLog._force_propagate = True
    StatusMessageWatcher._force_propagate = True
    logging.getLogger(f'apify.{_MOCKED_ACTOR_NAME}-{_MOCKED_RUN_ID}').setLevel(logging.DEBUG)


@pytest.fixture
def reduce_final_timeout_for_status_message_redirector() -> None:
    """Reduce timeout used by the `StatusMessageWatcher`

    This timeout makes sense on the platform, but in tests it is better to reduce it to speed up the tests.
    """
    StatusMessageWatcher._final_sleep_time_s = 2


@pytest.mark.parametrize(
    ('log_from_start', 'expected_log_count'),
    [
        (True, len(_EXPECTED_MESSAGES_AND_LEVELS)),
        (False, len(_EXPECTED_MESSAGES_AND_LEVELS) - _EXISTING_LOGS_BEFORE_REDIRECT_ATTACH),
    ],
)
@respx.mock
async def test_redirected_logs_async(
    *,
    caplog: LogCaptureFixture,
    mock_api_async: None,  # noqa: ARG001, fixture
    propagate_stream_logs: None,  # noqa: ARG001, fixture
    log_from_start: bool,
    expected_log_count: int,
) -> None:
    """Test that redirected logs are formatted correctly."""

    run_client = ApifyClientAsync(token='mocked_token', api_url=_MOCKED_API_URL).run(run_id=_MOCKED_RUN_ID)

    with patch('apify_client.clients.resource_clients.log.datetime') as mocked_datetime:
        # Mock `now()` so that it has timestamp bigger than the first 3 logs
        mocked_datetime.now.return_value = datetime.fromisoformat('2025-05-13T07:24:14.132+00:00')
        streamed_log = await run_client.get_streamed_log(from_start=log_from_start)

    # Set `propagate=True` during the tests, so that caplog can see the logs..
    logger_name = f'apify.{_MOCKED_ACTOR_NAME}-{_MOCKED_RUN_ID}'

    with caplog.at_level(logging.DEBUG, logger=logger_name):
        async with streamed_log:
            # Do stuff while the log from the other Actor is being redirected to the logs.
            await asyncio.sleep(2)

    # Ensure logs are propagated
    assert {(record.message, record.levelno) for record in caplog.records} == set(
        _EXPECTED_MESSAGES_AND_LEVELS[-expected_log_count:]
    )


@pytest.mark.parametrize(
    ('log_from_start', 'expected_log_count'),
    [
        (True, len(_EXPECTED_MESSAGES_AND_LEVELS)),
        (False, len(_EXPECTED_MESSAGES_AND_LEVELS) - _EXISTING_LOGS_BEFORE_REDIRECT_ATTACH),
    ],
)
@respx.mock
def test_redirected_logs_sync(
    *,
    caplog: LogCaptureFixture,
    mock_api_sync: None,  # noqa: ARG001, fixture
    propagate_stream_logs: None,  # noqa: ARG001, fixture
    log_from_start: bool,
    expected_log_count: int,
) -> None:
    """Test that redirected logs are formatted correctly."""

    run_client = ApifyClient(token='mocked_token', api_url=_MOCKED_API_URL).run(run_id=_MOCKED_RUN_ID)

    with patch('apify_client.clients.resource_clients.log.datetime') as mocked_datetime:
        # Mock `now()` so that it has timestamp bigger than the first 3 logs
        mocked_datetime.now.return_value = datetime.fromisoformat('2025-05-13T07:24:14.132+00:00')
        streamed_log = run_client.get_streamed_log(from_start=log_from_start)

    # Set `propagate=True` during the tests, so that caplog can see the logs..
    logger_name = f'apify.{_MOCKED_ACTOR_NAME}-{_MOCKED_RUN_ID}'

    with caplog.at_level(logging.DEBUG, logger=logger_name), streamed_log:
        # Do stuff while the log from the other Actor is being redirected to the logs.
        time.sleep(2)

    # Ensure logs are propagated
    assert {(record.message, record.levelno) for record in caplog.records} == set(
        _EXPECTED_MESSAGES_AND_LEVELS[-expected_log_count:]
    )


@respx.mock
async def test_actor_call_redirect_logs_to_default_logger_async(
    caplog: LogCaptureFixture,
    mock_api_async: None,  # noqa: ARG001, fixture
    propagate_stream_logs: None,  # noqa: ARG001, fixture
    reduce_final_timeout_for_status_message_redirector: None,  # noqa: ARG001, fixture
) -> None:
    """Test that logs are redirected correctly to the default logger.

    Caplog contains logs before formatting, so formatting is not included in the test expectations."""
    logger_name = f'apify.{_MOCKED_ACTOR_NAME} runId:{_MOCKED_RUN_ID}'
    logger = logging.getLogger(logger_name)
    actor_client = ApifyClientAsync(token='mocked_token', api_url=_MOCKED_API_URL).actor(actor_id=_MOCKED_ACTOR_ID)

    with caplog.at_level(logging.DEBUG, logger=logger_name):
        await actor_client.call()

    # Ensure expected handler and formater
    assert isinstance(logger.handlers[0].formatter, RedirectLogFormatter)
    assert isinstance(logger.handlers[0], logging.StreamHandler)

    # Ensure logs are propagated
    assert {(record.message, record.levelno) for record in caplog.records} == set(
        _EXPECTED_MESSAGES_AND_LEVELS_WITH_STATUS_MESSAGES
    )


@respx.mock
def test_actor_call_redirect_logs_to_default_logger_sync(
    caplog: LogCaptureFixture,
    mock_api_sync: None,  # noqa: ARG001, fixture
    propagate_stream_logs: None,  # noqa: ARG001, fixture
    reduce_final_timeout_for_status_message_redirector: None,  # noqa: ARG001, fixture
) -> None:
    """Test that logs are redirected correctly to the default logger.

    Caplog contains logs before formatting, so formatting is not included in the test expectations."""
    logger_name = f'apify.{_MOCKED_ACTOR_NAME} runId:{_MOCKED_RUN_ID}'
    logger = logging.getLogger(logger_name)
    actor_client = ApifyClient(token='mocked_token', api_url=_MOCKED_API_URL).actor(actor_id=_MOCKED_ACTOR_ID)

    with caplog.at_level(logging.DEBUG, logger=logger_name):
        actor_client.call()

    # Ensure expected handler and formater
    assert isinstance(logger.handlers[0].formatter, RedirectLogFormatter)
    assert isinstance(logger.handlers[0], logging.StreamHandler)

    # Ensure logs are propagated
    assert {(record.message, record.levelno) for record in caplog.records} == set(
        _EXPECTED_MESSAGES_AND_LEVELS_WITH_STATUS_MESSAGES
    )


@respx.mock
async def test_actor_call_no_redirect_logs_async(
    caplog: LogCaptureFixture,
    mock_api_async: None,  # noqa: ARG001, fixture
    propagate_stream_logs: None,  # noqa: ARG001, fixture
) -> None:
    logger_name = f'apify.{_MOCKED_ACTOR_NAME}-{_MOCKED_RUN_ID}'
    actor_client = ApifyClientAsync(token='mocked_token', api_url=_MOCKED_API_URL).actor(actor_id=_MOCKED_ACTOR_ID)

    with caplog.at_level(logging.DEBUG, logger=logger_name):
        await actor_client.call(logger=None)

    assert len(caplog.records) == 0


@respx.mock
def test_actor_call_no_redirect_logs_sync(
    caplog: LogCaptureFixture,
    mock_api_sync: None,  # noqa: ARG001, fixture
    propagate_stream_logs: None,  # noqa: ARG001, fixture
) -> None:
    logger_name = f'apify.{_MOCKED_ACTOR_NAME}-{_MOCKED_RUN_ID}'
    actor_client = ApifyClient(token='mocked_token', api_url=_MOCKED_API_URL).actor(actor_id=_MOCKED_ACTOR_ID)

    with caplog.at_level(logging.DEBUG, logger=logger_name):
        actor_client.call(logger=None)

    assert len(caplog.records) == 0


@respx.mock
async def test_actor_call_redirect_logs_to_custom_logger_async(
    caplog: LogCaptureFixture,
    mock_api_async: None,  # noqa: ARG001, fixture
    propagate_stream_logs: None,  # noqa: ARG001, fixture
    reduce_final_timeout_for_status_message_redirector: None,  # noqa: ARG001, fixture
) -> None:
    """Test that logs are redirected correctly to the custom logger."""
    logger_name = 'custom_logger'
    logger = logging.getLogger(logger_name)
    actor_client = ApifyClientAsync(token='mocked_token', api_url=_MOCKED_API_URL).actor(actor_id=_MOCKED_ACTOR_ID)

    with caplog.at_level(logging.DEBUG, logger=logger_name):
        await actor_client.call(logger=logger)

    # Ensure logs are propagated
    assert {(record.message, record.levelno) for record in caplog.records} == set(
        _EXPECTED_MESSAGES_AND_LEVELS_WITH_STATUS_MESSAGES
    )


@respx.mock
def test_actor_call_redirect_logs_to_custom_logger_sync(
    caplog: LogCaptureFixture,
    mock_api_sync: None,  # noqa: ARG001, fixture
    propagate_stream_logs: None,  # noqa: ARG001, fixture
    reduce_final_timeout_for_status_message_redirector: None,  # noqa: ARG001, fixture
) -> None:
    """Test that logs are redirected correctly to the custom logger."""
    logger_name = 'custom_logger'
    logger = logging.getLogger(logger_name)
    actor_client = ApifyClient(token='mocked_token', api_url=_MOCKED_API_URL).actor(actor_id=_MOCKED_ACTOR_ID)

    with caplog.at_level(logging.DEBUG, logger=logger_name):
        actor_client.call(logger=logger)

    # Ensure logs are propagated
    assert {(record.message, record.levelno) for record in caplog.records} == set(
        _EXPECTED_MESSAGES_AND_LEVELS_WITH_STATUS_MESSAGES
    )


@respx.mock
async def test_redirect_status_message_async(
    *,
    caplog: LogCaptureFixture,
    mock_api: None,  # noqa: ARG001, fixture
    propagate_stream_logs: None,  # noqa: ARG001, fixture
    reduce_final_timeout_for_status_message_redirector: None,  # noqa: ARG001, fixture
) -> None:
    """Test redirected status and status messages."""

    run_client = ApifyClientAsync(token='mocked_token', api_url=_MOCKED_API_URL).run(run_id=_MOCKED_RUN_ID)

    logger_name = f'apify.{_MOCKED_ACTOR_NAME}-{_MOCKED_RUN_ID}'

    status_message_redirector = await run_client.get_status_message_watcher(check_period=timedelta(seconds=0))
    with caplog.at_level(logging.DEBUG, logger=logger_name):
        async with status_message_redirector:
            # Do stuff while the status from the other Actor is being redirected to the logs.
            await asyncio.sleep(3)

    assert caplog.records[0].message == 'Status: RUNNING, Message: Initial message'
    assert caplog.records[1].message == 'Status: RUNNING, Message: Another message'
    assert caplog.records[2].message == 'Status: SUCCEEDED, Message: Final message'


@respx.mock
def test_redirect_status_message_sync(
    *,
    caplog: LogCaptureFixture,
    mock_api: None,  # noqa: ARG001, fixture
    propagate_stream_logs: None,  # noqa: ARG001, fixture
    reduce_final_timeout_for_status_message_redirector: None,  # noqa: ARG001, fixture
) -> None:
    """Test redirected status and status messages."""

    run_client = ApifyClient(token='mocked_token', api_url=_MOCKED_API_URL).run(run_id=_MOCKED_RUN_ID)

    logger_name = f'apify.{_MOCKED_ACTOR_NAME}-{_MOCKED_RUN_ID}'

    status_message_redirector = run_client.get_status_message_watcher(check_period=timedelta(seconds=0))
    with caplog.at_level(logging.DEBUG, logger=logger_name), status_message_redirector:
        # Do stuff while the status from the other Actor is being redirected to the logs.
        time.sleep(3)

    assert caplog.records[0].message == 'Status: RUNNING, Message: Initial message'
    assert caplog.records[1].message == 'Status: RUNNING, Message: Another message'
    assert caplog.records[2].message == 'Status: SUCCEEDED, Message: Final message'

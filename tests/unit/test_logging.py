from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from apify_shared.consts import ActorJobStatus
from werkzeug import Request, Response

from apify_client import ApifyClient, ApifyClientAsync
from apify_client._logging import RedirectLogFormatter
from apify_client.clients.resource_clients.log import StatusMessageWatcher, StreamedLog

if TYPE_CHECKING:
    from collections.abc import Iterator

    from _pytest.logging import LogCaptureFixture
    from pytest_httpserver import HTTPServer

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


class StatusResponseGenerator:
    """Generator for actor run status responses to simulate changing status over time."""

    def __init__(self) -> None:
        self.current_status_index = 0
        self.requests_for_current_status = 0
        self.min_requests_per_status = 5

        self.statuses = [
            ('Initial message', ActorJobStatus.RUNNING, False),
            ('Another message', ActorJobStatus.RUNNING, False),
            ('Final message', ActorJobStatus.SUCCEEDED, True),
        ]

    def get_response(self, _request: Request) -> Response:
        if self.current_status_index < len(self.statuses):
            message, status, is_terminal = self.statuses[self.current_status_index]
        else:
            message, status, is_terminal = self.statuses[-1]

        self.requests_for_current_status += 1

        if (
            self.requests_for_current_status >= self.min_requests_per_status
            and self.current_status_index < len(self.statuses) - 1
            and not is_terminal
        ):
            self.current_status_index += 1
            self.requests_for_current_status = 0

        status_data = {
            'data': {
                'id': _MOCKED_RUN_ID,
                'actId': _MOCKED_ACTOR_ID,
                'status': status,
                'statusMessage': message,
                'isStatusMessageTerminal': is_terminal,
            }
        }

        return Response(response=json.dumps(status_data), status=200, mimetype='application/json')


def _streaming_log_handler(_request: Request) -> Response:
    """Handler for streaming log requests."""

    def generate_logs() -> Iterator[bytes]:
        for chunk in _MOCKED_ACTOR_LOGS:
            yield chunk
            time.sleep(0.01)

    total_size = sum(len(chunk) for chunk in _MOCKED_ACTOR_LOGS)

    return Response(
        response=generate_logs(),
        status=200,
        mimetype='application/octet-stream',
        headers={'Content-Length': str(total_size)},
    )


@pytest.fixture
def mock_api(httpserver: HTTPServer) -> None:
    """Set up HTTP server with mocked API endpoints."""
    status_generator = StatusResponseGenerator()

    # Add actor run status endpoint
    httpserver.expect_request(f'/v2/actor-runs/{_MOCKED_RUN_ID}', method='GET').respond_with_handler(
        status_generator.get_response
    )

    # Add actor info endpoint
    httpserver.expect_request(f'/v2/acts/{_MOCKED_ACTOR_ID}', method='GET').respond_with_json(
        {'data': {'name': _MOCKED_ACTOR_NAME}}
    )

    # Add actor run creation endpoint
    httpserver.expect_request(f'/v2/acts/{_MOCKED_ACTOR_ID}/runs', method='POST').respond_with_json(
        {'data': {'id': _MOCKED_RUN_ID}}
    )

    httpserver.expect_request(
        f'/v2/actor-runs/{_MOCKED_RUN_ID}/log', method='GET', query_string='stream=1&raw=1'
    ).respond_with_handler(_streaming_log_handler)


@pytest.fixture
def propagate_stream_logs() -> None:
    """Enable propagation of logs to the caplog fixture."""
    StreamedLog._force_propagate = True
    StatusMessageWatcher._force_propagate = True
    logging.getLogger(f'apify.{_MOCKED_ACTOR_NAME}-{_MOCKED_RUN_ID}').setLevel(logging.DEBUG)


@pytest.fixture
def reduce_final_timeout_for_status_message_redirector() -> None:
    """Reduce timeout used by the `StatusMessageWatcher`.

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
@pytest.mark.usefixtures('mock_api', 'propagate_stream_logs')
async def test_redirected_logs_async(
    *,
    caplog: LogCaptureFixture,
    log_from_start: bool,
    expected_log_count: int,
    httpserver: HTTPServer,
) -> None:
    """Test that redirected logs are formatted correctly."""

    api_url = httpserver.url_for('/').removesuffix('/')

    run_client = ApifyClientAsync(token='mocked_token', api_url=api_url).run(run_id=_MOCKED_RUN_ID)

    with patch('apify_client.clients.resource_clients.log.datetime') as mocked_datetime:
        # Mock `now()` so that it has timestamp bigger than the first 3 logs
        mocked_datetime.now.return_value = datetime.fromisoformat('2025-05-13T07:24:14.132+00:00')
        streamed_log = await run_client.get_streamed_log(from_start=log_from_start)

    # Set `propagate=True` during the tests, so that caplog can see the logs..
    logger_name = f'apify.{_MOCKED_ACTOR_NAME}-{_MOCKED_RUN_ID}'

    with caplog.at_level(logging.DEBUG, logger=logger_name):
        async with streamed_log:
            # Do stuff while the log from the other Actor is being redirected to the logs.
            await asyncio.sleep(1)

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
@pytest.mark.usefixtures('mock_api', 'propagate_stream_logs')
def test_redirected_logs_sync(
    *,
    caplog: LogCaptureFixture,
    log_from_start: bool,
    expected_log_count: int,
    httpserver: HTTPServer,
) -> None:
    """Test that redirected logs are formatted correctly."""

    api_url = httpserver.url_for('/').removesuffix('/')

    run_client = ApifyClient(token='mocked_token', api_url=api_url).run(run_id=_MOCKED_RUN_ID)

    with patch('apify_client.clients.resource_clients.log.datetime') as mocked_datetime:
        # Mock `now()` so that it has timestamp bigger than the first 3 logs
        mocked_datetime.now.return_value = datetime.fromisoformat('2025-05-13T07:24:14.132+00:00')
        streamed_log = run_client.get_streamed_log(from_start=log_from_start)

    # Set `propagate=True` during the tests, so that caplog can see the logs..
    logger_name = f'apify.{_MOCKED_ACTOR_NAME}-{_MOCKED_RUN_ID}'

    with caplog.at_level(logging.DEBUG, logger=logger_name), streamed_log:
        # Do stuff while the log from the other Actor is being redirected to the logs.
        time.sleep(1)

    # Ensure logs are propagated
    assert {(record.message, record.levelno) for record in caplog.records} == set(
        _EXPECTED_MESSAGES_AND_LEVELS[-expected_log_count:]
    )


@pytest.mark.usefixtures('mock_api', 'propagate_stream_logs', 'reduce_final_timeout_for_status_message_redirector')
async def test_actor_call_redirect_logs_to_default_logger_async(
    caplog: LogCaptureFixture,
    httpserver: HTTPServer,
) -> None:
    """Test that logs are redirected correctly to the default logger.

    Caplog contains logs before formatting, so formatting is not included in the test expectations."""
    api_url = httpserver.url_for('/').removesuffix('/')

    logger_name = f'apify.{_MOCKED_ACTOR_NAME} runId:{_MOCKED_RUN_ID}'
    logger = logging.getLogger(logger_name)
    actor_client = ApifyClientAsync(token='mocked_token', api_url=api_url).actor(actor_id=_MOCKED_ACTOR_ID)

    with caplog.at_level(logging.DEBUG, logger=logger_name):
        await actor_client.call()

    # Ensure expected handler and formatter
    assert isinstance(logger.handlers[0].formatter, RedirectLogFormatter)
    assert isinstance(logger.handlers[0], logging.StreamHandler)

    # Ensure logs are propagated
    assert {(record.message, record.levelno) for record in caplog.records} == set(
        _EXPECTED_MESSAGES_AND_LEVELS_WITH_STATUS_MESSAGES
    )


@pytest.mark.usefixtures('mock_api', 'propagate_stream_logs', 'reduce_final_timeout_for_status_message_redirector')
def test_actor_call_redirect_logs_to_default_logger_sync(
    caplog: LogCaptureFixture,
    httpserver: HTTPServer,
) -> None:
    """Test that logs are redirected correctly to the default logger.

    Caplog contains logs before formatting, so formatting is not included in the test expectations."""
    api_url = httpserver.url_for('/').removesuffix('/')

    logger_name = f'apify.{_MOCKED_ACTOR_NAME} runId:{_MOCKED_RUN_ID}'
    logger = logging.getLogger(logger_name)
    actor_client = ApifyClient(token='mocked_token', api_url=api_url).actor(actor_id=_MOCKED_ACTOR_ID)

    with caplog.at_level(logging.DEBUG, logger=logger_name):
        actor_client.call()

    # Ensure expected handler and formatter
    assert isinstance(logger.handlers[0].formatter, RedirectLogFormatter)
    assert isinstance(logger.handlers[0], logging.StreamHandler)

    # Ensure logs are propagated
    assert {(record.message, record.levelno) for record in caplog.records} == set(
        _EXPECTED_MESSAGES_AND_LEVELS_WITH_STATUS_MESSAGES
    )


@pytest.mark.usefixtures('mock_api', 'propagate_stream_logs')
async def test_actor_call_no_redirect_logs_async(
    caplog: LogCaptureFixture,
    httpserver: HTTPServer,
) -> None:
    api_url = httpserver.url_for('/').removesuffix('/')

    logger_name = f'apify.{_MOCKED_ACTOR_NAME}-{_MOCKED_RUN_ID}'
    actor_client = ApifyClientAsync(token='mocked_token', api_url=api_url).actor(actor_id=_MOCKED_ACTOR_ID)

    with caplog.at_level(logging.DEBUG, logger=logger_name):
        await actor_client.call(logger=None)

    assert len(caplog.records) == 0


@pytest.mark.usefixtures('mock_api', 'propagate_stream_logs')
def test_actor_call_no_redirect_logs_sync(
    caplog: LogCaptureFixture,
    httpserver: HTTPServer,
) -> None:
    api_url = httpserver.url_for('/').removesuffix('/')

    logger_name = f'apify.{_MOCKED_ACTOR_NAME}-{_MOCKED_RUN_ID}'
    actor_client = ApifyClient(token='mocked_token', api_url=api_url).actor(actor_id=_MOCKED_ACTOR_ID)

    with caplog.at_level(logging.DEBUG, logger=logger_name):
        actor_client.call(logger=None)

    assert len(caplog.records) == 0


@pytest.mark.usefixtures('mock_api', 'propagate_stream_logs', 'reduce_final_timeout_for_status_message_redirector')
async def test_actor_call_redirect_logs_to_custom_logger_async(
    caplog: LogCaptureFixture,
    httpserver: HTTPServer,
) -> None:
    """Test that logs are redirected correctly to the custom logger."""
    api_url = httpserver.url_for('/').removesuffix('/')

    logger_name = 'custom_logger'
    logger = logging.getLogger(logger_name)
    actor_client = ApifyClientAsync(token='mocked_token', api_url=api_url).actor(actor_id=_MOCKED_ACTOR_ID)

    with caplog.at_level(logging.DEBUG, logger=logger_name):
        await actor_client.call(logger=logger)

    # Ensure logs are propagated
    assert {(record.message, record.levelno) for record in caplog.records} == set(
        _EXPECTED_MESSAGES_AND_LEVELS_WITH_STATUS_MESSAGES
    )


@pytest.mark.usefixtures('mock_api', 'propagate_stream_logs', 'reduce_final_timeout_for_status_message_redirector')
def test_actor_call_redirect_logs_to_custom_logger_sync(
    caplog: LogCaptureFixture,
    httpserver: HTTPServer,
) -> None:
    """Test that logs are redirected correctly to the custom logger."""
    api_url = httpserver.url_for('/').removesuffix('/')

    logger_name = 'custom_logger'
    logger = logging.getLogger(logger_name)
    actor_client = ApifyClient(token='mocked_token', api_url=api_url).actor(actor_id=_MOCKED_ACTOR_ID)

    with caplog.at_level(logging.DEBUG, logger=logger_name):
        actor_client.call(logger=logger)

    # Ensure logs are propagated
    assert {(record.message, record.levelno) for record in caplog.records} == set(
        _EXPECTED_MESSAGES_AND_LEVELS_WITH_STATUS_MESSAGES
    )


@pytest.mark.usefixtures('mock_api', 'propagate_stream_logs', 'reduce_final_timeout_for_status_message_redirector')
async def test_redirect_status_message_async(
    *,
    caplog: LogCaptureFixture,
    httpserver: HTTPServer,
) -> None:
    """Test redirected status and status messages."""
    api_url = httpserver.url_for('/').removesuffix('/')

    run_client = ApifyClientAsync(token='mocked_token', api_url=api_url).run(run_id=_MOCKED_RUN_ID)

    logger_name = f'apify.{_MOCKED_ACTOR_NAME}-{_MOCKED_RUN_ID}'

    status_message_redirector = await run_client.get_status_message_watcher(check_period=timedelta(seconds=0))
    with caplog.at_level(logging.DEBUG, logger=logger_name):
        async with status_message_redirector:
            # Do stuff while the status from the other Actor is being redirected to the logs.
            await asyncio.sleep(1)

    assert caplog.records[0].message == 'Status: RUNNING, Message: Initial message'
    assert caplog.records[1].message == 'Status: RUNNING, Message: Another message'
    assert caplog.records[2].message == 'Status: SUCCEEDED, Message: Final message'


@pytest.mark.usefixtures('mock_api', 'propagate_stream_logs', 'reduce_final_timeout_for_status_message_redirector')
def test_redirect_status_message_sync(
    *,
    caplog: LogCaptureFixture,
    httpserver: HTTPServer,
) -> None:
    """Test redirected status and status messages."""

    api_url = httpserver.url_for('/').removesuffix('/')

    run_client = ApifyClient(token='mocked_token', api_url=api_url).run(run_id=_MOCKED_RUN_ID)

    logger_name = f'apify.{_MOCKED_ACTOR_NAME}-{_MOCKED_RUN_ID}'

    status_message_redirector = run_client.get_status_message_watcher(check_period=timedelta(seconds=0))
    with caplog.at_level(logging.DEBUG, logger=logger_name), status_message_redirector:
        # Do stuff while the status from the other Actor is being redirected to the logs.
        time.sleep(1)

    assert caplog.records[0].message == 'Status: RUNNING, Message: Initial message'
    assert caplog.records[1].message == 'Status: RUNNING, Message: Another message'
    assert caplog.records[2].message == 'Status: SUCCEEDED, Message: Final message'

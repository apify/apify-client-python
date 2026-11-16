from __future__ import annotations

import logging
from unittest.mock import Mock

import pytest

from apify_client._streamed_log import StreamedLogBase


@pytest.mark.parametrize(
    ('chunks', 'expected_calls'),
    [
        pytest.param(
            [b'2025-05-13T07:24:12.588Z first\n2025-05-13T07:24:13', b'.588Z second\n'],
            [(logging.INFO, '2025-05-13T07:24:12.588Z first'), (logging.INFO, '2025-05-13T07:24:13.588Z second')],
            id='marker-split-across-chunks',
        ),
        pytest.param(
            [b'2025-05-13T07:24:12.588Z unterminated'],
            [],
            id='unterminated-line-waits-for-newline',
        ),
        pytest.param(
            [b'preamble without marker\n', b'2025-05-13T07:24:12.588Z first\n'],
            [(logging.INFO, '2025-05-13T07:24:12.588Z first')],
            id='text-before-first-message-is-skipped',
        ),
    ],
)
def test_streamed_log_redirects_each_complete_line(chunks: list[bytes], expected_calls: list[tuple[int, str]]) -> None:
    """Each chunk redirects the messages its newlines complete and keeps only the unterminated rest."""
    to_logger = Mock(spec=logging.Logger)
    streamed_log = StreamedLogBase(to_logger)

    for chunk in chunks:
        streamed_log._process_new_data(chunk)

    calls = [(call.kwargs['level'], call.kwargs['msg']) for call in to_logger.log.call_args_list]
    assert calls == expected_calls

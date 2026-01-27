"""Utilities for parsing HTTP responses."""

from __future__ import annotations

import re
from http import HTTPStatus
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from impit import Response

from apify_client.errors import InvalidResponseBodyError


def response_to_dict(response: Response) -> dict:
    """Ensure the API response is a dictionary.

    Args:
        response: The parsed API response (typically from `response.json()`).

    Returns:
        The response as a dictionary.

    Raises:
        ValueError: If the response is not a dictionary.
    """
    data = response.json()
    if isinstance(data, dict):
        return data

    raise ValueError(f'The response is not a dictionary. Got: {type(data).__name__}')


def response_to_list(response: Response) -> list:
    """Ensure the API response is a list.

    Args:
        response: The parsed API response (typically from `response.json()`).

    Returns:
        The response as a list.

    Raises:
        ValueError: If the response is not a list.
    """
    data = response.json()
    if isinstance(data, list):
        return data

    raise ValueError(f'The response is not a list. Got: {type(data).__name__}')


def maybe_parse_response(response: Response) -> Any:
    """Parse an HTTP response based on its content type.

    Args:
        response: The HTTP response to parse.

    Returns:
        Parsed response data (JSON dict/list, text string, or raw bytes).

    Raises:
        InvalidResponseBodyError: If the response body cannot be parsed.
    """
    if response.status_code == HTTPStatus.NO_CONTENT:
        return None

    content_type = ''
    if 'content-type' in response.headers:
        content_type = response.headers['content-type'].split(';')[0].strip()

    try:
        if re.search(r'^application/json', content_type, flags=re.IGNORECASE):
            response_data = response.json()
        elif re.search(r'^application/.*xml$', content_type, flags=re.IGNORECASE) or re.search(
            r'^text/', content_type, flags=re.IGNORECASE
        ):
            response_data = response.text
        else:
            response_data = response.content
    except ValueError as err:
        raise InvalidResponseBodyError(response) from err
    else:
        return response_data

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from apify_client._consts import OVERRIDABLE_DEFAULT_HEADERS

if TYPE_CHECKING:
    from apify_client.http_clients import HttpResponse


def to_safe_id(id: str) -> str:
    """Convert a resource ID to URL-safe format by replacing forward slashes with tildes.

    Args:
        id: The resource identifier in format `resource_id` or `username/resource_id`.

    Returns:
        The resource identifier with `/` characters replaced by `~`.
    """
    return id.replace('/', '~')


def response_to_dict(response: HttpResponse) -> dict:
    """Parse the API response as a dictionary and validate its type.

    Args:
        response: The HTTP response object from the API.

    Returns:
        The parsed response as a dictionary.

    Raises:
        ValueError: If the response is not a dictionary.
    """
    data = response.json()

    if isinstance(data, dict):
        return data

    raise ValueError(f'The response is not a dictionary. Got: {type(data).__name__}')


def response_to_list(response: HttpResponse) -> list:
    """Parse the API response as a list and validate its type.

    Args:
        response: The HTTP response object from the API.

    Returns:
        The parsed response as a list.

    Raises:
        ValueError: If the response is not a list.
    """
    data = response.json()

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        return [data]

    raise ValueError(f'The response is not a list. Got: {type(data).__name__}')


def check_custom_headers(class_name: str, headers: dict[str, str]) -> None:
    """Warn if custom headers override important default headers."""
    overwrite_headers = [key for key in headers if key.title() in OVERRIDABLE_DEFAULT_HEADERS]

    if overwrite_headers:
        warnings.warn(
            f'{", ".join(overwrite_headers)} headers of {class_name} was overridden with an '
            'explicit value. A wrong header value can lead to API errors, it is recommended to use the default '
            f'value for following headers: {", ".join(OVERRIDABLE_DEFAULT_HEADERS)}.',
            category=UserWarning,
            stacklevel=3,
        )

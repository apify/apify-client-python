from __future__ import annotations

import warnings
from typing import TYPE_CHECKING
from urllib.parse import quote

from apify_client._consts import (
    ALREADY_COMPRESSED_MEDIA_TYPE_PREFIXES,
    ALREADY_COMPRESSED_MEDIA_TYPES,
    COMPRESSIBLE_MEDIA_TYPE_SUFFIXES,
    COMPRESSIBLE_MEDIA_TYPES,
    OVERRIDABLE_DEFAULT_HEADERS,
)

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


def to_path_segment(value: str) -> str:
    """Percent-encode a caller-supplied value so it stays a single URL path segment.

    Without this, a value carrying `/`, `?` or `#` would restructure the URL it is interpolated into: it could
    reach a different endpoint, append its own query parameters, or be silently truncated at a fragment.

    Args:
        value: The value to place in a single path segment, for example a key-value store record key.

    Returns:
        The percent-encoded value, which a URL parser can only read as one path segment.

    Raises:
        ValueError: If the value is empty, `.` or `..`, none of which can be carried in a path segment at all.
    """
    # Encoding cannot save these three: an empty value leaves nothing but the separator, and a URL parser
    # resolves a dot segment after percent-decoding, so `%2E%2E` collapses just like `..`. Either way the
    # request lands on a parent endpoint, where `..` makes the same verb act on the whole resource.
    if value in {'', '.', '..'}:
        raise ValueError(f'"{value}" cannot be used as a URL path segment.')

    return quote(value, safe='')


def is_compressible_content_type(content_type: str | None) -> bool:
    """Decide whether a request body with the given content type is worth compressing.

    Images, audio, video and archives already carry their own compression. Running them through gzip or brotli
    burns CPU, holds a second full copy of the body in memory, and usually produces output slightly larger than
    the input. Formats that are raw despite such a media type, for example `image/bmp` or `audio/wav`, are still
    compressed. A body with no content type is assumed to be compressible.

    Args:
        content_type: The value of the `Content-Type` header, if any.

    Returns:
        `True` if the body should be compressed before it is sent.
    """
    if not content_type:
        return True

    # `Content-Type` is case-insensitive and may carry parameters, for example `text/plain; charset=utf-8`.
    media_type = content_type.split(';', 1)[0].strip().lower()

    if media_type in COMPRESSIBLE_MEDIA_TYPES or media_type.endswith(COMPRESSIBLE_MEDIA_TYPE_SUFFIXES):
        return True

    return not (
        media_type in ALREADY_COMPRESSED_MEDIA_TYPES or media_type.startswith(ALREADY_COMPRESSED_MEDIA_TYPE_PREFIXES)
    )


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

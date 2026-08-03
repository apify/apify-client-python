from __future__ import annotations

from datetime import timedelta

DEFAULT_API_URL = 'https://api.apify.com'
"""Default base URL for the Apify API."""

API_VERSION = 'v2'
"""Current Apify API version."""

DEFAULT_TIMEOUT_SHORT = timedelta(seconds=5)
"""Default timeout for fast CRUD operations (e.g., get, update, delete)."""

DEFAULT_TIMEOUT_MEDIUM = timedelta(seconds=30)
"""Default timeout for batch, list, and data transfer operations."""

DEFAULT_TIMEOUT_LONG = timedelta(seconds=360)
"""Default timeout for long-polling, streaming, and other heavy operations."""

DEFAULT_TIMEOUT_MAX = timedelta(seconds=360)
"""Default maximum timeout cap for individual API requests (limits exponential growth)."""

DEFAULT_MAX_RETRIES = 4
"""Default maximum number of retries for failed requests."""

DEFAULT_MIN_DELAY_BETWEEN_RETRIES = timedelta(milliseconds=500)
"""Default minimum delay between retries."""

DEFAULT_WAIT_FOR_FINISH = timedelta(seconds=999999)
"""Default maximum wait time for job completion (effectively infinite)."""

DEFAULT_WAIT_WHEN_JOB_NOT_EXIST = timedelta(seconds=3)
"""How long to wait for a job to exist before giving up."""

OVERRIDABLE_DEFAULT_HEADERS = {'Accept', 'Authorization', 'Accept-Encoding', 'User-Agent'}
"""Headers that can be overridden by users, but will trigger a warning if they do so, as it may lead to API errors."""

ALREADY_COMPRESSED_MEDIA_TYPE_PREFIXES = ('audio/', 'image/', 'video/')
"""Media type prefixes whose payloads carry their own compression, so compressing the request body is wasted work."""

ALREADY_COMPRESSED_MEDIA_TYPES = frozenset(
    {
        'application/epub+zip',
        'application/gzip',
        'application/java-archive',
        'application/vnd.android.package-archive',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.rar',
        'application/x-7z-compressed',
        'application/x-bzip',
        'application/x-bzip2',
        'application/x-gzip',
        'application/x-rar-compressed',
        'application/x-xz',
        'application/x-zip-compressed',
        'application/zip',
        'application/zstd',
        'font/woff',
        'font/woff2',
    }
)
"""Exact media types whose payloads carry their own compression."""

COMPRESSIBLE_MEDIA_TYPES = frozenset(
    {
        'audio/aiff',
        'audio/basic',
        'audio/l16',
        'audio/vnd.wave',
        'audio/wav',
        'audio/wave',
        'audio/x-aiff',
        'audio/x-wav',
        'image/bmp',
        'image/tiff',
        'image/vnd.adobe.photoshop',
        'image/vnd.microsoft.icon',
        'image/x-icon',
        'image/x-ms-bmp',
    }
)
"""Uncompressed media types that sit under an already-compressed prefix, so compressing them still pays off."""

COMPRESSIBLE_MEDIA_TYPE_SUFFIXES = ('+json', '+xml')
"""Structured syntax suffixes marking a media type as text even under an already-compressed prefix (`image/svg+xml`)."""

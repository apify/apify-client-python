from __future__ import annotations

from typing import TYPE_CHECKING

from apify_client.http_compressors._base import HttpCompressor
from apify_client.http_compressors._gzip import GzipHttpCompressor

if TYPE_CHECKING:
    from apify_client.types import HttpCompressionAlgorithm


def resolve_compressor(compression: HttpCompressionAlgorithm | HttpCompressor) -> HttpCompressor:
    """Convert a compression string or `HttpCompressor` instance into a concrete `HttpCompressor`.

    Args:
        compression: A string literal naming an HTTP compression algorithm, or an `HttpCompressor` instance.

    Returns:
        A ready-to-use `HttpCompressor`.

    Raises:
        ImportError: If the requested algorithm needs an optional extra that is not installed.
        ValueError: If `compression` is not a recognized compression algorithm.
    """
    if isinstance(compression, HttpCompressor):
        return compression
    if compression == 'gzip':
        return GzipHttpCompressor()
    if compression == 'brotli':
        # The import is here so the ImportError is raised at call time,
        # not at module import time, giving users a clear message.
        from apify_client.http_compressors import BrotliHttpCompressor  # noqa: PLC0415

        return BrotliHttpCompressor()

    # The backend supports also `deflate` and `identity` (no compression). One can build
    # a custom compressor if needed.
    raise ValueError(f'Unsupported compression algorithm: {compression!r}')

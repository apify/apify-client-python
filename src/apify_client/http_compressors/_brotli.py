from __future__ import annotations

import brotli

from apify_client.http_compressors._base import HttpCompressor


class BrotliHttpCompressor(HttpCompressor):
    """Compresses request bodies using brotli.

    Requires the `brotli` extra: `pip install "apify-client[brotli]"`.
    """

    content_encoding = 'br'

    _min_quality = 0
    """Lowest valid quality (fastest, least compression)."""

    _max_quality = 11
    """Highest valid quality (slowest, best compression)."""

    def __init__(self, *, quality: int = 6) -> None:
        """Initialize the brotli compressor.

        Args:
            quality: Compression level, from the fastest to the best compression.

        Raises:
            ValueError: If `quality` is out of the valid range.
        """
        if not self._min_quality <= quality <= self._max_quality:
            raise ValueError(
                f'brotli quality must be between {self._min_quality} and {self._max_quality}, got {quality}.'
            )
        self._quality = quality

    def compress(self, data: bytes) -> bytes:
        return brotli.compress(data, quality=self._quality)

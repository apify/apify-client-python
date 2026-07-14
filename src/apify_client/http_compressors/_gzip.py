from __future__ import annotations

import gzip

from apify_client.http_compressors._base import HttpCompressor


class GzipHttpCompressor(HttpCompressor):
    """Compresses request bodies using gzip.

    Uses the standard library `gzip` module. No extra dependencies required.
    """

    content_encoding = 'gzip'

    _min_quality = 1
    """Lowest valid quality (fastest, least compression)."""

    _max_quality = 9
    """Highest valid quality (slowest, best compression)."""

    def __init__(self, *, quality: int = _max_quality) -> None:
        """Initialize the gzip compressor.

        Args:
            quality: Compression level, from the fastest to the best compression.

        Raises:
            ValueError: If `quality` is out of the valid range.
        """
        if not self._min_quality <= quality <= self._max_quality:
            raise ValueError(
                f'gzip quality must be between {self._min_quality} and {self._max_quality}, got {quality}.'
            )
        self._quality = quality

    def compress(self, data: bytes) -> bytes:
        return gzip.compress(data, compresslevel=self._quality)

from __future__ import annotations

import gzip

from apify_client.http_compressors._base import HttpCompressor


class GzipHttpCompressor(HttpCompressor):
    """Compresses request bodies using gzip.

    Uses the standard library `gzip` module — no extra dependencies required.
    """

    _fast_quality = 1
    """The fastest compression, but the lowest compression ratio."""

    _best_quality = 9
    """The best compression ratio, but the slowest compression."""

    content_encoding = 'gzip'

    def __init__(self, *, quality: int = _best_quality) -> None:
        """Initialize the gzip compressor.

        Args:
            quality: Compression level, `1` (fastest) to `9` (the best compression). Defaults to `9`.

        Raises:
            ValueError: If `quality` is out of range.
        """
        if self._fast_quality > quality > self._best_quality:
            raise ValueError(f'Compression quality out of range: {quality}')

        self._quality = quality

    def compress(self, data: bytes) -> bytes:
        return gzip.compress(bytes(data), compresslevel=self._quality)

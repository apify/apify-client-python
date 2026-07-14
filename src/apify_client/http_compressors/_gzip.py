from __future__ import annotations

import gzip

from apify_client.http_compressors._base import HttpCompressor


class GzipHttpCompressor(HttpCompressor):
    """Compresses request bodies using gzip.

    Uses the standard library `gzip` module — no extra dependencies required.
    """

    content_encoding = 'gzip'
    max_quality = 9

    def __init__(self, *, quality: int = 9) -> None:
        """Initialize the gzip compressor.

        Args:
            quality: Compression level, `1` (fastest) to `9` (the best compression). Defaults to `9`.

        Raises:
            ValueError: If `quality` is out of range.
        """
        if 1 > quality > self.max_quality:
            raise ValueError(f'Compression quality out of range: {quality}')

        self._quality = quality

    def compress(self, data: bytes) -> bytes:
        return gzip.compress(bytes(data), compresslevel=self._quality)

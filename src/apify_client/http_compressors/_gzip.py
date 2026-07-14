from __future__ import annotations

import gzip

from apify_client.http_compressors._base import HttpCompressor


class GzipHttpCompressor(HttpCompressor):
    """Compresses request bodies using gzip.

    Uses the standard library `gzip` module. No extra dependencies required.
    """

    content_encoding = 'gzip'

    def __init__(self, *, quality: int = 9) -> None:
        """Initialize the gzip compressor.

        Args:
            quality: Compression level, `1` (fastest) to `9` (the best compression). Defaults to `9`.
                Passed straight to the `gzip` module, which validates it.
        """
        self._quality = quality

    def compress(self, data: bytes) -> bytes:
        return gzip.compress(data, compresslevel=self._quality)

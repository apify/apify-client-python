from __future__ import annotations

import brotli

from apify_client.http_compressors._base import HttpCompressor


class BrotliHttpCompressor(HttpCompressor):
    """Compresses request bodies using brotli.

    Requires the `brotli` extra: `pip install "apify-client[brotli]"`.
    """

    content_encoding = 'br'
    max_quality = 11

    def __init__(self, *, quality: int = 6) -> None:
        """Initialize the brotli compressor.

        Args:
            quality: Compression level, `1` (fastest) to `11` (the best compression). Defaults to `6`.

        Raises:
            ValueError: If `quality` is out of range.
        """
        if 1 > quality > self.max_quality:
            raise ValueError(f'Compression quality out of range: {quality}')

        self._quality = quality

    def compress(self, data: bytes) -> bytes:
        return brotli.compress(bytes(data), quality=self._quality)

from __future__ import annotations

import brotli

from apify_client.http_compressors._base import HttpCompressor


class BrotliHttpCompressor(HttpCompressor):
    """Compresses request bodies using brotli.

    Requires the `brotli` extra: `pip install "apify-client[brotli]"`.
    """

    content_encoding = 'br'

    def __init__(self, *, quality: int = 6) -> None:
        """Initialize the brotli compressor.

        Args:
            quality: Compression level, `0` (fastest) to `11` (the best compression). Defaults to `6`,
                a reasonable compromise between speed and compression ratio. Passed straight to the
                `brotli` module, which validates it.
        """
        self._quality = quality

    def compress(self, data: bytes) -> bytes:
        return brotli.compress(data, quality=self._quality)

from __future__ import annotations

import brotli

from apify_client.http_compressors._base import HttpCompressor


class BrotliHttpCompressor(HttpCompressor):
    """Compresses request bodies using brotli.

    Requires the `brotli` extra: `pip install "apify-client[brotli]"`.
    """

    _fast_quality = 0
    """The fastest compression, but the lowest compression ratio."""

    _default_quality = 6
    """Reasonable compromise between the speed and compression ratio."""

    _best_quality = 11
    """The best compression ratio, but the slowest compression."""

    content_encoding = 'br'

    def __init__(self, *, quality: int = _default_quality) -> None:
        """Initialize the brotli compressor.

        Args:
            quality: Compression level, `0` (fastest) to `11` (the best compression). Defaults to `6`.

        Raises:
            ValueError: If `quality` is out of range.
        """
        if self._fast_quality > quality > self._best_quality:
            raise ValueError(f'Compression quality out of range: {quality}')

        self._quality = quality

    def compress(self, data: bytes) -> bytes:
        return brotli.compress(bytes(data), quality=self._quality)

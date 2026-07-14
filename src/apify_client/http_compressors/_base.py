from __future__ import annotations

from abc import ABC, abstractmethod


class HttpCompressor(ABC):
    """Strategy for compressing HTTP request bodies.

    Extend this class to create a custom compressor. Set `content_encoding` to the value
    that should be sent in the `Content-Encoding` header and implement `compress`.
    """

    content_encoding: str
    """Value sent in the `Content-Encoding` header, for example `gzip` or `br`."""

    @abstractmethod
    def compress(self, data: bytes) -> bytes:
        """Compress a request body.

        Args:
            data: The raw bytes to compress.

        Returns:
            The compressed bytes.
        """

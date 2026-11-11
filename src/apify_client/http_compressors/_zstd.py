from __future__ import annotations

import sys

from apify_client.http_compressors._base import HttpCompressor

if sys.version_info >= (3, 14):
    try:
        from compression import zstd
    except ImportError as exc:
        # `compression.zstd` is optional when CPython is built, and no extra can add it to a build without it. A plain
        # `ImportError` means `_zstd` exists but can't load, for example when the zstd shared library is missing.
        if exc.name != '_zstd':
            raise
        # The name must match the `dependency_name` that `http_compressors/__init__.py` passes to `try_import`.
        raise ModuleNotFoundError(
            'zstd compression is unavailable because this Python build was compiled without zstd support, or its zstd '
            f"library cannot be loaded ({exc}). Use compression='gzip' or compression='brotli' instead.",
            name='_zstd',
        ) from exc
else:
    # Not `from backports import zstd`: when another `backports.*` package is installed but this one is not, that
    # raises a plain `ImportError` instead of the `ModuleNotFoundError` the optional-extra handling expects.
    try:
        import backports.zstd as zstd  # noqa: PLR0402
    except ModuleNotFoundError:
        raise
    except ImportError as exc:
        # The package is installed but its C extension can't load. Without this, `import apify_client` would fail for
        # every user, not only for those who pick zstd.
        raise ModuleNotFoundError(
            f'`backports.zstd` failed to load ({exc})',
            name='backports.zstd',
        ) from exc


class ZstdHttpCompressor(HttpCompressor):
    """Compresses request bodies using zstd.

    Uses the standard library `compression.zstd` module on Python 3.14 and newer, provided the Python build includes
    it. On older versions it requires the `zstd` extra: `pip install "apify-client[zstd]"`.
    """

    content_encoding = 'zstd'

    _min_quality = 1
    """Lowest valid quality (fastest, least compression)."""

    _max_quality = 19
    """Highest valid quality (slowest, best compression).

    zstd itself goes up to 22, but levels 20 to 22 use a window above the 8 MB that RFC 9659 requires HTTP decoders
    to support, so a record stored at those levels could fail to decode in a client that accepts zstd.
    """

    def __init__(self, *, quality: int = 3) -> None:
        """Initialize the zstd compressor.

        Args:
            quality: Compression level, from the fastest to the best compression. zstd's levels 20 to 22 are not
                accepted: their window exceeds the 8 MB that HTTP decoders are required to support.

        Raises:
            ValueError: If `quality` is out of the valid range.
        """
        if not self._min_quality <= quality <= self._max_quality:
            raise ValueError(
                f'zstd quality must be between {self._min_quality} and {self._max_quality}, got {quality}.'
            )
        self._quality = quality

    def compress(self, data: bytes) -> bytes:
        return zstd.compress(data, level=self._quality)

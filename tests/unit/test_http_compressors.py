from __future__ import annotations

import gzip
import importlib
import sys
from contextlib import contextmanager
from typing import TYPE_CHECKING

import brotli
import pytest

from apify_client.http_compressors import BrotliHttpCompressor, GzipHttpCompressor
from apify_client.http_compressors._resolve import resolve_compressor

if TYPE_CHECKING:
    from collections.abc import Iterator


@contextmanager
def _brotli_unavailable() -> Iterator[None]:
    """Reimport the `http_compressors` package with the `brotli` import forced to fail.

    Simulates an environment where the optional `brotli` extra is not installed, and restores the
    original module state afterwards so other tests in the same worker are unaffected.
    """

    class _Blocker:
        def find_spec(self, name: str, *_args: object) -> None:
            if name == 'brotli' or name.startswith('brotli.'):
                raise ModuleNotFoundError(f"No module named '{name}'")

    def _affected(name: str) -> bool:
        return name == 'brotli' or name.startswith(('brotli.', 'apify_client.http_compressors'))

    saved = {name: mod for name, mod in list(sys.modules.items()) if _affected(name)}
    blocker = _Blocker()
    sys.meta_path.insert(0, blocker)
    for name in saved:
        del sys.modules[name]

    try:
        importlib.import_module('apify_client.http_compressors')
        yield
    finally:
        sys.meta_path.remove(blocker)
        for name in [name for name in sys.modules if _affected(name)]:
            del sys.modules[name]
        sys.modules.update(saved)


@pytest.mark.parametrize('quality', [1, 9])
def test_gzip_compressor_round_trips_at_quality(quality: int) -> None:
    """Gzip compressor round-trips data at the boundary quality levels."""
    assert gzip.decompress(GzipHttpCompressor(quality=quality).compress(b'payload')) == b'payload'


@pytest.mark.parametrize('quality', [0, 11])
def test_brotli_compressor_round_trips_at_quality(quality: int) -> None:
    """Brotli compressor round-trips data at the boundary quality levels."""
    assert brotli.decompress(BrotliHttpCompressor(quality=quality).compress(b'payload')) == b'payload'


def test_gzip_compressor_round_trips_and_sets_content_encoding() -> None:
    """Gzip compressor round-trips data and reports `gzip` as its content encoding."""
    compressor = GzipHttpCompressor()
    assert compressor.content_encoding == 'gzip'
    assert gzip.decompress(compressor.compress(b'hello world')) == b'hello world'


def test_brotli_compressor_round_trips_and_sets_content_encoding() -> None:
    """Brotli compressor round-trips data and reports `br` as its content encoding."""
    compressor = BrotliHttpCompressor()
    assert compressor.content_encoding == 'br'
    assert brotli.decompress(compressor.compress(b'hello world')) == b'hello world'


def test_resolve_compressor_gzip() -> None:
    """The `'gzip'` literal resolves to a `GzipHttpCompressor`."""
    assert isinstance(resolve_compressor('gzip'), GzipHttpCompressor)


def test_resolve_compressor_brotli() -> None:
    """The `'brotli'` literal resolves to a `BrotliHttpCompressor`."""
    assert isinstance(resolve_compressor('brotli'), BrotliHttpCompressor)


def test_resolve_compressor_passes_through_instance() -> None:
    """An `HttpCompressor` instance is returned unchanged."""
    compressor = BrotliHttpCompressor(quality=11)
    assert resolve_compressor(compressor) is compressor


def test_resolve_compressor_rejects_unknown_algorithm() -> None:
    """An unrecognized encoding raises `ValueError`."""
    with pytest.raises(ValueError, match='Unsupported compression algorithm'):
        resolve_compressor('deflate')  # ty: ignore[invalid-argument-type]


def test_brotli_import_hook_raises_clear_error_when_extra_missing() -> None:
    """Accessing `BrotliHttpCompressor` without the `brotli` extra raises `ImportError`, not `TypeError`."""
    with _brotli_unavailable():
        module = importlib.import_module('apify_client.http_compressors')
        with pytest.raises(ImportError):
            _ = module.BrotliHttpCompressor


def test_resolve_compressor_brotli_raises_clear_error_when_extra_missing() -> None:
    """Resolving `compression='brotli'` without the extra raises `ImportError` at resolution time."""
    with _brotli_unavailable(), pytest.raises(ImportError):
        resolve_compressor('brotli')

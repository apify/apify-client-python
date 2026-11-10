from __future__ import annotations

import gzip
import importlib
import json
import sys
from contextlib import contextmanager
from typing import TYPE_CHECKING
from unittest.mock import Mock

import brotli
import pytest
from werkzeug import Request, Response

from apify_client import ApifyClient, ApifyClientAsync
from apify_client._consts import MIN_COMPRESSION_SIZE
from apify_client.http_compressors import BrotliHttpCompressor, GzipHttpCompressor, ZstdHttpCompressor
from apify_client.http_compressors._resolve import resolve_compressor

if sys.version_info >= (3, 14):
    from compression import zstd
else:
    import backports.zstd as zstd  # noqa: PLR0402 - the same import form as `http_compressors/_zstd.py`

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

    from pytest_httpserver import HTTPServer

    from apify_client.types import HttpCompressionAlgorithm


pytestmark = pytest.mark.usefixtures('http_client_classes')


@contextmanager
def _dependency_unavailable(dependency: str, *importers: str) -> Generator[None]:
    """Reimport the `http_compressors` package with the `dependency` import forced to fail.

    Simulates an environment where the optional extra providing `dependency` is not installed, and restores the
    original module state afterwards so other tests in the same worker are unaffected. `importers` names cached
    packages outside `http_compressors` that import `dependency`; they and their submodules are reimported too.
    """

    class _Blocker:
        def find_spec(self, name: str, *_args: object) -> None:
            if name == dependency or name.startswith(f'{dependency}.'):
                raise ModuleNotFoundError(f"No module named '{name}'", name=dependency)

    def _affected(name: str) -> bool:
        prefixes = tuple(f'{package}.' for package in (dependency, *importers))
        return name in (dependency, *importers) or name.startswith((*prefixes, 'apify_client.http_compressors'))

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


def test_gzip_compressor_defaults_to_quality_6(monkeypatch: pytest.MonkeyPatch) -> None:
    """Gzip compressor uses compression level `6` when no quality is given."""
    compress = Mock(return_value=b'compressed')
    monkeypatch.setattr(gzip, 'compress', compress)

    assert GzipHttpCompressor().compress(b'payload') == b'compressed'
    compress.assert_called_once_with(b'payload', compresslevel=6)


@pytest.mark.parametrize(
    'quality',
    [
        pytest.param(1, id='fastest'),
        pytest.param(9, id='best'),
    ],
)
def test_gzip_compressor_round_trips_at_quality(quality: int) -> None:
    """Gzip compressor round-trips data at the boundary quality levels."""
    assert gzip.decompress(GzipHttpCompressor(quality=quality).compress(b'payload')) == b'payload'


def test_zstd_compressor_defaults_to_level_3(monkeypatch: pytest.MonkeyPatch) -> None:
    """Zstd compressor uses compression level `3` when no quality is given."""
    compress = Mock(return_value=b'compressed')
    monkeypatch.setattr(zstd, 'compress', compress)

    assert ZstdHttpCompressor().compress(b'payload') == b'compressed'
    compress.assert_called_once_with(b'payload', level=3)


@pytest.mark.parametrize(
    'quality',
    [
        pytest.param(1, id='fastest'),
        pytest.param(19, id='best'),
    ],
)
def test_zstd_compressor_round_trips_at_quality(quality: int) -> None:
    """Zstd compressor round-trips data at the boundary quality levels."""
    assert zstd.decompress(ZstdHttpCompressor(quality=quality).compress(b'payload')) == b'payload'


@pytest.mark.parametrize(
    'quality',
    [
        pytest.param(0, id='fastest'),
        pytest.param(11, id='best'),
    ],
)
def test_brotli_compressor_round_trips_at_quality(quality: int) -> None:
    """Brotli compressor round-trips data at the boundary quality levels."""
    assert brotli.decompress(BrotliHttpCompressor(quality=quality).compress(b'payload')) == b'payload'


@pytest.mark.parametrize(
    'quality',
    [
        pytest.param(0, id='below minimum'),
        pytest.param(10, id='above maximum'),
        pytest.param(-1, id='negative'),
    ],
)
def test_gzip_compressor_rejects_out_of_range_quality(quality: int) -> None:
    """Gzip compressor raises `ValueError` at construction for a quality not between `1` and `9`."""
    with pytest.raises(ValueError, match='gzip quality must be between 1 and 9'):
        GzipHttpCompressor(quality=quality)


@pytest.mark.parametrize(
    'quality',
    [
        pytest.param(-1, id='negative'),
        pytest.param(12, id='above maximum'),
    ],
)
def test_brotli_compressor_rejects_out_of_range_quality(quality: int) -> None:
    """Brotli compressor raises `ValueError` at construction for a quality not between `0` and `11`."""
    with pytest.raises(ValueError, match='brotli quality must be between 0 and 11'):
        BrotliHttpCompressor(quality=quality)


@pytest.mark.parametrize(
    'quality',
    [
        pytest.param(0, id='below minimum'),
        pytest.param(20, id='above maximum'),
        pytest.param(-1, id='negative'),
    ],
)
def test_zstd_compressor_rejects_out_of_range_quality(quality: int) -> None:
    """Zstd compressor raises `ValueError` at construction for a quality not between `1` and `19`."""
    with pytest.raises(ValueError, match='zstd quality must be between 1 and 19'):
        ZstdHttpCompressor(quality=quality)


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


def test_zstd_compressor_round_trips_and_sets_content_encoding() -> None:
    """Zstd compressor round-trips data and reports `zstd` as its content encoding."""
    compressor = ZstdHttpCompressor()
    assert compressor.content_encoding == 'zstd'
    assert zstd.decompress(compressor.compress(b'hello world')) == b'hello world'


def test_resolve_compressor_gzip() -> None:
    """The `'gzip'` literal resolves to a `GzipHttpCompressor`."""
    assert isinstance(resolve_compressor('gzip'), GzipHttpCompressor)


def test_resolve_compressor_brotli() -> None:
    """The `'brotli'` literal resolves to a `BrotliHttpCompressor`."""
    assert isinstance(resolve_compressor('brotli'), BrotliHttpCompressor)


def test_resolve_compressor_zstd() -> None:
    """The `'zstd'` literal resolves to a `ZstdHttpCompressor`."""
    assert isinstance(resolve_compressor('zstd'), ZstdHttpCompressor)


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
    with _dependency_unavailable('brotli'):
        module = importlib.import_module('apify_client.http_compressors')
        with pytest.raises(ImportError):
            _ = module.BrotliHttpCompressor


def test_resolve_compressor_brotli_raises_clear_error_when_extra_missing() -> None:
    """Resolving `compression='brotli'` without the extra raises `ImportError` at resolution time."""
    with _dependency_unavailable('brotli'), pytest.raises(ImportError):
        resolve_compressor('brotli')


@pytest.mark.skipif(sys.version_info >= (3, 14), reason='zstd is in the standard library from Python 3.14')
def test_zstd_import_hook_raises_clear_error_when_extra_missing() -> None:
    """Accessing `ZstdHttpCompressor` without the `zstd` extra raises an `ImportError` naming the extra."""
    with _dependency_unavailable('backports.zstd'):
        module = importlib.import_module('apify_client.http_compressors')
        with pytest.raises(ImportError, match=r'apify-client\[zstd\]'):
            _ = module.ZstdHttpCompressor


@pytest.mark.skipif(sys.version_info >= (3, 14), reason='zstd is in the standard library from Python 3.14')
def test_resolve_compressor_zstd_raises_clear_error_when_extra_missing() -> None:
    """Resolving `compression='zstd'` without the extra raises `ImportError` at resolution time."""
    with _dependency_unavailable('backports.zstd'), pytest.raises(ImportError):
        resolve_compressor('zstd')


@pytest.mark.skipif(sys.version_info < (3, 14), reason='zstd is in the standard library only from Python 3.14')
def test_zstd_import_hook_raises_clear_error_when_python_lacks_zstd() -> None:
    """On a Python 3.14+ build without zstd, the package still imports and `ZstdHttpCompressor` raises `ImportError`."""
    with _dependency_unavailable('_zstd', 'compression'):
        module = importlib.import_module('apify_client.http_compressors')
        assert module.GzipHttpCompressor is not None
        with pytest.raises(ImportError, match='compiled without zstd support'):
            _ = module.ZstdHttpCompressor


_ITEMS_PATH = '/v2/datasets/test_dataset_id/items'
_LARGE_BODY = [{'index': index, 'url': f'https://example.com/item/{index}'} for index in range(MIN_COMPRESSION_SIZE)]


def _capture_body(captured: list[Request]) -> Callable[[Request], Response]:
    def handler(request: Request) -> Response:
        captured.append(request)
        return Response(status=201, mimetype='application/json')

    return handler


@pytest.mark.parametrize(
    ('compression', 'content_encoding', 'decompress'),
    [
        pytest.param('gzip', 'gzip', gzip.decompress, id='gzip'),
        pytest.param('brotli', 'br', brotli.decompress, id='brotli'),
        pytest.param('zstd', 'zstd', zstd.decompress, id='zstd'),
    ],
)
def test_configured_compression_reaches_the_wire_sync(
    httpserver: HTTPServer,
    compression: HttpCompressionAlgorithm,
    content_encoding: str,
    decompress: Callable[[bytes], bytes],
) -> None:
    """A body above the threshold arrives at the server compressed with the algorithm the client was given."""
    captured: list[Request] = []
    httpserver.expect_request(_ITEMS_PATH, method='POST').respond_with_handler(_capture_body(captured))

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(token='test_token', api_url=api_url, compression=compression)

    client.dataset('test_dataset_id').push_items(_LARGE_BODY)

    assert len(captured) == 1
    assert captured[0].headers['Content-Encoding'] == content_encoding
    assert json.loads(decompress(captured[0].get_data())) == _LARGE_BODY


@pytest.mark.parametrize(
    ('compression', 'content_encoding', 'decompress'),
    [
        pytest.param('gzip', 'gzip', gzip.decompress, id='gzip'),
        pytest.param('brotli', 'br', brotli.decompress, id='brotli'),
        pytest.param('zstd', 'zstd', zstd.decompress, id='zstd'),
    ],
)
async def test_configured_compression_reaches_the_wire_async(
    httpserver: HTTPServer,
    compression: HttpCompressionAlgorithm,
    content_encoding: str,
    decompress: Callable[[bytes], bytes],
) -> None:
    """Async variant of `test_configured_compression_reaches_the_wire_sync`."""
    captured: list[Request] = []
    httpserver.expect_request(_ITEMS_PATH, method='POST').respond_with_handler(_capture_body(captured))

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync(token='test_token', api_url=api_url, compression=compression)

    await client.dataset('test_dataset_id').push_items(_LARGE_BODY)

    assert len(captured) == 1
    assert captured[0].headers['Content-Encoding'] == content_encoding
    assert json.loads(decompress(captured[0].get_data())) == _LARGE_BODY

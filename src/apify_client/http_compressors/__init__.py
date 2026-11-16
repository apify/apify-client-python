from apify_client._utils.try_import import install_import_hook as _install_import_hook
from apify_client._utils.try_import import try_import as _try_import

# These imports have only mandatory dependencies, so they are imported directly.
from apify_client.http_compressors._base import HttpCompressor
from apify_client.http_compressors._gzip import GzipHttpCompressor
from apify_client.http_compressors._zstd_dependency import ZSTD_DEPENDENCY_NAME as _ZSTD_DEPENDENCY_NAME

_install_import_hook(__name__)

# `brotli` is an optional extra, so it's wrapped in try_import. Accessing `BrotliHttpCompressor`
# without the extra installed raises a clear ImportError instead of failing at package import time.
with _try_import(__name__, 'BrotliHttpCompressor', dependency_name='brotli', extra_name='brotli') as _brotli_import:
    from apify_client.http_compressors._brotli import BrotliHttpCompressor

# zstd comes from the standard library on Python 3.14 and newer, and from the `zstd` extra before that.
with _try_import(
    __name__, 'ZstdHttpCompressor', dependency_name=_ZSTD_DEPENDENCY_NAME, extra_name='zstd'
) as _zstd_import:
    from apify_client.http_compressors._zstd import ZstdHttpCompressor

__all__ = ['GzipHttpCompressor', 'HttpCompressor']
if _brotli_import.available:
    __all__ += ['BrotliHttpCompressor']
if _zstd_import.available:
    __all__ += ['ZstdHttpCompressor']

from apify_client._utils.try_import import install_import_hook as _install_import_hook
from apify_client._utils.try_import import try_import as _try_import

# These imports have only mandatory dependencies, so they are imported directly.
from apify_client.http_compressors._base import HttpCompressor
from apify_client.http_compressors._gzip import GzipHttpCompressor

_install_import_hook(__name__)

# `brotli` is an optional extra, so it's wrapped in try_import. Accessing `BrotliHttpCompressor`
# without the extra installed raises a clear ImportError instead of failing at package import time.
with _try_import(__name__, 'BrotliHttpCompressor'):
    from apify_client.http_compressors._brotli import BrotliHttpCompressor

__all__ = ['BrotliHttpCompressor', 'GzipHttpCompressor', 'HttpCompressor']

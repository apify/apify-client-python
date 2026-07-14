from apify_client._utils import install_import_hook, try_import
from apify_client.http_compressors._base import HttpCompressor
from apify_client.http_compressors._gzip import GzipHttpCompressor

# `brotli` is an optional extra. Defer the ImportError until
# BrotliHttpCompressor is actually accessed.
with try_import(__name__, 'BrotliHttpCompressor'):
    from apify_client.http_compressors._brotli import BrotliHttpCompressor

install_import_hook(__name__)

__all__ = ['BrotliHttpCompressor', 'GzipHttpCompressor', 'HttpCompressor']

from apify_client._utils.try_import import install_import_hook as _install_import_hook
from apify_client._utils.try_import import try_import as _try_import
from apify_client.http_clients._base import HttpClient, HttpClientAsync, HttpResponse
from apify_client.http_clients._impit import ImpitHttpClient, ImpitHttpClientAsync

_install_import_hook(__name__)

# The HTTPX clients depend on `httpx2`, installed by the optional `httpx` extra, so the import is wrapped in
# try_import. Accessing them without the extra installed raises a clear ImportError instead of failing at package
# import time.
with _try_import(
    __name__,
    'HttpxHttpClient',
    'HttpxHttpClientAsync',
    dependency_name='httpx2',
) as _httpx_import:
    from apify_client.http_clients._httpx import HttpxHttpClient, HttpxHttpClientAsync

__all__ = [
    'HttpClient',
    'HttpClientAsync',
    'HttpResponse',
    'ImpitHttpClient',
    'ImpitHttpClientAsync',
]

if _httpx_import.available:
    __all__ += [
        'HttpxHttpClient',
        'HttpxHttpClientAsync',
    ]

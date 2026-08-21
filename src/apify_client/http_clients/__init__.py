from apify_client._utils.try_import import install_import_hook as _install_import_hook
from apify_client._utils.try_import import try_import as _try_import
from apify_client.http_clients._base import HttpClient, HttpClientAsync, HttpResponse
from apify_client.http_clients._impit import ImpitHttpClient, ImpitHttpClientAsync

_install_import_hook(__name__)

# `httpx2` is an optional extra, so it's wrapped in try_import. Accessing the HTTPX2 clients
# without the extra installed raises a clear ImportError instead of failing at package import time.
with _try_import(
    __name__,
    'Httpx2HttpClient',
    'Httpx2HttpClientAsync',
    dependency_name='httpx2',
) as _httpx2_import:
    from apify_client.http_clients._httpx2 import Httpx2HttpClient, Httpx2HttpClientAsync

if _httpx2_import.available:
    __all__ = [
        'HttpClient',
        'HttpClientAsync',
        'HttpResponse',
        'Httpx2HttpClient',
        'Httpx2HttpClientAsync',
        'ImpitHttpClient',
        'ImpitHttpClientAsync',
    ]
else:
    __all__ = [
        'HttpClient',
        'HttpClientAsync',
        'HttpResponse',
        'ImpitHttpClient',
        'ImpitHttpClientAsync',
    ]

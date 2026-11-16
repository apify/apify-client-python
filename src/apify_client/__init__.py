from importlib import metadata

from ._apify_client import ApifyClient, ApifyClientAsync
from ._statistics import ClientStatistics

__version__ = metadata.version('apify-client')

__all__ = [
    'ApifyClient',
    'ApifyClientAsync',
    'ClientStatistics',
    '__version__',
]

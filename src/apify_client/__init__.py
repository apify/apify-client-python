from importlib import metadata

from ._apify_client import ApifyClient, ApifyClientAsync

__version__ = metadata.version('apify-client')

__all__ = ['ApifyClient', 'ApifyClientAsync', '__version__']

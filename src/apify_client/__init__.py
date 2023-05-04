from importlib import metadata

from .client import ApifyClient, ApifyClientAsync

__version__ = metadata.version('apify-client')

__all__ = ['ApifyClient', 'ApifyClientAsync', '__version__']

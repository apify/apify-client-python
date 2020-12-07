from typing import Any, Dict

from ..._http_client import _HTTPClient
from ..._utils import _to_safe_id


class BaseClient:
    """Base class for sub-clients."""
    def __init__(self, *, base_url: str, http_client: _HTTPClient, resource_id: str = None, resource_path: str, params: Dict = None) -> None:
        """Initializes the sub-client.

        Args:
            base_url: Base URL of the API server
            http_client: The _HTTPClient instance to be used in this client
            resource_id: ID of the manipulated resource, in case of a single-resource client
            resource_path: Path to the resource's endpoint on the API server
            params: Parameters to include in all requests from this client
        """
        self.base_url = base_url
        self.http_client = http_client
        self.params = params or {}
        self.resource_path = resource_path
        self.resource_id = resource_id
        self.url = f'{self.base_url}/{self.resource_path}'
        if self.resource_id is not None:
            self.safe_id = _to_safe_id(self.resource_id)
            self.url = f'{self.url}/{self.safe_id}'

    def _url(self, path: str = None) -> str:
        if path is not None:
            return f'{self.url}/{path}'
        return self.url

    def _params(self, **kwargs: Any) -> Dict:
        merged_params = self.params.copy()
        merged_params.update(kwargs)
        return merged_params

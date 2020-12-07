import io
import json
from typing import Any, Dict, Optional

from ..._errors import ApifyApiError
from ..._utils import _catch_not_found_or_throw, _parse_date_fields, _pluck_data
from ..base.resource_client import ResourceClient


class KeyValueStoreClient(ResourceClient):
    """Sub-client for manipulating a single key-value store."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes the KeyValueStoreClient."""
        super().__init__(*args, resource_path='key-value-stores', **kwargs)

    def get(self) -> Optional[Dict]:
        """Retrieves the key-value store.

        Returns:
            The retrieved key-value store
        """
        return self._get()

    def update(self, new_fields: Dict) -> Optional[Dict]:
        """Updates the key-value store with specified fields.

        Args:
            new_fields: The fields of the key-value store to update

        Returns:
            The updated key-value store
        """
        return self._update(new_fields)

    def delete(self) -> None:
        """Deletes the key-value store."""
        return self._delete()

    def list_keys(self, *, limit: int = None, exclusive_start_key: str = None, desc: bool = None) -> Any:
        """Lists the keys in the key-value store.

        Args:
            limit: TODO
            exclusive_start_key: TODO
            desc: TODO
        """
        request_params = self._params(
            limit=limit,
            exclusiveStartKey=exclusive_start_key,
            desc=desc,
        )

        response = self.http_client.call(
            url=self._url('keys'),
            method='GET',
            params=request_params,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    def get_record(self, key: str, *, buffer: bool = None, stream: bool = None) -> Optional[Dict]:
        """Retrieves the given record from the key-value store.

        Args:
            key: TODO
            buffer: TODO
            stream: TODO
        """
        try:
            response = self.http_client.call(
                url=self._url(f'records/{key}'),
                method='GET',
                params=self._params(),
                stream=stream,
            )

            result: Any = None
            # TODO verify this makes sense
            if buffer:
                result = response.content
            elif stream:
                response.raw.decode_content = True
                result = response.raw
            else:
                result = response.text

            return {
                'key': key,
                'value': result,
                'content_type': response.headers['content-type'],
            }

        except ApifyApiError as exc:
            _catch_not_found_or_throw(exc)

        return None

        # TODO force_buffer, naming?

    def set_record(self, key: str, value: Any, content_type: str = None) -> None:
        """Sets a value to the given record in the key-value store.

        Args:
            key: TODO
            value: TODO
            content_type: TODO
        """
        # TODO revisit this when it's decided whether we keep using the signed URL route or not

        headers = None

        if not content_type:
            if _is_file_or_bytes(value):
                content_type = 'application/octet-stream'
            elif isinstance(value, str):
                content_type = 'text/plain; charset=utf-8'
            else:
                content_type = 'application/json; charset=utf-8'

        if 'application/json' in content_type and not _is_file_or_bytes(value) and not isinstance(value, str):
            value = json.dumps(value, indent=2)

        headers = {'content-type': content_type}

        self.http_client.call(
            url=self._url(f'records/{key}'),
            method='PUT',
            params=self._params(),
            data=value,
            headers=headers,
        )

    def delete_record(self, key: str) -> None:
        """Deletes the specified record from the key-value store.

        Args:
            key: The key of the record which to delete
        """
        self.http_client.call(
            url=self._url(f'records/{key}'),
            method='DELETE',
            params=self._params(),
        )


def _is_file_or_bytes(value: Any) -> bool:
    return isinstance(value, (bytes, bytearray, io.IOBase))

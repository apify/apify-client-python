from typing import Any, Dict, Optional

from ..._errors import ApifyApiError
from ..._utils import _catch_not_found_or_throw, _encode_key_value_store_record_value, _parse_date_fields, _pluck_data
from ..base import ResourceClient


class KeyValueStoreClient(ResourceClient):
    """Sub-client for manipulating a single key-value store."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the KeyValueStoreClient."""
        resource_path = kwargs.pop('resource_path', 'key-value-stores')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> Optional[Dict]:
        """Retrieve the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/get-store

        Returns:
            dict, optional: The retrieved key-value store, or None if it does not exist
        """
        return self._get()

    def update(self, *, name: Optional[str] = None) -> Dict:
        """Update the key-value store with specified fields.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/update-store

        Args:
            name (str, optional): The new name for key-value store

        Returns:
            dict: The updated key-value store
        """
        updated_fields = {}
        if name is not None:
            updated_fields['name'] = name

        return self._update(updated_fields)

    def delete(self) -> None:
        """Delete the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/delete-store
        """
        return self._delete()

    def list_keys(self, *, limit: Optional[int] = None, exclusive_start_key: Optional[str] = None) -> Dict:
        """List the keys in the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/key-collection/get-list-of-keys

        Args:
            limit (int, optional): Number of keys to be returned. Maximum value is 1000
            exclusive_start_key (str, optional): All keys up to this one (including) are skipped from the result

        Returns:
            dict: The list of keys in the key-value store matching the given arguments
        """
        request_params = self._params(
            limit=limit,
            exclusiveStartKey=exclusive_start_key,
        )

        response = self.http_client.call(
            url=self._url('keys'),
            method='GET',
            params=request_params,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    def get_record(self, key: str, *, as_bytes: bool = False, as_file: bool = False) -> Optional[Dict]:
        """Retrieve the given record from the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record

        Args:
            key (str): Key of the record to retrieve
            as_bytes (bool, optional): Whether to retrieve the record as unparsed bytes, default False
            as_file (bool, optional): Whether to retrieve the record as a file-like object, default False

        Returns:
            dict, optional: The requested record, or None, if the record does not exist
        """
        try:
            # TODO revisit the as_bytes and as_file parameters when we decide how to rewrite the record-getting functions
            if as_bytes and as_file:
                raise ValueError('You cannot have both as_bytes and as_file set.')

            response = self.http_client.call(
                url=self._url(f'records/{key}'),
                method='GET',
                params=self._params(),
                stream=as_file,
                parse_response=(not as_bytes and not as_file),
            )

            return {
                'key': key,
                'value': response._maybe_parsed_body,  # type: ignore
                'content_type': response.headers['content-type'],
            }

        except ApifyApiError as exc:
            _catch_not_found_or_throw(exc)

        return None

    def set_record(self, key: str, value: Any, content_type: Optional[str] = None) -> None:
        """Set a value to the given record in the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/put-record

        Args:
            key (str): The key of the record to save the value to
            value (Any): The value to save into the record
            content_type (str, optional): The content type of the saved value
        """
        value, content_type = _encode_key_value_store_record_value(value, content_type)

        headers = {'content-type': content_type}

        self.http_client.call(
            url=self._url(f'records/{key}'),
            method='PUT',
            params=self._params(),
            data=value,
            headers=headers,
        )

    def delete_record(self, key: str) -> None:
        """Delete the specified record from the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/delete-record

        Args:
            key (str): The key of the record which to delete
        """
        self.http_client.call(
            url=self._url(f'records/{key}'),
            method='DELETE',
            params=self._params(),
        )

import warnings
from contextlib import asynccontextmanager, contextmanager
from typing import Any, AsyncIterator, Dict, Iterator, Optional

from ..._errors import ApifyApiError
from ..._utils import (
    _catch_not_found_or_throw,
    _encode_key_value_store_record_value,
    _filter_out_none_values_recursively,
    _make_async_docs,
    _parse_date_fields,
    _pluck_data,
)
from ..base import ResourceClient, ResourceClientAsync


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
        updated_fields = {
            'name': name,
        }

        return self._update(_filter_out_none_values_recursively(updated_fields))

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
            as_bytes (bool, optional): Deprecated, use `get_record_as_bytes()` instead. Whether to retrieve the record as raw bytes, default False
            as_file (bool, optional): Deprecated, use `stream_record()` instead. Whether to retrieve the record as a file-like object, default False

        Returns:
            dict, optional: The requested record, or None, if the record does not exist
        """
        try:
            if as_bytes and as_file:
                raise ValueError('You cannot have both as_bytes and as_file set.')

            if as_bytes:
                # We need to override and then restore the warnings filter so that the warning gets printed out,
                # Otherwise it would be silently swallowed
                with warnings.catch_warnings():
                    warnings.simplefilter('always')
                    warnings.warn(
                        '`KeyValueStoreClient.get_record(..., as_bytes=True)` is deprecated, use `KeyValueStoreClient.get_record_as_bytes()` instead.',  # noqa: E501
                        DeprecationWarning,
                        stacklevel=2,
                    )

                return self.get_record_as_bytes(key)

            if as_file:
                # We need to override and then restore the warnings filter so that the warning gets printed out,
                # Otherwise it would be silently swallowed
                with warnings.catch_warnings():
                    warnings.simplefilter('always')
                    warnings.warn(
                        '`KeyValueStoreClient.get_record(..., as_file=True)` is deprecated, use `KeyValueStoreClient.stream_record()` instead.',
                        DeprecationWarning,
                        stacklevel=2,
                    )
                return self.stream_record(key)  # type: ignore

            response = self.http_client.call(
                url=self._url(f'records/{key}'),
                method='GET',
                params=self._params(),
            )

            return {
                'key': key,
                'value': response._maybe_parsed_body,  # type: ignore
                'content_type': response.headers['content-type'],
            }

        except ApifyApiError as exc:
            _catch_not_found_or_throw(exc)

        return None

    def get_record_as_bytes(self, key: str) -> Optional[Dict]:
        """Retrieve the given record from the key-value store, without parsing it.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record

        Args:
            key (str): Key of the record to retrieve

        Returns:
            dict, optional: The requested record, or None, if the record does not exist
        """
        try:
            response = self.http_client.call(
                url=self._url(f'records/{key}'),
                method='GET',
                params=self._params(),
                parse_response=False,
            )

            return {
                'key': key,
                'value': response.content,
                'content_type': response.headers['content-type'],
            }

        except ApifyApiError as exc:
            _catch_not_found_or_throw(exc)

        return None

    @contextmanager
    def stream_record(self, key: str) -> Iterator[Optional[Dict]]:
        """Retrieve the given record from the key-value store, as a stream.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record

        Args:
            key (str): Key of the record to retrieve

        Returns:
            dict, optional: The requested record as a context-managed streaming Response, or None, if the record does not exist
        """
        response = None
        try:
            response = self.http_client.call(
                url=self._url(f'records/{key}'),
                method='GET',
                params=self._params(),
                parse_response=False,
                stream=True,
            )

            yield {
                'key': key,
                'value': response,
                'content_type': response.headers['content-type'],
            }

        except ApifyApiError as exc:
            _catch_not_found_or_throw(exc)
            yield None
        finally:
            if response:
                response.close()

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


class KeyValueStoreClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single key-value store."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the KeyValueStoreClientAsync."""
        resource_path = kwargs.pop('resource_path', 'key-value-stores')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    @_make_async_docs(src=KeyValueStoreClient.get)
    async def get(self) -> Optional[Dict]:
        return await self._get()

    @_make_async_docs(src=KeyValueStoreClient.update)
    async def update(self, *, name: Optional[str] = None) -> Dict:
        updated_fields = {
            'name': name,
        }

        return await self._update(_filter_out_none_values_recursively(updated_fields))

    @_make_async_docs(src=KeyValueStoreClient.delete)
    async def delete(self) -> None:
        return await self._delete()

    @_make_async_docs(src=KeyValueStoreClient.list_keys)
    async def list_keys(self, *, limit: Optional[int] = None, exclusive_start_key: Optional[str] = None) -> Dict:
        request_params = self._params(
            limit=limit,
            exclusiveStartKey=exclusive_start_key,
        )

        response = await self.http_client.call(
            url=self._url('keys'),
            method='GET',
            params=request_params,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    @_make_async_docs(src=KeyValueStoreClient.get_record)
    async def get_record(self, key: str) -> Optional[Dict]:
        try:
            response = await self.http_client.call(
                url=self._url(f'records/{key}'),
                method='GET',
                params=self._params(),
            )

            return {
                'key': key,
                'value': response._maybe_parsed_body,  # type: ignore
                'content_type': response.headers['content-type'],
            }

        except ApifyApiError as exc:
            _catch_not_found_or_throw(exc)

        return None

    @_make_async_docs(src=KeyValueStoreClient.get_record_as_bytes)
    async def get_record_as_bytes(self, key: str) -> Optional[Dict]:
        try:
            response = await self.http_client.call(
                url=self._url(f'records/{key}'),
                method='GET',
                params=self._params(),
                parse_response=False,
            )

            return {
                'key': key,
                'value': response.content,
                'content_type': response.headers['content-type'],
            }

        except ApifyApiError as exc:
            _catch_not_found_or_throw(exc)

        return None

    @asynccontextmanager
    @_make_async_docs(src=KeyValueStoreClient.stream_record)
    async def stream_record(self, key: str) -> AsyncIterator[Optional[Dict]]:
        response = None
        try:
            response = await self.http_client.call(
                url=self._url(f'records/{key}'),
                method='GET',
                params=self._params(),
                parse_response=False,
                stream=True,
            )

            yield {
                'key': key,
                'value': response,
                'content_type': response.headers['content-type'],
            }

        except ApifyApiError as exc:
            _catch_not_found_or_throw(exc)
            yield None
        finally:
            if response:
                await response.aclose()

    @_make_async_docs(src=KeyValueStoreClient.set_record)
    async def set_record(self, key: str, value: Any, content_type: Optional[str] = None) -> None:
        value, content_type = _encode_key_value_store_record_value(value, content_type)

        headers = {'content-type': content_type}

        await self.http_client.call(
            url=self._url(f'records/{key}'),
            method='PUT',
            params=self._params(),
            data=value,
            headers=headers,
        )

    @_make_async_docs(src=KeyValueStoreClient.delete_record)
    async def delete_record(self, key: str) -> None:
        await self.http_client.call(
            url=self._url(f'records/{key}'),
            method='DELETE',
            params=self._params(),
        )

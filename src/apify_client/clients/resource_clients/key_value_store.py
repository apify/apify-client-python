from __future__ import annotations

import warnings
from contextlib import asynccontextmanager, contextmanager
from typing import Any, AsyncIterator, Iterator

from apify_shared.utils import filter_out_none_values_recursively, ignore_docs, parse_date_fields

from apify_client._errors import ApifyApiError
from apify_client._utils import catch_not_found_or_throw, encode_key_value_store_record_value, pluck_data
from apify_client.clients.base import ResourceClient, ResourceClientAsync


class KeyValueStoreClient(ResourceClient):
    """Sub-client for manipulating a single key-value store."""

    @ignore_docs
    def __init__(self: KeyValueStoreClient, *args: Any, **kwargs: Any) -> None:
        """Initialize the KeyValueStoreClient."""
        resource_path = kwargs.pop('resource_path', 'key-value-stores')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self: KeyValueStoreClient) -> dict | None:
        """Retrieve the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/get-store

        Returns:
            dict, optional: The retrieved key-value store, or None if it does not exist
        """
        return self._get()

    def update(self: KeyValueStoreClient, *, name: str | None = None) -> dict:
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

        return self._update(filter_out_none_values_recursively(updated_fields))

    def delete(self: KeyValueStoreClient) -> None:
        """Delete the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/delete-store
        """
        return self._delete()

    def list_keys(self: KeyValueStoreClient, *, limit: int | None = None, exclusive_start_key: str | None = None) -> dict:
        """List the keys in the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/key-collection/get-list-of-keys

        Args:
            limit (int, optional): Number of keys to be returned. Maximum value is 1000
            exclusive_start_key (str, optional): All keys up to this one (including) are skipped from the result

        Returns:
            dict: The list of keys in the key-value store matching the given arguments
        """
        request_params = self._params(limit=limit, exclusiveStartKey=exclusive_start_key)

        response = self.http_client.call(
            url=self._url('keys'),
            method='GET',
            params=request_params,
        )

        return parse_date_fields(pluck_data(response.json()))

    def get_record(self: KeyValueStoreClient, key: str, *, as_bytes: bool = False, as_file: bool = False) -> dict | None:
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
                warnings.warn(
                    '`KeyValueStoreClient.get_record(..., as_bytes=True)` is deprecated, use `KeyValueStoreClient.get_record_as_bytes()` instead.',
                    DeprecationWarning,
                    stacklevel=2,
                )
                return self.get_record_as_bytes(key)

            if as_file:
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
                'value': response._maybe_parsed_body,  # type: ignore  # noqa: SLF001
                'content_type': response.headers['content-type'],
            }

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    def get_record_as_bytes(self: KeyValueStoreClient, key: str) -> dict | None:
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
            catch_not_found_or_throw(exc)

        return None

    @contextmanager
    def stream_record(self: KeyValueStoreClient, key: str) -> Iterator[dict | None]:
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
            catch_not_found_or_throw(exc)
            yield None
        finally:
            if response:
                response.close()

    def set_record(
        self: KeyValueStoreClient,
        key: str,
        value: Any,
        content_type: str | None = None,
    ) -> None:
        """Set a value to the given record in the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/put-record

        Args:
            key (str): The key of the record to save the value to
            value (Any): The value to save into the record
            content_type (str, optional): The content type of the saved value
        """
        value, content_type = encode_key_value_store_record_value(value, content_type)

        headers = {'content-type': content_type}

        self.http_client.call(
            url=self._url(f'records/{key}'),
            method='PUT',
            params=self._params(),
            data=value,
            headers=headers,
        )

    def delete_record(self: KeyValueStoreClient, key: str) -> None:
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

    @ignore_docs
    def __init__(self: KeyValueStoreClientAsync, *args: Any, **kwargs: Any) -> None:
        """Initialize the KeyValueStoreClientAsync."""
        resource_path = kwargs.pop('resource_path', 'key-value-stores')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self: KeyValueStoreClientAsync) -> dict | None:
        """Retrieve the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/get-store

        Returns:
            dict, optional: The retrieved key-value store, or None if it does not exist
        """
        return await self._get()

    async def update(self: KeyValueStoreClientAsync, *, name: str | None = None) -> dict:
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

        return await self._update(filter_out_none_values_recursively(updated_fields))

    async def delete(self: KeyValueStoreClientAsync) -> None:
        """Delete the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/delete-store
        """
        return await self._delete()

    async def list_keys(self: KeyValueStoreClientAsync, *, limit: int | None = None, exclusive_start_key: str | None = None) -> dict:
        """List the keys in the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/key-collection/get-list-of-keys

        Args:
            limit (int, optional): Number of keys to be returned. Maximum value is 1000
            exclusive_start_key (str, optional): All keys up to this one (including) are skipped from the result

        Returns:
            dict: The list of keys in the key-value store matching the given arguments
        """
        request_params = self._params(limit=limit, exclusiveStartKey=exclusive_start_key)

        response = await self.http_client.call(
            url=self._url('keys'),
            method='GET',
            params=request_params,
        )

        return parse_date_fields(pluck_data(response.json()))

    async def get_record(self: KeyValueStoreClientAsync, key: str) -> dict | None:
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
            response = await self.http_client.call(
                url=self._url(f'records/{key}'),
                method='GET',
                params=self._params(),
            )

            return {
                'key': key,
                'value': response._maybe_parsed_body,  # type: ignore  # noqa: SLF001
                'content_type': response.headers['content-type'],
            }

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    async def get_record_as_bytes(self: KeyValueStoreClientAsync, key: str) -> dict | None:
        """Retrieve the given record from the key-value store, without parsing it.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record

        Args:
            key (str): Key of the record to retrieve

        Returns:
            dict, optional: The requested record, or None, if the record does not exist
        """
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
            catch_not_found_or_throw(exc)

        return None

    @asynccontextmanager
    async def stream_record(self: KeyValueStoreClientAsync, key: str) -> AsyncIterator[dict | None]:
        """Retrieve the given record from the key-value store, as a stream.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record

        Args:
            key (str): Key of the record to retrieve

        Returns:
            dict, optional: The requested record as a context-managed streaming Response, or None, if the record does not exist
        """
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
            catch_not_found_or_throw(exc)
            yield None
        finally:
            if response:
                await response.aclose()

    async def set_record(
        self: KeyValueStoreClientAsync,
        key: str,
        value: Any,
        content_type: str | None = None,
    ) -> None:
        """Set a value to the given record in the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/put-record

        Args:
            key (str): The key of the record to save the value to
            value (Any): The value to save into the record
            content_type (str, optional): The content type of the saved value
        """
        value, content_type = encode_key_value_store_record_value(value, content_type)

        headers = {'content-type': content_type}

        await self.http_client.call(
            url=self._url(f'records/{key}'),
            method='PUT',
            params=self._params(),
            data=value,
            headers=headers,
        )

    async def delete_record(self: KeyValueStoreClientAsync, key: str) -> None:
        """Delete the specified record from the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/delete-record

        Args:
            key (str): The key of the record which to delete
        """
        await self.http_client.call(
            url=self._url(f'records/{key}'),
            method='DELETE',
            params=self._params(),
        )

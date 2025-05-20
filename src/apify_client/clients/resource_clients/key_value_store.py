from __future__ import annotations

import warnings
from contextlib import asynccontextmanager, contextmanager
from typing import TYPE_CHECKING, Any

from apify_shared.utils import filter_out_none_values_recursively, ignore_docs, parse_date_fields

from apify_client._errors import ApifyApiError
from apify_client._utils import catch_not_found_or_throw, encode_key_value_store_record_value, pluck_data
from apify_client.clients.base import ResourceClient, ResourceClientAsync

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from apify_shared.consts import StorageGeneralAccess

_SMALL_TIMEOUT = 5  # For fast and common actions. Suitable for idempotent actions.
_MEDIUM_TIMEOUT = 30  # For actions that may take longer.


class KeyValueStoreClient(ResourceClient):
    """Sub-client for manipulating a single key-value store."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'key-value-stores')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> dict | None:
        """Retrieve the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/get-store

        Returns:
            The retrieved key-value store, or None if it does not exist.
        """
        return self._get(timeout_secs=_SMALL_TIMEOUT)

    def update(self, *, name: str | None = None, general_access: StorageGeneralAccess | None = None) -> dict:
        """Update the key-value store with specified fields.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/update-store

        Args:
            name: The new name for key-value store.
            general_access: Determines how others can access the key-value store.

        Returns:
            The updated key-value store.
        """
        updated_fields = {
            'name': name,
            'generalAccess': general_access,
        }

        return self._update(filter_out_none_values_recursively(updated_fields))

    def delete(self) -> None:
        """Delete the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/delete-store
        """
        return self._delete(timeout_secs=_SMALL_TIMEOUT)

    def list_keys(
        self,
        *,
        limit: int | None = None,
        exclusive_start_key: str | None = None,
        collection: str | None = None,
        prefix: str | None = None,
    ) -> dict:
        """List the keys in the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/key-collection/get-list-of-keys

        Args:
            limit: Number of keys to be returned. Maximum value is 1000.
            exclusive_start_key: All keys up to this one (including) are skipped from the result.
            collection: The name of the collection in store schema to list keys from.
            prefix: The prefix of the keys to be listed.

        Returns:
            The list of keys in the key-value store matching the given arguments.
        """
        request_params = self._params(
            limit=limit,
            exclusiveStartKey=exclusive_start_key,
            collection=collection,
            prefix=prefix,
        )

        response = self.http_client.call(
            url=self._url('keys'),
            method='GET',
            params=request_params,
            timeout_secs=_MEDIUM_TIMEOUT,
        )

        return parse_date_fields(pluck_data(response.json()))

    def get_record(self, key: str, *, as_bytes: bool = False, as_file: bool = False) -> dict | None:
        """Retrieve the given record from the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record

        Args:
            key: Key of the record to retrieve.
            as_bytes: Deprecated, use `get_record_as_bytes()` instead. Whether to retrieve the record as raw bytes,
                default False.
            as_file: Deprecated, use `stream_record()` instead. Whether to retrieve the record as a file-like object,
                default False.

        Returns:
            The requested record, or None, if the record does not exist.
        """
        try:
            if as_bytes and as_file:
                raise ValueError('You cannot have both as_bytes and as_file set.')

            if as_bytes:
                warnings.warn(
                    '`KeyValueStoreClient.get_record(..., as_bytes=True)` is deprecated, '
                    'use `KeyValueStoreClient.get_record_as_bytes()` instead.',
                    DeprecationWarning,
                    stacklevel=2,
                )
                return self.get_record_as_bytes(key)

            if as_file:
                warnings.warn(
                    '`KeyValueStoreClient.get_record(..., as_file=True)` is deprecated, '
                    'use `KeyValueStoreClient.stream_record()` instead.',
                    DeprecationWarning,
                    stacklevel=2,
                )
                return self.stream_record(key)  # type: ignore[return-value]

            response = self.http_client.call(
                url=self._url(f'records/{key}'),
                method='GET',
                params=self._params(),
            )

            return {
                'key': key,
                'value': response._maybe_parsed_body,  # type: ignore[attr-defined]  # noqa: SLF001
                'content_type': response.headers['content-type'],
            }

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    def get_record_as_bytes(self, key: str) -> dict | None:
        """Retrieve the given record from the key-value store, without parsing it.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record

        Args:
            key: Key of the record to retrieve.

        Returns:
            The requested record, or None, if the record does not exist.
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
    def stream_record(self, key: str) -> Iterator[dict | None]:
        """Retrieve the given record from the key-value store, as a stream.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record

        Args:
            key: Key of the record to retrieve.

        Returns:
            The requested record as a context-managed streaming Response, or None, if the record does not exist.
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
        self,
        key: str,
        value: Any,
        content_type: str | None = None,
    ) -> None:
        """Set a value to the given record in the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/put-record

        Args:
            key: The key of the record to save the value to.
            value: The value to save into the record.
            content_type: The content type of the saved value.
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

    def delete_record(self, key: str) -> None:
        """Delete the specified record from the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/delete-record

        Args:
            key: The key of the record which to delete.
        """
        self.http_client.call(
            url=self._url(f'records/{key}'),
            method='DELETE',
            params=self._params(),
            timeout_secs=_SMALL_TIMEOUT,
        )


class KeyValueStoreClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single key-value store."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'key-value-stores')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self) -> dict | None:
        """Retrieve the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/get-store

        Returns:
            The retrieved key-value store, or None if it does not exist.
        """
        return await self._get(timeout_secs=_SMALL_TIMEOUT)

    async def update(self, *, name: str | None = None, general_access: StorageGeneralAccess | None = None) -> dict:
        """Update the key-value store with specified fields.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/update-store

        Args:
            name: The new name for key-value store.
            general_access: Determines how others can access the key-value store.

        Returns:
            The updated key-value store.
        """
        updated_fields = {
            'name': name,
            'generalAccess': general_access,
        }

        return await self._update(filter_out_none_values_recursively(updated_fields))

    async def delete(self) -> None:
        """Delete the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/delete-store
        """
        return await self._delete(timeout_secs=_SMALL_TIMEOUT)

    async def list_keys(
        self,
        *,
        limit: int | None = None,
        exclusive_start_key: str | None = None,
        collection: str | None = None,
        prefix: str | None = None,
    ) -> dict:
        """List the keys in the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/key-collection/get-list-of-keys

        Args:
            limit: Number of keys to be returned. Maximum value is 1000.
            exclusive_start_key: All keys up to this one (including) are skipped from the result.
            collection: The name of the collection in store schema to list keys from.
            prefix: The prefix of the keys to be listed.

        Returns:
            The list of keys in the key-value store matching the given arguments.
        """
        request_params = self._params(
            limit=limit,
            exclusiveStartKey=exclusive_start_key,
            collection=collection,
            prefix=prefix,
        )

        response = await self.http_client.call(
            url=self._url('keys'),
            method='GET',
            params=request_params,
            timeout_secs=_MEDIUM_TIMEOUT,
        )

        return parse_date_fields(pluck_data(response.json()))

    async def get_record(self, key: str) -> dict | None:
        """Retrieve the given record from the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record

        Args:
            key: Key of the record to retrieve.
            as_bytes: Deprecated, use `get_record_as_bytes()` instead. Whether to retrieve the record as raw bytes,
                default False.
            as_file: Deprecated, use `stream_record()` instead. Whether to retrieve the record as a file-like object,
                default False.

        Returns:
            The requested record, or None, if the record does not exist.
        """
        try:
            response = await self.http_client.call(
                url=self._url(f'records/{key}'),
                method='GET',
                params=self._params(),
            )

            return {
                'key': key,
                'value': response._maybe_parsed_body,  # type: ignore[attr-defined]  # noqa: SLF001
                'content_type': response.headers['content-type'],
            }

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    async def get_record_as_bytes(self, key: str) -> dict | None:
        """Retrieve the given record from the key-value store, without parsing it.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record

        Args:
            key: Key of the record to retrieve.

        Returns:
            The requested record, or None, if the record does not exist.
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
    async def stream_record(self, key: str) -> AsyncIterator[dict | None]:
        """Retrieve the given record from the key-value store, as a stream.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record

        Args:
            key: Key of the record to retrieve.

        Returns:
            The requested record as a context-managed streaming Response, or None, if the record does not exist.
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
        self,
        key: str,
        value: Any,
        content_type: str | None = None,
    ) -> None:
        """Set a value to the given record in the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/put-record

        Args:
            key: The key of the record to save the value to.
            value: The value to save into the record.
            content_type: The content type of the saved value.
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

    async def delete_record(self, key: str) -> None:
        """Delete the specified record from the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/delete-record

        Args:
            key: The key of the record which to delete.
        """
        await self.http_client.call(
            url=self._url(f'records/{key}'),
            method='DELETE',
            params=self._params(),
            timeout_secs=_SMALL_TIMEOUT,
        )

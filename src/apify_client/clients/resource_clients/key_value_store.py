from __future__ import annotations

from contextlib import asynccontextmanager, contextmanager
from http import HTTPStatus
from typing import TYPE_CHECKING, Any
from urllib.parse import urlencode, urlparse, urlunparse

from apify_shared.utils import create_hmac_signature, create_storage_content_signature

from apify_client._utils import (
    catch_not_found_or_throw,
    encode_key_value_store_record_value,
    filter_out_none_values_recursively,
    maybe_parse_response,
    parse_date_fields,
    pluck_data,
)
from apify_client.clients.base import ResourceClient, ResourceClientAsync
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from apify_shared.consts import StorageGeneralAccess

_SMALL_TIMEOUT = 5  # For fast and common actions. Suitable for idempotent actions.
_MEDIUM_TIMEOUT = 30  # For actions that may take longer.


class KeyValueStoreClient(ResourceClient):
    """Sub-client for manipulating a single key-value store."""

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
        signature: str | None = None,
    ) -> dict:
        """List the keys in the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/key-collection/get-list-of-keys

        Args:
            limit: Number of keys to be returned. Maximum value is 1000.
            exclusive_start_key: All keys up to this one (including) are skipped from the result.
            collection: The name of the collection in store schema to list keys from.
            prefix: The prefix of the keys to be listed.
            signature: Signature used to access the items.

        Returns:
            The list of keys in the key-value store matching the given arguments.
        """
        request_params = self._params(
            limit=limit,
            exclusiveStartKey=exclusive_start_key,
            collection=collection,
            prefix=prefix,
            signature=signature,
        )

        response = self.http_client.call(
            url=self._url('keys'),
            method='GET',
            params=request_params,
            timeout_secs=_MEDIUM_TIMEOUT,
        )

        return parse_date_fields(pluck_data(response.json()))

    def get_record(self, key: str, signature: str | None = None) -> dict | None:
        """Retrieve the given record from the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record

        Args:
            key: Key of the record to retrieve.
            signature: Signature used to access the items.

        Returns:
            The requested record, or None, if the record does not exist.
        """
        try:
            response = self.http_client.call(
                url=self._url(f'records/{key}'),
                method='GET',
                params=self._params(signature=signature),
            )

            return {
                'key': key,
                'value': maybe_parse_response(response),
                'content_type': response.headers['content-type'],
            }

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    def record_exists(self, key: str) -> bool:
        """Check if given record is present in the key-value store.

        https://docs.apify.com/api/v2/key-value-store-record-head

        Args:
            key: Key of the record to check.

        Returns:
            True if the record exists, False otherwise.
        """
        try:
            response = self.http_client.call(
                url=self._url(f'records/{key}'),
                method='HEAD',
                params=self._params(),
            )
        except ApifyApiError as exc:
            if exc.status_code == HTTPStatus.NOT_FOUND:
                return False

            raise

        return response.status_code == HTTPStatus.OK

    def get_record_as_bytes(self, key: str, signature: str | None = None) -> dict | None:
        """Retrieve the given record from the key-value store, without parsing it.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record

        Args:
            key: Key of the record to retrieve.
            signature: Signature used to access the items.

        Returns:
            The requested record, or None, if the record does not exist.
        """
        try:
            response = self.http_client.call(
                url=self._url(f'records/{key}'),
                method='GET',
                params=self._params(signature=signature),
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
    def stream_record(self, key: str, signature: str | None = None) -> Iterator[dict | None]:
        """Retrieve the given record from the key-value store, as a stream.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record

        Args:
            key: Key of the record to retrieve.
            signature: Signature used to access the items.

        Returns:
            The requested record as a context-managed streaming Response, or None, if the record does not exist.
        """
        response = None
        try:
            response = self.http_client.call(
                url=self._url(f'records/{key}'),
                method='GET',
                params=self._params(signature=signature),
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

    def get_record_public_url(self, key: str) -> str:
        """Generate a URL that can be used to access key-value store record.

        If the client has permission to access the key-value store's URL signing key, the URL will include a signature
        to verify its authenticity.

        Args:
            key: The key for which the URL should be generated.

        Returns:
            A public URL that can be used to access the value of the given key in the KVS.
        """
        if self.resource_id is None:
            raise ValueError('resource_id cannot be None when generating a public URL')

        metadata = self.get()

        request_params = self._params()

        if metadata and 'urlSigningSecretKey' in metadata:
            request_params['signature'] = create_hmac_signature(metadata['urlSigningSecretKey'], key)

        key_public_url = urlparse(self._url(f'records/{key}', public=True))
        filtered_params = {k: v for k, v in request_params.items() if v is not None}

        if filtered_params:
            key_public_url = key_public_url._replace(query=urlencode(filtered_params))

        return urlunparse(key_public_url)

    def create_keys_public_url(
        self,
        *,
        limit: int | None = None,
        exclusive_start_key: str | None = None,
        collection: str | None = None,
        prefix: str | None = None,
        expires_in_secs: int | None = None,
    ) -> str:
        """Generate a URL that can be used to access key-value store keys.

        If the client has permission to access the key-value store's URL signing key,
        the URL will include a signature to verify its authenticity.

        You can optionally control how long the signed URL should be valid using the `expires_in_secs` option.
        This value sets the expiration duration in seconds from the time the URL is generated.
        If not provided, the URL will not expire.

        Any other options (like `limit` or `prefix`) will be included as query parameters in the URL.

        Returns:
            The public key-value store keys URL.
        """
        metadata = self.get()

        request_params = self._params(
            limit=limit,
            exclusiveStartKey=exclusive_start_key,
            collection=collection,
            prefix=prefix,
        )

        if metadata and 'urlSigningSecretKey' in metadata:
            signature = create_storage_content_signature(
                resource_id=metadata['id'],
                url_signing_secret_key=metadata['urlSigningSecretKey'],
                expires_in_millis=expires_in_secs * 1000 if expires_in_secs is not None else None,
            )
            request_params['signature'] = signature

        keys_public_url = urlparse(self._url('keys', public=True))

        filtered_params = {k: v for k, v in request_params.items() if v is not None}
        if filtered_params:
            keys_public_url = keys_public_url._replace(query=urlencode(filtered_params))

        return urlunparse(keys_public_url)


class KeyValueStoreClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single key-value store."""

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
        signature: str | None = None,
    ) -> dict:
        """List the keys in the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/key-collection/get-list-of-keys

        Args:
            limit: Number of keys to be returned. Maximum value is 1000.
            exclusive_start_key: All keys up to this one (including) are skipped from the result.
            collection: The name of the collection in store schema to list keys from.
            prefix: The prefix of the keys to be listed.
            signature: Signature used to access the items.

        Returns:
            The list of keys in the key-value store matching the given arguments.
        """
        request_params = self._params(
            limit=limit,
            exclusiveStartKey=exclusive_start_key,
            collection=collection,
            prefix=prefix,
            signature=signature,
        )

        response = await self.http_client.call(
            url=self._url('keys'),
            method='GET',
            params=request_params,
            timeout_secs=_MEDIUM_TIMEOUT,
        )

        return parse_date_fields(pluck_data(response.json()))

    async def get_record(self, key: str, signature: str | None = None) -> dict | None:
        """Retrieve the given record from the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record

        Args:
            key: Key of the record to retrieve.
            signature: Signature used to access the items.

        Returns:
            The requested record, or None, if the record does not exist.
        """
        try:
            response = await self.http_client.call(
                url=self._url(f'records/{key}'),
                method='GET',
                params=self._params(signature=signature),
            )

            return {
                'key': key,
                'value': maybe_parse_response(response),
                'content_type': response.headers['content-type'],
            }

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    async def record_exists(self, key: str) -> bool:
        """Check if given record is present in the key-value store.

        https://docs.apify.com/api/v2/key-value-store-record-head

        Args:
            key: Key of the record to check.

        Returns:
            True if the record exists, False otherwise.
        """
        try:
            response = await self.http_client.call(
                url=self._url(f'records/{key}'),
                method='HEAD',
                params=self._params(),
            )
        except ApifyApiError as exc:
            if exc.status_code == HTTPStatus.NOT_FOUND:
                return False

            raise

        return response.status_code == HTTPStatus.OK

    async def get_record_as_bytes(self, key: str, signature: str | None = None) -> dict | None:
        """Retrieve the given record from the key-value store, without parsing it.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record

        Args:
            key: Key of the record to retrieve.
            signature: Signature used to access the items.

        Returns:
            The requested record, or None, if the record does not exist.
        """
        try:
            response = await self.http_client.call(
                url=self._url(f'records/{key}'),
                method='GET',
                params=self._params(signature=signature),
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
    async def stream_record(self, key: str, signature: str | None = None) -> AsyncIterator[dict | None]:
        """Retrieve the given record from the key-value store, as a stream.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record

        Args:
            key: Key of the record to retrieve.
            signature: Signature used to access the items.

        Returns:
            The requested record as a context-managed streaming Response, or None, if the record does not exist.
        """
        response = None
        try:
            response = await self.http_client.call(
                url=self._url(f'records/{key}'),
                method='GET',
                params=self._params(signature=signature),
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

    async def get_record_public_url(self, key: str) -> str:
        """Generate a URL that can be used to access key-value store record.

        If the client has permission to access the key-value store's URL signing key, the URL will include a signature
        to verify its authenticity.

        Args:
            key: The key for which the URL should be generated.

        Returns:
            A public URL that can be used to access the value of the given key in the KVS.
        """
        if self.resource_id is None:
            raise ValueError('resource_id cannot be None when generating a public URL')

        metadata = await self.get()

        request_params = self._params()

        if metadata and 'urlSigningSecretKey' in metadata:
            request_params['signature'] = create_hmac_signature(metadata['urlSigningSecretKey'], key)

        key_public_url = urlparse(self._url(f'records/{key}', public=True))
        filtered_params = {k: v for k, v in request_params.items() if v is not None}

        if filtered_params:
            key_public_url = key_public_url._replace(query=urlencode(filtered_params))

        return urlunparse(key_public_url)

    async def create_keys_public_url(
        self,
        *,
        limit: int | None = None,
        exclusive_start_key: str | None = None,
        collection: str | None = None,
        prefix: str | None = None,
        expires_in_secs: int | None = None,
    ) -> str:
        """Generate a URL that can be used to access key-value store keys.

        If the client has permission to access the key-value store's URL signing key,
        the URL will include a signature to verify its authenticity.

        You can optionally control how long the signed URL should be valid using the `expires_in_secs` option.
        This value sets the expiration duration in seconds from the time the URL is generated.
        If not provided, the URL will not expire.

        Any other options (like `limit` or `prefix`) will be included as query parameters in the URL.

        Returns:
            The public key-value store keys URL.
        """
        metadata = await self.get()

        keys_public_url = urlparse(self._url('keys'))

        request_params = self._params(
            limit=limit,
            exclusiveStartKey=exclusive_start_key,
            collection=collection,
            prefix=prefix,
        )

        if metadata and 'urlSigningSecretKey' in metadata:
            signature = create_storage_content_signature(
                resource_id=metadata['id'],
                url_signing_secret_key=metadata['urlSigningSecretKey'],
                expires_in_millis=expires_in_secs * 1000 if expires_in_secs is not None else None,
            )
            request_params['signature'] = signature

        keys_public_url = urlparse(self._url('keys', public=True))
        filtered_params = {k: v for k, v in request_params.items() if v is not None}
        if filtered_params:
            keys_public_url = keys_public_url._replace(query=urlencode(filtered_params))

        return urlunparse(keys_public_url)

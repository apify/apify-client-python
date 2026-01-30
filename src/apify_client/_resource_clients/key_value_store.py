from __future__ import annotations

import re
from contextlib import asynccontextmanager, contextmanager
from http import HTTPStatus
from typing import TYPE_CHECKING, Any
from urllib.parse import urlencode, urlparse, urlunparse

from apify_client._consts import FAST_OPERATION_TIMEOUT, STANDARD_OPERATION_TIMEOUT
from apify_client._models import (
    GetKeyValueStoreResponse,
    GetListOfKeysResponse,
    KeyValueStore,
    KeyValueStoreKey,
    ListOfKeys,
)
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import (
    catch_not_found_or_throw,
    create_hmac_signature,
    create_storage_content_signature,
    encode_key_value_store_record_value,
    filter_none_values,
    response_to_dict,
)
from apify_client.errors import ApifyApiError, InvalidResponseBodyError

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator
    from datetime import timedelta

    from impit import Response

    from apify_client._models import GeneralAccessEnum


def _parse_get_record_response(response: Response) -> Any:
    """Parse an HTTP response based on its content type.

    Args:
        response: The HTTP response to parse.

    Returns:
        Parsed response data (JSON dict/list, text string, or raw bytes).

    Raises:
        InvalidResponseBodyError: If the response body cannot be parsed.
    """
    if response.status_code == HTTPStatus.NO_CONTENT:
        return None

    content_type = ''
    if 'content-type' in response.headers:
        content_type = response.headers['content-type'].split(';')[0].strip()

    try:
        if re.search(r'^application/json', content_type, flags=re.IGNORECASE):
            response_data = response.json()
        elif re.search(r'^application/.*xml$', content_type, flags=re.IGNORECASE) or re.search(
            r'^text/', content_type, flags=re.IGNORECASE
        ):
            response_data = response.text
        else:
            response_data = response.content
    except ValueError as err:
        raise InvalidResponseBodyError(response) from err
    else:
        return response_data


class KeyValueStoreClient(ResourceClient):
    """Sub-client for manipulating a single key-value store."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'key-value-stores')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> KeyValueStore | None:
        """Retrieve the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/get-store

        Returns:
            The retrieved key-value store, or None if it does not exist.
        """
        try:
            response = self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(),
                timeout=FAST_OPERATION_TIMEOUT,
            )
            result = response_to_dict(response)
            return GetKeyValueStoreResponse.model_validate(result).data
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            return None

    def update(self, *, name: str | None = None, general_access: GeneralAccessEnum | None = None) -> KeyValueStore:
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
        cleaned = filter_none_values(updated_fields)

        response = self._http_client.call(
            url=self._build_url(),
            method='PUT',
            params=self._build_params(),
            json=cleaned,
        )
        result = response_to_dict(response)
        return GetKeyValueStoreResponse.model_validate(result).data

    def delete(self) -> None:
        """Delete the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/delete-store
        """
        try:
            self._http_client.call(
                url=self._build_url(),
                method='DELETE',
                params=self._build_params(),
                timeout=FAST_OPERATION_TIMEOUT,
            )
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

    def list_keys(
        self,
        *,
        limit: int | None = None,
        exclusive_start_key: str | None = None,
        collection: str | None = None,
        prefix: str | None = None,
        signature: str | None = None,
    ) -> ListOfKeys:
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
        request_params = self._build_params(
            limit=limit,
            exclusiveStartKey=exclusive_start_key,
            collection=collection,
            prefix=prefix,
            signature=signature,
        )

        response = self._http_client.call(
            url=self._build_url('keys'),
            method='GET',
            params=request_params,
            timeout=STANDARD_OPERATION_TIMEOUT,
        )

        result = response.json()
        return GetListOfKeysResponse.model_validate(result).data

    def iterate_keys(
        self,
        *,
        limit: int | None = None,
        collection: str | None = None,
        prefix: str | None = None,
        signature: str | None = None,
    ) -> Iterator[KeyValueStoreKey]:
        """Iterate over the keys in the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/key-collection/get-list-of-keys

        Args:
            limit: Maximum number of keys to return. By default there is no limit.
            collection: The name of the collection in store schema to list keys from.
            prefix: The prefix of the keys to be listed.
            signature: Signature used to access the items.

        Yields:
            A key from the key-value store.
        """
        cache_size = 1000
        read_keys = 0
        exclusive_start_key: str | None = None

        while True:
            effective_limit = cache_size
            if limit is not None:
                if read_keys == limit:
                    break
                effective_limit = min(cache_size, limit - read_keys)

            current_keys_page = self.list_keys(
                limit=effective_limit,
                exclusive_start_key=exclusive_start_key,
                collection=collection,
                prefix=prefix,
                signature=signature,
            )

            yield from current_keys_page.items

            read_keys += len(current_keys_page.items)

            if not current_keys_page.is_truncated:
                break

            exclusive_start_key = current_keys_page.next_exclusive_start_key

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
            response = self._http_client.call(
                url=self._build_url(f'records/{key}'),
                method='GET',
                params=self._build_params(signature=signature, attachment=True),
            )

            return {
                'key': key,
                'value': _parse_get_record_response(response),
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
            response = self._http_client.call(
                url=self._build_url(f'records/{key}'),
                method='HEAD',
                params=self._build_params(),
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
            response = self._http_client.call(
                url=self._build_url(f'records/{key}'),
                method='GET',
                params=self._build_params(signature=signature, attachment=True),
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
            response = self._http_client.call(
                url=self._build_url(f'records/{key}'),
                method='GET',
                params=self._build_params(signature=signature, attachment=True),
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

        self._http_client.call(
            url=self._build_url(f'records/{key}'),
            method='PUT',
            params=self._build_params(),
            data=value,
            headers=headers,
        )

    def delete_record(self, key: str) -> None:
        """Delete the specified record from the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/delete-record

        Args:
            key: The key of the record which to delete.
        """
        self._http_client.call(
            url=self._build_url(f'records/{key}'),
            method='DELETE',
            params=self._build_params(),
            timeout=FAST_OPERATION_TIMEOUT,
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
        if self._resource_id is None:
            raise ValueError('resource_id cannot be None when generating a public URL')

        metadata = self.get()

        request_params = self._build_params()

        if metadata and metadata.url_signing_secret_key:
            request_params['signature'] = create_hmac_signature(metadata.url_signing_secret_key, key)

        key_public_url = urlparse(self._build_url(f'records/{key}', public=True))
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
        expires_in: timedelta | None = None,
    ) -> str:
        """Generate a URL that can be used to access key-value store keys.

        If the client has permission to access the key-value store's URL signing key,
        the URL will include a signature to verify its authenticity.

        You can optionally control how long the signed URL should be valid using the `expires_in` option.
        This value sets the expiration duration from the time the URL is generated.
        If not provided, the URL will not expire.

        Any other options (like `limit` or `prefix`) will be included as query parameters in the URL.

        Returns:
            The public key-value store keys URL.
        """
        metadata = self.get()

        request_params = self._build_params(
            limit=limit,
            exclusiveStartKey=exclusive_start_key,
            collection=collection,
            prefix=prefix,
        )

        if metadata and metadata.url_signing_secret_key:
            signature = create_storage_content_signature(
                resource_id=metadata.id,
                url_signing_secret_key=metadata.url_signing_secret_key,
                expires_in=expires_in,
            )
            request_params['signature'] = signature

        keys_public_url = urlparse(self._build_url('keys', public=True))

        filtered_params = {k: v for k, v in request_params.items() if v is not None}
        if filtered_params:
            keys_public_url = keys_public_url._replace(query=urlencode(filtered_params))

        return urlunparse(keys_public_url)


class KeyValueStoreClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single key-value store."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'key-value-stores')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self) -> KeyValueStore | None:
        """Retrieve the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/get-store

        Returns:
            The retrieved key-value store, or None if it does not exist.
        """
        try:
            response = await self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(),
                timeout=FAST_OPERATION_TIMEOUT,
            )
            result = response_to_dict(response)
            return GetKeyValueStoreResponse.model_validate(result).data
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            return None

    async def update(
        self,
        *,
        name: str | None = None,
        general_access: GeneralAccessEnum | None = None,
    ) -> KeyValueStore:
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
        cleaned = filter_none_values(updated_fields)

        response = await self._http_client.call(
            url=self._build_url(),
            method='PUT',
            params=self._build_params(),
            json=cleaned,
        )
        result = response_to_dict(response)
        return GetKeyValueStoreResponse.model_validate(result).data

    async def delete(self) -> None:
        """Delete the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/delete-store
        """
        try:
            await self._http_client.call(
                url=self._build_url(),
                method='DELETE',
                params=self._build_params(),
                timeout=FAST_OPERATION_TIMEOUT,
            )
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

    async def list_keys(
        self,
        *,
        limit: int | None = None,
        exclusive_start_key: str | None = None,
        collection: str | None = None,
        prefix: str | None = None,
        signature: str | None = None,
    ) -> ListOfKeys:
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
        request_params = self._build_params(
            limit=limit,
            exclusiveStartKey=exclusive_start_key,
            collection=collection,
            prefix=prefix,
            signature=signature,
        )

        response = await self._http_client.call(
            url=self._build_url('keys'),
            method='GET',
            params=request_params,
            timeout=STANDARD_OPERATION_TIMEOUT,
        )

        result = response.json()
        return GetListOfKeysResponse.model_validate(result).data

    async def iterate_keys(
        self,
        *,
        limit: int | None = None,
        collection: str | None = None,
        prefix: str | None = None,
        signature: str | None = None,
    ) -> AsyncIterator[KeyValueStoreKey]:
        """Iterate over the keys in the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/key-collection/get-list-of-keys

        Args:
            limit: Maximum number of keys to return. By default there is no limit.
            collection: The name of the collection in store schema to list keys from.
            prefix: The prefix of the keys to be listed.
            signature: Signature used to access the items.

        Yields:
            A key from the key-value store.
        """
        cache_size = 1000
        read_keys = 0
        exclusive_start_key: str | None = None

        while True:
            effective_limit = cache_size
            if limit is not None:
                if read_keys == limit:
                    break
                effective_limit = min(cache_size, limit - read_keys)

            current_keys_page = await self.list_keys(
                limit=effective_limit,
                exclusive_start_key=exclusive_start_key,
                collection=collection,
                prefix=prefix,
                signature=signature,
            )

            for key in current_keys_page.items:
                yield key

            read_keys += len(current_keys_page.items)

            if not current_keys_page.is_truncated:
                break

            exclusive_start_key = current_keys_page.next_exclusive_start_key

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
            response = await self._http_client.call(
                url=self._build_url(f'records/{key}'),
                method='GET',
                params=self._build_params(signature=signature, attachment=True),
            )

            return {
                'key': key,
                'value': _parse_get_record_response(response),
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
            response = await self._http_client.call(
                url=self._build_url(f'records/{key}'),
                method='HEAD',
                params=self._build_params(),
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
            response = await self._http_client.call(
                url=self._build_url(f'records/{key}'),
                method='GET',
                params=self._build_params(signature=signature, attachment=True),
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
            response = await self._http_client.call(
                url=self._build_url(f'records/{key}'),
                method='GET',
                params=self._build_params(signature=signature, attachment=True),
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

        await self._http_client.call(
            url=self._build_url(f'records/{key}'),
            method='PUT',
            params=self._build_params(),
            data=value,
            headers=headers,
        )

    async def delete_record(self, key: str) -> None:
        """Delete the specified record from the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/delete-record

        Args:
            key: The key of the record which to delete.
        """
        await self._http_client.call(
            url=self._build_url(f'records/{key}'),
            method='DELETE',
            params=self._build_params(),
            timeout=FAST_OPERATION_TIMEOUT,
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
        if self._resource_id is None:
            raise ValueError('resource_id cannot be None when generating a public URL')

        metadata = await self.get()

        request_params = self._build_params()

        if metadata and metadata.url_signing_secret_key:
            request_params['signature'] = create_hmac_signature(metadata.url_signing_secret_key, key)

        key_public_url = urlparse(self._build_url(f'records/{key}', public=True))
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
        expires_in: timedelta | None = None,
    ) -> str:
        """Generate a URL that can be used to access key-value store keys.

        If the client has permission to access the key-value store's URL signing key,
        the URL will include a signature to verify its authenticity.

        You can optionally control how long the signed URL should be valid using the `expires_in` option.
        This value sets the expiration duration from the time the URL is generated.
        If not provided, the URL will not expire.

        Any other options (like `limit` or `prefix`) will be included as query parameters in the URL.

        Returns:
            The public key-value store keys URL.
        """
        metadata = await self.get()

        keys_public_url = urlparse(self._build_url('keys'))

        request_params = self._build_params(
            limit=limit,
            exclusiveStartKey=exclusive_start_key,
            collection=collection,
            prefix=prefix,
        )

        if metadata and metadata.url_signing_secret_key:
            signature = create_storage_content_signature(
                resource_id=metadata.id,
                url_signing_secret_key=metadata.url_signing_secret_key,
                expires_in=expires_in,
            )
            request_params['signature'] = signature

        keys_public_url = urlparse(self._build_url('keys', public=True))
        filtered_params = {k: v for k, v in request_params.items() if v is not None}
        if filtered_params:
            keys_public_url = keys_public_url._replace(query=urlencode(filtered_params))

        return urlunparse(keys_public_url)

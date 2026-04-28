from __future__ import annotations

import re
import warnings
from contextlib import asynccontextmanager, contextmanager
from http import HTTPStatus
from typing import TYPE_CHECKING, Any
from urllib.parse import urlencode, urlparse, urlunparse

from apify_client._docs import docs_group
from apify_client._models_generated import (
    KeyValueStore,
    KeyValueStoreResponse,
    ListOfKeysResponse,
)
from apify_client._pagination import (
    _LazyTask,
    _min_for_limit_param,
    build_get_cursor_iterator,
    build_get_cursor_iterator_async,
)
from apify_client._pagination_classes import (
    ListPageOfKeys,
    ListPageOfKeysAsync,
    PageOfKeys,
)
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import (
    catch_not_found_or_throw,
    create_hmac_signature,
    create_storage_content_signature,
    encode_key_value_store_record_value,
    response_to_dict,
)
from apify_client.errors import ApifyApiError, InvalidResponseBodyError

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator
    from datetime import timedelta

    from apify_client._http_clients import HttpResponse
    from apify_client._models_generated import GeneralAccess, KeyValueStoreKey
    from apify_client._types import Timeout


def _parse_get_record_response(response: HttpResponse) -> Any:
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


@docs_group('Resource clients')
class KeyValueStoreClient(ResourceClient):
    """Sub-client for managing a specific key-value store.

    Provides methods to manage a specific key-value store, e.g. get it, update it, or manage its records. Obtain an
    instance via an appropriate method on the `ApifyClient` class.
    """

    def __init__(
        self,
        *,
        resource_id: str | None = None,
        resource_path: str = 'key-value-stores',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_id=resource_id,
            resource_path=resource_path,
            **kwargs,
        )

    def get(self, *, timeout: Timeout = 'short') -> KeyValueStore | None:
        """Retrieve the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/get-store

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved key-value store, or None if it does not exist.
        """
        result = self._get(timeout=timeout)
        if result is None:
            return None
        return KeyValueStoreResponse.model_validate(result).data

    def update(
        self,
        *,
        name: str | None = None,
        general_access: GeneralAccess | None = None,
        timeout: Timeout = 'long',
    ) -> KeyValueStore:
        """Update the key-value store with specified fields.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/update-store

        Args:
            name: The new name for key-value store.
            general_access: Determines how others can access the key-value store.
            timeout: Timeout for the API HTTP request.

        Returns:
            The updated key-value store.
        """
        result = self._update(timeout=timeout, name=name, generalAccess=general_access)
        return KeyValueStoreResponse.model_validate(result).data

    def delete(self, *, timeout: Timeout = 'short') -> None:
        """Delete the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/delete-store

        Args:
            timeout: Timeout for the API HTTP request.
        """
        self._delete(timeout=timeout)

    def list_keys(
        self,
        *,
        limit: int | None = None,
        exclusive_start_key: str | None = None,
        collection: str | None = None,
        prefix: str | None = None,
        signature: str | None = None,
        chunk_size: int | None = None,
        timeout: Timeout = 'medium',
    ) -> ListPageOfKeys:
        """List the keys in the key-value store.

        The returned page also supports iteration: `for key in client.list_keys(...)` yields individual
        keys and transparently fetches further pages using cursor-based pagination.

        https://docs.apify.com/api/v2#/reference/key-value-stores/key-collection/get-list-of-keys

        Args:
            limit: Total number of keys to yield across all pages when iterating. The API caps each
                individual request at 1000 keys; use `chunk_size` to control the per-request size.
            exclusive_start_key: All keys up to this one (including) are skipped from the result.
            collection: The name of the collection in store schema to list keys from.
            prefix: The prefix of the keys to be listed.
            signature: Signature used to access the items.
            chunk_size: Maximum number of keys requested per API call when iterating. Capped at
                1000 by the API. Only relevant when iterating across pages.
            timeout: Timeout for the API HTTP request.

        Returns:
            The list of keys in the key-value store matching the given arguments.
        """

        def _callback(*, limit: int | None = None, exclusive_start_key: str | None = None) -> PageOfKeys:
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
                timeout=timeout,
            )
            result = response_to_dict(response)
            data = ListOfKeysResponse.model_validate(result).data
            return PageOfKeys(
                items=data.items,
                count=data.count,
                limit=data.limit,
                is_truncated=data.is_truncated,
                exclusive_start_key=data.exclusive_start_key,
                next_exclusive_start_key=data.next_exclusive_start_key,
            )

        first_limit = _min_for_limit_param(limit, chunk_size)
        first_page = _callback(limit=first_limit, exclusive_start_key=exclusive_start_key)
        get_iterator = build_get_cursor_iterator(
            _callback,
            first_page,
            cursor_param='exclusive_start_key',
            limit=limit,
            chunk_size=chunk_size,
        )

        return ListPageOfKeys(
            _get_iterator=get_iterator,
            items=first_page.items,
            count=first_page.count,
            limit=first_page.limit,
            is_truncated=first_page.is_truncated,
            exclusive_start_key=first_page.exclusive_start_key,
            next_exclusive_start_key=first_page.next_exclusive_start_key,
        )

    def iterate_keys(
        self,
        *,
        limit: int | None = None,
        exclusive_start_key: str | None = None,
        collection: str | None = None,
        prefix: str | None = None,
        signature: str | None = None,
        chunk_size: int | None = 1000,
        timeout: Timeout = 'medium',
    ) -> Iterator[KeyValueStoreKey]:
        """Iterate over the keys in the key-value store.

        Deprecated: iterate the return value of `KeyValueStoreClient.list_keys()` instead.

        https://docs.apify.com/api/v2#/reference/key-value-stores/key-collection/get-list-of-keys

        Args:
            limit: Total number of keys to yield across all pages. The API caps each individual
                request at 1000 keys; use `chunk_size` to control the per-request size.
            exclusive_start_key: All keys up to this one (including) are skipped from the result.
            collection: The name of the collection in store schema to list keys from.
            prefix: The prefix of the keys to be listed.
            signature: Signature used to access the items.
            chunk_size: Maximum number of keys requested per API call when iterating. Capped at
                1000 by the API. Only relevant when iterating across pages.
            timeout: Timeout for the API HTTP request.

        Yields:
            A key from the key-value store.
        """
        warnings.warn(
            '`KeyValueStoreClient.iterate_keys()` is deprecated, iterate the return value of '
            '`KeyValueStoreClient.list_keys()` instead.',
            DeprecationWarning,
            stacklevel=2,
        )
        yield from self.list_keys(
            limit=limit,
            exclusive_start_key=exclusive_start_key,
            collection=collection,
            prefix=prefix,
            signature=signature,
            chunk_size=chunk_size,
            timeout=timeout,
        )

    def get_record(self, key: str, *, signature: str | None = None, timeout: Timeout = 'long') -> dict | None:
        """Retrieve the given record from the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record

        Args:
            key: Key of the record to retrieve.
            signature: Signature used to access the items.
            timeout: Timeout for the API HTTP request.

        Returns:
            The requested record, or None, if the record does not exist.
        """
        try:
            response = self._http_client.call(
                url=self._build_url(f'records/{key}'),
                method='GET',
                params=self._build_params(signature=signature, attachment=True),
                timeout=timeout,
            )

            return {
                'key': key,
                'value': _parse_get_record_response(response),
                'content_type': response.headers['content-type'],
            }

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    def record_exists(self, key: str, *, timeout: Timeout = 'long') -> bool:
        """Check if given record is present in the key-value store.

        https://docs.apify.com/api/v2/key-value-store-record-head

        Args:
            key: Key of the record to check.
            timeout: Timeout for the API HTTP request.

        Returns:
            True if the record exists, False otherwise.
        """
        try:
            response = self._http_client.call(
                url=self._build_url(f'records/{key}'),
                method='HEAD',
                params=self._build_params(),
                timeout=timeout,
            )
        except ApifyApiError as exc:
            if exc.status_code == HTTPStatus.NOT_FOUND:
                return False

            raise

        return response.status_code == HTTPStatus.OK

    def get_record_as_bytes(self, key: str, *, signature: str | None = None, timeout: Timeout = 'long') -> dict | None:
        """Retrieve the given record from the key-value store, without parsing it.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record

        Args:
            key: Key of the record to retrieve.
            signature: Signature used to access the items.
            timeout: Timeout for the API HTTP request.

        Returns:
            The requested record, or None, if the record does not exist.
        """
        try:
            response = self._http_client.call(
                url=self._build_url(f'records/{key}'),
                method='GET',
                params=self._build_params(signature=signature, attachment=True),
                timeout=timeout,
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
    def stream_record(
        self, key: str, *, signature: str | None = None, timeout: Timeout = 'long'
    ) -> Iterator[dict | None]:
        """Retrieve the given record from the key-value store, as a stream.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record

        Args:
            key: Key of the record to retrieve.
            signature: Signature used to access the items.
            timeout: Timeout for the API HTTP request.

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
                timeout=timeout,
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
        *,
        content_type: str | None = None,
        timeout: Timeout = 'long',
    ) -> None:
        """Set a value to the given record in the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/put-record

        Args:
            key: The key of the record to save the value to.
            value: The value to save into the record.
            content_type: The content type of the saved value.
            timeout: Timeout for the API HTTP request.
        """
        value, content_type = encode_key_value_store_record_value(value, content_type=content_type)

        headers = {'content-type': content_type}

        self._http_client.call(
            url=self._build_url(f'records/{key}'),
            method='PUT',
            params=self._build_params(),
            data=value,
            headers=headers,
            timeout=timeout,
        )

    def delete_record(self, key: str, *, timeout: Timeout = 'short') -> None:
        """Delete the specified record from the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/delete-record

        Args:
            key: The key of the record which to delete.
            timeout: Timeout for the API HTTP request.
        """
        self._http_client.call(
            url=self._build_url(f'records/{key}'),
            method='DELETE',
            params=self._build_params(),
            timeout=timeout,
        )

    def get_record_public_url(self, key: str, *, timeout: Timeout = 'long') -> str:
        """Generate a URL that can be used to access key-value store record.

        If the client has permission to access the key-value store's URL signing key, the URL will include a signature
        to verify its authenticity.

        Args:
            key: The key for which the URL should be generated.
            timeout: Timeout for the API HTTP request.

        Returns:
            A public URL that can be used to access the value of the given key in the KVS.
        """
        if self._resource_id is None:
            raise ValueError('resource_id cannot be None when generating a public URL')

        metadata = self.get(timeout=timeout)

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
        timeout: Timeout = 'long',
    ) -> str:
        """Generate a URL that can be used to access key-value store keys.

        If the client has permission to access the key-value store's URL signing key,
        the URL will include a signature to verify its authenticity.

        You can optionally control how long the signed URL should be valid using the `expires_in` option.
        This value sets the expiration duration from the time the URL is generated.
        If not provided, the URL will not expire.

        Any other options (like `limit` or `prefix`) will be included as query parameters in the URL.

        Args:
            limit: Number of keys to be returned by the signed request. Maximum value is 1000.
            exclusive_start_key: All keys up to this one (including) are skipped from the result.
            collection: The name of the collection in store schema to list keys from.
            prefix: The prefix of the keys to be listed.
            expires_in: How long the signed URL should be valid from the time it is generated.
            timeout: Timeout for the API HTTP request.

        Returns:
            The public key-value store keys URL.
        """
        metadata = self.get(timeout=timeout)

        request_params = self._build_params(
            limit=limit,
            exclusiveStartKey=exclusive_start_key,
            collection=collection,
            prefix=prefix,
        )

        if metadata and metadata.url_signing_secret_key:
            signature = create_storage_content_signature(
                metadata.id,
                metadata.url_signing_secret_key,
                expires_in=expires_in,
            )
            request_params['signature'] = signature

        keys_public_url = urlparse(self._build_url('keys', public=True))

        filtered_params = {k: v for k, v in request_params.items() if v is not None}
        if filtered_params:
            keys_public_url = keys_public_url._replace(query=urlencode(filtered_params))

        return urlunparse(keys_public_url)


@docs_group('Resource clients')
class KeyValueStoreClientAsync(ResourceClientAsync):
    """Sub-client for managing a specific key-value store.

    Provides methods to manage a specific key-value store, e.g. get it, update it, or manage its records. Obtain an
    instance via an appropriate method on the `ApifyClientAsync` class.
    """

    def __init__(
        self,
        *,
        resource_id: str | None = None,
        resource_path: str = 'key-value-stores',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_id=resource_id,
            resource_path=resource_path,
            **kwargs,
        )

    async def get(self, *, timeout: Timeout = 'short') -> KeyValueStore | None:
        """Retrieve the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/get-store

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved key-value store, or None if it does not exist.
        """
        result = await self._get(timeout=timeout)
        if result is None:
            return None
        return KeyValueStoreResponse.model_validate(result).data

    async def update(
        self,
        *,
        name: str | None = None,
        general_access: GeneralAccess | None = None,
        timeout: Timeout = 'long',
    ) -> KeyValueStore:
        """Update the key-value store with specified fields.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/update-store

        Args:
            name: The new name for key-value store.
            general_access: Determines how others can access the key-value store.
            timeout: Timeout for the API HTTP request.

        Returns:
            The updated key-value store.
        """
        result = await self._update(timeout=timeout, name=name, generalAccess=general_access)
        return KeyValueStoreResponse.model_validate(result).data

    async def delete(self, *, timeout: Timeout = 'short') -> None:
        """Delete the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/delete-store

        Args:
            timeout: Timeout for the API HTTP request.
        """
        await self._delete(timeout=timeout)

    def list_keys(
        self,
        *,
        limit: int | None = None,
        exclusive_start_key: str | None = None,
        collection: str | None = None,
        prefix: str | None = None,
        signature: str | None = None,
        chunk_size: int | None = None,
        timeout: Timeout = 'medium',
    ) -> ListPageOfKeysAsync:
        """List the keys in the key-value store.

        The returned page also supports iteration: `async for key in client.list_keys(...)` yields individual
        keys and transparently fetches further pages using cursor-based pagination.

        https://docs.apify.com/api/v2#/reference/key-value-stores/key-collection/get-list-of-keys

        Args:
            limit: Total number of keys to yield across all pages when iterating. The API caps each
                individual request at 1000 keys; use `chunk_size` to control the per-request size.
            exclusive_start_key: All keys up to this one (including) are skipped from the result.
            collection: The name of the collection in store schema to list keys from.
            prefix: The prefix of the keys to be listed.
            signature: Signature used to access the items.
            chunk_size: Maximum number of keys requested per API call when iterating. Capped at
                1000 by the API. Only relevant when iterating across pages.
            timeout: Timeout for the API HTTP request.

        Returns:
            The list of keys in the key-value store matching the given arguments.
        """

        async def _callback(*, limit: int | None = None, exclusive_start_key: str | None = None) -> PageOfKeys:
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
                timeout=timeout,
            )
            result = response_to_dict(response)
            data = ListOfKeysResponse.model_validate(result).data
            return PageOfKeys(
                items=data.items,
                count=data.count,
                limit=data.limit,
                is_truncated=data.is_truncated,
                exclusive_start_key=data.exclusive_start_key,
                next_exclusive_start_key=data.next_exclusive_start_key,
            )

        first_limit = _min_for_limit_param(limit, chunk_size)
        fetch_first_page = _LazyTask(_callback(limit=first_limit, exclusive_start_key=exclusive_start_key))
        get_async_iterator = build_get_cursor_iterator_async(
            _callback,
            fetch_first_page,
            cursor_param='exclusive_start_key',
            limit=limit,
            chunk_size=chunk_size,
        )

        return ListPageOfKeysAsync(
            _awaitable_first_page=fetch_first_page,
            _get_async_iterator=get_async_iterator,
        )

    async def iterate_keys(
        self,
        *,
        limit: int | None = None,
        exclusive_start_key: str | None = None,
        collection: str | None = None,
        prefix: str | None = None,
        signature: str | None = None,
        chunk_size: int | None = 1000,
        timeout: Timeout = 'medium',
    ) -> AsyncIterator[KeyValueStoreKey]:
        """Iterate over the keys in the key-value store.

        Deprecated: iterate the return value of `KeyValueStoreClientAsync.list_keys()` instead.

        https://docs.apify.com/api/v2#/reference/key-value-stores/key-collection/get-list-of-keys

        Args:
            limit: Total number of keys to yield across all pages. The API caps each individual
                request at 1000 keys; use `chunk_size` to control the per-request size.
            exclusive_start_key: All keys up to this one (including) are skipped from the result.
            collection: The name of the collection in store schema to list keys from.
            prefix: The prefix of the keys to be listed.
            signature: Signature used to access the items.
            chunk_size: Maximum number of keys requested per API call when iterating. Capped at
                1000 by the API. Only relevant when iterating across pages.
            timeout: Timeout for the API HTTP request.

        Yields:
            A key from the key-value store.
        """
        warnings.warn(
            '`KeyValueStoreClientAsync.iterate_keys()` is deprecated, iterate the return value of '
            '`KeyValueStoreClientAsync.list_keys()` instead.',
            DeprecationWarning,
            stacklevel=2,
        )
        async for key in self.list_keys(
            limit=limit,
            exclusive_start_key=exclusive_start_key,
            collection=collection,
            prefix=prefix,
            signature=signature,
            chunk_size=chunk_size,
            timeout=timeout,
        ):
            yield key

    async def get_record(self, key: str, *, signature: str | None = None, timeout: Timeout = 'long') -> dict | None:
        """Retrieve the given record from the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record

        Args:
            key: Key of the record to retrieve.
            signature: Signature used to access the items.
            timeout: Timeout for the API HTTP request.

        Returns:
            The requested record, or None, if the record does not exist.
        """
        try:
            response = await self._http_client.call(
                url=self._build_url(f'records/{key}'),
                method='GET',
                params=self._build_params(signature=signature, attachment=True),
                timeout=timeout,
            )

            return {
                'key': key,
                'value': _parse_get_record_response(response),
                'content_type': response.headers['content-type'],
            }

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    async def record_exists(self, key: str, *, timeout: Timeout = 'long') -> bool:
        """Check if given record is present in the key-value store.

        https://docs.apify.com/api/v2/key-value-store-record-head

        Args:
            key: Key of the record to check.
            timeout: Timeout for the API HTTP request.

        Returns:
            True if the record exists, False otherwise.
        """
        try:
            response = await self._http_client.call(
                url=self._build_url(f'records/{key}'),
                method='HEAD',
                params=self._build_params(),
                timeout=timeout,
            )
        except ApifyApiError as exc:
            if exc.status_code == HTTPStatus.NOT_FOUND:
                return False

            raise

        return response.status_code == HTTPStatus.OK

    async def get_record_as_bytes(
        self, key: str, *, signature: str | None = None, timeout: Timeout = 'long'
    ) -> dict | None:
        """Retrieve the given record from the key-value store, without parsing it.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record

        Args:
            key: Key of the record to retrieve.
            signature: Signature used to access the items.
            timeout: Timeout for the API HTTP request.

        Returns:
            The requested record, or None, if the record does not exist.
        """
        try:
            response = await self._http_client.call(
                url=self._build_url(f'records/{key}'),
                method='GET',
                params=self._build_params(signature=signature, attachment=True),
                timeout=timeout,
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
    async def stream_record(
        self, key: str, *, signature: str | None = None, timeout: Timeout = 'long'
    ) -> AsyncIterator[dict | None]:
        """Retrieve the given record from the key-value store, as a stream.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record

        Args:
            key: Key of the record to retrieve.
            signature: Signature used to access the items.
            timeout: Timeout for the API HTTP request.

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
                timeout=timeout,
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
        *,
        content_type: str | None = None,
        timeout: Timeout = 'long',
    ) -> None:
        """Set a value to the given record in the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/put-record

        Args:
            key: The key of the record to save the value to.
            value: The value to save into the record.
            content_type: The content type of the saved value.
            timeout: Timeout for the API HTTP request.
        """
        value, content_type = encode_key_value_store_record_value(value, content_type=content_type)

        headers = {'content-type': content_type}

        await self._http_client.call(
            url=self._build_url(f'records/{key}'),
            method='PUT',
            params=self._build_params(),
            data=value,
            headers=headers,
            timeout=timeout,
        )

    async def delete_record(self, key: str, *, timeout: Timeout = 'short') -> None:
        """Delete the specified record from the key-value store.

        https://docs.apify.com/api/v2#/reference/key-value-stores/record/delete-record

        Args:
            key: The key of the record which to delete.
            timeout: Timeout for the API HTTP request.
        """
        await self._http_client.call(
            url=self._build_url(f'records/{key}'),
            method='DELETE',
            params=self._build_params(),
            timeout=timeout,
        )

    async def get_record_public_url(self, key: str, *, timeout: Timeout = 'long') -> str:
        """Generate a URL that can be used to access key-value store record.

        If the client has permission to access the key-value store's URL signing key, the URL will include a signature
        to verify its authenticity.

        Args:
            key: The key for which the URL should be generated.
            timeout: Timeout for the API HTTP request.

        Returns:
            A public URL that can be used to access the value of the given key in the KVS.
        """
        if self._resource_id is None:
            raise ValueError('resource_id cannot be None when generating a public URL')

        metadata = await self.get(timeout=timeout)

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
        timeout: Timeout = 'long',
    ) -> str:
        """Generate a URL that can be used to access key-value store keys.

        If the client has permission to access the key-value store's URL signing key,
        the URL will include a signature to verify its authenticity.

        You can optionally control how long the signed URL should be valid using the `expires_in` option.
        This value sets the expiration duration from the time the URL is generated.
        If not provided, the URL will not expire.

        Any other options (like `limit` or `prefix`) will be included as query parameters in the URL.

        Args:
            limit: Number of keys to be returned by the signed request. Maximum value is 1000.
            exclusive_start_key: All keys up to this one (including) are skipped from the result.
            collection: The name of the collection in store schema to list keys from.
            prefix: The prefix of the keys to be listed.
            expires_in: How long the signed URL should be valid from the time it is generated.
            timeout: Timeout for the API HTTP request.

        Returns:
            The public key-value store keys URL.
        """
        metadata = await self.get(timeout=timeout)

        request_params = self._build_params(
            limit=limit,
            exclusiveStartKey=exclusive_start_key,
            collection=collection,
            prefix=prefix,
        )

        if metadata and metadata.url_signing_secret_key:
            signature = create_storage_content_signature(
                metadata.id,
                metadata.url_signing_secret_key,
                expires_in=expires_in,
            )
            request_params['signature'] = signature

        keys_public_url = urlparse(self._build_url('keys', public=True))

        filtered_params = {k: v for k, v in request_params.items() if v is not None}
        if filtered_params:
            keys_public_url = keys_public_url._replace(query=urlencode(filtered_params))

        return urlunparse(keys_public_url)

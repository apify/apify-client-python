from __future__ import annotations

import warnings
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast
from urllib.parse import urlencode, urlparse, urlunparse

from apify_client._consts import FAST_OPERATION_TIMEOUT, STANDARD_OPERATION_TIMEOUT
from apify_client._models import CreateDatasetResponse, Dataset, DatasetStatistics, GetDatasetStatisticsResponse
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import (
    catch_not_found_or_throw,
    create_storage_content_signature,
    filter_none_values,
    response_to_dict,
    response_to_list,
)
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator
    from datetime import timedelta

    import impit

    from apify_client._consts import JsonSerializable
    from apify_client._models import GeneralAccessEnum


@dataclass
class DatasetItemsPage:
    """A page of dataset items returned by the `list_items` method.

    Dataset items are arbitrary JSON objects stored in the dataset, so they cannot be
    represented by a specific Pydantic model. This class provides pagination metadata
    along with the raw items.
    """

    items: list[dict[str, Any]]
    """List of dataset items. Each item is a JSON object (dictionary)."""

    total: int
    """Total number of items in the dataset."""

    offset: int
    """The offset of the first item in this page."""

    count: int
    """Number of items in this page."""

    limit: int
    """The limit that was used for this request."""

    desc: bool
    """Whether the items are sorted in descending order."""


class DatasetClient(ResourceClient):
    """Sub-client for manipulating a single dataset."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'datasets')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> Dataset | None:
        """Retrieve the dataset.

        https://docs.apify.com/api/v2#/reference/datasets/dataset/get-dataset

        Returns:
            The retrieved dataset, or None, if it does not exist.
        """
        try:
            response = self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(),
                timeout=FAST_OPERATION_TIMEOUT,
            )
            result = response_to_dict(response)
            return CreateDatasetResponse.model_validate(result).data
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            return None

    def update(self, *, name: str | None = None, general_access: GeneralAccessEnum | None = None) -> Dataset:
        """Update the dataset with specified fields.

        https://docs.apify.com/api/v2#/reference/datasets/dataset/update-dataset

        Args:
            name: The new name for the dataset.
            general_access: Determines how others can access the dataset.

        Returns:
            The updated dataset.
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
            timeout=FAST_OPERATION_TIMEOUT,
        )
        result = response_to_dict(response)
        return CreateDatasetResponse.model_validate(result).data

    def delete(self) -> None:
        """Delete the dataset.

        https://docs.apify.com/api/v2#/reference/datasets/dataset/delete-dataset
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

    def list_items(
        self,
        *,
        offset: int | None = None,
        limit: int | None = None,
        clean: bool | None = None,
        desc: bool | None = None,
        fields: list[str] | None = None,
        omit: list[str] | None = None,
        unwind: list[str] | None = None,
        skip_empty: bool | None = None,
        skip_hidden: bool | None = None,
        flatten: list[str] | None = None,
        view: str | None = None,
        signature: str | None = None,
    ) -> DatasetItemsPage:
        """List the items of the dataset.

        https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items

        Args:
            offset: Number of items that should be skipped at the start. The default value is 0.
            limit: Maximum number of items to return. By default there is no limit.
            desc: By default, results are returned in the same order as they were stored. To reverse the order,
                set this parameter to True.
            clean: If True, returns only non-empty items and skips hidden fields (i.e. fields starting with
                the # character). The clean parameter is just a shortcut for skip_hidden=True and skip_empty=True
                parameters. Note that since some objects might be skipped from the output, that the result might
                contain less items than the limit value.
            fields: A list of fields which should be picked from the items, only these fields will remain
                in the resulting record objects. Note that the fields in the outputted items are sorted the same
                way as they are specified in the fields parameter. You can use this feature to effectively fix
                the output format.
            omit: A list of fields which should be omitted from the items.
            unwind: A list of fields which should be unwound, in order which they should be processed. Each field
                should be either an array or an object. If the field is an array then every element of the array
                will become a separate record and merged with parent object. If the unwound field is an object then
                it is merged with the parent object. If the unwound field is missing or its value is neither an array
                nor an object and therefore cannot be merged with a parent object, then the item gets preserved
                as it is. Note that the unwound items ignore the desc parameter.
            skip_empty: If True, then empty items are skipped from the output. Note that if used, the results might
                contain less items than the limit value.
            skip_hidden: If True, then hidden fields are skipped from the output, i.e. fields starting with
                the # character.
            flatten: A list of fields that should be flattened.
            view: Name of the dataset view to be used.
            signature: Signature used to access the items.

        Returns:
            A page of the list of dataset items according to the specified filters.
        """
        request_params = self._build_params(
            offset=offset,
            limit=limit,
            desc=desc,
            clean=clean,
            fields=fields,
            omit=omit,
            unwind=unwind,
            skipEmpty=skip_empty,
            skipHidden=skip_hidden,
            flatten=flatten,
            view=view,
            signature=signature,
        )

        response = self._http_client.call(
            url=self._build_url('items'),
            method='GET',
            params=request_params,
        )

        # When using signature, API returns items as list directly
        try:
            items = response_to_list(response)
        except ValueError:
            items = cast('list', response_to_dict(response))

        return DatasetItemsPage(
            items=items,
            total=int(response.headers['x-apify-pagination-total']),
            offset=int(response.headers['x-apify-pagination-offset']),
            # x-apify-pagination-count returns invalid values when hidden/empty items are skipped
            count=len(items),
            # API returns 999999999999 when no limit is used
            limit=int(response.headers['x-apify-pagination-limit']),
            desc=bool(response.headers['x-apify-pagination-desc']),
        )

    def iterate_items(
        self,
        *,
        offset: int = 0,
        limit: int | None = None,
        clean: bool | None = None,
        desc: bool | None = None,
        fields: list[str] | None = None,
        omit: list[str] | None = None,
        unwind: list[str] | None = None,
        skip_empty: bool | None = None,
        skip_hidden: bool | None = None,
        signature: str | None = None,
    ) -> Iterator[dict]:
        """Iterate over the items in the dataset.

        https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items

        Args:
            offset: Number of items that should be skipped at the start. The default value is 0.
            limit: Maximum number of items to return. By default there is no limit.
            desc: By default, results are returned in the same order as they were stored. To reverse the order,
                set this parameter to True.
            clean: If True, returns only non-empty items and skips hidden fields (i.e. fields starting with
                the # character). The clean parameter is just a shortcut for skip_hidden=True and skip_empty=True
                parameters. Note that since some objects might be skipped from the output, that the result might
                contain less items than the limit value.
            fields: A list of fields which should be picked from the items, only these fields will remain in
                the resulting record objects. Note that the fields in the outputted items are sorted the same way
                as they are specified in the fields parameter. You can use this feature to effectively fix
                the output format.
            omit: A list of fields which should be omitted from the items.
            unwind: A list of fields which should be unwound, in order which they should be processed. Each field
                should be either an array or an object. If the field is an array then every element of the array
                will become a separate record and merged with parent object. If the unwound field is an object then
                it is merged with the parent object. If the unwound field is missing or its value is neither an array
                nor an object and therefore cannot be merged with a parent object, then the item gets preserved
                as it is. Note that the unwound items ignore the desc parameter.
            skip_empty: If True, then empty items are skipped from the output. Note that if used, the results might
                contain less items than the limit value.
            skip_hidden: If True, then hidden fields are skipped from the output, i.e. fields starting with
                the # character.
            signature: Signature used to access the items.

        Yields:
            An item from the dataset.
        """
        cache_size = 1000

        should_finish = False
        read_items = 0

        # We can't rely on DatasetItemsPage.total because that is updated with a delay,
        # so if you try to read the dataset items right after a run finishes, you could miss some.
        # Instead, we just read and read until we reach the limit, or until there are no more items to read.
        while not should_finish:
            effective_limit = cache_size
            if limit is not None:
                if read_items == limit:
                    break
                effective_limit = min(cache_size, limit - read_items)

            current_items_page = self.list_items(
                offset=offset + read_items,
                limit=effective_limit,
                clean=clean,
                desc=desc,
                fields=fields,
                omit=omit,
                unwind=unwind,
                skip_empty=skip_empty,
                skip_hidden=skip_hidden,
                signature=signature,
            )

            yield from current_items_page.items

            current_page_item_count = len(current_items_page.items)
            read_items += current_page_item_count

            if current_page_item_count < cache_size:
                should_finish = True

    def download_items(
        self,
        *,
        item_format: str = 'json',
        offset: int | None = None,
        limit: int | None = None,
        desc: bool | None = None,
        clean: bool | None = None,
        bom: bool | None = None,
        delimiter: str | None = None,
        fields: list[str] | None = None,
        omit: list[str] | None = None,
        unwind: list[str] | None = None,
        skip_empty: bool | None = None,
        skip_header_row: bool | None = None,
        skip_hidden: bool | None = None,
        xml_root: str | None = None,
        xml_row: str | None = None,
        flatten: list[str] | None = None,
        signature: str | None = None,
    ) -> bytes:
        """Get the items in the dataset as raw bytes.

        Deprecated: this function is a deprecated alias of `get_items_as_bytes`. It will be removed in
        a future version.

        https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items

        Args:
            item_format: Format of the results, possible values are: json, jsonl, csv, html, xlsx, xml and rss.
                The default value is json.
            offset: Number of items that should be skipped at the start. The default value is 0.
            limit: Maximum number of items to return. By default there is no limit.
            desc: By default, results are returned in the same order as they were stored. To reverse the order,
                set this parameter to True.
            clean: If True, returns only non-empty items and skips hidden fields (i.e. fields starting with
                the # character). The clean parameter is just a shortcut for skip_hidden=True and skip_empty=True
                parameters. Note that since some objects might be skipped from the output, that the result might
                contain less items than the limit value.
            bom: All text responses are encoded in UTF-8 encoding. By default, csv files are prefixed with
                the UTF-8 Byte Order Mark (BOM), while json, jsonl, xml, html and rss files are not. If you want
                to override this default behavior, specify bom=True query parameter to include the BOM or bom=False
                to skip it.
            delimiter: A delimiter character for CSV files. The default delimiter is a simple comma (,).
            fields: A list of fields which should be picked from the items, only these fields will remain in
                the resulting record objects. Note that the fields in the outputted items are sorted the same way
                as they are specified in the fields parameter. You can use this feature to effectively fix the
                output format.
            omit: A list of fields which should be omitted from the items.
            unwind: A list of fields which should be unwound, in order which they should be processed. Each field
                should be either an array or an object. If the field is an array then every element of the array
                will become a separate record and merged with parent object. If the unwound field is an object then
                it is merged with the parent object. If the unwound field is missing or its value is neither an array
                nor an object and therefore cannot be merged with a parent object, then the item gets preserved
                as it is. Note that the unwound items ignore the desc parameter.
            skip_empty: If True, then empty items are skipped from the output. Note that if used, the results might
                contain less items than the limit value.
            skip_header_row: If True, then header row in the csv format is skipped.
            skip_hidden: If True, then hidden fields are skipped from the output, i.e. fields starting with
                the # character.
            xml_root: Overrides default root element name of xml output. By default the root element is items.
            xml_row: Overrides default element name that wraps each page or page function result object in xml output.
                By default the element name is item.
            flatten: A list of fields that should be flattened.
            signature: Signature used to access the items.

        Returns:
            The dataset items as raw bytes.
        """
        warnings.warn(
            '`DatasetClient.download_items()` is deprecated, use `DatasetClient.get_items_as_bytes()` instead.',
            DeprecationWarning,
            stacklevel=2,
        )

        return self.get_items_as_bytes(
            item_format=item_format,
            offset=offset,
            limit=limit,
            desc=desc,
            clean=clean,
            bom=bom,
            delimiter=delimiter,
            fields=fields,
            omit=omit,
            unwind=unwind,
            skip_empty=skip_empty,
            skip_header_row=skip_header_row,
            skip_hidden=skip_hidden,
            xml_root=xml_root,
            xml_row=xml_row,
            flatten=flatten,
            signature=signature,
        )

    def get_items_as_bytes(
        self,
        *,
        item_format: str = 'json',
        offset: int | None = None,
        limit: int | None = None,
        desc: bool | None = None,
        clean: bool | None = None,
        bom: bool | None = None,
        delimiter: str | None = None,
        fields: list[str] | None = None,
        omit: list[str] | None = None,
        unwind: list[str] | None = None,
        skip_empty: bool | None = None,
        skip_header_row: bool | None = None,
        skip_hidden: bool | None = None,
        xml_root: str | None = None,
        xml_row: str | None = None,
        flatten: list[str] | None = None,
        signature: str | None = None,
    ) -> bytes:
        """Get the items in the dataset as raw bytes.

        https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items

        Args:
            item_format: Format of the results, possible values are: json, jsonl, csv, html, xlsx, xml and rss.
                The default value is json.
            offset: Number of items that should be skipped at the start. The default value is 0.
            limit: Maximum number of items to return. By default there is no limit.
            desc: By default, results are returned in the same order as they were stored. To reverse the order,
                set this parameter to True.
            clean: If True, returns only non-empty items and skips hidden fields (i.e. fields starting with
                the # character). The clean parameter is just a shortcut for skip_hidden=True and skip_empty=True
                parameters. Note that since some objects might be skipped from the output, that the result might
                contain less items than the limit value.
            bom: All text responses are encoded in UTF-8 encoding. By default, csv files are prefixed with
                the UTF-8 Byte Order Mark (BOM), while json, jsonl, xml, html and rss files are not. If you want
                to override this default behavior, specify bom=True query parameter to include the BOM or bom=False
                to skip it.
            delimiter: A delimiter character for CSV files. The default delimiter is a simple comma (,).
            fields: A list of fields which should be picked from the items, only these fields will remain
                in the resulting record objects. Note that the fields in the outputted items are sorted the same
                way as they are specified in the fields parameter. You can use this feature to effectively fix
                the output format.
                You can use this feature to effectively fix the output format.
            omit: A list of fields which should be omitted from the items.
            unwind: A list of fields which should be unwound, in order which they should be processed. Each field
                should be either an array or an object. If the field is an array then every element of the array
                will become a separate record and merged with parent object. If the unwound field is an object then
                it is merged with the parent object. If the unwound field is missing or its value is neither an array
                nor an object and therefore cannot be merged with a parent object, then the item gets preserved
                as it is. Note that the unwound items ignore the desc parameter.
            skip_empty: If True, then empty items are skipped from the output. Note that if used, the results might
                contain less items than the limit value.
            skip_header_row: If True, then header row in the csv format is skipped.
            skip_hidden: If True, then hidden fields are skipped from the output, i.e. fields starting with
                the # character.
            xml_root: Overrides default root element name of xml output. By default the root element is items.
            xml_row: Overrides default element name that wraps each page or page function result object in xml output.
                By default the element name is item.
            flatten: A list of fields that should be flattened.
            signature: Signature used to access the items.

        Returns:
            The dataset items as raw bytes.
        """
        request_params = self._build_params(
            format=item_format,
            offset=offset,
            limit=limit,
            desc=desc,
            clean=clean,
            bom=bom,
            delimiter=delimiter,
            fields=fields,
            omit=omit,
            unwind=unwind,
            skipEmpty=skip_empty,
            skipHeaderRow=skip_header_row,
            skipHidden=skip_hidden,
            xmlRoot=xml_root,
            xmlRow=xml_row,
            flatten=flatten,
            signature=signature,
        )

        response = self._http_client.call(
            url=self._build_url('items'),
            method='GET',
            params=request_params,
        )

        return response.content

    @contextmanager
    def stream_items(
        self,
        *,
        item_format: str = 'json',
        offset: int | None = None,
        limit: int | None = None,
        desc: bool | None = None,
        clean: bool | None = None,
        bom: bool | None = None,
        delimiter: str | None = None,
        fields: list[str] | None = None,
        omit: list[str] | None = None,
        unwind: list[str] | None = None,
        skip_empty: bool | None = None,
        skip_header_row: bool | None = None,
        skip_hidden: bool | None = None,
        xml_root: str | None = None,
        xml_row: str | None = None,
        signature: str | None = None,
    ) -> Iterator[impit.Response]:
        """Retrieve the items in the dataset as a stream.

        https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items

        Args:
            item_format: Format of the results, possible values are: json, jsonl, csv, html, xlsx, xml and rss.
                The default value is json.
            offset: Number of items that should be skipped at the start. The default value is 0.
            limit: Maximum number of items to return. By default there is no limit.
            desc: By default, results are returned in the same order as they were stored. To reverse the order,
                set this parameter to True.
            clean: If True, returns only non-empty items and skips hidden fields (i.e. fields starting with
                the # character). The clean parameter is just a shortcut for skip_hidden=True and skip_empty=True
                parameters. Note that since some objects might be skipped from the output, that the result might
                contain less items than the limit value.
            bom: All text responses are encoded in UTF-8 encoding. By default, csv files are prefixed with
                the UTF-8 Byte Order Mark (BOM), while json, jsonl, xml, html and rss files are not. If you want
                to override this default behavior, specify bom=True query parameter to include the BOM or bom=False
                to skip it.
            delimiter: A delimiter character for CSV files. The default delimiter is a simple comma (,).
            fields: A list of fields which should be picked from the items, only these fields will remain
                in the resulting record objects. Note that the fields in the outputted items are sorted the same
                way as they are specified in the fields parameter. You can use this feature to effectively fix
                the output format.
                You can use this feature to effectively fix the output format.
            omit: A list of fields which should be omitted from the items.
            unwind: A list of fields which should be unwound, in order which they should be processed. Each field
                should be either an array or an object. If the field is an array then every element of the array
                will become a separate record and merged with parent object. If the unwound field is an object then
                it is merged with the parent object. If the unwound field is missing or its value is neither an array
                nor an object and therefore cannot be merged with a parent object, then the item gets preserved
                as it is. Note that the unwound items ignore the desc parameter.
            skip_empty: If True, then empty items are skipped from the output. Note that if used, the results might
                contain less items than the limit value.
            skip_header_row: If True, then header row in the csv format is skipped.
            skip_hidden: If True, then hidden fields are skipped from the output, i.e. fields starting with
                the # character.
            xml_root: Overrides default root element name of xml output. By default the root element is items.
            xml_row: Overrides default element name that wraps each page or page function result object in xml output.
                By default the element name is item.
            signature: Signature used to access the items.

        Returns:
            The dataset items as a context-managed streaming `Response`.
        """
        response = None
        try:
            request_params = self._build_params(
                format=item_format,
                offset=offset,
                limit=limit,
                desc=desc,
                clean=clean,
                bom=bom,
                delimiter=delimiter,
                fields=fields,
                omit=omit,
                unwind=unwind,
                skipEmpty=skip_empty,
                skipHeaderRow=skip_header_row,
                skipHidden=skip_hidden,
                xmlRoot=xml_root,
                xmlRow=xml_row,
                signature=signature,
            )

            response = self._http_client.call(
                url=self._build_url('items'),
                method='GET',
                params=request_params,
                stream=True,
            )
            yield response
        finally:
            if response:
                response.close()

    def push_items(self, items: JsonSerializable) -> None:
        """Push items to the dataset.

        https://docs.apify.com/api/v2#/reference/datasets/item-collection/put-items

        Args:
            items: The items which to push in the dataset. Either a stringified JSON, a dictionary, or a list
                of strings or dictionaries.
        """
        data = None
        json = None

        if isinstance(items, str):
            data = items
        else:
            json = items

        self._http_client.call(
            url=self._build_url('items'),
            method='POST',
            headers={'content-type': 'application/json; charset=utf-8'},
            params=self._build_params(),
            data=data,
            json=json,
            timeout=STANDARD_OPERATION_TIMEOUT,
        )

    def get_statistics(self) -> DatasetStatistics | None:
        """Get the dataset statistics.

        https://docs.apify.com/api/v2#tag/DatasetsStatistics/operation/dataset_statistics_get

        Returns:
            The dataset statistics or None if the dataset does not exist.
        """
        try:
            response = self._http_client.call(
                url=self._build_url('statistics'),
                method='GET',
                params=self._build_params(),
                timeout=FAST_OPERATION_TIMEOUT,
            )
            result = response.json()
            return GetDatasetStatisticsResponse.model_validate(result).data if result is not None else None
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    def create_items_public_url(
        self,
        *,
        offset: int | None = None,
        limit: int | None = None,
        clean: bool | None = None,
        desc: bool | None = None,
        fields: list[str] | None = None,
        omit: list[str] | None = None,
        unwind: list[str] | None = None,
        skip_empty: bool | None = None,
        skip_hidden: bool | None = None,
        flatten: list[str] | None = None,
        view: str | None = None,
        expires_in: timedelta | None = None,
    ) -> str:
        """Generate a URL that can be used to access dataset items.

        If the client has permission to access the dataset's URL signing key,
        the URL will include a signature to verify its authenticity.

        You can optionally control how long the signed URL should be valid using the `expires_in` option.
        This value sets the expiration duration from the time the URL is generated.
        If not provided, the URL will not expire.

        Any other options (like `limit` or `offset`) will be included as query parameters in the URL.

        Returns:
            The public dataset items URL.
        """
        dataset = self.get()

        request_params = self._build_params(
            offset=offset,
            limit=limit,
            desc=desc,
            clean=clean,
            fields=fields,
            omit=omit,
            unwind=unwind,
            skipEmpty=skip_empty,
            skipHidden=skip_hidden,
            flatten=flatten,
            view=view,
        )

        if dataset and dataset.url_signing_secret_key:
            signature = create_storage_content_signature(
                resource_id=dataset.id,
                url_signing_secret_key=dataset.url_signing_secret_key,
                expires_in=expires_in,
            )
            request_params['signature'] = signature

        items_public_url = urlparse(self._build_url('items', public=True))
        filtered_params = {k: v for k, v in request_params.items() if v is not None}
        if filtered_params:
            items_public_url = items_public_url._replace(query=urlencode(filtered_params))

        return urlunparse(items_public_url)


class DatasetClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single dataset."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'datasets')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self) -> Dataset | None:
        """Retrieve the dataset.

        https://docs.apify.com/api/v2#/reference/datasets/dataset/get-dataset

        Returns:
            The retrieved dataset, or None, if it does not exist.
        """
        try:
            response = await self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(),
                timeout=FAST_OPERATION_TIMEOUT,
            )
            result = response_to_dict(response)
            return CreateDatasetResponse.model_validate(result).data
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            return None

    async def update(self, *, name: str | None = None, general_access: GeneralAccessEnum | None = None) -> Dataset:
        """Update the dataset with specified fields.

        https://docs.apify.com/api/v2#/reference/datasets/dataset/update-dataset

        Args:
            name: The new name for the dataset.
            general_access: Determines how others can access the dataset.

        Returns:
            The updated dataset.
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
            timeout=FAST_OPERATION_TIMEOUT,
        )
        result = response_to_dict(response)
        return CreateDatasetResponse.model_validate(result).data

    async def delete(self) -> None:
        """Delete the dataset.

        https://docs.apify.com/api/v2#/reference/datasets/dataset/delete-dataset
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

    async def list_items(
        self,
        *,
        offset: int | None = None,
        limit: int | None = None,
        clean: bool | None = None,
        desc: bool | None = None,
        fields: list[str] | None = None,
        omit: list[str] | None = None,
        unwind: list[str] | None = None,
        skip_empty: bool | None = None,
        skip_hidden: bool | None = None,
        flatten: list[str] | None = None,
        view: str | None = None,
        signature: str | None = None,
    ) -> DatasetItemsPage:
        """List the items of the dataset.

        https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items

        Args:
            offset: Number of items that should be skipped at the start. The default value is 0.
            limit: Maximum number of items to return. By default there is no limit.
            desc: By default, results are returned in the same order as they were stored. To reverse the order,
                set this parameter to True.
            clean: If True, returns only non-empty items and skips hidden fields (i.e. fields starting with
                the # character). The clean parameter is just a shortcut for skip_hidden=True and skip_empty=True
                parameters. Note that since some objects might be skipped from the output, that the result might
                contain less items than the limit value.
            fields: A list of fields which should be picked from the items, only these fields will remain
                in the resulting record objects. Note that the fields in the outputted items are sorted the same
                way as they are specified in the fields parameter. You can use this feature to effectively fix
                the output format.
            omit: A list of fields which should be omitted from the items.
            unwind: A list of fields which should be unwound, in order which they should be processed. Each field
                should be either an array or an object. If the field is an array then every element of the array
                will become a separate record and merged with parent object. If the unwound field is an object then
                it is merged with the parent object. If the unwound field is missing or its value is neither an array
                nor an object and therefore cannot be merged with a parent object, then the item gets preserved
                as it is. Note that the unwound items ignore the desc parameter.
            skip_empty: If True, then empty items are skipped from the output. Note that if used, the results might
                contain less items than the limit value.
            skip_hidden: If True, then hidden fields are skipped from the output, i.e. fields starting with
                the # character.
            flatten: A list of fields that should be flattened.
            view: Name of the dataset view to be used.
            signature: Signature used to access the items.

        Returns:
            A page of the list of dataset items according to the specified filters.
        """
        request_params = self._build_params(
            offset=offset,
            limit=limit,
            desc=desc,
            clean=clean,
            fields=fields,
            omit=omit,
            unwind=unwind,
            skipEmpty=skip_empty,
            skipHidden=skip_hidden,
            flatten=flatten,
            view=view,
            signature=signature,
        )

        response = await self._http_client.call(
            url=self._build_url('items'),
            method='GET',
            params=request_params,
        )

        # When using signature, API returns items as list directly
        try:
            items = response_to_list(response)
        except ValueError:
            items = cast('list', response_to_dict(response))

        return DatasetItemsPage(
            items=items,
            total=int(response.headers['x-apify-pagination-total']),
            offset=int(response.headers['x-apify-pagination-offset']),
            # x-apify-pagination-count returns invalid values when hidden/empty items are skipped
            count=len(items),
            # API returns 999999999999 when no limit is used
            limit=int(response.headers['x-apify-pagination-limit']),
            desc=bool(response.headers['x-apify-pagination-desc']),
        )

    async def iterate_items(
        self,
        *,
        offset: int = 0,
        limit: int | None = None,
        clean: bool | None = None,
        desc: bool | None = None,
        fields: list[str] | None = None,
        omit: list[str] | None = None,
        unwind: list[str] | None = None,
        skip_empty: bool | None = None,
        skip_hidden: bool | None = None,
        signature: str | None = None,
    ) -> AsyncIterator[dict]:
        """Iterate over the items in the dataset.

        https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items

        Args:
            offset: Number of items that should be skipped at the start. The default value is 0.
            limit: Maximum number of items to return. By default there is no limit.
            desc: By default, results are returned in the same order as they were stored. To reverse the order,
                set this parameter to True.
            clean: If True, returns only non-empty items and skips hidden fields (i.e. fields starting with
                the # character). The clean parameter is just a shortcut for skip_hidden=True and skip_empty=True
                parameters. Note that since some objects might be skipped from the output, that the result might
                contain less items than the limit value.
            fields: A list of fields which should be picked from the items, only these fields will remain in
                the resulting record objects. Note that the fields in the outputted items are sorted the same way
                as they are specified in the fields parameter. You can use this feature to effectively fix
                the output format.
            omit: A list of fields which should be omitted from the items.
            unwind: A list of fields which should be unwound, in order which they should be processed. Each field
                should be either an array or an object. If the field is an array then every element of the array
                will become a separate record and merged with parent object. If the unwound field is an object then
                it is merged with the parent object. If the unwound field is missing or its value is neither an array
                nor an object and therefore cannot be merged with a parent object, then the item gets preserved
                as it is. Note that the unwound items ignore the desc parameter.
            skip_empty: If True, then empty items are skipped from the output. Note that if used, the results might
                contain less items than the limit value.
            skip_hidden: If True, then hidden fields are skipped from the output, i.e. fields starting with
                the # character.
            signature: Signature used to access the items.

        Yields:
            An item from the dataset.
        """
        cache_size = 1000

        should_finish = False
        read_items = 0

        # We can't rely on DatasetItemsPage.total because that is updated with a delay,
        # so if you try to read the dataset items right after a run finishes, you could miss some.
        # Instead, we just read and read until we reach the limit, or until there are no more items to read.
        while not should_finish:
            effective_limit = cache_size
            if limit is not None:
                if read_items == limit:
                    break
                effective_limit = min(cache_size, limit - read_items)

            current_items_page = await self.list_items(
                offset=offset + read_items,
                limit=effective_limit,
                clean=clean,
                desc=desc,
                fields=fields,
                omit=omit,
                unwind=unwind,
                skip_empty=skip_empty,
                skip_hidden=skip_hidden,
                signature=signature,
            )

            for item in current_items_page.items:
                yield item

            current_page_item_count = len(current_items_page.items)
            read_items += current_page_item_count

            if current_page_item_count < cache_size:
                should_finish = True

    async def get_items_as_bytes(
        self,
        *,
        item_format: str = 'json',
        offset: int | None = None,
        limit: int | None = None,
        desc: bool | None = None,
        clean: bool | None = None,
        bom: bool | None = None,
        delimiter: str | None = None,
        fields: list[str] | None = None,
        omit: list[str] | None = None,
        unwind: list[str] | None = None,
        skip_empty: bool | None = None,
        skip_header_row: bool | None = None,
        skip_hidden: bool | None = None,
        xml_root: str | None = None,
        xml_row: str | None = None,
        flatten: list[str] | None = None,
        signature: str | None = None,
    ) -> bytes:
        """Get the items in the dataset as raw bytes.

        https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items

        Args:
            item_format: Format of the results, possible values are: json, jsonl, csv, html, xlsx, xml and rss.
                The default value is json.
            offset: Number of items that should be skipped at the start. The default value is 0.
            limit: Maximum number of items to return. By default there is no limit.
            desc: By default, results are returned in the same order as they were stored. To reverse the order,
                set this parameter to True.
            clean: If True, returns only non-empty items and skips hidden fields (i.e. fields starting with
                the # character). The clean parameter is just a shortcut for skip_hidden=True and skip_empty=True
                parameters. Note that since some objects might be skipped from the output, that the result might
                contain less items than the limit value.
            bom: All text responses are encoded in UTF-8 encoding. By default, csv files are prefixed with
                the UTF-8 Byte Order Mark (BOM), while json, jsonl, xml, html and rss files are not. If you want
                to override this default behavior, specify bom=True query parameter to include the BOM or bom=False
                to skip it.
            delimiter: A delimiter character for CSV files. The default delimiter is a simple comma (,).
            fields: A list of fields which should be picked from the items, only these fields will remain
                in the resulting record objects. Note that the fields in the outputted items are sorted the same
                way as they are specified in the fields parameter. You can use this feature to effectively fix
                the output format.
                You can use this feature to effectively fix the output format.
            omit: A list of fields which should be omitted from the items.
            unwind: A list of fields which should be unwound, in order which they should be processed. Each field
                should be either an array or an object. If the field is an array then every element of the array
                will become a separate record and merged with parent object. If the unwound field is an object then
                it is merged with the parent object. If the unwound field is missing or its value is neither an array
                nor an object and therefore cannot be merged with a parent object, then the item gets preserved
                as it is. Note that the unwound items ignore the desc parameter.
            skip_empty: If True, then empty items are skipped from the output. Note that if used, the results might
                contain less items than the limit value.
            skip_header_row: If True, then header row in the csv format is skipped.
            skip_hidden: If True, then hidden fields are skipped from the output, i.e. fields starting with
                the # character.
            xml_root: Overrides default root element name of xml output. By default the root element is items.
            xml_row: Overrides default element name that wraps each page or page function result object in xml output.
                By default the element name is item.
            flatten: A list of fields that should be flattened.
            signature: Signature used to access the items.

        Returns:
            The dataset items as raw bytes.
        """
        request_params = self._build_params(
            format=item_format,
            offset=offset,
            limit=limit,
            desc=desc,
            clean=clean,
            bom=bom,
            delimiter=delimiter,
            fields=fields,
            omit=omit,
            unwind=unwind,
            skipEmpty=skip_empty,
            skipHeaderRow=skip_header_row,
            skipHidden=skip_hidden,
            xmlRoot=xml_root,
            xmlRow=xml_row,
            flatten=flatten,
            signature=signature,
        )

        response = await self._http_client.call(
            url=self._build_url('items'),
            method='GET',
            params=request_params,
        )

        return response.content

    @asynccontextmanager
    async def stream_items(
        self,
        *,
        item_format: str = 'json',
        offset: int | None = None,
        limit: int | None = None,
        desc: bool | None = None,
        clean: bool | None = None,
        bom: bool | None = None,
        delimiter: str | None = None,
        fields: list[str] | None = None,
        omit: list[str] | None = None,
        unwind: list[str] | None = None,
        skip_empty: bool | None = None,
        skip_header_row: bool | None = None,
        skip_hidden: bool | None = None,
        xml_root: str | None = None,
        xml_row: str | None = None,
        signature: str | None = None,
    ) -> AsyncIterator[impit.Response]:
        """Retrieve the items in the dataset as a stream.

        https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items

        Args:
            item_format: Format of the results, possible values are: json, jsonl, csv, html, xlsx, xml and rss.
                The default value is json.
            offset: Number of items that should be skipped at the start. The default value is 0.
            limit: Maximum number of items to return. By default there is no limit.
            desc: By default, results are returned in the same order as they were stored. To reverse the order,
                set this parameter to True.
            clean: If True, returns only non-empty items and skips hidden fields (i.e. fields starting with
                the # character). The clean parameter is just a shortcut for skip_hidden=True and skip_empty=True
                parameters. Note that since some objects might be skipped from the output, that the result might
                contain less items than the limit value.
            bom: All text responses are encoded in UTF-8 encoding. By default, csv files are prefixed with
                the UTF-8 Byte Order Mark (BOM), while json, jsonl, xml, html and rss files are not. If you want
                to override this default behavior, specify bom=True query parameter to include the BOM or bom=False
                to skip it.
            delimiter: A delimiter character for CSV files. The default delimiter is a simple comma (,).
            fields: A list of fields which should be picked from the items, only these fields will remain
                in the resulting record objects. Note that the fields in the outputted items are sorted the same
                way as they are specified in the fields parameter. You can use this feature to effectively fix
                the output format.
                You can use this feature to effectively fix the output format.
            omit: A list of fields which should be omitted from the items.
            unwind: A list of fields which should be unwound, in order which they should be processed. Each field
                should be either an array or an object. If the field is an array then every element of the array
                will become a separate record and merged with parent object. If the unwound field is an object then
                it is merged with the parent object. If the unwound field is missing or its value is neither an array
                nor an object and therefore cannot be merged with a parent object, then the item gets preserved
                as it is. Note that the unwound items ignore the desc parameter.
            skip_empty: If True, then empty items are skipped from the output. Note that if used, the results might
                contain less items than the limit value.
            skip_header_row: If True, then header row in the csv format is skipped.
            skip_hidden: If True, then hidden fields are skipped from the output, i.e. fields starting with
                the # character.
            xml_root: Overrides default root element name of xml output. By default the root element is items.
            xml_row: Overrides default element name that wraps each page or page function result object in xml output.
                By default the element name is item.
            signature: Signature used to access the items.

        Returns:
            The dataset items as a context-managed streaming `Response`.
        """
        response = None
        try:
            request_params = self._build_params(
                format=item_format,
                offset=offset,
                limit=limit,
                desc=desc,
                clean=clean,
                bom=bom,
                delimiter=delimiter,
                fields=fields,
                omit=omit,
                unwind=unwind,
                skipEmpty=skip_empty,
                skipHeaderRow=skip_header_row,
                skipHidden=skip_hidden,
                xmlRoot=xml_root,
                xmlRow=xml_row,
                signature=signature,
            )

            response = await self._http_client.call(
                url=self._build_url('items'),
                method='GET',
                params=request_params,
                stream=True,
            )
            yield response
        finally:
            if response:
                await response.aclose()

    async def push_items(self, items: JsonSerializable) -> None:
        """Push items to the dataset.

        https://docs.apify.com/api/v2#/reference/datasets/item-collection/put-items

        Args:
            items: The items which to push in the dataset. Either a stringified JSON, a dictionary, or a list
                of strings or dictionaries.
        """
        data = None
        json = None

        if isinstance(items, str):
            data = items
        else:
            json = items

        await self._http_client.call(
            url=self._build_url('items'),
            method='POST',
            headers={'content-type': 'application/json; charset=utf-8'},
            params=self._build_params(),
            data=data,
            json=json,
            timeout=STANDARD_OPERATION_TIMEOUT,
        )

    async def get_statistics(self) -> DatasetStatistics | None:
        """Get the dataset statistics.

        https://docs.apify.com/api/v2#tag/DatasetsStatistics/operation/dataset_statistics_get

        Returns:
            The dataset statistics or None if the dataset does not exist.
        """
        try:
            response = await self._http_client.call(
                url=self._build_url('statistics'),
                method='GET',
                params=self._build_params(),
                timeout=FAST_OPERATION_TIMEOUT,
            )
            result = response.json()
            return GetDatasetStatisticsResponse.model_validate(result).data if result is not None else None
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    async def create_items_public_url(
        self,
        *,
        offset: int | None = None,
        limit: int | None = None,
        clean: bool | None = None,
        desc: bool | None = None,
        fields: list[str] | None = None,
        omit: list[str] | None = None,
        unwind: list[str] | None = None,
        skip_empty: bool | None = None,
        skip_hidden: bool | None = None,
        flatten: list[str] | None = None,
        view: str | None = None,
        expires_in: timedelta | None = None,
    ) -> str:
        """Generate a URL that can be used to access dataset items.

        If the client has permission to access the dataset's URL signing key,
        the URL will include a signature to verify its authenticity.

        You can optionally control how long the signed URL should be valid using the `expires_in` option.
        This value sets the expiration duration from the time the URL is generated.
        If not provided, the URL will not expire.

        Any other options (like `limit` or `offset`) will be included as query parameters in the URL.

        Returns:
            The public dataset items URL.
        """
        dataset = await self.get()

        request_params = self._build_params(
            offset=offset,
            limit=limit,
            desc=desc,
            clean=clean,
            fields=fields,
            omit=omit,
            unwind=unwind,
            skipEmpty=skip_empty,
            skipHidden=skip_hidden,
            flatten=flatten,
            view=view,
        )

        if dataset and dataset.url_signing_secret_key:
            signature = create_storage_content_signature(
                resource_id=dataset.id,
                url_signing_secret_key=dataset.url_signing_secret_key,
                expires_in=expires_in,
            )
            request_params['signature'] = signature

        items_public_url = urlparse(self._build_url('items', public=True))
        filtered_params = {k: v for k, v in request_params.items() if v is not None}
        if filtered_params:
            items_public_url = items_public_url._replace(query=urlencode(filtered_params))

        return urlunparse(items_public_url)

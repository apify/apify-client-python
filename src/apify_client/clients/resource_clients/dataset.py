from __future__ import annotations

import warnings
from contextlib import asynccontextmanager, contextmanager
from typing import TYPE_CHECKING, Any

from apify_shared.models import ListPage
from apify_shared.utils import filter_out_none_values_recursively, ignore_docs

from apify_client._errors import ApifyApiError
from apify_client._utils import catch_not_found_or_throw, pluck_data
from apify_client.clients.base import ResourceClient, ResourceClientAsync

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    import httpx
    from apify_shared.consts import StorageGeneralAccess
    from apify_shared.types import JSONSerializable

_SMALL_TIMEOUT = 5  # For fast and common actions. Suitable for idempotent actions.
_MEDIUM_TIMEOUT = 30  # For actions that may take longer.


class DatasetClient(ResourceClient):
    """Sub-client for manipulating a single dataset."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'datasets')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> dict | None:
        """Retrieve the dataset.

        https://docs.apify.com/api/v2#/reference/datasets/dataset/get-dataset

        Returns:
            The retrieved dataset, or None, if it does not exist.
        """
        return self._get(timeout_secs=_SMALL_TIMEOUT)

    def update(self, *, name: str | None = None, general_access: StorageGeneralAccess | None = None) -> dict:
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

        return self._update(filter_out_none_values_recursively(updated_fields), timeout_secs=_SMALL_TIMEOUT)

    def delete(self) -> None:
        """Delete the dataset.

        https://docs.apify.com/api/v2#/reference/datasets/dataset/delete-dataset
        """
        return self._delete(timeout_secs=_SMALL_TIMEOUT)

    def list_items(
        self,
        *,
        offset: int | None = None,
        limit: int | None = None,
        clean: bool | None = None,
        desc: bool | None = None,
        fields: list[str] | None = None,
        omit: list[str] | None = None,
        # TODO: change to list[str] only when doing a breaking release
        # https://github.com/apify/apify-client-python/issues/255
        unwind: str | list[str] | None = None,
        skip_empty: bool | None = None,
        skip_hidden: bool | None = None,
        flatten: list[str] | None = None,
        view: str | None = None,
    ) -> ListPage:
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

        Returns:
            A page of the list of dataset items according to the specified filters.
        """
        request_params = self._params(
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

        response = self.http_client.call(
            url=self._url('items'),
            method='GET',
            params=request_params,
        )

        data = response.json()

        return ListPage(
            {
                'items': data,
                'total': int(response.headers['x-apify-pagination-total']),
                'offset': int(response.headers['x-apify-pagination-offset']),
                'count': len(
                    data
                ),  # because x-apify-pagination-count returns invalid values when hidden/empty items are skipped
                'limit': int(
                    response.headers['x-apify-pagination-limit']
                ),  # API returns 999999999999 when no limit is used
                'desc': bool(response.headers['x-apify-pagination-desc']),
            }
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
        # TODO: change to list[str] only when doing a breaking release
        # https://github.com/apify/apify-client-python/issues/255
        unwind: str | list[str] | None = None,
        skip_empty: bool | None = None,
        skip_hidden: bool | None = None,
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

        Yields:
            An item from the dataset.
        """
        cache_size = 1000

        should_finish = False
        read_items = 0

        # We can't rely on ListPage.total because that is updated with a delay,
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
        # TODO: change to list[str] only when doing a breaking release
        # https://github.com/apify/apify-client-python/issues/255
        unwind: str | list[str] | None = None,
        skip_empty: bool | None = None,
        skip_header_row: bool | None = None,
        skip_hidden: bool | None = None,
        xml_root: str | None = None,
        xml_row: str | None = None,
        flatten: list[str] | None = None,
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
        # TODO: change to list[str] only when doing a breaking release
        # https://github.com/apify/apify-client-python/issues/255
        unwind: str | list[str] | None = None,
        skip_empty: bool | None = None,
        skip_header_row: bool | None = None,
        skip_hidden: bool | None = None,
        xml_root: str | None = None,
        xml_row: str | None = None,
        flatten: list[str] | None = None,
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

        Returns:
            The dataset items as raw bytes.
        """
        request_params = self._params(
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
        )

        response = self.http_client.call(
            url=self._url('items'),
            method='GET',
            params=request_params,
            parse_response=False,
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
        # TODO: change to list[str] only when doing a breaking release
        # https://github.com/apify/apify-client-python/issues/255
        unwind: str | list[str] | None = None,
        skip_empty: bool | None = None,
        skip_header_row: bool | None = None,
        skip_hidden: bool | None = None,
        xml_root: str | None = None,
        xml_row: str | None = None,
    ) -> Iterator[httpx.Response]:
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

        Returns:
            The dataset items as a context-managed streaming `Response`.
        """
        response = None
        try:
            request_params = self._params(
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
            )

            response = self.http_client.call(
                url=self._url('items'),
                method='GET',
                params=request_params,
                stream=True,
                parse_response=False,
            )
            yield response
        finally:
            if response:
                response.close()

    def push_items(self, items: JSONSerializable) -> None:
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

        self.http_client.call(
            url=self._url('items'),
            method='POST',
            headers={'content-type': 'application/json; charset=utf-8'},
            params=self._params(),
            data=data,
            json=json,
            timeout_secs=_MEDIUM_TIMEOUT,
        )

    def get_statistics(self) -> dict | None:
        """Get the dataset statistics.

        https://docs.apify.com/api/v2#tag/DatasetsStatistics/operation/dataset_statistics_get

        Returns:
            The dataset statistics or None if the dataset does not exist.
        """
        try:
            response = self.http_client.call(
                url=self._url('statistics'),
                method='GET',
                params=self._params(),
                timeout_secs=_SMALL_TIMEOUT,
            )
            return pluck_data(response.json())
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None


class DatasetClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single dataset."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'datasets')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self) -> dict | None:
        """Retrieve the dataset.

        https://docs.apify.com/api/v2#/reference/datasets/dataset/get-dataset

        Returns:
            The retrieved dataset, or None, if it does not exist.
        """
        return await self._get(timeout_secs=_SMALL_TIMEOUT)

    async def update(self, *, name: str | None = None, general_access: StorageGeneralAccess | None = None) -> dict:
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

        return await self._update(filter_out_none_values_recursively(updated_fields), timeout_secs=_SMALL_TIMEOUT)

    async def delete(self) -> None:
        """Delete the dataset.

        https://docs.apify.com/api/v2#/reference/datasets/dataset/delete-dataset
        """
        return await self._delete(timeout_secs=_SMALL_TIMEOUT)

    async def list_items(
        self,
        *,
        offset: int | None = None,
        limit: int | None = None,
        clean: bool | None = None,
        desc: bool | None = None,
        fields: list[str] | None = None,
        omit: list[str] | None = None,
        # TODO: change to list[str] only when doing a breaking release
        # https://github.com/apify/apify-client-python/issues/255
        unwind: str | list[str] | None = None,
        skip_empty: bool | None = None,
        skip_hidden: bool | None = None,
        flatten: list[str] | None = None,
        view: str | None = None,
    ) -> ListPage:
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

        Returns:
            A page of the list of dataset items according to the specified filters.
        """
        request_params = self._params(
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

        response = await self.http_client.call(
            url=self._url('items'),
            method='GET',
            params=request_params,
        )

        data = response.json()

        return ListPage(
            {
                'items': data,
                'total': int(response.headers['x-apify-pagination-total']),
                'offset': int(response.headers['x-apify-pagination-offset']),
                'count': len(
                    data
                ),  # because x-apify-pagination-count returns invalid values when hidden/empty items are skipped
                'limit': int(
                    response.headers['x-apify-pagination-limit']
                ),  # API returns 999999999999 when no limit is used
                'desc': bool(response.headers['x-apify-pagination-desc']),
            }
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
        # TODO: change to list[str] only when doing a breaking release
        # https://github.com/apify/apify-client-python/issues/255
        unwind: str | list[str] | None = None,
        skip_empty: bool | None = None,
        skip_hidden: bool | None = None,
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

        Yields:
            An item from the dataset.
        """
        cache_size = 1000

        should_finish = False
        read_items = 0

        # We can't rely on ListPage.total because that is updated with a delay,
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
        # TODO: change to list[str] only when doing a breaking release
        # https://github.com/apify/apify-client-python/issues/255
        unwind: str | list[str] | None = None,
        skip_empty: bool | None = None,
        skip_header_row: bool | None = None,
        skip_hidden: bool | None = None,
        xml_root: str | None = None,
        xml_row: str | None = None,
        flatten: list[str] | None = None,
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

        Returns:
            The dataset items as raw bytes.
        """
        request_params = self._params(
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
        )

        response = await self.http_client.call(
            url=self._url('items'),
            method='GET',
            params=request_params,
            parse_response=False,
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
        # TODO: change to list[str] only when doing a breaking release
        # https://github.com/apify/apify-client-python/issues/255
        unwind: str | list[str] | None = None,
        skip_empty: bool | None = None,
        skip_header_row: bool | None = None,
        skip_hidden: bool | None = None,
        xml_root: str | None = None,
        xml_row: str | None = None,
    ) -> AsyncIterator[httpx.Response]:
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

        Returns:
            The dataset items as a context-managed streaming `Response`.
        """
        response = None
        try:
            request_params = self._params(
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
            )

            response = await self.http_client.call(
                url=self._url('items'),
                method='GET',
                params=request_params,
                stream=True,
                parse_response=False,
            )
            yield response
        finally:
            if response:
                await response.aclose()

    async def push_items(self, items: JSONSerializable) -> None:
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

        await self.http_client.call(
            url=self._url('items'),
            method='POST',
            headers={'content-type': 'application/json; charset=utf-8'},
            params=self._params(),
            data=data,
            json=json,
            timeout_secs=_MEDIUM_TIMEOUT,
        )

    async def get_statistics(self) -> dict | None:
        """Get the dataset statistics.

        https://docs.apify.com/api/v2#tag/DatasetsStatistics/operation/dataset_statistics_get

        Returns:
            The dataset statistics or None if the dataset does not exist.
        """
        try:
            response = await self.http_client.call(
                url=self._url('statistics'),
                method='GET',
                params=self._params(),
                timeout_secs=_SMALL_TIMEOUT,
            )
            return pluck_data(response.json())
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

import warnings
from contextlib import asynccontextmanager, contextmanager
from typing import Any, AsyncIterator, Dict, Iterator, List, Optional

import httpx

from apify_shared.models import ListPage
from apify_shared.types import JSONSerializable
from apify_shared.utils import filter_out_none_values_recursively, ignore_docs

from ..base import ResourceClient, ResourceClientAsync


class DatasetClient(ResourceClient):
    """Sub-client for manipulating a single dataset."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the DatasetClient."""
        resource_path = kwargs.pop('resource_path', 'datasets')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> Optional[Dict]:
        """Retrieve the dataset.

        https://docs.apify.com/api/v2#/reference/datasets/dataset/get-dataset

        Returns:
            dict, optional: The retrieved dataset, or None, if it does not exist
        """
        return self._get()

    def update(self, *, name: Optional[str] = None) -> Dict:
        """Update the dataset with specified fields.

        https://docs.apify.com/api/v2#/reference/datasets/dataset/update-dataset

        Args:
            name (str, optional): The new name for the dataset

        Returns:
            dict: The updated dataset
        """
        updated_fields = {
            'name': name,
        }

        return self._update(filter_out_none_values_recursively(updated_fields))

    def delete(self) -> None:
        """Delete the dataset.

        https://docs.apify.com/api/v2#/reference/datasets/dataset/delete-dataset
        """
        return self._delete()

    def list_items(
        self,
        *,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        clean: Optional[bool] = None,
        desc: Optional[bool] = None,
        fields: Optional[List[str]] = None,
        omit: Optional[List[str]] = None,
        unwind: Optional[str] = None,
        skip_empty: Optional[bool] = None,
        skip_hidden: Optional[bool] = None,
        flatten: Optional[List[str]] = None,
        view: Optional[str] = None,
    ) -> ListPage:
        """List the items of the dataset.

        https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items

        Args:
            offset (int, optional): Number of items that should be skipped at the start. The default value is 0
            limit (int, optional): Maximum number of items to return. By default there is no limit.
            desc (bool, optional): By default, results are returned in the same order as they were stored.
                To reverse the order, set this parameter to True.
            clean (bool, optional): If True, returns only non-empty items and skips hidden fields (i.e. fields starting with the # character).
                The clean parameter is just a shortcut for skip_hidden=True and skip_empty=True parameters.
                Note that since some objects might be skipped from the output, that the result might contain less items than the limit value.
            fields (list of str, optional): A list of fields which should be picked from the items,
                only these fields will remain in the resulting record objects.
                Note that the fields in the outputted items are sorted the same way as they are specified in the fields parameter.
                You can use this feature to effectively fix the output format.
            omit (list of str, optional): A list of fields which should be omitted from the items.
            unwind (str, optional): Name of a field which should be unwound.
                If the field is an array then every element of the array will become a separate record and merged with parent object.
                If the unwound field is an object then it is merged with the parent object.
                If the unwound field is missing or its value is neither an array nor an object and therefore cannot be merged with a parent object,
                then the item gets preserved as it is. Note that the unwound items ignore the desc parameter.
            skip_empty (bool, optional): If True, then empty items are skipped from the output.
                Note that if used, the results might contain less items than the limit value.
            skip_hidden (bool, optional): If True, then hidden fields are skipped from the output, i.e. fields starting with the # character.
            flatten (list of str, optional): A list of fields that should be flattened
            view (str, optional): Name of the dataset view to be used

        Returns:
            ListPage: A page of the list of dataset items according to the specified filters.
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

        return ListPage({
            'items': data,
            'total': int(response.headers['x-apify-pagination-total']),
            'offset': int(response.headers['x-apify-pagination-offset']),
            'count': len(data),  # because x-apify-pagination-count returns invalid values when hidden/empty items are skipped
            'limit': int(response.headers['x-apify-pagination-limit']),  # API returns 999999999999 when no limit is used
            'desc': bool(response.headers['x-apify-pagination-desc']),
        })

    def iterate_items(
        self,
        *,
        offset: int = 0,
        limit: Optional[int] = None,
        clean: Optional[bool] = None,
        desc: Optional[bool] = None,
        fields: Optional[List[str]] = None,
        omit: Optional[List[str]] = None,
        unwind: Optional[str] = None,
        skip_empty: Optional[bool] = None,
        skip_hidden: Optional[bool] = None,
    ) -> Iterator[Dict]:
        """Iterate over the items in the dataset.

        https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items

        Args:
            offset (int, optional): Number of items that should be skipped at the start. The default value is 0
            limit (int, optional): Maximum number of items to return. By default there is no limit.
            desc (bool, optional): By default, results are returned in the same order as they were stored.
                To reverse the order, set this parameter to True.
            clean (bool, optional): If True, returns only non-empty items and skips hidden fields (i.e. fields starting with the # character).
                The clean parameter is just a shortcut for skip_hidden=True and skip_empty=True parameters.
                Note that since some objects might be skipped from the output, that the result might contain less items than the limit value.
            fields (list of str, optional): A list of fields which should be picked from the items,
                only these fields will remain in the resulting record objects.
                Note that the fields in the outputted items are sorted the same way as they are specified in the fields parameter.
                You can use this feature to effectively fix the output format.
            omit (list of str, optional): A list of fields which should be omitted from the items.
            unwind (str, optional): Name of a field which should be unwound.
                If the field is an array then every element of the array will become a separate record and merged with parent object.
                If the unwound field is an object then it is merged with the parent object.
                If the unwound field is missing or its value is neither an array nor an object and therefore cannot be merged with a parent object,
                then the item gets preserved as it is. Note that the unwound items ignore the desc parameter.
            skip_empty (bool, optional): If True, then empty items are skipped from the output.
                Note that if used, the results might contain less items than the limit value.
            skip_hidden (bool, optional): If True, then hidden fields are skipped from the output, i.e. fields starting with the # character.

        Yields:
            dict: An item from the dataset
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
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        desc: Optional[bool] = None,
        clean: Optional[bool] = None,
        bom: Optional[bool] = None,
        delimiter: Optional[str] = None,
        fields: Optional[List[str]] = None,
        omit: Optional[List[str]] = None,
        unwind: Optional[str] = None,
        skip_empty: Optional[bool] = None,
        skip_header_row: Optional[bool] = None,
        skip_hidden: Optional[bool] = None,
        xml_root: Optional[str] = None,
        xml_row: Optional[str] = None,
        flatten: Optional[List[str]] = None,
    ) -> bytes:
        """Get the items in the dataset as raw bytes.

        Deprecated: this function is a deprecated alias of `get_items_as_bytes`. It will be removed in a future version.

        https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items

        Args:
            item_format (str): Format of the results, possible values are: json, jsonl, csv, html, xlsx, xml and rss. The default value is json.
            offset (int, optional): Number of items that should be skipped at the start. The default value is 0
            limit (int, optional): Maximum number of items to return. By default there is no limit.
            desc (bool, optional): By default, results are returned in the same order as they were stored.
                To reverse the order, set this parameter to True.
            clean (bool, optional): If True, returns only non-empty items and skips hidden fields (i.e. fields starting with the # character).
                The clean parameter is just a shortcut for skip_hidden=True and skip_empty=True parameters.
                Note that since some objects might be skipped from the output, that the result might contain less items than the limit value.
            bom (bool, optional): All text responses are encoded in UTF-8 encoding.
                By default, csv files are prefixed with the UTF-8 Byte Order Mark (BOM),
                while json, jsonl, xml, html and rss files are not. If you want to override this default behavior,
                specify bom=True query parameter to include the BOM or bom=False to skip it.
            delimiter (str, optional): A delimiter character for CSV files. The default delimiter is a simple comma (,).
            fields (list of str, optional): A list of fields which should be picked from the items,
                only these fields will remain in the resulting record objects.
                Note that the fields in the outputted items are sorted the same way as they are specified in the fields parameter.
                You can use this feature to effectively fix the output format.
            omit (list of str, optional): A list of fields which should be omitted from the items.
            unwind (str, optional): Name of a field which should be unwound.
                If the field is an array then every element of the array will become a separate record and merged with parent object.
                If the unwound field is an object then it is merged with the parent object.
                If the unwound field is missing or its value is neither an array nor an object and therefore cannot be merged with a parent object,
                then the item gets preserved as it is. Note that the unwound items ignore the desc parameter.
            skip_empty (bool, optional): If True, then empty items are skipped from the output.
                Note that if used, the results might contain less items than the limit value.
            skip_header_row (bool, optional): If True, then header row in the csv format is skipped.
            skip_hidden (bool, optional): If True, then hidden fields are skipped from the output, i.e. fields starting with the # character.
            xml_root (str, optional): Overrides default root element name of xml output. By default the root element is items.
            xml_row (str, optional): Overrides default element name that wraps each page or page function result object in xml output.
                By default the element name is item.
            flatten (list of str, optional): A list of fields that should be flattened

        Returns:
            bytes: The dataset items as raw bytes
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
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        desc: Optional[bool] = None,
        clean: Optional[bool] = None,
        bom: Optional[bool] = None,
        delimiter: Optional[str] = None,
        fields: Optional[List[str]] = None,
        omit: Optional[List[str]] = None,
        unwind: Optional[str] = None,
        skip_empty: Optional[bool] = None,
        skip_header_row: Optional[bool] = None,
        skip_hidden: Optional[bool] = None,
        xml_root: Optional[str] = None,
        xml_row: Optional[str] = None,
        flatten: Optional[List[str]] = None,
    ) -> bytes:
        """Get the items in the dataset as raw bytes.

        https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items

        Args:
            item_format (str): Format of the results, possible values are: json, jsonl, csv, html, xlsx, xml and rss. The default value is json.
            offset (int, optional): Number of items that should be skipped at the start. The default value is 0
            limit (int, optional): Maximum number of items to return. By default there is no limit.
            desc (bool, optional): By default, results are returned in the same order as they were stored.
                To reverse the order, set this parameter to True.
            clean (bool, optional): If True, returns only non-empty items and skips hidden fields (i.e. fields starting with the # character).
                The clean parameter is just a shortcut for skip_hidden=True and skip_empty=True parameters.
                Note that since some objects might be skipped from the output, that the result might contain less items than the limit value.
            bom (bool, optional): All text responses are encoded in UTF-8 encoding.
                By default, csv files are prefixed with the UTF-8 Byte Order Mark (BOM),
                while json, jsonl, xml, html and rss files are not. If you want to override this default behavior,
                specify bom=True query parameter to include the BOM or bom=False to skip it.
            delimiter (str, optional): A delimiter character for CSV files. The default delimiter is a simple comma (,).
            fields (list of str, optional): A list of fields which should be picked from the items,
                only these fields will remain in the resulting record objects.
                Note that the fields in the outputted items are sorted the same way as they are specified in the fields parameter.
                You can use this feature to effectively fix the output format.
            omit (list of str, optional): A list of fields which should be omitted from the items.
            unwind (str, optional): Name of a field which should be unwound.
                If the field is an array then every element of the array will become a separate record and merged with parent object.
                If the unwound field is an object then it is merged with the parent object.
                If the unwound field is missing or its value is neither an array nor an object and therefore cannot be merged with a parent object,
                then the item gets preserved as it is. Note that the unwound items ignore the desc parameter.
            skip_empty (bool, optional): If True, then empty items are skipped from the output.
                Note that if used, the results might contain less items than the limit value.
            skip_header_row (bool, optional): If True, then header row in the csv format is skipped.
            skip_hidden (bool, optional): If True, then hidden fields are skipped from the output, i.e. fields starting with the # character.
            xml_root (str, optional): Overrides default root element name of xml output. By default the root element is items.
            xml_row (str, optional): Overrides default element name that wraps each page or page function result object in xml output.
                By default the element name is item.
            flatten (list of str, optional): A list of fields that should be flattened

        Returns:
            bytes: The dataset items as raw bytes
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
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        desc: Optional[bool] = None,
        clean: Optional[bool] = None,
        bom: Optional[bool] = None,
        delimiter: Optional[str] = None,
        fields: Optional[List[str]] = None,
        omit: Optional[List[str]] = None,
        unwind: Optional[str] = None,
        skip_empty: Optional[bool] = None,
        skip_header_row: Optional[bool] = None,
        skip_hidden: Optional[bool] = None,
        xml_root: Optional[str] = None,
        xml_row: Optional[str] = None,
    ) -> Iterator[httpx.Response]:
        """Retrieve the items in the dataset as a stream.

        https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items

        Args:
            item_format (str): Format of the results, possible values are: json, jsonl, csv, html, xlsx, xml and rss. The default value is json.
            offset (int, optional): Number of items that should be skipped at the start. The default value is 0
            limit (int, optional): Maximum number of items to return. By default there is no limit.
            desc (bool, optional): By default, results are returned in the same order as they were stored.
                To reverse the order, set this parameter to True.
            clean (bool, optional): If True, returns only non-empty items and skips hidden fields (i.e. fields starting with the # character).
                The clean parameter is just a shortcut for skip_hidden=True and skip_empty=True parameters.
                Note that since some objects might be skipped from the output, that the result might contain less items than the limit value.
            bom (bool, optional): All text responses are encoded in UTF-8 encoding.
                By default, csv files are prefixed with the UTF-8 Byte Order Mark (BOM),
                while json, jsonl, xml, html and rss files are not. If you want to override this default behavior,
                specify bom=True query parameter to include the BOM or bom=False to skip it.
            delimiter (str, optional): A delimiter character for CSV files. The default delimiter is a simple comma (,).
            fields (list of str, optional): A list of fields which should be picked from the items,
                only these fields will remain in the resulting record objects.
                Note that the fields in the outputted items are sorted the same way as they are specified in the fields parameter.
                You can use this feature to effectively fix the output format.
            omit (list of str, optional): A list of fields which should be omitted from the items.
            unwind (str, optional): Name of a field which should be unwound.
                If the field is an array then every element of the array will become a separate record and merged with parent object.
                If the unwound field is an object then it is merged with the parent object.
                If the unwound field is missing or its value is neither an array nor an object and therefore cannot be merged with a parent object,
                then the item gets preserved as it is. Note that the unwound items ignore the desc parameter.
            skip_empty (bool, optional): If True, then empty items are skipped from the output.
                Note that if used, the results might contain less items than the limit value.
            skip_header_row (bool, optional): If True, then header row in the csv format is skipped.
            skip_hidden (bool, optional): If True, then hidden fields are skipped from the output, i.e. fields starting with the # character.
            xml_root (str, optional): Overrides default root element name of xml output. By default the root element is items.
            xml_row (str, optional): Overrides default element name that wraps each page or page function result object in xml output.
                By default the element name is item.

        Returns:
            httpx.Response: The dataset items as a context-managed streaming Response
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
            items: The items which to push in the dataset. Either a stringified JSON, a dictionary, or a list of strings or dictionaries.
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
        )


class DatasetClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single dataset."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the DatasetClientAsync."""
        resource_path = kwargs.pop('resource_path', 'datasets')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self) -> Optional[Dict]:
        """Retrieve the dataset.

        https://docs.apify.com/api/v2#/reference/datasets/dataset/get-dataset

        Returns:
            dict, optional: The retrieved dataset, or None, if it does not exist
        """
        return await self._get()

    async def update(self, *, name: Optional[str] = None) -> Dict:
        """Update the dataset with specified fields.

        https://docs.apify.com/api/v2#/reference/datasets/dataset/update-dataset

        Args:
            name (str, optional): The new name for the dataset

        Returns:
            dict: The updated dataset
        """
        updated_fields = {
            'name': name,
        }

        return await self._update(filter_out_none_values_recursively(updated_fields))

    async def delete(self) -> None:
        """Delete the dataset.

        https://docs.apify.com/api/v2#/reference/datasets/dataset/delete-dataset
        """
        return await self._delete()

    async def list_items(
        self,
        *,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        clean: Optional[bool] = None,
        desc: Optional[bool] = None,
        fields: Optional[List[str]] = None,
        omit: Optional[List[str]] = None,
        unwind: Optional[str] = None,
        skip_empty: Optional[bool] = None,
        skip_hidden: Optional[bool] = None,
        flatten: Optional[List[str]] = None,
        view: Optional[str] = None,
    ) -> ListPage:
        """List the items of the dataset.

        https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items

        Args:
            offset (int, optional): Number of items that should be skipped at the start. The default value is 0
            limit (int, optional): Maximum number of items to return. By default there is no limit.
            desc (bool, optional): By default, results are returned in the same order as they were stored.
                To reverse the order, set this parameter to True.
            clean (bool, optional): If True, returns only non-empty items and skips hidden fields (i.e. fields starting with the # character).
                The clean parameter is just a shortcut for skip_hidden=True and skip_empty=True parameters.
                Note that since some objects might be skipped from the output, that the result might contain less items than the limit value.
            fields (list of str, optional): A list of fields which should be picked from the items,
                only these fields will remain in the resulting record objects.
                Note that the fields in the outputted items are sorted the same way as they are specified in the fields parameter.
                You can use this feature to effectively fix the output format.
            omit (list of str, optional): A list of fields which should be omitted from the items.
            unwind (str, optional): Name of a field which should be unwound.
                If the field is an array then every element of the array will become a separate record and merged with parent object.
                If the unwound field is an object then it is merged with the parent object.
                If the unwound field is missing or its value is neither an array nor an object and therefore cannot be merged with a parent object,
                then the item gets preserved as it is. Note that the unwound items ignore the desc parameter.
            skip_empty (bool, optional): If True, then empty items are skipped from the output.
                Note that if used, the results might contain less items than the limit value.
            skip_hidden (bool, optional): If True, then hidden fields are skipped from the output, i.e. fields starting with the # character.
            flatten (list of str, optional): A list of fields that should be flattened
            view (str, optional): Name of the dataset view to be used

        Returns:
            ListPage: A page of the list of dataset items according to the specified filters.
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

        return ListPage({
            'items': data,
            'total': int(response.headers['x-apify-pagination-total']),
            'offset': int(response.headers['x-apify-pagination-offset']),
            'count': len(data),  # because x-apify-pagination-count returns invalid values when hidden/empty items are skipped
            'limit': int(response.headers['x-apify-pagination-limit']),  # API returns 999999999999 when no limit is used
            'desc': bool(response.headers['x-apify-pagination-desc']),
        })

    async def iterate_items(
        self,
        *,
        offset: int = 0,
        limit: Optional[int] = None,
        clean: Optional[bool] = None,
        desc: Optional[bool] = None,
        fields: Optional[List[str]] = None,
        omit: Optional[List[str]] = None,
        unwind: Optional[str] = None,
        skip_empty: Optional[bool] = None,
        skip_hidden: Optional[bool] = None,
    ) -> AsyncIterator[Dict]:
        """Iterate over the items in the dataset.

        https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items

        Args:
            offset (int, optional): Number of items that should be skipped at the start. The default value is 0
            limit (int, optional): Maximum number of items to return. By default there is no limit.
            desc (bool, optional): By default, results are returned in the same order as they were stored.
                To reverse the order, set this parameter to True.
            clean (bool, optional): If True, returns only non-empty items and skips hidden fields (i.e. fields starting with the # character).
                The clean parameter is just a shortcut for skip_hidden=True and skip_empty=True parameters.
                Note that since some objects might be skipped from the output, that the result might contain less items than the limit value.
            fields (list of str, optional): A list of fields which should be picked from the items,
                only these fields will remain in the resulting record objects.
                Note that the fields in the outputted items are sorted the same way as they are specified in the fields parameter.
                You can use this feature to effectively fix the output format.
            omit (list of str, optional): A list of fields which should be omitted from the items.
            unwind (str, optional): Name of a field which should be unwound.
                If the field is an array then every element of the array will become a separate record and merged with parent object.
                If the unwound field is an object then it is merged with the parent object.
                If the unwound field is missing or its value is neither an array nor an object and therefore cannot be merged with a parent object,
                then the item gets preserved as it is. Note that the unwound items ignore the desc parameter.
            skip_empty (bool, optional): If True, then empty items are skipped from the output.
                Note that if used, the results might contain less items than the limit value.
            skip_hidden (bool, optional): If True, then hidden fields are skipped from the output, i.e. fields starting with the # character.

        Yields:
            dict: An item from the dataset
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
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        desc: Optional[bool] = None,
        clean: Optional[bool] = None,
        bom: Optional[bool] = None,
        delimiter: Optional[str] = None,
        fields: Optional[List[str]] = None,
        omit: Optional[List[str]] = None,
        unwind: Optional[str] = None,
        skip_empty: Optional[bool] = None,
        skip_header_row: Optional[bool] = None,
        skip_hidden: Optional[bool] = None,
        xml_root: Optional[str] = None,
        xml_row: Optional[str] = None,
        flatten: Optional[List[str]] = None,
    ) -> bytes:
        """Get the items in the dataset as raw bytes.

        https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items

        Args:
            item_format (str): Format of the results, possible values are: json, jsonl, csv, html, xlsx, xml and rss. The default value is json.
            offset (int, optional): Number of items that should be skipped at the start. The default value is 0
            limit (int, optional): Maximum number of items to return. By default there is no limit.
            desc (bool, optional): By default, results are returned in the same order as they were stored.
                To reverse the order, set this parameter to True.
            clean (bool, optional): If True, returns only non-empty items and skips hidden fields (i.e. fields starting with the # character).
                The clean parameter is just a shortcut for skip_hidden=True and skip_empty=True parameters.
                Note that since some objects might be skipped from the output, that the result might contain less items than the limit value.
            bom (bool, optional): All text responses are encoded in UTF-8 encoding.
                By default, csv files are prefixed with the UTF-8 Byte Order Mark (BOM),
                while json, jsonl, xml, html and rss files are not. If you want to override this default behavior,
                specify bom=True query parameter to include the BOM or bom=False to skip it.
            delimiter (str, optional): A delimiter character for CSV files. The default delimiter is a simple comma (,).
            fields (list of str, optional): A list of fields which should be picked from the items,
                only these fields will remain in the resulting record objects.
                Note that the fields in the outputted items are sorted the same way as they are specified in the fields parameter.
                You can use this feature to effectively fix the output format.
            omit (list of str, optional): A list of fields which should be omitted from the items.
            unwind (str, optional): Name of a field which should be unwound.
                If the field is an array then every element of the array will become a separate record and merged with parent object.
                If the unwound field is an object then it is merged with the parent object.
                If the unwound field is missing or its value is neither an array nor an object and therefore cannot be merged with a parent object,
                then the item gets preserved as it is. Note that the unwound items ignore the desc parameter.
            skip_empty (bool, optional): If True, then empty items are skipped from the output.
                Note that if used, the results might contain less items than the limit value.
            skip_header_row (bool, optional): If True, then header row in the csv format is skipped.
            skip_hidden (bool, optional): If True, then hidden fields are skipped from the output, i.e. fields starting with the # character.
            xml_root (str, optional): Overrides default root element name of xml output. By default the root element is items.
            xml_row (str, optional): Overrides default element name that wraps each page or page function result object in xml output.
                By default the element name is item.
            flatten (list of str, optional): A list of fields that should be flattened

        Returns:
            bytes: The dataset items as raw bytes
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
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        desc: Optional[bool] = None,
        clean: Optional[bool] = None,
        bom: Optional[bool] = None,
        delimiter: Optional[str] = None,
        fields: Optional[List[str]] = None,
        omit: Optional[List[str]] = None,
        unwind: Optional[str] = None,
        skip_empty: Optional[bool] = None,
        skip_header_row: Optional[bool] = None,
        skip_hidden: Optional[bool] = None,
        xml_root: Optional[str] = None,
        xml_row: Optional[str] = None,
    ) -> AsyncIterator[httpx.Response]:
        """Retrieve the items in the dataset as a stream.

        https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items

        Args:
            item_format (str): Format of the results, possible values are: json, jsonl, csv, html, xlsx, xml and rss. The default value is json.
            offset (int, optional): Number of items that should be skipped at the start. The default value is 0
            limit (int, optional): Maximum number of items to return. By default there is no limit.
            desc (bool, optional): By default, results are returned in the same order as they were stored.
                To reverse the order, set this parameter to True.
            clean (bool, optional): If True, returns only non-empty items and skips hidden fields (i.e. fields starting with the # character).
                The clean parameter is just a shortcut for skip_hidden=True and skip_empty=True parameters.
                Note that since some objects might be skipped from the output, that the result might contain less items than the limit value.
            bom (bool, optional): All text responses are encoded in UTF-8 encoding.
                By default, csv files are prefixed with the UTF-8 Byte Order Mark (BOM),
                while json, jsonl, xml, html and rss files are not. If you want to override this default behavior,
                specify bom=True query parameter to include the BOM or bom=False to skip it.
            delimiter (str, optional): A delimiter character for CSV files. The default delimiter is a simple comma (,).
            fields (list of str, optional): A list of fields which should be picked from the items,
                only these fields will remain in the resulting record objects.
                Note that the fields in the outputted items are sorted the same way as they are specified in the fields parameter.
                You can use this feature to effectively fix the output format.
            omit (list of str, optional): A list of fields which should be omitted from the items.
            unwind (str, optional): Name of a field which should be unwound.
                If the field is an array then every element of the array will become a separate record and merged with parent object.
                If the unwound field is an object then it is merged with the parent object.
                If the unwound field is missing or its value is neither an array nor an object and therefore cannot be merged with a parent object,
                then the item gets preserved as it is. Note that the unwound items ignore the desc parameter.
            skip_empty (bool, optional): If True, then empty items are skipped from the output.
                Note that if used, the results might contain less items than the limit value.
            skip_header_row (bool, optional): If True, then header row in the csv format is skipped.
            skip_hidden (bool, optional): If True, then hidden fields are skipped from the output, i.e. fields starting with the # character.
            xml_root (str, optional): Overrides default root element name of xml output. By default the root element is items.
            xml_row (str, optional): Overrides default element name that wraps each page or page function result object in xml output.
                By default the element name is item.

        Returns:
            httpx.Response: The dataset items as a context-managed streaming Response
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
            items: The items which to push in the dataset. Either a stringified JSON, a dictionary, or a list of strings or dictionaries.
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
        )

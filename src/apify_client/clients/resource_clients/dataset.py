import io
from typing import Any, Dict, Generator, List, Optional, cast

from ..._types import JSONSerializable
from ..._utils import ListPage
from ..base import ResourceClient


class DatasetClient(ResourceClient):
    """Sub-client for manipulating a single dataset."""

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
        updated_fields = {}
        if name is not None:
            updated_fields['name'] = name

        return self._update(updated_fields)

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
    ) -> Generator:
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
        first_item = offset

        # If there is no limit, set last_item to None until we get the total from the first API response
        if limit is None:
            last_item = None
        else:
            last_item = offset + limit

        current_offset = first_item
        while last_item is None or current_offset < last_item:
            if last_item is None:
                current_limit = cache_size
            else:
                current_limit = min(cache_size, last_item - current_offset)

            current_items_page = self.list_items(
                offset=current_offset,
                limit=current_limit,
                clean=clean,
                desc=desc,
                fields=fields,
                omit=omit,
                unwind=unwind,
                skip_empty=skip_empty,
                skip_hidden=skip_hidden,
            )

            current_offset += current_items_page.count
            if last_item is None or current_items_page.total < last_item:
                last_item = current_items_page.total

            yield from current_items_page.items

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
    ) -> bytes:
        """Download the items in the dataset as raw bytes.

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
        )

        response = self.http_client.call(
            url=self._url('items'),
            method='GET',
            params=request_params,
            parse_response=False,
        )

        return response.content

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
    ) -> io.IOBase:
        """Retrieve the items in the dataset as a file-like object.

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
            io.IOBase: The dataset items as a file-like object
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
        )

        response = self.http_client.call(
            url=self._url('items'),
            method='GET',
            params=request_params,
            stream=True,
            parse_response=False,
        )

        response.raw.decode_content = True
        # response.raw is the raw urllib3 response, which subclasses IOBase
        return cast(io.IOBase, response.raw)

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

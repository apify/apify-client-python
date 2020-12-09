from typing import Any, Dict, List, Optional, Union

from ..base.resource_client import ResourceClient


class DatasetClient(ResourceClient):
    """Sub-client for manipulating a single dataset."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes the DatasetClient."""
        super().__init__(*args, resource_path='datasets', **kwargs)

    def get(self) -> Optional[Dict]:
        """Retrieves the dataset.

        https://docs.apify.com/api/v2#/reference/datasets/dataset/get-dataset

        Returns:
            The retrieved dataset
        """
        return self._get()

    def update(self, new_fields: Dict) -> Dict:
        """Updates the dataset with specified fields.

        https://docs.apify.com/api/v2#/reference/datasets/dataset/update-dataset

        Args:
            new_fields (dict): The fields of the dataset to update

        Returns:
            The updated dataset
        """
        return self._update(new_fields)

    def delete(self) -> None:
        """Deletes the dataset.

        https://docs.apify.com/api/v2#/reference/datasets/dataset/delete-dataset
        """
        return self._delete()

    def list_items(
        self,
        *,
        offset: int = None,
        limit: int = None,
        clean: bool = None,
        desc: bool = None,
        fields: List[str] = None,
        omit: List[str] = None,
        unwind: str = None,
        skip_empty: bool = None,
        skip_hidden: bool = None,
    ) -> Dict:
        """Lists the items of the dataset.

        https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items

        Args:
            offset: (int, optional): Number of items that should be skipped at the start. The default value is 0
            limit: (int, optional): Maximum number of items to return. By default there is no limit.
            desc (bool, optional): By default, results are returned in the same order as they were stored.
                To reverse the order, set this parameter to True.
            clean (bool, optional): If True, returns only non-empty items and skips hidden fields (i.e. fields starting with the # character).
                The clean parameter is just a shortcut for skip_hidden=True and skip_empty=True parameters.
                Note that since some objects might be skipped from the output, that the result might contain less items than the limit value.
            fields (list[str], optional): A list of fields which should be picked from the items,
                only these fields will remain in the resulting record objects.
                Note that the fields in the outputted items are sorted the same way as they are specified in the fields parameter.
                You can use this feature to effectively fix the output format.
            omit: (list[str], optional): A list of fields which should be omitted from the items.
            unwind: (str, optional): Name of a field which should be unwound.
                If the field is an array then every element of the array will become a separate record and merged with parent object.
                If the unwound field is an object then it is merged with the parent object.
                If the unwound field is missing or its value is neither an array nor an object and therefore cannot be merged with a parent object,
                then the item gets preserved as it is. Note that the unwound items ignore the desc parameter.
            skip_empty (bool, optional): If True, then empty items are skipped from the output.
                Note that if used, the results might contain less items than the limit value.
            skip_hidden (bool, optional): If True, then hidden fields are skipped from the output, i.e. fields starting with the # character.

        Returns:
            The dataset items
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

        return {
            'items': data,
            'total': int(response.headers['x-apify-pagination-total']),
            'offset': int(response.headers['x-apify-pagination-offset']),
            'count': len(data),  # because x-apify-pagination-count returns invalid values when hidden/empty items are skipped
            'limit': int(response.headers['x-apify-pagination-limit']),  # API returns 999999999999 when no limit is used
        }

    def download_items(
        self,
        download_format: str = 'json',
        *,
        as_file: bool = False,
        offset: int = None,
        limit: int = None,
        desc: bool = None,
        clean: bool = None,
        bom: bool = None,
        delimiter: str = None,
        fields: List[str] = None,
        omit: List[str] = None,
        unwind: str = None,
        skip_empty: bool = None,
        skip_header_row: bool = None,
        skip_hidden: bool = None,
        xml_root: str = None,
        xml_row: str = None,
    ) -> Any:
        """Downloads the items in the dataset, either as raw bytes or as a file-like object.

        https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items

        Args:
            download_format(str): Format of the results, possible values are: json, jsonl, csv, html, xlsx, xml and rss. The default value is json.
            as_file (bool, optional): Whether to retrieve the results as a file-like object
            offset: (int, optional): Number of items that should be skipped at the start. The default value is 0
            limit: (int, optional): Maximum number of items to return. By default there is no limit.
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
            fields (list[str], optional): A list of fields which should be picked from the items,
                only these fields will remain in the resulting record objects.
                Note that the fields in the outputted items are sorted the same way as they are specified in the fields parameter.
                You can use this feature to effectively fix the output format.
            omit: (list[str], optional): A list of fields which should be omitted from the items.
            unwind: (str, optional): Name of a field which should be unwound.
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
            The dataset items in the specified format, either as raw bytes or a file-like object
        """
        request_params = self._params(
            format=download_format,
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
            stream=as_file,
            parse_response=False,
        )

        if as_file:
            response.raw.decode_content = True
            return response.raw
        else:
            return response.content

    def push_items(self, items: Union[str, Dict, List[str], List[Dict]]) -> None:
        """Pushes items to the dataset.

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

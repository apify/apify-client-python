from typing import Any, Dict, List, Optional, Union

from ..base.resource_client import ResourceClient


class DatasetClient(ResourceClient):
    """Sub-client for manipulating a single dataset."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes the DatasetClient."""
        super().__init__(*args, resource_path='datasets', **kwargs)

    def get(self) -> Optional[Dict]:
        """Retrieves the dataset.

        Returns:
            The retrieved dataset
        """
        return self._get()

    def update(self, new_fields: Dict) -> Optional[Dict]:
        """Updates the dataset with specified fields.

        Args:
            new_fields: The fields of the dataset to update

        Returns:
            The updated dataset
        """
        return self._update(new_fields)

    def delete(self) -> None:
        """Deletes the dataset."""
        return self._delete()

    def list_items(
        self,
        *,
        clean: bool = None,
        desc: bool = None,
        fields: List[str] = None,
        omit: List[str] = None,
        limit: int = None,
        offset: int = None,
        skip_empty: bool = None,
        skip_hidden: bool = None,
        unwind: str = None,
    ) -> Dict:
        """Lists the items of the dataset.

        Args:
            clean: TODO
            desc: TODO
            fields: TODO
            omit: TODO
            limit: TODO
            offset: TODO
            skip_empty: TODO
            skip_hidden: TODO
            unwind: TODO

        Returns:
            The dataset items
        """
        request_params = self._params(
            clean=clean,
            desc=desc,
            fields=fields,
            omit=omit,
            limit=limit,
            offset=offset,
            skipEmpty=skip_empty,
            skipHidden=skip_hidden,
            unwind=unwind,
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
        format: str,
        *,
        attachment: bool = None,
        bom: bool = None,
        clean: bool = None,
        delimiter: str = None,
        desc: bool = None,
        fields: List[str] = None,
        omit: List[str] = None,
        limit: int = None,
        offset: int = None,
        skip_empty: bool = None,
        skip_header_row: bool = None,
        skip_hidden: bool = None,
        unwind: str = None,
        xml_root: str = None,
        xml_row: str = None,
    ) -> bytes:
        """Downloads the items in the dataset.

        Args:
            format: TODO
            attachment: TODO
            bom: TODO
            clean: TODO
            delimiter: TODO
            desc: TODO
            fields: TODO
            omit: TODO
            limit: TODO
            offset: TODO
            skip_empty: TODO
            skip_header_row: TODO
            skip_hidden: TODO
            unwind: TODO
            xml_root: TODO
            xml_row: TODO

        Returns:
            The dataset items in the specified format, as bytes
        """
        request_params = self._params(
            format=format,
            attachment=attachment,
            bom=bom,
            clean=clean,
            delimiter=delimiter,
            desc=desc,
            fields=fields,
            omit=omit,
            limit=limit,
            offset=offset,
            skipEmpty=skip_empty,
            skipHeaderRow=skip_header_row,
            skipHidden=skip_hidden,
            unwind=unwind,
            xmlRoot=xml_root,
            xmlRow=xml_row,
        )

        # TODO force_buffer = True

        response = self.http_client.call(
            url=self._url('items'),
            method='GET',
            params=request_params,
        )

        return response.content

    def push_items(self, items: Union[str, Dict, List[Union[str, Dict]]]) -> None:
        """Pushes items to the dataset.

        Args:
            items: The items which to push in the dataset
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

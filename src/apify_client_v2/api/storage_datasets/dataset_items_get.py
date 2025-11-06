from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.dataset_items_get_response_200_item import DatasetItemsGetResponse200Item
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    dataset_id: str,
    *,
    format_: str | Unset = UNSET,
    clean: bool | Unset = UNSET,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    fields: str | Unset = UNSET,
    omit: str | Unset = UNSET,
    unwind: str | Unset = UNSET,
    flatten: str | Unset = UNSET,
    desc: bool | Unset = UNSET,
    attachment: bool | Unset = UNSET,
    delimiter: str | Unset = UNSET,
    bom: bool | Unset = UNSET,
    xml_root: str | Unset = UNSET,
    xml_row: str | Unset = UNSET,
    skip_header_row: bool | Unset = UNSET,
    skip_hidden: bool | Unset = UNSET,
    skip_empty: bool | Unset = UNSET,
    simplified: bool | Unset = UNSET,
    view: str | Unset = UNSET,
    skip_failed_pages: bool | Unset = UNSET,
    signature: str | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["format"] = format_

    params["clean"] = clean

    params["offset"] = offset

    params["limit"] = limit

    params["fields"] = fields

    params["omit"] = omit

    params["unwind"] = unwind

    params["flatten"] = flatten

    params["desc"] = desc

    params["attachment"] = attachment

    params["delimiter"] = delimiter

    params["bom"] = bom

    params["xmlRoot"] = xml_root

    params["xmlRow"] = xml_row

    params["skipHeaderRow"] = skip_header_row

    params["skipHidden"] = skip_hidden

    params["skipEmpty"] = skip_empty

    params["simplified"] = simplified

    params["view"] = view

    params["skipFailedPages"] = skip_failed_pages

    params["signature"] = signature


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/datasets/{dataset_id}/items".format(dataset_id=dataset_id,),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> list[DatasetItemsGetResponse200Item] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = DatasetItemsGetResponse200Item.from_dict(response_200_item_data)



            response_200.append(response_200_item)

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[list[DatasetItemsGetResponse200Item]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    format_: str | Unset = UNSET,
    clean: bool | Unset = UNSET,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    fields: str | Unset = UNSET,
    omit: str | Unset = UNSET,
    unwind: str | Unset = UNSET,
    flatten: str | Unset = UNSET,
    desc: bool | Unset = UNSET,
    attachment: bool | Unset = UNSET,
    delimiter: str | Unset = UNSET,
    bom: bool | Unset = UNSET,
    xml_root: str | Unset = UNSET,
    xml_row: str | Unset = UNSET,
    skip_header_row: bool | Unset = UNSET,
    skip_hidden: bool | Unset = UNSET,
    skip_empty: bool | Unset = UNSET,
    simplified: bool | Unset = UNSET,
    view: str | Unset = UNSET,
    skip_failed_pages: bool | Unset = UNSET,
    signature: str | Unset = UNSET,

) -> Response[list[DatasetItemsGetResponse200Item]]:
    r""" Get items

     Returns data stored in the dataset in a desired format.

    ### Response format

    The format of the response depends on <code>format</code> query parameter.

    The <code>format</code> parameter can have one of the following values:
    <code>json</code>, <code>jsonl</code>, <code>xml</code>, <code>html</code>,
    <code>csv</code>, <code>xlsx</code> and <code>rss</code>.

    The following table describes how each format is treated.

    <table>
      <tr>
        <th>Format</th>
        <th>Items</th>
      </tr>
      <tr>
        <td><code>json</code></td>
        <td rowspan=\"3\">The response is a JSON, JSONL or XML array of raw item objects.</td>
      </tr>
      <tr>
        <td><code>jsonl</code></td>
      </tr>
      <tr>
        <td><code>xml</code></td>
      </tr>
      <tr>
        <td><code>html</code></td>
        <td rowspan=\"3\">The response is a HTML, CSV or XLSX table, where columns correspond to the
        properties of the item and rows correspond to each dataset item.</td>
      </tr>
      <tr>
        <td><code>csv</code></td>
      </tr>
      <tr>
        <td><code>xlsx</code></td>
      </tr>
      <tr>
        <td><code>rss</code></td>
        <td colspan=\"2\">The response is a RSS file. Each item is displayed as child elements of one
        <code>&lt;item&gt;</code>.</td>
      </tr>
    </table>

    Note that CSV, XLSX and HTML tables are limited to 2000 columns and the column names cannot be
    longer than 200 characters.
    JSON, XML and RSS formats do not have such restrictions.

    ### Hidden fields

    The top-level fields starting with the `#` character are considered hidden.
    These are useful to store debugging information and can be omitted from the output by providing the
    `skipHidden=1` or `clean=1` query parameters.
    For example, if you store the following object to the dataset:

    ```
    {
        productName: \"iPhone Xs\",
        description: \"Welcome to the big screens.\"
        #debug: {
            url: \"https://www.apple.com/lae/iphone-xs/\",
            crawledAt: \"2019-01-21T16:06:03.683Z\"
        }
    }
    ```

    The `#debug` field will be considered as hidden and can be omitted from the
    results. This is useful to
    provide nice cleaned data to end users, while keeping debugging info
    available if needed. The Dataset object
    returned by the API contains the number of such clean items in the`dataset.cleanItemCount` property.

    ### XML format extension

    When exporting results to XML or RSS formats, the names of object properties become XML tags and the
    corresponding values become tag's children. For example, the following JavaScript object:

    ```
    {
        name: \"Paul Newman\",
        address: [
            { type: \"home\", street: \"21st\", city: \"Chicago\" },
            { type: \"office\", street: null, city: null }
        ]
    }
    ```

    will be transformed to the following XML snippet:

    ```
    <name>Paul Newman</name>
    <address>
      <type>home</type>
      <street>21st</street>
      <city>Chicago</city>
    </address>
    <address>
      <type>office</type>
      <street/>
      <city/>
    </address>
    ```

    If the JavaScript object contains a property named `@` then its sub-properties are exported as
    attributes of the parent XML
    element.
    If the parent XML element does not have any child elements then its value is taken from a JavaScript
    object property named `#`.

    For example, the following JavaScript object:

    ```
    {
      \"address\": [{
        \"@\": {
          \"type\": \"home\"
        },
        \"street\": \"21st\",
        \"city\": \"Chicago\"
      },
      {
        \"@\": {
          \"type\": \"office\"
        },
        \"#\": 'unknown'
      }]
    }
    ```

    will be transformed to the following XML snippet:

    ```
    <address type=\"home\">
      <street>21st</street>
      <city>Chicago</city>
    </address>
    <address type=\"office\">unknown</address>
    ```

    This feature is also useful to customize your RSS feeds generated for various websites.

    By default the whole result is wrapped in a `<items>` element and each page object is wrapped in a
    `<item>` element.
    You can change this using <code>xmlRoot</code> and <code>xmlRow</code> url parameters.

    ### Pagination

    The generated response supports [pagination](#/introduction/pagination).
    The pagination is always performed with the granularity of a single item, regardless whether
    <code>unwind</code> parameter was provided.
    By default, the **Items** in the response are sorted by the time they were stored to the database,
    therefore you can use pagination to incrementally fetch the items as they are being added.
    No limit exists to how many items can be returned in one response.

    If you specify `desc=1` query parameter, the results are returned in the reverse order than they
    were stored (i.e. from newest to oldest items).
    Note that only the order of **Items** is reversed, but not the order of the `unwind` array elements.

    Args:
        dataset_id (str):  Example: WkzbQMuFYuamGv3YF.
        format_ (str | Unset):  Example: json.
        clean (bool | Unset):
        offset (float | Unset):
        limit (float | Unset):  Example: 99.
        fields (str | Unset):  Example: myValue,myOtherValue.
        omit (str | Unset):  Example: myValue,myOtherValue.
        unwind (str | Unset):  Example: myValue,myOtherValue.
        flatten (str | Unset):  Example: myValue.
        desc (bool | Unset):  Example: True.
        attachment (bool | Unset):  Example: True.
        delimiter (str | Unset):  Example: ;.
        bom (bool | Unset):
        xml_root (str | Unset):  Example: items.
        xml_row (str | Unset):  Example: item.
        skip_header_row (bool | Unset):  Example: True.
        skip_hidden (bool | Unset):
        skip_empty (bool | Unset):
        simplified (bool | Unset):
        view (str | Unset):  Example: overview.
        skip_failed_pages (bool | Unset):
        signature (str | Unset):  Example: 2wTI46Bg8qWQrV7tavlPI.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[DatasetItemsGetResponse200Item]]
     """


    kwargs = _get_kwargs(
        dataset_id=dataset_id,
format_=format_,
clean=clean,
offset=offset,
limit=limit,
fields=fields,
omit=omit,
unwind=unwind,
flatten=flatten,
desc=desc,
attachment=attachment,
delimiter=delimiter,
bom=bom,
xml_root=xml_root,
xml_row=xml_row,
skip_header_row=skip_header_row,
skip_hidden=skip_hidden,
skip_empty=skip_empty,
simplified=simplified,
view=view,
skip_failed_pages=skip_failed_pages,
signature=signature,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    format_: str | Unset = UNSET,
    clean: bool | Unset = UNSET,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    fields: str | Unset = UNSET,
    omit: str | Unset = UNSET,
    unwind: str | Unset = UNSET,
    flatten: str | Unset = UNSET,
    desc: bool | Unset = UNSET,
    attachment: bool | Unset = UNSET,
    delimiter: str | Unset = UNSET,
    bom: bool | Unset = UNSET,
    xml_root: str | Unset = UNSET,
    xml_row: str | Unset = UNSET,
    skip_header_row: bool | Unset = UNSET,
    skip_hidden: bool | Unset = UNSET,
    skip_empty: bool | Unset = UNSET,
    simplified: bool | Unset = UNSET,
    view: str | Unset = UNSET,
    skip_failed_pages: bool | Unset = UNSET,
    signature: str | Unset = UNSET,

) -> list[DatasetItemsGetResponse200Item] | None:
    r""" Get items

     Returns data stored in the dataset in a desired format.

    ### Response format

    The format of the response depends on <code>format</code> query parameter.

    The <code>format</code> parameter can have one of the following values:
    <code>json</code>, <code>jsonl</code>, <code>xml</code>, <code>html</code>,
    <code>csv</code>, <code>xlsx</code> and <code>rss</code>.

    The following table describes how each format is treated.

    <table>
      <tr>
        <th>Format</th>
        <th>Items</th>
      </tr>
      <tr>
        <td><code>json</code></td>
        <td rowspan=\"3\">The response is a JSON, JSONL or XML array of raw item objects.</td>
      </tr>
      <tr>
        <td><code>jsonl</code></td>
      </tr>
      <tr>
        <td><code>xml</code></td>
      </tr>
      <tr>
        <td><code>html</code></td>
        <td rowspan=\"3\">The response is a HTML, CSV or XLSX table, where columns correspond to the
        properties of the item and rows correspond to each dataset item.</td>
      </tr>
      <tr>
        <td><code>csv</code></td>
      </tr>
      <tr>
        <td><code>xlsx</code></td>
      </tr>
      <tr>
        <td><code>rss</code></td>
        <td colspan=\"2\">The response is a RSS file. Each item is displayed as child elements of one
        <code>&lt;item&gt;</code>.</td>
      </tr>
    </table>

    Note that CSV, XLSX and HTML tables are limited to 2000 columns and the column names cannot be
    longer than 200 characters.
    JSON, XML and RSS formats do not have such restrictions.

    ### Hidden fields

    The top-level fields starting with the `#` character are considered hidden.
    These are useful to store debugging information and can be omitted from the output by providing the
    `skipHidden=1` or `clean=1` query parameters.
    For example, if you store the following object to the dataset:

    ```
    {
        productName: \"iPhone Xs\",
        description: \"Welcome to the big screens.\"
        #debug: {
            url: \"https://www.apple.com/lae/iphone-xs/\",
            crawledAt: \"2019-01-21T16:06:03.683Z\"
        }
    }
    ```

    The `#debug` field will be considered as hidden and can be omitted from the
    results. This is useful to
    provide nice cleaned data to end users, while keeping debugging info
    available if needed. The Dataset object
    returned by the API contains the number of such clean items in the`dataset.cleanItemCount` property.

    ### XML format extension

    When exporting results to XML or RSS formats, the names of object properties become XML tags and the
    corresponding values become tag's children. For example, the following JavaScript object:

    ```
    {
        name: \"Paul Newman\",
        address: [
            { type: \"home\", street: \"21st\", city: \"Chicago\" },
            { type: \"office\", street: null, city: null }
        ]
    }
    ```

    will be transformed to the following XML snippet:

    ```
    <name>Paul Newman</name>
    <address>
      <type>home</type>
      <street>21st</street>
      <city>Chicago</city>
    </address>
    <address>
      <type>office</type>
      <street/>
      <city/>
    </address>
    ```

    If the JavaScript object contains a property named `@` then its sub-properties are exported as
    attributes of the parent XML
    element.
    If the parent XML element does not have any child elements then its value is taken from a JavaScript
    object property named `#`.

    For example, the following JavaScript object:

    ```
    {
      \"address\": [{
        \"@\": {
          \"type\": \"home\"
        },
        \"street\": \"21st\",
        \"city\": \"Chicago\"
      },
      {
        \"@\": {
          \"type\": \"office\"
        },
        \"#\": 'unknown'
      }]
    }
    ```

    will be transformed to the following XML snippet:

    ```
    <address type=\"home\">
      <street>21st</street>
      <city>Chicago</city>
    </address>
    <address type=\"office\">unknown</address>
    ```

    This feature is also useful to customize your RSS feeds generated for various websites.

    By default the whole result is wrapped in a `<items>` element and each page object is wrapped in a
    `<item>` element.
    You can change this using <code>xmlRoot</code> and <code>xmlRow</code> url parameters.

    ### Pagination

    The generated response supports [pagination](#/introduction/pagination).
    The pagination is always performed with the granularity of a single item, regardless whether
    <code>unwind</code> parameter was provided.
    By default, the **Items** in the response are sorted by the time they were stored to the database,
    therefore you can use pagination to incrementally fetch the items as they are being added.
    No limit exists to how many items can be returned in one response.

    If you specify `desc=1` query parameter, the results are returned in the reverse order than they
    were stored (i.e. from newest to oldest items).
    Note that only the order of **Items** is reversed, but not the order of the `unwind` array elements.

    Args:
        dataset_id (str):  Example: WkzbQMuFYuamGv3YF.
        format_ (str | Unset):  Example: json.
        clean (bool | Unset):
        offset (float | Unset):
        limit (float | Unset):  Example: 99.
        fields (str | Unset):  Example: myValue,myOtherValue.
        omit (str | Unset):  Example: myValue,myOtherValue.
        unwind (str | Unset):  Example: myValue,myOtherValue.
        flatten (str | Unset):  Example: myValue.
        desc (bool | Unset):  Example: True.
        attachment (bool | Unset):  Example: True.
        delimiter (str | Unset):  Example: ;.
        bom (bool | Unset):
        xml_root (str | Unset):  Example: items.
        xml_row (str | Unset):  Example: item.
        skip_header_row (bool | Unset):  Example: True.
        skip_hidden (bool | Unset):
        skip_empty (bool | Unset):
        simplified (bool | Unset):
        view (str | Unset):  Example: overview.
        skip_failed_pages (bool | Unset):
        signature (str | Unset):  Example: 2wTI46Bg8qWQrV7tavlPI.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[DatasetItemsGetResponse200Item]
     """


    return sync_detailed(
        dataset_id=dataset_id,
client=client,
format_=format_,
clean=clean,
offset=offset,
limit=limit,
fields=fields,
omit=omit,
unwind=unwind,
flatten=flatten,
desc=desc,
attachment=attachment,
delimiter=delimiter,
bom=bom,
xml_root=xml_root,
xml_row=xml_row,
skip_header_row=skip_header_row,
skip_hidden=skip_hidden,
skip_empty=skip_empty,
simplified=simplified,
view=view,
skip_failed_pages=skip_failed_pages,
signature=signature,

    ).parsed

async def asyncio_detailed(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    format_: str | Unset = UNSET,
    clean: bool | Unset = UNSET,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    fields: str | Unset = UNSET,
    omit: str | Unset = UNSET,
    unwind: str | Unset = UNSET,
    flatten: str | Unset = UNSET,
    desc: bool | Unset = UNSET,
    attachment: bool | Unset = UNSET,
    delimiter: str | Unset = UNSET,
    bom: bool | Unset = UNSET,
    xml_root: str | Unset = UNSET,
    xml_row: str | Unset = UNSET,
    skip_header_row: bool | Unset = UNSET,
    skip_hidden: bool | Unset = UNSET,
    skip_empty: bool | Unset = UNSET,
    simplified: bool | Unset = UNSET,
    view: str | Unset = UNSET,
    skip_failed_pages: bool | Unset = UNSET,
    signature: str | Unset = UNSET,

) -> Response[list[DatasetItemsGetResponse200Item]]:
    r""" Get items

     Returns data stored in the dataset in a desired format.

    ### Response format

    The format of the response depends on <code>format</code> query parameter.

    The <code>format</code> parameter can have one of the following values:
    <code>json</code>, <code>jsonl</code>, <code>xml</code>, <code>html</code>,
    <code>csv</code>, <code>xlsx</code> and <code>rss</code>.

    The following table describes how each format is treated.

    <table>
      <tr>
        <th>Format</th>
        <th>Items</th>
      </tr>
      <tr>
        <td><code>json</code></td>
        <td rowspan=\"3\">The response is a JSON, JSONL or XML array of raw item objects.</td>
      </tr>
      <tr>
        <td><code>jsonl</code></td>
      </tr>
      <tr>
        <td><code>xml</code></td>
      </tr>
      <tr>
        <td><code>html</code></td>
        <td rowspan=\"3\">The response is a HTML, CSV or XLSX table, where columns correspond to the
        properties of the item and rows correspond to each dataset item.</td>
      </tr>
      <tr>
        <td><code>csv</code></td>
      </tr>
      <tr>
        <td><code>xlsx</code></td>
      </tr>
      <tr>
        <td><code>rss</code></td>
        <td colspan=\"2\">The response is a RSS file. Each item is displayed as child elements of one
        <code>&lt;item&gt;</code>.</td>
      </tr>
    </table>

    Note that CSV, XLSX and HTML tables are limited to 2000 columns and the column names cannot be
    longer than 200 characters.
    JSON, XML and RSS formats do not have such restrictions.

    ### Hidden fields

    The top-level fields starting with the `#` character are considered hidden.
    These are useful to store debugging information and can be omitted from the output by providing the
    `skipHidden=1` or `clean=1` query parameters.
    For example, if you store the following object to the dataset:

    ```
    {
        productName: \"iPhone Xs\",
        description: \"Welcome to the big screens.\"
        #debug: {
            url: \"https://www.apple.com/lae/iphone-xs/\",
            crawledAt: \"2019-01-21T16:06:03.683Z\"
        }
    }
    ```

    The `#debug` field will be considered as hidden and can be omitted from the
    results. This is useful to
    provide nice cleaned data to end users, while keeping debugging info
    available if needed. The Dataset object
    returned by the API contains the number of such clean items in the`dataset.cleanItemCount` property.

    ### XML format extension

    When exporting results to XML or RSS formats, the names of object properties become XML tags and the
    corresponding values become tag's children. For example, the following JavaScript object:

    ```
    {
        name: \"Paul Newman\",
        address: [
            { type: \"home\", street: \"21st\", city: \"Chicago\" },
            { type: \"office\", street: null, city: null }
        ]
    }
    ```

    will be transformed to the following XML snippet:

    ```
    <name>Paul Newman</name>
    <address>
      <type>home</type>
      <street>21st</street>
      <city>Chicago</city>
    </address>
    <address>
      <type>office</type>
      <street/>
      <city/>
    </address>
    ```

    If the JavaScript object contains a property named `@` then its sub-properties are exported as
    attributes of the parent XML
    element.
    If the parent XML element does not have any child elements then its value is taken from a JavaScript
    object property named `#`.

    For example, the following JavaScript object:

    ```
    {
      \"address\": [{
        \"@\": {
          \"type\": \"home\"
        },
        \"street\": \"21st\",
        \"city\": \"Chicago\"
      },
      {
        \"@\": {
          \"type\": \"office\"
        },
        \"#\": 'unknown'
      }]
    }
    ```

    will be transformed to the following XML snippet:

    ```
    <address type=\"home\">
      <street>21st</street>
      <city>Chicago</city>
    </address>
    <address type=\"office\">unknown</address>
    ```

    This feature is also useful to customize your RSS feeds generated for various websites.

    By default the whole result is wrapped in a `<items>` element and each page object is wrapped in a
    `<item>` element.
    You can change this using <code>xmlRoot</code> and <code>xmlRow</code> url parameters.

    ### Pagination

    The generated response supports [pagination](#/introduction/pagination).
    The pagination is always performed with the granularity of a single item, regardless whether
    <code>unwind</code> parameter was provided.
    By default, the **Items** in the response are sorted by the time they were stored to the database,
    therefore you can use pagination to incrementally fetch the items as they are being added.
    No limit exists to how many items can be returned in one response.

    If you specify `desc=1` query parameter, the results are returned in the reverse order than they
    were stored (i.e. from newest to oldest items).
    Note that only the order of **Items** is reversed, but not the order of the `unwind` array elements.

    Args:
        dataset_id (str):  Example: WkzbQMuFYuamGv3YF.
        format_ (str | Unset):  Example: json.
        clean (bool | Unset):
        offset (float | Unset):
        limit (float | Unset):  Example: 99.
        fields (str | Unset):  Example: myValue,myOtherValue.
        omit (str | Unset):  Example: myValue,myOtherValue.
        unwind (str | Unset):  Example: myValue,myOtherValue.
        flatten (str | Unset):  Example: myValue.
        desc (bool | Unset):  Example: True.
        attachment (bool | Unset):  Example: True.
        delimiter (str | Unset):  Example: ;.
        bom (bool | Unset):
        xml_root (str | Unset):  Example: items.
        xml_row (str | Unset):  Example: item.
        skip_header_row (bool | Unset):  Example: True.
        skip_hidden (bool | Unset):
        skip_empty (bool | Unset):
        simplified (bool | Unset):
        view (str | Unset):  Example: overview.
        skip_failed_pages (bool | Unset):
        signature (str | Unset):  Example: 2wTI46Bg8qWQrV7tavlPI.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[DatasetItemsGetResponse200Item]]
     """


    kwargs = _get_kwargs(
        dataset_id=dataset_id,
format_=format_,
clean=clean,
offset=offset,
limit=limit,
fields=fields,
omit=omit,
unwind=unwind,
flatten=flatten,
desc=desc,
attachment=attachment,
delimiter=delimiter,
bom=bom,
xml_root=xml_root,
xml_row=xml_row,
skip_header_row=skip_header_row,
skip_hidden=skip_hidden,
skip_empty=skip_empty,
simplified=simplified,
view=view,
skip_failed_pages=skip_failed_pages,
signature=signature,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    dataset_id: str,
    *,
    client: AuthenticatedClient | Client,
    format_: str | Unset = UNSET,
    clean: bool | Unset = UNSET,
    offset: float | Unset = UNSET,
    limit: float | Unset = UNSET,
    fields: str | Unset = UNSET,
    omit: str | Unset = UNSET,
    unwind: str | Unset = UNSET,
    flatten: str | Unset = UNSET,
    desc: bool | Unset = UNSET,
    attachment: bool | Unset = UNSET,
    delimiter: str | Unset = UNSET,
    bom: bool | Unset = UNSET,
    xml_root: str | Unset = UNSET,
    xml_row: str | Unset = UNSET,
    skip_header_row: bool | Unset = UNSET,
    skip_hidden: bool | Unset = UNSET,
    skip_empty: bool | Unset = UNSET,
    simplified: bool | Unset = UNSET,
    view: str | Unset = UNSET,
    skip_failed_pages: bool | Unset = UNSET,
    signature: str | Unset = UNSET,

) -> list[DatasetItemsGetResponse200Item] | None:
    r""" Get items

     Returns data stored in the dataset in a desired format.

    ### Response format

    The format of the response depends on <code>format</code> query parameter.

    The <code>format</code> parameter can have one of the following values:
    <code>json</code>, <code>jsonl</code>, <code>xml</code>, <code>html</code>,
    <code>csv</code>, <code>xlsx</code> and <code>rss</code>.

    The following table describes how each format is treated.

    <table>
      <tr>
        <th>Format</th>
        <th>Items</th>
      </tr>
      <tr>
        <td><code>json</code></td>
        <td rowspan=\"3\">The response is a JSON, JSONL or XML array of raw item objects.</td>
      </tr>
      <tr>
        <td><code>jsonl</code></td>
      </tr>
      <tr>
        <td><code>xml</code></td>
      </tr>
      <tr>
        <td><code>html</code></td>
        <td rowspan=\"3\">The response is a HTML, CSV or XLSX table, where columns correspond to the
        properties of the item and rows correspond to each dataset item.</td>
      </tr>
      <tr>
        <td><code>csv</code></td>
      </tr>
      <tr>
        <td><code>xlsx</code></td>
      </tr>
      <tr>
        <td><code>rss</code></td>
        <td colspan=\"2\">The response is a RSS file. Each item is displayed as child elements of one
        <code>&lt;item&gt;</code>.</td>
      </tr>
    </table>

    Note that CSV, XLSX and HTML tables are limited to 2000 columns and the column names cannot be
    longer than 200 characters.
    JSON, XML and RSS formats do not have such restrictions.

    ### Hidden fields

    The top-level fields starting with the `#` character are considered hidden.
    These are useful to store debugging information and can be omitted from the output by providing the
    `skipHidden=1` or `clean=1` query parameters.
    For example, if you store the following object to the dataset:

    ```
    {
        productName: \"iPhone Xs\",
        description: \"Welcome to the big screens.\"
        #debug: {
            url: \"https://www.apple.com/lae/iphone-xs/\",
            crawledAt: \"2019-01-21T16:06:03.683Z\"
        }
    }
    ```

    The `#debug` field will be considered as hidden and can be omitted from the
    results. This is useful to
    provide nice cleaned data to end users, while keeping debugging info
    available if needed. The Dataset object
    returned by the API contains the number of such clean items in the`dataset.cleanItemCount` property.

    ### XML format extension

    When exporting results to XML or RSS formats, the names of object properties become XML tags and the
    corresponding values become tag's children. For example, the following JavaScript object:

    ```
    {
        name: \"Paul Newman\",
        address: [
            { type: \"home\", street: \"21st\", city: \"Chicago\" },
            { type: \"office\", street: null, city: null }
        ]
    }
    ```

    will be transformed to the following XML snippet:

    ```
    <name>Paul Newman</name>
    <address>
      <type>home</type>
      <street>21st</street>
      <city>Chicago</city>
    </address>
    <address>
      <type>office</type>
      <street/>
      <city/>
    </address>
    ```

    If the JavaScript object contains a property named `@` then its sub-properties are exported as
    attributes of the parent XML
    element.
    If the parent XML element does not have any child elements then its value is taken from a JavaScript
    object property named `#`.

    For example, the following JavaScript object:

    ```
    {
      \"address\": [{
        \"@\": {
          \"type\": \"home\"
        },
        \"street\": \"21st\",
        \"city\": \"Chicago\"
      },
      {
        \"@\": {
          \"type\": \"office\"
        },
        \"#\": 'unknown'
      }]
    }
    ```

    will be transformed to the following XML snippet:

    ```
    <address type=\"home\">
      <street>21st</street>
      <city>Chicago</city>
    </address>
    <address type=\"office\">unknown</address>
    ```

    This feature is also useful to customize your RSS feeds generated for various websites.

    By default the whole result is wrapped in a `<items>` element and each page object is wrapped in a
    `<item>` element.
    You can change this using <code>xmlRoot</code> and <code>xmlRow</code> url parameters.

    ### Pagination

    The generated response supports [pagination](#/introduction/pagination).
    The pagination is always performed with the granularity of a single item, regardless whether
    <code>unwind</code> parameter was provided.
    By default, the **Items** in the response are sorted by the time they were stored to the database,
    therefore you can use pagination to incrementally fetch the items as they are being added.
    No limit exists to how many items can be returned in one response.

    If you specify `desc=1` query parameter, the results are returned in the reverse order than they
    were stored (i.e. from newest to oldest items).
    Note that only the order of **Items** is reversed, but not the order of the `unwind` array elements.

    Args:
        dataset_id (str):  Example: WkzbQMuFYuamGv3YF.
        format_ (str | Unset):  Example: json.
        clean (bool | Unset):
        offset (float | Unset):
        limit (float | Unset):  Example: 99.
        fields (str | Unset):  Example: myValue,myOtherValue.
        omit (str | Unset):  Example: myValue,myOtherValue.
        unwind (str | Unset):  Example: myValue,myOtherValue.
        flatten (str | Unset):  Example: myValue.
        desc (bool | Unset):  Example: True.
        attachment (bool | Unset):  Example: True.
        delimiter (str | Unset):  Example: ;.
        bom (bool | Unset):
        xml_root (str | Unset):  Example: items.
        xml_row (str | Unset):  Example: item.
        skip_header_row (bool | Unset):  Example: True.
        skip_hidden (bool | Unset):
        skip_empty (bool | Unset):
        simplified (bool | Unset):
        view (str | Unset):  Example: overview.
        skip_failed_pages (bool | Unset):
        signature (str | Unset):  Example: 2wTI46Bg8qWQrV7tavlPI.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[DatasetItemsGetResponse200Item]
     """


    return (await asyncio_detailed(
        dataset_id=dataset_id,
client=client,
format_=format_,
clean=clean,
offset=offset,
limit=limit,
fields=fields,
omit=omit,
unwind=unwind,
flatten=flatten,
desc=desc,
attachment=attachment,
delimiter=delimiter,
bom=bom,
xml_root=xml_root,
xml_row=xml_row,
skip_header_row=skip_header_row,
skip_hidden=skip_hidden,
skip_empty=skip_empty,
simplified=simplified,
view=view,
skip_failed_pages=skip_failed_pages,
signature=signature,

    )).parsed

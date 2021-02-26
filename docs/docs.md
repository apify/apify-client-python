# Apify API client for Python

`apify_client` is the official library to access the [Apify API](https://docs.apify.com/api/v2) from your Python applications.
It provides useful features like automatic retries and convenience functions that improve the experience of using the Apify API.

* [Quick Start](#quick-start)
* [Features](#features)
  * [Automatic parsing and error handling](#automatic-parsing-and-error-handling)
  * [Retries with exponential backoff](#retries-with-exponential-backoff)
  * [Convenience functions and options](#convenience-functions-and-options)
* [Usage concepts](#usage-concepts)
  * [Nested clients](#nested-clients)
  * [Pagination](#pagination)
* [API Reference](#api-reference)

## Installation

Requires Python 3.7+

Right now the client is not available on PyPI yet, so you can install it only from its [git repo](https://github.com/apify/apify-client-python).
To do that, run `pip install git+https://github.com/apify/apify-client-python.git`

## Quick Start

```python
from apify_client import ApifyClient

apify_client = ApifyClient('MY-APIFY-TOKEN')

# Start an actor and waits for it to finish
actor_call = apify_client.actor('john-doe/my-cool-actor').call()

# Fetch results from the actor's default dataset
dataset_items = apify_client.dataset(actor_call['defaultDatasetId']).list_items()['items']
```

## Features

Besides greatly simplifying the process of querying the Apify API, the client provides other useful features.

### Automatic parsing and error handling

Based on the endpoint, the client automatically extracts the relevant data and returns it in the
expected format. Date strings are automatically converted to `datetime.datetime` objects. For exceptions,
we throw an `ApifyApiError`, which wraps the plain JSON errors returned by API and enriches
them with other context for easier debugging.

### Retries with exponential backoff

Network communication sometimes fails. The client will automatically retry requests that
failed due to a network error, an internal error of the Apify API (HTTP 500+) or rate limit error (HTTP 429).
By default, it will retry up to 8 times. First retry will be attempted after ~500ms, second after ~1000ms
and so on. You can configure those parameters using the `max_retries` and `min_delay_between_retries_millis`
options of the `ApifyClient` constructor.

### Convenience functions and options

Some actions can't be performed by the API itself, such as indefinite waiting for an actor run to finish
(because of network timeouts). The client provides convenient `call()` and `wait_for_finish()` functions that do that.
Key-value store records can be retrieved as objects, buffers or streams via the respective options, dataset items
can be fetched as individual objects or serialized data and we plan to add better stream support and async iterators.

## Usage concepts

The `ApifyClient` interface follows a generic pattern that is applicable to all of its components.
By calling individual methods of `ApifyClient`, specific clients which target individual API
resources are created. There are two types of those clients. A client for management of a single
resource and a client for a collection of resources.

```python
from apify_client import ApifyClient
apify_client = ApifyClient('MY-APIFY-TOKEN')

# Collection clients do not require a parameter
actor_collection_client = apify_client.actors()
# Create an actor with the name: my-actor
my_actor = actor_collection_client.create({ name: 'my-actor' })
# List all of your actors
actor_list = actor_collection_client.list()['items']
```

```python
# Collection clients do not require a parameter
dataset_collection_client = apify_client.datasets()
# Get (or create, if it doesn't exist) a dataset with the name of my-dataset
my_dataset = dataset_collection_client.get_or_create('my-dataset')
```

```python
# Resource clients accept an ID of the resource
actor_client = apify_client.actor('john-doe/my-actor')
# Fetch the john-doe/my-actor object from the API
my_actor = actor_client.get()
# Start the run of john-doe/my-actor and return the Run object
my_actor_run = actor_client.start();
```

```python
# Resource clients accept an ID of the resource
dataset_client = apify_client.dataset('john-doe/my-dataset')
# Append items to the end of john-doe/my-dataset
dataset_client.push_items([{ "foo": 1 }, { "bar": 2 }])
```

> The ID of the resource can be either the `id` of the said resource,
> or a combination of your `username/resource-name`.

This is really all you need to remember, because all resource clients
follow the pattern you see above.

### Nested clients

Sometimes clients return other clients. That's to simplify working with
nested collections, such as runs of a given actor.

```python
actor_client = apify_client.actor('john-doe/my-actor')
runs_client = actor_client.runs()
# List the last 10 runs of the john-doe/hello-world actor
actor_runs = runs_client.list(limit=10, desc=True)['items']

# Select the last run of the john-doe/hello-world actor that finished with a SUCCEEDED status
last_succeeded_run_client = actor_client.last_run(status='SUCCEEDED')
# Fetch items from the run's dataset
dataset_items = last_succeeded_run_client.dataset().list_items()['items']
```

> The quick access to `dataset` and other storages directly from the run
> client can now only be used with the `last_run()` method, but the feature
> will be available to all runs in the future.

### Pagination

Most methods named `list` or `list_something` return a pagination dictionary,
containing keys `items`, `total`, `offset`, `count` and `limit`.
There are some exceptions though, like `list_keys` or `list_head` which paginate differently.
The results you're looking for are always stored under `items` and you can use the `limit`
property to get only a subset of results. Other props can be available depending on the method.

## API Reference

All public classes, methods and their parameters can be inspected in this API reference.

### [](#apifyclient) ApifyClient

The Apify API client.

* [\_\_init\_\_()](#apifyclient-\_\_init\_\_)
* [build()](#apifyclient-build)
* [builds()](#apifyclient-builds)
* [dataset()](#apifyclient-dataset)
* [datasets()](#apifyclient-datasets)
* [key\_value\_store()](#apifyclient-key\_value\_store)
* [key\_value\_stores()](#apifyclient-key\_value\_stores)
* [request\_queue()](#apifyclient-request\_queue)
* [request\_queues()](#apifyclient-request\_queues)
* [webhook()](#apifyclient-webhook)
* [webhooks()](#apifyclient-webhooks)
* [webhook\_dispatch()](#apifyclient-webhook\_dispatch)
* [webhook\_dispatches()](#apifyclient-webhook\_dispatches)
* [schedule()](#apifyclient-schedule)
* [schedules()](#apifyclient-schedules)
* [log()](#apifyclient-log)
* [task()](#apifyclient-task)
* [tasks()](#apifyclient-tasks)
* [user()](#apifyclient-user)

***

#### [](#apifyclient-__init__) `ApifyClient.__init__(token=None, *, base_url='https://api.apify.com/v2', max_retries=8, min_delay_between_retries_millis=500)`

Initialize the Apify API Client.

* **Parameters**

  * **token** (`str`, *optional*) – The Apify API token

  * **base_url** (`str`, *optional*) – The URL of the Apify API server to which to connect to. Defaults to [https://api.apify.com/v2](https://api.apify.com/v2)

  * **max_retries** (`int`, *optional*) – How many times to retry a failed request at most

  * **min_delay_between_retries_millis** (`int`, *optional*) – How long will the client wait between retrying requests
  (increases exponentially from this value)

***

#### [](#apifyclient-build) `ApifyClient.build(build_id)`

Retrieve the sub-client for manipulating a single actor build.

* **Parameters**

  * **build_id** (`str`) – ID of the actor build to be manipulated

* **Return type**

  [`BuildClient`](#buildclient)

***

#### [](#apifyclient-builds) `ApifyClient.builds()`

Retrieve the sub-client for querying multiple builds of a user.

* **Return type**

  [`BuildCollectionClient`](#buildcollectionclient)

***

#### [](#apifyclient-dataset) `ApifyClient.dataset(dataset_id)`

Retrieve the sub-client for manipulating a single dataset.

* **Parameters**

  * **dataset_id** (`str`) – ID of the dataset to be manipulated

* **Return type**

  [`DatasetClient`](#datasetclient)

***

#### [](#apifyclient-datasets) `ApifyClient.datasets()`

Retrieve the sub-client for manipulating datasets.

* **Return type**

  [`DatasetCollectionClient`](#datasetcollectionclient)

***

#### [](#apifyclient-key_value_store) `ApifyClient.key_value_store(key_value_store_id)`

Retrieve the sub-client for manipulating a single key-value store.

* **Parameters**

  * **key_value_store_id** (`str`) – ID of the key-value store to be manipulated

* **Return type**

  [`KeyValueStoreClient`](#keyvaluestoreclient)

***

#### [](#apifyclient-key_value_stores) `ApifyClient.key_value_stores()`

Retrieve the sub-client for manipulating key-value stores.

* **Return type**

  [`KeyValueStoreCollectionClient`](#keyvaluestorecollectionclient)

***

#### [](#apifyclient-request_queue) `ApifyClient.request_queue(request_queue_id, *, client_key=None)`

Retrieve the sub-client for manipulating a single request queue.

* **Parameters**

  * **request_queue_id** (`str`) – ID of the request queue to be manipulated

  * **client_key** (`str`) – A unique identifier of the client accessing the request queue

* **Return type**

  [`RequestQueueClient`](#requestqueueclient)

***

#### [](#apifyclient-request_queues) `ApifyClient.request_queues()`

Retrieve the sub-client for manipulating request queues.

* **Return type**

  [`RequestQueueCollectionClient`](#requestqueuecollectionclient)

***

#### [](#apifyclient-webhook) `ApifyClient.webhook(webhook_id)`

Retrieve the sub-client for manipulating a single webhook.

* **Parameters**

  * **webhook_id** (`str`) – ID of the webhook to be manipulated

* **Return type**

  [`WebhookClient`](#webhookclient)

***

#### [](#apifyclient-webhooks) `ApifyClient.webhooks()`

Retrieve the sub-client for querying multiple webhooks of a user.

* **Return type**

  [`WebhookCollectionClient`](#webhookcollectionclient)

***

#### [](#apifyclient-webhook_dispatch) `ApifyClient.webhook_dispatch(webhook_dispatch_id)`

Retrieve the sub-client for accessing a single webhook dispatch.

* **Parameters**

  * **webhook_dispatch_id** (`str`) – ID of the webhook dispatch to access

* **Return type**

  [`WebhookDispatchClient`](#webhookdispatchclient)

***

#### [](#apifyclient-webhook_dispatches) `ApifyClient.webhook_dispatches()`

Retrieve the sub-client for querying multiple webhook dispatches of a user.

* **Return type**

  [`WebhookDispatchCollectionClient`](#webhookdispatchcollectionclient)

***

#### [](#apifyclient-schedule) `ApifyClient.schedule(schedule_id)`

Retrieve the sub-client for manipulating a single schedule.

* **Parameters**

  * **schedule_id** (`str`) – ID of the schedule to be manipulated

* **Return type**

  [`ScheduleClient`](#scheduleclient)

***

#### [](#apifyclient-schedules) `ApifyClient.schedules()`

Retrieve the sub-client for manipulating schedules.

* **Return type**

  [`ScheduleCollectionClient`](#schedulecollectionclient)

***

#### [](#apifyclient-log) `ApifyClient.log(build_or_run_id)`

Retrieve the sub-client for retrieving logs.

* **Parameters**

  * **build_or_run_id** (`str`) – ID of the actor build or run for which to access the log

* **Return type**

  [`LogClient`](#logclient)

***

#### [](#apifyclient-task) `ApifyClient.task(task_id)`

Retrieve the sub-client for manipulating a single task.

* **Parameters**

  * **task_id** (`str`) – ID of the task to be manipulated

* **Return type**

  [`TaskClient`](#taskclient)

***

#### [](#apifyclient-tasks) `ApifyClient.tasks()`

Retrieve the sub-client for retrieving tasks.

* **Return type**

  [`TaskCollectionClient`](#taskcollectionclient)

***

#### [](#apifyclient-user) `ApifyClient.user(user_id=None)`

Retrieve the sub-client for querying users.

* **Parameters**

  * **user_id** (`str`, *optional*) – ID of user to be queried. If `None`, queries the user belonging to the token supplied to the client

* **Return type**

  [`UserClient`](#userclient)

***

### [](#buildclient) BuildClient

Sub-client for manipulating a single actor build.

* [get()](#buildclient-get)
* [abort()](#buildclient-abort)
* [wait\_for\_finish()](#buildclient-wait\_for\_finish)

***

#### [](#buildclient-get) `BuildClient.get()`

Return information about the actor build.

[https://docs.apify.com/api/v2#/reference/actor-builds/build-object/get-build](https://docs.apify.com/api/v2#/reference/actor-builds/build-object/get-build)

* **Returns**

  The retrieved actor build data

* **Return type**

  `dict`

***

#### [](#buildclient-abort) `BuildClient.abort()`

Abort the actor build which is starting or currently running and return its details.

[https://docs.apify.com/api/v2#/reference/actor-builds/abort-build/abort-build](https://docs.apify.com/api/v2#/reference/actor-builds/abort-build/abort-build)

* **Returns**

  The data of the aborted actor build

* **Return type**

  `dict`

***

#### [](#buildclient-wait_for_finish) `BuildClient.wait_for_finish(*, wait_secs=None)`

Wait synchronously until the build finishes or the server times out.

* **Parameters**

  * **wait_secs** (`int`, *optional*) – how long does the client wait for build to finish. `None` for indefinite.

* **Returns**

  The actor build data. If the status on the object is not one of the terminal statuses

    (SUCEEDED, FAILED, TIMED_OUT, ABORTED), then the build has not yet finished.

* **Return type**

  `dict`, optional

***

### [](#buildcollectionclient) BuildCollectionClient

Sub-client for listing user builds.

Note that this client is not specific for a particular actor but queries all builds for a user based on the provided API token.

* [list()](#buildcollectionclient-list)

***

#### [](#buildcollectionclient-list) `BuildCollectionClient.list(*, limit=None, offset=None, desc=None)`

List all builds of a user.

[https://docs.apify.com/api/v2#/reference/actor-builds/build-collection/get-user-builds-list](https://docs.apify.com/api/v2#/reference/actor-builds/build-collection/get-user-builds-list)

* **Parameters**

  * **limit** (`int`, *optional*) – How many builds to retrieve

  * **offset** (`int`, *optional*) – What build store to include as first when retrieving the list

  * **desc** (`bool`, *optional*) – Whether to sort the builds in descending order based on their modification date

* **Returns**

  The retrieved builds of a user

* **Return type**

  `dict`

***

### [](#datasetclient) DatasetClient

Sub-client for manipulating a single dataset.

* [get()](#datasetclient-get)
* [update()](#datasetclient-update)
* [delete()](#datasetclient-delete)
* [list\_items()](#datasetclient-list\_items)
* [iterate\_items()](#datasetclient-iterate\_items)
* [download\_items()](#datasetclient-download\_items)
* [stream\_items()](#datasetclient-stream\_items)
* [push\_items()](#datasetclient-push\_items)

***

#### [](#datasetclient-get) `DatasetClient.get()`

Retrieve the dataset.

[https://docs.apify.com/api/v2#/reference/datasets/dataset/get-dataset](https://docs.apify.com/api/v2#/reference/datasets/dataset/get-dataset)

* **Returns**

  The retrieved dataset, or `None`, if it does not exist

* **Return type**

  `dict`, optional

***

#### [](#datasetclient-update) `DatasetClient.update(new_fields)`

Update the dataset with specified fields.

[https://docs.apify.com/api/v2#/reference/datasets/dataset/update-dataset](https://docs.apify.com/api/v2#/reference/datasets/dataset/update-dataset)

* **Parameters**

  * **new_fields** (`dict`) – The fields of the dataset to update

* **Returns**

  The updated dataset

* **Return type**

  `dict`

***

#### [](#datasetclient-delete) `DatasetClient.delete()`

Delete the dataset.

[https://docs.apify.com/api/v2#/reference/datasets/dataset/delete-dataset](https://docs.apify.com/api/v2#/reference/datasets/dataset/delete-dataset)

* **Return type**

  `None`

***

#### [](#datasetclient-list_items) `DatasetClient.list_items(*, offset=None, limit=None, clean=None, desc=None, fields=None, omit=None, unwind=None, skip_empty=None, skip_hidden=None)`

List the items of the dataset.

[https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items](https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items)

* **Parameters**

  * **offset** (`int`, *optional*) – Number of items that should be skipped at the start. The default value is 0

  * **limit** (`int`, *optional*) – Maximum number of items to return. By default there is no limit.

  * **desc** (`bool`, *optional*) – By default, results are returned in the same order as they were stored.
  To reverse the order, set this parameter to True.

  * **clean** (`bool`, *optional*) – If True, returns only non-empty items and skips hidden fields (i.e. fields starting with the # character).
  The clean parameter is just a shortcut for skip_hidden=True and skip_empty=True parameters.
  Note that since some objects might be skipped from the output, that the result might contain less items than the limit value.

  * **fields** (`list of str`, *optional*) – A list of fields which should be picked from the items,
  only these fields will remain in the resulting record objects.
  Note that the fields in the outputted items are sorted the same way as they are specified in the fields parameter.
  You can use this feature to effectively fix the output format.

  * **omit** (`list of str`, *optional*) – A list of fields which should be omitted from the items.

  * **unwind** (`str`, *optional*) – Name of a field which should be unwound.
  If the field is an array then every element of the array will become a separate record and merged with parent object.
  If the unwound field is an object then it is merged with the parent object.
  If the unwound field is missing or its value is neither an array nor an object and therefore cannot be merged with a parent object,
  then the item gets preserved as it is. Note that the unwound items ignore the desc parameter.

  * **skip_empty** (`bool`, *optional*) – If True, then empty items are skipped from the output.
  Note that if used, the results might contain less items than the limit value.

  * **skip_hidden** (`bool`, *optional*) – If True, then hidden fields are skipped from the output, i.e. fields starting with the # character.

* **Returns**

  The dataset items

* **Return type**

  `dict`

***

#### [](#datasetclient-iterate_items) `DatasetClient.iterate_items(offset=0, limit=None, clean=None, desc=None, fields=None, omit=None, unwind=None, skip_empty=None, skip_hidden=None)`

Iterate over the items in the dataset.

[https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items](https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items)

* **Parameters**

  * **offset** (`int`, *optional*) – Number of items that should be skipped at the start. The default value is 0

  * **limit** (`int`, *optional*) – Maximum number of items to return. By default there is no limit.

  * **desc** (`bool`, *optional*) – By default, results are returned in the same order as they were stored.
  To reverse the order, set this parameter to True.

  * **clean** (`bool`, *optional*) – If True, returns only non-empty items and skips hidden fields (i.e. fields starting with the # character).
  The clean parameter is just a shortcut for skip_hidden=True and skip_empty=True parameters.
  Note that since some objects might be skipped from the output, that the result might contain less items than the limit value.

  * **fields** (`list of str`, *optional*) – A list of fields which should be picked from the items,
  only these fields will remain in the resulting record objects.
  Note that the fields in the outputted items are sorted the same way as they are specified in the fields parameter.
  You can use this feature to effectively fix the output format.

  * **omit** (`list of str`, *optional*) – A list of fields which should be omitted from the items.

  * **unwind** (`str`, *optional*) – Name of a field which should be unwound.
  If the field is an array then every element of the array will become a separate record and merged with parent object.
  If the unwound field is an object then it is merged with the parent object.
  If the unwound field is missing or its value is neither an array nor an object and therefore cannot be merged with a parent object,
  then the item gets preserved as it is. Note that the unwound items ignore the desc parameter.

  * **skip_empty** (`bool`, *optional*) – If True, then empty items are skipped from the output.
  Note that if used, the results might contain less items than the limit value.

  * **skip_hidden** (`bool`, *optional*) – If True, then hidden fields are skipped from the output, i.e. fields starting with the # character.

* **Yields**

  `dict` – An item from the dataset

* **Return type**

  `Generator`

***

#### [](#datasetclient-download_items) `DatasetClient.download_items(item_format='json', *, offset=None, limit=None, desc=None, clean=None, bom=None, delimiter=None, fields=None, omit=None, unwind=None, skip_empty=None, skip_header_row=None, skip_hidden=None, xml_root=None, xml_row=None)`

Download the items in the dataset as raw bytes.

[https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items](https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items)

* **Parameters**

  * **item_format** (`str`) – Format of the results, possible values are: json, jsonl, csv, html, xlsx, xml and rss. The default value is json.

  * **offset** (`int`, *optional*) – Number of items that should be skipped at the start. The default value is 0

  * **limit** (`int`, *optional*) – Maximum number of items to return. By default there is no limit.

  * **desc** (`bool`, *optional*) – By default, results are returned in the same order as they were stored.
  To reverse the order, set this parameter to True.

  * **clean** (`bool`, *optional*) – If True, returns only non-empty items and skips hidden fields (i.e. fields starting with the # character).
  The clean parameter is just a shortcut for skip_hidden=True and skip_empty=True parameters.
  Note that since some objects might be skipped from the output, that the result might contain less items than the limit value.

  * **bom** (`bool`, *optional*) – All text responses are encoded in UTF-8 encoding.
  By default, csv files are prefixed with the UTF-8 Byte Order Mark (BOM),
  while json, jsonl, xml, html and rss files are not. If you want to override this default behavior,
  specify bom=True query parameter to include the BOM or bom=False to skip it.

  * **delimiter** (`str`, *optional*) – A delimiter character for CSV files. The default delimiter is a simple comma (,).

  * **fields** (`list of str`, *optional*) – A list of fields which should be picked from the items,
  only these fields will remain in the resulting record objects.
  Note that the fields in the outputted items are sorted the same way as they are specified in the fields parameter.
  You can use this feature to effectively fix the output format.

  * **omit** (`list of str`, *optional*) – A list of fields which should be omitted from the items.

  * **unwind** (`str`, *optional*) – Name of a field which should be unwound.
  If the field is an array then every element of the array will become a separate record and merged with parent object.
  If the unwound field is an object then it is merged with the parent object.
  If the unwound field is missing or its value is neither an array nor an object and therefore cannot be merged with a parent object,
  then the item gets preserved as it is. Note that the unwound items ignore the desc parameter.

  * **skip_empty** (`bool`, *optional*) – If True, then empty items are skipped from the output.
  Note that if used, the results might contain less items than the limit value.

  * **skip_header_row** (`bool`, *optional*) – If True, then header row in the csv format is skipped.

  * **skip_hidden** (`bool`, *optional*) – If True, then hidden fields are skipped from the output, i.e. fields starting with the # character.

  * **xml_root** (`str`, *optional*) – Overrides default root element name of xml output. By default the root element is items.

  * **xml_row** (`str`, *optional*) – Overrides default element name that wraps each page or page function result object in xml output.
  By default the element name is item.

* **Returns**

  The dataset items as raw bytes

* **Return type**

  `bytes`

***

#### [](#datasetclient-stream_items) `DatasetClient.stream_items(item_format='json', *, offset=None, limit=None, desc=None, clean=None, bom=None, delimiter=None, fields=None, omit=None, unwind=None, skip_empty=None, skip_header_row=None, skip_hidden=None, xml_root=None, xml_row=None)`

Retrieve the items in the dataset as a file-like object.

[https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items](https://docs.apify.com/api/v2#/reference/datasets/item-collection/get-items)

* **Parameters**

  * **item_format** (`str`) – Format of the results, possible values are: json, jsonl, csv, html, xlsx, xml and rss. The default value is json.

  * **offset** (`int`, *optional*) – Number of items that should be skipped at the start. The default value is 0

  * **limit** (`int`, *optional*) – Maximum number of items to return. By default there is no limit.

  * **desc** (`bool`, *optional*) – By default, results are returned in the same order as they were stored.
  To reverse the order, set this parameter to True.

  * **clean** (`bool`, *optional*) – If True, returns only non-empty items and skips hidden fields (i.e. fields starting with the # character).
  The clean parameter is just a shortcut for skip_hidden=True and skip_empty=True parameters.
  Note that since some objects might be skipped from the output, that the result might contain less items than the limit value.

  * **bom** (`bool`, *optional*) – All text responses are encoded in UTF-8 encoding.
  By default, csv files are prefixed with the UTF-8 Byte Order Mark (BOM),
  while json, jsonl, xml, html and rss files are not. If you want to override this default behavior,
  specify bom=True query parameter to include the BOM or bom=False to skip it.

  * **delimiter** (`str`, *optional*) – A delimiter character for CSV files. The default delimiter is a simple comma (,).

  * **fields** (`list of str`, *optional*) – A list of fields which should be picked from the items,
  only these fields will remain in the resulting record objects.
  Note that the fields in the outputted items are sorted the same way as they are specified in the fields parameter.
  You can use this feature to effectively fix the output format.

  * **omit** (`list of str`, *optional*) – A list of fields which should be omitted from the items.

  * **unwind** (`str`, *optional*) – Name of a field which should be unwound.
  If the field is an array then every element of the array will become a separate record and merged with parent object.
  If the unwound field is an object then it is merged with the parent object.
  If the unwound field is missing or its value is neither an array nor an object and therefore cannot be merged with a parent object,
  then the item gets preserved as it is. Note that the unwound items ignore the desc parameter.

  * **skip_empty** (`bool`, *optional*) – If True, then empty items are skipped from the output.
  Note that if used, the results might contain less items than the limit value.

  * **skip_header_row** (`bool`, *optional*) – If True, then header row in the csv format is skipped.

  * **skip_hidden** (`bool`, *optional*) – If True, then hidden fields are skipped from the output, i.e. fields starting with the # character.

  * **xml_root** (`str`, *optional*) – Overrides default root element name of xml output. By default the root element is items.

  * **xml_row** (`str`, *optional*) – Overrides default element name that wraps each page or page function result object in xml output.
  By default the element name is item.

* **Returns**

  The dataset items as a file-like object

* **Return type**

  `io.IOBase`

***

#### [](#datasetclient-push_items) `DatasetClient.push_items(items)`

Push items to the dataset.

[https://docs.apify.com/api/v2#/reference/datasets/item-collection/put-items](https://docs.apify.com/api/v2#/reference/datasets/item-collection/put-items)

* **Parameters**

  * **items** (`Union[str, int, float, bool, None, Dict[str, Any], List[Any]]`) – The items which to push in the dataset. Either a stringified JSON, a dictionary, or a list of strings or dictionaries.

* **Return type**

  `None`

***

### [](#datasetcollectionclient) DatasetCollectionClient

Sub-client for manipulating datasets.

* [list()](#datasetcollectionclient-list)
* [get\_or\_create()](#datasetcollectionclient-get\_or\_create)

***

#### [](#datasetcollectionclient-list) `DatasetCollectionClient.list(*, unnamed=None, limit=None, offset=None, desc=None)`

List the available datasets.

[https://docs.apify.com/api/v2#/reference/datasets/dataset-collection/get-list-of-datasets](https://docs.apify.com/api/v2#/reference/datasets/dataset-collection/get-list-of-datasets)

* **Parameters**

  * **unnamed** (`bool`, *optional*) – Whether to include unnamed datasets in the list

  * **limit** (`int`, *optional*) – How many datasets to retrieve

  * **offset** (`int`, *optional*) – What dataset to include as first when retrieving the list

  * **desc** (`bool`, *optional*) – Whether to sort the datasets in descending order based on their modification date

* **Returns**

  The list of available datasets matching the specified filters.

* **Return type**

  `dict`

***

#### [](#datasetcollectionclient-get_or_create) `DatasetCollectionClient.get_or_create(*, name='')`

Retrieve a named dataset, or create a new one when it doesn’t exist.

[https://docs.apify.com/api/v2#/reference/datasets/dataset-collection/create-dataset](https://docs.apify.com/api/v2#/reference/datasets/dataset-collection/create-dataset)

* **Parameters**

  * **name** (`str`, *optional*) – The name of the dataset to retrieve or create.

* **Returns**

  The retrieved or newly-created dataset.

* **Return type**

  `dict`

***

### [](#keyvaluestoreclient) KeyValueStoreClient

Sub-client for manipulating a single key-value store.

* [get()](#keyvaluestoreclient-get)
* [update()](#keyvaluestoreclient-update)
* [delete()](#keyvaluestoreclient-delete)
* [list\_keys()](#keyvaluestoreclient-list\_keys)
* [get\_record()](#keyvaluestoreclient-get\_record)
* [set\_record()](#keyvaluestoreclient-set\_record)
* [delete\_record()](#keyvaluestoreclient-delete\_record)

***

#### [](#keyvaluestoreclient-get) `KeyValueStoreClient.get()`

Retrieve the key-value store.

[https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/get-store](https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/get-store)

* **Returns**

  The retrieved key-value store, or `None` if it does not exist

* **Return type**

  `dict`, optional

***

#### [](#keyvaluestoreclient-update) `KeyValueStoreClient.update(new_fields)`

Update the key-value store with specified fields.

[https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/update-store](https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/update-store)

* **Parameters**

  * **new_fields** (`dict`) – The fields of the key-value store to update

* **Returns**

  The updated key-value store

* **Return type**

  `dict`

***

#### [](#keyvaluestoreclient-delete) `KeyValueStoreClient.delete()`

Delete the key-value store.

[https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/delete-store](https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/delete-store)

* **Return type**

  `None`

***

#### [](#keyvaluestoreclient-list_keys) `KeyValueStoreClient.list_keys(*, limit=None, exclusive_start_key=None)`

List the keys in the key-value store.

[https://docs.apify.com/api/v2#/reference/key-value-stores/key-collection/get-list-of-keys](https://docs.apify.com/api/v2#/reference/key-value-stores/key-collection/get-list-of-keys)

* **Parameters**

  * **limit** (`int`, *optional*) – Number of keys to be returned. Maximum value is 1000

  * **exclusive_start_key** (`str`, *optional*) – All keys up to this one (including) are skipped from the result

* **Returns**

  The list of keys in the key-value store matching the given arguments

* **Return type**

  `dict`

***

#### [](#keyvaluestoreclient-get_record) `KeyValueStoreClient.get_record(key, *, as_bytes=False, as_file=False)`

Retrieve the given record from the key-value store.

[https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record](https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record)

* **Parameters**

  * **key** (`str`) – Key of the record to retrieve

  * **as_bytes** (`bool`, *optional*) – Whether to retrieve the record as unparsed bytes, default False

  * **as_file** (`bool`, *optional*) – Whether to retrieve the record as a file-like object, default False

* **Returns**

  The requested record, or `None`, if the record does not exist

* **Return type**

  `dict`, optional

***

#### [](#keyvaluestoreclient-set_record) `KeyValueStoreClient.set_record(key, value, content_type=None)`

Set a value to the given record in the key-value store.

[https://docs.apify.com/api/v2#/reference/key-value-stores/record/put-record](https://docs.apify.com/api/v2#/reference/key-value-stores/record/put-record)

* **Parameters**

  * **key** (`str`) – The key of the record to save the value to

  * **value** (`Any`) – The value to save into the record

  * **content_type** (`str`, *optional*) – The content type of the saved value

* **Return type**

  `None`

***

#### [](#keyvaluestoreclient-delete_record) `KeyValueStoreClient.delete_record(key)`

Delete the specified record from the key-value store.

[https://docs.apify.com/api/v2#/reference/key-value-stores/record/delete-record](https://docs.apify.com/api/v2#/reference/key-value-stores/record/delete-record)

* **Parameters**

  * **key** (`str`) – The key of the record which to delete

* **Return type**

  `None`

***

### [](#keyvaluestorecollectionclient) KeyValueStoreCollectionClient

Sub-client for manipulating key-value stores.

* [list()](#keyvaluestorecollectionclient-list)
* [get\_or\_create()](#keyvaluestorecollectionclient-get\_or\_create)

***

#### [](#keyvaluestorecollectionclient-list) `KeyValueStoreCollectionClient.list(*, unnamed=None, limit=None, offset=None, desc=None)`

List the available key-value stores.

[https://docs.apify.com/api/v2#/reference/key-value-stores/store-collection/get-list-of-key-value-stores](https://docs.apify.com/api/v2#/reference/key-value-stores/store-collection/get-list-of-key-value-stores)

* **Parameters**

  * **unnamed** (`bool`, *optional*) – Whether to include unnamed key-value stores in the list

  * **limit** (`int`, *optional*) – How many key-value stores to retrieve

  * **offset** (`int`, *optional*) – What key-value store to include as first when retrieving the list

  * **desc** (`bool`, *optional*) – Whether to sort the key-value stores in descending order based on their modification date

* **Returns**

  The list of available key-value stores matching the specified filters.

* **Return type**

  `dict`

***

#### [](#keyvaluestorecollectionclient-get_or_create) `KeyValueStoreCollectionClient.get_or_create(*, name='')`

Retrieve a named key-value store, or create a new one when it doesn’t exist.

[https://docs.apify.com/api/v2#/reference/key-value-stores/store-collection/create-key-value-store](https://docs.apify.com/api/v2#/reference/key-value-stores/store-collection/create-key-value-store)

* **Parameters**

  * **name** (`str`, *optional*) – The name of the key-value store to retrieve or create.

* **Returns**

  The retrieved or newly-created key-value store.

* **Return type**

  `dict`

***

### [](#logclient) LogClient

Sub-client for manipulating logs.

* [get()](#logclient-get)
* [stream()](#logclient-stream)

***

#### [](#logclient-get) `LogClient.get()`

Retrieve the log as text.

[https://docs.apify.com/api/v2#/reference/logs/log/get-log](https://docs.apify.com/api/v2#/reference/logs/log/get-log)

* **Returns**

  The retrieved log, or `None`, if it does not exist.

* **Return type**

  `str`, optional

***

#### [](#logclient-stream) `LogClient.stream()`

Retrieve the log as a file-like object.

[https://docs.apify.com/api/v2#/reference/logs/log/get-log](https://docs.apify.com/api/v2#/reference/logs/log/get-log)

* **Returns**

  The retrieved log as a file-like object, or `None`, if it does not exist.

* **Return type**

  `io.IOBase`, optional

***

### [](#requestqueueclient) RequestQueueClient

Sub-client for manipulating a single request queue.

* [get()](#requestqueueclient-get)
* [update()](#requestqueueclient-update)
* [delete()](#requestqueueclient-delete)
* [list\_head()](#requestqueueclient-list\_head)
* [add\_request()](#requestqueueclient-add\_request)
* [get\_request()](#requestqueueclient-get\_request)
* [update\_request()](#requestqueueclient-update\_request)
* [delete\_request()](#requestqueueclient-delete\_request)

***

#### [](#requestqueueclient-get) `RequestQueueClient.get()`

Retrieve the request queue.

[https://docs.apify.com/api/v2#/reference/request-queues/queue/get-request-queue](https://docs.apify.com/api/v2#/reference/request-queues/queue/get-request-queue)

* **Returns**

  The retrieved request queue, or `None`, if it does not exist

* **Return type**

  `dict`, optional

***

#### [](#requestqueueclient-update) `RequestQueueClient.update(new_fields)`

Update the request queue with specified fields.

[https://docs.apify.com/api/v2#/reference/request-queues/queue/update-request-queue](https://docs.apify.com/api/v2#/reference/request-queues/queue/update-request-queue)

* **Parameters**

  * **new_fields** (`dict`) – The fields of the request queue to update

* **Returns**

  The updated request queue

* **Return type**

  `dict`

***

#### [](#requestqueueclient-delete) `RequestQueueClient.delete()`

Delete the request queue.

[https://docs.apify.com/api/v2#/reference/request-queues/queue/delete-request-queue](https://docs.apify.com/api/v2#/reference/request-queues/queue/delete-request-queue)

* **Return type**

  `None`

***

#### [](#requestqueueclient-list_head) `RequestQueueClient.list_head(*, limit=None)`

Retrieve a given number of requests from the beginning of the queue.

[https://docs.apify.com/api/v2#/reference/request-queues/queue-head/get-head](https://docs.apify.com/api/v2#/reference/request-queues/queue-head/get-head)

* **Parameters**

  * **limit** (`int`, *optional*) – How many requests to retrieve

* **Returns**

  The desired number of requests from the beginning of the queue.

* **Return type**

  `dict`

***

#### [](#requestqueueclient-add_request) `RequestQueueClient.add_request(request, *, forefront=None)`

Add a request to the queue.

[https://docs.apify.com/api/v2#/reference/request-queues/request-collection/add-request](https://docs.apify.com/api/v2#/reference/request-queues/request-collection/add-request)

* **Parameters**

  * **request** (`dict`) – The request to add to the queue

  * **forefront** (`bool`, *optional*) – Whether to add the request to the head or the end of the queue

* **Returns**

  The added request.

* **Return type**

  `dict`

***

#### [](#requestqueueclient-get_request) `RequestQueueClient.get_request(request_id)`

Retrieve a request from the queue.

[https://docs.apify.com/api/v2#/reference/request-queues/request/get-request](https://docs.apify.com/api/v2#/reference/request-queues/request/get-request)

* **Parameters**

  * **request_id** (`str`) – ID of the request to retrieve

* **Returns**

  The retrieved request, or `None`, if it did not exist.

* **Return type**

  `dict`, optional

***

#### [](#requestqueueclient-update_request) `RequestQueueClient.update_request(request, *, forefront=None)`

Update a request in the queue.

[https://docs.apify.com/api/v2#/reference/request-queues/request/update-request](https://docs.apify.com/api/v2#/reference/request-queues/request/update-request)

* **Parameters**

  * **request** (`dict`) – The updated request

  * **forefront** (`bool`, *optional*) – Whether to put the updated request in the beginning or the end of the queue

* **Returns**

  The updated request

* **Return type**

  `dict`

***

#### [](#requestqueueclient-delete_request) `RequestQueueClient.delete_request(request_id)`

Delete a request from the queue.

[https://docs.apify.com/api/v2#/reference/request-queues/request/delete-request](https://docs.apify.com/api/v2#/reference/request-queues/request/delete-request)

* **Parameters**

  * **request_id** (`str`) – ID of the request to delete.

* **Return type**

  `None`

***

### [](#requestqueuecollectionclient) RequestQueueCollectionClient

Sub-client for manipulating request queues.

* [list()](#requestqueuecollectionclient-list)
* [get\_or\_create()](#requestqueuecollectionclient-get\_or\_create)

***

#### [](#requestqueuecollectionclient-list) `RequestQueueCollectionClient.list(*, unnamed=None, limit=None, offset=None, desc=None)`

List the available request queues.

[https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/get-list-of-request-queues](https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/get-list-of-request-queues)

* **Parameters**

  * **unnamed** (`bool`, *optional*) – Whether to include unnamed request queues in the list

  * **limit** (`int`, *optional*) – How many request queues to retrieve

  * **offset** (`int`, *optional*) – What request queue to include as first when retrieving the list

  * **desc** (`bool`, *optional*) – Whether to sort therequest queues in descending order based on their modification date

* **Returns**

  The list of available request queues matching the specified filters.

* **Return type**

  `dict`

***

#### [](#requestqueuecollectionclient-get_or_create) `RequestQueueCollectionClient.get_or_create(*, name='')`

Retrieve a named request queue, or create a new one when it doesn’t exist.

[https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/create-request-queue](https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/create-request-queue)

* **Parameters**

  * **name** (`str`) – The name of the request queue to retrieve or create.

* **Returns**

  The retrieved or newly-created request queue.

* **Return type**

  `dict`

***

### [](#scheduleclient) ScheduleClient

Sub-client for manipulating a single schedule.

* [get()](#scheduleclient-get)
* [update()](#scheduleclient-update)
* [delete()](#scheduleclient-delete)
* [get\_log()](#scheduleclient-get\_log)

***

#### [](#scheduleclient-get) `ScheduleClient.get()`

Return information about the schedule.

[https://docs.apify.com/api/v2#/reference/schedules/schedule-object/get-schedule](https://docs.apify.com/api/v2#/reference/schedules/schedule-object/get-schedule)

* **Returns**

  The retrieved schedule

* **Return type**

  `dict`, optional

***

#### [](#scheduleclient-update) `ScheduleClient.update(*, cron_expression=None, is_enabled=None, is_exclusive=None, name=None, actions=None, description=None, timezone=None)`

Update the schedule with specified fields.

[https://docs.apify.com/api/v2#/reference/schedules/schedule-object/update-schedule](https://docs.apify.com/api/v2#/reference/schedules/schedule-object/update-schedule)

* **Parameters**

  * **cron_expression** (`str`, *optional*) – The cron expression used by this schedule

  * **is_enabled** (`bool`, *optional*) – True if the schedule should be enabled

  * **is_exclusive** (`bool`, *optional*) – When set to true, don’t start actor or actor task if it’s still running from the previous schedule.

  * **name** (`str`, *optional*) – The name of the schedule to create.

  * **actions** (`list of dict`, *optional*) – Actors or tasks that should be run on this schedule. See the API documentation for exact structure.

  * **description** (`str`, *optional*) – Description of this schedule

  * **timezone** (`str`, *optional*) – Timezone in which your cron expression runs
  (TZ database name from [https://en.wikipedia.org/wiki/List_of_tz_database_time_zones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones))

* **Returns**

  The updated schedule

* **Return type**

  `dict`

***

#### [](#scheduleclient-delete) `ScheduleClient.delete()`

Delete the schedule.

[https://docs.apify.com/api/v2#/reference/schedules/schedule-object/delete-schedule](https://docs.apify.com/api/v2#/reference/schedules/schedule-object/delete-schedule)

* **Return type**

  `None`

***

#### [](#scheduleclient-get_log) `ScheduleClient.get_log()`

Return log for the given schedule.

[https://docs.apify.com/api/v2#/reference/schedules/schedule-log/get-schedule-log](https://docs.apify.com/api/v2#/reference/schedules/schedule-log/get-schedule-log)

* **Returns**

  Retrieved log of the given schedule

* **Return type**

  `list`, optional

***

### [](#schedulecollectionclient) ScheduleCollectionClient

Sub-client for manipulating schedules.

* [list()](#schedulecollectionclient-list)
* [create()](#schedulecollectionclient-create)

***

#### [](#schedulecollectionclient-list) `ScheduleCollectionClient.list(*, limit=None, offset=None, desc=None)`

List the available schedules.

[https://docs.apify.com/api/v2#/reference/schedules/schedules-collection/get-list-of-schedules](https://docs.apify.com/api/v2#/reference/schedules/schedules-collection/get-list-of-schedules)

* **Parameters**

  * **limit** (`int`, *optional*) – How many schedules to retrieve

  * **offset** (`int`, *optional*) – What schedules to include as first when retrieving the list

  * **desc** (`bool`, *optional*) – Whether to sort the schedules in descending order based on their modification date

* **Return type**

  `Dict`

* **Returns**

  The list of available schedules matching the specified filters.

***

#### [](#schedulecollectionclient-create) `ScheduleCollectionClient.create(*, cron_expression, is_enabled, is_exclusive, name=None, actions=[], description=None, timezone=None)`

Create a new schedule.

[https://docs.apify.com/api/v2#/reference/schedules/schedules-collection/create-schedule](https://docs.apify.com/api/v2#/reference/schedules/schedules-collection/create-schedule)

* **Parameters**

  * **cron_expression** (`str`) – The cron expression used by this schedule

  * **is_enabled** (`bool`) – True if the schedule should be enabled

  * **is_exclusive** (`bool`) – When set to true, don’t start actor or actor task if it’s still running from the previous schedule.

  * **name** (`Optional[str]`) – The name of the schedule to create.

  * **actions** (`List[Dict]`) – Actors or tasks that should be run on this schedule. See the API documentation for exact structure.

  * **description** (`Optional[str]`) – Description of this schedule

  * **timezone** (`Optional[str]`) – Timezone in which your cron expression runs (TZ database name from [https://en.wikipedia.org/wiki/List_of_tz_database_time_zones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones))

* **Return type**

  `Dict`

* **Returns**

  The created schedule.

***

### [](#taskclient) TaskClient

Sub-client for manipulating a single task.

* [get()](#taskclient-get)
* [update()](#taskclient-update)
* [delete()](#taskclient-delete)
* [start()](#taskclient-start)
* [call()](#taskclient-call)
* [get\_input()](#taskclient-get\_input)
* [update\_input()](#taskclient-update\_input)
* [last\_run()](#taskclient-last\_run)
* [runs()](#taskclient-runs)
* [webhooks()](#taskclient-webhooks)

***

#### [](#taskclient-get) `TaskClient.get()`

Retrieve the task.

[https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/get-task](https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/get-task)

* **Returns**

  The retrieved task

* **Return type**

  `dict`, optional

***

#### [](#taskclient-update) `TaskClient.update(*, name=None, task_input=None, build=None, memory_mbytes=None, timeout_secs=None)`

Update the task with specified fields.

[https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/update-task](https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/update-task)

* **Parameters**

  * **name** (`str`, *optional*) – Name of the task

  * **build** (`str`, *optional*) – Actor build to run. It can be either a build tag or build number.
  By default, the run uses the build specified in the task settings (typically latest).

  * **memory_mbytes** (`int`, *optional*) – Memory limit for the run, in megabytes.
  By default, the run uses a memory limit specified in the task settings.

  * **timeout_secs** (`int`, *optional*) – Optional timeout for the run, in seconds. By default, the run uses timeout specified in the task settings.

  * **task_input** (`dict`, *optional*) – Task input dictionary

* **Returns**

  The updated task

* **Return type**

  `dict`

***

#### [](#taskclient-delete) `TaskClient.delete()`

Delete the task.

[https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/delete-task](https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/delete-task)

* **Return type**

  `None`

***

#### [](#taskclient-start) `TaskClient.start(*, task_input=None, build=None, memory_mbytes=None, timeout_secs=None, wait_for_finish=None, webhooks=None)`

Start the task and immediately return the Run object.

[https://docs.apify.com/api/v2#/reference/actor-tasks/run-collection/run-task](https://docs.apify.com/api/v2#/reference/actor-tasks/run-collection/run-task)

* **Parameters**

  * **task_input** (`dict`, *optional*) – Task input dictionary

  * **build** (`str`, *optional*) – Specifies the actor build to run. It can be either a build tag or build number.
  By default, the run uses the build specified in the task settings (typically latest).

  * **memory_mbytes** (`int`, *optional*) – Memory limit for the run, in megabytes.
  By default, the run uses a memory limit specified in the task settings.

  * **timeout_secs** (`int`, *optional*) – Optional timeout for the run, in seconds. By default, the run uses timeout specified in the task settings.

  * **wait_for_finish** (`bool`, *optional*) – The maximum number of seconds the server waits for the run to finish.
  By default, it is 0, the maximum value is 300.

  * **webhooks** (`list`, *optional*) – Optional webhooks ([https://docs.apify.com/webhooks](https://docs.apify.com/webhooks)) associated with the actor run,
  which can be used to receive a notification, e.g. when the actor finished or failed.
  If you already have a webhook set up for the actor or task, you do not have to add it again here.

* **Returns**

  The run object

* **Return type**

  `dict`

***

#### [](#taskclient-call) `TaskClient.call(*, task_input=None, build=None, memory_mbytes=None, timeout_secs=None, wait_for_finish=None, webhooks=None)`

Start a task and wait for it to finish before returning the Run object.

It waits indefinitely, unless the wait_secs argument is provided.

[https://docs.apify.com/api/v2#/reference/actor-tasks/run-collection/run-task](https://docs.apify.com/api/v2#/reference/actor-tasks/run-collection/run-task)

* **Parameters**

  * **task_input** (`dict`, *optional*) – Task input dictionary

  * **build** (`str`, *optional*) – Specifies the actor build to run. It can be either a build tag or build number.
  By default, the run uses the build specified in the task settings (typically latest).

  * **memory_mbytes** (`int`, *optional*) – Memory limit for the run, in megabytes.
  By default, the run uses a memory limit specified in the task settings.

  * **timeout_secs** (`int`, *optional*) – Optional timeout for the run, in seconds. By default, the run uses timeout specified in the task settings.

  * **wait_for_finish** (`bool`, *optional*) – The maximum number of seconds the server waits for the run to finish.
  By default, it is 0, the maximum value is 300.

  * **webhooks** (`list`, *optional*) – Specifies optional webhooks associated with the actor run, which can be used to receive a notification
  e.g. when the actor finished or failed. Note: if you already have a webhook set up for the actor or task,
  you do not have to add it again here.

* **Returns**

  The run object

* **Return type**

  `dict`

***

#### [](#taskclient-get_input) `TaskClient.get_input()`

Retrieve the default input for this task.

[https://docs.apify.com/api/v2#/reference/actor-tasks/task-input-object/get-task-input](https://docs.apify.com/api/v2#/reference/actor-tasks/task-input-object/get-task-input)

* **Returns**

  Retrieved task input

* **Return type**

  `dict`, optional

***

#### [](#taskclient-update_input) `TaskClient.update_input(*, task_input)`

Update the default input for this task.

[https://docs.apify.com/api/v2#/reference/actor-tasks/task-input-object/update-task-input](https://docs.apify.com/api/v2#/reference/actor-tasks/task-input-object/update-task-input)

* **Return type**

  `Dict`

* **Returns**

  dict, Retrieved task input

***

#### [](#taskclient-last_run) `TaskClient.last_run(*, status=None)`

Retrieve RunClient for last run of this task.

Last run is retrieved based on the start time of the runs.

* **Parameters**

  * **status** (`optional, dict`) – Consider only runs with this status.

* **Return type**

  `None`

***

#### [](#taskclient-runs) `TaskClient.runs()`

Retrieve RunCollectionClient for runs of this task.

* **Return type**

  `None`

***

#### [](#taskclient-webhooks) `TaskClient.webhooks()`

Retrieve WebhookCollectionClient for webhooks associated with this task.

* **Return type**

  [`WebhookCollectionClient`](#webhookcollectionclient)

***

### [](#taskcollectionclient) TaskCollectionClient

Sub-client for manipulating tasks.

* [list()](#taskcollectionclient-list)
* [create()](#taskcollectionclient-create)

***

#### [](#taskcollectionclient-list) `TaskCollectionClient.list(*, limit=None, offset=None, desc=None)`

List the available tasks.

[https://docs.apify.com/api/v2#/reference/actor-tasks/task-collection/get-list-of-tasks](https://docs.apify.com/api/v2#/reference/actor-tasks/task-collection/get-list-of-tasks)

* **Parameters**

  * **limit** (`int`, *optional*) – How many tasks to list

  * **offset** (`int`, *optional*) – What task to include as first when retrieving the list

  * **desc** (`bool`, *optional*) – Whether to sort the tasks in descending order based on their modification date

* **Returns**

  The list of available tasks matching the specified filters.

* **Return type**

  `dict`

***

#### [](#taskcollectionclient-create) `TaskCollectionClient.create(*, actor_id, name, build=None, timeout_secs=None, memory_mbytes=None, task_input=None)`

Create a new task.

[https://docs.apify.com/api/v2#/reference/actor-tasks/task-collection/create-task](https://docs.apify.com/api/v2#/reference/actor-tasks/task-collection/create-task)

* **Parameters**

  * **actor_id** (`str`) – Id of the actor that should be run

  * **name** (`str`) – Name of the task

  * **build** (`str`, *optional*) – Actor build to run. It can be either a build tag or build number.
  By default, the run uses the build specified in the task settings (typically latest).

  * **memory_mbytes** (`int`, *optional*) – Memory limit for the run, in megabytes.
  By default, the run uses a memory limit specified in the task settings.

  * **timeout_secs** (`int`, *optional*) – Optional timeout for the run, in seconds. By default, the run uses timeout specified in the task settings.

  * **task_input** (`dict`, *optional*) – Task input object.

* **Returns**

  The created task.

* **Return type**

  `dict`

***

### [](#userclient) UserClient

Sub-client for querying user data.

* [get()](#userclient-get)

***

#### [](#userclient-get) `UserClient.get()`

Return information about user account.

You receive all or only public info based on your token permissions.

[https://docs.apify.com/api/v2#/reference/users](https://docs.apify.com/api/v2#/reference/users)

* **Returns**

  The retrieved user data, or `None` if the user does not exist.

* **Return type**

  `dict`, optional

***

### [](#webhookclient) WebhookClient

Sub-client for manipulating a single webhook.

* [get()](#webhookclient-get)
* [update()](#webhookclient-update)
* [delete()](#webhookclient-delete)
* [dispatches()](#webhookclient-dispatches)

***

#### [](#webhookclient-get) `WebhookClient.get()`

Retrieve the webhook.

[https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/get-webhook](https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/get-webhook)

* **Returns**

  The retrieved webhook, or `None` if it does not exist

* **Return type**

  `dict`, optional

***

#### [](#webhookclient-update) `WebhookClient.update(*, event_types=None, request_url=None, payload_template=None, actor_id=None, actor_task_id=None, actor_run_id=None, ignore_ssl_errors=None, do_not_retry=None, is_ad_hoc=None)`

Update the webhook.

[https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/update-webhook](https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/update-webhook)

* **Parameters**

  * **event_types** (`list`, *optional*) – List of event types that should trigger the webhook.
  Present in the client constants as WebhookEventType. At least one is required.

  * **request_url** (`str`, *optional*) – URL that will be invoked once the webhook is triggered.

  * **payload_template** (`str`, *optional*) – Specification of the payload that will be sent to request_url

  * **actor_id** (`str`, *optional*) – Id of the actor whose runs should trigger the webhook.

  * **actor_task_id** (`str`, *optional*) – Id of the actor task whose runs should trigger the webhook.

  * **actor_run_id** (`str`, *optional*) – Id of the actor run which should trigger the webhook.

  * **ignore_ssl_errors** (`bool`, *optional*) – Whether the webhook should ignore SSL errors returned by request_url

  * **do_not_retry** (`bool`, *optional*) – Whether the webhook should retry sending the payload to request_url upon
  failure.

  * **is_ad_hoc** (`bool`, *optional*) – Set to True if you want the webhook to be triggered only the first time the
  condition is fulfilled. Only applicable when actor_run_id is filled.

* **Returns**

  The updated webhook

* **Return type**

  `dict`

***

#### [](#webhookclient-delete) `WebhookClient.delete()`

Delete the webhook.

[https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/delete-webhook](https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/delete-webhook)

* **Return type**

  `None`

***

#### [](#webhookclient-dispatches) `WebhookClient.dispatches()`

Get dispatches of the webhook.

[https://docs.apify.com/api/v2#/reference/webhooks/dispatches-collection/get-collection](https://docs.apify.com/api/v2#/reference/webhooks/dispatches-collection/get-collection)

* **Returns**

  A client allowing access to dispatches of this webhook using its list method

* **Return type**

  [`WebhookDispatchCollectionClient`](#webhookdispatchcollectionclient)

***

### [](#webhookcollectionclient) WebhookCollectionClient

Sub-client for manipulating webhooks.

* [list()](#webhookcollectionclient-list)
* [create()](#webhookcollectionclient-create)

***

#### [](#webhookcollectionclient-list) `WebhookCollectionClient.list(*, limit=None, offset=None, desc=None)`

List the available webhooks.

[https://docs.apify.com/api/v2#/reference/webhooks/webhook-collection/get-list-of-webhooks](https://docs.apify.com/api/v2#/reference/webhooks/webhook-collection/get-list-of-webhooks)

* **Parameters**

  * **limit** (`int`, *optional*) – How many webhooks to retrieve

  * **offset** (`int`, *optional*) – What webhook to include as first when retrieving the list

  * **desc** (`bool`, *optional*) – Whether to sort the webhooks in descending order based on their date of creation

* **Returns**

  The list of available webhooks matching the specified filters.

* **Return type**

  `dict`

***

#### [](#webhookcollectionclient-create) `WebhookCollectionClient.create(*, event_types, request_url, payload_template=None, actor_id=None, actor_task_id=None, actor_run_id=None, ignore_ssl_errors=None, do_not_retry=None, idempotency_key=None, is_ad_hoc=None)`

Create a new webhook.

You have to specify exactly one out of actor_id, actor_task_id or actor_run_id.

[https://docs.apify.com/api/v2#/reference/webhooks/webhook-collection/create-webhook](https://docs.apify.com/api/v2#/reference/webhooks/webhook-collection/create-webhook)

* **Parameters**

  * **event_types** (`list`) – List of event types that should trigger the webhook.
  Present in the client constants as WebhookEventType. At least one is required.

  * **request_url** (`str`) – URL that will be invoked once the webhook is triggered.

  * **payload_template** (`str`, *optional*) – Specification of the payload that will be sent to request_url

  * **actor_id** (`str`, *optional*) – Id of the actor whose runs should trigger the webhook.

  * **actor_task_id** (`str`, *optional*) – Id of the actor task whose runs should trigger the webhook.

  * **actor_run_id** (`str`, *optional*) – Id of the actor run which should trigger the webhook.

  * **ignore_ssl_errors** (`bool`, *optional*) – Whether the webhook should ignore SSL errors returned by request_url

  * **do_not_retry** (`bool`, *optional*) – Whether the webhook should retry sending the payload to request_url upon
  failure.

  * **idempotency_key** (`str`, *optional*) – A unique identifier of a webhook. You can use it to ensure that you won’t
  create the same webhook multiple times.

  * **is_ad_hoc** (`bool`, *optional*) – Set to True if you want the webhook to be triggered only the first time the
  condition is fulfilled. Only applicable when actor_run_id is filled.

* **Returns**

  The created webhook

* **Return type**

  `dict`

***

### [](#webhookdispatchclient) WebhookDispatchClient

Sub-client for querying information about a webhook dispatch.

* [get()](#webhookdispatchclient-get)

***

#### [](#webhookdispatchclient-get) `WebhookDispatchClient.get()`

Retrieve the webhook dispatch.

[https://docs.apify.com/api/v2#/reference/webhook-dispatches/webhook-dispatch-object/get-webhook-dispatch](https://docs.apify.com/api/v2#/reference/webhook-dispatches/webhook-dispatch-object/get-webhook-dispatch)

* **Returns**

  The retrieved webhook dispatch, or `None` if it does not exist

* **Return type**

  `dict`, optional

***

### [](#webhookdispatchcollectionclient) WebhookDispatchCollectionClient

Sub-client for listing webhook dispatches.

* [list()](#webhookdispatchcollectionclient-list)

***

#### [](#webhookdispatchcollectionclient-list) `WebhookDispatchCollectionClient.list(*, limit=None, offset=None, desc=None)`

List all webhook dispatches of a user.

[https://docs.apify.com/api/v2#/reference/webhook-dispatches/webhook-dispatches-collection/get-list-of-webhook-dispatches](https://docs.apify.com/api/v2#/reference/webhook-dispatches/webhook-dispatches-collection/get-list-of-webhook-dispatches)

* **Parameters**

  * **limit** (`int`, *optional*) – How many webhook dispatches to retrieve

  * **offset** (`int`, *optional*) – What webhook dispatch to include as first when retrieving the list

  * **desc** (`bool`, *optional*) – Whether to sort the webhook dispatches in descending order based on the date of their creation

* **Returns**

  The retrieved webhook dispatches of a user

* **Return type**

  `dict`

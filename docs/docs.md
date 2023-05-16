# Apify API client for Python

`apify_client` is the official library to access the [Apify API](https://docs.apify.com/api/v2) from your Python applications.
It provides useful features like automatic retries and convenience functions that improve the experience of using the Apify API.

* [Quick Start](#quick-start)
* [Features](#features)
  * [Automatic parsing and error handling](#automatic-parsing-and-error-handling)
  * [Retries with exponential backoff](#retries-with-exponential-backoff)
  * [Support for asynchronous usage](#support-for-asynchronous-usage)
  * [Convenience functions and options](#convenience-functions-and-options)
* [Usage concepts](#usage-concepts)
  * [Nested clients](#nested-clients)
  * [Pagination](#pagination)
  * [Streaming resources](#streaming-resources)
  * [Asynchronous usage](#asynchronous-usage)
  * [Logging](#logging)
* [API Reference](#api-reference)

## Installation

Requires Python 3.8+

You can install the client from its [PyPI listing](https://pypi.org/project/apify-client/).
To do that, simply run `pip install apify-client`.

## Quick Start

```python
from apify_client import ApifyClient

apify_client = ApifyClient('MY-APIFY-TOKEN')

# Start an actor and wait for it to finish
actor_call = apify_client.actor('john-doe/my-cool-actor').call()

# Fetch results from the actor's default dataset
dataset_items = apify_client.dataset(actor_call['defaultDatasetId']).list_items().items
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

### Support for asynchronous usage

Starting with version 1.0.0, the package offers an asynchronous version of the client, [`ApifyClientAsync`](#ApifyClientAsync),
which allows you to work with the Apify API in an asynchronous way, using the standard `async`/`await` syntax.

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
my_actor = actor_collection_client.create(name='my-actor')
# List all of your actors
actor_list = actor_collection_client.list().items
```

```python
# Collection clients do not require a parameter
dataset_collection_client = apify_client.datasets()
# Get (or create, if it doesn't exist) a dataset with the name of my-dataset
my_dataset = dataset_collection_client.get_or_create(name='my-dataset')
```

```python
# Resource clients accept an ID of the resource
actor_client = apify_client.actor('john-doe/my-actor')
# Fetch the john-doe/my-actor object from the API
my_actor = actor_client.get()
# Start the run of john-doe/my-actor and return the Run object
my_actor_run = actor_client.start()
```

```python
# Resource clients accept an ID of the resource
dataset_client = apify_client.dataset('john-doe/my-dataset')
# Append items to the end of john-doe/my-dataset
dataset_client.push_items([{ 'foo': 1 }, { 'bar': 2 }])
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
actor_runs = runs_client.list(limit=10, desc=True).items

# Select the last run of the john-doe/hello-world actor that finished with a SUCCEEDED status
last_succeeded_run_client = actor_client.last_run(status='SUCCEEDED')
# Fetch items from the run's dataset
dataset_items = last_succeeded_run_client.dataset().list_items().items
```

### Pagination

Most methods named `list` or `list_something` return a [`ListPage`](#ListPage) object,
containing properties `items`, `total`, `offset`, `count` and `limit`.
There are some exceptions though, like `list_keys` or `list_head` which paginate differently.
The results you're looking for are always stored under `items` and you can use the `limit`
property to get only a subset of results. Other properties can be available depending on the method.

### Streaming resources

Some resources (dataset items, key-value store records and logs)
support streaming the resource from the Apify API in parts,
without having to download the whole (potentially huge) resource to memory before processing it.

The methods to stream these resources are
[`DatasetClient.stream_items()`](#datasetclient-stream_items),
[`KeyValueStoreClient.stream_record()`](#keyvaluestoreclient-stream_record),
and [`LogClient.stream()`](#logclient-stream).

Instead of the parsed resource, they return a raw, context-managed
[`httpx.Response`](https://www.python-httpx.org/quickstart/#streaming-responses) object,
which has to be consumed using the `with` keyword,
and automatically gets closed once you exit the `with` block, preventing memory leaks and unclosed connections.

For example, to consume an actor run log in a streaming fashion, you can use this snippet:

```python
with apify_client.run('MY-RUN-ID').log().stream() as log_stream:
    if log_stream:
        for line in log_stream.iter_lines():
            print(line, end='')
```

### Asynchronous usage

To use the asynchronous [`ApifyClientAsync`](#ApifyClientAsync) in your async code,
you can use the standard `async`/`await` syntax [offered by Python](https://docs.python.org/3/library/asyncio-task.html).

For example, to run an actor and asynchronously stream its log while it's running, you can use this snippet:

```python
from apify_client import ApifyClientAsync
apify_client_async = ApifyClientAsync('MY-APIFY-TOKEN')

async def main():
    run = await apify_client_async.actor('my-actor').start()

    async with apify_client_async.run(run['id']).log().stream() as async_log_stream:
        if async_log_stream:
            async for line in async_log_stream.aiter_lines():
                print(line, end='')

asyncio.run(main())
```

### Logging

The library logs some useful debug information to the `apify_client` logger
when sending requests to the Apify API.
To have them printed out to the standard output, you need to add a handler to the logger:

```python
import logging
apify_client_logger = logging.getLogger('apify_client')
apify_client_logger.setLevel(logging.DEBUG)
apify_client_logger.addHandler(logging.StreamHandler())
```

The log records have useful properties added with the `extra` argument,
like `attempt`, `status_code`, `url`, `client_method` and `resource_id`.
To print those out, you'll need to use a custom log formatter.
To learn more about log formatters and how to use them,
please refer to the official Python [documentation on logging](https://docs.python.org/3/howto/logging.html#formatters).

## API Reference

All public classes, methods and their parameters can be inspected in this API reference.

### [](#apifyclient) ApifyClient

The Apify API client.

* [\_\_init\_\_()](#apifyclient-\_\_init\_\_)
* [actor()](#apifyclient-actor)
* [actors()](#apifyclient-actors)
* [build()](#apifyclient-build)
* [builds()](#apifyclient-builds)
* [run()](#apifyclient-run)
* [runs()](#apifyclient-runs)
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

#### [](#apifyclient-__init__) `ApifyClient.__init__(token=None, *, api_url=None, max_retries=8, min_delay_between_retries_millis=500, timeout_secs=360)`

Initialize the ApifyClient.

* **Parameters**

  * **token** (`str`, *optional*) – The Apify API token

  * **api_url** (`str`, *optional*) – The URL of the Apify API server to which to connect to. Defaults to [https://api.apify.com](https://api.apify.com)

  * **max_retries** (`int`, *optional*) – How many times to retry a failed request at most

  * **min_delay_between_retries_millis** (`int`, *optional*) – How long will the client wait between retrying requests
  (increases exponentially from this value)

  * **timeout_secs** (`int`, *optional*) – The socket timeout of the HTTP requests sent to the Apify API

***

#### [](#apifyclient-actor) `ApifyClient.actor(actor_id)`

Retrieve the sub-client for manipulating a single actor.

* **Parameters**

  * **actor_id** (`str`) – ID of the actor to be manipulated

* **Return type**

  [`ActorClient`](#actorclient)

***

#### [](#apifyclient-actors) `ApifyClient.actors()`

Retrieve the sub-client for manipulating actors.

* **Return type**

  [`ActorCollectionClient`](#actorcollectionclient)

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

#### [](#apifyclient-run) `ApifyClient.run(run_id)`

Retrieve the sub-client for manipulating a single actor run.

* **Parameters**

  * **run_id** (`str`) – ID of the actor run to be manipulated

* **Return type**

  [`RunClient`](#runclient)

***

#### [](#apifyclient-runs) `ApifyClient.runs()`

Retrieve the sub-client for querying multiple actor runs of a user.

* **Return type**

  [`RunCollectionClient`](#runcollectionclient)

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

Retrieve the sub-client for manipulating tasks.

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

### [](#apifyclientasync) ApifyClientAsync

The asynchronous version of the Apify API client.

* [\_\_init\_\_()](#apifyclientasync-\_\_init\_\_)
* [actor()](#apifyclientasync-actor)
* [actors()](#apifyclientasync-actors)
* [build()](#apifyclientasync-build)
* [builds()](#apifyclientasync-builds)
* [run()](#apifyclientasync-run)
* [runs()](#apifyclientasync-runs)
* [dataset()](#apifyclientasync-dataset)
* [datasets()](#apifyclientasync-datasets)
* [key\_value\_store()](#apifyclientasync-key\_value\_store)
* [key\_value\_stores()](#apifyclientasync-key\_value\_stores)
* [request\_queue()](#apifyclientasync-request\_queue)
* [request\_queues()](#apifyclientasync-request\_queues)
* [webhook()](#apifyclientasync-webhook)
* [webhooks()](#apifyclientasync-webhooks)
* [webhook\_dispatch()](#apifyclientasync-webhook\_dispatch)
* [webhook\_dispatches()](#apifyclientasync-webhook\_dispatches)
* [schedule()](#apifyclientasync-schedule)
* [schedules()](#apifyclientasync-schedules)
* [log()](#apifyclientasync-log)
* [task()](#apifyclientasync-task)
* [tasks()](#apifyclientasync-tasks)
* [user()](#apifyclientasync-user)

***

#### [](#apifyclientasync-__init__) `ApifyClientAsync.__init__(token=None, *, api_url=None, max_retries=8, min_delay_between_retries_millis=500, timeout_secs=360)`

Initialize the ApifyClientAsync.

* **Parameters**

  * **token** (`str`, *optional*) – The Apify API token

  * **api_url** (`str`, *optional*) – The URL of the Apify API server to which to connect to. Defaults to [https://api.apify.com](https://api.apify.com)

  * **max_retries** (`int`, *optional*) – How many times to retry a failed request at most

  * **min_delay_between_retries_millis** (`int`, *optional*) – How long will the client wait between retrying requests
  (increases exponentially from this value)

  * **timeout_secs** (`int`, *optional*) – The socket timeout of the HTTP requests sent to the Apify API

***

#### [](#apifyclientasync-actor) `ApifyClientAsync.actor(actor_id)`

Retrieve the sub-client for manipulating a single actor.

* **Parameters**

  * **actor_id** (`str`) – ID of the actor to be manipulated

* **Return type**

  `ActorClientAsync`

***

#### [](#apifyclientasync-actors) `ApifyClientAsync.actors()`

Retrieve the sub-client for manipulating actors.

* **Return type**

  `ActorCollectionClientAsync`

***

#### [](#apifyclientasync-build) `ApifyClientAsync.build(build_id)`

Retrieve the sub-client for manipulating a single actor build.

* **Parameters**

  * **build_id** (`str`) – ID of the actor build to be manipulated

* **Return type**

  `BuildClientAsync`

***

#### [](#apifyclientasync-builds) `ApifyClientAsync.builds()`

Retrieve the sub-client for querying multiple builds of a user.

* **Return type**

  `BuildCollectionClientAsync`

***

#### [](#apifyclientasync-run) `ApifyClientAsync.run(run_id)`

Retrieve the sub-client for manipulating a single actor run.

* **Parameters**

  * **run_id** (`str`) – ID of the actor run to be manipulated

* **Return type**

  `RunClientAsync`

***

#### [](#apifyclientasync-runs) `ApifyClientAsync.runs()`

Retrieve the sub-client for querying multiple actor runs of a user.

* **Return type**

  `RunCollectionClientAsync`

***

#### [](#apifyclientasync-dataset) `ApifyClientAsync.dataset(dataset_id)`

Retrieve the sub-client for manipulating a single dataset.

* **Parameters**

  * **dataset_id** (`str`) – ID of the dataset to be manipulated

* **Return type**

  `DatasetClientAsync`

***

#### [](#apifyclientasync-datasets) `ApifyClientAsync.datasets()`

Retrieve the sub-client for manipulating datasets.

* **Return type**

  `DatasetCollectionClientAsync`

***

#### [](#apifyclientasync-key_value_store) `ApifyClientAsync.key_value_store(key_value_store_id)`

Retrieve the sub-client for manipulating a single key-value store.

* **Parameters**

  * **key_value_store_id** (`str`) – ID of the key-value store to be manipulated

* **Return type**

  `KeyValueStoreClientAsync`

***

#### [](#apifyclientasync-key_value_stores) `ApifyClientAsync.key_value_stores()`

Retrieve the sub-client for manipulating key-value stores.

* **Return type**

  `KeyValueStoreCollectionClientAsync`

***

#### [](#apifyclientasync-request_queue) `ApifyClientAsync.request_queue(request_queue_id, *, client_key=None)`

Retrieve the sub-client for manipulating a single request queue.

* **Parameters**

  * **request_queue_id** (`str`) – ID of the request queue to be manipulated

  * **client_key** (`str`) – A unique identifier of the client accessing the request queue

* **Return type**

  `RequestQueueClientAsync`

***

#### [](#apifyclientasync-request_queues) `ApifyClientAsync.request_queues()`

Retrieve the sub-client for manipulating request queues.

* **Return type**

  `RequestQueueCollectionClientAsync`

***

#### [](#apifyclientasync-webhook) `ApifyClientAsync.webhook(webhook_id)`

Retrieve the sub-client for manipulating a single webhook.

* **Parameters**

  * **webhook_id** (`str`) – ID of the webhook to be manipulated

* **Return type**

  `WebhookClientAsync`

***

#### [](#apifyclientasync-webhooks) `ApifyClientAsync.webhooks()`

Retrieve the sub-client for querying multiple webhooks of a user.

* **Return type**

  `WebhookCollectionClientAsync`

***

#### [](#apifyclientasync-webhook_dispatch) `ApifyClientAsync.webhook_dispatch(webhook_dispatch_id)`

Retrieve the sub-client for accessing a single webhook dispatch.

* **Parameters**

  * **webhook_dispatch_id** (`str`) – ID of the webhook dispatch to access

* **Return type**

  `WebhookDispatchClientAsync`

***

#### [](#apifyclientasync-webhook_dispatches) `ApifyClientAsync.webhook_dispatches()`

Retrieve the sub-client for querying multiple webhook dispatches of a user.

* **Return type**

  `WebhookDispatchCollectionClientAsync`

***

#### [](#apifyclientasync-schedule) `ApifyClientAsync.schedule(schedule_id)`

Retrieve the sub-client for manipulating a single schedule.

* **Parameters**

  * **schedule_id** (`str`) – ID of the schedule to be manipulated

* **Return type**

  `ScheduleClientAsync`

***

#### [](#apifyclientasync-schedules) `ApifyClientAsync.schedules()`

Retrieve the sub-client for manipulating schedules.

* **Return type**

  `ScheduleCollectionClientAsync`

***

#### [](#apifyclientasync-log) `ApifyClientAsync.log(build_or_run_id)`

Retrieve the sub-client for retrieving logs.

* **Parameters**

  * **build_or_run_id** (`str`) – ID of the actor build or run for which to access the log

* **Return type**

  `LogClientAsync`

***

#### [](#apifyclientasync-task) `ApifyClientAsync.task(task_id)`

Retrieve the sub-client for manipulating a single task.

* **Parameters**

  * **task_id** (`str`) – ID of the task to be manipulated

* **Return type**

  `TaskClientAsync`

***

#### [](#apifyclientasync-tasks) `ApifyClientAsync.tasks()`

Retrieve the sub-client for manipulating tasks.

* **Return type**

  `TaskCollectionClientAsync`

***

#### [](#apifyclientasync-user) `ApifyClientAsync.user(user_id=None)`

Retrieve the sub-client for querying users.

* **Parameters**

  * **user_id** (`str`, *optional*) – ID of user to be queried. If `None`, queries the user belonging to the token supplied to the client

* **Return type**

  `UserClientAsync`

***

### [](#actorclient) ActorClient

Sub-client for manipulating a single actor.

* [get()](#actorclient-get)
* [update()](#actorclient-update)
* [delete()](#actorclient-delete)
* [start()](#actorclient-start)
* [call()](#actorclient-call)
* [build()](#actorclient-build)
* [builds()](#actorclient-builds)
* [runs()](#actorclient-runs)
* [last\_run()](#actorclient-last\_run)
* [versions()](#actorclient-versions)
* [version()](#actorclient-version)
* [webhooks()](#actorclient-webhooks)

***

#### [](#actorclient-get) `ActorClient.get()`

Retrieve the actor.

[https://docs.apify.com/api/v2#/reference/actors/actor-object/get-actor](https://docs.apify.com/api/v2#/reference/actors/actor-object/get-actor)

* **Returns**

  The retrieved actor

* **Return type**

  `dict`, optional

***

#### [](#actorclient-update) `ActorClient.update(*, name=None, title=None, description=None, seo_title=None, seo_description=None, versions=None, restart_on_error=None, is_public=None, is_deprecated=None, is_anonymously_runnable=None, categories=None, default_run_build=None, default_run_memory_mbytes=None, default_run_timeout_secs=None, example_run_input_body=None, example_run_input_content_type=None)`

Update the actor with the specified fields.

[https://docs.apify.com/api/v2#/reference/actors/actor-object/update-actor](https://docs.apify.com/api/v2#/reference/actors/actor-object/update-actor)

* **Parameters**

  * **name** (`str`, *optional*) – The name of the actor

  * **title** (`str`, *optional*) – The title of the actor (human-readable)

  * **description** (`str`, *optional*) – The description for the actor

  * **seo_title** (`str`, *optional*) – The title of the actor optimized for search engines

  * **seo_description** (`str`, *optional*) – The description of the actor optimized for search engines

  * **versions** (`list of dict`, *optional*) – The list of actor versions

  * **restart_on_error** (`bool`, *optional*) – If true, the main actor run process will be restarted whenever it exits with a non-zero status code.

  * **is_public** (`bool`, *optional*) – Whether the actor is public.

  * **is_deprecated** (`bool`, *optional*) – Whether the actor is deprecated.

  * **is_anonymously_runnable** (`bool`, *optional*) – Whether the actor is anonymously runnable.

  * **categories** (`list of str`, *optional*) – The categories to which the actor belongs to.

  * **default_run_build** (`str`, *optional*) – Tag or number of the build that you want to run by default.

  * **default_run_memory_mbytes** (`int`, *optional*) – Default amount of memory allocated for the runs of this actor, in megabytes.

  * **default_run_timeout_secs** (`int`, *optional*) – Default timeout for the runs of this actor in seconds.

  * **example_run_input_body** (`Any`, *optional*) – Input to be prefilled as default input to new users of this actor.

  * **example_run_input_content_type** (`str`, *optional*) – The content type of the example run input.

* **Returns**

  The updated actor

* **Return type**

  `dict`

***

#### [](#actorclient-delete) `ActorClient.delete()`

Delete the actor.

[https://docs.apify.com/api/v2#/reference/actors/actor-object/delete-actor](https://docs.apify.com/api/v2#/reference/actors/actor-object/delete-actor)

* **Return type**

  `None`

***

#### [](#actorclient-start) `ActorClient.start(*, run_input=None, content_type=None, build=None, memory_mbytes=None, timeout_secs=None, wait_for_finish=None, webhooks=None)`

Start the actor and immediately return the Run object.

[https://docs.apify.com/api/v2#/reference/actors/run-collection/run-actor](https://docs.apify.com/api/v2#/reference/actors/run-collection/run-actor)

* **Parameters**

  * **run_input** (`Any`, *optional*) – The input to pass to the actor run.

  * **content_type** (`str`, *optional*) – The content type of the input.

  * **build** (`str`, *optional*) – Specifies the actor build to run. It can be either a build tag or build number.
  By default, the run uses the build specified in the default run configuration for the actor (typically latest).

  * **memory_mbytes** (`int`, *optional*) – Memory limit for the run, in megabytes.
  By default, the run uses a memory limit specified in the default run configuration for the actor.

  * **timeout_secs** (`int`, *optional*) – Optional timeout for the run, in seconds.
  By default, the run uses timeout specified in the default run configuration for the actor.

  * **wait_for_finish** (`int`, *optional*) – The maximum number of seconds the server waits for the run to finish.
  By default, it is 0, the maximum value is 300.

  * **webhooks** (`list of dict`, *optional*) – Optional ad-hoc webhooks ([https://docs.apify.com/webhooks/ad-hoc-webhooks](https://docs.apify.com/webhooks/ad-hoc-webhooks))
  associated with the actor run which can be used to receive a notification,
  e.g. when the actor finished or failed.
  If you already have a webhook set up for the actor or task, you do not have to add it again here.
  Each webhook is represented by a dictionary containing these items:
    * `event_types`: list of [`WebhookEventType`](#webhookeventtype) values which trigger the webhook
    * `request_url`: URL to which to send the webhook HTTP request
    * `payload_template` (optional): Optional template for the request payload

* **Returns**

  The run object

* **Return type**

  `dict`

***

#### [](#actorclient-call) `ActorClient.call(*, run_input=None, content_type=None, build=None, memory_mbytes=None, timeout_secs=None, webhooks=None, wait_secs=None)`

Start the actor and wait for it to finish before returning the Run object.

It waits indefinitely, unless the wait_secs argument is provided.

[https://docs.apify.com/api/v2#/reference/actors/run-collection/run-actor](https://docs.apify.com/api/v2#/reference/actors/run-collection/run-actor)

* **Parameters**

  * **run_input** (`Any`, *optional*) – The input to pass to the actor run.

  * **content_type** (`str`, *optional*) – The content type of the input.

  * **build** (`str`, *optional*) – Specifies the actor build to run. It can be either a build tag or build number.
  By default, the run uses the build specified in the default run configuration for the actor (typically latest).

  * **memory_mbytes** (`int`, *optional*) – Memory limit for the run, in megabytes.
  By default, the run uses a memory limit specified in the default run configuration for the actor.

  * **timeout_secs** (`int`, *optional*) – Optional timeout for the run, in seconds.
  By default, the run uses timeout specified in the default run configuration for the actor.

  * **webhooks** (`list`, *optional*) – Optional webhooks ([https://docs.apify.com/webhooks](https://docs.apify.com/webhooks)) associated with the actor run,
  which can be used to receive a notification, e.g. when the actor finished or failed.
  If you already have a webhook set up for the actor, you do not have to add it again here.

  * **wait_secs** (`int`, *optional*) – The maximum number of seconds the server waits for the run to finish. If not provided, waits indefinitely.

* **Returns**

  The run object

* **Return type**

  `dict`

***

#### [](#actorclient-build) `ActorClient.build(*, version_number, beta_packages=None, tag=None, use_cache=None, wait_for_finish=None)`

Build the actor.

[https://docs.apify.com/api/v2#/reference/actors/build-collection/build-actor](https://docs.apify.com/api/v2#/reference/actors/build-collection/build-actor)

* **Parameters**

  * **version_number** (`str`) – Actor version number to be built.

  * **beta_packages** (`bool`, *optional*) – If True, then the actor is built with beta versions of Apify NPM packages.
  By default, the build uses latest stable packages.

  * **tag** (`str`, *optional*) – Tag to be applied to the build on success. By default, the tag is taken from the actor version’s buildTag property.

  * **use_cache** (`bool`, *optional*) – If true, the actor’s Docker container will be rebuilt using layer cache
  ([https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#leverage-build-cache](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#leverage-build-cache)).
  This is to enable quick rebuild during development.
  By default, the cache is not used.

  * **wait_for_finish** (`int`, *optional*) – The maximum number of seconds the server waits for the build to finish before returning.
  By default it is 0, the maximum value is 300.

* **Returns**

  The build object

* **Return type**

  `dict`

***

#### [](#actorclient-builds) `ActorClient.builds()`

Retrieve a client for the builds of this actor.

* **Return type**

  [`BuildCollectionClient`](#buildcollectionclient)

***

#### [](#actorclient-runs) `ActorClient.runs()`

Retrieve a client for the runs of this actor.

* **Return type**

  [`RunCollectionClient`](#runcollectionclient)

***

#### [](#actorclient-last_run) `ActorClient.last_run(*, status=None, origin=None)`

Retrieve the client for the last run of this actor.

Last run is retrieved based on the start time of the runs.

* **Parameters**

  * **status** ([`ActorJobStatus`](#actorjobstatus), *optional*) – Consider only runs with this status.

  * **origin** (`MetaOrigin`, *optional*) – Consider only runs started with this origin.

* **Returns**

  The resource client for the last run of this actor.

* **Return type**

  [`RunClient`](#runclient)

***

#### [](#actorclient-versions) `ActorClient.versions()`

Retrieve a client for the versions of this actor.

* **Return type**

  [`ActorVersionCollectionClient`](#actorversioncollectionclient)

***

#### [](#actorclient-version) `ActorClient.version(version_number)`

Retrieve the client for the specified version of this actor.

* **Parameters**

  * **version_number** (`str`) – The version number for which to retrieve the resource client.

* **Returns**

  The resource client for the specified actor version.

* **Return type**

  [`ActorVersionClient`](#actorversionclient)

***

#### [](#actorclient-webhooks) `ActorClient.webhooks()`

Retrieve a client for webhooks associated with this actor.

* **Return type**

  [`WebhookCollectionClient`](#webhookcollectionclient)

***

### [](#actorclientasync) ActorClientAsync

Async sub-client for manipulating a single actor.

* [async get()](#actorclientasync-get)
* [async update()](#actorclientasync-update)
* [async delete()](#actorclientasync-delete)
* [async start()](#actorclientasync-start)
* [async call()](#actorclientasync-call)
* [async build()](#actorclientasync-build)
* [builds()](#actorclientasync-builds)
* [runs()](#actorclientasync-runs)
* [last\_run()](#actorclientasync-last\_run)
* [versions()](#actorclientasync-versions)
* [version()](#actorclientasync-version)
* [webhooks()](#actorclientasync-webhooks)

***

#### [](#actorclientasync-get) `async ActorClientAsync.get()`

Retrieve the actor.

[https://docs.apify.com/api/v2#/reference/actors/actor-object/get-actor](https://docs.apify.com/api/v2#/reference/actors/actor-object/get-actor)

* **Returns**

  The retrieved actor

* **Return type**

  `dict`, optional

***

#### [](#actorclientasync-update) `async ActorClientAsync.update(*, name=None, title=None, description=None, seo_title=None, seo_description=None, versions=None, restart_on_error=None, is_public=None, is_deprecated=None, is_anonymously_runnable=None, categories=None, default_run_build=None, default_run_memory_mbytes=None, default_run_timeout_secs=None, example_run_input_body=None, example_run_input_content_type=None)`

Update the actor with the specified fields.

[https://docs.apify.com/api/v2#/reference/actors/actor-object/update-actor](https://docs.apify.com/api/v2#/reference/actors/actor-object/update-actor)

* **Parameters**

  * **name** (`str`, *optional*) – The name of the actor

  * **title** (`str`, *optional*) – The title of the actor (human-readable)

  * **description** (`str`, *optional*) – The description for the actor

  * **seo_title** (`str`, *optional*) – The title of the actor optimized for search engines

  * **seo_description** (`str`, *optional*) – The description of the actor optimized for search engines

  * **versions** (`list of dict`, *optional*) – The list of actor versions

  * **restart_on_error** (`bool`, *optional*) – If true, the main actor run process will be restarted whenever it exits with a non-zero status code.

  * **is_public** (`bool`, *optional*) – Whether the actor is public.

  * **is_deprecated** (`bool`, *optional*) – Whether the actor is deprecated.

  * **is_anonymously_runnable** (`bool`, *optional*) – Whether the actor is anonymously runnable.

  * **categories** (`list of str`, *optional*) – The categories to which the actor belongs to.

  * **default_run_build** (`str`, *optional*) – Tag or number of the build that you want to run by default.

  * **default_run_memory_mbytes** (`int`, *optional*) – Default amount of memory allocated for the runs of this actor, in megabytes.

  * **default_run_timeout_secs** (`int`, *optional*) – Default timeout for the runs of this actor in seconds.

  * **example_run_input_body** (`Any`, *optional*) – Input to be prefilled as default input to new users of this actor.

  * **example_run_input_content_type** (`str`, *optional*) – The content type of the example run input.

* **Returns**

  The updated actor

* **Return type**

  `dict`

***

#### [](#actorclientasync-delete) `async ActorClientAsync.delete()`

Delete the actor.

[https://docs.apify.com/api/v2#/reference/actors/actor-object/delete-actor](https://docs.apify.com/api/v2#/reference/actors/actor-object/delete-actor)

* **Return type**

  `None`

***

#### [](#actorclientasync-start) `async ActorClientAsync.start(*, run_input=None, content_type=None, build=None, memory_mbytes=None, timeout_secs=None, wait_for_finish=None, webhooks=None)`

Start the actor and immediately return the Run object.

[https://docs.apify.com/api/v2#/reference/actors/run-collection/run-actor](https://docs.apify.com/api/v2#/reference/actors/run-collection/run-actor)

* **Parameters**

  * **run_input** (`Any`, *optional*) – The input to pass to the actor run.

  * **content_type** (`str`, *optional*) – The content type of the input.

  * **build** (`str`, *optional*) – Specifies the actor build to run. It can be either a build tag or build number.
  By default, the run uses the build specified in the default run configuration for the actor (typically latest).

  * **memory_mbytes** (`int`, *optional*) – Memory limit for the run, in megabytes.
  By default, the run uses a memory limit specified in the default run configuration for the actor.

  * **timeout_secs** (`int`, *optional*) – Optional timeout for the run, in seconds.
  By default, the run uses timeout specified in the default run configuration for the actor.

  * **wait_for_finish** (`int`, *optional*) – The maximum number of seconds the server waits for the run to finish.
  By default, it is 0, the maximum value is 300.

  * **webhooks** (`list of dict`, *optional*) – Optional ad-hoc webhooks ([https://docs.apify.com/webhooks/ad-hoc-webhooks](https://docs.apify.com/webhooks/ad-hoc-webhooks))
  associated with the actor run which can be used to receive a notification,
  e.g. when the actor finished or failed.
  If you already have a webhook set up for the actor or task, you do not have to add it again here.
  Each webhook is represented by a dictionary containing these items:
    * `event_types`: list of [`WebhookEventType`](#webhookeventtype) values which trigger the webhook
    * `request_url`: URL to which to send the webhook HTTP request
    * `payload_template` (optional): Optional template for the request payload

* **Returns**

  The run object

* **Return type**

  `dict`

***

#### [](#actorclientasync-call) `async ActorClientAsync.call(*, run_input=None, content_type=None, build=None, memory_mbytes=None, timeout_secs=None, webhooks=None, wait_secs=None)`

Start the actor and wait for it to finish before returning the Run object.

It waits indefinitely, unless the wait_secs argument is provided.

[https://docs.apify.com/api/v2#/reference/actors/run-collection/run-actor](https://docs.apify.com/api/v2#/reference/actors/run-collection/run-actor)

* **Parameters**

  * **run_input** (`Any`, *optional*) – The input to pass to the actor run.

  * **content_type** (`str`, *optional*) – The content type of the input.

  * **build** (`str`, *optional*) – Specifies the actor build to run. It can be either a build tag or build number.
  By default, the run uses the build specified in the default run configuration for the actor (typically latest).

  * **memory_mbytes** (`int`, *optional*) – Memory limit for the run, in megabytes.
  By default, the run uses a memory limit specified in the default run configuration for the actor.

  * **timeout_secs** (`int`, *optional*) – Optional timeout for the run, in seconds.
  By default, the run uses timeout specified in the default run configuration for the actor.

  * **webhooks** (`list`, *optional*) – Optional webhooks ([https://docs.apify.com/webhooks](https://docs.apify.com/webhooks)) associated with the actor run,
  which can be used to receive a notification, e.g. when the actor finished or failed.
  If you already have a webhook set up for the actor, you do not have to add it again here.

  * **wait_secs** (`int`, *optional*) – The maximum number of seconds the server waits for the run to finish. If not provided, waits indefinitely.

* **Returns**

  The run object

* **Return type**

  `dict`

***

#### [](#actorclientasync-build) `async ActorClientAsync.build(*, version_number, beta_packages=None, tag=None, use_cache=None, wait_for_finish=None)`

Build the actor.

[https://docs.apify.com/api/v2#/reference/actors/build-collection/build-actor](https://docs.apify.com/api/v2#/reference/actors/build-collection/build-actor)

* **Parameters**

  * **version_number** (`str`) – Actor version number to be built.

  * **beta_packages** (`bool`, *optional*) – If True, then the actor is built with beta versions of Apify NPM packages.
  By default, the build uses latest stable packages.

  * **tag** (`str`, *optional*) – Tag to be applied to the build on success. By default, the tag is taken from the actor version’s buildTag property.

  * **use_cache** (`bool`, *optional*) – If true, the actor’s Docker container will be rebuilt using layer cache
  ([https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#leverage-build-cache](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#leverage-build-cache)).
  This is to enable quick rebuild during development.
  By default, the cache is not used.

  * **wait_for_finish** (`int`, *optional*) – The maximum number of seconds the server waits for the build to finish before returning.
  By default it is 0, the maximum value is 300.

* **Returns**

  The build object

* **Return type**

  `dict`

***

#### [](#actorclientasync-builds) `ActorClientAsync.builds()`

Retrieve a client for the builds of this actor.

* **Return type**

  `BuildCollectionClientAsync`

***

#### [](#actorclientasync-runs) `ActorClientAsync.runs()`

Retrieve a client for the runs of this actor.

* **Return type**

  `RunCollectionClientAsync`

***

#### [](#actorclientasync-last_run) `ActorClientAsync.last_run(*, status=None, origin=None)`

Retrieve the client for the last run of this actor.

Last run is retrieved based on the start time of the runs.

* **Parameters**

  * **status** ([`ActorJobStatus`](#actorjobstatus), *optional*) – Consider only runs with this status.

  * **origin** (`MetaOrigin`, *optional*) – Consider only runs started with this origin.

* **Returns**

  The resource client for the last run of this actor.

* **Return type**

  `RunClientAsync`

***

#### [](#actorclientasync-versions) `ActorClientAsync.versions()`

Retrieve a client for the versions of this actor.

* **Return type**

  `ActorVersionCollectionClientAsync`

***

#### [](#actorclientasync-version) `ActorClientAsync.version(version_number)`

Retrieve the client for the specified version of this actor.

* **Parameters**

  * **version_number** (`str`) – The version number for which to retrieve the resource client.

* **Returns**

  The resource client for the specified actor version.

* **Return type**

  `ActorVersionClientAsync`

***

#### [](#actorclientasync-webhooks) `ActorClientAsync.webhooks()`

Retrieve a client for webhooks associated with this actor.

* **Return type**

  `WebhookCollectionClientAsync`

***

### [](#actorcollectionclient) ActorCollectionClient

Sub-client for manipulating actors.

* [list()](#actorcollectionclient-list)
* [create()](#actorcollectionclient-create)

***

#### [](#actorcollectionclient-list) `ActorCollectionClient.list(*, my=None, limit=None, offset=None, desc=None)`

List the actors the user has created or used.

[https://docs.apify.com/api/v2#/reference/actors/actor-collection/get-list-of-actors](https://docs.apify.com/api/v2#/reference/actors/actor-collection/get-list-of-actors)

* **Parameters**

  * **my** (`bool`, *optional*) – If True, will return only actors which the user has created themselves.

  * **limit** (`int`, *optional*) – How many actors to list

  * **offset** (`int`, *optional*) – What actor to include as first when retrieving the list

  * **desc** (`bool`, *optional*) – Whether to sort the actors in descending order based on their creation date

* **Returns**

  The list of available actors matching the specified filters.

* **Return type**

  [`ListPage`](#listpage)

***

#### [](#actorcollectionclient-create) `ActorCollectionClient.create(*, name, title=None, description=None, seo_title=None, seo_description=None, versions=None, restart_on_error=None, is_public=None, is_deprecated=None, is_anonymously_runnable=None, categories=None, default_run_build=None, default_run_memory_mbytes=None, default_run_timeout_secs=None, example_run_input_body=None, example_run_input_content_type=None)`

Create a new actor.

[https://docs.apify.com/api/v2#/reference/actors/actor-collection/create-actor](https://docs.apify.com/api/v2#/reference/actors/actor-collection/create-actor)

* **Parameters**

  * **name** (`str`) – The name of the actor

  * **title** (`str`, *optional*) – The title of the actor (human-readable)

  * **description** (`str`, *optional*) – The description for the actor

  * **seo_title** (`str`, *optional*) – The title of the actor optimized for search engines

  * **seo_description** (`str`, *optional*) – The description of the actor optimized for search engines

  * **versions** (`list of dict`, *optional*) – The list of actor versions

  * **restart_on_error** (`bool`, *optional*) – If true, the main actor run process will be restarted whenever it exits with a non-zero status code.

  * **is_public** (`bool`, *optional*) – Whether the actor is public.

  * **is_deprecated** (`bool`, *optional*) – Whether the actor is deprecated.

  * **is_anonymously_runnable** (`bool`, *optional*) – Whether the actor is anonymously runnable.

  * **categories** (`list of str`, *optional*) – The categories to which the actor belongs to.

  * **default_run_build** (`str`, *optional*) – Tag or number of the build that you want to run by default.

  * **default_run_memory_mbytes** (`int`, *optional*) – Default amount of memory allocated for the runs of this actor, in megabytes.

  * **default_run_timeout_secs** (`int`, *optional*) – Default timeout for the runs of this actor in seconds.

  * **example_run_input_body** (`Any`, *optional*) – Input to be prefilled as default input to new users of this actor.

  * **example_run_input_content_type** (`str`, *optional*) – The content type of the example run input.

* **Returns**

  The created actor.

* **Return type**

  `dict`

***

### [](#actorcollectionclientasync) ActorCollectionClientAsync

Async sub-client for manipulating actors.

* [async list()](#actorcollectionclientasync-list)
* [async create()](#actorcollectionclientasync-create)

***

#### [](#actorcollectionclientasync-list) `async ActorCollectionClientAsync.list(*, my=None, limit=None, offset=None, desc=None)`

List the actors the user has created or used.

[https://docs.apify.com/api/v2#/reference/actors/actor-collection/get-list-of-actors](https://docs.apify.com/api/v2#/reference/actors/actor-collection/get-list-of-actors)

* **Parameters**

  * **my** (`bool`, *optional*) – If True, will return only actors which the user has created themselves.

  * **limit** (`int`, *optional*) – How many actors to list

  * **offset** (`int`, *optional*) – What actor to include as first when retrieving the list

  * **desc** (`bool`, *optional*) – Whether to sort the actors in descending order based on their creation date

* **Returns**

  The list of available actors matching the specified filters.

* **Return type**

  [`ListPage`](#listpage)

***

#### [](#actorcollectionclientasync-create) `async ActorCollectionClientAsync.create(*, name, title=None, description=None, seo_title=None, seo_description=None, versions=None, restart_on_error=None, is_public=None, is_deprecated=None, is_anonymously_runnable=None, categories=None, default_run_build=None, default_run_memory_mbytes=None, default_run_timeout_secs=None, example_run_input_body=None, example_run_input_content_type=None)`

Create a new actor.

[https://docs.apify.com/api/v2#/reference/actors/actor-collection/create-actor](https://docs.apify.com/api/v2#/reference/actors/actor-collection/create-actor)

* **Parameters**

  * **name** (`str`) – The name of the actor

  * **title** (`str`, *optional*) – The title of the actor (human-readable)

  * **description** (`str`, *optional*) – The description for the actor

  * **seo_title** (`str`, *optional*) – The title of the actor optimized for search engines

  * **seo_description** (`str`, *optional*) – The description of the actor optimized for search engines

  * **versions** (`list of dict`, *optional*) – The list of actor versions

  * **restart_on_error** (`bool`, *optional*) – If true, the main actor run process will be restarted whenever it exits with a non-zero status code.

  * **is_public** (`bool`, *optional*) – Whether the actor is public.

  * **is_deprecated** (`bool`, *optional*) – Whether the actor is deprecated.

  * **is_anonymously_runnable** (`bool`, *optional*) – Whether the actor is anonymously runnable.

  * **categories** (`list of str`, *optional*) – The categories to which the actor belongs to.

  * **default_run_build** (`str`, *optional*) – Tag or number of the build that you want to run by default.

  * **default_run_memory_mbytes** (`int`, *optional*) – Default amount of memory allocated for the runs of this actor, in megabytes.

  * **default_run_timeout_secs** (`int`, *optional*) – Default timeout for the runs of this actor in seconds.

  * **example_run_input_body** (`Any`, *optional*) – Input to be prefilled as default input to new users of this actor.

  * **example_run_input_content_type** (`str`, *optional*) – The content type of the example run input.

* **Returns**

  The created actor.

* **Return type**

  `dict`

***

### [](#actorversionclient) ActorVersionClient

Sub-client for manipulating a single actor version.

* [get()](#actorversionclient-get)
* [update()](#actorversionclient-update)
* [delete()](#actorversionclient-delete)
* [env\_vars()](#actorversionclient-env\_vars)
* [env\_var()](#actorversionclient-env\_var)

***

#### [](#actorversionclient-get) `ActorVersionClient.get()`

Return information about the actor version.

[https://docs.apify.com/api/v2#/reference/actors/version-object/get-version](https://docs.apify.com/api/v2#/reference/actors/version-object/get-version)

* **Returns**

  The retrieved actor version data

* **Return type**

  `dict`, optional

***

#### [](#actorversionclient-update) `ActorVersionClient.update(*, build_tag=None, env_vars=None, apply_env_vars_to_build=None, source_type=None, source_files=None, git_repo_url=None, tarball_url=None, github_gist_url=None)`

Update the actor version with specified fields.

[https://docs.apify.com/api/v2#/reference/actors/version-object/update-version](https://docs.apify.com/api/v2#/reference/actors/version-object/update-version)

* **Parameters**

  * **build_tag** (`str`, *optional*) – Tag that is automatically set to the latest successful build of the current version.

  * **env_vars** (`list of dict`, *optional*) – Environment variables that will be available to the actor run process,
  and optionally also to the build process. See the API docs for their exact structure.

  * **apply_env_vars_to_build** (`bool`, *optional*) – Whether the environment variables specified for the actor run
  will also be set to the actor build process.

  * **source_type** ([`ActorSourceType`](#actorsourcetype), *optional*) – What source type is the actor version using.

  * **source_files** (`list of dict`, *optional*) – Source code comprised of multiple files, each an item of the array.
  Required when `source_type` is [`ActorSourceType.SOURCE_FILES`](#actorsourcetype-source_files). See the API docs for the exact structure.

  * **git_repo_url** (`str`, *optional*) – The URL of a Git repository from which the source code will be cloned.
  Required when `source_type` is [`ActorSourceType.GIT_REPO`](#actorsourcetype-git_repo).

  * **tarball_url** (`str`, *optional*) – The URL of a tarball or a zip archive from which the source code will be downloaded.
  Required when `source_type` is [`ActorSourceType.TARBALL`](#actorsourcetype-tarball).

  * **github_gist_url** (`str`, *optional*) – The URL of a GitHub Gist from which the source will be downloaded.
  Required when `source_type` is [`ActorSourceType.GITHUB_GIST`](#actorsourcetype-github_gist).

* **Returns**

  The updated actor version

* **Return type**

  `dict`

***

#### [](#actorversionclient-delete) `ActorVersionClient.delete()`

Delete the actor version.

[https://docs.apify.com/api/v2#/reference/actors/version-object/delete-version](https://docs.apify.com/api/v2#/reference/actors/version-object/delete-version)

* **Return type**

  `None`

***

#### [](#actorversionclient-env_vars) `ActorVersionClient.env_vars()`

Retrieve a client for the environment variables of this actor version.

* **Return type**

  [`ActorEnvVarCollectionClient`](#actorenvvarcollectionclient)

***

#### [](#actorversionclient-env_var) `ActorVersionClient.env_var(env_var_name)`

Retrieve the client for the specified environment variable of this actor version.

* **Parameters**

  * **env_var_name** (`str`) – The name of the environment variable for which to retrieve the resource client.

* **Returns**

  The resource client for the specified actor environment variable.

* **Return type**

  [`ActorEnvVarClient`](#actorenvvarclient)

***

### [](#actorversionclientasync) ActorVersionClientAsync

Async sub-client for manipulating a single actor version.

* [async get()](#actorversionclientasync-get)
* [async update()](#actorversionclientasync-update)
* [async delete()](#actorversionclientasync-delete)
* [env\_vars()](#actorversionclientasync-env\_vars)
* [env\_var()](#actorversionclientasync-env\_var)

***

#### [](#actorversionclientasync-get) `async ActorVersionClientAsync.get()`

Return information about the actor version.

[https://docs.apify.com/api/v2#/reference/actors/version-object/get-version](https://docs.apify.com/api/v2#/reference/actors/version-object/get-version)

* **Returns**

  The retrieved actor version data

* **Return type**

  `dict`, optional

***

#### [](#actorversionclientasync-update) `async ActorVersionClientAsync.update(*, build_tag=None, env_vars=None, apply_env_vars_to_build=None, source_type=None, source_files=None, git_repo_url=None, tarball_url=None, github_gist_url=None)`

Update the actor version with specified fields.

[https://docs.apify.com/api/v2#/reference/actors/version-object/update-version](https://docs.apify.com/api/v2#/reference/actors/version-object/update-version)

* **Parameters**

  * **build_tag** (`str`, *optional*) – Tag that is automatically set to the latest successful build of the current version.

  * **env_vars** (`list of dict`, *optional*) – Environment variables that will be available to the actor run process,
  and optionally also to the build process. See the API docs for their exact structure.

  * **apply_env_vars_to_build** (`bool`, *optional*) – Whether the environment variables specified for the actor run
  will also be set to the actor build process.

  * **source_type** ([`ActorSourceType`](#actorsourcetype), *optional*) – What source type is the actor version using.

  * **source_files** (`list of dict`, *optional*) – Source code comprised of multiple files, each an item of the array.
  Required when `source_type` is [`ActorSourceType.SOURCE_FILES`](#actorsourcetype-source_files). See the API docs for the exact structure.

  * **git_repo_url** (`str`, *optional*) – The URL of a Git repository from which the source code will be cloned.
  Required when `source_type` is [`ActorSourceType.GIT_REPO`](#actorsourcetype-git_repo).

  * **tarball_url** (`str`, *optional*) – The URL of a tarball or a zip archive from which the source code will be downloaded.
  Required when `source_type` is [`ActorSourceType.TARBALL`](#actorsourcetype-tarball).

  * **github_gist_url** (`str`, *optional*) – The URL of a GitHub Gist from which the source will be downloaded.
  Required when `source_type` is [`ActorSourceType.GITHUB_GIST`](#actorsourcetype-github_gist).

* **Returns**

  The updated actor version

* **Return type**

  `dict`

***

#### [](#actorversionclientasync-delete) `async ActorVersionClientAsync.delete()`

Delete the actor version.

[https://docs.apify.com/api/v2#/reference/actors/version-object/delete-version](https://docs.apify.com/api/v2#/reference/actors/version-object/delete-version)

* **Return type**

  `None`

***

#### [](#actorversionclientasync-env_vars) `ActorVersionClientAsync.env_vars()`

Retrieve a client for the environment variables of this actor version.

* **Return type**

  `ActorEnvVarCollectionClientAsync`

***

#### [](#actorversionclientasync-env_var) `ActorVersionClientAsync.env_var(env_var_name)`

Retrieve the client for the specified environment variable of this actor version.

* **Parameters**

  * **env_var_name** (`str`) – The name of the environment variable for which to retrieve the resource client.

* **Returns**

  The resource client for the specified actor environment variable.

* **Return type**

  `ActorEnvVarClientAsync`

***

### [](#actorversioncollectionclient) ActorVersionCollectionClient

Sub-client for manipulating actor versions.

* [list()](#actorversioncollectionclient-list)
* [create()](#actorversioncollectionclient-create)

***

#### [](#actorversioncollectionclient-list) `ActorVersionCollectionClient.list()`

List the available actor versions.

[https://docs.apify.com/api/v2#/reference/actors/version-collection/get-list-of-versions](https://docs.apify.com/api/v2#/reference/actors/version-collection/get-list-of-versions)

* **Returns**

  The list of available actor versions.

* **Return type**

  [`ListPage`](#listpage)

***

#### [](#actorversioncollectionclient-create) `ActorVersionCollectionClient.create(*, version_number, build_tag=None, env_vars=None, apply_env_vars_to_build=None, source_type, source_files=None, git_repo_url=None, tarball_url=None, github_gist_url=None)`

Create a new actor version.

[https://docs.apify.com/api/v2#/reference/actors/version-collection/create-version](https://docs.apify.com/api/v2#/reference/actors/version-collection/create-version)

* **Parameters**

  * **version_number** (`str`) – Major and minor version of the actor (e.g. `1.0`)

  * **build_tag** (`str`, *optional*) – Tag that is automatically set to the latest successful build of the current version.

  * **env_vars** (`list of dict`, *optional*) – Environment variables that will be available to the actor run process,
  and optionally also to the build process. See the API docs for their exact structure.

  * **apply_env_vars_to_build** (`bool`, *optional*) – Whether the environment variables specified for the actor run
  will also be set to the actor build process.

  * **source_type** ([`ActorSourceType`](#actorsourcetype)) – What source type is the actor version using.

  * **source_files** (`list of dict`, *optional*) – Source code comprised of multiple files, each an item of the array.
  Required when `source_type` is [`ActorSourceType.SOURCE_FILES`](#actorsourcetype-source_files). See the API docs for the exact structure.

  * **git_repo_url** (`str`, *optional*) – The URL of a Git repository from which the source code will be cloned.
  Required when `source_type` is [`ActorSourceType.GIT_REPO`](#actorsourcetype-git_repo).

  * **tarball_url** (`str`, *optional*) – The URL of a tarball or a zip archive from which the source code will be downloaded.
  Required when `source_type` is [`ActorSourceType.TARBALL`](#actorsourcetype-tarball).

  * **github_gist_url** (`str`, *optional*) – The URL of a GitHub Gist from which the source will be downloaded.
  Required when `source_type` is [`ActorSourceType.GITHUB_GIST`](#actorsourcetype-github_gist).

* **Returns**

  The created actor version

* **Return type**

  `dict`

***

### [](#actorversioncollectionclientasync) ActorVersionCollectionClientAsync

Async sub-client for manipulating actor versions.

* [async list()](#actorversioncollectionclientasync-list)
* [async create()](#actorversioncollectionclientasync-create)

***

#### [](#actorversioncollectionclientasync-list) `async ActorVersionCollectionClientAsync.list()`

List the available actor versions.

[https://docs.apify.com/api/v2#/reference/actors/version-collection/get-list-of-versions](https://docs.apify.com/api/v2#/reference/actors/version-collection/get-list-of-versions)

* **Returns**

  The list of available actor versions.

* **Return type**

  [`ListPage`](#listpage)

***

#### [](#actorversioncollectionclientasync-create) `async ActorVersionCollectionClientAsync.create(*, version_number, build_tag=None, env_vars=None, apply_env_vars_to_build=None, source_type, source_files=None, git_repo_url=None, tarball_url=None, github_gist_url=None)`

Create a new actor version.

[https://docs.apify.com/api/v2#/reference/actors/version-collection/create-version](https://docs.apify.com/api/v2#/reference/actors/version-collection/create-version)

* **Parameters**

  * **version_number** (`str`) – Major and minor version of the actor (e.g. `1.0`)

  * **build_tag** (`str`, *optional*) – Tag that is automatically set to the latest successful build of the current version.

  * **env_vars** (`list of dict`, *optional*) – Environment variables that will be available to the actor run process,
  and optionally also to the build process. See the API docs for their exact structure.

  * **apply_env_vars_to_build** (`bool`, *optional*) – Whether the environment variables specified for the actor run
  will also be set to the actor build process.

  * **source_type** ([`ActorSourceType`](#actorsourcetype)) – What source type is the actor version using.

  * **source_files** (`list of dict`, *optional*) – Source code comprised of multiple files, each an item of the array.
  Required when `source_type` is [`ActorSourceType.SOURCE_FILES`](#actorsourcetype-source_files). See the API docs for the exact structure.

  * **git_repo_url** (`str`, *optional*) – The URL of a Git repository from which the source code will be cloned.
  Required when `source_type` is [`ActorSourceType.GIT_REPO`](#actorsourcetype-git_repo).

  * **tarball_url** (`str`, *optional*) – The URL of a tarball or a zip archive from which the source code will be downloaded.
  Required when `source_type` is [`ActorSourceType.TARBALL`](#actorsourcetype-tarball).

  * **github_gist_url** (`str`, *optional*) – The URL of a GitHub Gist from which the source will be downloaded.
  Required when `source_type` is [`ActorSourceType.GITHUB_GIST`](#actorsourcetype-github_gist).

* **Returns**

  The created actor version

* **Return type**

  `dict`

***

### [](#runclient) RunClient

Sub-client for manipulating a single actor run.

* [get()](#runclient-get)
* [update()](#runclient-update)
* [abort()](#runclient-abort)
* [wait\_for\_finish()](#runclient-wait\_for\_finish)
* [metamorph()](#runclient-metamorph)
* [resurrect()](#runclient-resurrect)
* [dataset()](#runclient-dataset)
* [key\_value\_store()](#runclient-key\_value\_store)
* [request\_queue()](#runclient-request\_queue)
* [log()](#runclient-log)

***

#### [](#runclient-get) `RunClient.get()`

Return information about the actor run.

[https://docs.apify.com/api/v2#/reference/actor-runs/run-object/get-run](https://docs.apify.com/api/v2#/reference/actor-runs/run-object/get-run)

* **Returns**

  The retrieved actor run data

* **Return type**

  `dict`

***

#### [](#runclient-update) `RunClient.update(*, status_message=None, is_status_message_terminal=None)`

Update the run with the specified fields.

[https://docs.apify.com/api/v2#/reference/actor-runs/run-object/update-run](https://docs.apify.com/api/v2#/reference/actor-runs/run-object/update-run)

* **Parameters**

  * **status_message** (`str`, *optional*) – The new status message for the run

  * **is_status_message_terminal** (`bool`, *optional*) – Set this flag to True if this is the final status message of the Actor run.

* **Returns**

  The updated run

* **Return type**

  `dict`

***

#### [](#runclient-abort) `RunClient.abort(*, gracefully=None)`

Abort the actor run which is starting or currently running and return its details.

[https://docs.apify.com/api/v2#/reference/actor-runs/abort-run/abort-run](https://docs.apify.com/api/v2#/reference/actor-runs/abort-run/abort-run)

* **Parameters**

  * **gracefully** (`bool`, *optional*) – If True, the actor run will abort gracefully.
  It will send `aborting` and `persistStates` events into the run and force-stop the run after 30 seconds.
  It is helpful in cases where you plan to resurrect the run later.

* **Returns**

  The data of the aborted actor run

* **Return type**

  `dict`

***

#### [](#runclient-wait_for_finish) `RunClient.wait_for_finish(*, wait_secs=None)`

Wait synchronously until the run finishes or the server times out.

* **Parameters**

  * **wait_secs** (`int`, *optional*) – how long does the client wait for run to finish. `None` for indefinite.

* **Returns**

  The actor run data. If the status on the object is not one of the terminal statuses

    (SUCEEDED, FAILED, TIMED_OUT, ABORTED), then the run has not yet finished.

* **Return type**

  `dict`, optional

***

#### [](#runclient-metamorph) `RunClient.metamorph(*, target_actor_id, target_actor_build=None, run_input=None, content_type=None)`

Transform an actor run into a run of another actor with a new input.

[https://docs.apify.com/api/v2#/reference/actor-runs/metamorph-run/metamorph-run](https://docs.apify.com/api/v2#/reference/actor-runs/metamorph-run/metamorph-run)

* **Parameters**

  * **target_actor_id** (`str`) – ID of the target actor that the run should be transformed into

  * **target_actor_build** (`str`, *optional*) – The build of the target actor. It can be either a build tag or build number.
  By default, the run uses the build specified in the default run configuration for the target actor (typically the latest build).

  * **run_input** (`Any`, *optional*) – The input to pass to the new run.

  * **content_type** (`str`, *optional*) – The content type of the input.

* **Returns**

  The actor run data.

* **Return type**

  `dict`

***

#### [](#runclient-resurrect) `RunClient.resurrect(*, build=None, memory_mbytes=None, timeout_secs=None)`

Resurrect a finished actor run.

Only finished runs, i.e. runs with status FINISHED, FAILED, ABORTED and TIMED-OUT can be resurrected.
Run status will be updated to RUNNING and its container will be restarted with the same default storages.

[https://docs.apify.com/api/v2#/reference/actor-runs/resurrect-run/resurrect-run](https://docs.apify.com/api/v2#/reference/actor-runs/resurrect-run/resurrect-run)

* **Parameters**

  * **build** (`str`, *optional*) – Which actor build the resurrected run should use. It can be either a build tag or build number.
  By default, the resurrected run uses the same build as before.

  * **memory_mbytes** (`int`, *optional*) – New memory limit for the resurrected run, in megabytes.
  By default, the resurrected run uses the same memory limit as before.

  * **timeout_secs** (`int`, *optional*) – New timeout for the resurrected run, in seconds.
  By default, the resurrected run uses the same timeout as before.

* **Returns**

  The actor run data.

* **Return type**

  `dict`

***

#### [](#runclient-dataset) `RunClient.dataset()`

Get the client for the default dataset of the actor run.

[https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages](https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages)

* **Returns**

  A client allowing access to the default dataset of this actor run.

* **Return type**

  [`DatasetClient`](#datasetclient)

***

#### [](#runclient-key_value_store) `RunClient.key_value_store()`

Get the client for the default key-value store of the actor run.

[https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages](https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages)

* **Returns**

  A client allowing access to the default key-value store of this actor run.

* **Return type**

  [`KeyValueStoreClient`](#keyvaluestoreclient)

***

#### [](#runclient-request_queue) `RunClient.request_queue()`

Get the client for the default request queue of the actor run.

[https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages](https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages)

* **Returns**

  A client allowing access to the default request_queue of this actor run.

* **Return type**

  [`RequestQueueClient`](#requestqueueclient)

***

#### [](#runclient-log) `RunClient.log()`

Get the client for the log of the actor run.

[https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages](https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages)

* **Returns**

  A client allowing access to the log of this actor run.

* **Return type**

  [`LogClient`](#logclient)

***

### [](#buildclientasync) BuildClientAsync

Async sub-client for manipulating a single actor build.

* [async get()](#buildclientasync-get)
* [async abort()](#buildclientasync-abort)
* [async wait\_for\_finish()](#buildclientasync-wait\_for\_finish)

***

#### [](#buildclientasync-get) `async BuildClientAsync.get()`

Return information about the actor build.

[https://docs.apify.com/api/v2#/reference/actor-builds/build-object/get-build](https://docs.apify.com/api/v2#/reference/actor-builds/build-object/get-build)

* **Returns**

  The retrieved actor build data

* **Return type**

  `dict`, optional

***

#### [](#buildclientasync-abort) `async BuildClientAsync.abort()`

Abort the actor build which is starting or currently running and return its details.

[https://docs.apify.com/api/v2#/reference/actor-builds/abort-build/abort-build](https://docs.apify.com/api/v2#/reference/actor-builds/abort-build/abort-build)

* **Returns**

  The data of the aborted actor build

* **Return type**

  `dict`

***

#### [](#buildclientasync-wait_for_finish) `async BuildClientAsync.wait_for_finish(*, wait_secs=None)`

Wait synchronously until the build finishes or the server times out.

* **Parameters**

  * **wait_secs** (`int`, *optional*) – how long does the client wait for build to finish. `None` for indefinite.

* **Returns**

  The actor build data. If the status on the object is not one of the terminal statuses

    (SUCEEDED, FAILED, TIMED_OUT, ABORTED), then the build has not yet finished.

* **Return type**

  `dict`, optional

***

### [](#runcollectionclient) RunCollectionClient

Sub-client for listing actor runs.

* [list()](#runcollectionclient-list)

***

#### [](#runcollectionclient-list) `RunCollectionClient.list(*, limit=None, offset=None, desc=None, status=None)`

List all actor runs (either of a single actor, or all user’s actors, depending on where this client was initialized from).

[https://docs.apify.com/api/v2#/reference/actors/run-collection/get-list-of-runs](https://docs.apify.com/api/v2#/reference/actors/run-collection/get-list-of-runs)

[https://docs.apify.com/api/v2#/reference/actor-runs/run-collection/get-user-runs-list](https://docs.apify.com/api/v2#/reference/actor-runs/run-collection/get-user-runs-list)

* **Parameters**

  * **limit** (`int`, *optional*) – How many runs to retrieve

  * **offset** (`int`, *optional*) – What run to include as first when retrieving the list

  * **desc** (`bool`, *optional*) – Whether to sort the runs in descending order based on their start date

  * **status** ([`ActorJobStatus`](#actorjobstatus), *optional*) – Retrieve only runs with the provided status

* **Returns**

  The retrieved actor runs

* **Return type**

  [`ListPage`](#listpage)

***

### [](#buildcollectionclientasync) BuildCollectionClientAsync

Async sub-client for listing actor builds.

* [async list()](#buildcollectionclientasync-list)

***

#### [](#buildcollectionclientasync-list) `async BuildCollectionClientAsync.list(*, limit=None, offset=None, desc=None)`

List all actor builds (either of a single actor, or all user’s actors, depending on where this client was initialized from).

[https://docs.apify.com/api/v2#/reference/actors/build-collection/get-list-of-builds](https://docs.apify.com/api/v2#/reference/actors/build-collection/get-list-of-builds)
[https://docs.apify.com/api/v2#/reference/actor-builds/build-collection/get-user-builds-list](https://docs.apify.com/api/v2#/reference/actor-builds/build-collection/get-user-builds-list)

* **Parameters**

  * **limit** (`int`, *optional*) – How many builds to retrieve

  * **offset** (`int`, *optional*) – What build to include as first when retrieving the list

  * **desc** (`bool`, *optional*) – Whether to sort the builds in descending order based on their start date

* **Returns**

  The retrieved actor builds

* **Return type**

  [`ListPage`](#listpage)

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

  `dict`, optional

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

### [](#datasetclientasync) DatasetClientAsync

Async sub-client for manipulating a single dataset.

* [async get()](#datasetclientasync-get)
* [async update()](#datasetclientasync-update)
* [async delete()](#datasetclientasync-delete)
* [async list\_items()](#datasetclientasync-list\_items)
* [async iterate\_items()](#datasetclientasync-iterate\_items)
* [async get\_items\_as\_bytes()](#datasetclientasync-get\_items\_as\_bytes)
* [stream\_items()](#datasetclientasync-stream\_items)
* [async push\_items()](#datasetclientasync-push\_items)

***

#### [](#datasetclientasync-get) `async DatasetClientAsync.get()`

Retrieve the dataset.

[https://docs.apify.com/api/v2#/reference/datasets/dataset/get-dataset](https://docs.apify.com/api/v2#/reference/datasets/dataset/get-dataset)

* **Returns**

  The retrieved dataset, or `None`, if it does not exist

* **Return type**

  `dict`, optional

***

#### [](#datasetclientasync-update) `async DatasetClientAsync.update(*, name=None)`

Update the dataset with specified fields.

[https://docs.apify.com/api/v2#/reference/datasets/dataset/update-dataset](https://docs.apify.com/api/v2#/reference/datasets/dataset/update-dataset)

* **Parameters**

  * **name** (`str`, *optional*) – The new name for the dataset

* **Returns**

  The updated dataset

* **Return type**

  `dict`

***

#### [](#datasetclientasync-delete) `async DatasetClientAsync.delete()`

Delete the dataset.

[https://docs.apify.com/api/v2#/reference/datasets/dataset/delete-dataset](https://docs.apify.com/api/v2#/reference/datasets/dataset/delete-dataset)

* **Return type**

  `None`

***

#### [](#datasetclientasync-list_items) `async DatasetClientAsync.list_items(*, offset=None, limit=None, clean=None, desc=None, fields=None, omit=None, unwind=None, skip_empty=None, skip_hidden=None, flatten=None, view=None)`

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

  * **flatten** (`list of str`, *optional*) – A list of fields that should be flattened

  * **view** (`str`, *optional*) – Name of the dataset view to be used

* **Returns**

  A page of the list of dataset items according to the specified filters.

* **Return type**

  [`ListPage`](#listpage)

***

#### [](#datasetclientasync-iterate_items) `async DatasetClientAsync.iterate_items(*, offset=0, limit=None, clean=None, desc=None, fields=None, omit=None, unwind=None, skip_empty=None, skip_hidden=None)`

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

  `AsyncIterator[Dict]`

***

#### [](#datasetclientasync-get_items_as_bytes) `async DatasetClientAsync.get_items_as_bytes(*, item_format='json', offset=None, limit=None, desc=None, clean=None, bom=None, delimiter=None, fields=None, omit=None, unwind=None, skip_empty=None, skip_header_row=None, skip_hidden=None, xml_root=None, xml_row=None, flatten=None)`

Get the items in the dataset as raw bytes.

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

  * **flatten** (`list of str`, *optional*) – A list of fields that should be flattened

* **Returns**

  The dataset items as raw bytes

* **Return type**

  `bytes`

***

#### [](#datasetclientasync-stream_items) `DatasetClientAsync.stream_items(*, item_format='json', offset=None, limit=None, desc=None, clean=None, bom=None, delimiter=None, fields=None, omit=None, unwind=None, skip_empty=None, skip_header_row=None, skip_hidden=None, xml_root=None, xml_row=None)`

Retrieve the items in the dataset as a stream.

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

  The dataset items as a context-managed streaming Response

* **Return type**

  `httpx.Response`

***

#### [](#datasetclientasync-push_items) `async DatasetClientAsync.push_items(items)`

Push items to the dataset.

[https://docs.apify.com/api/v2#/reference/datasets/item-collection/put-items](https://docs.apify.com/api/v2#/reference/datasets/item-collection/put-items)

* **Parameters**

  * **items** (`Union[str, int, float, bool, None, Dict[str, Any], List[Any]]`) – The items which to push in the dataset. Either a stringified JSON, a dictionary, or a list of strings or dictionaries.

* **Return type**

  `None`

***

### [](#buildcollectionclient) BuildCollectionClient

Sub-client for listing actor builds.

* [list()](#buildcollectionclient-list)

***

#### [](#buildcollectionclient-list) `BuildCollectionClient.list(*, limit=None, offset=None, desc=None)`

List all actor builds (either of a single actor, or all user’s actors, depending on where this client was initialized from).

[https://docs.apify.com/api/v2#/reference/actors/build-collection/get-list-of-builds](https://docs.apify.com/api/v2#/reference/actors/build-collection/get-list-of-builds)
[https://docs.apify.com/api/v2#/reference/actor-builds/build-collection/get-user-builds-list](https://docs.apify.com/api/v2#/reference/actor-builds/build-collection/get-user-builds-list)

* **Parameters**

  * **limit** (`int`, *optional*) – How many builds to retrieve

  * **offset** (`int`, *optional*) – What build to include as first when retrieving the list

  * **desc** (`bool`, *optional*) – Whether to sort the builds in descending order based on their start date

* **Returns**

  The retrieved actor builds

* **Return type**

  [`ListPage`](#listpage)

***

### [](#datasetcollectionclientasync) DatasetCollectionClientAsync

Async sub-client for manipulating datasets.

* [async list()](#datasetcollectionclientasync-list)
* [async get\_or\_create()](#datasetcollectionclientasync-get\_or\_create)

***

#### [](#datasetcollectionclientasync-list) `async DatasetCollectionClientAsync.list(*, unnamed=None, limit=None, offset=None, desc=None)`

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

  [`ListPage`](#listpage)

***

#### [](#datasetcollectionclientasync-get_or_create) `async DatasetCollectionClientAsync.get_or_create(*, name=None, schema=None)`

Retrieve a named dataset, or create a new one when it doesn’t exist.

[https://docs.apify.com/api/v2#/reference/datasets/dataset-collection/create-dataset](https://docs.apify.com/api/v2#/reference/datasets/dataset-collection/create-dataset)

* **Parameters**

  * **name** (`str`, *optional*) – The name of the dataset to retrieve or create.

  * **schema** (`Dict`, *optional*) – The schema of the dataset

* **Returns**

  The retrieved or newly-created dataset.

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
* [get\_items\_as\_bytes()](#datasetclient-get\_items\_as\_bytes)
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

#### [](#datasetclient-update) `DatasetClient.update(*, name=None)`

Update the dataset with specified fields.

[https://docs.apify.com/api/v2#/reference/datasets/dataset/update-dataset](https://docs.apify.com/api/v2#/reference/datasets/dataset/update-dataset)

* **Parameters**

  * **name** (`str`, *optional*) – The new name for the dataset

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

#### [](#datasetclient-list_items) `DatasetClient.list_items(*, offset=None, limit=None, clean=None, desc=None, fields=None, omit=None, unwind=None, skip_empty=None, skip_hidden=None, flatten=None, view=None)`

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

  * **flatten** (`list of str`, *optional*) – A list of fields that should be flattened

  * **view** (`str`, *optional*) – Name of the dataset view to be used

* **Returns**

  A page of the list of dataset items according to the specified filters.

* **Return type**

  [`ListPage`](#listpage)

***

#### [](#datasetclient-iterate_items) `DatasetClient.iterate_items(*, offset=0, limit=None, clean=None, desc=None, fields=None, omit=None, unwind=None, skip_empty=None, skip_hidden=None)`

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

  `Iterator[Dict]`

***

#### [](#datasetclient-download_items) `DatasetClient.download_items(*, item_format='json', offset=None, limit=None, desc=None, clean=None, bom=None, delimiter=None, fields=None, omit=None, unwind=None, skip_empty=None, skip_header_row=None, skip_hidden=None, xml_root=None, xml_row=None, flatten=None)`

Get the items in the dataset as raw bytes.

Deprecated: this function is a deprecated alias of get_items_as_bytes. It will be removed in a future version.

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

  * **flatten** (`list of str`, *optional*) – A list of fields that should be flattened

* **Returns**

  The dataset items as raw bytes

* **Return type**

  `bytes`

***

#### [](#datasetclient-get_items_as_bytes) `DatasetClient.get_items_as_bytes(*, item_format='json', offset=None, limit=None, desc=None, clean=None, bom=None, delimiter=None, fields=None, omit=None, unwind=None, skip_empty=None, skip_header_row=None, skip_hidden=None, xml_root=None, xml_row=None, flatten=None)`

Get the items in the dataset as raw bytes.

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

  * **flatten** (`list of str`, *optional*) – A list of fields that should be flattened

* **Returns**

  The dataset items as raw bytes

* **Return type**

  `bytes`

***

#### [](#datasetclient-stream_items) `DatasetClient.stream_items(*, item_format='json', offset=None, limit=None, desc=None, clean=None, bom=None, delimiter=None, fields=None, omit=None, unwind=None, skip_empty=None, skip_header_row=None, skip_hidden=None, xml_root=None, xml_row=None)`

Retrieve the items in the dataset as a stream.

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

  The dataset items as a context-managed streaming Response

* **Return type**

  `httpx.Response`

***

#### [](#datasetclient-push_items) `DatasetClient.push_items(items)`

Push items to the dataset.

[https://docs.apify.com/api/v2#/reference/datasets/item-collection/put-items](https://docs.apify.com/api/v2#/reference/datasets/item-collection/put-items)

* **Parameters**

  * **items** (`Union[str, int, float, bool, None, Dict[str, Any], List[Any]]`) – The items which to push in the dataset. Either a stringified JSON, a dictionary, or a list of strings or dictionaries.

* **Return type**

  `None`

***

### [](#keyvaluestoreclientasync) KeyValueStoreClientAsync

Async sub-client for manipulating a single key-value store.

* [async get()](#keyvaluestoreclientasync-get)
* [async update()](#keyvaluestoreclientasync-update)
* [async delete()](#keyvaluestoreclientasync-delete)
* [async list\_keys()](#keyvaluestoreclientasync-list\_keys)
* [async get\_record()](#keyvaluestoreclientasync-get\_record)
* [async get\_record\_as\_bytes()](#keyvaluestoreclientasync-get\_record\_as\_bytes)
* [stream\_record()](#keyvaluestoreclientasync-stream\_record)
* [async set\_record()](#keyvaluestoreclientasync-set\_record)
* [async delete\_record()](#keyvaluestoreclientasync-delete\_record)

***

#### [](#keyvaluestoreclientasync-get) `async KeyValueStoreClientAsync.get()`

Retrieve the key-value store.

[https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/get-store](https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/get-store)

* **Returns**

  The retrieved key-value store, or `None` if it does not exist

* **Return type**

  `dict`, optional

***

#### [](#keyvaluestoreclientasync-update) `async KeyValueStoreClientAsync.update(*, name=None)`

Update the key-value store with specified fields.

[https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/update-store](https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/update-store)

* **Parameters**

  * **name** (`str`, *optional*) – The new name for key-value store

* **Returns**

  The updated key-value store

* **Return type**

  `dict`

***

#### [](#keyvaluestoreclientasync-delete) `async KeyValueStoreClientAsync.delete()`

Delete the key-value store.

[https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/delete-store](https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/delete-store)

* **Return type**

  `None`

***

#### [](#keyvaluestoreclientasync-list_keys) `async KeyValueStoreClientAsync.list_keys(*, limit=None, exclusive_start_key=None)`

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

#### [](#keyvaluestoreclientasync-get_record) `async KeyValueStoreClientAsync.get_record(key)`

Retrieve the given record from the key-value store.

[https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record](https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record)

* **Parameters**

  * **key** (`str`) – Key of the record to retrieve

  * **as_bytes** (`bool`, *optional*) – Deprecated, use get_record_as_bytes() instead. Whether to retrieve the record as raw bytes, default False

  * **as_file** (`bool`, *optional*) – Deprecated, use stream_record() instead. Whether to retrieve the record as a file-like object, default False

* **Returns**

  The requested record, or `None`, if the record does not exist

* **Return type**

  `dict`, optional

***

#### [](#keyvaluestoreclientasync-get_record_as_bytes) `async KeyValueStoreClientAsync.get_record_as_bytes(key)`

Retrieve the given record from the key-value store, without parsing it.

[https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record](https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record)

* **Parameters**

  * **key** (`str`) – Key of the record to retrieve

* **Returns**

  The requested record, or `None`, if the record does not exist

* **Return type**

  `dict`, optional

***

#### [](#keyvaluestoreclientasync-stream_record) `KeyValueStoreClientAsync.stream_record(key)`

Retrieve the given record from the key-value store, as a stream.

[https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record](https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record)

* **Parameters**

  * **key** (`str`) – Key of the record to retrieve

* **Returns**

  The requested record as a context-managed streaming Response, or `None`, if the record does not exist

* **Return type**

  `dict`, optional

***

#### [](#keyvaluestoreclientasync-set_record) `async KeyValueStoreClientAsync.set_record(key, value, content_type=None)`

Set a value to the given record in the key-value store.

[https://docs.apify.com/api/v2#/reference/key-value-stores/record/put-record](https://docs.apify.com/api/v2#/reference/key-value-stores/record/put-record)

* **Parameters**

  * **key** (`str`) – The key of the record to save the value to

  * **value** (`Any`) – The value to save into the record

  * **content_type** (`str`, *optional*) – The content type of the saved value

* **Return type**

  `None`

***

#### [](#keyvaluestoreclientasync-delete_record) `async KeyValueStoreClientAsync.delete_record(key)`

Delete the specified record from the key-value store.

[https://docs.apify.com/api/v2#/reference/key-value-stores/record/delete-record](https://docs.apify.com/api/v2#/reference/key-value-stores/record/delete-record)

* **Parameters**

  * **key** (`str`) – The key of the record which to delete

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

  [`ListPage`](#listpage)

***

#### [](#datasetcollectionclient-get_or_create) `DatasetCollectionClient.get_or_create(*, name=None, schema=None)`

Retrieve a named dataset, or create a new one when it doesn’t exist.

[https://docs.apify.com/api/v2#/reference/datasets/dataset-collection/create-dataset](https://docs.apify.com/api/v2#/reference/datasets/dataset-collection/create-dataset)

* **Parameters**

  * **name** (`str`, *optional*) – The name of the dataset to retrieve or create.

  * **schema** (`Dict`, *optional*) – The schema of the dataset

* **Returns**

  The retrieved or newly-created dataset.

* **Return type**

  `dict`

***

### [](#keyvaluestorecollectionclientasync) KeyValueStoreCollectionClientAsync

Async sub-client for manipulating key-value stores.

* [async list()](#keyvaluestorecollectionclientasync-list)
* [async get\_or\_create()](#keyvaluestorecollectionclientasync-get\_or\_create)

***

#### [](#keyvaluestorecollectionclientasync-list) `async KeyValueStoreCollectionClientAsync.list(*, unnamed=None, limit=None, offset=None, desc=None)`

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

  [`ListPage`](#listpage)

***

#### [](#keyvaluestorecollectionclientasync-get_or_create) `async KeyValueStoreCollectionClientAsync.get_or_create(*, name=None, schema=None)`

Retrieve a named key-value store, or create a new one when it doesn’t exist.

[https://docs.apify.com/api/v2#/reference/key-value-stores/store-collection/create-key-value-store](https://docs.apify.com/api/v2#/reference/key-value-stores/store-collection/create-key-value-store)

* **Parameters**

  * **name** (`str`, *optional*) – The name of the key-value store to retrieve or create.

  * **schema** (`Dict`, *optional*) – The schema of the key-value store

* **Returns**

  The retrieved or newly-created key-value store.

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
* [get\_record\_as\_bytes()](#keyvaluestoreclient-get\_record\_as\_bytes)
* [stream\_record()](#keyvaluestoreclient-stream\_record)
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

#### [](#keyvaluestoreclient-update) `KeyValueStoreClient.update(*, name=None)`

Update the key-value store with specified fields.

[https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/update-store](https://docs.apify.com/api/v2#/reference/key-value-stores/store-object/update-store)

* **Parameters**

  * **name** (`str`, *optional*) – The new name for key-value store

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

  * **as_bytes** (`bool`, *optional*) – Deprecated, use get_record_as_bytes() instead. Whether to retrieve the record as raw bytes, default False

  * **as_file** (`bool`, *optional*) – Deprecated, use stream_record() instead. Whether to retrieve the record as a file-like object, default False

* **Returns**

  The requested record, or `None`, if the record does not exist

* **Return type**

  `dict`, optional

***

#### [](#keyvaluestoreclient-get_record_as_bytes) `KeyValueStoreClient.get_record_as_bytes(key)`

Retrieve the given record from the key-value store, without parsing it.

[https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record](https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record)

* **Parameters**

  * **key** (`str`) – Key of the record to retrieve

* **Returns**

  The requested record, or `None`, if the record does not exist

* **Return type**

  `dict`, optional

***

#### [](#keyvaluestoreclient-stream_record) `KeyValueStoreClient.stream_record(key)`

Retrieve the given record from the key-value store, as a stream.

[https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record](https://docs.apify.com/api/v2#/reference/key-value-stores/record/get-record)

* **Parameters**

  * **key** (`str`) – Key of the record to retrieve

* **Returns**

  The requested record as a context-managed streaming Response, or `None`, if the record does not exist

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

### [](#logclientasync) LogClientAsync

Async sub-client for manipulating logs.

* [async get()](#logclientasync-get)
* [async get\_as\_bytes()](#logclientasync-get\_as\_bytes)
* [stream()](#logclientasync-stream)

***

#### [](#logclientasync-get) `async LogClientAsync.get()`

Retrieve the log as text.

[https://docs.apify.com/api/v2#/reference/logs/log/get-log](https://docs.apify.com/api/v2#/reference/logs/log/get-log)

* **Returns**

  The retrieved log, or `None`, if it does not exist.

* **Return type**

  `str`, optional

***

#### [](#logclientasync-get_as_bytes) `async LogClientAsync.get_as_bytes()`

Retrieve the log as raw bytes.

[https://docs.apify.com/api/v2#/reference/logs/log/get-log](https://docs.apify.com/api/v2#/reference/logs/log/get-log)

* **Returns**

  The retrieved log as raw bytes, or `None`, if it does not exist.

* **Return type**

  `bytes`, optional

***

#### [](#logclientasync-stream) `LogClientAsync.stream()`

Retrieve the log as a stream.

[https://docs.apify.com/api/v2#/reference/logs/log/get-log](https://docs.apify.com/api/v2#/reference/logs/log/get-log)

* **Returns**

  The retrieved log as a context-managed streaming Response, or `None`, if it does not exist.

* **Return type**

  `httpx.Response`, optional

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

  [`ListPage`](#listpage)

***

#### [](#keyvaluestorecollectionclient-get_or_create) `KeyValueStoreCollectionClient.get_or_create(*, name=None, schema=None)`

Retrieve a named key-value store, or create a new one when it doesn’t exist.

[https://docs.apify.com/api/v2#/reference/key-value-stores/store-collection/create-key-value-store](https://docs.apify.com/api/v2#/reference/key-value-stores/store-collection/create-key-value-store)

* **Parameters**

  * **name** (`str`, *optional*) – The name of the key-value store to retrieve or create.

  * **schema** (`Dict`, *optional*) – The schema of the key-value store

* **Returns**

  The retrieved or newly-created key-value store.

* **Return type**

  `dict`

***

### [](#requestqueueclientasync) RequestQueueClientAsync

Async sub-client for manipulating a single request queue.

* [async get()](#requestqueueclientasync-get)
* [async update()](#requestqueueclientasync-update)
* [async delete()](#requestqueueclientasync-delete)
* [async list\_head()](#requestqueueclientasync-list\_head)
* [async add\_request()](#requestqueueclientasync-add\_request)
* [async get\_request()](#requestqueueclientasync-get\_request)
* [async update\_request()](#requestqueueclientasync-update\_request)
* [async delete\_request()](#requestqueueclientasync-delete\_request)

***

#### [](#requestqueueclientasync-get) `async RequestQueueClientAsync.get()`

Retrieve the request queue.

[https://docs.apify.com/api/v2#/reference/request-queues/queue/get-request-queue](https://docs.apify.com/api/v2#/reference/request-queues/queue/get-request-queue)

* **Returns**

  The retrieved request queue, or `None`, if it does not exist

* **Return type**

  `dict`, optional

***

#### [](#requestqueueclientasync-update) `async RequestQueueClientAsync.update(*, name=None)`

Update the request queue with specified fields.

[https://docs.apify.com/api/v2#/reference/request-queues/queue/update-request-queue](https://docs.apify.com/api/v2#/reference/request-queues/queue/update-request-queue)

* **Parameters**

  * **name** (`str`, *optional*) – The new name for the request queue

* **Returns**

  The updated request queue

* **Return type**

  `dict`

***

#### [](#requestqueueclientasync-delete) `async RequestQueueClientAsync.delete()`

Delete the request queue.

[https://docs.apify.com/api/v2#/reference/request-queues/queue/delete-request-queue](https://docs.apify.com/api/v2#/reference/request-queues/queue/delete-request-queue)

* **Return type**

  `None`

***

#### [](#requestqueueclientasync-list_head) `async RequestQueueClientAsync.list_head(*, limit=None)`

Retrieve a given number of requests from the beginning of the queue.

[https://docs.apify.com/api/v2#/reference/request-queues/queue-head/get-head](https://docs.apify.com/api/v2#/reference/request-queues/queue-head/get-head)

* **Parameters**

  * **limit** (`int`, *optional*) – How many requests to retrieve

* **Returns**

  The desired number of requests from the beginning of the queue.

* **Return type**

  `dict`

***

#### [](#requestqueueclientasync-add_request) `async RequestQueueClientAsync.add_request(request, *, forefront=None)`

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

#### [](#requestqueueclientasync-get_request) `async RequestQueueClientAsync.get_request(request_id)`

Retrieve a request from the queue.

[https://docs.apify.com/api/v2#/reference/request-queues/request/get-request](https://docs.apify.com/api/v2#/reference/request-queues/request/get-request)

* **Parameters**

  * **request_id** (`str`) – ID of the request to retrieve

* **Returns**

  The retrieved request, or `None`, if it did not exist.

* **Return type**

  `dict`, optional

***

#### [](#requestqueueclientasync-update_request) `async RequestQueueClientAsync.update_request(request, *, forefront=None)`

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

#### [](#requestqueueclientasync-delete_request) `async RequestQueueClientAsync.delete_request(request_id)`

Delete a request from the queue.

[https://docs.apify.com/api/v2#/reference/request-queues/request/delete-request](https://docs.apify.com/api/v2#/reference/request-queues/request/delete-request)

* **Parameters**

  * **request_id** (`str`) – ID of the request to delete.

* **Return type**

  `None`

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

#### [](#requestqueueclient-update) `RequestQueueClient.update(*, name=None)`

Update the request queue with specified fields.

[https://docs.apify.com/api/v2#/reference/request-queues/queue/update-request-queue](https://docs.apify.com/api/v2#/reference/request-queues/queue/update-request-queue)

* **Parameters**

  * **name** (`str`, *optional*) – The new name for the request queue

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

### [](#requestqueuecollectionclientasync) RequestQueueCollectionClientAsync

Async sub-client for manipulating request queues.

* [async list()](#requestqueuecollectionclientasync-list)
* [async get\_or\_create()](#requestqueuecollectionclientasync-get\_or\_create)

***

#### [](#requestqueuecollectionclientasync-list) `async RequestQueueCollectionClientAsync.list(*, unnamed=None, limit=None, offset=None, desc=None)`

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

  [`ListPage`](#listpage)

***

#### [](#requestqueuecollectionclientasync-get_or_create) `async RequestQueueCollectionClientAsync.get_or_create(*, name=None)`

Retrieve a named request queue, or create a new one when it doesn’t exist.

[https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/create-request-queue](https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/create-request-queue)

* **Parameters**

  * **name** (`str`, *optional*) – The name of the request queue to retrieve or create.

* **Returns**

  The retrieved or newly-created request queue.

* **Return type**

  `dict`

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

  [`ListPage`](#listpage)

***

#### [](#requestqueuecollectionclient-get_or_create) `RequestQueueCollectionClient.get_or_create(*, name=None)`

Retrieve a named request queue, or create a new one when it doesn’t exist.

[https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/create-request-queue](https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/create-request-queue)

* **Parameters**

  * **name** (`str`, *optional*) – The name of the request queue to retrieve or create.

* **Returns**

  The retrieved or newly-created request queue.

* **Return type**

  `dict`

***

### [](#runclientasync) RunClientAsync

Async sub-client for manipulating a single actor run.

* [async get()](#runclientasync-get)
* [async update()](#runclientasync-update)
* [async abort()](#runclientasync-abort)
* [async wait\_for\_finish()](#runclientasync-wait\_for\_finish)
* [async metamorph()](#runclientasync-metamorph)
* [async resurrect()](#runclientasync-resurrect)
* [dataset()](#runclientasync-dataset)
* [key\_value\_store()](#runclientasync-key\_value\_store)
* [request\_queue()](#runclientasync-request\_queue)
* [log()](#runclientasync-log)

***

#### [](#runclientasync-get) `async RunClientAsync.get()`

Return information about the actor run.

[https://docs.apify.com/api/v2#/reference/actor-runs/run-object/get-run](https://docs.apify.com/api/v2#/reference/actor-runs/run-object/get-run)

* **Returns**

  The retrieved actor run data

* **Return type**

  `dict`

***

#### [](#runclientasync-update) `async RunClientAsync.update(*, status_message=None, is_status_message_terminal=None)`

Update the run with the specified fields.

[https://docs.apify.com/api/v2#/reference/actor-runs/run-object/update-run](https://docs.apify.com/api/v2#/reference/actor-runs/run-object/update-run)

* **Parameters**

  * **status_message** (`str`, *optional*) – The new status message for the run

  * **is_status_message_terminal** (`bool`, *optional*) – Set this flag to True if this is the final status message of the Actor run.

* **Returns**

  The updated run

* **Return type**

  `dict`

***

#### [](#runclientasync-abort) `async RunClientAsync.abort(*, gracefully=None)`

Abort the actor run which is starting or currently running and return its details.

[https://docs.apify.com/api/v2#/reference/actor-runs/abort-run/abort-run](https://docs.apify.com/api/v2#/reference/actor-runs/abort-run/abort-run)

* **Parameters**

  * **gracefully** (`bool`, *optional*) – If True, the actor run will abort gracefully.
  It will send `aborting` and `persistStates` events into the run and force-stop the run after 30 seconds.
  It is helpful in cases where you plan to resurrect the run later.

* **Returns**

  The data of the aborted actor run

* **Return type**

  `dict`

***

#### [](#runclientasync-wait_for_finish) `async RunClientAsync.wait_for_finish(*, wait_secs=None)`

Wait synchronously until the run finishes or the server times out.

* **Parameters**

  * **wait_secs** (`int`, *optional*) – how long does the client wait for run to finish. `None` for indefinite.

* **Returns**

  The actor run data. If the status on the object is not one of the terminal statuses

    (SUCEEDED, FAILED, TIMED_OUT, ABORTED), then the run has not yet finished.

* **Return type**

  `dict`, optional

***

#### [](#runclientasync-metamorph) `async RunClientAsync.metamorph(*, target_actor_id, target_actor_build=None, run_input=None, content_type=None)`

Transform an actor run into a run of another actor with a new input.

[https://docs.apify.com/api/v2#/reference/actor-runs/metamorph-run/metamorph-run](https://docs.apify.com/api/v2#/reference/actor-runs/metamorph-run/metamorph-run)

* **Parameters**

  * **target_actor_id** (`str`) – ID of the target actor that the run should be transformed into

  * **target_actor_build** (`str`, *optional*) – The build of the target actor. It can be either a build tag or build number.
  By default, the run uses the build specified in the default run configuration for the target actor (typically the latest build).

  * **run_input** (`Any`, *optional*) – The input to pass to the new run.

  * **content_type** (`str`, *optional*) – The content type of the input.

* **Returns**

  The actor run data.

* **Return type**

  `dict`

***

#### [](#runclientasync-resurrect) `async RunClientAsync.resurrect(*, build=None, memory_mbytes=None, timeout_secs=None)`

Resurrect a finished actor run.

Only finished runs, i.e. runs with status FINISHED, FAILED, ABORTED and TIMED-OUT can be resurrected.
Run status will be updated to RUNNING and its container will be restarted with the same default storages.

[https://docs.apify.com/api/v2#/reference/actor-runs/resurrect-run/resurrect-run](https://docs.apify.com/api/v2#/reference/actor-runs/resurrect-run/resurrect-run)

* **Parameters**

  * **build** (`str`, *optional*) – Which actor build the resurrected run should use. It can be either a build tag or build number.
  By default, the resurrected run uses the same build as before.

  * **memory_mbytes** (`int`, *optional*) – New memory limit for the resurrected run, in megabytes.
  By default, the resurrected run uses the same memory limit as before.

  * **timeout_secs** (`int`, *optional*) – New timeout for the resurrected run, in seconds.
  By default, the resurrected run uses the same timeout as before.

* **Returns**

  The actor run data.

* **Return type**

  `dict`

***

#### [](#runclientasync-dataset) `RunClientAsync.dataset()`

Get the client for the default dataset of the actor run.

[https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages](https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages)

* **Returns**

  A client allowing access to the default dataset of this actor run.

* **Return type**

  `DatasetClientAsync`

***

#### [](#runclientasync-key_value_store) `RunClientAsync.key_value_store()`

Get the client for the default key-value store of the actor run.

[https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages](https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages)

* **Returns**

  A client allowing access to the default key-value store of this actor run.

* **Return type**

  `KeyValueStoreClientAsync`

***

#### [](#runclientasync-request_queue) `RunClientAsync.request_queue()`

Get the client for the default request queue of the actor run.

[https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages](https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages)

* **Returns**

  A client allowing access to the default request_queue of this actor run.

* **Return type**

  `RequestQueueClientAsync`

***

#### [](#runclientasync-log) `RunClientAsync.log()`

Get the client for the log of the actor run.

[https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages](https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages)

* **Returns**

  A client allowing access to the log of this actor run.

* **Return type**

  `LogClientAsync`

***

### [](#logclient) LogClient

Sub-client for manipulating logs.

* [get()](#logclient-get)
* [get\_as\_bytes()](#logclient-get\_as\_bytes)
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

#### [](#logclient-get_as_bytes) `LogClient.get_as_bytes()`

Retrieve the log as raw bytes.

[https://docs.apify.com/api/v2#/reference/logs/log/get-log](https://docs.apify.com/api/v2#/reference/logs/log/get-log)

* **Returns**

  The retrieved log as raw bytes, or `None`, if it does not exist.

* **Return type**

  `bytes`, optional

***

#### [](#logclient-stream) `LogClient.stream()`

Retrieve the log as a stream.

[https://docs.apify.com/api/v2#/reference/logs/log/get-log](https://docs.apify.com/api/v2#/reference/logs/log/get-log)

* **Returns**

  The retrieved log as a context-managed streaming Response, or `None`, if it does not exist.

* **Return type**

  `httpx.Response`, optional

***

### [](#runcollectionclientasync) RunCollectionClientAsync

Async sub-client for listing actor runs.

* [async list()](#runcollectionclientasync-list)

***

#### [](#runcollectionclientasync-list) `async RunCollectionClientAsync.list(*, limit=None, offset=None, desc=None, status=None)`

List all actor runs (either of a single actor, or all user’s actors, depending on where this client was initialized from).

[https://docs.apify.com/api/v2#/reference/actors/run-collection/get-list-of-runs](https://docs.apify.com/api/v2#/reference/actors/run-collection/get-list-of-runs)

[https://docs.apify.com/api/v2#/reference/actor-runs/run-collection/get-user-runs-list](https://docs.apify.com/api/v2#/reference/actor-runs/run-collection/get-user-runs-list)

* **Parameters**

  * **limit** (`int`, *optional*) – How many runs to retrieve

  * **offset** (`int`, *optional*) – What run to include as first when retrieving the list

  * **desc** (`bool`, *optional*) – Whether to sort the runs in descending order based on their start date

  * **status** ([`ActorJobStatus`](#actorjobstatus), *optional*) – Retrieve only runs with the provided status

* **Returns**

  The retrieved actor runs

* **Return type**

  [`ListPage`](#listpage)

***

### [](#webhookclient) WebhookClient

Sub-client for manipulating a single webhook.

* [get()](#webhookclient-get)
* [update()](#webhookclient-update)
* [delete()](#webhookclient-delete)
* [test()](#webhookclient-test)
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

  * **event_types** ([`list of WebhookEventType`](#webhookeventtype), *optional*) – List of event types that should trigger the webhook. At least one is required.

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

#### [](#webhookclient-test) `WebhookClient.test()`

Test a webhook.

Creates a webhook dispatch with a dummy payload.

[https://docs.apify.com/api/v2#/reference/webhooks/webhook-test/test-webhook](https://docs.apify.com/api/v2#/reference/webhooks/webhook-test/test-webhook)

* **Returns**

  The webhook dispatch created by the test

* **Return type**

  `dict`, optional

***

#### [](#webhookclient-dispatches) `WebhookClient.dispatches()`

Get dispatches of the webhook.

[https://docs.apify.com/api/v2#/reference/webhooks/dispatches-collection/get-collection](https://docs.apify.com/api/v2#/reference/webhooks/dispatches-collection/get-collection)

* **Returns**

  A client allowing access to dispatches of this webhook using its list method

* **Return type**

  [`WebhookDispatchCollectionClient`](#webhookdispatchcollectionclient)

***

### [](#scheduleclientasync) ScheduleClientAsync

Async sub-client for manipulating a single schedule.

* [async get()](#scheduleclientasync-get)
* [async update()](#scheduleclientasync-update)
* [async delete()](#scheduleclientasync-delete)
* [async get\_log()](#scheduleclientasync-get\_log)

***

#### [](#scheduleclientasync-get) `async ScheduleClientAsync.get()`

Return information about the schedule.

[https://docs.apify.com/api/v2#/reference/schedules/schedule-object/get-schedule](https://docs.apify.com/api/v2#/reference/schedules/schedule-object/get-schedule)

* **Returns**

  The retrieved schedule

* **Return type**

  `dict`, optional

***

#### [](#scheduleclientasync-update) `async ScheduleClientAsync.update(*, cron_expression=None, is_enabled=None, is_exclusive=None, name=None, actions=None, description=None, timezone=None, title=None)`

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

  * **title** (`str`, *optional*) – A human-friendly equivalent of the name

* **Returns**

  The updated schedule

* **Return type**

  `dict`

***

#### [](#scheduleclientasync-delete) `async ScheduleClientAsync.delete()`

Delete the schedule.

[https://docs.apify.com/api/v2#/reference/schedules/schedule-object/delete-schedule](https://docs.apify.com/api/v2#/reference/schedules/schedule-object/delete-schedule)

* **Return type**

  `None`

***

#### [](#scheduleclientasync-get_log) `async ScheduleClientAsync.get_log()`

Return log for the given schedule.

[https://docs.apify.com/api/v2#/reference/schedules/schedule-log/get-schedule-log](https://docs.apify.com/api/v2#/reference/schedules/schedule-log/get-schedule-log)

* **Returns**

  Retrieved log of the given schedule

* **Return type**

  `list`, optional

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

  [`ListPage`](#listpage)

***

#### [](#webhookcollectionclient-create) `WebhookCollectionClient.create(*, event_types, request_url, payload_template=None, actor_id=None, actor_task_id=None, actor_run_id=None, ignore_ssl_errors=None, do_not_retry=None, idempotency_key=None, is_ad_hoc=None)`

Create a new webhook.

You have to specify exactly one out of actor_id, actor_task_id or actor_run_id.

[https://docs.apify.com/api/v2#/reference/webhooks/webhook-collection/create-webhook](https://docs.apify.com/api/v2#/reference/webhooks/webhook-collection/create-webhook)

* **Parameters**

  * **event_types** ([`list of WebhookEventType`](#webhookeventtype)) – List of event types that should trigger the webhook. At least one is required.

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

### [](#schedulecollectionclientasync) ScheduleCollectionClientAsync

Async sub-client for manipulating schedules.

* [async list()](#schedulecollectionclientasync-list)
* [async create()](#schedulecollectionclientasync-create)

***

#### [](#schedulecollectionclientasync-list) `async ScheduleCollectionClientAsync.list(*, limit=None, offset=None, desc=None)`

List the available schedules.

[https://docs.apify.com/api/v2#/reference/schedules/schedules-collection/get-list-of-schedules](https://docs.apify.com/api/v2#/reference/schedules/schedules-collection/get-list-of-schedules)

* **Parameters**

  * **limit** (`int`, *optional*) – How many schedules to retrieve

  * **offset** (`int`, *optional*) – What schedules to include as first when retrieving the list

  * **desc** (`bool`, *optional*) – Whether to sort the schedules in descending order based on their modification date

* **Returns**

  The list of available schedules matching the specified filters.

* **Return type**

  [`ListPage`](#listpage)

***

#### [](#schedulecollectionclientasync-create) `async ScheduleCollectionClientAsync.create(*, cron_expression, is_enabled, is_exclusive, name=None, actions=None, description=None, timezone=None, title=None)`

Create a new schedule.

[https://docs.apify.com/api/v2#/reference/schedules/schedules-collection/create-schedule](https://docs.apify.com/api/v2#/reference/schedules/schedules-collection/create-schedule)

* **Parameters**

  * **cron_expression** (`str`) – The cron expression used by this schedule

  * **is_enabled** (`bool`) – True if the schedule should be enabled

  * **is_exclusive** (`bool`) – When set to true, don’t start actor or actor task if it’s still running from the previous schedule.

  * **name** (`str`, *optional*) – The name of the schedule to create.

  * **actions** (`list of dict`, *optional*) – Actors or tasks that should be run on this schedule. See the API documentation for exact structure.

  * **description** (`str`, *optional*) – Description of this schedule

  * **timezone** (`str`, *optional*) – Timezone in which your cron expression runs
  (TZ database name from [https://en.wikipedia.org/wiki/List_of_tz_database_time_zones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones))

* **Returns**

  The created schedule.

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

### [](#taskclientasync) TaskClientAsync

Async sub-client for manipulating a single task.

* [async get()](#taskclientasync-get)
* [async update()](#taskclientasync-update)
* [async delete()](#taskclientasync-delete)
* [async start()](#taskclientasync-start)
* [async call()](#taskclientasync-call)
* [async get\_input()](#taskclientasync-get\_input)
* [async update\_input()](#taskclientasync-update\_input)
* [runs()](#taskclientasync-runs)
* [last\_run()](#taskclientasync-last\_run)
* [webhooks()](#taskclientasync-webhooks)

***

#### [](#taskclientasync-get) `async TaskClientAsync.get()`

Retrieve the task.

[https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/get-task](https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/get-task)

* **Returns**

  The retrieved task

* **Return type**

  `dict`, optional

***

#### [](#taskclientasync-update) `async TaskClientAsync.update(*, name=None, task_input=None, build=None, memory_mbytes=None, timeout_secs=None, title=None)`

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

  * **title** (`str`, *optional*) – A human-friendly equivalent of the name

* **Returns**

  The updated task

* **Return type**

  `dict`

***

#### [](#taskclientasync-delete) `async TaskClientAsync.delete()`

Delete the task.

[https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/delete-task](https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/delete-task)

* **Return type**

  `None`

***

#### [](#taskclientasync-start) `async TaskClientAsync.start(*, task_input=None, build=None, memory_mbytes=None, timeout_secs=None, wait_for_finish=None, webhooks=None)`

Start the task and immediately return the Run object.

[https://docs.apify.com/api/v2#/reference/actor-tasks/run-collection/run-task](https://docs.apify.com/api/v2#/reference/actor-tasks/run-collection/run-task)

* **Parameters**

  * **task_input** (`dict`, *optional*) – Task input dictionary

  * **build** (`str`, *optional*) – Specifies the actor build to run. It can be either a build tag or build number.
  By default, the run uses the build specified in the task settings (typically latest).

  * **memory_mbytes** (`int`, *optional*) – Memory limit for the run, in megabytes.
  By default, the run uses a memory limit specified in the task settings.

  * **timeout_secs** (`int`, *optional*) – Optional timeout for the run, in seconds. By default, the run uses timeout specified in the task settings.

  * **wait_for_finish** (`int`, *optional*) – The maximum number of seconds the server waits for the run to finish.
  By default, it is 0, the maximum value is 300.

  * **webhooks** (`list of dict`, *optional*) – Optional ad-hoc webhooks ([https://docs.apify.com/webhooks/ad-hoc-webhooks](https://docs.apify.com/webhooks/ad-hoc-webhooks))
  associated with the actor run which can be used to receive a notification,
  e.g. when the actor finished or failed.
  If you already have a webhook set up for the actor or task, you do not have to add it again here.
  Each webhook is represented by a dictionary containing these items:
    * `event_types`: list of [`WebhookEventType`](#webhookeventtype) values which trigger the webhook
    * `request_url`: URL to which to send the webhook HTTP request
    * `payload_template` (optional): Optional template for the request payload

* **Returns**

  The run object

* **Return type**

  `dict`

***

#### [](#taskclientasync-call) `async TaskClientAsync.call(*, task_input=None, build=None, memory_mbytes=None, timeout_secs=None, webhooks=None, wait_secs=None)`

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

  * **webhooks** (`list`, *optional*) – Specifies optional webhooks associated with the actor run, which can be used to receive a notification
  e.g. when the actor finished or failed. Note: if you already have a webhook set up for the actor or task,
  you do not have to add it again here.

  * **wait_secs** (`int`, *optional*) – The maximum number of seconds the server waits for the task run to finish. If not provided, waits indefinitely.

* **Returns**

  The run object

* **Return type**

  `dict`

***

#### [](#taskclientasync-get_input) `async TaskClientAsync.get_input()`

Retrieve the default input for this task.

[https://docs.apify.com/api/v2#/reference/actor-tasks/task-input-object/get-task-input](https://docs.apify.com/api/v2#/reference/actor-tasks/task-input-object/get-task-input)

* **Returns**

  Retrieved task input

* **Return type**

  `dict`, optional

***

#### [](#taskclientasync-update_input) `async TaskClientAsync.update_input(*, task_input)`

Update the default input for this task.

[https://docs.apify.com/api/v2#/reference/actor-tasks/task-input-object/update-task-input](https://docs.apify.com/api/v2#/reference/actor-tasks/task-input-object/update-task-input)

* **Return type**

  `Dict`

* **Returns**

  dict, Retrieved task input

***

#### [](#taskclientasync-runs) `TaskClientAsync.runs()`

Retrieve a client for the runs of this task.

* **Return type**

  `RunCollectionClientAsync`

***

#### [](#taskclientasync-last_run) `TaskClientAsync.last_run(*, status=None, origin=None)`

Retrieve the client for the last run of this task.

Last run is retrieved based on the start time of the runs.

* **Parameters**

  * **status** ([`ActorJobStatus`](#actorjobstatus), *optional*) – Consider only runs with this status.

  * **origin** (`MetaOrigin`, *optional*) – Consider only runs started with this origin.

* **Returns**

  The resource client for the last run of this task.

* **Return type**

  `RunClientAsync`

***

#### [](#taskclientasync-webhooks) `TaskClientAsync.webhooks()`

Retrieve a client for webhooks associated with this task.

* **Return type**

  `WebhookCollectionClientAsync`

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

  [`ListPage`](#listpage)

***

### [](#taskcollectionclientasync) TaskCollectionClientAsync

Async sub-client for manipulating tasks.

* [async list()](#taskcollectionclientasync-list)
* [async create()](#taskcollectionclientasync-create)

***

#### [](#taskcollectionclientasync-list) `async TaskCollectionClientAsync.list(*, limit=None, offset=None, desc=None)`

List the available tasks.

[https://docs.apify.com/api/v2#/reference/actor-tasks/task-collection/get-list-of-tasks](https://docs.apify.com/api/v2#/reference/actor-tasks/task-collection/get-list-of-tasks)

* **Parameters**

  * **limit** (`int`, *optional*) – How many tasks to list

  * **offset** (`int`, *optional*) – What task to include as first when retrieving the list

  * **desc** (`bool`, *optional*) – Whether to sort the tasks in descending order based on their creation date

* **Returns**

  The list of available tasks matching the specified filters.

* **Return type**

  [`ListPage`](#listpage)

***

#### [](#taskcollectionclientasync-create) `async TaskCollectionClientAsync.create(*, actor_id, name, build=None, timeout_secs=None, memory_mbytes=None, task_input=None, title=None)`

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

  * **title** (`str`, *optional*) – A human-friendly equivalent of the name

* **Returns**

  The created task.

* **Return type**

  `dict`

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
* [runs()](#taskclient-runs)
* [last\_run()](#taskclient-last\_run)
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

#### [](#taskclient-update) `TaskClient.update(*, name=None, task_input=None, build=None, memory_mbytes=None, timeout_secs=None, title=None)`

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

  * **title** (`str`, *optional*) – A human-friendly equivalent of the name

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

  * **wait_for_finish** (`int`, *optional*) – The maximum number of seconds the server waits for the run to finish.
  By default, it is 0, the maximum value is 300.

  * **webhooks** (`list of dict`, *optional*) – Optional ad-hoc webhooks ([https://docs.apify.com/webhooks/ad-hoc-webhooks](https://docs.apify.com/webhooks/ad-hoc-webhooks))
  associated with the actor run which can be used to receive a notification,
  e.g. when the actor finished or failed.
  If you already have a webhook set up for the actor or task, you do not have to add it again here.
  Each webhook is represented by a dictionary containing these items:
    * `event_types`: list of [`WebhookEventType`](#webhookeventtype) values which trigger the webhook
    * `request_url`: URL to which to send the webhook HTTP request
    * `payload_template` (optional): Optional template for the request payload

* **Returns**

  The run object

* **Return type**

  `dict`

***

#### [](#taskclient-call) `TaskClient.call(*, task_input=None, build=None, memory_mbytes=None, timeout_secs=None, webhooks=None, wait_secs=None)`

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

  * **webhooks** (`list`, *optional*) – Specifies optional webhooks associated with the actor run, which can be used to receive a notification
  e.g. when the actor finished or failed. Note: if you already have a webhook set up for the actor or task,
  you do not have to add it again here.

  * **wait_secs** (`int`, *optional*) – The maximum number of seconds the server waits for the task run to finish. If not provided, waits indefinitely.

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

#### [](#taskclient-runs) `TaskClient.runs()`

Retrieve a client for the runs of this task.

* **Return type**

  [`RunCollectionClient`](#runcollectionclient)

***

#### [](#taskclient-last_run) `TaskClient.last_run(*, status=None, origin=None)`

Retrieve the client for the last run of this task.

Last run is retrieved based on the start time of the runs.

* **Parameters**

  * **status** ([`ActorJobStatus`](#actorjobstatus), *optional*) – Consider only runs with this status.

  * **origin** (`MetaOrigin`, *optional*) – Consider only runs started with this origin.

* **Returns**

  The resource client for the last run of this task.

* **Return type**

  [`RunClient`](#runclient)

***

#### [](#taskclient-webhooks) `TaskClient.webhooks()`

Retrieve a client for webhooks associated with this task.

* **Return type**

  [`WebhookCollectionClient`](#webhookcollectionclient)

***

### [](#userclientasync) UserClientAsync

Async sub-client for querying user data.

* [async get()](#userclientasync-get)

***

#### [](#userclientasync-get) `async UserClientAsync.get()`

Return information about user account.

You receive all or only public info based on your token permissions.

[https://docs.apify.com/api/v2#/reference/users](https://docs.apify.com/api/v2#/reference/users)

* **Returns**

  The retrieved user data, or `None` if the user does not exist.

* **Return type**

  `dict`, optional

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

  * **desc** (`bool`, *optional*) – Whether to sort the tasks in descending order based on their creation date

* **Returns**

  The list of available tasks matching the specified filters.

* **Return type**

  [`ListPage`](#listpage)

***

#### [](#taskcollectionclient-create) `TaskCollectionClient.create(*, actor_id, name, build=None, timeout_secs=None, memory_mbytes=None, task_input=None, title=None)`

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

  * **title** (`str`, *optional*) – A human-friendly equivalent of the name

* **Returns**

  The created task.

* **Return type**

  `dict`

***

### [](#webhookclientasync) WebhookClientAsync

Async sub-client for manipulating a single webhook.

* [async get()](#webhookclientasync-get)
* [async update()](#webhookclientasync-update)
* [async delete()](#webhookclientasync-delete)
* [async test()](#webhookclientasync-test)
* [dispatches()](#webhookclientasync-dispatches)

***

#### [](#webhookclientasync-get) `async WebhookClientAsync.get()`

Retrieve the webhook.

[https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/get-webhook](https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/get-webhook)

* **Returns**

  The retrieved webhook, or `None` if it does not exist

* **Return type**

  `dict`, optional

***

#### [](#webhookclientasync-update) `async WebhookClientAsync.update(*, event_types=None, request_url=None, payload_template=None, actor_id=None, actor_task_id=None, actor_run_id=None, ignore_ssl_errors=None, do_not_retry=None, is_ad_hoc=None)`

Update the webhook.

[https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/update-webhook](https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/update-webhook)

* **Parameters**

  * **event_types** ([`list of WebhookEventType`](#webhookeventtype), *optional*) – List of event types that should trigger the webhook. At least one is required.

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

#### [](#webhookclientasync-delete) `async WebhookClientAsync.delete()`

Delete the webhook.

[https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/delete-webhook](https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/delete-webhook)

* **Return type**

  `None`

***

#### [](#webhookclientasync-test) `async WebhookClientAsync.test()`

Test a webhook.

Creates a webhook dispatch with a dummy payload.

[https://docs.apify.com/api/v2#/reference/webhooks/webhook-test/test-webhook](https://docs.apify.com/api/v2#/reference/webhooks/webhook-test/test-webhook)

* **Returns**

  The webhook dispatch created by the test

* **Return type**

  `dict`, optional

***

#### [](#webhookclientasync-dispatches) `WebhookClientAsync.dispatches()`

Get dispatches of the webhook.

[https://docs.apify.com/api/v2#/reference/webhooks/dispatches-collection/get-collection](https://docs.apify.com/api/v2#/reference/webhooks/dispatches-collection/get-collection)

* **Returns**

  A client allowing access to dispatches of this webhook using its list method

* **Return type**

  `WebhookDispatchCollectionClientAsync`

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

#### [](#scheduleclient-update) `ScheduleClient.update(*, cron_expression=None, is_enabled=None, is_exclusive=None, name=None, actions=None, description=None, timezone=None, title=None)`

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

  * **title** (`str`, *optional*) – A human-friendly equivalent of the name

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

### [](#webhookcollectionclientasync) WebhookCollectionClientAsync

Async sub-client for manipulating webhooks.

* [async list()](#webhookcollectionclientasync-list)
* [async create()](#webhookcollectionclientasync-create)

***

#### [](#webhookcollectionclientasync-list) `async WebhookCollectionClientAsync.list(*, limit=None, offset=None, desc=None)`

List the available webhooks.

[https://docs.apify.com/api/v2#/reference/webhooks/webhook-collection/get-list-of-webhooks](https://docs.apify.com/api/v2#/reference/webhooks/webhook-collection/get-list-of-webhooks)

* **Parameters**

  * **limit** (`int`, *optional*) – How many webhooks to retrieve

  * **offset** (`int`, *optional*) – What webhook to include as first when retrieving the list

  * **desc** (`bool`, *optional*) – Whether to sort the webhooks in descending order based on their date of creation

* **Returns**

  The list of available webhooks matching the specified filters.

* **Return type**

  [`ListPage`](#listpage)

***

#### [](#webhookcollectionclientasync-create) `async WebhookCollectionClientAsync.create(*, event_types, request_url, payload_template=None, actor_id=None, actor_task_id=None, actor_run_id=None, ignore_ssl_errors=None, do_not_retry=None, idempotency_key=None, is_ad_hoc=None)`

Create a new webhook.

You have to specify exactly one out of actor_id, actor_task_id or actor_run_id.

[https://docs.apify.com/api/v2#/reference/webhooks/webhook-collection/create-webhook](https://docs.apify.com/api/v2#/reference/webhooks/webhook-collection/create-webhook)

* **Parameters**

  * **event_types** ([`list of WebhookEventType`](#webhookeventtype)) – List of event types that should trigger the webhook. At least one is required.

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

* **Returns**

  The list of available schedules matching the specified filters.

* **Return type**

  [`ListPage`](#listpage)

***

#### [](#schedulecollectionclient-create) `ScheduleCollectionClient.create(*, cron_expression, is_enabled, is_exclusive, name=None, actions=None, description=None, timezone=None, title=None)`

Create a new schedule.

[https://docs.apify.com/api/v2#/reference/schedules/schedules-collection/create-schedule](https://docs.apify.com/api/v2#/reference/schedules/schedules-collection/create-schedule)

* **Parameters**

  * **cron_expression** (`str`) – The cron expression used by this schedule

  * **is_enabled** (`bool`) – True if the schedule should be enabled

  * **is_exclusive** (`bool`) – When set to true, don’t start actor or actor task if it’s still running from the previous schedule.

  * **name** (`str`, *optional*) – The name of the schedule to create.

  * **actions** (`list of dict`, *optional*) – Actors or tasks that should be run on this schedule. See the API documentation for exact structure.

  * **description** (`str`, *optional*) – Description of this schedule

  * **timezone** (`str`, *optional*) – Timezone in which your cron expression runs
  (TZ database name from [https://en.wikipedia.org/wiki/List_of_tz_database_time_zones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones))

* **Returns**

  The created schedule.

* **Return type**

  `dict`

***

### [](#webhookdispatchclientasync) WebhookDispatchClientAsync

Async sub-client for querying information about a webhook dispatch.

* [async get()](#webhookdispatchclientasync-get)

***

#### [](#webhookdispatchclientasync-get) `async WebhookDispatchClientAsync.get()`

Retrieve the webhook dispatch.

[https://docs.apify.com/api/v2#/reference/webhook-dispatches/webhook-dispatch-object/get-webhook-dispatch](https://docs.apify.com/api/v2#/reference/webhook-dispatches/webhook-dispatch-object/get-webhook-dispatch)

* **Returns**

  The retrieved webhook dispatch, or `None` if it does not exist

* **Return type**

  `dict`, optional

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

### [](#webhookdispatchcollectionclientasync) WebhookDispatchCollectionClientAsync

Async sub-client for listing webhook dispatches.

* [async list()](#webhookdispatchcollectionclientasync-list)

***

#### [](#webhookdispatchcollectionclientasync-list) `async WebhookDispatchCollectionClientAsync.list(*, limit=None, offset=None, desc=None)`

List all webhook dispatches of a user.

[https://docs.apify.com/api/v2#/reference/webhook-dispatches/webhook-dispatches-collection/get-list-of-webhook-dispatches](https://docs.apify.com/api/v2#/reference/webhook-dispatches/webhook-dispatches-collection/get-list-of-webhook-dispatches)

* **Parameters**

  * **limit** (`int`, *optional*) – How many webhook dispatches to retrieve

  * **offset** (`int`, *optional*) – What webhook dispatch to include as first when retrieving the list

  * **desc** (`bool`, *optional*) – Whether to sort the webhook dispatches in descending order based on the date of their creation

* **Returns**

  The retrieved webhook dispatches of a user

* **Return type**

  [`ListPage`](#listpage)

***

### [](#listpage) ListPage

A single page of items returned from a list() method.

#### Instance attributes

Name | Type | Description
---- | ---- | -----------
`items` | `list` | List of returned objects on this page
`offset` | `int` | The limit on the number of returned objects offset specified in the API call
`limit` | `int` | The offset of the first object specified in the API call
`count` | `int` | Count of the returned objects on this page
`total` | `int` | Total number of objects matching the API call criteria
`desc` | `bool` | Whether the listing is descending or not

***

### [](#actorjobstatus) ActorJobStatus

Available statuses for actor jobs (runs or builds).

* [READY](#actorjobstatus-ready)
* [RUNNING](#actorjobstatus-running)
* [SUCCEEDED](#actorjobstatus-succeeded)
* [FAILED](#actorjobstatus-failed)
* [TIMING\_OUT](#actorjobstatus-timing\_out)
* [TIMED\_OUT](#actorjobstatus-timed\_out)
* [ABORTING](#actorjobstatus-aborting)
* [ABORTED](#actorjobstatus-aborted)

***

#### [](#actorjobstatus-ready) `ActorJobStatus.READY`

Actor job initialized but not started yet

***

#### [](#actorjobstatus-running) `ActorJobStatus.RUNNING`

Actor job in progress

***

#### [](#actorjobstatus-succeeded) `ActorJobStatus.SUCCEEDED`

Actor job finished successfully

***

#### [](#actorjobstatus-failed) `ActorJobStatus.FAILED`

Actor job or build failed

***

#### [](#actorjobstatus-timing_out) `ActorJobStatus.TIMING_OUT`

Actor job currently timing out

***

#### [](#actorjobstatus-timed_out) `ActorJobStatus.TIMED_OUT`

Actor job timed out

***

#### [](#actorjobstatus-aborting) `ActorJobStatus.ABORTING`

Actor job currently being aborted by user

***

#### [](#actorjobstatus-aborted) `ActorJobStatus.ABORTED`

Actor job aborted by user

***

### [](#actorsourcetype) ActorSourceType

Available source types for actors.

* [SOURCE\_FILES](#actorsourcetype-source\_files)
* [GIT\_REPO](#actorsourcetype-git\_repo)
* [TARBALL](#actorsourcetype-tarball)
* [GITHUB\_GIST](#actorsourcetype-github\_gist)

***

#### [](#actorsourcetype-source_files) `ActorSourceType.SOURCE_FILES`

Actor source code is comprised of multiple files

***

#### [](#actorsourcetype-git_repo) `ActorSourceType.GIT_REPO`

Actor source code is cloned from a Git repository

***

#### [](#actorsourcetype-tarball) `ActorSourceType.TARBALL`

Actor source code is downloaded using a tarball or Zip file

***

#### [](#actorsourcetype-github_gist) `ActorSourceType.GITHUB_GIST`

Actor source code is taken from a GitHub Gist

***

### [](#webhookeventtype) WebhookEventType

Events that can trigger a webhook.

* [ACTOR\_RUN\_CREATED](#webhookeventtype-actor\_run\_created)
* [ACTOR\_RUN\_SUCCEEDED](#webhookeventtype-actor\_run\_succeeded)
* [ACTOR\_RUN\_FAILED](#webhookeventtype-actor\_run\_failed)
* [ACTOR\_RUN\_TIMED\_OUT](#webhookeventtype-actor\_run\_timed\_out)
* [ACTOR\_RUN\_ABORTED](#webhookeventtype-actor\_run\_aborted)
* [ACTOR\_RUN\_RESURRECTED](#webhookeventtype-actor\_run\_resurrected)
* [ACTOR\_BUILD\_CREATED](#webhookeventtype-actor\_build\_created)
* [ACTOR\_BUILD\_SUCCEEDED](#webhookeventtype-actor\_build\_succeeded)
* [ACTOR\_BUILD\_FAILED](#webhookeventtype-actor\_build\_failed)
* [ACTOR\_BUILD\_TIMED\_OUT](#webhookeventtype-actor\_build\_timed\_out)
* [ACTOR\_BUILD\_ABORTED](#webhookeventtype-actor\_build\_aborted)

***

#### [](#webhookeventtype-actor_run_created) `WebhookEventType.ACTOR_RUN_CREATED`

The actor run was created

***

#### [](#webhookeventtype-actor_run_succeeded) `WebhookEventType.ACTOR_RUN_SUCCEEDED`

The actor run has succeeded

***

#### [](#webhookeventtype-actor_run_failed) `WebhookEventType.ACTOR_RUN_FAILED`

The actor run has failed

***

#### [](#webhookeventtype-actor_run_timed_out) `WebhookEventType.ACTOR_RUN_TIMED_OUT`

The actor run has timed out

***

#### [](#webhookeventtype-actor_run_aborted) `WebhookEventType.ACTOR_RUN_ABORTED`

The actor run was aborted

***

#### [](#webhookeventtype-actor_run_resurrected) `WebhookEventType.ACTOR_RUN_RESURRECTED`

The actor run was resurrected

***

#### [](#webhookeventtype-actor_build_created) `WebhookEventType.ACTOR_BUILD_CREATED`

The actor build was created

***

#### [](#webhookeventtype-actor_build_succeeded) `WebhookEventType.ACTOR_BUILD_SUCCEEDED`

The actor build has succeeded

***

#### [](#webhookeventtype-actor_build_failed) `WebhookEventType.ACTOR_BUILD_FAILED`

The actor build has failed

***

#### [](#webhookeventtype-actor_build_timed_out) `WebhookEventType.ACTOR_BUILD_TIMED_OUT`

The actor build has timed out

***

#### [](#webhookeventtype-actor_build_aborted) `WebhookEventType.ACTOR_BUILD_ABORTED`

The actor build was aborted

***

### [](#metaorigin) MetaOrigin

Possible origins for actor runs, i.e. how were the jobs started.

* [DEVELOPMENT](#metaorigin-development)
* [WEB](#metaorigin-web)
* [API](#metaorigin-api)
* [SCHEDULER](#metaorigin-scheduler)
* [TEST](#metaorigin-test)
* [WEBHOOK](#metaorigin-webhook)
* [ACTOR](#metaorigin-actor)

***

#### [](#metaorigin-development) `MetaOrigin.DEVELOPMENT`

Job started from Developer console in Source section of actor

***

#### [](#metaorigin-web) `MetaOrigin.WEB`

Job started from other place on the website (either console or task detail page)

***

#### [](#metaorigin-api) `MetaOrigin.API`

Job started through API

***

#### [](#metaorigin-scheduler) `MetaOrigin.SCHEDULER`

Job started through Scheduler

***

#### [](#metaorigin-test) `MetaOrigin.TEST`

Job started through test actor page

***

#### [](#metaorigin-webhook) `MetaOrigin.WEBHOOK`

Job started by the webhook

***

#### [](#metaorigin-actor) `MetaOrigin.ACTOR`

Job started by another actor run

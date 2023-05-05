---
title: Usage concepts
---

The [`ApifyClient`](../reference/class/ApifyClient) interface follows a generic pattern that is applicable to all of its components.
By calling individual methods of [`ApifyClient`](../reference/class/ApifyClient),
specific clients which target individual API resources are created.
There are two types of those clients.
A client for management of a single resource and a client for a collection of resources.

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

Most methods named `list` or `list_something` return a [`ListPage`](../reference/class/ListPage) object,
containing properties `items`, `total`, `offset`, `count` and `limit`.
There are some exceptions though, like `list_keys` or `list_head` which paginate differently.
The results you're looking for are always stored under `items` and you can use the `limit`
property to get only a subset of results. Other properties can be available depending on the method.

### Streaming resources

Some resources (dataset items, key-value store records and logs)
support streaming the resource from the Apify API in parts,
without having to download the whole (potentially huge) resource to memory before processing it.

The methods to stream these resources are
[`DatasetClient.stream_items()`](../reference/class/DatasetClient#stream_items),
[`KeyValueStoreClient.stream_record()`](../reference/class/KeyValueStoreClient#stream_record),
and [`LogClient.stream()`](../reference/class/LogClient#stream).

Instead of the parsed resource, they return a raw, context-managed
[`httpx.Response`](https://www.python-httpx.org/quickstart/#streaming-responses) object,
which has to be consumed using the `with` keyword,
and automatically gets closed once you exit the `with` block, preventing memory leaks and unclosed connections.

For example, to consume an actor run log in a streaming fashion, you can use this snippet:

```python
with apify_client.run('MY-RUN-ID').log().stream() as log_stream:
    if log_stream:
        for line in log_stream.iter_lines():
            print(line)
```

### Asynchronous usage

To use the asynchronous [`ApifyClientAsync`](../reference/class/ApifyClientAsync) in your async code,
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
                print(line)

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

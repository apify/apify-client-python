---
sidebar_label: 'Getting started'
title: 'Getting started'
---

# Apify API client for Python

`apify-client` is the official library to access the [Apify REST API](https://docs.apify.com/api/v2) from your Python applications. It provides useful features like automatic retries and convenience functions that improve the experience of using the Apify API. All requests and responses (including errors) are encoded in JSON format with UTF-8 encoding.

## Pre-requisites

`apify-client` requires Python version 3.8 or higher. Python is available for download on the [official website](https://www.python.org/). Check for your current Python version by running:

```bash
python -V
```

## Installation

You can install the client from its [PyPI listing](https://pypi.org/project/apify-client/).
To do that, run:

```bash
pip install apify-client
```

## Authentication and initialization

To use the client, you need an [API token](https://docs.apify.com/platform/integrations/api#api-token). You can find your token under [Integrations](https://console.apify.com/account/integrations) tab in Apify Console. Copy the token and initialize the client by providing the token (`MY-APIFY-TOKEN`) as a parameter to the `ApifyClient` constructor.

```python
# import Apify client
from apify_client import ApifyClient

# Client initialization with the API token
apify_client = ApifyClient('MY-APIFY-TOKEN')
```

:::warning Secure access

The API token is used to authorize your requests to the Apify API. You can be charged for the usage of the underlying services, so do not share your API token with untrusted parties or expose it on the client side of your applications.

:::

## Quick start

One of the most common use cases is starting [Actors](https://docs.apify.com/platform/actors) (serverless programs running in the [Apify cloud](https://docs.apify.com/platform)) and getting results from their [datasets](https://docs.apify.com/platform/storage/dataset) (storage) after they finish the job (usually scraping, automation processes or data processing).

```python
from apify_client import ApifyClient

apify_client = ApifyClient('MY-APIFY-TOKEN')

# Start an Actor and waits for it to finish
actor_call = apify_client.actor('username/actor-name').call()

# Get a Actor's dataset
dataset_client = apify_client.dataset(actor_call['defaultDatasetId'])

# Lists items from the Actor's dataset
dataset_items = dataset_client.list_items().items
```

### Running Actors

To start an Actor, you can use the [ActorClient](/reference/class/ActorClient) (`client.actor()`) and pass the Actor's ID (e.g. `john-doe/my-cool-actor`) to define which Actor you want to run. The Actor's ID is a combination of the username and the Actor owner’s username. You can run both your own Actors and [Actors from Apify Store](https://docs.apify.com/platform/actors/running/actors-in-store).

#### Passing input to the Actor

To define the Actor's input, you can pass a run input to the [`call()`](/reference/class/ActorClient#call) method. The input can be any JSON object that the Actor expects (respects the Actor's [input schema](https://docs.apify.com/platform/actors/development/actor-definition/input-schema)).The input is used to pass configuration to the Actor, such as URLs to scrape, search terms, or any other data.

```python
from apify_client import ApifyClient

apify_client = ApifyClient('MY-APIFY-TOKEN')

# Define the input for the Actor
actor_input = {
    'some': 'input',
}

# Start an Actor and waits for it to finish
actor_call = apify_client.actor('username/actor-name').call(run_input=actor_input)
```

### Getting results from the dataset

To get the results from the dataset, you can use the [DatasetClient](/reference/class/DatasetClient) (`client.dataset()`) and [`list_items()`](/reference/class/DatasetClient#list_items) method. You need to pass the dataset ID to define which dataset you want to access. You can get the dataset ID from the Actor's run dictionary (represented by `defaultDatasetId`).

```python
from apify_client import ApifyClient

apify_client = ApifyClient('MY-APIFY-TOKEN')

# Get dataset
dataset_client = apify_client.dataset('dataset-id')

# Lists items from the Actor's dataset
dataset_items = dataset_client.list_items().items
```

:::note Dataset access

Running an Actor might take time, depending on the Actor's complexity and the amount of data it processes. If you want only to get data and have an immediate response you should access the existing dataset of the finished [Actor run](https://docs.apify.com/platform/actors/running/runs-and-builds#runs).

:::

## Usage concepts

The `ApifyClient` interface follows a generic pattern that applies to all of its components. By calling individual methods of `ApifyClient`, specific clients that target individual API resources are created. There are two types of those clients:

- [`actorClient`](/reference/class/ActorClient): a client for the management of a single resource
- [`actorCollectionClient`](/reference/class/ActorCollectionClient): a client for the collection of resources

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

:::note Resource identification

The resource ID can be either the `id` of the said resource, or a combination of your `username/resource-name`.

:::

```python
# Resource clients accept an ID of the resource
actor_client = apify_client.actor('username/actor-name')

# Fetch the 'username/actor-name' object from the API
my_actor = actor_client.get()

# Start the run of 'username/actor-name' and return the Run object
my_actor_run = actor_client.start()
```

### Nested clients

Sometimes clients return other clients. That's to simplify working with nested collections, such as runs of a given Actor.

```python
from apify_client import ApifyClient

apify_client = ApifyClient('MY-APIFY-TOKEN')

actor_client = apify_client.actor('username/actor-name')
runs_client = actor_client.runs()

# List the last 10 runs of the Actor
actor_runs = runs_client.list(limit=10, desc=True).items

# Select the last run of the Actor that finished with a SUCCEEDED status
last_succeeded_run_client = actor_client.last_run(status='SUCCEEDED')

# Get dataset
actor_run_dataset_client = last_succeeded_run_client.dataset()

# Fetch items from the run's dataset
dataset_items = actor_run_dataset_client.list_items().items
```

The quick access to `dataset` and other storage directly from the run client can be used with the [`last_run()`](/reference/class/ActorClient#last_run) method.

## Features

Based on the endpoint, the client automatically extracts the relevant data
and returns it in the expected format.
Date strings are automatically converted to `datetime.datetime` objects.
For exceptions, we throw an [`ApifyApiError`](/reference/class/ApifyApiError),
which wraps the plain JSON errors returned by API and enriches them with other context for easier debugging.

```python
from apify_client import ApifyClient

apify_client = ApifyClient('MY-APIFY-TOKEN')

try:
    # Try to list items from non-existing dataset
    dataset_client = apify_client.dataset('not-existing-dataset-id')
    dataset_items = dataset_client.list_items().items
except Exception as ApifyApiError:
    # The exception is an instance of ApifyApiError
    print(ApifyApiError)
```

### Retries with exponential backoff

Network communication sometimes fails.
The client will automatically retry requests that failed due to a network error,
an internal error of the Apify API (HTTP 500+) or rate limit error (HTTP 429).
By default, it will retry up to 8 times.
First retry will be attempted after ~500ms, second after ~1000ms and so on.
You can configure those parameters using the `max_retries` and `min_delay_between_retries_millis` options
of the [`ApifyClient`](/reference/class/ApifyClient) constructor.

```python
from apify_client import ApifyClient

apify_client = ApifyClient(
    token='MY-APIFY-TOKEN',
    max_retries=8,
    min_delay_between_retries_millis=500, # 0.5s
    timeout_secs=360, # 6 mins
)
```

### Support for asynchronous usage

The package offers an asynchronous version of the client,
[`ApifyClientAsync`](/reference/class/ApifyClientAsync),
which allows you to work with the Apify API in an asynchronous way, using the standard `async`/`await` syntax [offered by Python](https://docs.python.org/3/library/asyncio-task.html).

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

### Convenience functions and options

Some actions can't be performed by the API itself, such as indefinite waiting for an actor run to finish (because of network timeouts).
The client provides convenient [`call()`](/reference/class/ActorClient#call)
and [`wait_for_finish()`](/reference/class/ActorClient#wait_for_finish) methods that do that.

[Key-value store](https://docs.apify.com/platform/storage/key-value-store) records can be retrieved as objects, buffers or streams via the respective options,
dataset items can be fetched as individual objects or serialized data, or iterated asynchronously.

```python
from apify_client import ApifyClient

apify_client = ApifyClient('MY-APIFY-TOKEN')

# Start an Actor and waits for it to finish
finished_actor_run = apify_client.actor('username/actor-name').call()

# Starts an Actor and waits maximum 60s (1 minute) for the finish 
actor_run = apify_client.actor('username/actor-name').start(wait_for_finish=60)
```

### Pagination

Most methods named `list` or `list_something` return a [`ListPage`](/reference/class/ListPage) object,
containing properties `items`, `total`, `offset`, `count` and `limit`.
There are some exceptions though, like `list_keys` or `list_head` which paginate differently.
The results you're looking for are always stored under `items` and you can use the `limit`
property to get only a subset of results. Other properties can be available depending on the method.

```python
from apify_client import ApifyClient

apify_client = ApifyClient('MY-APIFY-TOKEN')

# Resource clients accept an ID of the resource
dataset_client = apify_client.dataset('dataset-id')

# Number of items per page
limit = 1000
# Initial offset
offset = 0
# List to store all items
all_items = []

while True:
    response = dataset_client.list_items(limit=limit, offset=offset)
    items = response.items
    total = response.total
    
    print(f'Fetched {len(items)} items')

    # Merge new items with other already loaded items
    all_items.extend(items)

    # If there are no more items to fetch, exit the loading
    if offset + limit >= total:
        break

    offset += limit

print(f'Overall fetched {len(all_items)} items')
```

### Streaming resources

Some resources (dataset items, key-value store records and logs)
support streaming the resource from the Apify API in parts,
without having to download the whole (potentially huge) resource to memory before processing it.

The methods to stream these resources are
[`DatasetClient.stream_items()`](/reference/class/DatasetClient#stream_items),
[`KeyValueStoreClient.stream_record()`](/reference/class/KeyValueStoreClient#stream_record),
and [`LogClient.stream()`](/reference/class/LogClient#stream).

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

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

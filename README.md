# Apify API client for Python

The Apify API Client for Python is the official library to access the [Apify API](https://docs.apify.com/api/v2) from your Python applications.
It provides useful features like automatic retries and convenience functions to improve your experience with the Apify API.

If you want to develop Apify Actors in Python,
check out the [Apify SDK for Python](https://docs.apify.com/sdk/python) instead.

## Installation

Requires Python 3.8+

You can install the package from its [PyPI listing](https://pypi.org/project/apify-client).
To do that, simply run `pip install apify-client` in your terminal.

## Usage

For usage instructions, check the documentation on [Apify Docs](https://docs.apify.com/api/client/python/).

## Quick Start

```python
from apify_client import ApifyClient

apify_client = ApifyClient('MY-APIFY-TOKEN')

# Start an Actor and wait for it to finish
actor_call = apify_client.actor('john-doe/my-cool-actor').call()

# Fetch results from the Actor's default dataset
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

Starting with version 1.0.0, the package offers an asynchronous version of the client, [`ApifyClientAsync`](https://docs.apify.com/api/client/python),
which allows you to work with the Apify API in an asynchronous way, using the standard `async`/`await` syntax.

### Convenience functions and options

Some actions can't be performed by the API itself, such as indefinite waiting for an Actor run to finish
(because of network timeouts). The client provides convenient `call()` and `wait_for_finish()` functions that do that.
Key-value store records can be retrieved as objects, buffers or streams via the respective options, dataset items
can be fetched as individual objects or serialized data and we plan to add better stream support and async iterators.

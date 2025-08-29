<h1 align=center>Apify API client for Python</h1>

<p align=center>
    <a href="https://badge.fury.io/py/apify-client" rel="nofollow">
        <img src="https://badge.fury.io/py/apify-client.svg" alt="PyPI - Version" style="max-width: 100%;">
    </a>
    <a href="https://pypi.org/project/apify-client/" rel="nofollow">
        <img src="https://img.shields.io/pypi/dm/apify-client" alt="PyPI - Downloads" style="max-width: 100%;">
    </a>
    <a href="https://pypi.org/project/apify-client/" rel="nofollow">
        <img src="https://img.shields.io/pypi/pyversions/apify-client" alt="PyPI - Python version" style="max-width: 100%;">
    </a>
    <a href="https://discord.gg/jyEM2PRvMU" rel="nofollow">
        <img src="https://img.shields.io/discord/801163717915574323?label=discord" alt="Chat on discord" style="max-width: 100%;">
    </a>
</p>

The Apify API Client for Python is the official library to access the [Apify API](https://docs.apify.com/api/v2) from your Python applications. It provides useful features like automatic retries and convenience functions to improve your experience with the Apify API.

If you want to develop Apify Actors in Python, check out the [Apify SDK for Python](https://docs.apify.com/sdk/python) instead.

## Installation

Requires Python 3.10+

You can install the package from its [PyPI listing](https://pypi.org/project/apify-client). To do that, simply run `pip install apify-client` in your terminal.

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

Based on the endpoint, the client automatically extracts the relevant data and returns it in the expected format. Date strings are automatically converted to `datetime.datetime` objects. For exceptions, we throw an `ApifyApiError`, which wraps the plain JSON errors returned by API and enriches them with other context for easier debugging.

### Retries with exponential backoff

Network communication sometimes fails. The client will automatically retry requests that failed due to a network error, an internal error of the Apify API (HTTP 500+) or rate limit error (HTTP 429). By default, it will retry up to 8 times. First retry will be attempted after ~500ms, second after ~1000ms and so on. You can configure those parameters using the `max_retries` and `min_delay_between_retries_millis` options of the `ApifyClient` constructor.

### Support for asynchronous usage

Starting with version 1.0.0, the package offers an asynchronous version of the client, [`ApifyClientAsync`](https://docs.apify.com/api/client/python), which allows you to work with the Apify API in an asynchronous way, using the standard `async`/`await` syntax.

### Convenience functions and options

Some actions can't be performed by the API itself, such as indefinite waiting for an Actor run to finish (because of network timeouts). The client provides convenient `call()` and `wait_for_finish()` functions that do that. Key-value store records can be retrieved as objects, buffers or streams via the respective options, dataset items can be fetched as individual objects or serialized data and we plan to add better stream support and async iterators.

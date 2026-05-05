<h1 align="center">Apify API client for Python</h1>

<p align="center">
  <strong>The official Python client for the <a href="https://docs.apify.com/api/v2">Apify REST API</a>.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/apify-client/"><img src="https://badge.fury.io/py/apify-client.svg" alt="PyPI version"></a>
  <a href="https://pypi.org/project/apify-client/"><img src="https://img.shields.io/pypi/dm/apify-client" alt="PyPI downloads"></a>
  <a href="https://pypi.org/project/apify-client/"><img src="https://img.shields.io/pypi/pyversions/apify-client" alt="Python versions"></a>
  <a href="https://codecov.io/gh/apify/apify-client-python"><img src="https://codecov.io/gh/apify/apify-client-python/graph/badge.svg?token=TYQQWYYZ7A" alt="Coverage"></a>
  <a href="https://github.com/apify/apify-client-python/blob/master/LICENSE"><img src="https://img.shields.io/pypi/l/apify-client" alt="License"></a>
  <a href="https://discord.gg/jyEM2PRvMU"><img src="https://img.shields.io/discord/801163717915574323?label=discord" alt="Chat on Discord"></a>
</p>

`apify-client` lets you talk to the [Apify platform](https://apify.com) from Python — run [Actors](https://docs.apify.com/platform/actors), manage [storages](https://docs.apify.com/platform/storage) (datasets, key-value stores, request queues), schedule tasks, configure webhooks, and use everything else exposed by the [Apify API](https://docs.apify.com/api/v2). It ships both synchronous and asynchronous clients, fully typed responses, automatic retries with exponential backoff, tiered timeouts, pagination helpers, streaming, and a pluggable HTTP layer.

> If you want to **build** Apify Actors in Python rather than consume the API, use the [Apify SDK for Python](https://docs.apify.com/sdk/python) instead — it bundles this client and adds Actor-side primitives.

## Table of contents

- [Installation](#installation)
- [Quick start](#quick-start)
- [Features](#features)
- [Usage examples](#usage-examples)
- [Documentation](#documentation)
- [Related projects](#related-projects)
- [Support and community](#support-and-community)
- [Contributing](#contributing)
- [License](#license)

## Installation

`apify-client` requires **Python 3.11 or higher**. It is published on [PyPI](https://pypi.org/project/apify-client/) and can be installed for example with [pip](https://pip.pypa.io/):

```bash
pip install apify-client
```

or with [uv](https://docs.astral.sh/uv/):

```bash
uv add apify-client
```

or any other Python package manager that consumes PyPI.

## Quick start

You'll need an Apify API token — find yours in the [Integrations section of Apify Console](https://console.apify.com/account/integrations). Pass it to the client and you're ready to go.

### Synchronous client

```python
from apify_client import ApifyClient

client = ApifyClient('MY-APIFY-TOKEN')

# Start an Actor and wait for it to finish.
run = client.actor('apify/hello-world').call(
    run_input={'message': 'Hello, Apify!'},
)

# Iterate items from the run's default dataset.
for item in client.dataset(run.default_dataset_id).iterate_items():
    print(item)
```

### Asynchronous client

```python
import asyncio

from apify_client import ApifyClientAsync


async def main() -> None:
    client = ApifyClientAsync('MY-APIFY-TOKEN')

    run = await client.actor('apify/hello-world').call(
        run_input={'message': 'Hello, Apify!'},
    )

    # Iterate items from the run's default dataset.
    async for item in client.dataset(run.default_dataset_id).iterate_items():
        print(item)


asyncio.run(main())
```

> **Keep your token secret.** It authorizes requests on your behalf and can incur usage costs. Never commit it to source control or expose it to client-side code.

For a guided walkthrough — authenticating, running an Actor, and reading its results — see the [Quick start guide](https://docs.apify.com/api/client/python/docs/quick-start).

## Features

- **Synchronous and asynchronous clients** — pick [`ApifyClient`](https://docs.apify.com/api/client/python/reference/class/ApifyClient) or [`ApifyClientAsync`](https://docs.apify.com/api/client/python/reference/class/ApifyClientAsync) to match your codebase; both expose the same API ([Asyncio support](https://docs.apify.com/api/client/python/docs/concepts/asyncio-support)).
- **Fully typed responses** — every method returns a [Pydantic](https://docs.pydantic.dev/) model generated from the Apify OpenAPI spec, with IDE autocomplete and runtime validation ([Typed models](https://docs.apify.com/api/client/python/docs/concepts/typed-models)).
- **Automatic retries** — exponential backoff for network errors, HTTP 429, and 5xx responses, configurable per client ([Retries](https://docs.apify.com/api/client/python/docs/concepts/retries)).
- **Tiered timeouts** — short / medium / long tiers picked per endpoint, overridable per call ([Timeouts](https://docs.apify.com/api/client/python/docs/concepts/timeouts)).
- **Pagination and streaming** — iterate datasets, key-value store keys, or live logs without manual paging or buffering ([Pagination](https://docs.apify.com/api/client/python/docs/concepts/pagination), [Streaming](https://docs.apify.com/api/client/python/docs/concepts/streaming-resources)).
- **Convenience methods** — `call()`, `wait_for_finish()`, nested resource access, and other shortcuts that hide platform quirks ([Convenience methods](https://docs.apify.com/api/client/python/docs/concepts/convenience-methods)).
- **Pluggable HTTP layer** — swap the default [Impit](https://github.com/apify/impit)-based HTTP client for `httpx`, `requests`, `aiohttp`, or any custom implementation ([Custom HTTP clients](https://docs.apify.com/api/client/python/docs/concepts/custom-http-clients)).
- **Structured errors** — every API error surfaces as an [`ApifyApiError`](https://docs.apify.com/api/client/python/reference/class/ApifyApiError) with HTTP-specific subclasses for precise handling ([Error handling](https://docs.apify.com/api/client/python/docs/concepts/error-handling)).
- **Debug logging** — opt-in structured logging on the `apify_client` logger captures request URLs, status codes, retry attempts, and more ([Logging](https://docs.apify.com/api/client/python/docs/concepts/logging)).

## Usage examples

The client mirrors the platform's resource model. Each entry point returns either a **single-resource client** for an individual item or a **collection client** for listing and creating items ([Single and collection clients](https://docs.apify.com/api/client/python/docs/concepts/single-and-collection-clients)).

### List Actors and create one

```python
actors = client.actors()
print(actors.list(limit=10).items)

new_actor = actors.create(name='my-actor')
```

### Stream live logs while a run is in progress

```python
run = client.actor('apify/web-scraper').start(run_input={...})

with client.run(run.id).log().stream() as log_stream:
    for chunk in log_stream.iter_bytes():
        print(chunk.decode(), end='')
```

### Read and write key-value store records

```python
store = client.key_value_store('STORE-ID')
store.set_record('greeting', {'message': 'Hello!'})
record = store.get_record('greeting')
```

### Iterate dataset items with automatic pagination

```python
for item in client.dataset('DATASET-ID').iterate_items(fields='title,url'):
    process(item)
```

### Tune retries and timeouts

```python
from datetime import timedelta

from apify_client import ApifyClient

client = ApifyClient(
    token='MY-APIFY-TOKEN',
    max_retries=8,
    min_delay_between_retries=timedelta(milliseconds=500),
    timeout_long=timedelta(minutes=10),
)
```

For end-to-end recipes — passing input, managing tasks for reusable input, retrieving and merging Actor data, integrating with Pandas, plugging in a custom HTTP client — see the [Guides](https://docs.apify.com/api/client/python/docs/guides/passing-input-to-actor).

## Documentation

The full documentation lives at **[docs.apify.com/api/client/python](https://docs.apify.com/api/client/python)**.

| Section | What you'll find |
|---|---|
| [Introduction](https://docs.apify.com/api/client/python/docs) | Overview, prerequisites, and a tour of the client. |
| [Quick start](https://docs.apify.com/api/client/python/docs/quick-start) | Authenticate, run an Actor, and fetch its results step by step. |
| [Concepts](https://docs.apify.com/api/client/python/docs/concepts/asyncio-support) | Asyncio, single vs. collection clients, nested clients, error handling, retries, logging, convenience methods, pagination, streaming, custom HTTP clients, timeouts. |
| [Guides](https://docs.apify.com/api/client/python/docs/guides/passing-input-to-actor) | Pass input to an Actor, manage tasks for reusable input, retrieve Actor data, integrate with data libraries (e.g. Pandas), use HTTPX as the HTTP client. |
| [Upgrading](https://docs.apify.com/api/client/python/docs/upgrading/upgrading-to-v3) | Migrating between major versions. |
| [API reference](https://docs.apify.com/api/client/python/reference) | Generated reference for every class, method, and model. |
| [Changelog](https://docs.apify.com/api/client/python/docs/changelog) | Release history and breaking changes. |

## Related projects

- **[Apify SDK for Python](https://docs.apify.com/sdk/python)** — toolkit for **building** Apify Actors in Python (this client is bundled with it).
- **[Crawlee for Python](https://crawlee.dev/python)** — high-level web scraping and browser automation framework that powers many Actors.
- **[Apify API client for JavaScript / TypeScript](https://docs.apify.com/api/client/js)** — equivalent Apify API client for Node.js.
- **[Apify SDK for JavaScript / TypeScript](https://docs.apify.com/sdk/js)** — equivalent Apify SDK for Node.js.
- **[Crawlee for JavaScript / TypeScript](https://crawlee.dev)** — original Node.js implementation of the Crawlee framework.
- **[Apify CLI](https://docs.apify.com/cli)** — command-line tool for interacting with the Apify platform: managing Actors, runs, storages, local development, and deployment.

## Support and community

- **Discord** — chat with the team and other users on the [Apify Discord server](https://discord.gg/jyEM2PRvMU).
- **GitHub issues** — report a bug or request a feature in the repository's [issue tracker](https://github.com/apify/apify-client-python/issues).

## Contributing

Bug reports, fixes, and improvements are welcome! See [CONTRIBUTING.md](./CONTRIBUTING.md) for the development setup, coding standards, testing, and the release process. The repo uses [uv](https://docs.astral.sh/uv/) for project management and [Poe the Poet](https://poethepoet.natn.io/) as a task runner; the typical loop is:

```bash
uv run poe install-dev   # install dev deps and git hooks
uv run poe check-code    # lint, type-check, unit tests, docstring check
```

## License

Released under the [Apache License 2.0](./LICENSE).

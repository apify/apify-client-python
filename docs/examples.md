---
sidebar_label: Examples
title: 'Code examples'
---

## Passing an input to the Actor

The fastest way to get results from an Actor is to pass input directly to the `call` function.
We can set up the input, pass it to `call` function and get the reference of running Actor (or wait for finish).

```python
from apify_client import ApifyClient

# Client initialization with the API token
apify_client = ApifyClient(token='MY_APIFY_TOKEN')

actor_client = apify_client.actor('apify/instagram-hashtag-scraper')

input_data = { 'hashtags': ['rainbow'], 'resultsLimit': 20 }

# Run the Actor and wait for it to finish up to 60 seconds.
# Input is not persisted for next runs.
run_data = actor_client.call(run_input=input_data, timeout_secs=60)
```

## Manipulating with tasks

To run multiple inputs with the same Actor, most convenient way is to create multiple [tasks](https://docs.apify.com/platform/actors/running/tasks) with different inputs.
Task input is persisted on Apify platform when task is created.

```python
from __future__ import annotations

import asyncio

from apify_client import ApifyClientAsync
from apify_client.clients.resource_clients import TaskClientAsync

animal_hashtags = ['zebra', 'lion', 'hippo']


async def run_apify_task(client: TaskClientAsync) -> dict:
    result = await client.call()
    return result or {}


async def main() -> None:
    apify_client = ApifyClientAsync(token='MY_APIFY_TOKEN')

    # Create Apify tasks

    apify_tasks: list[dict] = []
    apify_tasks_client = apify_client.tasks()

    for hashtag in animal_hashtags:
        apify_task = await apify_tasks_client.create(
            name=f'hashtags-{hashtag}',
            actor_id='apify/instagram-hashtag-scraper',
            task_input={'hashtags': [hashtag], 'resultsLimit': 20},
            memory_mbytes=1024,
        )
        apify_tasks.append(apify_task)

    print('Tasks created:', apify_tasks)

    # Create Apify task clients

    apify_task_clients: list[TaskClientAsync] = []

    for apify_task in apify_tasks:
        task_id = apify_task['id']
        apify_task_client = apify_client.task(task_id)
        apify_task_clients.append(apify_task_client)

    print('Task clients created:', apify_task_clients)

    # Execute Apify tasks

    run_apify_tasks = [run_apify_task(client) for client in apify_task_clients]
    task_run_results = await asyncio.gather(*run_apify_tasks)

    print('Task results:', task_run_results)


if __name__ == '__main__':
    asyncio.run(main())
```

## Getting latest data from an Actor, joining datasets

Actor data are stored to [datasets](https://docs.apify.com/platform/storage/dataset). Datasets can be retrieved from Actor runs.
Dataset items can be listed with pagination.
Also, datasets can be merged together to make analysis further on with single file as dataset can be exported to various data format (CSV, JSON, XSLX, XML).
[Integrations](https://docs.apify.com/platform/integrations) can do the trick as well.

```python
from apify_client import ApifyClient

# Client initialization with the API token
apify_client = ApifyClient(token='MY_APIFY_TOKEN')

actor_client = apify_client.actor('apify/instagram-hashtag-scraper')

actor_runs = actor_client.runs()

# See pagination to understand how to get more datasets
actor_datasets = actor_runs.list(limit=20)

merging_dataset = apify_client.datasets().get_or_create(name='merge-dataset')

for dataset_item in actor_datasets.items:
    # Dataset items can be handled here. Dataset items can be paginated
    dataset_items = apify_client.dataset(dataset_id=dataset_item['id']).list_items(limit=1000)

    # Items can be pushed to single dataset
    apify_client.dataset(merging_dataset['id']).push_items(dataset_items.items)

    # ...
```

## Integration with data analysis libraries (Pandas)

The Apify API client for Python can be easily integrated with data analysis libraries.
Following example demonstrates how to load items from the last dataset run and pass them to a Pandas DataFrame for further analysis.
Pandas is a data analysis library that provides data structures and functions to efficiently manipulate large datasets.

```python
from apify_client import ApifyClient
import pandas

# Initialize the Apify client
client = ApifyClient(token="MY_APIFY_TOKEN")

# Load items from last dataset run
dataset_data = client.actor('apify/web-scraper').last_run().dataset().list_items()

# Pass dataset items to Pandas DataFrame
data_frame = pandas.DataFrame(dataset_data.items)

print(data_frame.info)
```

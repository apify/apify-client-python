---
title: Quick Start
sidebar_position: 1
---

## Installation

Requires Python 3.8+

You can install the client from its [PyPI listing](https://pypi.org/project/apify-client/).
To do that, simply run `pip install apify-client`.

## Quick Start

```python
from apify_client import ApifyClient

apify_client = ApifyClient('MY-APIFY-TOKEN')

# Start an actor and waits for it to finish
actor_call = apify_client.actor('john-doe/my-cool-actor').call()

# Fetch results from the actor's default dataset
dataset_items = apify_client.dataset(actor_call['defaultDatasetId']).list_items().items
```

# Apify Client v2 - attrs-based Client

This is version 2 of the Apify Python client, generated using `openapi-python-client` with **attrs** models.

## Overview

- **Generator**: `openapi-python-client` v0.27.0
- **Models**: attrs-based classes
- **Type Safety**: Full type hints with attrs
- **HTTP Client**: httpx-based, auto-generated
- **Structure**: Organized by API resource (actors, datasets, etc.)

## Generation

This client was generated from the Apify OpenAPI specification using:

```bash
# Install the generator
pip install openapi-python-client

# Generate the client
openapi-python-client generate \
    --url https://docs.apify.com/api/openapi.json \
    --output-path src/apify_client_v2
```

### What Gets Generated

`openapi-python-client` creates a **complete, production-ready client**:

- ✅ Full HTTP client (sync only)
- ✅ All API endpoints organized by resource
- ✅ attrs models for requests and responses
- ✅ Type hints throughout
- ✅ Error handling
- ✅ Documentation strings

### File Structure

```
src/apify_client_v2/
├── __init__.py           # Exports Client and AuthenticatedClient
├── client.py             # HTTP client implementation
├── errors.py             # Error classes
├── types.py              # Type definitions
├── models/               # attrs models (469 files)
│   ├── actor_short.py
│   ├── dataset_collection_item.py
│   ├── pagination_response.py
│   └── ...
└── api/                  # API endpoint modules
    ├── actors/           # Actor endpoints
    ├── actor_runs/       # Actor run endpoints
    ├── actor_tasks/      # Task endpoints
    ├── storage_datasets/ # Dataset endpoints
    └── ...
```

## Installation

```bash
# Required dependencies
pip install attrs httpx
```

## Usage

### Basic Client Setup

```python
from apify_client_v2 import Client, AuthenticatedClient

# Unauthenticated client (limited endpoints)
client = Client(base_url="https://api.apify.com/v2")

# Authenticated client (recommended)
client = AuthenticatedClient(
    base_url="https://api.apify.com/v2",
    token="your_apify_token"
)
```

### Making API Calls

```python
from apify_client_v2 import AuthenticatedClient
from apify_client_v2.api.actors import get_list_of_actors
from apify_client_v2.models import GetListOfActorsResponse

# Create authenticated client
client = AuthenticatedClient(
    base_url="https://api.apify.com/v2",
    token="your_token"
)

# Get list of actors
response: GetListOfActorsResponse = get_list_of_actors.sync(
    client=client,
    limit=10,
    offset=0
)

# Access the data (attrs models)
print(f"Total actors: {response.data.total}")
for actor in response.data.items:
    print(f"Actor: {actor.name} (ID: {actor.id})")
```

### Working with Different Resources

#### Actors

```python
from apify_client_v2.api.actors import (
    get_list_of_actors,
    get_actor,
    create_actor,
    update_actor,
    delete_actor,
)

# List actors
actors = get_list_of_actors.sync(client=client, limit=10)

# Get specific actor
actor = get_actor.sync(client=client, actor_id="my-actor-id")

# Create new actor
new_actor = create_actor.sync(
    client=client,
    json_body={"name": "my-new-actor", ...}
)
```

#### Datasets

```python
from apify_client_v2.api.storage_datasets import (
    get_list_of_datasets,
    get_dataset,
    get_items,
)

# List datasets
datasets = get_list_of_datasets.sync(client=client)

# Get dataset items
items = get_items.sync(
    client=client,
    dataset_id="your-dataset-id",
    format="json"
)
```

#### Actor Runs

```python
from apify_client_v2.api.actor_runs import (
    run_actor,
    get_run,
    abort_run,
)

# Run an actor
run = run_actor.sync(
    client=client,
    actor_id="my-actor-id",
    json_body={"input": {"url": "https://example.com"}}
)

# Get run status
run_info = get_run.sync(client=client, run_id=run.id)

# Abort run
abort_run.sync(client=client, run_id=run.id)
```

### Error Handling

```python
from apify_client_v2.errors import UnexpectedStatus
import httpx

try:
    response = get_list_of_actors.sync(client=client)
except UnexpectedStatus as e:
    print(f"API error: {e.status_code}")
    print(f"Response: {e.content}")
except httpx.HTTPError as e:
    print(f"HTTP error: {e}")
```

## Features

### attrs Models

All models use attrs for data validation:

```python
import attrs

@attrs.define
class ActorShort:
    id: str
    name: str
    username: str
    created_at: str
    modified_at: str
```

**Benefits**:
- Type checking
- Automatic `__init__`, `__repr__`, `__eq__`
- Immutable by default (if configured)
- Good IDE support

### Type Safety

Full type hints throughout:

```python
def get_list_of_actors(
    client: AuthenticatedClient,
    limit: int = 1000,
    offset: int = 0,
) -> GetListOfActorsResponse:
    ...
```

### Organized API Endpoints

Each API resource has its own module:

- `api.actors.*` - Actor management
- `api.actor_runs.*` - Running actors
- `api.actor_tasks.*` - Actor tasks
- `api.storage_datasets.*` - Dataset operations
- `api.storage_key_value_stores.*` - Key-value store operations
- `api.storage_request_queues.*` - Request queue operations
- `api.schedules.*` - Scheduling
- `api.webhooks_webhooks.*` - Webhook management
- `api.store.*` - Apify Store operations
- `api.users.*` - User management

## Advantages of v2

✅ **Complete Generation**: Everything generated automatically
✅ **Well-Organized**: Clear resource-based structure
✅ **Production-Ready**: Error handling, types, docs included
✅ **Maintained**: openapi-python-client is actively maintained
✅ **No Custom Code**: Just regenerate when API changes

## Limitations of v2

❌ **attrs, not Pydantic**: Uses attrs instead of Pydantic
❌ **No Pydantic v2**: Cannot use Pydantic v2 features
❌ **Sync Only**: No async support out of the box
❌ **Large Codebase**: 469+ model files

## Comparison with Other Versions

| Feature | v2 | v3 | v4 |
|---------|----|----|---|
| **Generator** | openapi-python-client | datamodel-code-generator | datamodel-code-generator |
| **Models** | attrs | Pydantic v2 | Pydantic v2 |
| **HTTP Client** | Generated (httpx) | Custom (httpx) | Custom (httpx) |
| **Async Support** | No | Yes | Yes |
| **Files** | 469+ | 3 | 3 |
| **Validation** | attrs | Pydantic v2 | Pydantic v2 |
| **Auto-complete** | Good | Excellent | Excellent |
| **API Endpoints** | All organized | Manual | Manual |

## When to Use v2

Use v2 if you:
- ✅ Are okay with attrs models
- ✅ Only need synchronous operations
- ✅ Want a complete, auto-generated solution
- ✅ Prefer resource-organized API structure
- ✅ Don't need Pydantic v2 features

Use v3/v4 if you:
- ✅ Need Pydantic v2 models
- ✅ Want async/await support
- ✅ Prefer a minimal codebase
- ✅ Need Pydantic validation features

## Regenerating v2

To regenerate when the API changes:

```bash
# Remove old version
rm -rf src/apify_client_v2

# Regenerate
openapi-python-client generate \
    --url https://docs.apify.com/api/openapi.json \
    --output-path src/apify_client_v2
```

## Documentation

All generated functions include docstrings with:
- Parameter descriptions
- Return types
- Example usage
- Error information

## Available Resources

The client provides access to all Apify API endpoints:

- **Actors**: Create, update, delete, list actors
- **Actor Runs**: Run actors, get status, abort runs
- **Actor Tasks**: Manage reusable actor configurations
- **Actor Versions**: Version management
- **Actor Builds**: Build management
- **Datasets**: Store and retrieve structured data
- **Key-Value Stores**: Store arbitrary data
- **Request Queues**: Manage crawling queues
- **Webhooks**: Event notifications
- **Schedules**: Scheduled actor runs
- **Store**: Browse Apify Store
- **Users**: User management

## Example: Complete Workflow

```python
from apify_client_v2 import AuthenticatedClient
from apify_client_v2.api.actors import get_list_of_actors, run_actor
from apify_client_v2.api.actor_runs import get_run, wait_for_finish
from apify_client_v2.api.storage_datasets import get_items

# Initialize client
client = AuthenticatedClient(
    base_url="https://api.apify.com/v2",
    token="your_token"
)

# 1. List available actors
actors = get_list_of_actors.sync(client=client, limit=5)
print(f"Found {actors.data.total} actors")

# 2. Run an actor
run = run_actor.sync(
    client=client,
    actor_id="apify/web-scraper",
    json_body={
        "startUrls": [{"url": "https://example.com"}],
        "maxCrawlDepth": 1
    }
)
print(f"Started run: {run.id}")

# 3. Wait for completion (manual polling)
import time
while True:
    run_info = get_run.sync(client=client, run_id=run.id)
    if run_info.status in ["SUCCEEDED", "FAILED", "ABORTED"]:
        break
    time.sleep(5)

# 4. Get results
if run_info.default_dataset_id:
    items = get_items.sync(
        client=client,
        dataset_id=run_info.default_dataset_id,
        format="json"
    )
    print(f"Got {len(items)} results")
```

## License

Apache 2.0

## Links

- [Apify API Documentation](https://docs.apify.com/api/v2)
- [Apify OpenAPI Spec](https://docs.apify.com/api/openapi.json)
- [openapi-python-client](https://github.com/openapi-generators/openapi-python-client)
- [attrs](https://www.attrs.org/)
- [httpx](https://www.python-httpx.org/)

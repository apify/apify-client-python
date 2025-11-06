# Apify Client v4 - Pydantic v2 Edition

The **recommended** Apify Python client with **Pydantic v2** models and custom HTTP client.

## Overview

- **Generator**: `datamodel-code-generator` v0.35.0 (models only)
- **Models**: Pydantic v2 BaseModel with full validation
- **Type Safety**: Complete IDE autocomplete and type checking
- **Sync & Async**: Both synchronous and asynchronous clients
- **HTTP Client**: Custom implementation built on `httpx`
- **Minimal Codebase**: Just 3 core files (vs 469+ in v2)
- **Version**: 4.0.0

## Why v4?

v4 is the **clean, recommended implementation** of the Pydantic v2 approach:

- ✅ **Pydantic v2**: Best-in-class validation and type safety
- ✅ **Minimal Code**: Small, maintainable codebase
- ✅ **Async Support**: Native async/await for modern Python
- ✅ **Type Safe**: Excellent IDE autocomplete and type checking
- ✅ **Auto-generated Models**: Always in sync with Apify API

### Generator Choice

After evaluating all available generators:

1. ❌ **openapi-python-client**: Excellent tool but uses attrs, no Pydantic v2 support
2. ❌ **openapi-generator** (Java): Only supports Pydantic v1, not v2
3. ✅ **datamodel-code-generator**: Only tool with `pydantic_v2.BaseModel` support

**Solution**: Use `datamodel-code-generator` for models + custom `httpx` client.

## Installation

```bash
# Install required dependencies
pip install httpx pydantic
```

## Generation Process

### Step 1: Download OpenAPI Spec

```bash
curl -o openapi.json https://docs.apify.com/api/openapi.json
```

### Step 2: Install Generator

```bash
pip install datamodel-code-generator
```

### Step 3: Generate Pydantic v2 Models

```bash
datamodel-codegen \
    --input openapi.json \
    --output src/apify_client_v4/models.py \
    --output-model-type pydantic_v2.BaseModel \
    --input-file-type openapi \
    --use-schema-description \
    --use-field-description \
    --use-default \
    --field-constraints
```

This generates:
- **2204 lines** of Pydantic v2 models
- **200+ model classes** covering all Apify API endpoints
- Full type hints with `Field()` descriptors
- Field descriptions from OpenAPI spec
- Default values where specified
- Field constraints (min/max, patterns, regex, etc.)

### Step 4: Custom HTTP Client

The HTTP client (`client.py`) was manually created to provide:
- `ApifyClient` - Synchronous client
- `ApifyClientAsync` - Asynchronous client
- Bearer token authentication
- Automatic Pydantic validation
- Context manager support
- All HTTP methods (GET, POST, PUT, DELETE)

## File Structure

```
src/apify_client_v4/
├── __init__.py          # Package exports (ApifyClient, ApifyClientAsync)
├── client.py            # HTTP client implementation (~290 lines)
├── models.py            # Pydantic v2 models (2204 lines, auto-generated)
└── README.md            # This file
```

**Breakdown**:

- **models.py** (2204 lines):
  - Generated from official Apify OpenAPI spec
  - 200+ Pydantic v2 `BaseModel` classes
  - Complete type hints and validation
  - Field descriptions and constraints

- **client.py** (~290 lines):
  - `ApifyClient` class for sync operations
  - `ApifyClientAsync` class for async operations
  - Built on `httpx` library
  - Automatic Pydantic validation

- **__init__.py**:
  - Exports the two client classes
  - Package version: 4.0.0

## Quick Start

### Synchronous Client

```python
from apify_client_v4 import ApifyClient
from apify_client_v4.models import GetListOfActorsResponse

# Initialize client with your API token
client = ApifyClient(token='your_apify_token')

# Get actors with automatic Pydantic validation
response = client.get(
    '/acts',
    params={'limit': 10},
    response_model=GetListOfActorsResponse
)

# Type-safe access with IDE autocomplete
print(f'Total: {response.total}')
for actor in response.data.items:
    print(f'{actor.name}: {actor.id}')
```

### Asynchronous Client

```python
from apify_client_v4 import ApifyClientAsync
from apify_client_v4.models import GetListOfActorsResponse

async def get_actors():
    async with ApifyClientAsync(token='your_token') as client:
        response = await client.get(
            '/acts',
            params={'limit': 10},
            response_model=GetListOfActorsResponse
        )
        return response

actors = await get_actors()
```

## Usage Examples

### Working with Datasets

```python
from apify_client_v4 import ApifyClient
from apify_client_v4.models import GetListOfDatasetsResponse

client = ApifyClient(token='your_token')

# List datasets with validation
datasets = client.get(
    '/datasets',
    params={'limit': 20, 'offset': 0},
    response_model=GetListOfDatasetsResponse
)

print(f"Total datasets: {datasets.data.total}")

# Get dataset items (raw response)
items = client.get(
    f'/datasets/{dataset_id}/items',
    params={'format': 'json', 'limit': 100}
)
```

### Running Actors

```python
from apify_client_v4 import ApifyClient
import time

client = ApifyClient(token='your_token')

# Start an actor run
run_response = client.post(
    f'/acts/{actor_id}/runs',
    json={
        'input': {
            'url': 'https://example.com',
            'maxDepth': 2
        }
    }
)

run_id = run_response['data']['id']
print(f'Started run: {run_id}')

# Poll for completion
while True:
    run_info = client.get(f'/actor-runs/{run_id}')
    status = run_info['data']['status']

    if status in ['SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT']:
        break

    time.sleep(5)

print(f"Run finished with status: {status}")
```

### Working with Request Queues

```python
from apify_client_v4 import ApifyClient

client = ApifyClient(token='your_token')

# Create a request queue
queue = client.post(
    '/request-queues',
    json={'name': 'my-queue'}
)

queue_id = queue['data']['id']

# Add requests to queue
client.post(
    f'/request-queues/{queue_id}/requests',
    json={
        'url': 'https://example.com',
        'method': 'GET'
    }
)
```

### Context Managers (Automatic Cleanup)

```python
# Sync - automatically closes connection
with ApifyClient(token='your_token') as client:
    data = client.get('/acts')
    # Client automatically closed after block

# Async - automatically closes connection
async with ApifyClientAsync(token='your_token') as client:
    data = await client.get('/acts')
    # Client automatically closed after block
```

### Optional Validation

```python
from apify_client_v4.models import GetListOfActorsResponse

# Option 1: With Pydantic validation (type-safe)
typed_response = client.get(
    '/acts',
    response_model=GetListOfActorsResponse
)
typed_response.total  # Full IDE autocomplete

# Option 2: Without validation (returns dict)
raw_response = client.get('/acts')
raw_response['data']['total']  # Raw dictionary
```

### All HTTP Methods

```python
# GET request
data = client.get('/path', params={'key': 'value'})

# POST request with JSON body
data = client.post('/path', json={'input': 'data'})

# PUT request
data = client.put('/path', json={'update': 'data'})

# DELETE request
client.delete('/path', params={'id': '123'})
```

### Error Handling

```python
import httpx
from pydantic import ValidationError

try:
    response = client.get(
        '/acts',
        response_model=GetListOfActorsResponse
    )
except httpx.HTTPStatusError as e:
    # HTTP errors (4xx, 5xx)
    print(f'HTTP {e.response.status_code}: {e.response.text}')
except ValidationError as e:
    # Pydantic validation errors
    print(f'Invalid response structure: {e}')
except httpx.TimeoutException:
    print('Request timed out')
```

## Features

### Pydantic v2 Models

All response models use Pydantic v2 for validation:

```python
from pydantic import BaseModel, Field

class ActorShort(BaseModel):
    id: str = Field(..., examples=['br9CKmk457'])
    name: str = Field(..., examples=['MyAct'])
    username: str = Field(..., examples=['janedoe'])
    created_at: str = Field(..., alias='createdAt')
    modified_at: str = Field(..., alias='modifiedAt')
```

**Benefits**:
- Automatic type validation
- Data conversion when safe
- JSON serialization with `.model_dump()` and `.model_dump_json()`
- Field validators and constraints
- Excellent IDE autocomplete

### HTTP Client Configuration

```python
client = ApifyClient(
    token='your_apify_token',      # Bearer token auth
    base_url='https://api.apify.com/v2',  # API endpoint
    timeout=60.0                    # Request timeout in seconds
)
```

### Async/Await Support

```python
import asyncio
from apify_client_v4 import ApifyClientAsync

async def fetch_multiple():
    async with ApifyClientAsync(token='your_token') as client:
        # Run multiple requests in parallel
        actors_task = client.get('/acts', params={'limit': 10})
        datasets_task = client.get('/datasets', params={'limit': 10})
        queues_task = client.get('/request-queues', params={'limit': 10})

        actors, datasets, queues = await asyncio.gather(
            actors_task,
            datasets_task,
            queues_task
        )

        return actors, datasets, queues

results = asyncio.run(fetch_multiple())
```

## Available Models

Key Pydantic models (200+ total):

**Actors**:
- `GetListOfActorsResponse` - Paginated actor list
- `ActorShort` - Actor summary
- `Actor` - Full actor details
- `ActorVersion` - Version information

**Datasets**:
- `GetListOfDatasetsResponse` - Dataset list
- `DatasetCollectionItem` - Dataset info
- `DatasetItem` - Individual item

**Key-Value Stores**:
- `GetListOfKeyValueStoresResponse` - Store list
- `KeyValueStoreCollectionItem` - Store info

**Request Queues**:
- `GetListOfRequestQueuesResponse` - Queue list
- `RequestQueueCollectionItem` - Queue info

**Runs & Tasks**:
- `RunResponse` - Actor run details
- `TaskResponse` - Task details

**Common**:
- `PaginationResponse` - Pagination metadata
- `EnvVar` - Environment variable

See `models.py` for all 200+ generated models.

## Comparison with Other Versions

| Feature | v2 (attrs) | v3 (Pydantic v2) | v4 (Pydantic v2) |
|---------|-----------|------------------|------------------|
| **Generator** | openapi-python-client | datamodel-code-generator | datamodel-code-generator |
| **Models** | attrs | Pydantic v2 | Pydantic v2 |
| **HTTP Client** | Generated | Custom (httpx) | Custom (httpx) |
| **Files** | 469+ files | 3 files | 3 files |
| **Validation** | attrs | Pydantic v2 | Pydantic v2 |
| **Async Support** | No | Yes | Yes |
| **Type Hints** | Good | Excellent | Excellent |
| **IDE Support** | Good | Excellent | Excellent |
| **Auto-complete** | Good | Excellent | Excellent |
| **API Endpoints** | All organized | Manual | Manual |
| **Code Size** | Large | Minimal | Minimal |
| **Pydantic Features** | No | Yes (v2) | Yes (v2) |
| **Status** | Legacy | Alternative | **Recommended** |

### When to Use v4

**Choose v4 (Recommended) if you:**
- ✅ Need Pydantic v2 models and validation
- ✅ Want async/await support
- ✅ Prefer a minimal, maintainable codebase
- ✅ Need Pydantic's JSON Schema generation
- ✅ Want excellent IDE autocomplete
- ✅ Are comfortable implementing endpoint wrappers as needed

**Choose v2 if you:**
- ✅ Are okay with attrs models (no Pydantic)
- ✅ Only need sync operations
- ✅ Want all API endpoints pre-organized
- ✅ Prefer complete auto-generated solution
- ✅ Don't need Pydantic-specific features

**v3 vs v4:**
- Both are functionally identical
- Both use datamodel-code-generator + custom httpx client
- v4 is the clean, recommended version
- v3 exists as proof-of-concept

## Regenerating Models

When Apify API changes, regenerate models:

```bash
# Download latest OpenAPI spec
curl -o openapi.json https://docs.apify.com/api/openapi.json

# Regenerate Pydantic v2 models
datamodel-codegen \
    --input openapi.json \
    --output src/apify_client_v4/models.py \
    --output-model-type pydantic_v2.BaseModel \
    --input-file-type openapi \
    --use-schema-description \
    --use-field-description \
    --use-default \
    --field-constraints
```

The HTTP client (`client.py`) doesn't need to change.

## Complete Example

```python
from apify_client_v4 import ApifyClient
from apify_client_v4.models import GetListOfActorsResponse
import time

# Initialize
client = ApifyClient(token='your_apify_token')

# 1. List actors
print("Fetching actors...")
actors = client.get(
    '/acts',
    params={'limit': 5},
    response_model=GetListOfActorsResponse
)

print(f"Found {actors.data.total} actors:")
for actor in actors.data.items:
    print(f"  - {actor.name} by {actor.username}")

# 2. Run an actor
print("\nStarting actor run...")
run = client.post(
    '/acts/apify~web-scraper/runs',
    json={
        'input': {
            'startUrls': [{'url': 'https://apify.com'}],
            'maxCrawlDepth': 1
        }
    }
)

run_id = run['data']['id']
print(f"Run ID: {run_id}")

# 3. Wait for completion
print("Waiting for completion...")
while True:
    run_info = client.get(f'/actor-runs/{run_id}')
    status = run_info['data']['status']
    print(f"  Status: {status}")

    if status in ['SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT']:
        break

    time.sleep(5)

# 4. Get results
if run_info['data'].get('defaultDatasetId'):
    dataset_id = run_info['data']['defaultDatasetId']
    items = client.get(
        f'/datasets/{dataset_id}/items',
        params={'format': 'json', 'limit': 10}
    )
    print(f"\nGot {len(items)} results from dataset")

# 5. Cleanup
client.close()
print("\nDone!")
```

## Advanced Usage

### Custom Validation Models

```python
from pydantic import BaseModel, Field, field_validator

class CustomActorModel(BaseModel):
    id: str
    name: str
    run_count: int = Field(alias='runCount', ge=0)

    @field_validator('name')
    @classmethod
    def name_must_be_lowercase(cls, v: str) -> str:
        return v.lower()

# Use with client
response = client.get(
    f'/acts/{actor_id}',
    response_model=CustomActorModel
)
```

### Async Batch Operations

```python
import asyncio
from apify_client_v4 import ApifyClientAsync

async def process_actors():
    async with ApifyClientAsync(token='your_token') as client:
        # Get list of actors
        actors_response = await client.get('/acts', params={'limit': 10})

        # Run all actors in parallel
        tasks = []
        for actor in actors_response['data']['items']:
            task = client.post(
                f"/acts/{actor['id']}/runs",
                json={'input': {}}
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        return results

runs = asyncio.run(process_actors())
```

### Custom Base URL

```python
# Use different API endpoint (e.g., local development)
client = ApifyClient(
    token='dev_token',
    base_url='http://localhost:8000/v2',
    timeout=120.0
)
```

## Why datamodel-code-generator?

We chose `datamodel-code-generator` because:

1. **Pydantic v2 Support**: Only tool with native `pydantic_v2.BaseModel` output
2. **OpenAPI 3.0 Compatible**: Excellent OpenAPI spec support
3. **Field-level Control**: Granular control over field generation
4. **Type Safety**: Superior type hint generation
5. **Active Development**: Well-maintained and regularly updated
6. **Customizable**: Many CLI options for fine-tuning

**Alternatives Considered**:
- ❌ **openapi-python-client**: Excellent but uses attrs, no Pydantic v2
- ❌ **openapi-generator** (Java): Only Pydantic v1, not v2
- ❌ **fastapi-codegen**: Designed for FastAPI servers, not clients

## Technical Details

### Generation Flags

The generation command uses these key flags:

- `--output-model-type pydantic_v2.BaseModel`: Use Pydantic v2
- `--input-file-type openapi`: Parse as OpenAPI specification
- `--use-schema-description`: Include schema descriptions
- `--use-field-description`: Include field-level descriptions
- `--use-default`: Include default values
- `--field-constraints`: Add validators (min, max, pattern, etc.)

### HTTP Client Architecture

```python
class ApifyClient:
    """Synchronous client"""
    def __init__(self, token, base_url, timeout): ...
    def get(self, path, params, response_model): ...
    def post(self, path, json, params, response_model): ...
    def put(self, path, json, params, response_model): ...
    def delete(self, path, params): ...
    def close(self): ...
    def __enter__(self): ...
    def __exit__(self): ...

class ApifyClientAsync:
    """Asynchronous client (same interface)"""
    async def get(...): ...
    async def post(...): ...
    # etc.
```

**Benefits of Custom Client**:
- Full control over behavior
- Easy to extend with helper methods
- No unnecessary generated code
- Simple to understand and maintain
- Minimal dependencies

## Dependencies

```bash
# Required
pip install httpx>=0.25.0
pip install pydantic>=2.0.0

# Optional for development
pip install datamodel-code-generator>=0.35.0
```

## License

Apache 2.0

## Links

- [Apify API Documentation](https://docs.apify.com/api/v2)
- [Apify OpenAPI Spec](https://docs.apify.com/api/openapi.json)
- [datamodel-code-generator](https://github.com/koxudaxi/datamodel-code-generator)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/)
- [httpx Documentation](https://www.python-httpx.org/)

## Support

For issues or questions:
- Apify API: https://docs.apify.com/
- This client: Check repository issues
- Pydantic: https://docs.pydantic.dev/
- httpx: https://www.python-httpx.org/

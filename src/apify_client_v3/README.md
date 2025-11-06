# Apify Client v3 - Pydantic v2 Edition

This is version 3 of the Apify Python client, featuring **Pydantic v2** models with a custom HTTP client.

## Overview

- **Generator**: `datamodel-code-generator` v0.35.0 (models only)
- **Models**: Pydantic v2 BaseModel
- **Type Safety**: Full IDE autocomplete and validation
- **Sync & Async**: Both synchronous and asynchronous clients
- **HTTP Client**: Custom implementation built on `httpx`
- **Minimal Codebase**: Just 3 core files (vs 469+ in v2)

## Why v3?

Version 2 uses `attrs` models. To get **Pydantic v2** support, we evaluated three generators:

1. ❌ **openapi-python-client**: Generates complete client but uses attrs, no Pydantic v2 support
2. ❌ **openapi-generator**: Java-based, only supports Pydantic v1
3. ✅ **datamodel-code-generator**: Supports Pydantic v2 via `--output-model-type pydantic_v2.BaseModel`

The trade-off: `datamodel-code-generator` only generates models, not the HTTP client. So v3 uses:
- **Generated**: Pydantic v2 models from OpenAPI spec
- **Custom**: HTTP client wrapper around `httpx`

## Generation

### Step 1: Generate Pydantic Models

```bash
# Download OpenAPI spec
curl -o openapi.json https://docs.apify.com/api/openapi.json

# Install generator
pip install datamodel-code-generator

# Generate Pydantic v2 models
datamodel-codegen \
    --input openapi.json \
    --output src/apify_client_v3/models.py \
    --output-model-type pydantic_v2.BaseModel \
    --input-file-type openapi \
    --use-schema-description \
    --use-field-description \
    --use-default \
    --field-constraints
```

This generates 2133 lines of Pydantic v2 models with:
- Full type hints
- Field descriptions
- Default values
- Field constraints (min/max, patterns, etc.)
- JSON schema support

### Step 2: Create HTTP Client

The HTTP client (`client.py`) was manually created to wrap `httpx` and provide:
- Sync and async support
- Bearer token authentication
- Automatic Pydantic validation
- Context manager support
- All HTTP methods (GET, POST, PUT, DELETE)

## Installation

```bash
# Install required dependencies
pip install httpx pydantic
```

## Usage Examples

### Basic Sync Usage

```python
from apify_client_v3 import ApifyClient
from apify_client_v3.models import GetListOfActorsResponse

# Initialize client
client = ApifyClient(token='your_apify_token')

# Get actors with Pydantic validation
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

### Basic Async Usage

```python
from apify_client_v3 import ApifyClientAsync
from apify_client_v3.models import GetListOfActorsResponse

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

### Working with Datasets

```python
from apify_client_v3 import ApifyClient
from apify_client_v3.models import GetListOfDatasetsResponse

client = ApifyClient(token='your_token')

# List datasets
datasets = client.get(
    '/datasets',
    params={'limit': 20},
    response_model=GetListOfDatasetsResponse
)

# Get dataset items (raw response)
items = client.get(
    f'/datasets/{dataset_id}/items',
    params={'format': 'json', 'limit': 100}
)
```

### Running Actors

```python
from apify_client_v3 import ApifyClient

client = ApifyClient(token='your_token')

# Run an actor
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

# Check run status
run_status = client.get(f'/actor-runs/{run_id}')
print(f"Status: {run_status['data']['status']}")
```

### Context Managers

```python
# Sync
with ApifyClient(token='your_token') as client:
    data = client.get('/acts')

# Async
async with ApifyClientAsync(token='your_token') as client:
    data = await client.get('/acts')
```

### Optional Validation

```python
# With Pydantic validation (type-safe)
typed_response = client.get(
    '/acts',
    response_model=GetListOfActorsResponse
)
typed_response.total  # Full autocomplete

# Without validation (returns dict)
raw_data = client.get('/acts')
raw_data['data']['total']  # Raw dict access
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

## File Structure

```
src/apify_client_v3/
├── __init__.py          # Package exports
├── client.py            # HTTP client (sync & async)
├── models.py            # Pydantic v2 models (2133 lines)
└── README.md            # This file
```

**models.py** (2133 lines):
- Generated from OpenAPI spec
- 200+ Pydantic v2 models
- Full type hints and validation

**client.py**:
- `ApifyClient` - Synchronous HTTP client
- `ApifyClientAsync` - Asynchronous HTTP client
- Built on `httpx`

**__init__.py**:
- Exports the two client classes
- Version: 3.0.0

## Features Deep Dive

### Pydantic v2 Validation

All models use Pydantic v2 for:

- **Automatic type validation**: Data is validated on assignment
- **Data conversion**: Automatic type coercion when safe
- **JSON serialization**: Built-in `.model_dump()` and `.model_dump_json()`
- **Field validation**: Custom validators and constraints
- **IDE autocomplete**: Full support in VSCode, PyCharm, etc.

Example model structure:

```python
from pydantic import BaseModel, Field

class ActorShort(BaseModel):
    id: str = Field(..., examples=['br9CKmk457'])
    name: str = Field(..., examples=['MyAct'])
    username: str = Field(..., examples=['janedoe'])
    created_at: str = Field(..., alias='createdAt')
    modified_at: str = Field(..., alias='modifiedAt')

class PaginationResponse(BaseModel):
    total: float = Field(..., examples=[2])
    offset: float = Field(..., examples=[0])
    limit: float = Field(..., examples=[1000])
    count: float = Field(..., examples=[2])
    desc: bool = Field(..., examples=[False])

class GetListOfActorsResponse(BaseModel):
    data: PaginationResponse
```

### HTTP Client Features

Both `ApifyClient` and `ApifyClientAsync` provide:

**Authentication**:
```python
client = ApifyClient(
    token='your_apify_token',  # Bearer token auth
    base_url='https://api.apify.com/v2',
    timeout=60.0  # Request timeout in seconds
)
```

**Flexible Responses**:
```python
# Option 1: Validated Pydantic model
typed = client.get('/acts', response_model=GetListOfActorsResponse)
typed.total  # Type: float, with autocomplete

# Option 2: Raw dictionary
raw = client.get('/acts')
raw['data']['total']  # Type: Any
```

**Error Handling**:
```python
import httpx
from pydantic import ValidationError

try:
    response = client.get('/acts', response_model=GetListOfActorsResponse)
except httpx.HTTPStatusError as e:
    # HTTP errors (4xx, 5xx)
    print(f'HTTP {e.response.status_code}: {e.response.text}')
except ValidationError as e:
    # Pydantic validation errors
    print(f'Invalid response: {e}')
except httpx.TimeoutException:
    print('Request timed out')
```

**Resource Cleanup**:
```python
# Manual cleanup
client = ApifyClient(token='...')
try:
    data = client.get('/acts')
finally:
    client.close()

# Automatic cleanup with context manager
with ApifyClient(token='...') as client:
    data = client.get('/acts')  # Client closed automatically
```

## Architecture

### Generated Models

Models are generated from the official Apify OpenAPI specification using `datamodel-code-generator`:

```bash
datamodel-codegen \
    --input openapi.json \
    --output src/apify_client_v3/models.py \
    --output-model-type pydantic_v2.BaseModel \
    --input-file-type openapi
```

### HTTP Client

The HTTP layer is built on `httpx`:
- Modern async/await support
- Connection pooling
- Timeout handling
- Automatic retries (configurable)

## Comparison with v2

| Feature | v2 (attrs) | v3 (Pydantic v2) |
|---------|-----------|------------------|
| Models | attrs | Pydantic v2 |
| Validation | Manual | Automatic |
| Type hints | Limited | Full |
| IDE support | Basic | Complete |
| Serialization | Custom | Built-in |
| Generation | openapi-python-client | datamodel-code-generator |

## Available Models

Key Pydantic models include (200+ total):

**Actors**:
- `GetListOfActorsResponse` - Paginated list of actors
- `ActorShort` - Actor summary
- `Actor` - Full actor details
- `ActorVersion` - Actor version information

**Datasets**:
- `GetListOfDatasetsResponse` - Paginated list of datasets
- `DatasetCollectionItem` - Dataset information
- `DatasetItem` - Individual dataset item

**Key-Value Stores**:
- `GetListOfKeyValueStoresResponse` - KV store list
- `KeyValueStoreCollectionItem` - KV store info

**Request Queues**:
- `GetListOfRequestQueuesResponse` - Request queue list
- `RequestQueueCollectionItem` - Queue information

**Runs & Tasks**:
- `RunResponse` - Actor run details
- `TaskResponse` - Actor task details

**Common Models**:
- `PaginationResponse` - Pagination metadata
- `EnvVar` - Environment variable

See `models.py` for the complete list of 200+ generated models.

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
| **API Endpoints** | All organized | Manual implementation | Manual implementation |
| **Code Size** | Large | Minimal | Minimal |
| **Pydantic Features** | No | Yes (v2) | Yes (v2) |

### When to Use v3

**Choose v3 if you:**
- ✅ Need Pydantic v2 models and validation
- ✅ Want async/await support
- ✅ Prefer a minimal, clean codebase
- ✅ Need Pydantic's JSON Schema generation
- ✅ Want excellent IDE autocomplete
- ✅ Are comfortable implementing endpoint wrappers as needed

**Choose v2 if you:**
- ✅ Are okay with attrs models
- ✅ Only need sync operations
- ✅ Want all API endpoints pre-organized
- ✅ Prefer a complete auto-generated solution
- ✅ Don't need Pydantic-specific features

**v3 vs v4:**
- Both are functionally identical
- Both use datamodel-code-generator + custom httpx client
- v4 is a clean rebuild confirming the approach
- Use whichever you prefer (v4 is recommended for new projects)

## Regenerating Models

If the Apify OpenAPI spec changes, regenerate the models:

```bash
# Download latest spec
curl -o openapi.json https://docs.apify.com/api/openapi.json

# Regenerate models
datamodel-codegen \
    --input openapi.json \
    --output src/apify_client_v3/models.py \
    --output-model-type pydantic_v2.BaseModel \
    --input-file-type openapi \
    --use-schema-description \
    --use-field-description \
    --use-default \
    --field-constraints
```

The HTTP client (`client.py`) remains unchanged.

## Complete Example

```python
from apify_client_v3 import ApifyClient
from apify_client_v3.models import GetListOfActorsResponse
import time

# Initialize client
client = ApifyClient(token='your_apify_token')

# 1. List actors
actors_response = client.get(
    '/acts',
    params={'limit': 5, 'offset': 0},
    response_model=GetListOfActorsResponse
)

print(f"Found {actors_response.data.total} actors")
for actor in actors_response.data.items:
    print(f"  - {actor.name} by {actor.username}")

# 2. Run an actor
run_response = client.post(
    '/acts/apify~web-scraper/runs',
    json={
        'input': {
            'startUrls': [{'url': 'https://apify.com'}],
            'maxCrawlDepth': 1
        }
    }
)

run_id = run_response['data']['id']
print(f"\nStarted run: {run_id}")

# 3. Wait for completion (simple polling)
while True:
    run_info = client.get(f'/actor-runs/{run_id}')
    status = run_info['data']['status']
    print(f"Status: {status}")

    if status in ['SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT']:
        break

    time.sleep(5)

# 4. Get results from default dataset
if run_info['data']['defaultDatasetId']:
    dataset_id = run_info['data']['defaultDatasetId']
    items = client.get(
        f'/datasets/{dataset_id}/items',
        params={'format': 'json', 'limit': 10}
    )
    print(f"\nGot {len(items)} results")

# 5. Cleanup
client.close()
```

## Advanced Usage

### Custom Base URL

```python
# Use a different API endpoint
client = ApifyClient(
    token='your_token',
    base_url='https://api.apify.com/v2',  # Default
    timeout=120.0  # Increase timeout
)
```

### Async Parallel Requests

```python
import asyncio
from apify_client_v3 import ApifyClientAsync

async def fetch_multiple():
    async with ApifyClientAsync(token='your_token') as client:
        # Run requests in parallel
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

### Custom Validation

```python
from pydantic import BaseModel, Field

# Define your own model for custom validation
class CustomActorResponse(BaseModel):
    id: str
    name: str
    run_count: int = Field(alias='runCount', ge=0)

# Use with the client
response = client.get(
    f'/acts/{actor_id}',
    response_model=CustomActorResponse
)
```

## Why datamodel-code-generator?

We chose `datamodel-code-generator` because:

1. **Pydantic v2 Support**: Only tool with native `pydantic_v2.BaseModel` output
2. **OpenAPI 3.0 Compatible**: Excellent OpenAPI spec support
3. **Field-level Control**: Granular control over field generation
4. **Type Safety**: Superior type hint generation
5. **Active Development**: Well-maintained and regularly updated
6. **Customizable**: Many CLI options for fine-tuning output

Alternatives considered:
- ❌ **openapi-python-client**: Great tool but uses attrs, no Pydantic v2
- ❌ **openapi-generator** (Java): Only supports Pydantic v1, not v2
- ❌ **fastapi-codegen**: Focused on FastAPI servers, not clients

## Technical Details

### Model Generation Options

The generation command uses these important flags:

- `--output-model-type pydantic_v2.BaseModel`: Use Pydantic v2
- `--input-file-type openapi`: Parse as OpenAPI spec
- `--use-schema-description`: Include schema descriptions
- `--use-field-description`: Include field descriptions
- `--use-default`: Include default values
- `--field-constraints`: Add field validators (min, max, pattern, etc.)

### HTTP Client Implementation

The custom HTTP client provides:

```python
class ApifyClient:
    def __init__(self, token, base_url, timeout): ...
    def get(self, path, params, response_model): ...
    def post(self, path, json, params, response_model): ...
    def put(self, path, json, params, response_model): ...
    def delete(self, path, params): ...
    def close(self): ...
    def __enter__(self): ...
    def __exit__(self): ...

class ApifyClientAsync:
    # Same methods but async
    async def get(...): ...
    async def post(...): ...
    # etc.
```

Benefits of custom client:
- Full control over behavior
- Easy to extend with custom methods
- No unnecessary generated code
- Simple to understand and maintain

## License

Apache 2.0

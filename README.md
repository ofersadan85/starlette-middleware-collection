# starlette-middleware-collection

A small collection of Starlette-compatible middleware, with FastAPI compatibility and examples.

## Included Middleware

- `SizeLimit`: Rejects requests with bodies larger than a configured byte limit.
- `RequestUUID`: Adds a per-request UUID to `request.state.id`.

## Installation

Install from source:

```bash
pip install -e .
```

## SizeLimit

The `SizeLimit` middleware checks the incoming `content-length` header and returns `413 Content Too Large` when the request body exceeds the configured limit.

- Constructor argument: `limit` (bytes)
- Environment variable: `MW_REQUEST_BODY_LIMIT`
- Default: `10 * 1024 * 1024` (10 MB)

### Basic Usage

```python
from fastapi import FastAPI
from starlette_middleware_collection import SizeLimit

app = FastAPI()
app.add_middleware(SizeLimit)
```

### With a Custom Limit

```python
from fastapi import FastAPI
from starlette_middleware_collection import SizeLimit

app = FastAPI()
app.add_middleware(SizeLimit, limit=5 * 1024 * 1024)  # 5 MB
```

### Using Environment Variable (SizeLimit)

```python
import os
from fastapi import FastAPI
from starlette_middleware_collection import SizeLimit

os.environ["MW_REQUEST_BODY_LIMIT"] = str(1024 * 1024)  # 1 MB

app = FastAPI()
app.add_middleware(SizeLimit)
```

> [!NOTE]
> The constructor argument takes precedence over the environment variable.

## RequestUUID

The `RequestUUID` middleware sets `request.state.id` for every request.

- Constructor argument: `uuid_version`
- Environment variable: `MW_UUID_VERSION`
- Supported versions: `4`, `7`
- Default: `7`

### Basic Usage (Default UUIDv7)

```python
from fastapi import FastAPI, Request
from starlette_middleware_collection import RequestUUID

app = FastAPI()
app.add_middleware(RequestUUID)


@app.post("/")
async def read_root(request: Request):
    return {"uuid": str(request.state.id)}
```

### With a Custom UUID Version

```python
from fastapi import FastAPI
from starlette_middleware_collection import RequestUUID

app = FastAPI()
app.add_middleware(RequestUUID, uuid_version=4)
```

### Using Environment Variable (RequestUUID)

```python
import os
from fastapi import FastAPI
from starlette_middleware_collection import RequestUUID

os.environ["MW_UUID_VERSION"] = "4"

app = FastAPI()
app.add_middleware(RequestUUID)
```

> [!NOTE]
> The constructor argument takes precedence over the environment variable.

If an unsupported `uuid_version` is provided, a `ValueError` is raised.

## Combined Example

```python
from fastapi import FastAPI, Request
from starlette_middleware_collection import RequestUUID, SizeLimit

app = FastAPI()
app.add_middleware(SizeLimit, limit=2 * 1024 * 1024)  # 2 MB
app.add_middleware(RequestUUID, uuid_version=7)


@app.post("/upload")
async def upload(request: Request):
    return {"request_id": str(request.state.id)}
```

## Running Tests

```bash
pytest
```

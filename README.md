# starlette-middleware-collection

[![starlette-middleware-collection on pypi](https://img.shields.io/pypi/v/starlette-middleware-collection)](https://pypi.org/project/starlette-middleware-collection/)
[![CI and Publish](https://github.com/ofersadan85/starlette-middleware-collection/actions/workflows/ci-publish.yml/badge.svg)](https://github.com/ofersadan85/starlette-middleware-collection/actions/workflows/ci-publish.yml)
![Code Size](https://img.shields.io/github/languages/code-size/ofersadan85/starlette-middleware-collection)
[![Coverage](https://img.shields.io/endpoint?url=https%3A%2F%2Fn8n.zero-ml.com%2Fwebhook%2F92771a42-9389-4c1d-865b-930acd27a5e5%3Fid%3D1)](https://github.com/ofersadan85/starlette-middleware-collection/actions/workflows/ci-publish.yml)

A small collection of Starlette compatible middleware, with FastAPI compatibility and examples.

## Included Middleware

- `SizeLimit`: Rejects requests with bodies larger than a configured byte limit.
- `RequestUUID`: Adds a per-request UUID to `request.state.id`.

## Installation

Install from PyPI:

```bash
pip install starlette-middleware-collection
```

Or with [uv](https://astral.sh/uv):

```bash
uv add starlette-middleware-collection
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

## Requirements

![starlette-middleware-collection](https://img.shields.io/pypi/pyversions/starlette-middleware-collection)

Currently supports only Python 3.14 with latest version of [Starlette](https://pypi.org/project/starlette/). We plan on supporting older versions of Python and Starlette in the near future.

## Contributing

[![Open Issues](https://img.shields.io/github/issues-raw/ofersadan85/starlette-middleware-collection)](https://github.com/ofersadan85/starlette-middleware-collection/issues)
[![Closed Issues](https://img.shields.io/github/issues-closed-raw/ofersadan85/starlette-middleware-collection)](https://github.com/ofersadan85/starlette-middleware-collection/issues)
[![Open Pull Requests](https://img.shields.io/github/issues-pr-raw/ofersadan85/starlette-middleware-collection)](https://github.com/ofersadan85/starlette-middleware-collection/pulls)
[![Closed Pull Requests](https://img.shields.io/github/issues-pr-closed-raw/ofersadan85/starlette-middleware-collection)](https://github.com/ofersadan85/starlette-middleware-collection/pulls)

For bugs / feature requests please submit [issues](https://github.com/ofersadan85/starlette-middleware-collection/issues). If you would like to contribute to this project, you are welcome to [submit a pull request](https://github.com/ofersadan85/starlette-middleware-collection/pulls)

## Warranty / Liability / Official support

This project is being developed independently, we provide the package "as-is" without any implied warranty or liability, usage is your own responsibility

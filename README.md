# starlette-middleware-collection

[![starlette-middleware-collection on pypi](https://img.shields.io/pypi/v/starlette-middleware-collection)](https://pypi.org/project/starlette-middleware-collection/)
[![CI and Publish](https://github.com/ofersadan85/starlette-middleware-collection/actions/workflows/ci-publish.yml/badge.svg)](https://github.com/ofersadan85/starlette-middleware-collection/actions/workflows/ci-publish.yml)
![Code Size](https://img.shields.io/github/languages/code-size/ofersadan85/starlette-middleware-collection)
[![Coverage](https://img.shields.io/endpoint?url=https%3A%2F%2Fn8n.zero-ml.com%2Fwebhook%2F92771a42-9389-4c1d-865b-930acd27a5e5%3Fid%3D1)](https://github.com/ofersadan85/starlette-middleware-collection/actions/workflows/ci-publish.yml)

A small collection of Starlette compatible middleware, with FastAPI compatibility and examples.

## Included Middleware

- `SizeLimit`: Rejects requests with bodies larger than a configured byte limit.
- `RequestUUID`: Adds a per-request UUID to `request.state.id`.
- `ResponseUUID`: Sets an `X-Api-Request-Id` response header, propagating the `RequestUUID` id when present.
- `ResponseTime`: Adds an `X-Process-Time` response header with the request duration in seconds.
- `RequestLogging`: Logs one record per request, with a configurable structure and pluggable backend.

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

### Basic Usage (SizeLimit)

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

## ResponseUUID

The `ResponseUUID` middleware sets a request-id header (`X-Api-Request-Id` by default) on
every response. When `RequestUUID` is also installed it propagates the same
`request.state.id`; otherwise it generates a fresh UUID so the header is always present.

- Constructor arguments: `header_name`, `uuid_version`
- Environment variable: `MW_RESPONSE_ID_HEADER` (header name)
- Default header: `X-Api-Request-Id`
- Supported versions: `4`, `7` (default `7`, used only when generating a fresh id)

### Basic Usage (ResponseUUID)

```python
from fastapi import FastAPI
from starlette_middleware_collection import ResponseUUID

app = FastAPI()
app.add_middleware(ResponseUUID)  # generates a fresh id per response
```

### Paired with RequestUUID

```python
from fastapi import FastAPI
from starlette_middleware_collection import RequestUUID, ResponseUUID

app = FastAPI()
app.add_middleware(ResponseUUID)   # reads request.state.id ...
app.add_middleware(RequestUUID)    # ... which this sets
```

### With a Custom Header (ResponseUUID)

```python
from fastapi import FastAPI
from starlette_middleware_collection import ResponseUUID

app = FastAPI()
app.add_middleware(ResponseUUID, header_name="X-Trace-Id")
```

> [!NOTE]
> The constructor argument takes precedence over the environment variable.

## ResponseTime

The `ResponseTime` middleware measures how long each request takes and sets the elapsed
time (in seconds) on a response header (`X-Process-Time` by default).

- Constructor argument: `header_name`
- Environment variable: `MW_TIMING_HEADER` (header name)
- Default header: `X-Process-Time`

### Basic Usage (ResponseTime)

```python
from fastapi import FastAPI
from starlette_middleware_collection import ResponseTime

app = FastAPI()
app.add_middleware(ResponseTime)  # e.g. X-Process-Time: 0.001234
```

### With a Custom Header (ResponseTime)

```python
from fastapi import FastAPI
from starlette_middleware_collection import ResponseTime

app = FastAPI()
app.add_middleware(ResponseTime, header_name="X-Elapsed-Seconds")
```

> [!NOTE]
> The constructor argument takes precedence over the environment variable.

## RequestLogging

The `RequestLogging` middleware emits one log record per request. By default it logs a
structured dict to a standard-library logger; you can customize the record with a
`formatter` and route it anywhere with a `handler` (a sync or async callable — write to a
file, database, queue, etc.). It pairs with `RequestUUID`: when a request id exists it is
included as `request_id`.

- Constructor arguments: `logger`, `level`, `handler`, `formatter`
- Environment variable: `MW_REQUEST_LOG_LEVEL` (log level, e.g. `20` for `INFO`)
- Default logger: `starlette_middleware_collection.request`
- Default level: `logging.INFO`

The default record looks like:

```python
{
    "request_id": "019f84...",  # or None when RequestUUID is not installed
    "method": "POST",
    "path": "/upload",
    "status_code": 200,
    "duration_ms": 12.3,
    "client": "127.0.0.1",
}
```

### Basic Usage (RequestLogging)

```python
import logging
from fastapi import FastAPI
from starlette_middleware_collection import RequestLogging

logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.add_middleware(RequestLogging)
```

### Custom Backend (file, database, ...)

```python
from fastapi import FastAPI
from starlette_middleware_collection import RequestLogging


async def to_database(record: dict) -> None:
    await db.access_logs.insert(record)  # your async backend


app = FastAPI()
app.add_middleware(RequestLogging, handler=to_database)
```

### Custom Record Structure

```python
from fastapi import FastAPI, Request
from starlette.responses import Response
from starlette_middleware_collection import RequestLogging


def formatter(request: Request, response: Response, elapsed: float) -> str:
    return f"{request.method} {request.url.path} -> {response.status_code} ({elapsed:.3f}s)"


app = FastAPI()
app.add_middleware(RequestLogging, formatter=formatter)
```

> [!NOTE]
> A failing `handler` never breaks the request; the error is logged instead.

## Combined Example

```python
from fastapi import FastAPI, Request
from starlette_middleware_collection import (
    RequestLogging,
    RequestUUID,
    ResponseTime,
    ResponseUUID,
    SizeLimit,
)

app = FastAPI()
# Middleware run outermost-first (last added runs first on the way in).
app.add_middleware(RequestLogging)
app.add_middleware(ResponseTime)                     # X-Process-Time
app.add_middleware(ResponseUUID)                       # X-Api-Request-Id (propagated below)
app.add_middleware(SizeLimit, limit=2 * 1024 * 1024)  # 2 MB
app.add_middleware(RequestUUID, uuid_version=7)        # sets request.state.id


@app.post("/upload")
async def upload(request: Request):
    return {"request_id": str(request.state.id)}
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed list of changes and version history.

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

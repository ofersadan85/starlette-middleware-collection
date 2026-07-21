# starlette-middleware-collection

[![starlette-middleware-collection on pypi](https://img.shields.io/pypi/v/starlette-middleware-collection)](https://pypi.org/project/starlette-middleware-collection/)
[![CI and Publish](https://github.com/ofersadan85/starlette-middleware-collection/actions/workflows/ci-publish.yml/badge.svg)](https://github.com/ofersadan85/starlette-middleware-collection/actions/workflows/ci-publish.yml)
![Code Size](https://img.shields.io/github/languages/code-size/ofersadan85/starlette-middleware-collection)
[![Coverage](https://img.shields.io/endpoint?url=https%3A%2F%2Fn8n.zero-ml.com%2Fwebhook%2F92771a42-9389-4c1d-865b-930acd27a5e5%3Fid%3D1)](https://github.com/ofersadan85/starlette-middleware-collection/actions/workflows/ci-publish.yml)

A small collection of Starlette compatible middleware, with FastAPI compatibility and examples.

📚 Full usage examples and API reference: <https://ofersadan85.github.io/starlette-middleware-collection/>

## Included Middleware

- [`SizeLimit`](https://ofersadan85.github.io/starlette-middleware-collection/middleware/size_limit/): Rejects requests with bodies larger than a configured byte limit.
- [`RequestUUID`](https://ofersadan85.github.io/starlette-middleware-collection/middleware/request_uuid/): Adds a per-request UUID to `request.state.id`.
- [`ResponseUUID`](https://ofersadan85.github.io/starlette-middleware-collection/middleware/response_uuid/): Sets an `X-Api-Request-Id` response header, propagating the `RequestUUID` id when present.
- [`ResponseTime`](https://ofersadan85.github.io/starlette-middleware-collection/middleware/response_timing/): Adds an `X-Process-Time` response header with the request duration in seconds.
- [`RequestLogging`](https://ofersadan85.github.io/starlette-middleware-collection/middleware/request_logging/): Logs one record per request, with a configurable structure and pluggable backend.

## Installation

Install from PyPI:

```bash
pip install starlette-middleware-collection
```

Or with [uv](https://astral.sh/uv):

```bash
uv add starlette-middleware-collection
```

## Quick Example

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

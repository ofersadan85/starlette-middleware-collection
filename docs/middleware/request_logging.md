# RequestLogging

::: starlette_middleware_collection.RequestLogging

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

## Usage

### Basic Usage

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

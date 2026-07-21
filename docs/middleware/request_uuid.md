# RequestUUID

::: starlette_middleware_collection.RequestUUID

## Usage

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

### Using an Environment Variable

```python
import os
from fastapi import FastAPI
from starlette_middleware_collection import RequestUUID

os.environ["MW_UUID_VERSION"] = "4"

app = FastAPI()
app.add_middleware(RequestUUID)
```

If an unsupported `uuid_version` is provided, a `ValueError` is raised.

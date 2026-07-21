# ResponseUUID

::: starlette_middleware_collection.ResponseUUID

## Usage

### Basic Usage

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

### With a Custom Header

```python
from fastapi import FastAPI
from starlette_middleware_collection import ResponseUUID

app = FastAPI()
app.add_middleware(ResponseUUID, header_name="X-Trace-Id")
```

# ResponseTime

::: starlette_middleware_collection.ResponseTime

## Usage

### Basic Usage

```python
from fastapi import FastAPI
from starlette_middleware_collection import ResponseTime

app = FastAPI()
app.add_middleware(ResponseTime)  # e.g. X-Process-Time: 0.001234
```

### With a Custom Header

```python
from fastapi import FastAPI
from starlette_middleware_collection import ResponseTime

app = FastAPI()
app.add_middleware(ResponseTime, header_name="X-Elapsed-Seconds")
```

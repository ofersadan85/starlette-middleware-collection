# SizeLimit

::: starlette_middleware_collection.SizeLimit

## Usage

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

### Using an Environment Variable

```python
import os
from fastapi import FastAPI
from starlette_middleware_collection import SizeLimit

os.environ["MW_REQUEST_BODY_LIMIT"] = str(1024 * 1024)  # 1 MB

app = FastAPI()
app.add_middleware(SizeLimit)
```
